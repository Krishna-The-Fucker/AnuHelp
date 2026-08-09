# ============================================================
# 🤖 Group Manager Bot - Main Entry (ULTRA PRO MAX++)
# ============================================================

import logging
import asyncio
import signal
import sys
import gc

from pyrogram import Client, filters, idle

from config import (
    API_ID, API_HASH, BOT_TOKEN,
    LOG_LEVEL, AUTO_CREATE_INDEXES, LOG_CHANNEL
)

# 🔐 Security
from security import verify_integrity, get_runtime_key

# 📦 Handlers
from handlers import register_all_handlers

# 🗄️ DB
from db import create_indexes, db


# ============================================================
# ⚙️ Logging Setup
# ============================================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger("MAIN")

logger.info("🚀 Starting Group Manager Bot...")


# ============================================================
# 🔐 Security Check
# ============================================================

try:
    verify_integrity()
    RUNTIME_KEY = get_runtime_key()
    logger.info("🔐 Security check passed!")
except Exception as e:
    logger.error(f"❌ Security check failed: {e}")
    sys.exit(1)


# ============================================================
# 🤖 Bot Client
# ============================================================

app = Client(
    "group_manager_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=50,
    sleep_threshold=20
)


# ============================================================
# 🚀 STARTUP TASKS
# ============================================================

async def startup():
    logger.info("⚙️ Running startup tasks...")

    try:
        if AUTO_CREATE_INDEXES:
            await create_indexes()
            logger.info("✅ Database indexes ready")
    except Exception as e:
        logger.error(f"❌ DB Index error: {e}")

    if LOG_CHANNEL:
        try:
            bot_info = await app.get_me()
            startup_message = (
                f"✅ **ʙᴏᴛ sᴜᴄᴄᴇssꜰᴜʟʟʏ sᴛᴀʀᴛᴇᴅ!**\n\n"
                f"🤖 **Bot:** @{bot_info.username}\n"
                f"🆔 **ID:** `{bot_info.id}`\n"
                f"🚀 **Status:** Online & Ready to Manage Groups!"
            )
            await app.send_message(LOG_CHANNEL, startup_message)
            logger.info("📢 Startup log sent to LOG_CHANNEL successfully!")
        except Exception as err:
            logger.error(f"❌ Failed to send log to LOG_CHANNEL: {err}")

    logger.info("🚀 Bot fully started!")


# ============================================================
# 🧹 CLEAN SHUTDOWN
# ============================================================

async def shutdown():
    logger.warning("🛑 Shutting down bot...")

    try:
        if LOG_CHANNEL:
            await app.send_message(LOG_CHANNEL, "⚠️ **ʙᴏᴛ ɪs sʜᴜᴛᴛɪɴɢ ᴅᴏᴡɴ...**")
    except Exception:
        pass

    try:
        if app.is_connected:
            await app.stop()
    except Exception:
        pass

    gc.collect()
    logger.info("✅ ᴀɴᴜ ᴜʟᴛɪᴍᴀᴛᴇ ʙᴏᴛ stopped safely")


# ============================================================
# 📦 Register Handlers
# ============================================================

try:
    register_all_handlers(app, db, LOG_CHANNEL)
    logger.info("✅ All handlers loaded!")
except Exception as e:
    logger.error(f"❌ Handler error: {e}")
    sys.exit(1)


# ============================================================
# ❤️ KEEP ALIVE
# ============================================================

@app.on_message(filters.private & filters.text & filters.incoming)
async def alive_ping(client, message):
    return


# ============================================================
# 🧠 SIGNAL HANDLER
# ============================================================

stop_event = asyncio.Event()

def handle_signal(*_):
    logger.warning("⚠️ Stop signal received...")
    stop_event.set()

signal.signal(signal.SIGINT, handle_signal)
signal.signal(signal.SIGTERM, handle_signal)


# ============================================================
# ▶️ MAIN RUNNER
# ============================================================

async def main():
    retry_delay = 5

    while not stop_event.is_set():
        try:
            logger.info("🚀 Starting bot session...")

            # Check karein ki client already connected toh nahi hai
            if not app.is_connected:
                await app.start()
                
            await startup()

            logger.info("🤖 Bot is running...")

            await asyncio.wait(
                [idle(), stop_event.wait()],
                return_when=asyncio.FIRST_COMPLETED
            )

        except Exception as e:
            logger.error(f"❌ Crash detected: {e}", exc_info=True)

            logger.info(f"🔄 Restarting in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)

            retry_delay = min(retry_delay * 2, 60)

        finally:
            await shutdown()


# ============================================================
# ▶️ ENTRY POINT
# ============================================================

if __name__ == "__main__":

    print("""
╔══════════════════════════════╗
║   🤖 ᴀɴᴜ ᴜʟɪᴍᴀᴛᴇ ʙᴏᴛ ꜱᴛᴀʀᴛ 🪄        ║
╚══════════════════════════════╝
""")

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.warning("⛔ Bot stopped manually")

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
