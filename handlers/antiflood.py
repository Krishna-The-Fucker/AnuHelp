# ============================================================
# 🚫 ANTIFLOOD SYSTEM (PRO MAX VERSION)
# ============================================================

import time
import logging
from collections import defaultdict, deque
from pyrogram import filters
from pyrogram.types import Message, ChatPermissions

# Project ke centralized db structure ke sath sync kiya gaya hai
from db import db

# =========================
# ⚙️ DEFAULT SETTINGS
# =========================
DEFAULT = {
    "limit": 6,
    "window": 5,
    "mute": 60,
    "action": "mute",  # mute / kick / ban
    "enabled": True,
    "delete": True,
    "silent": False
}

settings_collection = db.antiflood_settings
flood_logs = db.flood_logs
warn_db = db.flood_warns
whitelist_db = db.whitelist_users

# =========================
# ⚡ CACHE
# =========================
user_cache = defaultdict(lambda: deque())

# =========================
# 🔧 SETTINGS
# =========================
async def get_settings(chat_id):
    data = await settings_collection.find_one({"chat_id": chat_id})

    if not data:
        default_data = DEFAULT.copy()
        default_data["chat_id"] = chat_id
        await settings_collection.insert_one(default_data)
        return default_data

    return data

# =========================
# 👑 CHECK PRIVILEGE
# =========================
async def is_protected(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)

        if member.status in ["administrator", "creator"]:
            return True

        wl = await whitelist_db.find_one({"user_id": user_id, "chat_id": chat_id})
        return bool(wl)

    except:
        return False

# =========================
# 🚫 FLOOD DETECT
# =========================
async def is_flood(user_id, chat_id):
    settings = await get_settings(chat_id)

    if not settings.get("enabled", True):
        return False

    now = time.time()
    dq = user_cache[(chat_id, user_id)]

    dq.append(now)

    window = settings.get("window", 5)
    limit = settings.get("limit", 6)

    while dq and now - dq[0] > window:
        dq.popleft()

    return len(dq) > limit

# =========================
# ⚔️ ACTION SYSTEM
# =========================
async def take_action(client, message, settings):

    user_id = message.from_user.id
    chat_id = message.chat.id

    warns = await warn_db.find_one({"user_id": user_id, "chat_id": chat_id})
    count = warns["count"] + 1 if warns else 1

    await warn_db.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"count": count}},
        upsert=True
    )

    action = settings.get("action", "mute")

    try:
        if action == "mute":
            mute_time = settings.get("mute", 60)
            duration = mute_time * count

            await message.chat.restrict_member(
                user_id,
                ChatPermissions(),
                until_date=int(time.time()) + duration
            )

        elif action == "kick":
            await message.chat.ban_member(user_id)
            await message.chat.unban_member(user_id)

        elif action == "ban":
            await message.chat.ban_member(user_id)

        if not settings.get("silent", False):
            await message.reply_text(
                f"🚫 **Flood Detected!**\n"
                f"👤 {message.from_user.mention}\n"
                f"⚠️ Warn: `{count}`\n"
                f"⚔️ Action: `{action.upper()}`"
            )

    except Exception as e:
        logging.error(f"Action error: {e}")

# =========================
# 📊 LOG
# =========================
async def save_log(chat_id, user_id):
    await flood_logs.insert_one({
        "chat_id": chat_id,
        "user_id": user_id,
        "time": time.time()
    })

# =========================
# 🔥 HANDLER & COMMANDS REGISTRATION
# =========================
def register_antiflood(app):

    # 1. Message Monitor (AntiFlood Check)
    @app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=2)
    async def antiflood_handler(client, message: Message):
        if not message.from_user:
            return

        user_id = message.from_user.id
        chat_id = message.chat.id

        # skip admins / whitelist
        if await is_protected(client, chat_id, user_id):
            return

        if await is_flood(user_id, chat_id):
            settings = await get_settings(chat_id)

            # delete message
            if settings.get("delete", True):
                try:
                    await message.delete()
                except:
                    pass

            await take_action(client, message, settings)
            await save_log(chat_id, user_id)

            user_cache[(chat_id, user_id)].clear()

    # 2. Toggle Command (/antiflood)
    @app.on_message(filters.command("antiflood") & filters.group)
    async def toggle(client, message: Message):
        data = await get_settings(message.chat.id)
        new = not data.get("enabled", True)

        await settings_collection.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": new}},
            upsert=True
        )

        await message.reply_text(f"⚙️ AntiFlood {'ON 🟢' if new else 'OFF 🔴'}")

    # 3. Set Limit Command (/setflood)
    @app.on_message(filters.command("setflood") & filters.group)
    async def set_flood(client, message: Message):
        try:
            _, l, w = message.text.split()

            await settings_collection.update_one(
                {"chat_id": message.chat.id},
                {"$set": {"limit": int(l), "window": int(w)}},
                upsert=True
            )

            await message.reply_text(f"✅ AntiFlood Limit updated: `{l}` messages in `{w}s`")
        except:
            await message.reply_text("❌ **Usage:** `/setflood <limit> <window_seconds>`\n*Example:* `/setflood 6 5`")

    # 4. Set Action Command (/setaction)
    @app.on_message(filters.command("setaction") & filters.group)
    async def set_action(client, message: Message):
        try:
            _, action = message.text.split()
            action = action.lower()

            if action not in ["mute", "kick", "ban"]:
                return await message.reply_text("❌ Allowed actions: `mute`, `kick`, `ban`")

            await settings_collection.update_one(
                {"chat_id": message.chat.id},
                {"$set": {"action": action}},
                upsert=True
            )

            await message.reply_text(f"⚔️ AntiFlood action set to: `{action.upper()}`")
        except:
            await message.reply_text("❌ **Usage:** `/setaction <mute/kick/ban>`")

    # 5. Stats Command (/floodstats)
    @app.on_message(filters.command("floodstats") & filters.group)
    async def stats(client, message: Message):
        count = await flood_logs.count_documents({"chat_id": message.chat.id})
        await message.reply_text(f"📊 Total Flood Cases Handled: `{count}`")
