# ============================================================
# 🚫 ANTI-EDIT SYSTEM MODULE (ULTRA FAST + MONGODB)
# ============================================================

__mod_name__ = "🚫 ᴀɴᴛɪ-ᴇᴅɪᴛ"

__help__ = """
*🚫 ᴀɴᴛɪ-ᴇᴅɪᴛ ᴍᴏᴅᴜʟᴇ* — Detect and instantly delete edited messages in your group to maintain chat integrity.

• `/antiedit` — Check the current anti-edit protection status.
• `/antiedit on` — Enable anti-edit protection for the group.
• `/antiedit off` — Disable anti-edit protection for the group.
"""

from pyrogram import filters
from pyrogram.types import Message
from db import db
import asyncio
import logging

logger = logging.getLogger("ANTIEDIT")

# ============================================================
# ⚡ MEMORY CACHE (ANTI DUPLICATE)
# ============================================================
EDIT_CACHE = {}

# ============================================================
# 🗄️ DATABASE HELPERS
# ============================================================
async def set_antiedit(chat_id: int, status: bool):
    await db.antiedit.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )

async def get_antiedit(chat_id: int) -> bool:
    data = await db.antiedit.find_one({"chat_id": chat_id})
    return data.get("enabled", False) if data else False

def register_antiedit_system(app):

    # ============================================================
    # 🚨 EDIT DETECTION HANDLER
    # ============================================================
    @app.on_edited_message(filters.group)
    async def anti_edit_handler(client, message: Message):
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else 0

        # ❌ Check if disabled for this chat
        if not await get_antiedit(chat_id):
            return

        # ⚡ Anti duplicate check
        key = f"{chat_id}_{message.id}"
        if key in EDIT_CACHE:
            return

        EDIT_CACHE[key] = True

        try:
            # ⚡ Ultra fast delete
            await asyncio.sleep(0.1)
            await message.delete()

            # 💬 Stylish alert message
            mention = message.from_user.mention if message.from_user else "Unknown User"
            warn = await client.send_message(
                chat_id,
                f"🚫 **Edited Message Deleted**\n\n"
                f"👤 **User:** {mention}\n"
                f"⚡ **Speed:** `0.1s`\n"
                f"🛡 **Protection:** `ACTIVE`\n\n"
                f"❌ **Editing messages is not allowed in this group!**"
            )

            # Auto-delete alert after 4 seconds
            await asyncio.sleep(4)
            await warn.delete()

        except Exception as e:
            logger.error(f"[AntiEdit Error]: {e}")

        finally:
            await asyncio.sleep(8)
            EDIT_CACHE.pop(key, None)

    # ============================================================
    # 🎛️ ADMIN TOGGLE COMMAND (`/antiedit`)
    # ============================================================
    @app.on_message(filters.command("antiedit") & filters.group)
    async def antiedit_toggle(client, message: Message):
        # Optional: Admin check can be enforced here
        chat_id = message.chat.id

        if len(message.command) == 1:
            status = await get_antiedit(chat_id)
            return await message.reply_text(
                f"🚫 **Anti-Edit Protection Status:** `{'ON' if status else 'OFF'}`"
            )

        arg = message.command[1].lower()

        if arg == "on":
            await set_antiedit(chat_id, True)
            await message.reply_text("✅ **Anti-Edit Protection has been Enabled!**")
        elif arg == "off":
            await set_antiedit(chat_id, False)
            await message.reply_text("❌ **Anti-Edit Protection has been Disabled!**")
        else:
            await message.reply("⚠️ **Invalid argument! Use:** `/antiedit on` or `/antiedit off`")
