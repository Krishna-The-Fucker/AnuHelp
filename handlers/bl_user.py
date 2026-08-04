# ============================================================
# 🚫 USER BLACKLIST / GLOBAL USER BAN MODULE (DEVELOPER 👑)
# ============================================================

__mod_name__ = "🚫 ʙʟ_ᴜꜱᴇʀ"

__help__ = """
*🚫 ᴜꜱᴇʀ ʙʟᴀᴄᴋʟɪꜱᴛ* — Globally restrict abusive or spamming users from interacting with any Nomad bot features (Developer Only).

• `/bluser [user_id]` — Globally blacklist a user (Reply to user or provide ID).
• `/unbluser [user_id]` — Remove a user from the global blacklist.
• `/blusers` — View all globally blacklisted users.
"""

from pyrogram import filters
from pyrogram.types import Message
from config import DEV_LIST, OWNER_ID
from db import db
import logging

logger = logging.getLogger("BL_USER")

def register_user_blacklist_system(app):

    # ============================================================
    # 🛡️ GLOBAL USER BLACKLIST MIDDLEWARE
    # ============================================================
    @app.on_message(~filters.service & ~filters.bot, group=-3)
    async def user_blacklist_middleware(client, message: Message):
        if not message.from_user:
            return

        user_id = message.from_user.id
        
        # Developers and owner cannot be globally restricted
        if user_id in DEV_LIST or user_id == OWNER_ID:
            return

        try:
            is_blacklisted = await db.blacklist_users.find_one({"user_id": user_id})
            if is_blacklisted:
                # Silently drop or ignore messages from blacklisted users across all commands/modules
                message.stop_propagation()
        except Exception as e:
            logger.error(f"[User Blacklist Middleware Error]: {e}")

    # ============================================================
    # ➕ BLACKLIST USER (`/bluser`)
    # ============================================================
    @app.on_message(filters.command("bluser") & filters.user(DEV_LIST + [OWNER_ID]))
    async def blacklist_user_cmd(client, message: Message):
        user_id = None
        
        if message.reply_to_message and message.reply_to_message.from_user:
            user_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            try:
                user_id = int(message.command[1])
            except ValueError:
                return message.reply("⚠️ **Invalid User ID format! Please provide a numeric ID or reply to a user.**")
        else:
            return message.reply("⚠️ **Please reply to a user or provide a User ID to blacklist! Example:** `/bluser 123456789`")

        if user_id in DEV_LIST or user_id == OWNER_ID:
            return message.reply("⚠️ **You cannot blacklist a Developer or Bot Owner!**")

        try:
            await db.blacklist_users.update_one(
                {"user_id": user_id},
                {"$set": {"blacklisted": True}},
                upsert=True
            )
            await message.reply(f"✅ **User ID `{user_id}` has been globally blacklisted from using Nomad bot.**")
        except Exception as e:
            logger.error(f"[Blacklist User Error]: {e}")
            await message.reply(f"❌ **Failed to blacklist user:** `{str(e)}`")

    # ============================================================
    # ➖ UNBLACKLIST USER (`/unbluser`)
    # ============================================================
    @app.on_message(filters.command("unbluser") & filters.user(DEV_LIST + [OWNER_ID]))
    async def unblacklist_user_cmd(client, message: Message):
        if len(message.command) < 2:
            return message.reply("⚠️ **Please provide a User ID to unblacklist! Example:** `/unbluser 123456789`")

        try:
            user_id = int(message.command[1])
        except ValueError:
            return message.reply("⚠️ **Invalid User ID format!**")

        try:
            result = await db.blacklist_users.delete_one({"user_id": user_id})
            if result.deleted_count > 0:
                await message.reply(f"✅ **User ID `{user_id}` has been removed from the user blacklist.**")
            else:
                await message.reply(f"ℹ️ **User ID `{user_id}` was not found in the blacklist database.**")
        except Exception as e:
            logger.error(f"[UnBlacklist User Error]: {e}")
            await message.reply(f"❌ **Failed to unblacklist user:** `{str(e)}`")

    # ============================================================
    # 📋 LIST BLACKLISTED USERS (`/blusers`)
    # ============================================================
    @app.on_message(filters.command("blusers") & filters.user(DEV_LIST + [OWNER_ID]))
    async def list_blacklisted_users_cmd(client, message: Message):
        try:
            cursor = db.blacklist_users.find({"blacklisted": True})
            users = await cursor.to_list(length=50)

            if not users:
                return message.reply("ℹ️ **No users are currently globally blacklisted.**")

            text = "🚫 **GLOBALLY BLACKLISTED USERS:**\n\n"
            for index, user in enumerate(users, start=1):
                text += f"{index}. User ID: `{user['user_id']}`\n"

            await message.reply(text)

        except Exception as e:
            logger.error(f"[List Blacklisted Users Error]: {e}")
            await message.reply(f"❌ **Failed to fetch blacklisted users:** `{str(e)}`")
