# ============================================================
# 🚫 FULL AI Anti-NSFW SYSTEM (ULTIMATE PRO VERSION)
# ============================================================

__mod_name__ = "𝐀ɴᴛɪ-𝐍sғᴡ🛡️"

__help__ = """
*𝐀ɴᴛɪ-𝐍sғᴡ🛡️* — Protect your group from porn content with AI detection      

• `/antiporn` — Toggle anti-NSFW      
• `/nsfwstatus` — Check system status      

Auto deletes NSFW media + warns user.  
"""

# ============================================================
import os
import cv2
import time
import logging
import imageio
from pyrogram import filters
from pyrogram.types import Message, ChatPermissions

# Project ke centralized db structure ke sath sync kiya gaya hai
from db import db
from nudenet import NudeClassifier

# ============================================================
# 📁 INIT
# ============================================================

os.makedirs("downloads", exist_ok=True)

logging.basicConfig(level=logging.INFO)

# ============================================================
# 🧠 CLASSIFIER (Singleton Load)
# ============================================================

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        _classifier = NudeClassifier()
    return _classifier

# ============================================================
# 🗄️ DATABASE COLLECTIONS
# ============================================================

settings_db = db.antiporn_settings
warn_db = db.antiporn_warns

# ============================================================
# ⚙️ DEFAULT SETTINGS
# ============================================================

DEFAULT = {
    "enabled": True,
    "warn_limit": 3,
    "action": "mute"  # mute / ban
}

# ============================================================
# 📦 LOAD SETTINGS
# ============================================================

async def get_settings(chat_id):
    data = await settings_db.find_one({"chat_id": chat_id})

    if not data:
        new = DEFAULT.copy()
        new["chat_id"] = chat_id
        await settings_db.insert_one(new)
        return new

    return data

# ============================================================
# 🧠 IMAGE SCAN (FAST)
# ============================================================

def scan_image(path):
    try:
        img = cv2.imread(path)
        img = cv2.resize(img, (320, 320))

        temp = f"{path}_small.jpg"
        cv2.imwrite(temp, img)

        classifier = get_classifier()
        result = classifier.classify(temp)

        os.remove(temp)

        score = list(result.values())[0]
        return score["unsafe"] > 0.80

    except Exception as e:
        logging.error(f"Image scan error: {e}")
        return False

# ============================================================
# 🎥 VIDEO SCAN
# ============================================================

def scan_video(path):
    cap = cv2.VideoCapture(path)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Every 30th frame
        if frame_count % 30 == 0:
            temp = f"{path}_frame.jpg"
            cv2.imwrite(temp, frame)

            if scan_image(temp):
                os.remove(temp)
                cap.release()
                return True

            os.remove(temp)

        frame_count += 1

    cap.release()
    return False

# ============================================================
# 🎞️ GIF SCAN
# ============================================================

def scan_gif(path):
    try:
        frames = imageio.mimread(path)

        for i, frame in enumerate(frames):
            if i % 5 == 0:
                temp = f"{path}_gif.jpg"
                imageio.imwrite(temp, frame)

                if scan_image(temp):
                    os.remove(temp)
                    return True

                os.remove(temp)

        return False

    except Exception as e:
        logging.error(f"GIF scan error: {e}")
        return False

# ============================================================
# ⚔️ ACTION SYSTEM
# ============================================================

async def take_action(message, settings):
    user_id = message.from_user.id
    chat_id = message.chat.id

    data = await warn_db.find_one({"user_id": user_id, "chat_id": chat_id})
    count = data["count"] + 1 if data else 1

    await warn_db.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"count": count}},
        upsert=True
    )

    # Punishment
    if count >= settings["warn_limit"]:
        if settings["action"] == "mute":
            await message.chat.restrict_member(
                user_id,
                ChatPermissions(),
                until_date=int(time.time()) + 300
            )
        elif settings["action"] == "ban":
            await message.chat.ban_member(user_id)

    await message.reply_text(
        f"""
🚫 **NSFW Content Detected!**

👤 {message.from_user.mention}
⚠️ Warn: `{count}/{settings['warn_limit']}`
"""
    )

# ============================================================
# 🔥 HANDLER & COMMANDS REGISTRATION
# ============================================================

def register_antiporn_system(app):

    # -------------------------
    # 📥 MEDIA CHECK HANDLER
    # -------------------------
    @app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=5)
    async def antiporn_handler(client, message: Message):
        if not message.from_user:
            return

        settings = await get_settings(message.chat.id)

        if not settings.get("enabled", True):
            return

        # 🛡️ Skip Admins
        try:
            member = await message.chat.get_member(message.from_user.id)
            if member.status in ["administrator", "creator"]:
                return
        except:
            pass

        file_path = None
        detected = False

        try:
            # 📥 Download media
            if message.photo:
                file_path = await message.download(f"downloads/{message.id}.jpg")
                detected = scan_image(file_path)

            elif message.video:
                file_path = await message.download(f"downloads/{message.id}.mp4")
                detected = scan_video(file_path)

            elif message.animation:
                file_path = await message.download(f"downloads/{message.id}.gif")
                detected = scan_gif(file_path)

            elif message.sticker:
                file_path = await message.download(f"downloads/{message.id}.webp")
                detected = scan_image(file_path)

        except Exception as e:
            logging.error(f"Download/Scan error: {e}")

        finally:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)

        if not detected:
            return

        # ❌ Delete message
        try:
            await message.delete()
        except:
            pass

        await take_action(message, settings)

    # -------------------------
    # ⚙️ /antiporn COMMAND
    # -------------------------
    @app.on_message(filters.command("antiporn") & filters.group)
    async def toggle_antiporn(client, message: Message):
        data = await get_settings(message.chat.id)
        new = not data.get("enabled", True)

        await settings_db.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": new}},
            upsert=True
        )

        await message.reply_text(
            f"🛡️ Anti-NSFW {'Enabled 🟢' if new else 'Disabled 🔴'}"
        )

    # -------------------------
    # 📊 /nsfwstatus COMMAND
    # -------------------------
    @app.on_message(filters.command("nsfwstatus") & filters.group)
    async def status(client, message: Message):
        data = await get_settings(message.chat.id)

        await message.reply_text(
            f"""
🛡️ **Anti-NSFW Status**

• Enabled: `{data.get('enabled', True)}`
• Warn Limit: `{data.get('warn_limit', 3)}`
• Action: `{data.get('action', 'mute')}`
"""
        )
