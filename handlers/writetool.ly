# ============================================================
# 🛠️ DEVELOPER & UTILS TOOLSET (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🛠️ ᴛᴏᴏʟs"

__help__ = """
*🛠️ ᴜᴛɪʟɪᴛɪᴇs & ᴛᴏᴏʟs* — Handy group management tools, ID lookups, pin generators, and developer utilities!

• `/id` — Get your ID, replied user's ID, or chat ID
• `/info` — Get detailed info about a user or replied user
• `/ping` — Check bot latency and server response time
• `/stats` — View total chats, users, and system uptime
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ParseMode
import time
import datetime
import logging

def register_writetool(app, db, START_TIME, OWNER_ID):

    # ============================================================
    # ⏱️ PING COMMAND
    # ============================================================
    @app.on_message(filters.command("ping"))
    async def ping_command(client, message: Message):
        start = time.time()
        msg = await message.reply("⚡ **Pinging...**")
        end = time.time()
        delta = round((end - start) * 1000, 2)
        
        await msg.edit_text(
            f"🏓 **Pong!**\n"
            f"• **Latency:** `{delta}ms`\n"
            f"• **Status:** `Online & Operational 🟢`"
        )

    # ============================================================
    # 🆔 ID COMMAND
    # ============================================================
    @app.on_message(filters.command("id"))
    async def id_command(client, message: Message):
        chat = message.chat
        user = message.from_user
        reply = message.reply_to_message

        text = f"🆔 **Identifier Details:**\n\n"

        if chat:
            text += f"• **Chat Title:** `{chat.title}`\n"
            text += f"• **Chat ID:** `{chat.id}`\n"
            text += f"• **Chat Type:** `{chat.type}`\n\n"

        if reply:
            target_user = reply.from_user or reply.sender_chat
            if target_user:
                id_val = target_user.id if hasattr(target_user, "id") else target_user
                name = target_user.first_name if hasattr(target_user, "first_name") else target_user.title
                text += f"• **Replied User/Sender:** `{name}`\n"
                text += f"• **Replied ID:** `{id_val}`\n\n"

        if user:
            text += f"• **Your Name:** {user.first_name}\n"
            text += f"• **Your ID:** `{user.id}`\n"

        await message.reply_text(text, disable_web_page_preview=True)

    # ============================================================
    # 👤 INFO COMMAND
    # ============================================================
    @app.on_message(filters.command("info"))
    async def info_command(client, message: Message):
        target_user = None

        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            try:
                arg = message.command[1]
                target_user = await client.get_users(int(arg) if arg.isdigit() else arg)
            except Exception:
                pass
        else:
            target_user = message.from_user

        if not target_user:
            return await message.reply("❌ **Could not fetch user information!**")

        try:
            user_full = await client.get_users(target_user.id)
            
            # Check admin status in chat if group
            status_str = "Member"
            if message.chat.type.name in ["GROUP", "SUPERGROUP"]:
                try:
                    member_info = await client.get_chat_member(message.chat.id, user_full.id)
                    if member_info.status == ChatMemberStatus.OWNER:
                        status_str = "Group Owner 👑"
                    elif member_info.status == ChatMemberStatus.ADMINISTRATOR:
                        status_str = "Administrator 🛡️"
                except Exception:
                    pass

            text = (
                f"👤 **User Information Panel:**\n\n"
                f"• **Full Name:** {user_full.first_name} {user_full.last_name or ''}\n"
                f"• **Username:** {f'@{user_full.username}' if user_full.username else 'None'}\n"
                f"• **User ID:** `{user_full.id}`\n"
                f"• **Role/Status:** `{status_str}`\n"
                f"• **Is Bot:** `{'Yes 🤖' if user_full.is_bot else 'No 👤'}`\n"
            )

            await message.reply_text(text)
        except Exception as e:
            logging.error(f"[Info Command Error]: {e}")
            await message.reply("❌ **Failed to retrieve user info.**")

    # ============================================================
    # 📊 STATS COMMAND
    # ============================================================
    @app.on_message(filters.command("stats"))
    async def stats_command(client, message: Message):
        try:
            # Calculate uptime
            uptime_seconds = int(time.time() - START_TIME)
            uptime_str = str(datetime.timedelta(seconds=uptime_seconds))

            # Fetch DB statistics safely if supported
            total_users = 0
            try:
                users_col = db.get_collection("users") if hasattr(db, "get_collection") else db.users
                total_users = await users_col.count_documents({})
            except Exception:
                pass

            text = (
                f"📊 **Bot Statistics & Uptime:**\n\n"
                f"• **Uptime:** `{uptime_str}`\n"
                f"• **Registered Users:** `{total_users}`\n"
                f"• **Core Engine:** `Pyrogram (Async)`\n"
                f"• **Database:** `MongoDB (Active)`\n"
                f"• **Status:** `All Systems Optimal ✨`"
            )

            await message.reply_text(text)
        except Exception as e:
            logging.error(f"[Stats Command Error]: {e}")
            await message.reply("❌ **Error generating bot statistics.**")
