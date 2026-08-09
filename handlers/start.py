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
            InlineKeyboardButton("📢 Update Channel", url=f"https://t.me/{LOG_CHANNEL}" if LOG_CHANNEL else "https://t.me/krishna_bots"),
            InlineKeyboardButton("💬 Support Channel", url=f"https://t.me/{SUPPORT_CHAT}" if SUPPORT_CHAT else "https://t.me/+MoDgQrl3Cn0yNDRk")
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
# 🛠 HELP & COMMANDS (COMBINED HANDLER)
# ============================================================

@filters.command("help")
@filters.regex("^help_menu$")
@filters.private
async def help_handler(client, update):
    help_text = (
        "**📚 Help & Command Center**\n\n"
        "Choose an option below:"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑 Owner", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("« Back to Start", callback_data="start_back")
        ]
    ])
    
    # Check if update is a CallbackQuery or a Message
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(help_text, reply_markup=keyboard)
    else:
        await update.reply_text(help_text, reply_markup=keyboard)

# ============================================================
# 🔄 BACK TO START CALLBACK HANDLER
# ============================================================

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
            InlineKeyboardButton("📢 ᴜᴩᴅᴀᴛᴇ", url=f"https://t.me/{LOG_CHANNEL}" if LOG_CHANNEL else "https://t.me/krishn_bots"),
            InlineKeyboardButton("💬 ꜱᴜᴩᴩσʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}" if SUPPORT_CHAT else "https://t.me/+MoDgQrl3Cn0yNDRk")
        ],
        [
            InlineKeyboardButton("👑 σᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("🛠ʜᴇʟᴩ & ꜰᴇᴀᴛᴜʀᴇꜱ", callback_data="help_menu")
        ]
    ])
    
    if callback_query.message.media:
        await callback_query.message.edit_caption(
            caption=caption,
            reply_markup=keyboard
        )
    else:
        await callback_query.message.edit_text(
            text=caption,
            reply_markup=keyboard
        )
