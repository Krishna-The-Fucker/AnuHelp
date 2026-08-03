# ============================================================
# 🤖 AUTO DELETE + EDIT DELETE SYSTEM (ULTRA PRO MAX)
# ============================================================

__mod_name__ = "🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ"

__help__ = """
*🗑️ ᴀᴜᴛᴏ ᴅᴇʟᴇᴛᴇ & ᴇᴅɪᴛ ᴅᴇʟᴇᴛᴇ* — Automatically wipe messages after a specific time or instantly delete edited messages to prevent hidden text exploits!

• `/autodel <time> <mode>` — Set auto-delete time & mode (e.g., `/autodel 30s all`, `/autodel 5m links`)
• `/autodel off` — Disable auto-delete
• `/autodel` — Check current auto-delete status
"""

import asyncio
import re
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import FloodWait
import logging

def register_autodel(app, db=None):

    # ============================================================
    # 🧠 LOCAL STORAGE & CACHE (Fallback if db not mapped)
    # ============================================================
    auto_delete_chats = {}
    auto_delete_modes = {}
    pending_tasks = set()

    # ============================================================
    # ⏱ TIME PARSER UTILS
    # ============================================================
    def parse_time(t: str):
        t = t.lower().strip()
        m = re.match(r'^(\d+)([smhd])$', t)
        if not m:
            return None
        v, u = int(m.group(1)), m.group(2)
        return v * {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[u]

    def format_time(s: int):
        if s < 60:
            return f"{s}s"
        if s < 3600:
            return f"{s // 60}m"
        if s < 86400:
            return f"{s // 3600}h"
        return f"{s // 86400}d"

    # ============================================================
    # 🔗 LINK DETECTION REGEX
    # ============================================================
    LINK_RE = re.compile(r"(https?://|t\.me/|www\.)")

    def is_link(text):
        return bool(text and LINK_RE.search(text))

    # ============================================================
    # 🎯 FILTER MODE LOGIC
    # ============================================================
    def should_delete(msg: Message, mode):
        text = msg.text or msg.caption or ""

        if mode == "all":
            return True
        if mode == "media":
            return bool(msg.media)
        if mode == "links" or mode == "url":
            return is_link(text)
        if mode == "text":
            return bool(text and not msg.media)
        if mode == "bots":
            return bool(msg.from_user and msg.from_user.is_bot)
        if mode == "commands":
            return text.startswith("/")

        return False

    # ============================================================
    # 🗑 DELAYED DELETION TASK ENGINE
    # ============================================================
    async def delete_later(client, chat_id: int, msg_id: int, delay: int):
        task = asyncio.current_task()
        pending_tasks.add(task)

        try:
            await asyncio.sleep(delay)
            try:
                await client.delete_messages(chat_id, msg_id)
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await client.delete_messages(chat_id, msg_id)
            except Exception:
                pass
        finally:
            pending_tasks.discard(task)

    # ============================================================
    # 👑 ADMIN CHECK HELPER
    # ============================================================
    async def is_admin(client, msg: Message):
        if not msg.from_user:
            return False
        try:
            member = await client.get_chat_member(msg.chat.id, msg.from_user.id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except Exception:
            return False

    # ============================================================
    # ⚙️ COMMAND HANDLER (`/autodel`)
    # ============================================================
    @app.on_message(filters.command("autodel") & filters.group)
    async def autodel_cmd(client, msg: Message):
        if not await is_admin(client, msg):
            return await msg.reply("❌ **Only administrators can configure Auto-Delete settings!**")

        cid = msg.chat.id
        parts = msg.command

        # 📊 STATUS CHECK (No arguments provided)
        if len(parts) == 1:
            delay = auto_delete_chats.get(cid)
            mode = auto_delete_modes.get(cid, "all")

            if delay:
                return await msg.reply(
                    f"⚙️ **AUTO DELETE STATUS**\n\n"
                    f"• **Status:** `ENABLED 🟢`\n"
                    f"• **Delay Time:** `{format_time(delay)}`\n"
                    f"• **Target Mode:** `{mode}`",
                    parse_mode=ParseMode.MARKDOWN
                )
            return await msg.reply("🔴 **Auto-Delete is currently DISABLED for this group.**")

        # ❌ DISABLE COMMAND (`/autodel off`)
        if parts[1].lower() in ("off", "disable"):
            auto_delete_chats.pop(cid, None)
            auto_delete_modes.pop(cid, None)
            return await msg.reply("🔴 **Auto-Delete System successfully disabled!**")

        # ❌ USAGE CORRECTION CHECK
        if len(parts) < 3:
            return await msg.reply(
                "⚠️ **Incorrect Usage!**\n"
                "• **Format:** `/autodel <time> <mode>`\n"
                "• **Example:** `/autodel 30s all` or `/autodel 5m links`\n"
                "• **Valid Modes:** `all`, `media`, `links`, `text`, `bots`, `commands`"
            )

        delay = parse_time(parts[1])
        mode = parts[2].lower()
        valid_modes = ["all", "media", "links", "url", "text", "bots", "commands"]

        if delay is None or mode not in valid_modes:
            return await msg.reply("❌ **Invalid time format or mode!** Use format like `30s`, `5m`, `1h`.")

        auto_delete_chats[cid] = delay
        auto_delete_modes[cid] = mode

        await msg.reply(
            f"🟢 **Auto-Delete Configured Successfully!**\n\n"
            f"• **Delay:** `{format_time(delay)}`\n"
            f"• **Mode:** `{mode}`\n\n"
            f"⚡ _Matching messages will now be automatically purged._",
            parse_mode=ParseMode.MARKDOWN
        )

    # ============================================================
    # 👀 MESSAGE WATCHER FOR AUTO-DELETE
    # ============================================================
    @app.on_message(filters.group & ~filters.service, group=8)
    async def watcher(client, msg: Message):
        cid = msg.chat.id
        if cid not in auto_delete_chats:
            return

        if not msg.from_user or msg.from_user.is_self:
            return

        delay = auto_delete_chats[cid]
        mode = auto_delete_modes.get(cid, "all")

        if should_delete(msg, mode):
            try:
                app.loop.create_task(delete_later(client, cid, msg.id, delay))
            except Exception:
                asyncio.create_task(delete_later(client, cid, msg.id, delay))

    # ============================================================
    # ✏️ EDITED MESSAGE WATCHER (INSTANT WIPE)
    # ============================================================
    @app.on_edited_message(filters.group & ~filters.service, group=9)
    async def edited_watcher(client, msg: Message):
        cid = msg.chat.id
        if cid not in auto_delete_chats:
            return

        if not msg.from_user or msg.from_user.is_self:
            return

        try:
            await msg.delete()
        except Exception:
            pass
