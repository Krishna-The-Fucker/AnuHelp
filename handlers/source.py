# ============================================================
# 📁 SOURCE CODE & REPOSITORY ACCESS MODULE
# ============================================================

__mod_name__ = "📁 sᴏᴜʀᴄᴇ"

__help__ = """
*📁 ꜱᴏᴜʀᴄᴇ ᴍᴏᴅᴜʟᴇ* — Get quick links to the bot's source code and repository details.

• `/source` — View the official repository link and project info.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def register_source_system(app):

    @app.on_message(filters.command("source"))
    async def source_code_cmd(client, message: Message):
        source_text = (
            f"📂 **NOMAD TELEGRAM MANAGEMENT BOT**\n\n"
            f"• **Architecture:** Asynchronous Modular Design\n"
            f"• **Core Framework:** Pyrogram (MTProto API)\n"
            f"• **Database:** MongoDB (Motor Async)\n"
            f"• **Status:** Open for Deployment & Customization\n\n"
            f"Click the button below to access the official repository."
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📂 View Source Code", url="https://github.com/your-username/nomad-telegram-bot"),
                    InlineKeyboardButton("💬 Support Chat", url="https://t.me/your_support_channel")
                ]
            ]
        )

        await message.reply(source_text, reply_markup=keyboard, disable_web_page_preview=True)
