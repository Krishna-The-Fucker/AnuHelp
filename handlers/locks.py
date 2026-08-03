# ============================================================
# 🔒 LOCK SYSTEM (ULTIMATE ROSE STYLE & FULL POWER)
# ============================================================

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
import re

# ============================================================
# 🔐 AVAILABLE LOCKS (ROSE STYLE COMPREHENSIVE LIST)
# ============================================================

LOCK_TYPES = [
    "all", "media", "photo", "video", "audio", "voice",
    "document", "sticker", "gif", "animation",
    "link", "url", "forward", "bots", "bot",
    "inline", "game", "location", "contact",
    "poll", "service", "text", "hashtag", "audio"
]

def register_lock_system(app, db):

    # ============================================================
    # 🔧 ADMIN CHECK (ROSE STYLE ROBUST)
    # ============================================================
    async def is_admin(client, chat_id, user_id):
        if not user_id:
            return False
        try:
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except:
            return False

    # ============================================================
    # 🗄️ DB FUNCTIONS
    # ============================================================
    async def set_lock(chat_id: int, lock_type: str, status: bool):
        await db.locks.update_one(
            {"chat_id": chat_id},
            {"$set": {lock_type: status}},
            upsert=True
        )

    async def get_locks(chat_id: int) -> dict:
        data = await db.locks.find_one({"chat_id": chat_id})
        return data if data else {}

    # ============================================================
    # 🔒 LOCK COMMAND
    # ============================================================
    @app.on_message(filters.command("lock") & filters.group)
    async def lock_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        if len(message.command) < 2:
            return await message.reply_text(
                "❌ **Incorrect usage!**\n"
                "• Usage: `/lock <type>`\n"
                "• Example: `/lock link` or `/lock sticker`"
            )

        lock_type = message.command[1].lower()

        if lock_type not in LOCK_TYPES:
            return await message.reply_text(
                f"❌ **Invalid lock type:** `{lock_type}`\n"
                f"Use `/locks` to view all available lock types."
            )

        await set_lock(message.chat.id, lock_type, True)
        await message.reply_text(f"🔒 **Locked Successfully:** `{lock_type}` 🟢")

    # ============================================================
    # 🔓 UNLOCK COMMAND
    # ============================================================
    @app.on_message(filters.command("unlock") & filters.group)
    async def unlock_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        if len(message.command) < 2:
            return await message.reply_text(
                "❌ **Incorrect usage!**\n"
                "• Usage: `/unlock <type>`\n"
                "• Example: `/unlock link`"
            )

        lock_type = message.command[1].lower()

        if lock_type not in LOCK_TYPES:
            return await message.reply_text(f"❌ **Invalid lock type:** `{lock_type}`")

        await set_lock(message.chat.id, lock_type, False)
        await message.reply_text(f"🔓 **Unlocked Successfully:** `{lock_type}` 🔴")

    # ============================================================
    # 📊 LOCK STATUS PANEL (ROSE STYLE)
    # ============================================================
    @app.on_message(filters.command("locks") & filters.group)
    async def locks_status(client, message: Message):
        data = await get_locks(message.chat.id)

        text = "🔒 **Current Group Locks Status:**\n\n"
        
        # Display main structured locks
        main_locks = ["all", "media", "photo", "video", "sticker", "link", "forward", "bots", "text", "poll", "game", "inline"]
        
        for lock in main_locks:
            status = "🔒 Locked" if data.get(lock) else "🔓 Unlocked"
            icon = "🔴" if data.get(lock) else "🟢"
            text.format()
            text += f"• **{lock.capitalize()}**: {status} {icon}\n"

        text += "\n_Use `/lock <type>` or `/unlock <type>` to change settings._"

        await message.reply_text(text)

    # ============================================================
    # 🚫 LINK & TEXT PATTERN DETECTION
    # ============================================================
    LINK_REGEX = re.compile(r"(https?://|t\.me/|www\.|[a-zA-Z0-9][-a-zA-Z0-90-9]*\.[a-zA-Z]{2,}(/.*)?)")

    def has_link(text):
        return bool(text and LINK_REGEX.search(text))

    # ============================================================
    # 🚨 ULTIMATE LOCK AUTO-FILTER (POWERFUL ENGINE)
    # ============================================================
    @app.on_message(filters.group & ~filters.service, group=5)
    async def lock_filter(client, message: Message):
        if not message.from_user:
            return

        # Skip check for group admins
        if await is_admin(client, message.chat.id, message.from_user.id):
            return

        locks = await get_locks(message.chat.id)
        if not locks:
            return

        should_delete = False

        # 1. GLOBAL LOCK (ALL)
        if locks.get("all"):
            should_delete = True

        # 2. MEDIA LOCKS
        elif locks.get("media") and message.media:
            should_delete = True
        elif locks.get("photo") and message.photo:
            should_delete = True
        elif locks.get("video") and message.video:
            should_delete = True
        elif locks.get("audio") and message.audio:
            should_delete = True
        elif locks.get("voice") and message.voice:
            should_delete = True
        elif locks.get("document") and message.document:
            should_delete = True
        elif locks.get("sticker") and message.sticker:
            should_delete = True
        elif (locks.get("gif") or locks.get("animation")) and message.animation:
            should_delete = True

        # 3. TEXT & LINK LOCKS
        elif locks.get("text") and message.text:
            should_delete = True
        elif (locks.get("link") or locks.get("url")) and (has_link(message.text) or has_link(message.caption)):
            should_delete = True
        elif locks.get("hashtag") and message.text and "#" in message.text:
            should_delete = True

        # 4. FORWARD & BOTS LOCKS
        elif locks.get("forward") and message.forward_date:
            should_delete = True
        elif (locks.get("bots") or locks.get("bot")) and message.from_user.is_bot:
            should_delete = True
        elif locks.get("inline") and message.via_bot:
            should_delete = True

        # 5. MISC LOCKS (POLL, GAME, LOCATION, CONTACT)
        elif locks.get("contact") and message.contact:
            should_delete = True
        elif locks.get("location") and message.location:
            should_delete = True
        elif locks.get("poll") and message.poll:
            should_delete = True
        elif locks.get("game") and message.game:
            should_delete = True

        # ========================================================
        # 🗑️ EXECUTE DELETION
        # ========================================================
        if should_delete:
            try:
                await message.delete()
            except Exception:
                pass
