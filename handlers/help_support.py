# ============================================================
# 💎 MODERN SUPPORT SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name = "💎 sᴜᴘᴘᴏʀᴛ"

__help__ = """
*💎 sᴜᴘᴘᴏʀᴛ sʏsᴛᴇᴍ* — Direct ticketing support channel connecting users with admins seamlessly!

• Send any message or media in private chat with the bot to open a support ticket
• Admins can reply directly to the forwarded message in the support group to respond to users
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

    # Configuration values
    SUPPORT_COOLDOWN = 5  # Cooldown in seconds to prevent spam

    # ============================================================
    # 📦 IN-MEMORY STORAGE (or database mapped)
    # ============================================================
    USER_MAP = {}       # msg_id → user_id
    LAST_MSG = {}       # anti spam timestamp tracking
    TICKET_DB = {}      # ticket_id → user_id

    # ============================================================
    # 🎟️ GENERATE TICKET ID
    # ============================================================
    def generate_ticket():
        return f"TKT-{random.randint(1000, 9999)}"

    # ============================================================
    # 👤 USER → BOT (PRIVATE CHAT TICKETING)
    # ============================================================
    @app.on_message(filters.private & ~filters.bot & ~filters.command(["start", "help"]))
    async def forward_help(client, message: Message):
        if not SUPPORT_CHAT:
            return await message.reply_text("❌ **Support system is currently disabled (No support chat configured).**")

        user = message.from_user

        # 🚫 Anti-Spam Check
        now = time.time()
        last = LAST_MSG.get(user.id, 0)

        if now - last < SUPPORT_COOLDOWN:
            return await message.reply_text(
                "⏳ **Slow down!**\nPlease wait a few seconds before sending another message."
            )

        LAST_MSG[user.id] = now

        if not (message.text or message.caption or message.media):
            return await message.reply_text("❌ **Please send text, image, or media content.**")

        # 🎟️ Ticket ID Generation
        ticket_id = generate_ticket()
        TICKET_DB[ticket_id] = user.id

        # 🧾 Stylish Ticket Message
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
            [
                InlineKeyboardButton("👤 Profile", url=f"tg://user?id={user.id}"),
                InlineKeyboardButton("❌ Close", callback_data=f"close_{ticket_id}")
            ]
        ])

        try:
            # 📤 SEND TO SUPPORT CHAT (SUPPORTING ALL MEDIA)
            if message.media:
                fwd = await message.forward(SUPPORT_CHAT)
                info = await client.send_message(
                    SUPPORT_CHAT,
                    text,
                    reply_markup=buttons
                )
                USER_MAP[fwd.id] = user.id
                USER_MAP[info.id] = user.id
            else:
                sent = await client.send_message(
                    SUPPORT_CHAT,
                    text,
                    reply_markup=buttons
                )
                USER_MAP[sent.id] = user.id

            await message.reply_text(
                f"✅ **Ticket Created Successfully!**\n🎟️ ID: `{ticket_id}`\n⏳ Please wait for support staff to reply."
            )
        except Exception as e:
            logging.error(f"[Support Ticket Creation Error]: {e}")
            await message.reply_text("❌ **Failed to send your message to the support team.**")

    # ============================================================
    # 🧑‍💻 ADMIN → USER (REPLY IN SUPPORT GROUP)
    # ============================================================
    @app.on_message(filters.reply & filters.chat(SUPPORT_CHAT))
    async def reply_help(client, message: Message):
        if not message.from_user:
            return

        # 🔒 Check if sender is in admin list or developer list
        if message.from_user.id not in ADMINS:
            return

        original = message.reply_to_message
        if not original:
            return

        user_id = USER_MAP.get(original.id)
        if not user_id:
            return await message.reply_text("❌ **User mapping not found for this ticket message.**")

        reply_text = (
            f"╔═══❰ 💬 SUPPORT REPLY ❱═══╗\n"
            f"┃ 👨‍💻 Admin: {message.from_user.mention}\n"
            f"┃\n"
            f"┃ 💬 Reply:\n"
            f"┃ {message.text or message.caption or '📎 Media Content'}\n"
            f"╚════════════════════════╝"
        )

        try:
            await client.send_chat_action(user_id, "typing")

            # 📤 SEND WITH MEDIA OR TEXT
            if message.media:
                await message.copy(user_id, caption=reply_text)
            else:
                await client.send_message(user_id, reply_text)

            await message.reply_text("✅ **Reply dispatched to user.**")

        except Exception as e:
            logging.error(f"[Support Reply Error]: {e}")
            await message.reply_text("❌ **Failed to send reply. The user might have blocked the bot.**")

    # ============================================================
    # ❌ CLOSE TICKET CALLBACK QUERY
    # ============================================================
    @app.on_callback_query(filters.regex(r"close_(TKT-\d+)"))
    async def close_ticket(client, callback):
        ticket_id = callback.data.split("_")[1]
        user_id = TICKET_DB.get(ticket_id)

        try:
            await callback.message.edit_text(
                f"❌ **Ticket `{ticket_id}` has been closed by {callback.from_user.mention}.**"
            )
        except Exception:
            pass

        if user_id:
            try:
                await client.send_message(
                    user_id,
                    f"❌ **Your support ticket `{ticket_id}` has been closed.**"
                )
            except Exception:
                pass

        await callback.answer("Ticket Closed Successfully ✅")
