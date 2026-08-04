# ============================================================
# ⏰ GETTIME / TIME & DATE UTILITY (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "⏰ ᴛɪᴍᴇ"

__help__ = """
*⏰ ᴛɪᴍᴇ & ᴅᴀᴛᴇ sʏsᴛᴇᴍ* — Quick utility to check current times, dates, timezones, and ping responses instantly!

• `/time` or `/date` — Get current UTC time and date details
• `/ping` — Check bot latency and response time
"""

from pyrogram import filters
from pyrogram.types import Message
import time
from datetime import datetime, timezone

def register_gettime_system(app, OWNER_ID):

    # ============================================================
    # ⏰ GETTIME / DATE COMMAND (`/time`, `/date`, `/clock`)
    # ============================================================
    @app.on_message(filters.command(["time", "date", "clock", "utcnow"]))
    async def get_time_cmd(client, message: Message):
        now_utc = datetime.now(timezone.utc)
        
        current_time = now_utc.strftime("%H:%M:%S")
        current_date = now_utc.strftime("%A, %B %d, %Y")
        
        text = (
            f"⏱️ **Nomad Bot — Time & Date Center**\n\n"
            f"📅 **Date:** `{current_date}`\n"
            f"⏰ **Time (UTC):** `{current_time}`\n"
            f"🌐 **Timezone:** `Coordinated Universal Time (UTC)`"
        )
        
        await message.reply_text(text)

    # ============================================================
    # ⚡ PING LATENCY UTILITY (`/ping`)
    # ============================================================
    @app.on_message(filters.command("ping"))
    async def ping_cmd(client, message: Message):
        start_time = time.time()
        sent_msg = await message.reply_text("⚡ **Pinging...**")
        end_time = time.time()
        
        ping_ms = round((end_time - start_time) * 1000, 2)
        
        await sent_msg.edit_text(
            f"🏓 **Pong!**\n"
            f"⚡ **Latency:** `{ping_ms}ms`\n"
            f"🤖 **Status:** `Nomad Bot is fully operational & running smoothly! ✨`"
        )
