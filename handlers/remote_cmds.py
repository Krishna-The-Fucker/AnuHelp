# ============================================================
# 🌐 REMOTE COMMANDS & SYSTEM MONITORING MODULE (DEVELOPER 👑)
# ============================================================

__mod_name__ = "🌐 ʀᴇᴍᴏᴛᴇ"

__help__ = """
*🌐 ʀᴇᴍᴏᴛᴇ ᴄᴏᴍᴍᴀɴᴅꜱ & ᴍᴏɴɪᴛᴏʀɪɴɢ* — Monitor server health, disk usage, memory, and execute remote maintenance operations (Restricted to Owner/Devs).

• `/sysinfo` — Get comprehensive server system specs (CPU, RAM, Disk, Uptime).
• `/restart` — Restart the bot container/process safely.
• `/update` — Pull the latest updates from Git and restart.
"""

from pyrogram import filters
from pyrogram.types import Message
import psutil
import platform
import shutil
import os
import sys
import subprocess
import asyncio
from datetime import datetime
from config import DEV_LIST, OWNER_ID

def register_remote_system(app):

    # ============================================================
    # 📊 SYSTEM STATS & MONITORING (`/sysinfo`)
    # ============================================================
    @app.on_message(filters.command("sysinfo") & filters.user(DEV_LIST + [OWNER_ID]))
    async def system_info_cmd(client, message: Message):
        status_msg = await message.reply("🔄 **Fetching server statistics...**")

        try:
            # CPU Stats
            cpu_usage = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=True)
            
            # Memory Stats
            ram = psutil.virtual_memory()
            ram_total = round(ram.total / (1024 ** 3), 2)
            ram_used = round(ram.used / (1024 ** 3), 2)
            ram_percent = ram.percent

            # Disk Stats
            disk = shutil.disk_usage("/")
            disk_total = round(disk.total / (1024 ** 3), 2)
            disk_used = round(disk.used / (1024 ** 3), 2)
            disk_percent = round((disk.used / disk.total) * 100, 2)

            # System Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

            info_text = (
                f"🖥️ **SERVER HARDWARE & SYSTEM STATUS**\n\n"
                f"• **Platform:** `{platform.system()} {platform.release()}`\n"
                f"• **Python Version:** `{platform.python_version()}`\n"
                f"• **System Boot Time:** `{boot_time}`\n\n"
                f"⚡ **CPU Cores:** `{cpu_count}`\n"
                f"• **CPU Usage:** `{cpu_usage}%`\n\n"
                f"🧠 **RAM Usage:** `{ram_used}GB / {ram_total}GB` (`{ram_percent}%`)\n\n"
                f"💾 **Disk Storage:** `{disk_used}GB / {disk_total}GB` (`{disk_percent}%`)\n"
                f"• **Bot Status:** `🟢 Online & Healthy`"
            )

            await status_msg.edit_text(info_text)

        except Exception as e:
            await status_msg.edit_text(f"❌ **Failed to fetch system info:** `{str(e)}`")

    # ============================================================
    # 🔄 RESTART BOT (`/restart`)
    # ============================================================
    @app.on_message(filters.command("restart") & filters.user(DEV_LIST + [OWNER_ID]))
    async def restart_bot_cmd(client, message: Message):
        await message.reply("🔄 **Restarting bot process... Please wait.**")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # ============================================================
    # 📥 GIT UPDATE & RELOAD (`/update`)
    # ============================================================
    @app.on_message(filters.command("update") & filters.user(DEV_LIST + [OWNER_ID]))
    async def update_bot_cmd(client, message: Message):
        status_msg = await message.reply("📥 **Checking for updates from repository...**")
        
        try:
            process = await asyncio.create_subprocess_shell(
                "git pull",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            output = stdout.decode().strip()
            
            if "Already up to date." in output:
                return await status_msg.edit_text("✅ **Bot is already running the latest version! No updates found.**")
            
            await status_msg.edit_text(
                f"📥 **Repository updated successfully!**\n\n```bash\n{output}\n```\n\n🔄 **Restarting bot to apply changes...**"
            )
            os.execl(sys.executable, sys.executable, *sys.argv)

        except Exception as e:
            await status_msg.edit_text(f"❌ **Update failed:** `{str(e)}`")
