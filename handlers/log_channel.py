# ============================================================
# 📢 LOG CHANNEL SYSTEM (ROSE STYLE)
# ============================================================

__mod_name__ = "📢 ʟᴏɢꜱ"

__help__ = """
*📢 ʟᴏɢ ᴄʜᴀɴɴᴇʟ sʏsᴛᴇᴍ* — Automatically log important group events to a dedicated log channel!

Setting a log channel is done by the following steps:
• Add the bot to your channel, as an admin.
• Send `/setlog` to your channel.
• Forward the `/setlog` command to the group you wish to be logged.
• Congrats! all done :)

Admin commands:
• `/logchannel` — Get the name of the current log channel.
• `/setlog` — Set the log channel for the current chat (by forwarding or using ID).
• `/unsetlog` — Unset the log channel for the current chat.
• `/log <category>` — Enable a log category - actions of that type will now be logged.
• `/nolog <category>` — Disable a log category - actions of that type will no longer be logged.
• `/logcategories` — List all support categories, with information on what they refer to.
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging

SUPPORTED_CATEGORIES = {
    "reports": "Logs user reports (@admin /report)",
    "bans": "Logs all bans and unbans",
    "kicks": "Logs all kicks",
    "mutes": "Logs all mutes and unmutes",
    "settings": "Logs changes to group settings",
    "admin": "Logs admin promotions and demotions"
}

def register_log_channel_system(app, db):

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
    # ⚙️ SET LOG CHANNEL COMMAND (`/setlog`)
    # ============================================================
    @app.on_message(filters.command("setlog") & filters.group)
    async def set_log_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can set the log channel!**")

        channel_id = None

        # Check if message is a forwarded command from a channel
        if message.forward_from_chat and message.forward_from_chat.type.value == "channel":
            channel_id = message.forward_from_chat.id
        elif len(message.command) >= 2:
            try:
                channel_id = int(message.command[1])
            except ValueError:
                return await message.reply("❌ **Invalid Channel ID format! Must be a valid integer or forwarded from a channel.**")
        else:
            return await message.reply(
                "⚠️ **Incorrect Usage!**\n"
                "• Send `/setlog` inside your channel, then **forward** that message to this group.\n"
                "• Alternatively, use `/setlog <channel_id>`."
            )

        chat_id = message.chat.id

        try:
            # Test if bot can send messages to the log channel
            test_msg = await client.send_message(channel_id, "🔗 **Log Channel Connected Successfully!** ✨")
            await test_msg.delete()
        except Exception as e:
            logging.error(f"[Log Channel Test Error]: {e}")
            return await message.reply(
                "❌ **Failed to verify log channel!**\n"
                "_Make sure I am added as an administrator in the target channel and can send messages._"
            )

        try:
            await db.log_channels.update_one(
                {"chat_id": chat_id},
                {"$set": {"channel_id": channel_id}},
                upsert=True
            )
            await message.reply(f"✅ **Log channel successfully configured to:** `{channel_id}`")
        except Exception as e:
            logging.error(f"[Log Channel DB Error]: {e}")
            await message.reply("❌ **Failed to save log channel to database.**")

    # ============================================================
    # 📋 CHECK LOG CHANNEL COMMAND (`/logchannel`)
    # ============================================================
    @app.on_message(filters.command("logchannel") & filters.group)
    async def get_log_channel_cmd(client, message: Message):
        chat_id = message.chat.id

        try:
            data = await db.log_channels.find_one({"chat_id": chat_id})
            if not data or not data.get("channel_id"):
                return await message.reply("📭 **No log channel configured for this group yet.**\n_Use `/setlog` to set one._")

            channel_id = data["channel_id"]
            try:
                chat_info = await client.get_chat(channel_id)
                channel_name = chat_info.title or str(channel_id)
            except Exception:
                channel_name = str(channel_id)

            await message.reply_text(f"📢 **Current Log Channel:** `{channel_name}` (`{channel_id}`)")
        except Exception as e:
            logging.error(f"[Log Channel Get Error]: {e}")
            await message.reply("❌ **Failed to fetch log channel info.**")

    # ============================================================
    # 🗑️ UNSET LOG CHANNEL COMMAND (`/unsetlog`)
    # ============================================================
    @app.on_message(filters.command(["unsetlog", "removelogchannel", "dellogchannel"]) & filters.group)
    async def unset_log_channel_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can remove the log channel!**")

        chat_id = message.chat.id

        try:
            result = await db.log_channels.delete_one({"chat_id": chat_id})
            if result.deleted_count > 0:
                await message.reply("🗑️ **Log channel has been successfully unset and removed!**")
            else:
                await message.reply("⚠️ **No log channel was configured for this group.**")
        except Exception as e:
            logging.error(f"[Log Channel Remove Error]: {e}")
            await message.reply("❌ **Failed to remove log channel configuration.**")

    # ============================================================
    # ➕ ENABLE LOG CATEGORY (`/log <category>`)
    # ============================================================
    @app.on_message(filters.command("log") & filters.group)
    async def enable_log_category(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can configure log categories!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please specify a category!** Use `/logcategories` to view available categories.")

        category = message.command[1].lower()
        if category not in SUPPORTED_CATEGORIES:
            return await message.reply(f"❌ **Invalid category!** Use `/logcategories` to see valid options.")

        chat_id = message.chat.id
        try:
            await db.log_categories.update_one(
                {"chat_id": chat_id},
                {"$addToSet": {"categories": category}},
                upsert=True
            )
            await message.reply(f"✅ **Log category `{category}` has been enabled.** Actions of this type will now be logged.")
        except Exception as e:
            logging.error(f"[Log Category Enable Error]: {e}")
            await message.reply("❌ **Failed to enable log category.**")

    # ============================================================
    # ➖ DISABLE LOG CATEGORY (`/nolog <category>`)
    # ============================================================
    @app.on_message(filters.command("nolog") & filters.group)
    async def disable_log_category(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can configure log categories!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please specify a category!** Use `/logcategories` to view available categories.")

        category = message.command[1].lower()
        if category not in SUPPORTED_CATEGORIES:
            return await message.reply(f"❌ **Invalid category!** Use `/logcategories` to see valid options.")

        chat_id = message.chat.id
        try:
            await db.log_categories.update_one(
                {"chat_id": chat_id},
                {"$pull": {"categories": category}}
            )
            await message.reply(f"✅ **Log category `{category}` has been disabled.** Actions of this type will no longer be logged.")
        except Exception as e:
            logging.error(f"[Log Category Disable Error]: {e}")
            await message.reply("❌ **Failed to disable log category.**")

    # ============================================================
    # 📋 LIST LOG CATEGORIES (`/logcategories`)
    # ============================================================
    @app.on_message(filters.command("logcategories") & filters.group)
    async def list_log_categories(client, message: Message):
        text = "📋 **SUPPORTED LOG CATEGORIES:**\n\n"
        for cat, desc in SUPPORTED_CATEGORIES.items():
            text += f"• `{cat}` — {desc}\n"
        text += "\nUse `/log <category>` to enable and `/nolog <category>` to disable."
        await message.reply(text)

    # ============================================================
    # 🛠️ HELPER FUNCTION TO SEND LOGS WITH CATEGORY CHECK
    # ============================================================
    async def send_log(chat_id: int, category: str, text: str):
        try:
            data = await db.log_channels.find_one({"chat_id": chat_id})
            if not data or not data.get("channel_id"):
                return
            
            channel_id = data["channel_id"]

            # Check if category is enabled (if category is specified)
            if category:
                cat_data = await db.log_categories.find_one({"chat_id": chat_id})
                enabled_cats = cat_data.get("categories", []) if cat_data else []
                if category not in enabled_cats:
                    return

            await app.send_message(channel_id, text, disable_web_page_preview=True)
        except Exception as e:
            logging.error(f"[Send Log Dispatch Error]: {e}")

    app.send_group_log = send_log
