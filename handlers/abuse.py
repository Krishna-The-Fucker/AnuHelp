# ============================================================
# 🚫 ABUSE FILTER SYSTEM (PRO MAX VERSION)
# ============================================================

import re
from pyrogram import filters
from pyrogram.types import ChatPermissions
from datetime import datetime, timedelta

# Project ke centralized db structure ke sath sync kiya gaya hai
from db import db

# Database Collections mapping (agar required ho toh direct use ke liye)
abuse_settings = db.abuse_settings
group_abuse_db = db.group_abuse_words
global_abuse_db = db.global_abuse_words
warns_db = db.abuse_warns

# ==========================================================
# 🔥 DEFAULT ABUSE WORD LIST
# ==========================================================

ABUSE_WORDS = [
    "madarchod", "bhenchod", "gandu", "chutiya", "randi",
    "mc", "bc", "bsdk", "lund", "chodu",
    "fuck", "bitch", "asshole", "bastard", "dick",
    "harami", "kamina", "kuttiya", "gand"
]

# ==========================================================
# 🧠 INTELLIGENT NORMALIZER
# ==========================================================

def normalize_text(text: str) -> str:
    text = text.lower()

    # remove spaces
    text = re.sub(r"\s+", "", text)

    # replace symbols
    replacements = {
        "@": "a", "0": "o", "1": "i", "$": "s", "3": "e", "7": "t"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # remove repeated letters
    text = re.sub(r"(.)\1+", r"\1", text)

    return text


# ==========================================================
# 🔥 HANDLER & COMMANDS REGISTRATION
# ==========================================================
def register_abuse_filter(app):

    # 🛡️ ADMIN CHECK HELPER
    async def is_admin(chat_id, user_id):
        try:
            member = await app.get_chat_member(chat_id, user_id)
            return member.status in ["administrator", "creator"]
        except:
            return False

    # 📊 DATABASE MOCK HELPERS (Agar db.py mein alag se defined nahi hain toh yahan handled hain)
    async def get_admins(chat_id):
        return []

    async def get_global_abuse():
        docs = await global_abuse_db.find().to_list(length=None)
        return [d["word"] for d in docs] if docs else []

    async def get_group_abuse(chat_id):
        docs = await group_abuse_db.find({"chat_id": chat_id}).to_list(length=None)
        return [d["word"] for d in docs] if docs else []

    async def add_group_abuse(chat_id, word):
        await group_abuse_db.update_one(
            {"chat_id": chat_id, "word": word},
            {"$set": {"chat_id": chat_id, "word": word}},
            upsert=True
        )

    async def remove_group_abuse(chat_id, word):
        await group_abuse_db.delete_one({"chat_id": chat_id, "word": word})

    async def add_warn(chat_id, user_id):
        res = await warns_db.find_one_and_update(
            {"chat_id": chat_id, "user_id": user_id},
            {"$inc": {"count": 1}},
            upsert=True,
            return_document=True
        )
        return res.get("count", 1)

    async def get_warn_limit(chat_id):
        return 3  # Default limit agar set na ho

    async def add_log(chat_id, action, user_id):
        pass  # Optional logging layer

    # 🚨 MAIN ABUSE FILTER HANDLER
    @app.on_message(filters.group & filters.text & ~filters.bot, group=3)
    async def abuse_filter(client, message):
        if not message.text or not message.from_user:
            return

        raw_text = message.text.lower()
        text = normalize_text(raw_text)

        chat_id = message.chat.id
        user_id = message.from_user.id

        # Admin check
        is_admin_user = await is_admin(chat_id, user_id)

        # Load DB words
        global_words = await get_global_abuse()
        group_words = await get_group_abuse(chat_id)

        ALL_WORDS = list(set(ABUSE_WORDS + global_words + group_words))

        if not ALL_WORDS:
            return

        abuse_regex = re.compile(
            r"\b(" + "|".join(map(re.escape, ALL_WORDS)) + r")\b",
            re.IGNORECASE
        )

        found = abuse_regex.search(raw_text) or abuse_regex.search(text)

        if not found:
            return

        # ❌ DELETE MESSAGE
        try:
            await message.delete()
        except:
            pass

        # 🔥 ADMIN CASE
        if is_admin_user:
            await message.reply_text(
                f"⚠️ Admin {message.from_user.mention}, abuse is not allowed!",
                quote=True
            )
            return

        # =========================
        # 👤 NORMAL USER FLOW
        # =========================

        warn_count = await add_warn(chat_id, user_id)
        warn_limit = await get_warn_limit(chat_id)

        action = "⚠️ Warning"

        if warn_count >= warn_limit:
            try:
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions(),
                    until_date=datetime.now() + timedelta(minutes=10)
                )
                action = "🔇 Muted (10 min)"
            except:
                action = "❌ Mute Failed"

        await add_log(chat_id, action, user_id)

        await message.reply_text(
            f"""
╭─❖ 𝗔𝗕𝗨𝗦𝗘 𝗦𝗬𝗦𝗧𝗘𝗠 ❖─╮
│ 👤 User: {message.from_user.mention}
│ 📊 Warns: {warn_count}/{warn_limit}
│ ⚡ Action: {action}
╰────────────────────╯
""",
            quote=True
        )

    # ⚙️ COMMAND: ADD GROUP ABUSE
    @app.on_message(filters.command("addabuse") & filters.group)
    async def add_abuse_word(client, message):
        if len(message.command) < 2:
            return await message.reply("⚠️ Usage: `/addabuse word`")

        word = message.command[1].lower()
        await add_group_abuse(message.chat.id, word)

        await message.reply(f"✅ Added to group abuse list:\n`{word}`")

    # ⚙️ COMMAND: REMOVE GROUP ABUSE
    @app.on_message(filters.command("delabuse") & filters.group)
    async def remove_abuse_word(client, message):
        if len(message.command) < 2:
            return await message.reply("⚠️ Usage: `/delabuse word`")

        word = message.command[1].lower()
        await remove_group_abuse(message.chat.id, word)

        await message.reply(f"❌ Removed from group abuse list:\n`{word}`")
