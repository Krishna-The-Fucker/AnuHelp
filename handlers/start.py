# ============================================================
# Group Manager Bot - Krishna Tiwari 
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from config import BOT_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, START_IMAGE, OWNER_ID
import db

def register_handlers(app: Client):

    # ============================================================
    # 📋 80+ MODULES FULL DETAILED COMMANDS & USAGE
    # ============================================================
    HELP_TEXTS = {
        "abuse": "🛡️ **Abuse Control**\n\n• **Usage:** Automatically filters or restricts abusive words and slang in chats.\n• **Commands:** Auto-filters bad words.",
        "admin": "👑 **Admin Tools**\n\n• **Usage:** Essential commands for group management.\n• **Commands:** `/ban`, `/unban`, `/mute`, `/unmute`, `/promote`, `/demote`, `/pin`, `/unpin`",
        "afk": "💤 **AFK Module**\n\n• **Usage:** Let others know you are away when they tag you.\n• **Command:** `/afk [reason]`",
        "aniquote": "📜 **Anime Quotes**\n\n• **Usage:** Fetches random motivational or famous anime quotes.\n• **Command:** `/aniquote`",
        "anti_biolink": "🔗 **Anti-Bio Link**\n\n• **Usage:** Restricts users from putting website/telegram links in their profile bio.",
        "anti_edite": "✏️ **Anti-Edit Tracker**\n\n• **Usage:** Detects and logs when a user edits their message in chat.",
        "anti_flood": "🌊 **Anti-Flood System**\n\n• **Usage:** Prevents continuous message spamming by a single user automatically.",
        "anti_pron": "🔞 **Anti-Pron / NSFW**\n\n• **Usage:** Automatically detects and removes NSFW or adult media contents.",
        "anti_raid": "🛡️ **Anti-Raid Protection**\n\n• **Usage:** Protects group from sudden mass bot/user attacks by locking chat.",
        "approve": "✅ **Approval System**\n\n• **Usage:** Approves trusted users to bypass certain chat restrictions.\n• **Commands:** `/approve`, `/unapprove`",
        "auto_spam": "🤖 **Auto Spam Detection**\n\n• **Usage:** AI-based automatic detection and punishment of spam messages.",
        "auto_del": "🗑️ **Auto Delete**\n\n• **Usage:** Automatically deletes service or specific command messages after a set time.\n• **Command:** `/autodel [time]`",
        "backups": "💾 **Backups Manager**\n\n• **Usage:** Takes backup of database and chat settings.\n• **Command:** `/backup`",
        "ban_all": "⚠️ **Ban All (Sudo)**\n\n• **Usage:** Mass ban utility for emergency situations (Sudo users only).\n• **Command:** `/banall`",
        "bl_chat": "🚫 **Blacklist Chat**\n\n• **Usage:** Restricts bot usage in unauthorized or blacklisted groups.",
        "bl_user": "🚷 **Blacklist User**\n\n• **Usage:** Globally blacklists misbehaving users from accessing the bot.\n• **Command:** `/bluser [id]`",
        "blacklist": "📋 **Word Blacklist**\n\n• **Usage:** Adds specific words to the group's auto-delete/warn list.\n• **Commands:** `/blacklist`, `/addbl [word]`, `/rmbl [word]`",
        "blacklist_user": "👤🚫 **Blacklist User Module**\n\n• **Usage:** Manages restricted user database across chats.",
        "broadcast": "📢 **Broadcast System**\n\n• **Usage:** Sends announcements to all registered users or chats.\n• **Command:** `/broadcast [text]`",
        "captcha": "🧩 **Captcha Verification**\n\n• **Usage:** Verifies new members with buttons or math puzzles to stop bots.",
        "chatbot": "🤖 **AI Chatbot**\n\n• **Usage:** Intelligent conversational AI bot feature for groups.",
        "clean_service": "🧹 **Clean Service Messages**\n\n• **Usage:** Automatically deletes 'user joined/left' service logs to keep chat clean.",
        "cleaner": "🧽 **Cleaner Tool**\n\n• **Usage:** Cleans up old cache and temporary database files.",
        "connection": "🔗 **Chat Connections**\n\n• **Usage:** Connects group to remote plugins/databases.\n• **Command:** `/connect`",
        "couple_games": "💞 **Couples Game**\n\n• **Usage:** Finds a random cute couple of the day in your group.\n• **Command:** `/couple`",
        "currency_converter": "💱 **Currency Converter**\n\n• **Usage:** Converts currency rates in real-time.\n• **Command:** `/convert [amount] [from] [to]`",
        "cust_filters": "⚡ **Custom Filters**\n\n• **Usage:** Saves custom automated replies for specific keywords.\n• **Commands:** `/filter`, `/filters`, `/stop`",
        "db_clean": "🗄️ **Database Cleaner**\n\n• **Usage:** Clears inactive chats and dead users from database.",
        "debug": "🛠️ **Debug Logs**\n\n• **Usage:** Developer tool to check error traces and performance logs.",
        "dev": "👨‍💻 **Developer Utilities**\n\n• **Usage:** Special administrative commands exclusively for bot owners.",
        "disable": "🔕 **Disable Commands**\n\n• **Usage:** Disables specific commands in a group.\n• **Command:** `/disable [cmd]`",
        "draw": "🎨 **Image Draw / AI Art**\n\n• **Usage:** Generates stunning AI images from text prompts.\n• **Command:** `/draw [prompt]`",
        "economy_games": "💰 **Economy System**\n\n• **Usage:** Virtual currency, wallet management, and daily rewards.\n• **Commands:** `/balance`, `/daily`, `/rob`",
        "error": "⚠️ **Error Handler**\n\n• **Usage:** Gracefully catches and logs bot runtime exceptions.",
        "eval": "⚡ **Evaluator (Sudo)**\n\n• **Usage:** Executes Python code directly on server terminal (Sudo only).",
        "fed": "🌐 **Federations (Fed Ban)**\n\n• **Usage:** Bans a user across multiple connected groups simultaneously.\n• **Commands:** `/fedcreate`, `/fban`, `/unfban`",
        "filters": "⚡ **Filters Module**\n\n• **Usage:** Advanced filter handling system for groups.",
        "stylish_name": "🔤 **Fancy Fonts Generator**\n\n• **Usage:** Converts normal text into stylish cool fonts.\n• **Command:** `/font [text]`",
        "force_join": "📢 **Force Subscribe**\n\n• **Usage:** Forces users to join a channel before chatting in the group.\n• **Command:** `/fsub [channel]`",
        "fun_games": "🎮 **Fun & Entertainment**\n\n• **Usage:** Fun commands and mini interaction tools like dice and dart.\n• **Commands:** `/dice`, `/dart`",
        "fun_string": "💬 **Fun Strings**\n\n• **Usage:** Stores hilarious dialogues and responses.",
        "ask": "✨ **Google Gemini AI**\n\n• **Usage:** Chat with Gemini AI directly inside chat.\n• **Command:** `/gemini [query]` or `/ask`",
        "common_chats": "👥 **Common Chats**\n\n• **Usage:** Finds groups shared between the bot and a user.",
        "gat_time": "⏰ **Time Utility**\n\n• **Usage:** Shows current time across different global timezones.",
        "gif": "🎞️ **GIF Search**\n\n• **Usage:** Searches and sends cool GIFs.\n• **Command:** `/gif [query]`",
        "github": "🐙 **GitHub Uploader**\n\n• **Usage:** Uploads files or logs directly to GitHub repositories.\n• **Command:** `/github`",
        "group_management": "👥 **Group Management**\n\n• **Usage:** Core settings and configuration tools for groups.",
        "hacker_game": "💻 **Hacker Game**\n\n• **Usage:** Interactive simulated hacking mini-game to hack friends.\n• **Command:** `/hack [user]`",
        "language": "🌐 **Language Settings**\n\n• **Usage:** Changes bot language preferences for chats.\n• **Command:** `/lang [code]`",
        "locks": "🔒 **Chat Locks**\n\n• **Usage:** Locks links, stickers, media types in chats.\n• **Commands:** `/lock [type]`, `/unlock [type]`",
        "logo_maker": "🖼️ **Logo Maker**\n\n• **Usage:** Creates custom name logos on attractive banners.\n• **Command:** `/logo [text]`",
        "mafiya_game": "🕵️ **Mafia Game**\n\n• **Usage:** Interactive group Mafia/Murder mystery roleplay game.\n• **Command:** `/mafia`",
        "memify": "🖼️ **Memify Tool**\n\n• **Usage:** Adds custom text to top of stickers or images.\n• **Command:** `/mm` (reply to media)",
        "misce": "🛠️ **Miscellaneous**\n\n• **Usage:** Extra utility tools and helpers.",
        "night_mode": "🌙 **Night Mode**\n\n• **Usage:** Automatically closes/locks group during night hours.\n• **Command:** `/nightmode [on/off]`",
        "notes": "📝 **Saved Notes**\n\n• **Usage:** Saves important notes and documentation in chat.\n• **Commands:** `/save [name]`, `/notes`, `#[name]`",
        "pins": "📌 **Pin Management**\n\n• **Usage:** Advanced pinned messages controller.\n• **Command:** `/pin`",
        "purge": "🗑️ **Purge Messages**\n\n• **Usage:** Deletes bulk messages instantly from chat.\n• **Command:** `/purge` or `/del`",
        "quick_games": "🎯 **Quick Games**\n\n• **Usage:** Fast mini games like truth and dare.\n• **Commands:** `/truth`, `/dare`",
        "reaction": "❤️ **Auto Reactions**\n\n• **Usage:** Reacts automatically to specific chat keywords.",
        "reporting": "🚨 **Admin Reporting**\n\n• **Usage:** Reports message to admins using `@admin` tag.",
        "rules": "📜 **Chat Rules**\n\n• **Usage:** Displays guidelines and rules of the group.\n• **Command:** `/rules`",
        "sed": "🔤 **Sed Replacement**\n\n• **Usage:** Replaces typos using s/old/new format instantly.",
        "shell": "💻 **Terminal Shell**\n\n• **Usage:** Executes linux shell commands on server (Sudo only).",
        "source": "📦 **Source Code**\n\n• **Usage:** Shows GitHub repository link of the bot.\n• **Command:** `/source`",
        "stickers": "🎨 **Sticker Tools**\n\n• **Usage:** Converts images/emojis to custom sticker packs.\n• **Command:** `/kang`",
        "sting_gen": "🪡 **String Session Gen**\n\n• **Usage:** Generates Pyrogram/Telethon userbot string sessions.\n• **Command:** `/string`",
        "sudo": "⚡ **Sudo Controls**\n\n• **Usage:** Bot administrator and elevated permission controls.",
        "tag_all": "📢 **Tag All Members**\n\n• **Usage:** Mentions all group members in one go.\n• **Commands:** `/tagall [text]`, `/cancel`",
        "telegaraph": "🌐 **Telegraph Maker**\n\n• **Usage:** Uploads text or media directly to a telegraph link.\n• **Command:** `/tgm`",
        "truth_dare": "🎯 **Truth & Dare**\n\n• **Usage:** Plays fun truth or dare interactive questions.\n• **Commands:** `/truth`, `/dare`",
        "ud": "📖 **Urban Dictionary**\n\n• **Usage:** Searches slang meanings on Urban Dictionary.\n• **Command:** `/ud [word]`",
        "underworld_game": "🎲 **Underworld Game**\n\n• **Usage:** Interactive underworld mafia roleplay game.",
        "user": "👤 **User Info**\n\n• **Usage:** Fetches basic profile info of users.\n• **Command:** `/id`",
        "userinfo": "ℹ️ **Detailed User Info**\n\n• **Usage:** Extended user profile tracking and history module.\n• **Command:** `/info`",
        "warn": "⚠️ **Warning System**\n\n• **Usage:** Warns users; auto-bans or mutes upon reaching limit.\n• **Commands:** `/warn`, `/unwarn`, `/warns`",
        "welcome": "👋 **Welcome Greeter**\n\n• **Usage:** Sends custom greeting cards to newcomers.\n• **Commands:** `/setwelcome`, `/welcome`",
        "wiki": "📚 **Wikipedia Search**\n\n• **Usage:** Searches Wikipedia articles directly in chat.\n• **Command:** `/wiki [query]`",
        "write": "✍️ **Handwriting Writer**\n\n• **Usage:** Converts text into realistic handwritten pages.\n• **Command:** `/write [text]`",
        "zip": "🗜️ **Zip Compressor**\n\n• **Usage:** Compresses or extracts zip archives easily.\n• **Commands:** `/zip`, `/unzip`"
    }

# ==========================================================
# Start Message Functionality
# ==========================================================
    async def send_start_menu(message, user_mention):
        text = (
            f"✨ **ʜᴇʟʟᴏ {user_mention} !**\n\n"
            f"⚡ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ **{bot_name}** — ᴛʜᴇ ᴍᴏꜱᴛ ᴘᴏᴡᴇʀꜰᴜʟ, ᴜʟᴛɪᴍᴀᴛᴇ ᴘʀᴏ ʙᴏᴛ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ᴇᴀꜱɪʟʏ, ꜱᴀꜰᴇʟʏ ! 🔥\n\n"
            f"🛡️ **ꜰᴇᴀᴛᴜʀᴇꜱ ᴀᴛ ᴀ ɢʟᴀɴᴄᴇ:**\n"
            f"🚫 **ᴜʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ** & ꜱᴇᴄᴜʀɪᴛʏ\n"
            f" 🪄ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ & ᴜʟɪᴍᴀᴛᴇ ɢᴀᴍᴇꜱ ᴍᴏᴅᴇ\n"
            f"• 🥷 **ᴍᴀꜰɪᴀ, ᴜɴᴅᴇʀᴡᴏʀʟᴅ & ʜᴀᴄᴋᴇʀ** ᴍɪɴɪ-ɢᴀᴍᴇꜱ\n"
            f"• 🤖 **ᴀɪ ᴄʜᴀᴛʙᴏᴛ** & 85+ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴜʟᴇꜱ\n\n"
            f"👉 **ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜱᴜᴘᴇʀɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀꜱ ᴀᴅᴍɪɴ ᴛᴏ ʟᴇᴛ ᴍᴇ ɢᴇᴛ ɪɴ ᴀᴄᴛɪᴏɴ!**\n\n"
            f"❓ **ᴡʜɪᴄʜ ᴀʀᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅꜱ?**\n"
            f"ᴘʀᴇꜱꜱ /help ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ᴀɴᴅ ʜᴏᴡ ᴛʜᴇʏ ᴡᴏʀᴋ!"
        )

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚒️ Add to Group ⚒️", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [
                InlineKeyboardButton("⌂ Support ⌂", url=SUPPORT_GROUP),
                InlineKeyboardButton("⌂ Update ⌂", url=UPDATE_CHANNEL),
            ],
            [
                InlineKeyboardButton("※ ŎŴɳēŔ ※", url=f"tg://user?id={OWNER_ID}"),
                InlineKeyboardButton("Repo", url="https://github.com/LearningBotsOfficial/Nomade"),
            ],
            [InlineKeyboardButton("📚 Help Commands (80+ Modules) 📚", callback_data="help")]
        ])

        if hasattr(message, "text") and message.text:
            await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons)
        else:
            media = InputMediaPhoto(media=START_IMAGE, caption=text)
            await message.edit_media(media=media, reply_markup=buttons)

# ==========================================================
# Start Command Handler
# ==========================================================
    @app.on_message(filters.private & filters.command("start"))
    async def start_command(client, message):
        user = message.from_user
        await db.add_user(user.id, user.first_name)
        await send_start_menu(message, user.mention)

# ==========================================================
# Help Menu & Dynamic Module Pagination Handler (80+ Modules)
# ==========================================================
    def get_help_keyboard(page=1):
        keys = list(HELP_TEXTS.keys())
        total_items = len(keys)
        per_page = 12 
        
        total_pages = (total_items + per_page - 1) // per_page
        if page > total_pages:
            page = total_pages
        if page < 1:
            page = 1

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        current_keys = keys[start_idx:end_idx]

        keyboard = []
        row = []
        for k in current_keys:
            display_name = k.replace("_", " ").title()
            row.append(InlineKeyboardButton(display_name, callback_data=f"help_mod_{k}_{page}"))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)

        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("⬅️ Back", callback_data=f"help_page_{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton("🏠 Home", callback_data="help_page_1"))
        nav_buttons.append(InlineKeyboardButton(f"📄 {page}/{total_pages}", callback_data="help_noop"))
        
        if page < total_pages:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"help_page_{page+1}"))
        
        keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_start")])
        return InlineKeyboardMarkup(keyboard)

    async def send_help_menu(message):
        text = """
╔══════════════════╗
     Help Menu (80+ Modules)
╚══════════════════╝

Choose a category below to explore commands:
─────────────────────────────
Click any module button below to check its detailed commands and usage instructions.
"""
        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await message.edit_media(media=media, reply_markup=get_help_keyboard(1))

# ==========================================================
# Help Callback Query
# ==========================================================
    @app.on_callback_query(filters.regex("^help$"))
    async def help_callback(client, callback_query):
        await send_help_menu(callback_query.message)
        await callback_query.answer()

    @app.on_callback_query(filters.regex(r"^help_page_(\d+)"))
    async def paginate_help(client, callback):
        page = int(callback.matches[0].group(1))
        text = """
╔══════════════════╗
     Help Menu (80+ Modules)
╚══════════════════╝

Choose a category below to explore commands:
─────────────────────────────
Click any module button below to check its detailed commands and usage instructions.
"""
        try:
            media = InputMediaPhoto(media=START_IMAGE, caption=text)
            await callback.message.edit_media(media=media, reply_markup=get_help_keyboard(page))
        except Exception:
            pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^help_mod_(.+)_(.+)"))
    async def module_help_callback(client, callback):
        mod = callback.matches[0].group(1)
        page = callback.matches[0].group(2)

        desc = HELP_TEXTS.get(mod, "❌ **Module information not available.**")
        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to List", callback_data=f"help_page_{page}")],
            [InlineKeyboardButton("🏠 Home", callback_data="help_page_1")]
        ])

        try:
            media = InputMediaPhoto(media=START_IMAGE, caption=desc)
            await callback.message.edit_media(media=media, reply_markup=back_kb)
        except Exception:
            pass
        await callback.answer()

    @app.on_callback_query(filters.regex(r"^help_noop$"))
    async def noop_callback(client, callback):
        await callback.answer("You are on this page!", show_alert=False)

# ==========================================================
# Back to Start Callback Query
# ==========================================================
    @app.on_callback_query(filters.regex("back_to_start"))
    async def back_to_start_callback(client, callback_query):
        user = callback_query.from_user
        await send_start_menu(callback_query.message, user.mention)
        await callback_query.answer()

# ==========================================================
# Broadcast Command
# ==========================================================
    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_message(client, message):
        if not message.reply_to_message:
            await message.reply_text("⚠️ Please reply to a message to broadcast it.")
            return

        if message.from_user.id != OWNER_ID:
            await message.reply_text("❌ Only the bot owner can use this command.")
            return

        text_to_send = message.reply_to_message.text or message.reply_to_message.caption
        if not text_to_send:
            await message.reply_text("⚠️ The replied message has no text to send.")
            return

        users = await db.get_all_users()
        sent, failed = 0, 0

        await message.reply_text(f"Broadcasting to {len(users)} users..")

        for user_id in users:
            try:
                await client.send_message(user_id, text_to_send)
                sent += 1
            except Exception:
                failed += 1

        await message.reply_text(f"✅ Broadcast finished!\n\n Sent: {sent}\nFailed: {failed}")

# ==========================================================
# Stats Command
# ==========================================================
    @app.on_message(filters.private & filters.command("stats"))
    async def stats_command(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Only the bot owner can use this command")

        users = await db.get_all_users()
        return await message.reply_text(f"💡 Total users: {len(users)}")
