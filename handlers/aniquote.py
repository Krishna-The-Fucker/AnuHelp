# ============================================================
# 📝 ANI-QUOTE SYSTEM MODULE
# ============================================================

__mod_name__ = "📝 ᴀɴɪ-ǫᴜᴏᴛᴇ"

__help__ = """
*📝 ᴀɴɪ-ǫᴜᴏᴛᴇ ᴍᴏᴅᴜʟᴇ* — Search anime quotes by character or fetch random iconic lines!

• `/aniquote` — Get a random anime quote.
• `/aniquote [character]` — Search quotes by a specific character (e.g., `/aniquote naruto`).
• `/aniquote [character] page [number]` — View a specific page of results.
"""

import re
import html
import aiohttp
import logging
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

logger = logging.getLogger("ANIQUOTE")

def register_aniquote_system(app):

    @app.on_message(filters.command("aniquote"))
    async def aniquote_cmd(client, message: Message):
        
        # =========================
        # PARSE INPUT
        # =========================
        search = None
        page = 1

        if len(message.command) > 1:
            search = " ".join(message.command[1:])

            page_match = re.search(r'page\s+(\d+)', search, re.IGNORECASE)
            if page_match:
                page = int(page_match.group(1))
                search = re.sub(r'page\s+\d+', '', search, flags=re.IGNORECASE).strip()

        is_random = False if search else True

        # =========================
        # LOADING MESSAGE
        # =========================
        status_msg = await message.reply("🎧 **Fetching Anime Quotes...**")

        # =========================
        # FETCH DATA (API)
        # =========================
        # Note: animechan API is utilized here
        url = "https://animechan.xyz/api/random" if is_random else f"https://animechan.xyz/api/quotes?character={search}&page={page}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 404:
                        return await status_msg.edit_text(f"❌ **No quotes found for character:** `{search}`")
                    elif resp.status != 200:
                        return await status_msg.edit_text("❌ **Anime Quote API is currently unavailable.**")

                    data = await resp.json()

        except Exception as e:
            logger.error(f"[AniQuote Error]: {e}")
            return await status_msg.edit_text(f"❌ **An error occurred:** `{str(e)}`")

        # =========================
        # NORMALIZE DATA
        # =========================
        if is_random:
            data = [data]

        if not data:
            return await status_msg.edit_text("❌ **No results found.**")

        # =========================
        # LIMIT (ANTI SPAM)
        # =========================
        data = data[:5]  # Limit to max 5 quotes to prevent flood waits

        # =========================
        # SEND QUOTES
        # =========================
        for q in data:
            quote = html.escape(q.get("quote", "No quote available."))
            character = html.escape(q.get("character", "Unknown Character"))
            anime = html.escape(q.get("anime", "Unknown Anime"))

            text = (
                f"<blockquote>{quote}</blockquote>\n"
                f"👤 **Character:** <code>{character}</code>\n"
                f"🎬 **Anime:** <code>{anime}</code>"
            )

            await message.reply_text(text, parse_mode=ParseMode.HTML)

        # =========================
        # CLEANUP
        # =========================
        await status_msg.delete()
