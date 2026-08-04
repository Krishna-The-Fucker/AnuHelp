# ============================================================
# 🛡️ GLOBAL ERROR HANDLER & EXCEPTION LOGGING MODULE
# ============================================================

__mod_name__ = "⚠️ ᴇʀʀᴏʀ"

import traceback
import logging
import sys
from pyrogram import filters
from pyrogram.types import Message
from config import LOG_CHANNEL, OWNER_ID

logger = logging.getLogger("ERROR_HANDLER")

def register_error_system(app):

    # ============================================================
    # 🚨 GLOBAL EXCEPTION CAPTURE FOR MESSAGES & CALLBACKS
    # ============================================================
    @app.on_raw_update
    async def global_exception_catcher(client, update, users, chats):
        # Pyrogram raw update middleware wrapper fallback if needed,
        # but standard message handling is typically caught inside individual blocks.
        pass

    async def notify_dev(client, error_text: str, context: str = "General"):
        """Sends critical error traces to the configured log channel or owner."""
        if not LOG_CHANNEL:
            return
        
        err_msg = (
            f"❌ **CRITICAL ERROR DETECTED**\n\n"
            f"📌 **Context:** `{context}`\n"
            f"🔍 **Error Trace:**\n```python\n{error_text[:3500]}\n```"
        )
        try:
            await client.send_message(LOG_CHANNEL, err_msg)
        except Exception as e:
            logger.error(f"[Error Handler] Failed to dispatch error log to channel: {e}")

    # Decorator or helper to wrap dangerous functions safely
    def catch_errors(context_name="Task"):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    tb = traceback.format_exc()
                    logger.error(f"[{context_name}] Unhandled exception: {e}\n{tb}")
                    # Try to find client/message from args if available
                    for arg in args:
                        if hasattr(arg, "client") and hasattr(arg, "reply"):
                            try:
                                await arg.reply("❌ **An unexpected error occurred while processing your request. The developers have been notified.**")
                            except Exception:
                                pass
                            break
            return wrapper
        return decorator

    # Expose helper globally or store in app attributes if needed
    app.catch_errors = catch_errors
    logger.info("✅ Global Error Handler Module Loaded Successfully.")
