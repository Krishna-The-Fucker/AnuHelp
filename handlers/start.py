from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import BOT_USERNAME, START_VIDEO_URL, SUPPORT_CHAT, UPDATE_CHANNEL, OWNER_ID, LOG_CHANNEL
from db import add_user


# ============================================================
# 🔌 LOADER HOOK (FIXED)
# ============================================================

def register_start(app, db, LOG_CHANNEL=None):

    # ============================================================
    # 📌 START COMMAND
    # ============================================================

    @app.on_message(filters.command("start") & filters.private)
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
                InlineKeyboardButton("📢 ᴜᴩᴅᴀᴛᴇ", url=f"https://t.me/{UPDATE_CHANNEL}" if UPDATE_CHANNEL else "https://t.me/krishna_bots"),
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
        except Exception:
            await message.reply_text(text=caption, reply_markup=keyboard)


    # ============================================================
    # 🛠 HELP COMMAND
    # ============================================================

    @app.on_message(filters.command("help") & filters.private)
    async def help_command_handler(client, message: Message):
        help_text = (
            "📚 Help & Command Center\n\n"
            "Choose an option below:"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 σᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="start_back")]
        ])
        await message.reply_text(help_text, reply_markup=keyboard)


    # ============================================================
    # 📌 HELP CALLBACK
    # ============================================================

    @app.on_callback_query(filters.regex("^help_menu$"))
    async def help_menu_callback(client, callback_query: CallbackQuery):
        help_text = (
            "📚 Help & Command Center\n\n"
            "Choose an option below:"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👑 σᴡɴᴇʀ", url=f"tg://user?id={OWNER_ID}")],
            [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="start_back")]
        ])

        try:
            if callback_query.message.media:
                await callback_query.message.edit_caption(caption=help_text, reply_markup=keyboard)
            else:
                await callback_query.message.edit_text(text=help_text, reply_markup=keyboard)
        except Exception:
            pass
        await callback_query.answer()


    # ============================================================
    # 📄 PRIVACY POLICY
    # ============================================================

    @app.on_callback_query(filters.regex("^privacy_policy$"))
    async def privacy_policy_callback(client, callback_query: CallbackQuery):
        policy_text = (
            "🛡️ ᴀɴᴜ x ʀᴏʙᴏᴛ — ᴩʀɪᴠᴀᴄʏ ᴩᴏʟɪᴄʏ\n\n"
            "1. Data Security...\n"
            "2. No Misuse...\n"
            "3. Bot Actions...\n\n"
            "✅ By using this bot, you agree."
        )
        back_kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("« ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", callback_data="start_back")]
        ])

        try:
            if callback_query.message.media:
                await callback_query.message.edit_caption(caption=policy_text, reply_markup=back_kb)
            else:
                await callback_query.message.edit_text(text=policy_text, reply_markup=back_kb)
        except Exception:
            pass
        await callback_query.answer()


    # ============================================================
    # 🔄 BACK CALLBACK
    # ============================================================

    @app.on_callback_query(filters.regex("^start_back$"))
    async def start_back_callback(client, callback_query: CallbackQuery):

        caption = f"✨ **ʜᴇʟʟᴏ {callback_query.from_user.mention}!**"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [InlineKeyboardButton("🛠 Help", callback_data="help_menu")]
        ])

        try:
            await callback_query.message.edit_text(caption, reply_markup=keyboard)
        except:
            pass

        await callback_query.answer()
