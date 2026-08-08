# ============================================================
# 🧹 PURGE & MESSAGE CLEANUP MODULE (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🧹 ᴄʟᴇᴀɴᴇʀ"

__help__ = """
*🧹 ᴍᴇssᴀɢᴇ ᴄʟᴇᴀɴᴇʀ* — Advanced group cleanup tools to delete messages, purge bulk histories, and remove bot/user clutter instantly.

• `/pall` — Reply to a message to delete all messages from that point up to the latest, or specify a count (e.g. `/pall 50`).
• `/delete` — Delete a specific replied-to message.
"""

from pyrogram import filters
from pyrogram.types import Message
import asyncio
import logging

def register_cleaner_system(app):

    # Helper function to check admin rights for cleanup
    async def check_cleaner_permissions(message: Message) -> bool:
        if message.chat.type.value == "private":
            await message.reply("⚠️ **This command can only be used inside group chats!**")
            return False

        bot_member = await message.chat.get_member(app.me.id)
        if not bot_member.status in ["administrator", "creator"] or not bot_member.can_delete_messages:
            await message.reply("❌ **I need to be an administrator with `can_delete_messages` permission to clean chats!**")
            return False

        user = await message.chat.get_member(message.from_user.id)
        if user.status not in ["administrator", "creator"]:
            await message.reply("⚠️ **Only group administrators can use cleanup commands!**")
            return False

        return True

    # ============================================================
    # 🗑️ DELETE SINGLE MESSAGE (`/delete`)
    # ============================================================
    @app.on_message(filters.command("delete") & ~filters.private)
    async def delete_single_message_cmd(client, message: Message):
        if not await check_cleaner_permissions(message):
            return

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to the message you want to delete!**")

        try:
            await message.reply_to_message.delete()
            await message.delete()
        except Exception as e:
            logging.error(f"[Delete Single Error]: {e}")
            await message.reply(f"❌ **Failed to delete message:** `{str(e)}`")

    # ============================================================
    # 🧹 PURGE / PALL MESSAGES (`/pall`)
    # ============================================================
    @app.on_message(filters.command("pall") & ~filters.private)
    async def purge_messages_cmd(client, message: Message):
        if not await check_cleaner_permissions(message):
            return

        chat_id = message.chat.id
        
        # Scenario A: Replying to a specific message to purge from there onwards
        if message.reply_to_message:
            start_message_id = message.reply_to_message.id
            end_message_id = message.id
            
            message_ids = []
            for msg_id in range(start_message_id, end_message_id + 1):
                message_ids.append(msg_id)
                # Telegram batch delete limit is usually 100 messages at a time
                if len(message_ids) >= 100:
                    try:
                        await client.delete_messages(chat_id=chat_id, message_ids=message_ids)
                    except Exception:
                        pass
                    message_ids = []

            if message_ids:
                try:
                    await client.delete_messages(chat_id=chat_id, message_ids=message_ids)
                except Exception:
                    pass

            # Send a temporary notification of success
            notif = await message.reply("✨ **Purge completed successfully!**")
            await asyncio.sleep(3)
            try:
                await notif.delete()
            except Exception:
                pass
            return

        # Scenario B: `/pall [count]` provided
        if len(message.command) > 1:
            try:
                count = int(message.command[1])
            except ValueError:
                return await message.reply("⚠️ **Please provide a valid number of messages to purge! Example:** `/pall 25`")

            if count < 1 or count > 500:
                return await message.reply("⚠️ **You can only purge between 1 and 500 messages at once!**")

            # Collect recent message IDs
            message_ids = []
            async for msg in client.get_chat_history(chat_id, limit=count + 1):
                message_ids.append(msg.id)
                if len(message_ids) >= 100:
                    try:
                        await client.delete_messages(chat_id=chat_id, message_ids=message_ids)
                    except Exception:
                        pass
                    message_ids = []

            if message_ids:
                try:
                    await client.delete_messages(chat_id=chat_id, message_ids=message_ids)
                except Exception:
                    pass

            notif = await message.reply(f"✨ **Successfully purged last {count} messages!**")
            try:
                await asyncio.sleep(3)
                await notif.delete()
            except Exception:
                pass
            return

        await message.reply(
            "⚠️ **Invalid purge usage!**\n\n"
            "📌 **Usage 1:** Reply to a message with `/pall`\n"
            "📌 **Usage 2:** Type `/pall [count]` (e.g., `/pall 50`)"
        )
