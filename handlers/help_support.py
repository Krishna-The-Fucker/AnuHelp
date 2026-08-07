# ============================================================
# 💎 MODERN SUPPORT & ULTIMATE HELP SYSTEM (85+ MODULES PRO MAX)
# ============================================================

__mod_name = "💎 sᴜᴘᴘᴏʀᴛ & ʜᴇʟᴘ"

__help__ = """
*💎 ULTIMATE BOT HELP MENU (85+ MODULES)* — Explore all available commands below!

Click any button to view detailed usage instructions for that specific feature. Use Next/Back to navigate through all modules.
"""

from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
import time
import random
import logging

def register_support_system(app, db, SUPPORT_CHAT: int, ADMINS: list):

    SUPPORT_COOLDOWN = 5  # Cooldown in seconds to prevent spam

    # ============================================================
    # 📦 IN-MEMORY STORAGE
    # ============================================================
    USER_MAP = {}       
    LAST_MSG = {}       
    TICKET_DB = {}      

    def generate_ticket():
        return f"TKT-{random.randint(1000, 9999)}"

    # ============================================================
    # 📋 85+ MODULES HELP TEXTS & USAGE
    # ============================================================
    HELP_TEXTS = {
        "abuse": "🛡️ **Abuse Control**\n\n• **Usage:** Automatically filters or restricts abusive words and slang in chats.",
        "admin": "👑 **Admin Tools**\n\n• **Usage:** Essential commands for group management.\n• **Commands:** `/ban`, `/unban`, `/promote`, `/demote`",
        "afk": "💤 **AFK Module**\n\n• **Usage:** Let others know you are away.\n• **Command:** `/afk [reason]`",
        "aniquote": "📜 **Anime Quotes**\n\n• **Usage:** Fetches random motivational or famous anime quotes.\n• **Command:** `/aniquote`",
        "antibiolink": "🔗 **Anti-Bio Link**\n\n• **Usage:** Restricts users from putting links in their profile bio.",
        "antiedit": "✏️ **Anti-Edit Tracker**\n\n• **Usage:** Detects and logs when a user edits their message.",
        "antiflood": "🌊 **Anti-Flood System**\n\n• **Usage:** Prevents continuous message spamming by a user.",
        "antipron": "🔞 **Anti-Pron / NSFW**\n\n• **Usage:** Automatically detects and removes NSFW or adult media.",
        "antiraid": "🛡️ **Anti-Raid Protection**\n\n• **Usage:** Protects group from sudden mass bot/user attacks.",
        "approve": "✅ **Approval System**\n\n• **Usage:** Approves trusted users to bypass certain chat restrictions.\n• **Command:** `/approve`",
        "auto_spam_detection": "🤖 **Auto Spam Detection**\n\n• **Usage:** AI-based automatic detection of spam messages.",
        "autodel": "🗑️ **Auto Delete**\n\n• **Usage:** Automatically deletes service or specific command messages after a set time.",
        "backups": "💾 **Backups Manager**\n\n• **Usage:** Takes backup of database and chat settings.\n• **Command:** `/backup`",
        "banall": "⚠️ **Ban All (Sudo)**\n\n• **Usage:** Mass ban utility for emergency situations (Sudo only).",
        "bl_chat": "🚫 **Blacklist Chat**\n\n• **Usage:** Restricts bot usage in unauthorized or blacklisted groups.",
        "bl_user": "🚷 **Blacklist User**\n\n• **Usage:** Globally blacklists misbehaving users from the bot.",
        "blacklist": "📋 **Word Blacklist**\n\n• **Usage:** Adds specific words to the group's auto-delete/warn list.",
        "blacklistuser": "👤🚫 **Blacklist User Module**\n\n• **Usage:** Manages restricted user database.",
        "broadcast": "📢 **Broadcast System**\n\n• **Usage:** Sends announcements to all users or chats.\n• **Command:** `/broadcast [text]`",
        "captcha": "🧩 **Captcha Verification**\n\n• **Usage:** Verifies new members with buttons/math to stop bots.",
        "chatbot": "🤖 **AI Chatbot**\n\n• **Usage:** Intelligent conversational bot feature.",
        "clean_service": "🧹 **Clean Service Messages**\n\n• **Usage:** Automatically deletes 'user joined/left' join logs.",
        "cleaner": "🧽 **Cleaner Tool**\n\n• **Usage:** Cleans up old cache and temporary files.",
        "connection": "🔗 **Chat Connections**\n\n• **Usage:** Connects group to remote plugins/databases.\n• **Command:** `/connect`",
        "couples": "💞 **Couples Game**\n\n• **Usage:** Finds a random cute couple of the day.\n• **Command:** `/couple`",
        "currency_converter": "💱 **Currency Converter**\n\n• **Usage:** Converts currency rates in real time.\n• **Command:** `/convert [amount] [from] [to]`",
        "cust_filters": "⚡ **Custom Filters**\n\n• **Usage:** Saves custom automated replies for keywords.",
        "dbclean": "🗄️ **Database Cleaner**\n\n• **Usage:** Clears inactive chats and dead users from database.",
        "debug": "🛠️ **Debug Logs**\n\n• **Usage:** Developer tool to check error traces.",
        "dev": "👨‍💻 **Developer Utilities**\n\n• **Usage:** Special commands for bot owners.",
        "disable": "🔕 **Disable Commands**\n\n• **Usage:** Disables specific commands in a group.\n• **Command:** `/disable [cmd]`",
        "draw": "🎨 **Image Draw / AI Art**\n\n• **Usage:** Generates images from text prompts.",
        "economy": "💰 **Economy System**\n\n• **Usage:** Virtual currency and wallet management.\n• **Command:** `/balance`, `/daily`",
        "error_handler": "⚠️ **Error Handler**\n\n• **Usage:** Gracefully catches and logs bot runtime exceptions.",
        "eval": "⚡ **Evaluator (Sudo)**\n\n• **Usage:** Executes python code directly on server terminal.",
        "fed": "🌐 **Federations (Fed Ban)**\n\n• **Usage:** Bans a user across multiple connected groups simultaneously.",
        "filters": "⚡ **Filters Module**\n\n• **Usage:** Advanced filter handling system.",
        "fonts": "🔤 **Fancy Fonts Generator**\n\n• **Usage:** Converts normal text into stylish cool fonts.\n• **Command:** `/font [text]`",
        "forcejoin": "📢 **Force Subscribe**\n\n• **Usage:** Forces users to join a channel before chatting in the group.",
        "fun": "🎮 **Fun & Entertainment**\n\n• **Usage:** Fun commands and mini interaction tools.",
        "fun_strings": "💬 **Fun Strings**\n\n• **Usage:** Stores hilarious dialogues and responses.",
        "gemini": "✨ **Google Gemini AI**\n\n• **Usage:** Chat with Gemini AI directly.\n• **Command:** `/gemini [query]`",
        "get_common_chats": "👥 **Common Chats**\n\n• **Usage:** Finds groups shared between bot and user.",
        "gettime": "⏰ **Time Utility**\n\n• **Usage:** Shows current time across different timezones.",
        "gif": "🎞️ **GIF Search**\n\n• **Usage:** Searches and sends cool GIFs.\n• **Command:** `/gif [query]`",
        "github_uploader": "🐙 **GitHub Uploader**\n\n• **Usage:** Uploads files or logs directly to GitHub repositories.",
        "group": "👥 **Group Management**\n\n• **Usage:** Core settings and configuration for groups.",
        "hacker_game": "💻 **Hacker Game**\n\n• **Usage:** Interactive simulated hacking mini-game.",
        "help_support": "🎟️ **Help & Support**\n\n• **Usage:** Opens help menu and creates support tickets.",
        "language": "🌐 **Language Settings**\n\n• **Usage:** Changes bot language preferences for chats.",
        "locks": "🔒 **Chat Locks**\n\n• **Usage:** Locks links, stickers, media types.\n• **Command:** `/lock [type]`",
        "log_channel": "📊 **Log Channel**\n\n• **Usage:** Forwards important group actions to a designated log channel.",
        "logo": "🖼️ **Logo Maker**\n\n• **Usage:** Creates custom name logos on banners.\n• **Command:** `/logo [text]`",
        "mafiya": "🕵️ **Mafia Game**\n\n• **Usage:** Interactive group Mafia/Murder mystery game.",
        "memify": "memify: 🖼️ **Memify Tool**\n\n• **Usage:** Adds text to top of stickers or images.\n• **Command:** `/mm` or reply to media.",
        "misc": "🛠️ **Miscellaneous**\n\n• **Usage:** Extra utility tools and helpers.",
        "night_mode": "🌙 **Night Mode**\n\n• **Usage:** Automatically closes group during night hours.",
        "notes": "📝 **Saved Notes**\n\n• **Usage:** Saves important notes and documentation.\n• **Command:** `/save [name]` / `#[name]`",
        "pins": "📌 **Pin Management**\n\n• **Usage:** Advanced pinned messages controller.",
        "purge": "🗑️ **Purge Messages**\n\n• **Usage:** Deletes bulk messages instantly.\n• **Command:** `/purge`",
        "quick_games": "🎯 **Quick Games**\n\n• **Usage:** Fast mini games like dice, dart, etc.",
        "reaction": "❤️ **Auto Reactions**\n\n• **Usage:** Reacts automatically to specific chat triggers.",
        "remote_cmds": "💻 **Remote Commands**\n\n• **Usage:** Executes commands remotely on remote nodes.",
        "reporting": "🚨 **Admin Reporting**\n\n• **Usage:** Reports message to admins using `@admin` tag.",
        "rules": "📜 **Chat Rules**\n\n• **Usage:** Displays guidelines of the group.\n• **Command:** `/rules`",
        "sed": "🔤 **Sed Replacement**\n\n• **Usage:** Replaces typos using s/old/new format.",
        "shell": "💻 **Terminal Shell**\n\n• **Usage:** Executes linux shell commands (Sudo).",
        "source": "📦 **Source Code**\n\n• **Usage:** Shows GitHub repository link of the bot.",
        "start": "🚀 **Start Module**\n\n• **Usage:** Initializes the bot session.\n• **Command:** `/start`",
        "stickers": "🎨 **Sticker Tools**\n\n• **Usage:** Converts images/emojis to stickers pack.",
        "string_gen": "🪡 **String Session Gen**\n\n• **Usage:** Generates Pyrogram/Telethon string sessions.",
        "sudo": "⚡ **Sudo Controls**\n\n• **Usage:** Bot administrator controls.",
        "taggall": "📢 **Tag All Members**\n\n• **Usage:** Mentions all members in a group.\n• **Command:** `/tagall [text]`",
        "telegraph": "🌐 **Telegraph Maker**\n\n• **Usage:** Uploads text/media to telegraph link.",
        "truth_and_dare": "🎯 **Truth & Dare**\n\n• **Usage:** Plays fun truth or dare questions.\n• **Command:** `/truth` / `/dare`",
        "ud": "📖 **Urban Dictionary**\n\n• **Usage:** Searches slang meanings on Urban Dictionary.\n• **Command:** `/ud [word]`",
        "underworld_game": "🎲 **Underworld Game**\n\n• **Usage:** Interactive mafia roleplay game.",
        "user": "👤 **User Info**\n\n• **Usage:** Fetches profile info of users.",
        "userinfo": "ℹ️ **Detailed User Info**\n\n• **Usage:** Extended user profile tracking module.",
        "warns": "⚠️ **Warning System**\n\n• **Usage:** Warns users; bans upon reaching limit.\n• **Command:** `/warn`",
        "welcome": "👋 **Welcome Greeter**\n\n• **Usage:** Sends custom greeting cards to newcomers.",
        "wiki": "📚 **Wikipedia Search**\n\n• **Usage:** Searches Wikipedia articles.\n• **Command:** `/wiki [query]`",
        "writetool": "✍️ **Handwriting Writer**\n\n• **Usage:** Converts text into realistic handwriting.\n• **Command:** `/write [text]`",
        "zip": "🗜️ **Zip Compressor**\n\n• **Usage:** Compresses or extracts zip archives."
    }

    # ============================================================
    # 📄 PAGINATED KEYBOARDS (PAGE 1 TO 5)
    # ============================================================
    def get_help_keyboard(page=1):
        keys = list(HELP_TEXTS.keys())
        per_page = 14  # 14 modules per page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_keys = keys[start_idx:end_idx]

        keyboard = []
        row = []
        for i, k in enumerate(current_keys):
            row.append(InlineKeyboardButton(k.replace("_", " ").title(), callback_data=f"help_{k}_{page}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        # Pagination Navigation Buttons
        nav_buttons = []
        total_pages = (len(keys) + per_page - 1) // per_page
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"help_page_{page-1}"))
        nav_buttons.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="help_noop"))
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"help_page_{page+1}"))
        
        keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("❌ Close Menu", callback_data="help_close")])
        return InlineKeyboardMarkup(keyboard)

    # ============================================================
    # 🎛️ CALLBACK QUERY HANDLERS
    # ============================================================
    @app.on_callback_query(filters.regex(r"^help_page_(\d+)"))
    async def paginate_help(client, callback):
        page = int(callback.matches[0].group(1))
        try:
            await callback.message.edit_text(
                __help__,
                reply_markup=get_help_keyboard(page)
            )
        except Exception:
            pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^help_(.+)_(.+)"))
    async def module_help_callback(client, callback):
        mod = callback.matches[0].group(1)
        page = callback.matches[0].group(2)

        if mod == "close":
            return await callback.message.delete()

        text = HELP_TEXTS.get(mod, "❌ **Module information not available.**")
        back_kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data=f"help_page_{page}")]])

        try:
            await callback.message.edit_text(text, reply_markup=back_kb)
        except Exception:
            pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^help_noop$"))
    async def noop_callback(client, callback):
        await callback.answer("You are on this page!", show_alert=False)

    @app.on_callback_query(filters.regex(r"^help_close$"))
    async def close_help_menu(client, callback):
        await callback.message.delete()

    # ============================================================
    # 🎟️ PRIVATE CHAT TICKET FORWARDING SYSTEM
    # ============================================================
    @app.on_message(filters.private & ~filters.bot & ~filters.command(["start", "help"]))
    async def forward_help(client, message: Message):
        if not SUPPORT_CHAT:
            return await message.reply_text("❌ **Support system is disabled.**")

        user = message.from_user
        now = time.time()
        if now - LAST_MSG.get(user.id, 0) < SUPPORT_COOLDOWN:
            return await message.reply_text("⏳ **Please wait a few seconds before sending another message.**")
        LAST_MSG[user.id] = now

        if not (message.text or message.caption or message.media):
            return

        ticket_id = generate_ticket()
        TICKET_DB[ticket_id] = user.id

        text = (
            f"╔═══❰ 🎟️ SUPPORT TICKET ❱═══╗\n"
            f"┃ 🆔 Ticket: `{ticket_id}`\n"
            f"┃ 👤 User: {user.mention}\n"
            f"┃ 🆔 ID: `{user.id}`\n"
            f"┃\n"
            f"┃ 💬 Message:\n"
            f"┃ {message.text or message.caption or '📎 Media Content'}\n"
            f"╚════════════════════════╝"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("👤 Profile", url=f"tg://user?id={user.id}"),
             InlineKeyboardButton("❌ Close", callback_data=f"close_{ticket_id}")]
        ])

        try:
            if message.media:
                fwd = await message.forward(SUPPORT_CHAT)
                info = await client.send_message(SUPPORT_CHAT, text, reply_markup=buttons)
                USER_MAP[fwd.id] = user.id
                USER_MAP[info.id] = user.id
            else:
                sent = await client.send_message(SUPPORT_CHAT, text, reply_markup=buttons)
                USER_MAP[sent.id] = user.id

            await message.reply_text(f"✅ **Ticket Created!** ID: `{ticket_id}`\n⏳ Please wait for support staff.")
        except Exception as e:
            logging.error(f"[Support Ticket Error]: {e}")

    @app.on_message(filters.reply & filters.chat(SUPPORT_CHAT))
    async def reply_help(client, message: Message):
        if not message.from_user or message.from_user.id not in ADMINS:
            return
        original = message.reply_to_message
        if not original:
            return
        user_id = USER_MAP.get(original.id)
        if not user_id:
            return await message.reply_text("❌ **User mapping not found.**")

        reply_text = (
            f"╔═══❰ 💬 SUPPORT REPLY ❱═══╗\n"
            f"┃ 👨‍💻 Admin: {message.from_user.mention}\n"
            f"┃\n"
            f"┃ 💬 Reply:\n"
            f"┃ {message.text or message.caption or '📎 Media'}\n"
            f"╚════════════════════════╝"
        )
        try:
            await client.send_chat_action(user_id, "typing")
            if message.media:
                await message.copy(user_id, caption=reply_text)
            else:
                await client.send_message(user_id, reply_text)
            await message.reply_text("✅ **Reply sent.**")
        except Exception as e:
            logging.error(f"[Support Reply Error]: {e}")

    @app.on_callback_query(filters.regex(r"close_(TKT-\d+)"))
    async def close_ticket(client, callback):
        ticket_id = callback.data.split("_")[1]
        user_id = TICKET_DB.get(ticket_id)
        try:
            await callback.message.edit_text(f"❌ **Ticket `{ticket_id}` closed.**")
        except Exception:
            pass
        if user_id:
            try:
                await client.send_message(user_id, f"❌ **Your ticket `{ticket_id}` was closed.**")
            except Exception:
                pass
        await callback.answer("Closed ✅")
