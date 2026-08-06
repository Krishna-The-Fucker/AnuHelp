# ============================================================
# 🚀 START & HELP MODULE (WITH OWNER BUTTON)
# ============================================================

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_USERNAME, START_VIDEO_URL, SUPPORT_CHAT, LOG_CHANNEL, OWNER_ID
from db import add_user

# ============================================================
# 📌 START COMMAND
# ============================================================

@filters.command("start")
@filters.private
async def start_handler(client, message: Message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    await add_user(user_id, name)
    
    caption = (
        f"**👋 Hello {name}, I am {client.me.mention}!**\n\n"
        "⚡ **An Advanced Group Manager & Moderation Bot**.\n"
        "✨ *Add me to your group and make me an admin to get started!*"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 Update Channel", url=f"https://t.me/{LOG_CHANNEL}" if LOG_CHANNEL else "https://t.me/telegram"),
            InlineKeyboardButton("💬 Support Channel", url=f"https://t.me/{SUPPORT_CHAT}" if SUPPORT_CHAT else "https://t.me/telegram")
        ],
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("🛠 Help & Commands", callback_data="help_menu")
        ]
    ])

    if START_VIDEO_URL and START_VIDEO_URL.endswith(".mp4"):
        await message.reply_video(
            video=START_VIDEO_URL,
            caption=caption,
            reply_markup=keyboard
        )
    else:
        await message.reply_photo(
            photo=START_VIDEO_URL if START_VIDEO_URL else "https://envs.sh/q3z.jpg",
            caption=caption,
            reply_markup=keyboard
        )

# ============================================================
# 🛠 HELP & COMMANDS
# ============================================================

@filters.command("help")
@filters.private
async def help_command_handler(client, message: Message):
    help_text = (
        "**📚 Help & Command Center**\n\n"
        "Choose a category below to view commands:"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛡 Moderation", callback_data="help_mod"),
            InlineKeyboardButton("⚙️ General", callback_data="help_general")
        ],
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("« Back to Start", callback_data="start_back")
        ]
    ])
    await message.reply_text(help_text, reply_markup=keyboard)

# ============================================================
# 🔄 CALLBACK QUERY HANDLERS
# ============================================================

@filters.regex("^help_menu$")
async def help_menu_callback(client, callback_query: CallbackQuery):
    help_text = (
        "**📚 Help & Command Center**\n\n"
        "Choose a category below to view commands:"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🛡 Moderation", callback_data="help_mod"),
            InlineKeyboardButton("⚙️ General", callback_data="help_general")
        ],
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("« Back to Start", callback_data="start_back")
        ]
    ])
    await callback_query.message.edit_text(help_text, reply_markup=keyboard)

@filters.regex("^help_mod$")
async def help_mod_callback(client, callback_query: CallbackQuery):
    text = (
        "**🛡 Moderation Commands:**\n\n"
        " • `/ban` - Ban a user\n"
        " • `/mute` - Mute a user\n"
        " • `/warn` - Warn a user\n"
        " • `/lock` - Lock chat features"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_menu")]])
    await callback_query.message.edit_text(text, reply_markup=keyboard)

@filters.regex("^help_general$")
async def help_general_callback(client, callback_query: CallbackQuery):
    text = (
        "**⚙️ General Commands:**\n\n"
        " • `/start` - Start the bot\n"
        " • `/help` - Open help panel"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_menu")]])
    await callback_query.message.edit_text(text, reply_markup=keyboard)

@filters.regex("^start_back$")
async def start_back_callback(client, callback_query: CallbackQuery):
    name = callback_query.from_user.first_name
    caption = (
        f"**👋 Hello {name}, I am {client.me.mention}!**\n\n"
        "⚡ **An Advanced Group Manager & Moderation Bot**.\n"
        "✨ *Add me to your group and make me an admin to get started!*"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Me To Your Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 Update Channel", url=f"https://t.me/{LOG_CHANNEL}" if LOG_CHANNEL else "https://t.me/telegram"),
            InlineKeyboardButton("💬 Support Channel", url=f"https://t.me/{SUPPORT_CHAT}" if SUPPORT_CHAT else "https://t.me/telegram")
        ],
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("🛠 Help & Commands", callback_data="help_menu")
        ]
    ])
    await callback_query.message.edit_text(caption, reply_markup=keyboard)
