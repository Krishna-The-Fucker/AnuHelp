# ============================================================
# 🚫 BLACKLIST / AUTO-BLACKLIST SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🚫 ʙʟᴀᴄᴋʟɪsᴛ"

__help__ = """
*🚫 ʙʟᴀᴄᴋʟɪsᴛ sʏsᴛᴇᴍ* — Automatically catch and delete forbidden trigger words, phrases, links, or media keywords in your group!

• `/blacklist` or `/addblacklist <word>` — Add a word or phrase to the group blacklist
• `/blacklist` — View all blacklisted words in the group
• `/rmblacklist <word>` or `/unblacklist <word>` — Remove a word from the blacklist
• `/clearblacklist` — Remove all blacklisted words (Admin only)
• `/blacklistmode <del/ban/kick/mute>` — Set action when a blacklisted word is triggered
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging

def register_blacklist_system(app, db):

    # ============================================================
    # 👑 ADMIN CHECK HELPER
    # ============================================================
    async def is_admin(client, message: Message):
        if not message.from_user:
            return False
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except Exception:
            return False

    # ============================================================
    # ➕ ADD TO BLACKLIST (`/blacklist`, `/addblacklist`)
    # ============================================================
    @app.on_message(filters.command(["blacklist", "addblacklist"]) & filters.group)
    async def add_blacklist_cmd(client, message: Message):
        chat_id = message.chat.id

        # If no arguments provided, show list of blacklisted words
        if len(message.command) < 2:
            try:
                doc = await db.blacklist_settings.find_one({"chat_id": chat_id})
                b_words = doc.get("words", []) if doc else []

                if not b_words:
                    return await message.reply("📭 **No blacklisted words configured in this group.**\n_Use `/blacklist <word>` or `/addblacklist <word>` to add one._")

                formatted = ", ".join([f"`{w}`" for w in b_words])
                return await message.reply_text(
                    f"🚫 **Nomad Bot — Group Blacklist:**\n\n"
                    f"{formatted}\n\n"
                    f"_Triggering any of these will trigger the configured action!_"
                )
            except Exception as e:
                logging.error(f"[Blacklist View Error]: {e}")
                return await message.reply("❌ **Failed to fetch blacklist.**")

        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can manage the group blacklist!**")

        word = " ".join(message.command[1:]).strip().lower()
        if not word:
            return await message.reply("⚠️ **Please provide a valid word or phrase to blacklist!**")

        try:
            await db.blacklist_settings.update_one(
                {"chat_id": chat_id},
                {"$addToSet": {"words": word}},
                upsert=True
            )
            await message.reply(f"✅ **Successfully added to group blacklist:** `{word}`")
        except Exception as e:
            logging.error(f"[Blacklist Add Error]: {e}")
            await message.reply("❌ **Failed to update blacklist database.**")

    # ============================================================
    # 🗑️ REMOVE FROM BLACKLIST (`/rmblacklist`, `/unblacklist`)
    # ============================================================
    @app.on_message(filters.command(["rmblacklist", "unblacklist", "delblacklist"]) & filters.group)
    async def remove_blacklist_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can manage the group blacklist!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please specify the word you want to remove from the blacklist!**")

        word = " ".join(message.command[1:]).strip().lower()
        chat_id = message.chat.id

        try:
            result = await db.blacklist_settings.update_one(
                {"chat_id": chat_id},
                {"$pull": {"words": word}}
            )
            if result.modified_count > 0:
                await message.reply(f"🗑️ **Successfully removed from blacklist:** `{word}`")
            else:
                await message.reply(f"⚠️ **Word not found in the group blacklist:** `{word}`")
        except Exception as e:
            logging.error(f"[Blacklist Remove Error]: {e}")
            await message.reply("❌ **Failed to remove word from blacklist.**")

    # ============================================================
    # ⚙️ SET BLACKLIST PUNISHMENT MODE (`/blacklistmode`)
    # ============================================================
    @app.on_message(filters.command("blacklistmode") & filters.group)
    async def blacklist_mode_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can configure blacklist punishment modes!**")

        if len(message.command) < 2:
            try:
                doc = await db.blacklist_settings.find_one({"chat_id": message.chat.id})
                mode = doc.get("mode", "del") if doc else "del"
                return await message.reply(
                    f"⚙️ **Current Blacklist Punishment Mode:** `{mode.upper()}`\n\n"
                    f"• Available modes: `del` (Delete only), `warn` (Warn + Delete), `mute` (Mute + Delete), `kick` (Kick + Delete), `ban` (Ban + Delete)\n"
                    f"_Usage: `/blacklistmode <mode>`_"
                )
            except Exception as e:
                logging.error(f"[Blacklist Mode View Error]: {e}")
                return await message.reply("❌ **Failed to fetch blacklist mode.**")

        mode = message.command[1].lower()
        valid_modes = ["del", "warn", "mute", "kick", "ban"]
        if mode not in valid_modes:
            return await message.reply(f"❌ **Invalid mode!** Choose from: `{', '.join(valid_modes)}`")

        chat_id = message.chat.id
        try:
            await db.blacklist_settings.update_one(
                {"chat_id": chat_id},
                {"$set": {"mode": mode}},
                upsert=True
            )
            await message.reply(f"✅ **Blacklist punishment mode updated successfully to:** `{mode.upper()}` ✨")
        except Exception as e:
            logging.error(f"[Blacklist Mode Set Error]: {e}")
            await message.reply("❌ **Failed to update blacklist mode.**")

    # ============================================================
    # ⚡ AUTOMATIC BLACKLIST MESSAGE DISPATCHER & ENFORCER
    # ============================================================
    @app.on_message((filters.text | filters.caption) & filters.group & ~filters.bot, group=5)
    async def blacklist_enforcer(client, message: Message):
        if not message.from_user:
            return

        # Skip checks if sender is an admin
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except Exception:
            pass

        chat_id = message.chat.id
        text_content = (message.text or message.caption or "").lower()

        if not text_content:
            return

        try:
            doc = await db.blacklist_settings.find_one({"chat_id": chat_id})
            if not doc or not doc.get("words"):
                return

            b_words = doc.get("words", [])
            mode = doc.get("mode", "del")

            # Check if any blacklisted word exists in message text
            triggered = any(word in text_content for word in b_words)
            if not triggered:
                return

            # Execute punishment action
            user = message.from_user
            await message.delete()

            if mode == "del":
                await client.send_message(
                    chat_id,
                    f"⚠️ {user.mention}, your message contained a blacklisted word and was removed.",
                    disable_web_page_preview=True
                )
            elif mode == "warn":
                await client.send_message(
                    chat_id,
                    f"⚠️ {user.mention} has been warned for using a blacklisted word!",
                    disable_web_page_preview=True
                )
            elif mode == "mute":
                from pyrogram.types import ChatPermissions
                await client.restrict_chat_member(chat_id, user.id, permissions=ChatPermissions())
                await client.send_message(
                    chat_id,
                    f"🔇 {user.mention} has been muted for sending blacklisted content.",
                    disable_web_page_preview=True
                )
            elif mode == "kick":
                await client.ban_chat_member(chat_id, user.id)
                await client.unban_chat_member(chat_id, user.id)
                await client.send_message(
                    chat_id,
                    f"👢 {user.mention} has been kicked for sending blacklisted content.",
                    disable_web_page_preview=True
                )
            elif mode == "ban":
                await client.ban_chat_member(chat_id, user.id)
                await client.send_message(
                    chat_id,
                    f"🔨 {user.mention} has been banned for sending blacklisted content.",
                    disable_web_page_preview=True
                )

        except Exception as e:
            logging.error(f"[Blacklist Enforcer Error]: {e}")
