# ============================================================
# 🤖 CAPTCHA SYSTEM (FINAL PRO MAX - FIXED + OPTIMIZED)
# ============================================================

__mod_name__ = "🤖 ᴄᴀᴘᴛᴄʜᴀ"

__help__ = """
*🤖 ᴄᴀᴘᴛᴄʜᴀ sʏsᴛᴇᴍ* — Protect your group from bot raids and spam by requiring new users to solve a quick captcha!

• `/captcha` — Check or toggle captcha settings
"""

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions, Message, CallbackQuery
import asyncio
import random
import string
import logging

def register_captcha_system(app, db, OWNER_ID, DEV_LIST, IGNORE_DEVS):

    CAPTCHA_TIMEOUT = 60  # seconds

    # ============================================================
    # 🧠 GENERATE CAPTCHA
    # ============================================================
    def generate_captcha():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    # ============================================================
    # 🚫 NEW USER JOIN WATCHER
    # ============================================================
    @app.on_message(filters.new_chat_members, group=3)
    async def captcha_join(client, message: Message):
        chat_id = message.chat.id

        for user in message.new_chat_members:
            if user.is_bot:
                continue

            if user.id == OWNER_ID or (IGNORE_DEVS and user.id in DEV_LIST):
                continue

            # Check if already exists (anti-duplicate)
            existing = await db.captcha.find_one({
                "chat_id": chat_id,
                "user_id": user.id
            })

            if existing and not existing.get("verified"):
                continue

            captcha_text = generate_captcha()

            try:
                # Restrict user (full mute)
                await client.restrict_chat_member(
                    chat_id,
                    user.id,
                    ChatPermissions(can_send_messages=False)
                )
            except Exception as e:
                logging.error(f"[Captcha Restriction Error]: {e}")
                continue

            # Save in DB
            await db.captcha.update_one(
                {"chat_id": chat_id, "user_id": user.id},
                {"$set": {
                    "captcha": captcha_text,
                    "verified": False
                }},
                upsert=True
            )

            try:
                msg = await message.reply(
                    f"🔐 **Welcome** {user.mention}!\n\n"
                    f"👉 **Please verify yourself to chat!**\n"
                    f"• **Captcha Code:** `{captcha_text}`\n\n"
                    f"_Click the button below and type this code in chat._",
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("✅ Verify Now", callback_data=f"verify_{user.id}")]]
                    )
                )
            except Exception:
                continue

            # Timeout system background task
            async def timeout_watcher():
                await asyncio.sleep(CAPTCHA_TIMEOUT)
                data = await db.captcha.find_one({"chat_id": chat_id, "user_id": user.id})

                if data and not data.get("verified"):
                    try:
                        await client.ban_chat_member(chat_id, user.id)
                        await client.unban_chat_member(chat_id, user.id) # Kick pattern
                        await msg.edit(f"❌ {user.mention} failed to verify within time → **Kicked!**")
                    except Exception:
                        pass

            try:
                app.loop.create_task(timeout_watcher())
            except Exception:
                asyncio.create_task(timeout_watcher())

    # ============================================================
    # ✅ VERIFY BUTTON HANDLER
    # ============================================================
    @app.on_callback_query(filters.regex("^verify_"))
    async def verify_captcha(client, callback: CallbackQuery):
        try:
            user_id = int(callback.data.split("_")[1])
            chat_id = callback.message.chat.id

            if callback.from_user.id != user_id:
                return await callback.answer("❌ This verification button is not for you!", show_alert=True)

            data = await db.captcha.find_one({"chat_id": chat_id, "user_id": user_id})

            if not data or data.get("verified"):
                return await callback.answer("❌ Captcha already verified or expired!", show_alert=True)

            await callback.message.reply(
                f"✍️ **{callback.from_user.mention}, please send the exact captcha code (`{data.get('captcha')}`) in this chat to verify.**"
            )
            await callback.answer("Check message instructions!", show_alert=False)
        except Exception as e:
            logging.error(f"[Captcha Callback Error]: {e}")

    # ============================================================
    # ✍️ TEXT VERIFICATION HANDLER
    # ============================================================
    @app.on_message(filters.text & filters.group, group=4)
    async def check_captcha(client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        data = await db.captcha.find_one({"chat_id": chat_id, "user_id": user_id})

        if not data or data.get("verified"):
            return

        if message.text.strip().upper() == data.get("captcha"):
            # Mark verified
            await db.captcha.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": {"verified": True}}
            )

            try:
                # Unmute user fully
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_polls=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True,
                        can_invite_users=True
                    )
                )
                await message.reply(f"✅ **Verification Successful!** Welcome to the group, {message.from_user.mention} 🎉")
            except Exception as e:
                logging.error(f"[Captcha Unmute Error]: {e}")
        else:
            # Wrong text entered, delete or notify optionally to prevent clutter
            pass
