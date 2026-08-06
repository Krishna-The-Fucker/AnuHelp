# ============================================================
# 🛠️ MISCELLANEOUS UTILITIES & EXTRA TOOLS MODULE
# ============================================================

__mod_name__ = "🛠️ ᴍɪꜱᴄ"

__help__ = """
*🛠️ ᴍɪꜱᴄᴇʟʟᴀɴᴇᴏᴜꜱ ᴜᴛɪʟɪᴛɪᴇꜱ* — An "odds and ends" module for small, simple commands which don't really fit anywhere.

• `/runs` — Respond with a randomly generated "run away" string.
• `/id` — Get the ID of a user, group, or channel. Can be used by reply, username, or mention.
• `/info` — Get a user's info.
• `/donate` — Donate to the bot creator.
• `/markdownhelp` — Information on how to use markdown with the bot. PM only.
• `/limits` — Show the bot's limits.
"""

from pyrogram import filters
from pyrogram.types import Message
import random
from db import db

def register_misc_system(app):

    # ============================================================
    # 🏃 RUNS COMMAND (`/runs`)
    # ============================================================
    @app.on_message(filters.command("runs"))
    async def runs_cmd(client, message: Message):
        RUN_STRINGS = (
            "Where do you think you're going?",
            "🏃‍♂️💨 There goes another one...",
            "You can run, but you can't hide!",
            "🏃‍♀️💨 Running away, huh? Coward!",
            "Where's the fire?",
            "💨 Zoom!",
            "🏃‍♂️ Running won't save you from Nomad Bot!",
            "And they're off! 🐎"
        )
        await message.reply(random.choice(RUN_STRINGS))

    # ============================================================
    # 🆔 ID LOOKUP (`/id`)
    # ============================================================
    @app.on_message(filters.command("id"))
    async def get_id_cmd(client, message: Message):
        chat = message.chat
        user = message.from_user
        reply = message.reply_to_message

        # Check if argument is passed (e.g., /id @username or chat id)
        if len(message.command) > 1:
            query = message.command[1].strip()
            try:
                if query.startswith("@") or query.lstrip("-").isdigit():
                    resolved_chat = await client.get_chat(query)
                    return await message.reply(
                        f"🆔 **IDENTIFICATION SYSTEM**\n\n"
                        f"💬 **Title/Name:** `{resolved_chat.title or resolved_chat.first_name}`\n"
                        f"📌 **ID:** `{resolved_chat.id}`\n"
                        f"🔹 **Type:** `{resolved_chat.type.name}`"
                    )
            except Exception as e:
                return await message.reply(f"❌ **Could not resolve ID for:** `{query}`\nError: `{str(e)}`")

        text = f"🆔 **IDENTIFICATION SYSTEM**\n\n"
        
        if reply and reply.from_user:
            r_user = reply.from_user
            text += f"👤 **Replied User Name:** `{r_user.first_name}`\n"
            text += f"🆔 **Replied User ID:** `{r_user.id}`\n\n"

        text += f"💬 **Chat Title:** `{chat.title if chat.type.name != 'PRIVATE' else 'Private Chat'}`\n"
        text += f"📌 **Chat ID:** `{chat.id}`\n\n"
        
        if user:
            text += f"🙋‍♂️ **Your Name:** `{user.first_name}`\n"
            text += f"🔑 **Your User ID:** `{user.id}`"

        await message.reply(text)

    # ============================================================
    # ℹ️ USER INFO (`/info`)
    # ============================================================
    @app.on_message(filters.command("info"))
    async def user_info_cmd(client, message: Message):
        target_user = message.from_user
        if message.reply_to_message and message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            try:
                query = message.command[1].strip()
                target_user = await client.get_users(query)
            except Exception:
                pass

        if not target_user:
            return await message.reply("⚠️ **Could not fetch user information!**")

        username_str = f"@{target_user.username}" if target_user.username else 'None'
        info_text = (
            f"👤 **USER INFORMATION SUMMARY**\n\n"
            f"• **First Name:** `{target_user.first_name}`\n"
            f"• **Last Name:** `{target_user.last_name or 'None'}`\n"
            f"• **Username:** `{username_str}`\n"
            f"• **User ID:** `{target_user.id}`\n"
            f"• **Is Bot:** `{target_user.is_bot}`\n"
            f"• **DC ID:** `{target_user.dc_id or 'Unknown'}`"
        )
        await message.reply(info_text)

    # ============================================================
    # 💖 DONATE COMMAND (`/donate`)
    # ============================================================
    @app.on_message(filters.command("donate"))
    async def donate_cmd(client, message: Message):
        donate_text = (
            f"💖 **SUPPORT THE DEVELOPER**\n\n"
            f"Thank you for wanting to support the creation and maintenance of **Nomad Bot**!\n\n"
            f"You can support via:\n"
            f"• **UPI / QR:** Contact the developer directly.\n"
            f"• **Crypto / GitHub Sponsors:** Coming soon!\n\n"
            f"Your support helps keep servers running 24/7 with ultra-fast responses! 🚀"
        )
        await message.reply(donate_text)

    # ============================================================
    # 📝 MARKDOWN HELP (`/markdownhelp`) - PM ONLY
    # ============================================================
    @app.on_message(filters.command("markdownhelp"))
    async def markdown_help_cmd(client, message: Message):
        if message.chat.type.name != "PRIVATE":
            bot_username = (await client.get_me()).username
            return await message.reply(
                "⚠️ **Markdown Help can only be viewed in Private Chat (PM)** to avoid group spam.",
                reply_markup=pyrogram.types.InlineKeyboardMarkup([[
                    pyrogram.types.InlineKeyboardButton("📤 Open in PM", url=f"https://t.me/{bot_username}?start=markdownhelp")
                ]])
            )

        md_text = (
            f"📖 **MARKDOWN FORMATTING GUIDE**\n\n"
            f"Nomad Bot supports rich formatting for welcomes, rules, notes, and filters:\n\n"
            f"• **Bold:** `**text**` -> **text**\n"
            f"• **Italic:** `__text__` or `*text*` -> *text*\n"
            f"• **Monospace / Code:** `` `text` `` -> `text`\n"
            f"• **Strikethrough:** `~text~` -> ~text~\n"
            f"• **Underline:** `--text--` -> <u>text</u>\n"
            f"• **Spoiler:** `||text||` -> ||text||\n"
            f"• **Link:** `[Text](https://example.com)` -> [Text](https://example.com)\n\n"
            f"📌 **Available Variables:**\n"
            f"• `{first}` - User's first name\n"
            f"• `{last}` - User's last name\n"
            f"• `{fullname}` - User's full name\n"
            f"• `{username}` - User's username\n"
            f"• `{mention}` - Mention user with tag\n"
            f"• `{chat}` - Group title"
        )
        await message.reply(md_text)

    # ============================================================
    # 📊 LIMITS COMMAND (`/limits`)
    # ============================================================
    @app.on_message(filters.command("limits"))
    async def limits_cmd(client, message: Message):
        limits_text = (
            f"⚙️ **NOMAD BOT SYSTEM LIMITS**\n\n"
            f"• **Max Filters per Chat:** `Unlimited (DB Backed)`\n"
            f"• **Max Notes per Chat:** `Unlimited (DB Backed)`\n"
            f"• **Max Warn Limit:** `10 Warns`\n"
            f"• **Max Pinned Messages:** `1 Active Pin Cache`\n"
            f"• **Flood Control:** `Active (Async Engine)`\n"
            f"• **Database Engine:** `Motor / MongoDB (Optimized)`"
        )
        await message.reply(limits_text)
