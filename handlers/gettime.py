# ============================================================
# ⏰ GETTIME / WORLD CLOCK UTILITY (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "⏰ ᴛɪᴍᴇ"

__help__ = """
*⏰ ᴛɪᴍᴇ & ᴅᴀᴛᴇ sʏsᴛᴇᴍ* — Quick utility to check current times, dates, and world timezones instantly!

• `/time` or `/date` — Get current UTC time and date details
• `/ctime <timezone/country>` — Check current time for a specific country or timezone (e.g., `/ctime India`, `/ctime America/New_York`, `/ctime Tokyo`)
"""

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime, timezone
import pytz

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
            f"⏱️ **AnuHelp — Time & Date Center**\n\n"
            f"📅 **Date:** `{current_date}`\n"
            f"⏰ **Time (UTC):** `{current_time}`\n"
            f"🌐 **Timezone:** `Coordinated Universal Time (UTC)`"
        )
        
        await message.reply_text(text)

    # ============================================================
    # 🌍 WORLD CLOCK / COUNTRY TIME UTILITY (`/ctime`)
    # ============================================================
    @app.on_message(filters.command("ctime"))
    async def country_time_cmd(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text(
                "⚠️ **Incorrect Usage!**\n"
                "• Usage: `/ctime <country or timezone>`\n"
                "• Example: `/ctime India` or `/ctime America/New_York` or `/ctime Tokyo`"
            )

        query = message.command[1].strip().lower()
        
        # Common Country/City Shortcuts Mapping
        aliases = {
            "india": "Asia/Kolkata",
            "pakistan": "Asia/Karachi",
            "usa": "America/New_York",
            "us": "America/New_York",
            "uk": "Europe/London",
            "london": "Europe/London",
            "japan": "Asia/Tokyo",
            "tokyo": "Asia/Tokyo",
            "dubai": "Asia/Dubai",
            "uae": "Asia/Dubai",
            "china": "Asia/Shanghai",
            "russia": "Europe/Moscow",
            "germany": "Europe/Berlin",
            "france": "Europe/Paris",
            "canada": "America/Toronto",
            "australia": "Australia/Sydney",
            "sri lanka": "Asia/Colombo",
            "bangladesh": "Asia/Dhaka",
            "nepal": "Asia/Kathmandu"
        }

        tz_name = aliases.get(query)
        
        # If not in shortcuts, try searching exact pytz timezones case-insensitively
        if not tz_name:
            matching_tzs = [tz for tz in pytz.all_timezones if query in tz.lower()]
            if matching_tzs:
                tz_name = matching_tzs[0]

        if not tz_name:
            return await message.reply_text(
                f"❌ **Timezone not found for `{query}`!**\n"
                "Please provide a valid country name (e.g., `India`, `USA`, `Dubai`) or standard timezone format (e.g., `Asia/Kolkata`)."
            )

        try:
            target_tz = pytz.timezone(tz_name)
            target_time = datetime.now(target_tz)
            
            c_time = target_time.strftime("%H:%M:%S")
            c_date = target_time.strftime("%A, %B %d, %Y")
            c_offset = target_time.strftime("%Z (UTC %z)")

            text = (
                f"🌍 **World Clock — {tz_name}**\n\n"
                f"📅 **Date:** `{c_date}`\n"
                f"⏰ **Time:** `{c_time}`\n"
                f"🌐 **Timezone:** `{c_offset}`"
            )
            await message.reply_text(text)
        except Exception as e:
            await message.reply_text(f"❌ **Error fetching time:** `{str(e)}`")
