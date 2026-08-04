# ============================================================
# 📚 WIKIPEDIA SEARCH MODULE (ULTRA PRO MAX)
# ============================================================

__mod_name__ = "📚 ᴡɪᴋɪ"

__help__ = """
*📚 ᴡɪᴋɪᴘᴇᴅɪᴀ ꜱᴇᴀʀᴄʜ* — Look up summaries and articles directly from Wikipedia without leaving Telegram!

• `/wiki [query]` — Search for any topic or question on Wikipedia.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import aiohttp
import logging

logger = logging.getLogger("WIKI")

def register_wiki_system(app):

    @app.on_message(filters.command("wiki"))
    async def wikipedia_search_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide a search query for Wikipedia! Example:** `/wiki Python programming`")

        status_msg = await message.reply(f"📚 **Searching Wikipedia for:** `{query}`...")

        try:
            # Wikimedia REST API endpoint for page summaries
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{aiohttp.helpers.quote(query)}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 404:
                        return await status_msg.edit_text(f"❌ **No Wikipedia article found for:** `{query}`")
                    if resp.status != 200:
                        return await status_msg.edit_text("❌ **Wikipedia API is currently unavailable or returned an error.**")

                    data = await resp.json()

                    title = data.get("title", query)
                    extract = data.get("extract", "No summary available.")
                    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")

                    # Truncate summary if excessively long
                    if len(extract) > 900:
                        extract = extract[:900] + "..."

                    text = (
                        f"📚 **WIKIPEDIA:** `{title}`\n\n"
                        f"{extract}"
                    )

                    keyboard = None
                    if page_url:
                        keyboard = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton("🌐 Read Full Article", url=page_url)]
                            ]
                        )

                    await status_msg.edit_text(text, reply_markup=keyboard, disable_web_page_preview=True)

        except Exception as e:
            logger.error(f"[Wiki Error]: {e}")
            await status_msg.edit_text(f"❌ **An error occurred while searching Wikipedia:** `{str(e)}`")
