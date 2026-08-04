# ============================================================
# 🗑️ PURGE & MESSAGE CLEANUP SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🗑️ ᴘᴜʀɢᴇ"

__help__ = """
*🗑️ ᴘᴜʀɢᴇ & ᴄʟᴇᴀɴᴜᴘ sʏsᴛᴇᴍ* — Bulk delete messages instantly to keep your group clean from clutter, spam, or unwanted media!

• `/purge` — Reply to any message to delete all messages from that replied message up to the current command message
• `/del` — Reply to a single message to delete it instantly
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import FloodWait
import asyncio
import logging

def register_purge_system(app):

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
    # 🗑️ SINGLE MESSAGE DELETE COMMAND (`/del`)
    # ============================================================
    @app.on_message(filters.command("del") & filters.group)
    async def delete_single_msg(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can use this command!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to the message you want to delete!**")

        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            logging.error(f"[Single Del Error]: {e}")
            await message.reply("❌ **Failed to delete message. Make sure I have delete permissions!**")

    # ============================================================
    # 🧹 BULK PURGE COMMAND (`/purge`)
    # ============================================================
    @app.on_message(filters.command("purge") & filters.group)
    async def purge_messages(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can use the purge command!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to a message from where you want to start purging!**")

        chat_id = message.chat.id
        start_message_id = message.reply_to_message.id
        end_message_id = message.id

        message_ids = []
        
        # Collect message IDs in chunks to respect Telegram limitations (max 100 per delete request)
        for msg_id in range(start_message_id, end_message_id + 1):
            message_ids.append(msg_id)
            if len(message_ids) == 100:
                try:
                    await client.delete_messages(chat_id=chat_id, message_ids=message_ids)
                except Exception:
                    pass
                message_ids = []
                await asyncio.sleep(0.1)

        # Delete remaining message IDs if any
        if message_ids:
            try:
                await client.delete_messages(chat_id=chat_id, message_ids=message_ids)
            except Exception:
                pass

        # Send success notification alert that auto-deletes after 3 seconds
        try:
            notif = await message.reply_text("🗑️ **Purge Successful!** ✨")
            await asyncio.sleep(3)
            await notif.delete()
        except Exception:
            pass
