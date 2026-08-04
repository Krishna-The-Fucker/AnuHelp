# ============================================================
# 📢 LOG CHANNEL SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "📢 ʟᴏɢs"

__help__ = """
*📢 ʟᴏɢ ᴄʜᴀɴɴᴇʟ sʏsᴛᴇᴍ* — Automatically log important group events, bans, kicks, reports, and admin actions to a dedicated log channel!

• `/setlogchannel <channel_id>` — Set the log channel for the group
• `/logchannel` — Check the current log channel configuration
• `/removelogchannel` — Disable and remove the log channel
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging

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
    # ⚙️ SET LOG CHANNEL COMMAND (`/setlogchannel`)
    # ============================================================
    @app.on_message(filters.command("setlogchannel") & filters.group)
    async def set_log_channel_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can set the log channel!**")

        if len(message.command) < 2:
            return await message.reply(
                "⚠️ **Incorrect Usage!**\n"
                "• Use `/setlogchannel <channel_id>` (e.g., `-1001234567890`)\n"
                "_Make sure I am an administrator in that channel with post permissions!_"
            )

        try:
            channel_id = int(message.command[1])
        except ValueError:
            return await message.reply("❌ **Invalid Channel ID format! Must be a valid integer.**")

        chat_id = message.chat.id

        try:
            # Test if bot can send messages to the log channel
            test_msg = await client.send_message(channel_id, "🔗 **Nomad Bot Log Channel Connected Successfully!** ✨")
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
                return await message.reply("📭 **No log channel configured for this group yet.**\n_Use `/setlogchannel <id>` to set one._")

            channel_id = data["channel_id"]
            await message.reply_text(f"📢 **Current Log Channel ID:** `{channel_id}`")
        except Exception as e:
            logging.error(f"[Log Channel Get Error]: {e}")
            await message.reply("❌ **Failed to fetch log channel info.**")

    # ============================================================
    # 🗑️ REMOVE LOG CHANNEL COMMAND (`/removelogchannel`)
    # ============================================================
    @app.on_message(filters.command(["removelogchannel", "dellogchannel"]) & filters.group)
    async def remove_log_channel_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can remove the log channel!**")

        chat_id = message.chat.id

        try:
            result = await db.log_channels.delete_one({"chat_id": chat_id})
            if result.deleted_count > 0:
                await message.reply("🗑️ **Log channel has been successfully disabled and removed!**")
            else:
                await message.reply("⚠️ **No log channel was configured for this group.**")
        except Exception as e:
            logging.error(f"[Log Channel Remove Error]: {e}")
            await message.reply("❌ **Failed to remove log channel configuration.**")

    # ============================================================
    # 🛠️ HELPER FUNCTION TO SEND LOGS TO CONFIGURED CHANNEL
    # ============================================================
    async def send_log(chat_id: int, text: str):
        try:
            data = await db.log_channels.find_one({"chat_id": chat_id})
            if data and data.get("channel_id"):
                channel_id = data["channel_id"]
                await app.send_message(channel_id, text, disable_web_page_preview=True)
        except Exception as e:
            logging.error(f"[Send Log Dispatch Error]: {e}")

    # Expose helper globally or store in app state if needed by other modules
    app.send_group_log = send_log
