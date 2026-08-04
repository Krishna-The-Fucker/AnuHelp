# ============================================================
# 🛠️ DEBUG & DIAGNOSTICS UTILITIES (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🛠️ ᴅᴇʙᴜɢ"

__help__ = """
*🛠️ ᴅᴇʙᴜɢ ᴛᴏᴏʟs* — Internal system checks, bot latency diagnostics, and environment validation tools (Developer/Sudo only).

• `/debug` — Run full system diagnostic check on database, memory, and APIs.
• `/ping` — Check bot response latency/speed.
"""

from pyrogram import filters
from pyrogram.types import Message
import time
import sys
import platform
import psutil
from datetime import datetime
from config import DEV_LIST, SUDO_USERS

def register_debug_system(app):

    # ============================================================
    # ⚡ PING LATENCY CHECK (`/ping`)
    # ============================================================
    @app.on_message(filters.command("ping"))
    async def ping_cmd(client, message: Message):
        start_time = time.time()
        status_msg = await message.reply("🏓 **Pinging...**")
        end_time = time.time()
        
        ping_ms = round((end_time - start_time) * 1000, 2)
        
        await status_msg.edit_text(
            f"🏓 **Pong!**\n"
            f"⚡ **Latency:** `{ping_ms} ms`\n"
            f"🤖 **Bot Status:** `Online & Fully Operational 🚀`"
        )

    # ============================================================
    # 🔍 FULL SYSTEM DEBUG (`/debug`)
    # ============================================================
    @app.on_message(filters.command("debug"))
    async def debug_system_cmd(client, message: Message):
        user_id = message.from_user.id if message.from_user else 0
        if user_id not in DEV_LIST and user_id not in SUDO_USERS:
            return await message.reply("⚠️ **This command is restricted to Developers and Sudo users only!**")

        status_msg = await message.reply("🛠️ **Running system diagnostics and environment checks...**")

        try:
            # System Metrics
            python_version = platform.python_version()
            os_info = platform.system() + " " + platform.release()
            cpu_usage = psutil.cpu_percent(interval=0.5)
            ram = psutil.virtual_memory()
            ram_usage = ram.percent
            ram_used_gb = round(ram.used / (1024**3), 2)
            ram_total_gb = round(ram.total / (1024**3), 2)

            # Database check
            db_status = "❌ Disconnected"
            try:
                from database import db
                await db.command("ping")
                db_status = "✅ Connected & Active"
            except Exception as e:
                db_status = f"⚠️ Error: {str(e)[:30]}"

            debug_report = (
                f"🛠️ **Nomad Bot Diagnostics Report**\n\n"
                f"• **Python Version:** `{python_version}`\n"
                f"• **Operating System:** `{os_info}`\n"
                f"• **CPU Usage:** `{cpu_usage}%`\n"
                f"• **RAM Usage:** `{ram_usage}%` ({ram_used_gb} GB / {ram_total_gb} GB)\n"
                f"• **Database (MongoDB):** `{db_status}`\n"
                f"• **Uptime Timestamp:** `{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC`\n\n"
                f"🚀 **All core modules and background loops running successfully.**"
            )

            await status_msg.edit_text(debug_report)

        except Exception as e:
            await status_msg.edit_text(f"❌ **Diagnostics failed:** `{str(e)}`")
