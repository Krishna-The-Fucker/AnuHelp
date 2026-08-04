# ============================================================
# 😊 REACTION & AUTO-REACT SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "😊 ʀᴇᴀᴄᴛɪᴏɴ"

__help__ = """
*😊 ʀᴇᴀᴄᴛɪᴏɴ sʏsᴛᴇᴍ* — Automatically add custom emojis or reactions to messages or respond with interactive triggers!

• `/autoreact <on/off>` — Toggle auto-reactions for incoming group messages
• `/setreact <emoji>` — Set custom default reaction emoji for the chat
"""

from pyrogram import filters
from pyrogram.types import Message
import logging

def register_reaction_system(app, db):

    # Collection for chat-specific reaction settings
    reactions_col = db.chat_reactions

    # ============================================================
    # ⚙️ TOGGLE AUTO-REACTION (`/autoreact`)
    # ============================================================
    @app.on_message(filters.command("autoreact") & filters.group)
    async def toggle_autoreact_cmd(client, message: Message):
        # Admin check
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ["administrator", "creator"]:
                return await message.reply("❌ **Only administrators can change auto-reaction settings!**")
        except Exception:
            return await message.reply("❌ **Failed to verify admin permissions.**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Usage:** `/autoreact on` or `/autoreact off`")

        action = message.command[1].lower()
        chat_id = message.chat.id

        if action in ["on", "enable", "true"]:
            await reactions_col.update_one(
                {"chat_id": chat_id},
                {"$set": {"enabled": True, "emoji": "👍"}},
                upsert=True
            )
            await message.reply("✅ **Auto-reactions have been enabled for this chat!**")
        elif action in ["off", "disable", "false"]:
            await reactions_col.update_one(
                {"chat_id": chat_id},
                {"$set": {"enabled": False}},
                upsert=True
            )
            await message.reply("❌ **Auto-reactions have been disabled for this chat!**")
        else:
            await message.reply("⚠️ **Invalid option! Use `on` or `off`.**")

    # ============================================================
    # 🎯 SET CUSTOM REACTION EMOJI (`/setreact`)
    # ============================================================
    @app.on_message(filters.command("setreact") & filters.group)
    async def set_reaction_emoji_cmd(client, message: Message):
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            if member.status not in ["administrator", "creator"]:
                return await message.reply("❌ **Only administrators can set the reaction emoji!**")
        except Exception:
            return await message.reply("❌ **Failed to verify admin permissions.**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please provide an emoji!** (e.g., `/setreact ❤️` or `/setreact 🔥`)")

        emoji = message.command[1]
        chat_id = message.chat.id

        await reactions_col.update_one(
            {"chat_id": chat_id},
            {"$set": {"emoji": emoji, "enabled": True}},
            upsert=True
        )
        await message.reply(f"✨ **Auto-reaction emoji updated to:** {emoji}")

    # ============================================================
    # ⚡ LISTENER: AUTO-REACT TO INCOMING MESSAGES
    # ============================================================
    @app.on_message(filters.group & ~filters.service & ~filters.bot)
    async def auto_react_listener(client, message: Message):
        try:
            chat_id = message.chat.id
            settings = await reactions_col.find_one({"chat_id": chat_id})

            if settings and settings.get("enabled", False):
                emoji = settings.get("emoji", "👍")
                # Attempt to send message reaction using Pyrogram's send_reaction API
                await client.send_reaction(
                    chat_id=chat_id,
                    message_id=message.id,
                    emoji=emoji
                )
        except Exception as e:
            # Silently log errors if bot lacks permission to react in the specific group
            logging.debug(f"[Auto-React Error]: {e}")
