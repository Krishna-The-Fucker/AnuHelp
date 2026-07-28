# ============================================================
# 🤖 Group Manager Bot - Nomad (FINAL PRO VERSION)
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)
from config import BOT_USERNAME, SUPPORT_GROUP, UPDATE_CHANNEL, START_IMAGE, OWNER_ID
import db

# ==========================================================
# 🔥 REGISTER HANDLERS
# ==========================================================
def register_handlers(app: Client):

    # ==========================================================
    # 📢 LOG FUNCTION
    # ==========================================================
    async def log_action(client, text):
        try:
            await client.send_message(UPDATE_CHANNEL, text)
        except:
            pass

    # ==========================================================
    # 🏠 START MENU
    # ==========================================================
    async def send_start_menu(message, user):
        text = f"""
✨ Hello {user}! ✨

👋 I am Nomad 🤖 

🔐 Smart Protection System:
• Anti-Spam + Anti-Link
• Locks System
• Admin Controls
• Fast & Reliable

🚀 More features coming soon...
"""

        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Me To Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
            [
                InlineKeyboardButton("Support", url=SUPPORT_GROUP),
                InlineKeyboardButton("Updates", url=UPDATE_CHANNEL),
            ],
            [
                InlineKeyboardButton("Owner", url=f"tg://user?id={OWNER_ID}"),
                InlineKeyboardButton("GitHub", url="https://github.com/LearningBotsOfficial/Nomade"),
            ],
            [InlineKeyboardButton("📚 Help Menu", callback_data="help")]
        ])

        try:
            if message.text:
                await message.reply_photo(START_IMAGE, caption=text, reply_markup=buttons)
            else:
                media = InputMediaPhoto(media=START_IMAGE, caption=text)
                await message.edit_media(media=media, reply_markup=buttons)
        except:
            await message.reply_text(text, reply_markup=buttons)

    # ==========================================================
    # 🚀 START COMMAND
    # ==========================================================
    @app.on_message(filters.private & filters.command("start"))
    async def start_command(client, message):
        user = message.from_user
        await db.add_user(user.id, user.first_name)
        await send_start_menu(message, user.first_name)

    # ==========================================================
    # 📚 HELP MENU
    # ==========================================================
    async def send_help_menu(message):
        text = """
╔══════════════════╗
     Help Menu
╚══════════════════╝

Choose a category:
"""

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Greetings", callback_data="greetings"),
                InlineKeyboardButton("Locks", callback_data="locks"),
            ],
            [
                InlineKeyboardButton("Moderation", callback_data="moderation")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
        ])

        media = InputMediaPhoto(media=START_IMAGE, caption=text)
        await message.edit_media(media=media, reply_markup=buttons)

    # ==========================================================
    # 🔁 CALLBACK HANDLER
    # ==========================================================
    @app.on_callback_query()
    async def callbacks(client, query):
        data = query.data

        # ===== HELP =====
        if data == "help":
            await send_help_menu(query.message)

        elif data == "back_to_start":
            await send_start_menu(query.message, query.from_user.first_name)

        # ===== GREETINGS =====
        elif data == "greetings":
            text = """
⚙ Welcome System

/setwelcome <text>
/welcome on | off

Placeholders:
{first_name} {username} {mention}
"""
            await query.message.edit_media(
                InputMediaPhoto(START_IMAGE, caption=text),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Back", callback_data="help")]]
                )
            )

        # ===== LOCKS =====
        elif data == "locks":
            text = """
⚙ Locks System

/lock <type>
/unlock <type>

Types:
url | media | sticker | username | language
"""
            await query.message.edit_media(
                InputMediaPhoto(START_IMAGE, caption=text),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Back", callback_data="help")]]
                )
            )

        # ===== MODERATION =====
        elif data == "moderation":
            text = """
⚙ Moderation

/ban /unban
/mute /unmute
/warn /warns
/resetwarns
/promote /demote
"""
            await query.message.edit_media(
                InputMediaPhoto(START_IMAGE, caption=text),
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🔙 Back", callback_data="help")]]
                )
            )

        await query.answer()

    # ==========================================================
    # 📢 BROADCAST
    # ==========================================================
    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_message(client, message):

        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Owner only command")

        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message")

        users = await db.get_all_users()
        sent, failed = 0, 0

        msg = await message.reply_text(f"📢 Broadcasting to {len(users)} users...")

        for i, user_id in enumerate(users):
            try:
                await message.reply_to_message.copy(user_id)
                sent += 1
            except:
                failed += 1

            if i % 50 == 0:
                await msg.edit_text(f"📢 Progress...\nSent: {sent}\nFailed: {failed}")

        await msg.edit_text(f"""
✅ Broadcast Completed

👤 Total: {len(users)}
✔ Sent: {sent}
❌ Failed: {failed}
""")

        await log_action(client, f"📢 Broadcast done by {message.from_user.id}")

    # ==========================================================
    # 📊 STATS
    # ==========================================================
    @app.on_message(filters.private & filters.command("stats"))
    async def stats_command(client, message):

        if message.from_user.id != OWNER_ID:
            return

        users = await db.get_all_users()

        await message.reply_text(f"""
📊 Bot Stats

👤 Users: {len(users)}
⚡ Status: Running
""")
