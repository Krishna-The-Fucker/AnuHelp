# ============================================================
# Group Manager Bot
# Author: Krishna-bots
# ============================================================

from pyrogram import filters
from pyrogram.types import Message

REPO_LINK = ""


# ============================================================
# 🔥 HANDLER & COMMANDS REGISTRATION
# ============================================================

def register_repo_handler(app):

    @app.on_message(filters.command("repo") & filters.group)
    async def repo_handler(client, message: Message):
        await message.reply_text(
            f"📦 **Official Repository:**\n🔗 {REPO_LINK if REPO_LINK else 'Repository link not provided yet!'}",
            disable_web_page_preview=True
        )
