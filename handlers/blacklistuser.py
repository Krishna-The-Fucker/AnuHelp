# ============================================================
# 🚫 BLACKLIST USER / GLOBAL-LOCAL USER BAN SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🚫 ᴜsᴇʀ ʙʟᴀᴄᴋʟɪsᴛ"

__help__ = """
*🚫 ᴜsᴇʀ ʙʟᴀᴄᴋʟɪsᴛ sʏsᴛᴇᴍ* — Automatically block or ban specific troublesome users from interacting with your group chat!

• `/blacklistuser <user_id/username>` — Permanently restrict & ban a user from joining or messaging the group
• `/unblacklistuser <user_id/username>` — Remove user from the chat user blacklist
• `/blacklistedusers` — View all blacklisted users in this group
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging

def register_blacklist_user_system(app, db):

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
    # 🔨 BLACKLIST / BAN USER COMMAND (`/blacklistuser`, `/bluser`)
    # ============================================================
    @app.on_message(filters.command(["blacklistuser", "bluser"]) & filters.group)
    async def blacklist_user_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can blacklist users!**")

        user_to_ban = None
        
        # Check if replied to a user
        if message.reply_to_message and message.reply_to_message.from_user:
            user_to_ban = message.reply_to_message.from_user
        elif len(message.command) > 1:
            query = message.command[1].strip()
            try:
                if query.isdigit():
                    user_to_ban = await client.get_users(int(query))
                else:
                    user_to_ban = await client.get_users(query)
            except Exception:
                pass

        if not user_to_ban:
            return await message.reply(
                "⚠️ **Incorrect Usage!**\n"
                "• Reply to a user's message with `/blacklistuser`\n"
                "• Or use `/blacklistuser <user_id / username>`"
            )

        chat_id = message.chat.id
        user_id = user_to_ban.id

        # Prevent blacklisting administrators or the bot itself
        try:
            member_status = await client.get_chat_member(chat_id, user_id)
            if member_status.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return await message.reply("❌ **You cannot blacklist an administrator or group owner!**")
        except Exception:
            pass

        if user_id == client.me.id:
            return await message.reply("❌ **I cannot blacklist myself!**")

        try:
            # 1. Save to database blacklist collection
            await db.chat_user_blacklist.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"username": user_to_ban.username, "name": user_to_ban.first_name}},
                upsert=True
            )

            # 2. Ban user from the chat immediately
            await client.ban_chat_member(chat_id, user_id)

            await message.reply(
                f"🚫 **User Successfully Blacklisted & Banned!**\n"
                f"👤 **User:** {user_to_ban.mention}\n"
                f"🆔 **ID:** `{user_id}`\n"
                f"_They will be automatically banned if they rejoin._"
            )
        except Exception as e:
            logging.error(f"[Blacklist User Error]: {e}")
            await message.reply("❌ **Failed to blacklist user. Make sure I have ban permissions!**")

    # ============================================================
    # 🔓 UNBLACKLIST USER COMMAND (`/unblacklistuser`, `/unbluser`)
    # ============================================================
    @app.on_message(filters.command(["unblacklistuser", "unbluser"]) & filters.group)
    async def unblacklist_user_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can unblacklist users!**")

        target_id = None
        if message.reply_to_message and message.reply_to_message.from_user:
            target_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            query = message.command[1].strip()
            try:
                if query.isdigit():
                    target_id = int(query)
                else:
                    user_obj = await client.get_users(query)
                    target_id = user_obj.id if user_obj else None
            except Exception:
                pass

        if not target_id:
            return await message.reply(
                "⚠️ **Incorrect Usage!**\n"
                "• Reply to a user with `/unblacklistuser`\n"
                "• Or use `/unblacklistuser <user_id>`"
            )

        chat_id = message.chat.id

        try:
            result = await db.chat_user_blacklist.delete_one({"chat_id": chat_id, "user_id": target_id})
            # Also unban them from the chat group restriction list
            await client.unban_chat_member(chat_id, target_id)

            if result.deleted_count > 0:
                await message.reply(f"✅ **Successfully removed user (`{target_id}`) from the group blacklist and unbanned them!**")
            else:
                await message.reply(f"⚠️ **User (`{target_id}`) was not found in the group blacklist.**")
        except Exception as e:
            logging.error(f"[Unblacklist User Error]: {e}")
            await message.reply("❌ **Failed to remove user from blacklist.**")

    # ============================================================
    # 📋 LIST BLACKLISTED USERS (`/blacklistedusers`)
    # ============================================================
    @app.on_message(filters.command(["blacklistedusers", "blusers"]) & filters.group)
    async def list_blacklisted_users_cmd(client, message: Message):
        chat_id = message.chat.id

        try:
            cursor = db.chat_user_blacklist.find({"chat_id": chat_id})
            b_users = [doc async for doc in cursor]

            if not b_users:
                return await message.reply("📭 **No blacklisted users in this group.**")

            formatted_list = ""
            for idx, user in enumerate(b_users, 1):
                name = user.get("name", "Unknown")
                u_id = user.get("user_id")
                uname = f"@{user.get('username')}" if user.get("username") else "No Username"
                formatted_list += f"{idx}. **{name}** (`{u_id}`) — {uname}\n"

            text = (
                f"🚫 **Nomad Bot — Blacklisted Users List:**\n\n"
                f"{formatted_list}\n"
                f"_These users are permanently banned from the chat._"
            )
            await message.reply_text(text)
        except Exception as e:
            logging.error(f"[List Blacklisted Users Error]: {e}")
            await message.reply("❌ **Failed to fetch blacklisted users list.**")

    # ============================================================
    # ⚡ AUTO-BAN WATCHER FOR REJOINING BLACKLISTED USERS
    # ============================================================
    @app.on_message(filters.new_chat_members & filters.group, group=4)
    async def blacklisted_user_auto_ban(client, message: Message):
        chat_id = message.chat.id

        try:
            for new_member in message.new_chat_members:
                if not new_member:
                    continue

                # Check if user exists in the group's blacklist database
                doc = await db.chat_user_blacklist.find_one({"chat_id": chat_id, "user_id": new_member.id})
                if doc:
                    await client.ban_chat_member(chat_id, new_member.id)
                    await message.reply(
                        f"🚨 **Blacklisted User Detected & Banned Automatically!**\n"
                        f"👤 **User:** {new_member.mention} (`{new_member.id}`)\n"
                        f"_This user is blacklisted from this group chat._",
                        disable_web_page_preview=True
                    )
        except Exception as e:
            logging.error(f"[Blacklisted User Auto-Ban Error]: {e}")
