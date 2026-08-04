# ============================================================
# 🛠️ MISCELLANEOUS UTILITIES & EXTRA TOOLS MODULE
# ============================================================

__mod_name__ = "🛠️ ᴍɪꜱᴄ"

__help__ = """
*🛠️ ᴍɪꜱᴄᴇʟʟᴀɴᴇᴏᴜꜱ ᴜᴛɪʟɪᴛɪᴇꜱ* — A collection of handy utility commands ranging from ID lookup to text formatting and pinging.

• `/id` — Get your user ID, the chat ID, or the replied user's ID.
• `/ping` — Check the bot's response latency/speed.
• `/info` — Get user information and account details.
• `/stats` — View general bot statistics and database metrics.
"""

from pyrogram import filters
from pyrogram.types import Message
import time
from datetime import datetime
from db import db

def register_misc_system(app):

    # ============================================================
    # 🆔 ID LOOKUP (`/id`)
    # ============================================================
    @app.on_message(filters.command("id"))
    async def get_id_cmd(client, message: Message):
        chat = message.chat
        user = message.from_user
        reply = message.reply_to_message

        text = f"🆔 **IDENTIFICATION SYSTEM**\n\n"
        
        if reply and reply.from_user:
            r_user = reply.from_user
            text += f"👤 **Replied User Name:** `{r_user.first_name}`\n"
            text += f"🆔 **Replied User ID:** `{r_user.id}`\n\n"

        text += f"💬 **Chat Title:** `{chat.title if chat.type.name != 'PRIVATE' else 'Private Chat'}`\n"
        text += f"📌 **Chat ID:** `{chat.id}`\n\n"
        
        if user:
            text += f"🙋‍♂️ **Your Name:** `{user.first_name}`\n"
            text += f"🔑 **Your User ID:** `{user.id}`"

        await message.reply(text)

    # ============================================================
    # 🏓 PING SPEED TEST (`/ping`)
    # ============================================================
    @app.on_message(filters.command("ping"))
    async def ping_cmd(client, message: Message):
        start_time = time.time()
        ping_msg = await message.reply("🏓 **Pinging...**")
        end_time = time.time()
        
        latency = round((end_time - start_time) * 1000, 2)
        await ping_msg.edit_text(f"🏓 **Pong!**\nLatency: `{latency}ms` ⚡")

    # ============================================================
    # ℹ️ USER INFO (`/info`)
    # ============================================================
    @app.on_message(filters.command("info"))
    async def user_info_cmd(client, message: Message):
        target_user = message.from_user
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user

        if not target_user:
            return await message.reply("⚠️ **Could not fetch user information!**")

        info_text = (
            f"👤 **USER INFORMATION SUMMARY**\n\n"
            f"• **First Name:** `{target_user.first_name}`\n"
            f"• **Last Name:** `{target_user.last_name or 'None'}`\n"
            f"• **Username:** `@{target_user.username}` if target_user.username else 'None'\n"
            f"• **User ID:** `{target_user.id}`\n"
            f"• **Is Bot:** `{target_user.is_bot}`\n"
            f"• **DC ID:** `{target_user.dc_id or 'Unknown'}`"
        )
        await message.reply(info_text)

    # ============================================================
    # 📊 BOT STATISTICS (`/stats`)
    # ============================================================
    @app.on_message(filters.command("stats"))
    async def bot_stats_cmd(client, message: Message):
        status_msg = await message.reply("📊 **Gathering database metrics...**")

        try:
            users_count = await db.users.count_documents({})
            chats_count = await db.language.count_documents({})
            warns_count = await db.warns.count_documents({})

            stats_text = (
                f"📈 **NOMAD BOT SYSTEM STATISTICS**\n\n"
                f"• **Registered Users:** `{users_count}`\n"
                f"• **Active Groups:** `{chats_count}`\n"
                f"• **Active Warnings Logged:** `{warns_count}`\n"
                f"• **Status:** `🟢 Optimal & Operational`"
            )
            await status_msg.edit_text(stats_text)

        except Exception as e:
            await status_msg.edit_text(f"❌ **Failed to load stats:** `{str(e)}`")
