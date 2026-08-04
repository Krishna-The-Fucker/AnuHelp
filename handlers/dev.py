# ============================================================
# 👑 DEVELOPER & SUDO MANAGEMENT SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "👑 ᴅᴇᴠ"

__help__ = """
*👑 ᴅᴇᴠᴇʟᴏᴘᴇʀ & sᴜᴅᴏ ᴛᴏᴏʟs* — High-privilege bot management commands restricted to Bot Developers and Owners!

• `/stats` — Check database collection stats, cache size, and system performance
• `/restart` — Restart the bot container/process safely
• `/broadcast <text>` — Broadcast an announcement message to all known groups or users
• `/adddev <user_id>` — Add a new user to the developer list
• `/remdev <user_id>` — Remove a user from the developer list
"""

from pyrogram import filters
from pyrogram.types import Message
import logging
import sys
import os
import time

def register_dev_system(app, db, OWNER_ID: int, DEV_LIST: list):

    # Helper to check if user is a developer/owner
    async def is_dev(user_id: int) -> bool:
        return user_id == OWNER_ID or user_id in DEV_LIST

    # ============================================================
    # 📊 BOT SYSTEM STATS (`/stats`)
    # ============================================================
    @app.on_message(filters.command("stats"))
    async def stats_cmd(client, message: Message):
        if not await is_dev(message.from_user.id):
            return await message.reply("❌ **This command is restricted to Bot Developers!**")

        status_msg = await message.reply("📊 **Gathering system & database statistics...**")

        try:
            # Fetch database statistics
            db_stats = await db.command("dbStats")
            collections = await db.list_collection_names()
            
            total_data_size = round(db_stats.get("dataSize", 0) / (1024 * 1024), 2)
            total_storage_size = round(db_stats.get("storageSize", 0) / (1024 * 1024), 2)
            collection_count = len(collections)

            # Get bot runtime info
            python_version = sys.version.split()[0]
            
            stats_text = (
                f"📈 **Nomad Bot Performance Stats:**\n\n"
                f"🤖 **Bot Username:** @{client.me.username}\n"
                f"👑 **Owner ID:** `{OWNER_ID}`\n"
                f"🐍 **Python Version:** `{python_version}`\n\n"
                f"🗄️ **Database Statistics:**\n"
                f"• **Database Name:** `{db.name}`\n"
                f"• **Collections Count:** `{collection_count}`\n"
                f"• **Data Size:** `{total_data_size} MB`\n"
                f"• **Storage Size:** `{total_storage_size} MB`\n\n"
                f"⚡ **System Status:** `Online & Fully Operational 🚀`"
            )

            await status_msg.edit_text(stats_text)
        except Exception as e:
            logging.error(f"[Stats Command Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to fetch stats:** `{str(e)}`")

    # ============================================================
    # 🔄 RESTART BOT (`/restart`)
    # ============================================================
    @app.on_message(filters.command("restart"))
    async def restart_cmd(client, message: Message):
        if not await is_dev(message.from_user.id):
            return await message.reply("❌ **This command is restricted to Bot Developers!**")

        await message.reply("🔄 **Restarting bot process... Please wait a moment.**")
        logging.warning(f"⚠️ Bot restart triggered by developer ID: {message.from_user.id}")
        
        # Flush streams and restart python process
        os.execv(sys.executable, [sys.executable] + sys.argv)

    # ============================================================
    # 📢 BROADCAST MESSAGE (`/broadcast`, `/bc`)
    # ============================================================
    @app.on_message(filters.command(["broadcast", "bc"]))
    async def broadcast_cmd(client, message: Message):
        if not await is_dev(message.from_user.id):
            return await message.reply("❌ **This command is restricted to Bot Developers!**")

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("⚠️ **Please provide text or reply to a message to broadcast!**")

        target_text = message.reply_to_message if message.reply_to_message else message.text.split(None, 1)[1]
        
        status_msg = await message.reply("📢 **Initiating broadcast to all registered chats...**")
        
        # Example collection scan logic for broadcast storage if implemented in DB
        success_count = 0
        failed_count = 0

        # Fetch active chats from a hypothetical chats collection or iterate known records
        try:
            async for chat_doc in db.chats.find({}):
                chat_id = chat_doc.get("chat_id")
                if not chat_id:
                    continue
                try:
                    if message.reply_to_message:
                        await message.reply_to_message.copy(chat_id)
                    else:
                        await client.send_message(chat_id, target_text)
                    success_count += 1
                except Exception:
                    failed_count + 1
        except Exception as e:
            logging.error(f"[Broadcast Error]: {e}")

        await status_msg.edit_text(
            f"📢 **Broadcast Completed!**\n\n"
            f"• **Successful Deliveries:** `{success_count}`\n"
            f"• **Failed Deliveries:** `{failed_count}`"
        )
