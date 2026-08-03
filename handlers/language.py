# ============================================================
# 🌍 ADVANCED LANGUAGE & TRANSLATION SYSTEM (ULTRA PRO MAX)
# ============================================================

__mod_name__ = "🌍 ʟᴀɴɢᴜᴀɢᴇ"

__help__ = """
*🌍 ʟᴀɴɢᴜᴀɢᴇ & ᴛʀᴀɴsʟᴀᴛɪᴏɴ* — Automatically translate group chats into your preferred language!

• `/setlang <lang_code>` — Set group target language
• `/lang` — View current group language & status
• `/lang on` — Enable automatic translation
• `/lang off` — Disable automatic translation
• `/langlist` — View supported language codes
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from googletrans import Translator
from datetime import datetime
import logging

translator = Translator()

# ============================================================
# 🌍 90+ SUPPORTED LANGUAGES
# ============================================================

LANGUAGES = {
    "en": "English", "hi": "Hindi", "bn": "Bengali", "te": "Telugu",
    "mr": "Marathi", "ta": "Tamil", "ur": "Urdu", "gu": "Gujarati",
    "kn": "Kannada", "ml": "Malayalam", "pa": "Punjabi", "or": "Odia",

    "fr": "French", "de": "German", "es": "Spanish", "it": "Italian",
    "pt": "Portuguese", "ru": "Russian", "zh-cn": "Chinese (Simplified)",
    "zh-tw": "Chinese (Traditional)", "ja": "Japanese", "ko": "Korean",

    "ar": "Arabic", "fa": "Persian", "tr": "Turkish", "id": "Indonesian",
    "ms": "Malay", "th": "Thai", "vi": "Vietnamese",

    "nl": "Dutch", "sv": "Swedish", "no": "Norwegian", "da": "Danish",
    "fi": "Finnish", "pl": "Polish", "cs": "Czech", "sk": "Slovak",
    "hu": "Hungarian", "ro": "Romanian", "bg": "Bulgarian",
    "el": "Greek", "uk": "Ukrainian",

    "he": "Hebrew", "sw": "Swahili", "af": "Afrikaans",
    "sq": "Albanian", "hy": "Armenian", "az": "Azerbaijani",
    "eu": "Basque", "be": "Belarusian", "bs": "Bosnian",
    "ca": "Catalan", "hr": "Croatian", "eo": "Esperanto",
    "et": "Estonian", "gl": "Galician", "ka": "Georgian",
    "is": "Icelandic", "ga": "Irish", "la": "Latin",
    "lv": "Latvian", "lt": "Lithuanian", "mk": "Macedonian",
    "mt": "Maltese", "mn": "Mongolian", "ne": "Nepali",
    "sr": "Serbian", "sl": "Slovenian", "so": "Somali",
    "tl": "Filipino", "cy": "Welsh",

    "km": "Khmer", "lo": "Lao", "my": "Myanmar",
    "si": "Sinhala", "am": "Amharic", "zu": "Zulu"
}

def register_language_system(app, db, cache_get, cache_set):

    # ============================================================
    # 👑 ADMIN CHECK HELPER
    # ============================================================
    async def is_admin(client, chat_id, user_id):
        try:
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except:
            return False

    # ============================================================
    # 📦 SET GROUP LANGUAGE DB & CACHE
    # ============================================================
    async def set_group_language(chat_id, lang_code):
        if lang_code not in LANGUAGES:
            return False

        await db.language.update_one(
            {"chat_id": chat_id},
            {"$set": {
                "lang": lang_code,
                "enabled": True,
                "updated": datetime.utcnow()
            }},
            upsert=True
        )

        cache_set(f"lang:{chat_id}", lang_code)
        cache_set(f"lang_status:{chat_id}", True)
        return True

    # ============================================================
    # 🔘 ENABLE / DISABLE TRANSLATION
    # ============================================================
    async def toggle_language(chat_id, status: bool):
        await db.language.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": status}},
            upsert=True
        )
        cache_set(f"lang_status:{chat_id}", status)

    async def is_language_enabled(chat_id):
        cached = cache_get(f"lang_status:{chat_id}")
        if cached is not None:
            return cached

        data = await db.language.find_one({"chat_id": chat_id})
        status = data.get("enabled", False) if data else False

        cache_set(f"lang_status:{chat_id}", status)
        return status

    # ============================================================
    # 📥 GET GROUP LANGUAGE
    # ============================================================
    async def get_group_language(chat_id):
        cached = cache_get(f"lang:{chat_id}")
        if cached:
            return cached

        data = await db.language.find_one({"chat_id": chat_id})
        lang = data.get("lang", "en") if data else "en"

        cache_set(f"lang:{chat_id}", lang)
        return lang

    # ============================================================
    # 🌍 TRANSLATE MESSAGE CORE (HIGH SPEED ENGINE)
    # ============================================================
    async def translate_text(chat_id, text):
        try:
            if not text or len(text) < 2:
                return text

            if not await is_language_enabled(chat_id):
                return text

            lang = await get_group_language(chat_id)
            if lang == "en":
                return text

            # 🚫 Skip commands or HTTP links
            if text.startswith("/") or "http" in text:
                return text

            cache_key = f"translated:{chat_id}:{hash(text)}"
            cached = cache_get(cache_key)
            if cached:
                return cached

            translated = translator.translate(text, dest=lang)
            result = translated.text

            cache_set(cache_key, result)
            return result
        except Exception:
            return text

    # ============================================================
    # 🎛️ COMMANDS REGISTRATION
    # ============================================================

    @app.on_message(filters.command("setlang") & filters.group)
    async def set_lang_command(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ **Only admins can change group language settings!**")

        if len(message.command) < 2:
            return await message.reply(
                "⚠️ **Usage:** `/setlang <language_code>`\n"
                "• Example: `/setlang hi` (Hindi) or `/setlang fr` (French)\n"
                "• Type `/langlist` to see all available language codes."
            )

        code = message.command[1].lower()
        if code not in LANGUAGES:
            return await message.reply("❌ **Invalid language code!** Use `/langlist` to see supported codes.")

        await set_group_language(message.chat.id, code)
        await message.reply(f"✅ **Group language successfully updated to:** `{LANGUAGES[code]}` (`{code}`) 🌍")

    @app.on_message(filters.command("lang") & filters.group)
    async def lang_status_command(client, message: Message):
        if len(message.command) > 1:
            if not await is_admin(client, message.chat.id, message.from_user.id):
                return await message.reply("❌ **Only admins can modify configuration!**")

            arg = message.command[1].lower()
            if arg == "on":
                await toggle_language(message.chat.id, True)
                return await message.reply("✅ **Auto-Translation System:** Enabled 🟢")
            elif arg == "off":
                await toggle_language(message.chat.id, False)
                return await message.reply("❌ **Auto-Translation System:** Disabled 🔴")

        current_lang = await get_group_language(message.chat.id)
        status = await is_language_enabled(message.chat.id)

        await message.reply(
            f"🌍 **Group Language Settings**\n\n"
            f"• **Status:** `{'ACTIVE 🟢' if status else 'INACTIVE 🔴'}`\n"
            f"• **Language:** `{LANGUAGES.get(current_lang, 'English')}` (`{current_lang}`)\n\n"
            f"_Use `/lang on` or `/lang off` to toggle automatic translation._"
        )

    @app.on_message(filters.command("langlist"))
    async def lang_list_command(client, message: Message):
        text = "📜 **Supported Language Codes:**\n\n"
        for code, name in list(LANGUAGES.items())[:30]:  # Show top 30 to avoid length limits
            text += f"• `{code}` — {name}\n"
        text += "\n_Use `/setlang <code>` to apply a language._"
        await message.reply(text)

    # ============================================================
    # 🔄 AUTO TRANSLATION INCOMING MESSAGE FILTER
    # ============================================================
    @app.on_message(filters.group & ~filters.service & ~filters.bot, group=12)
    async def group_translation_watcher(client, message: Message):
        try:
            if not message.text:
                return

            if not await is_language_enabled(message.chat.id):
                return

            # Skip if user is admin
            if await is_admin(client, message.chat.id, message.from_user.id):
                return

            translated_content = await translate_text(message.chat.id, message.text)
            if translated_content and translated_content != message.text:
                # Append translated version neatly
                await message.reply_text(
                    f"🌐 **Translated ({LANGUAGES.get(await get_group_language(message.chat.id), 'EN')}):**\n"
                    f"{translated_content}",
                    quote=True
                )
        except Exception as e:
            logging.error(f"[Translation Watcher Error]: {e}")
