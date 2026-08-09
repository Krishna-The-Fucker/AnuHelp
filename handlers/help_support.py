# ============================================================
# 💎 MODERN SUPPORT & ULTIMATE HELP SYSTEM (85+ MODULES PRO MAX)
# ============================================================

__mod_name__ = "💎 ꜱᴜᴘᴘᴏʀᴛ & ʜᴇʟᴘ"

__help__ = """
*💎 ᴜʟᴛɪᴍᴀᴛᴇ ʙᴏᴛ ʜᴇʟᴘ ᴍᴇɴᴜ (𝟾𝟻+ ᴍᴏᴅᴜʟᴇꜱ)* — ᴇxᴘʟᴏʀᴇ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ʙᴇʟᴏᴡ!

ᴄʟɪᴄᴋ ᴀɴʏ ʙᴜᴛᴛᴏɴ ᴛᴏ ᴠɪᴇᴡ ᴅᴇᴛᴀɪʟᴇᴅ ᴜꜱᴀɢᴇ ɪɴꜱᴛʀᴜᴄᴛɪᴏɴꜱ ꜰᴏʀ ᴛʜᴀᴛ ꜱᴘᴇᴄɪꜰɪᴄ ꜰᴇᴀᴛᴜʀᴇ. ᴜꜱᴇ ɴᴇxᴛ/ʙᴀᴄᴋ/ʜᴏᴍᴇ ᴛᴏ ɴᴀᴠɪɢᴀᴛᴇ ᴛʜʀᴏᴜɢʜ ᴀʟʟ ᴍᴏᴅᴜʟᴇꜱ.
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
    # 📋 85+ MODULES FULL DETAILED COMMANDS & USAGE
    # ============================================================
    HELP_TEXTS = {
        "ᴀʙᴜꜱᴇ": "🛡️ **Abuse Control**\n\n• **Usage:** Automatically filters or restricts abusive words and slang in chats.\n• **Commands:** Auto-filters bad words.",
        "ᴀᴅᴍɪɴ": "👑 **Admin Tools**\n\n• **Usage:** Essential commands for group management.\n• **Commands:** `/ban`, `/unban`, `/mute`, `/unmute`, `/promote`, `/demote`, `/pin`, `/unpin`",
        "ᴀꜰᴋ": "💤 **AFK Module**\n\n• **Usage:** Let others know you are away when they tag you.\n• **Command:** `/afk [reason]`",
        "ᴀɴɪqᴜᴏᴛᴇ": "📜 **Anime Quotes**\n\n• **Usage:** Fetches random motivational or famous anime quotes.\n• **Command:** `/aniquote`",
        "ᴀɴᴛɪ-ʙɪᴏʟɪɴᴋ": "🔗 **Anti-Bio Link**\n\n• **Usage:** Restricts users from putting website/telegram links in their profile bio.",
        "ᴀɴᴛɪ-ᴇᴅɪᴛᴇ": "✏️ **Anti-Edit Tracker**\n\n• **Usage:** Detects and logs when a user edits their message in chat.",
        "ᴀɴᴛɪ-ꜰʟᴏᴏᴅ": "🌊 **Anti-Flood System**\n\n• **Usage:** Prevents continuous message spamming by a single user automatically.",
        "ᴀɴᴛɪ-ᴩʀᴏɴ": "🔞 **Anti-Pron / NSFW**\n\n• **Usage:** Automatically detects and removes NSFW or adult media contents.",
        "ᴀɴᴛɪ-ʀᴀɪᴅ": "🛡️ **Anti-Raid Protection**\n\n• **Usage:** Protects group from sudden mass bot/user attacks by locking chat.",
        "ᴀᴩᴩʀᴏᴠᴇ": "✅ **Approval System**\n\n• **Usage:** Approves trusted users to bypass certain chat restrictions.\n• **Commands:** `/approve`, `/unapprove`",
        "ᴀᴜᴛᴏ-ꜱᴩᴀᴍ": "🤖 **Auto Spam Detection**\n\n• **Usage:** AI-based automatic detection and punishment of spam messages.",
        "ᴀᴜᴛᴏ-ᴅᴇʟ": "🗑️ **Auto Delete**\n\n• **Usage:** Automatically deletes service or specific command messages after a set time.\n• **Command:** `/autodel [time]`",
        "ʙᴀᴄᴋᴜᴩꜱ": "💾 **Backups Manager**\n\n• **Usage:** Takes backup of database and chat settings.\n• **Command:** `/backup`",
        "ʙᴀɴ-ᴀʟʟ": "⚠️ **Ban All (Sudo)**\n\n• **Usage:** Mass ban utility for emergency situations (Sudo users only).\n• **Command:** `/banall`",
        "ʙʟ-ᴄʜᴀᴛ": "🚫 **Blacklist Chat**\n\n• **Usage:** Restricts bot usage in unauthorized or blacklisted groups.",
        "ʙʟ-ᴜꜱᴇʀ": "🚷 **Blacklist User**\n\n• **Usage:** Globally blacklists misbehaving users from accessing the bot.\n• **Command:** `/bluser [id]`",
        "ʙʟᴏᴄᴋʟɪꜱᴛ": "📋 **Word Blacklist**\n\n• **Usage:** Adds specific words to the group's auto-delete/warn list.\n• **Commands:** `/blacklist`, `/addbl [word]`, `/rmbl [word]`",
        "ʙʟᴏᴄᴋʟɪꜱᴛ-ᴜꜱᴇʀ": "👤🚫 **Blacklist User Module**\n\n• **Usage:** Manages restricted user database across chats.",
        "ʙʀᴏᴀᴅᴄᴀᴛ": "📢 **Broadcast System**\n\n• **Usage:** Sends announcements to all registered users or chats.\n• **Command:** `/broadcast [text]`",
        "ᴄᴀᴩᴛᴄʜᴀ": "🧩 **Captcha Verification**\n\n• **Usage:** Verifies new members with buttons or math puzzles to stop bots.",
        "ᴄʜᴀᴛʙᴏᴛ": "🤖 **AI Chatbot**\n\n• **Usage:** Intelligent conversational AI bot feature for groups.",
        "ᴄʟᴇᴀɴ-ꜱᴇʀᴠᴜᴄᴇ": "🧹 **Clean Service Messages**\n\n• **Usage:** Automatically deletes 'user joined/left' service logs to keep chat clean.",
        "ᴄʟᴇᴀɴᴇʀ": "🧽 **Cleaner Tool**\n\n• **Usage:** Cleans up old cache and temporary database files.",
        "ᴄᴏɴɴᴇᴄᴛɪᴏɴ": "🔗 **Chat Connections**\n\n• **Usage:** Connects group to remote plugins/databases.\n• **Command:** `/connect`",
        "ᴄᴏᴜᴩʟᴇ-ɢᴀᴍᴇꜱ": "💞 **Couples Game**\n\n• **Usage:** Finds a random cute couple of the day in your group.\n• **Command:** `/couple`",
        "ᴄᴜʀʀᴇɴᴄʏ-ᴄᴏɴᴠᴇʀᴛᴇʀ": "💱 **Currency Converter**\n\n• **Usage:** Converts currency rates in real-time.\n• **Command:** `/convert [amount] [from] [to]`",
        "ᴄᴜꜱᴛ-ꜰɪʟᴛᴇʀꜱ": "⚡ **Custom Filters**\n\n• **Usage:** Saves custom automated replies for specific keywords.\n• **Commands:** `/filter`, `/filters`, `/stop`",
        "ᴅʙ-ᴄʟᴇᴀɴ": "🗄️ **Database Cleaner**\n\n• **Usage:** Clears inactive chats and dead users from database.",
        "ᴅᴇʙᴜɢ": "🛠️ **Debug Logs**\n\n• **Usage:** Developer tool to check error traces and performance logs.",
        "ᴅᴇᴠ": "👨‍💻 **Developer Utilities**\n\n• **Usage:** Special administrative commands exclusively for bot owners.",
        "ᴅisᴀʙʟᴇ": "🔕 **Disable Commands**\n\n• **Usage:** Disables specific commands in a group.\n• **Command:** `/disable [cmd]`",
        "ᴅʀᴀᴡ": "🎨 **Image Draw / AI Art**\n\n• **Usage:** Generates stunning AI images from text prompts.\n• **Command:** `/draw [prompt]`",
        "ᴇᴄᴏɴᴏᴍʏ-ɢᴀᴍᴇꜱ": "💰 **Economy System**\n\n• **Usage:** Virtual currency, wallet management, and daily rewards.\n• **Commands:** `/balance`, `/daily`, `/rob`",
        "ᴇʀʀᴏʀ": "⚠️ **Error Handler**\n\n• **Usage:** Gracefully catches and logs bot runtime exceptions.",
        "ᴇᴠᴀʟ": "⚡ **Evaluator (Sudo)**\n\n• **Usage:** Executes Python code directly on server terminal (Sudo only).",
        "ꜰᴇᴅ": "🌐 **Federations (Fed Ban)**\n\n• **Usage:** Bans a user across multiple connected groups simultaneously.\n• **Commands:** `/fedcreate`, `/fban`, `/unfban`",
        "ꜰɪʟᴛᴇʀꜱ": "⚡ **Filters Module**\n\n• **Usage:** Advanced filter handling system for groups.",
        "ꜱᴛʏʟɪꜱʜ-ɴᴀᴍᴇ": "🔤 **Fancy Fonts Generator**\n\n• **Usage:** Converts normal text into stylish cool fonts.\n• **Command:** `/font [text]`",
        "ꜰᴏʀᴄᴇ-ᴊᴏɪɴ": "📢 **Force Subscribe**\n\n• **Usage:** Forces users to join a channel before chatting in the group.\n• **Command:** `/fsub [channel]`",
        "ꜰᴜɴ-ɢᴀᴍᴇꜱ": "🎮 **Fun & Entertainment**\n\n• **Usage:** Fun commands and mini interaction tools like dice and dart.\n• **Commands:** `/dice`, `/dart`",
        "ꜰᴜɴ-ꜱᴛʀɪɴɢ": "💬 **Fun Strings**\n\n• **Usage:** Stores hilarious dialogues and responses.",
        "ᴀꜱᴋ": "✨ **Google Gemini AI**\n\n• **Usage:** Chat with Gemini AI directly inside chat.\n• **Command:** `/gemini [query]` or `/ask`",
        "ᴄᴏᴍᴍᴏɴ-ᴄʜᴀᴛꜱ": "👥 **Common Chats**\n\n• **Usage:** Finds groups shared between the bot and a user.",
        "ɢᴀᴛ-ᴛɪᴍᴇ": "⏰ **Time Utility**\n\n• **Usage:** Shows current time across different global timezones.",
        "ɢɪꜰ": "🎞️ **GIF Search**\n\n• **Usage:** Searches and sends cool GIFs.\n• **Command:** `/gif [query]`",
        "ɢɪᴛʜᴜʙ": "🐙 **GitHub Uploader**\n\n• **Usage:** Uploads files or logs directly to GitHub repositories.\n• **Command:** `/github`",
        "ɢʀᴏᴜᴩ-ᴍᴀɴᴀɢᴇᴍᴇɴᴛ": "👥 **Group Management**\n\n• **Usage:** Core settings and configuration tools for groups.",
        "ʜᴀᴄᴋᴇʀ-ɢᴀᴍᴇ": "💻 **Hacker Game**\n\n• **Usage:** Interactive simulated hacking mini-game to hack friends.\n• **Command:** `/hack [user]`",
        "ʟᴀɴɢuᴀɢᴇ": "🌐 **Language Settings**\n\n• **Usage:** Changes bot language preferences for chats.\n• **Command:** `/lang [code]`",
        "ʟᴏᴄᴋꜱ": "🔒 **Chat Locks**\n\n• **Usage:** Locks links, stickers, media types in chats.\n• **Commands:** `/lock [type]`, `/unlock [type]`",
        "ʟᴏɢᴏ-ᴍᴀᴋᴇʀ": "🖼️ **Logo Maker**\n\n• **Usage:** Creates custom name logos on attractive banners.\n• **Command:** `/logo [text]`",
        "mᴀꜰɪʏᴀ-ɢᴀᴍᴇ": "🕵️ **Mafia Game**\n\n• **Usage:** Interactive group Mafia/Murder mystery roleplay game.\n• **Command:** `/mafia`",
        "ᴍᴇᴍɪꜰʏ": "🖼️ **Memify Tool**\n\n• **Usage:** Adds custom text to top of stickers or images.\n• **Command:** `/mm` (reply to media)",
        "ᴍɪꜱᴄᴇ": "🛠️ **Miscellaneous**\n\n• **Usage:** Extra utility tools and helpers.",
        "ɴɪɢʜᴛ-ᴍᴏᴅᴇ": "🌙 **Night Mode**\n\n• **Usage:** Automatically closes/locks group during night hours.\n• **Command:** `/nightmode [on/off]`",
        "ɴᴏᴛᴇꜱ": "📝 **Saved Notes**\n\n• **Usage:** Saves important notes and documentation in chat.\n• **Commands:** `/save [name]`, `/notes`, `#[name]`",
        "ᴩɪɴꜱ": "📌 **Pin Management**\n\n• **Usage:** Advanced pinned messages controller.\n• **Command:** `/pin`",
        "ᴩᴜʀɢᴇ": "🗑️ **Purge Messages**\n\n• **Usage:** Deletes bulk messages instantly from chat.\n• **Command:** `/purge` or `/del`",
        "𝚀ᴜɪᴄᴋ-ɢᴀᴍᴇꜱ": "🎯 **Quick Games**\n\n• **Usage:** Fast mini games like truth and dare.\n• **Commands:** `/truth`, `/dare`",
        "ʀᴇᴀᴄᴛɪᴏɴ": "❤️ **Auto Reactions**\n\n• **Usage:** Reacts automatically to specific chat keywords.",
        "ʀᴇᴩᴏʀᴛɪɴɢ": "🚨 **Admin Reporting**\n\n• **Usage:** Reports message to admins using `@admin` tag.",
        "ʀᴜʟᴇꜱ": "📜 **Chat Rules**\n\n• **Usage:** Displays guidelines and rules of the group.\n• **Command:** `/rules`",
        "ꜱᴇᴅ": "🔤 **Sed Replacement**\n\n• **Usage:** Replaces typos using s/old/new format instantly.",
        "ꜱʜᴇʟʟ": "💻 **Terminal Shell**\n\n• **Usage:** Executes linux shell commands on server (Sudo only).",
        "ꜱᴏᴜʀᴄᴇ": "📦 **Source Code**\n\n• **Usage:** Shows GitHub repository link of the bot.\n• **Command:** `/source`",
        "ꜱᴛɪᴄᴋᴇʀs": "🎨 **Sticker Tools**\n\n• **Usage:** Converts images/emojis to custom sticker packs.\n• **Command:** `/kang`",
        "ꜱᴛɪɴɢ-ɢᴇɴ": "🪡 **String Session Gen**\n\n• **Usage:** Generates Pyrogram/Telethon userbot string sessions.\n• **Command:** `/string`",
        "ꜱᴜᴅᴏ": "⚡ **Sudo Controls**\n\n• **Usage:** Bot administrator and elevated permission controls.",
        "ᴛᴀɢ-ᴀʟʟ": "📢 **Tag All Members**\n\n• **Usage:** Mentions all group members in one go.\n• **Commands:** `/tagall [text]`, `/cancel`",
        "ᴛᴇʟᴇɢᴀʀᴀᴩʜ": "🌐 **Telegraph Maker**\n\n• **Usage:** Uploads text or media directly to a telegraph link.\n• **Command:** `/tgm`",
        "ᴛʀᴜᴛʜ-&-ᴅᴀʀᴇ": "🎯 **Truth & Dare**\n\n• **Usage:** Plays fun truth or dare interactive questions.\n• **Commands:** `/truth`, `/dare`",
        "ᴜᴅ": "📖 **Urban Dictionary**\n\n• **Usage:** Searches slang meanings on Urban Dictionary.\n• **Command:** `/ud [word]`",
        "underworld_game": "🎲 **Underworld Game**\n\n• **Usage:** Interactive underworld mafia roleplay game.",
        "ᴜꜱᴇʀ": "👤 **User Info**\n\n• **Usage:** Fetches basic profile info of users.\n• **Command:** `/id`",
        "ᴜꜱᴇʀɪɴꜰᴏ": "ℹ️ **Detailed User Info**\n\n• **Usage:** Extended user profile tracking and history module.\n• **Command:** `/info`",
        "ᴡᴀʀɴ": "⚠️ **Warning System**\n\n• **Usage:** Warns users; auto-bans or mutes upon reaching limit.\n• **Commands:** `/warn`, `/unwarn`, `/warns`",
        "ᴡᴇʟᴄᴏᴍᴇ": "👋 **Welcome Greeter**\n\n• **Usage:** Sends custom greeting cards to newcomers.\n• **Commands:** `/setwelcome`, `/welcome`",
        "ᴡɪᴋɪ": "📚 **Wikipedia Search**\n\n• **Usage:** Searches Wikipedia articles directly in chat.\n• **Command:** `/wiki [query]`",
        "ᴡʀɪᴛᴇ": "✍️ **Handwriting Writer**\n\n• **Usage:** Converts text into realistic handwritten pages.\n• **Command:** `/write [text]`",
        "ᴢɪᴩ": "🗜️ **Zip Compressor**\n\n• **Usage:** Compresses or extracts zip archives easily.\n• **Commands:** `/zip`, `/unzip`"
    }

    # ============================================================
    # 📄 6-PART PAGINATED KEYBOARDS (WITH NEXT, BACK, HOME BUTTONS)
    # ============================================================
    def get_help_keyboard(page=1):
        keys = list(HELP_TEXTS.keys())
        total_items = len(keys)
        
        per_page = (total_items + 5) // 6 
        if per_page < 1:
            per_page = 1

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_keys = keys[start_idx:end_idx]

        keyboard = []
        row = []
        for k in current_keys:
            display_name = "".join([
                {"a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ", "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ", "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ", "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ", "_": " "}.get(c, c)
                for c in k.replace("_", " ").lower()
            ]).title()

            row.append(InlineKeyboardButton(display_name, callback_data=f"help_{k}_{page}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        nav_buttons = []
        total_pages = 6
        
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"help_page_{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="help_page_1"))
        nav_buttons.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="help_noop"))
        
        if page < total_pages and end_idx < total_items:
            nav_buttons.append(InlineKeyboardButton("ɴᴇxᴛ ➡️", callback_data=f"help_page_{page+1}"))
        
        keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("❌ ᴄʟᴏꜱᴇ ᴍᴇɴᴜ", callback_data="help_close")])
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

        text = HELP_TEXTS.get(mod, "❌ **ᴍᴏᴅᴜʟᴇ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ.**")
        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 ʙᴀᴄᴋ ᴛᴏ ᴍᴇɴᴜ", callback_data=f"help_page_{page}")],
            [InlineKeyboardButton("🏠 ʜᴏᴍᴇ", callback_data="help_page_1")]
        ])

        try:
            await callback.message.edit_text(text, reply_markup=back_kb)
        except Exception:
            pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^help_noop$"))
    async def noop_callback(client, callback):
        await callback.answer("ʏᴏᴜ ᴀʀᴇ ᴏɴ ᴛʜɪꜱ ᴘᴀɢᴇ!", show_alert=False)

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
        await callback.answer("ᴄʟᴏꜱᴇ ⚡")
