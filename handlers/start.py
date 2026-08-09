# ============================================================
# 🚀 START & (WITH OWNER BUTTON)
# ============================================================

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_USERNAME, START_VIDEO_URL, SUPPORT_CHAT, UPDATE_CHANNEL, OWNER_ID
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
        f"✨ **ʜᴇʟʟᴏ {message.from_user.mention} !**\n\n"
        f"⚡ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ **{client.me.mention}** — ᴛʜᴇ ᴍᴏꜱᴛ ᴘᴏᴡᴇʀꜰᴜʟ ᴜʟᴛɪᴍᴀᴛᴇ ᴩʀᴏ ʙᴏᴛ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ᴇᴀꜱɪʟʏ, ꜱᴀꜰᴇʟʏ! 🔥\n\n"
        f"🪄 ᴀɴᴅ ᴡɪᴛʜ ᴜʟᴛɪᴍᴀᴛᴇ ɢᴀᴍɪɴɢ ᴇɴᴊᴏʏɪɴɢ ꜰᴏʀ ʏᴏᴜʀ ɢʀᴏᴜᴩꜱ\n"
        f"🛡️ **ꜰᴇᴀᴛᴜʀᴇꜱ ᴀᴛ ᴀ ɢʟᴀɴᴄᴇ:**\n"
        f"• 🚫 **ᴜʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ** & ꜱᴇᴄᴜʀɪᴛʏ\n"
        f"• 🥷 **ᴍᴀꜰɪᴀ, ᴜɴᴅᴇʀᴡᴏʀʟᴅ & ʜᴀᴄᴋᴇʀ** ᴍɪɴɪ-ɢᴀᴍᴇꜱ\n"
        f"• 🤖 **ᴀɪ ᴄʜᴀᴛʙᴏᴛ** & 85+ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴜʟᴇꜱ\n\n"
        f"👉 **ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜱᴜᴘᴇʀɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀꜱ ᴀᴅᴍɪɴ ᴛᴏ ʟᴇᴛ ᴍᴇ ɢᴇᴛ ɪɴ ᴀᴄᴛɪᴏɴ!**\n\n"
        f"❓ **ᴡʜɪᴄʜ ᴀʀᴇ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅꜱ?**\n"
        f"ᴘʀᴇꜱꜱ /help ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ᴀɴᴅ ʜᴏᴡ ᴛʜᴇʏ ᴡᴏʀᴋ!"
    )
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ʏᴏᴜʀ ɢʀᴏᴜᴩ ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 ᴜᴩᴅᴀᴛᴇ", url=f"https://t.me/{LOG_CHANNEL}" if LOG_CHANNEL else "https://t.me/krishna_bots"),
            InlineKeyboardButton("💬 ꜱᴜᴩᴩσʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}" if SUPPORT_CHAT else "https://t.me/+MoDgQrl3Cn0yNDRk")
        ],
        [
            InlineKeyboardButton("👑 σᴡηᴇʀ", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("🛠ʜᴇʟᴩ & ꜰᴇᴀᴛᴜʀᴇꜱ", callback_data="help_menu")
        ],
        [
            InlineKeyboardButton("📄 ᴩʀɪᴠᴀᴄʏ ᴩᴏʟɪᴄʏ", callback_data="privacy_policy")
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
            photo=START_VIDEO_URL if START_VIDEO_URL else "https://n.uguu.se/nQlDgtaT.mp4",
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
            InlineKeyboardButton("👑 σᴡηᴇʀ", url=f"tg://user?id={OWNER_ID}")
        ],
        [
            InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="start_back")
        ]
    ])
    
    # Check if update is a CallbackQuery or a Message
    if isinstance(update, CallbackQuery):
        await update.message.edit_text(help_text, reply_markup=keyboard)
    else:
        await update.reply_text(help_text, reply_markup=keyboard)

# ============================================================
# 📄 PRIVACY POLICY CALLBACK HANDLER
# ============================================================

@filters.regex("^privacy_policy$")
async def privacy_policy_callback(client, callback_query: CallbackQuery):
    policy_text = (
        "🛡️ **ᴀɴᴜ x ʀᴏʙᴏᴛ — ᴩʀɪᴠᴀᴄʏ ᴩᴏʟɪᴄʏ**\n\n"
        "1. **Data Security:** We value your privacy. We only store basic group configs, filter settings, and user IDs required for management.\n"
        "2. **No Misuse:** Your data is never shared with third parties.\n"
        "3. **Bot Actions:** The bot only performs administrative actions when triggered by authorized admins or automated security modules.\n\n"
        "✅ *By using this bot, you agree to our terms & safety guidelines.*"
    )
    back_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="start_back")]
    ])
    
    try:
        if callback_query.message.media:
            await callback_query.message.edit_caption(
                caption=policy_text,
                reply_markup=back_kb
            )
        else:
            await callback_query.message.edit_text(
                text=policy_text,
                reply_markup=back_kb
            )
    except Exception:
        pass
    await callback_query.answer()

# ============================================================
# 🔄 BACK TO START CALLBACK HANDLER
# ============================================================

@filters.regex("^start_back$")
async def start_back_callback(client, callback_query: CallbackQuery):
    name = callback_query.from_user.first_name
    caption = (
        f"✨ **ʜᴇʟʟᴏ {callback_query.from_user.mention} !**\n\n"
        f"⚡ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ **{client.me.mention}** — ᴛʜᴇ ᴍᴏꜱᴛ ᴘᴏᴡᴇʀꜰᴜʟ, ᴜʟᴛɪᴍᴀᴛᴇ ᴘʀᴏ ᴍᴀx ʙᴀᴡᴀʟ ʙᴏᴛ ᴛᴏ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘꜱ ᴇᴀꜱɪʟʏ, ꜱᴀꜰᴇʟʏ ᴀɴᴅ ᴡɪᴛʜ ꜰᴜʟʟ ᴇɴᴛᴇʀᴛᴀɪɴᴍᴇɴᴛ! 🔥\n\n"
        f"🛡️ **ꜰᴇᴀᴛᴜʀᴇꜱ ᴀᴛ ᴀ ɢʟᴀɴᴄᴇ:**\n"
        f"• 🚫 **ᴜʟᴛɪᴍᴀᴛᴇ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ** & ꜱᴇᴄᴜʀɪᴛʏ\n"
        f"• 🥷 **ᴍᴀꜰɪᴀ, ᴜɴᴅᴇʀᴡᴏʀʟᴅ & ʜᴀᴄᴋᴇʀ** ᴍɪɴɪ-ɢᴀᴍᴇꜱ\n"
        f"• 🤖 **ᴀɪ ᴄʜᴀᴛʙᴏᴛ** & 85+ ᴀᴅᴠᴀɴᴄᴇᴅ ᴍᴏᴅᴜʟᴇꜱ\n\n"
        f"👉 **ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ꜱᴜᴘᴇʀɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀꜱ ᴀᴅᴍɪɴ ᴛᴏ ʟᴇᴛ ᴍᴇ ɢᴇᴛ ɪɴ ᴀᴄᴛɪᴏɴ!**\n\n"
        f"❓ **ᴡʜɪᴄʜ ᴀʀᴇ ᴛ𝙝𝙚 ᴄᴏᴍᴍᴀɴᴅꜱ?**\n"
        f"ᴘʀᴇꜱꜱ /help ᴛᴏ ꜱᴇᴇ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅꜱ ᴀɴᴅ ʜᴏᴡ ᴛʜᴇʏ ᴡᴏʀᴋ!"
    )
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ʏᴏᴜʀ ɢʀᴏᴜᴩ ➕", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 ᴜᴩᴅᴀᴛᴇ", url=f"https://t.me/{LOG_CHANNEL}" if LOG_CHANNEL else "https://t.me/krishn_bots"),
            InlineKeyboardButton("💬 ꜱᴜᴩᴩσʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}" if SUPPORT_CHAT else "https://t.me/+MoDgQrl3Cn0yNDRk")
        ],
        [
            InlineKeyboardButton("👑 σᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}"),
            InlineKeyboardButton("🛠ʜᴇʟᴩ & ꜰᴇᴀᴛᴜʀᴇꜱ", callback_data="help_menu")
        ],
        [
            InlineKeyboardButton("📄 ᴩʀɪᴠᴀᴄʏ ᴩᴏʟɪᴄʏ", callback_data="privacy_policy")
        ]
    ])
    
    try:
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
    except Exception:
        pass
    await callback_query.answer()
