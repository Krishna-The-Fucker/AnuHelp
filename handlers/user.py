# ============================================================
# 👤 USER MANAGEMENT & DATABASE SYNCHRONIZATION MODULE
# ============================================================

__mod_name__ = "👤 ᴜsᴇʀs"

__help__ = """
*👤 ᴜsᴇʀ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ* — Tracks and manages active users interacting with the Nomad bot ecosystem.

• Automatic middleware tracking for every message received.
• `/users` — View total registered users count in the database (Developer only).
"""

from pyrogram import filters
from pyrogram.types import Message
from db import db
from config import DEV_LIST, OWNER_ID
import logging

logger = logging.getLogger("USERS")

def register_user_system(app):

    # ============================================================
    # 🔄 USER TRACKING MIDDLEWARE
    # ============================================================
    @app.on_message(~filters.service & ~filters.bot, group=-1)
    async def user_tracking_middleware(client, message: Message):
        if not message.from_user:
            return

        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = message.from_user.username

        try:
            # Check if user already exists in DB, if not insert, else update info
            await db.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "first_name": first_name,
                        "username": username,
                    },
                    "$setOnInsert": {
                        "user_id": user_id
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"[User Tracking Error]: {e}")

    # ============================================================
    # 📊 TOTAL REGISTERED USERS CMD (`/users`)
    # ============================================================
    @app.on_message(filters.command("users") & filters.user(DEV_LIST + [OWNER_ID]))
    async def total_users_cmd(client, message: Message):
        try:
            count = await db.users.count_documents({})
            await message.reply(f"👥 **Total Unique Registered Users:** `{count}`")
        except Exception as e:
            await message.reply(f"❌ **Failed to fetch user count:** `{str(e)}`")
