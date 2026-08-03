# ============================================================
# 🤖 ANTI-SPAM SYSTEM (MODERN + STYLISH + PRO MAX)
# ============================================================

__mod_name__ = "🛡️ ᴀɴᴛɪ-sᴘᴀᴍ"

__help__ = """
*🛡️ ᴀɴᴛɪ-sᴘᴀᴍ sʏsᴛᴇᴍ* — Automatically detects and purges spam, promotional scams, crypto shills, and explicit material with advanced warning/ban enforcement!

• Anti-spam is fully automatic and active for all non-admin members.
"""

import re
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus, ParseMode
import logging

def register_anti_spam(app, db, add_warn, get_warn_limit, reset_warns, add_log):

    # ============================================================
    # 🚫 EXPANDED SPAM & SCAM KEYWORDS (MASSIVE LIST)
    # ============================================================
    CONTEXT = [
        # Crypto, Trading & Finance Scams
        "crypto", "cash", "win", "bonus", "spins", "sell", "bet", "usdt", 
        "profit", "invest", "reward", "money", "price", "promo", "airdrop", 
        "referral", "earn", "buy", "forex", "trading", "signals", "passive income", 
        "financial freedom", "nft", "token", "giveaway", "binance", "metamask", 
        "wallet connect", "solana", "ethereum", "bitcoin", "doge", "shiba", "payout", 
        "withdraw", "deposit", "staking", "pump", "dump", "rich", "millionaire", 
        "doubler", "roi", "dividend",

        # Adult & Explicit Content
        "nude", "porn", "sex", "fuck", "horny", "hot girls", "milf", "sugar daddy", 
        "sugar mommy", "telegram girls", "video call", "live cam", "onlyfans", 
        "nsfw", "xxx", "dildo", "boobs", "pussy", "dick", "cock", "escort", 
        "hookup", "dating", "slut", "whore",

        # Scam, Phishing & Bot Services
        "free telegram", "buy members", "buy views", "fake views", "bot service", 
        "mass dm", "sponsring", "sponsor", "collaboration dm", "cheap service", 
        "verification code", "admin panel", "hack", "cracked", "generator", 
        "license key", "activation code", "free nitro", "discord nitro"
    ]

    PATTERNS = [re.compile(rf"\b{p}\b", re.IGNORECASE) for p in CONTEXT]

    # ============================================================
    # 🔍 ADVANCED SPAM DETECTION ENGINE
    # ============================================================
    async def check_spam(text: str):
        if not text:
            return False

        matched = [p.pattern.replace("\\b", "") for p in PATTERNS if p.search(text)]

        # Strict detection rule (>=2 keywords matched to prevent false positives)
        return matched if len(matched) >= 2 else False

    # ============================================================
    # 🎭 CENSOR WORD UTILITY
    # ============================================================
    def censor_word(word: str):
        return ''.join(c if i % 2 == 0 else '•' for i, c in enumerate(word))

    # ============================================================
    # 🎨 FORMAT USER UTILITY
    # ============================================================
    def format_user(user):
        return f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"

    # ============================================================
    # 🚀 REGISTER ANTI-SPAM HANDLER
    # ============================================================
    @app.on_message(filters.text & filters.group, group=-5)
    async def auto_spam_detect(client, message: Message):
        if not message.from_user:
            return

        user = message.from_user
        user_id = user.id
        chat_id = message.chat.id

        # =========================
        # 👑 ADMIN BYPASS CHECK
        # =========================
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return
        except Exception:
            return

        # =========================
        # 🧠 EXTRACT & SCAN TEXT
        # =========================
        text = message.text or message.caption or ""
        result = await check_spam(text)

        if not result:
            return

        # =========================
        # ❌ DELETE SPAM MESSAGE
        # =========================
        try:
            await message.delete()
        except Exception:
            pass

        # =========================
        # ⚠️ WARN SYSTEM INTEGRATION
        # =========================
        try:
            warns = await add_warn(chat_id, user_id)
            limit = await get_warn_limit(chat_id)
            await add_log(chat_id, "spam", user_id)
        except Exception:
            warns = 1
            limit = 3

        # =========================
        # 🔒 AUTO BAN ENFORCEMENT
        # =========================
        if warns >= limit:
            try:
                await client.ban_chat_member(chat_id, user_id)
                await reset_warns(chat_id, user_id)
            except Exception:
                pass

            return await message.reply_text(
                f"🚫 **USER BANNED AUTOMATICALLY**\n\n"
                f"👤 **User:** {format_user(user)}\n"
                f"📌 **Reason:** Spam & Promotional Flood\n"
                f"⚠️ **Warning Limit Reached:** `{limit}/{limit}`\n\n"
                f"🛡️ **Security Status:** Active & Protected ✨",
                parse_mode=ParseMode.HTML
            )

        # =========================
        # 🎯 CENSOR KEYWORDS FORMATTING
        # =========================
        keywords = ", ".join([censor_word(k) for k in result])

        # =========================
        # ⚠️ WARNING MESSAGE NOTIFICATION
        # =========================
        try:
            await message.reply_text(
                f"⚠️ **SPAM DETECTED & PURGED**\n\n"
                f"👤 **User:** {format_user(user)}\n"
                f"🔍 **Flagged Keywords:** `[{keywords}]`\n\n"
                f"📊 **Warning Count:** `{warns}/{limit}`\n"
                f"🛡️ **Action Taken:** Message Deleted\n\n"
                f"❗ _Please avoid sending promotional, scam, or explicit material._",
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
        except Exception as e:
            logging.error(f"[Anti-Spam Reply Error]: {e}")
