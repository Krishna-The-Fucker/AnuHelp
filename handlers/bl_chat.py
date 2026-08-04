# ============================================================
# 🚫 BLACKLIST CHAT / GLOBAL BAN ENFORCEMENT MODULE
# ============================================================

__mod_name__ = "🚫 ʙʟᴀᴄᴋʟɪꜱᴛ"

__help__ = """
*🚫 ʙʟᴀᴄᴋʟɪꜱᴛ ᴍᴏᴅᴜʟᴇ* — Restrict unauthorized or malicious chats from utilizing Nomad bot services (Developer Only).

• `/blchat [chat_id]` — Blacklist a specific group chat.
• `/unblchat [chat_id]` — Remove a group chat from the blacklist.
• `/blchats` — View all blacklisted chats.
"""

from pyrogram import filters
from pyrogram.types import Message
from config import DEV_LIST, OWNER_ID
from db import db
import logging

logger = logging.getLogger("BLACKLIST")

def register_blacklist_system(app):

    # ============================================================
    # 🛡️ BLACKLIST MIDDLEWARE (AUTO-LEAVE UNAUTHORIZED CHATS)
    # ============================================================
    @app.on_message(filters.group, group=-2)
    async def blacklist_middleware(client, message: Message):
        chat_id = message.chat.id
        
        try:
            is_blacklisted = await db.blacklist_chats.find_one({"chat_id": chat_id})
            if is_blacklisted:
                await message.reply("🚫 **This chat has been blacklisted by the bot developers. Leaving chat...**")
                await client.leave_chat(chat_id)
                message.stop_propagation()
        except Exception as e:
            logger.error(f"[Blacklist Middleware Error]: {e}")

    # ============================================================
    # ➕ BLACKLIST CHAT (`/blchat`)
    # ============================================================
    @app.on_message(filters.command("blchat") & filters.user(DEV_LIST + [OWNER_ID]))
    async def blacklist_chat_cmd(client, message: Message):
        args = message.command
        chat_id = message.chat.id

        if len(args) > 1:
            try:
                chat_id = int(args[1])
            except ValueError:
                return await message.reply("⚠️ **Invalid Chat ID format! Please provide a numeric ID.**")

        try:
            await db.blacklist_chats.update_one(
                {"chat_id": chat_id},
                {"$set": {"blacklisted": True}},
                upsert=True
            )

            await message.reply(f"✅ **Chat ID `{chat_id}` has been successfully blacklisted.**")

            # Try leaving immediately if bot is currently in that chat
            try:
                await client.leave_chat(chat_id)
            except Exception:
                pass

        except Exception as e:
            logger.error(f"[Blacklist Cmd Error]: {e}")
            await message.reply(f"❌ **Failed to blacklist chat:** `{str(e)}`")

    # ============================================================
    # ➖ UNBLACKLIST CHAT (`/unblchat`)
    # ============================================================
    @app.on_message(filters.command("unblchat") & filters.user(DEV_LIST + [OWNER_ID]))
    async def unblacklist_chat_cmd(client, message: Message):
        args = message.command
        if len(args) < 2:
            return await message.reply("⚠️ **Please provide a Chat ID to unblacklist! Example:** `/unblchat -100xxxxxxxxxx`")

        try:
            chat_id = int(args[1])
        except ValueError:
            return await message.reply("⚠️ **Invalid Chat ID format!**")

        try:
            result = await db.blacklist_chats.delete_one({"chat_id": chat_id})
            if result.deleted_count > 0:
                await message.reply(f"✅ **Chat ID `{chat_id}` has been removed from the blacklist.**")
            else:
                await message.reply(f"ℹ️ **Chat ID `{chat_id}` was not found in the blacklist database.**")
        except Exception as e:
            logger.error(f"[UnBlacklist Error]: {e}")
            await message.reply(f"❌ **Failed to unblacklist chat:** `{str(e)}`")

    # ============================================================
    # 📋 LIST BLACKLISTED CHATS (`/blchats`)
    # ============================================================
    @app.on_message(filters.command("blchats") & filters.user(DEV_LIST + [OWNER_ID]))
    async def list_blacklisted_chats_cmd(client, message: Message):
        try:
            cursor = db.blacklist_chats.find({"blacklisted": True})
            chats = await cursor.to_list(length=50)

            if not chats:
                return await message.reply("ℹ️ **No chats are currently blacklisted.**")

            text = "🚫 **BLACKLISTED CHATS LIST:**\n\n"
            for index, chat in enumerate(chats, start=1):
                text += f"{index}. Chat ID: `{chat['chat_id']}`\n"

            await message.reply(text)

        except Exception as e:
            logger.error(f"[List Blacklist Error]: {e}")
            await message.reply(f"❌ **Failed to fetch blacklisted chats:** `{str(e)}`")
