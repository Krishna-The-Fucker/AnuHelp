# ============================================================
# 📝 SED (TEXT REPLACEMENT / QUICK FIX) MODULE
# ============================================================

__mod_name__ = "📝 sᴇᴅ"

__help__ = """
*📝 ꜱᴇᴅ ᴍᴏᴅᴜʟᴇ* — Quickly fix typos in your messages using standard substitution syntax (just like Unix sed)!

• Reply to a message with `s/old/new/` or `s/old/new/g` to replace text instantly.
"""

from pyrogram import filters
from pyrogram.types import Message
import re
import logging

logger = logging.getLogger("SED")

def register_sed_system(app):

    @app.on_message(filters.text & filters.reply & ~filters.edited)
    async def sed_text_replacer(client, message: Message):
        text = message.text
        if not text or not text.startswith("s/"):
            return

        # Parse sed command structure: s/pattern/replacement/flags
        try:
            parts = text.split("/")
            if len(parts) < 3:
                return

            pattern = parts[1]
            replacement = parts[2]
            flags = parts[3] if len(parts) > 3 else ""

            target_message = message.reply_to_message
            if not target_message or not target_message.text:
                return

            original_text = target_message.text

            # Apply regex substitution
            count = 0 if "g" in flags else 1
            
            # Escape pattern safely if needed, or allow raw regex
            new_text, matches = re.subn(pattern, replacement, original_text, count=count)

            if matches > 0 and new_text != original_text:
                sender_name = target_message.from_user.first_name if target_message.from_user else "User"
                await message.reply(
                    f"💬 **Did you mean ({sender_name}):**\n\n{new_text}"
                )

        except Exception as e:
            logger.error(f"[Sed Error]: {e}")
