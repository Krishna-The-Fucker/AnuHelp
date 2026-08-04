# ============================================================
# 📖 URBAN DICTIONARY LOOKUP MODULE (ULTRA PRO MAX)
# ============================================================

__mod_name__ = "📖 ᴜʀʙᴀɴ"

__help__ = """
*📖 ᴜʀʙᴀɴ ᴅɪᴄᴛɪᴏɴᴀʀ🇾* — Search slang, phrases, and definitions directly from Urban Dictionary!

• `/ud [term]` — Search for the definition of any word or slang phrase.
"""

from pyrogram import filters
from pyrogram.types import Message
import aiohttp
import logging

logger = logging.getLogger("URBAN")

def register_urban_system(app):

    @app.on_message(filters.command("ud"))
    async def urban_dictionary_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide a term to search on Urban Dictionary! Example:** `/ud nomad`")

        status_msg = await message.reply(f"🔍 **Searching Urban Dictionary for:** `{query}`...")

        try:
            url = f"https://api.urbandictionary.com/v0/define?term={query}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        return await status_msg.edit_text("❌ **Urban Dictionary API is currently unavailable or returned an error.**")
                    
                    data = await resp.json()
                    list_items = data.get("list", [])

                    if not list_items:
                        return await status_msg.edit_text(f"❌ **No definitions found for:** `{query}`")

                    # Grab the top definition
                    item = list_items[0]
                    word = item.get("word", query)
                    definition = item.get("definition", "No definition").replace("[", "").replace("]", "")
                    example = item.get("example", "No example").replace("[", "").replace("]", "")
                    thumbs_up = item.get("thumbs_up", 0)
                    thumbs_down = item.get("thumbs_down", 0)
                    permalink = item.get("permalink", "")

                    # Truncate if too long for telegram message limits
                    if len(definition) > 800:
                        definition = definition[:800] + "..."
                    if len(example) > 400:
                        example = example[:400] + "..."

                    text = (
                        f"📖 **URBAN DICTIONARY:** `{word}`\n\n"
                        f"📝 **Definition:**\n{definition}\n\n"
                        f"💬 **Example:**\n_{example}_\n\n"
                        f"👍 `{thumbs_up}` 👎 `{thumbs_down}`\n"
                        f"🔗 [Read more on Urban Dictionary]({permalink})"
                    )

                    await status_msg.edit_text(text, disable_web_page_preview=True)

        except Exception as e:
            logger.error(f"[Urban Error]: {e}")
            await status_msg.edit_text(f"❌ **An error occurred while fetching the definition:** `{str(e)}`")
