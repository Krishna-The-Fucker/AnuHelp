# ============================================================
# 🧶 PYROGRAM STRING SESSION GENERATOR MODULE
# ============================================================

__mod_name__ = "🧶 ꜱᴛʀɪɴɢ ɢᴇɴ"

__help__ = """
*🧶 ꜱᴛʀɪɴɢ ɢᴇɴ ᴍᴏᴅᴜʟᴇ* — Generate Pyrogram v2 String Sessions securely via interactive bot steps (Developer / User Utility).

• `/string` or `/genstring` — Start the interactive wizard to generate a Pyrogram session string.
"""

from pyrogram import filters, Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import (
    SessionPasswordNeeded,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    PhoneNumberInvalid,
    ApiIdInvalid
)
import asyncio
import logging

logger = logging.getLogger("STRING_GEN")

# In-memory temporary state tracking for multi-step interactive login
# format: user_id -> {"step": str, "phone": str, "hash": str, "client": Client}
USER_SESSIONS = {}

def register_string_gen_system(app):

    # ============================================================
    # 🚀 START GENERATOR WIZARD (`/string`)
    # ============================================================
    @app.on_message(filters.command(["string", "genstring"]))
    async def string_gen_start(client, message: Message):
        user_id = message.from_user.id

        # Clean up any prior stuck state
        if user_id in USER_SESSIONS:
            try:
                await USER_SESSIONS[user_id]["client"].stop()
            except:
                pass
            USER_SESSIONS.pop(user_id, None)

        text = (
            "🧶 **Pyrogram V2 String Session Generator**\n\n"
            "To generate a session string, you will need your Telegram **API_ID** and **API_HASH** "
            "(obtained from [my.telegram.org](https://my.telegram.org)).\n\n"
            "Do you want to use the default bot/system API credentials or provide your own?"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Use Default API", callback_data="str_default_api"),
                InlineKeyboardButton("✏️ Custom API", callback_data="str_custom_api")
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data="str_cancel")
            ]
        ])

        await message.reply(text, reply_markup=keyboard, disable_web_page_preview=True)

    # ============================================================
    # 🔘 CALLBACK QUERY HANDLER FOR WIZARD STEPS
    # ============================================================
    @app.on_callback_query(filters.regex(r"^str_"))
    async def string_gen_callbacks(client, callback_query: CallbackQuery):
        user_id = callback_query.from_user.id
        data = callback_query.data

        if data == "str_cancel":
            if user_id in USER_SESSIONS:
                try:
                    await USER_SESSIONS[user_id]["client"].stop()
                except:
                    pass
                USER_SESSIONS.pop(user_id, None)
            return await callback_query.message.edit_text("❌ **String session generation cancelled.**")

        elif data == "str_default_api":
            # Pull default config or fallback credentials if defined
            try:
                from config import API_ID, API_HASH
                if not API_ID or not API_HASH:
                    return await callback_query.answer("⚠️ Default API credentials are not configured in your bot files. Please use Custom API.", show_alert=True)
                
                USER_SESSIONS[user_id] = {
                    "api_id": int(API_ID),
                    "api_hash": API_HASH,
                    "step": "waiting_phone"
                }

                await callback_query.message.edit_text(
                    "📱 **Default API Selected.**\n\n"
                    "Now, please send your Telegram account **Phone Number** with country code (e.g., `+1234567890`).\n\n"
                    "_Send /cancel to abort._"
                )
            except ImportError:
                await callback_query.answer("⚠️ API_ID and API_HASH not found in config.py!", show_alert=True)

        elif data == "str_custom_api":
            USER_SESSIONS[user_id] = {"step": "waiting_api_id"}
            await callback_query.message.edit_text(
                "✏️ **Custom API Setup**\n\n"
                "Please send your Telegram **API_ID** (numeric value).\n\n"
                "_Send /cancel to abort._"
            )

    # ============================================================
    # 💬 TEXT MESSAGE LISTENER FOR MULTI-STEP INPUT
    # ============================================================
    @app.on_message(filters.private & ~filters.command(["string", "genstring", "cancel"]))
    async def string_gen_listener(client, message: Message):
        user_id = message.from_user.id
        if user_id not in USER_SESSIONS:
            return

        session_data = USER_SESSIONS[user_id]
        step = session_data.get("step")
        text = message.text.strip()

        try:
            if step == "waiting_api_id":
                try:
                    api_id = int(text)
                except ValueError:
                    return await message.reply("⚠️ **API ID must be an integer number. Try again:**")

                session_data["api_id"] = api_id
                session_data["step"] = "waiting_api_hash"
                await message.reply("🔑 **Great! Now send your Telegram API_HASH (string):**")

            elif step == "waiting_api_hash":
                session_data["api_hash"] = text
                session_data["step"] = "waiting_phone"
                await message.reply("📱 **Now send your Telegram Phone Number with country code (e.g., `+919876543210`):**")

            elif step == "waiting_phone":
                session_data["phone"] = text
                await message.reply("⏳ **Initializing Pyrogram client and sending verification code to Telegram...**")

                # Spin up a temporary temporary Client instance in memory
                temp_client = Client(
                    name=f"gen_{user_id}",
                    api_id=session_data["api_id"],
                    api_hash=session_data["api_hash"],
                    in_memory=True
                )

                await temp_client.connect()
                session_data["client"] = temp_client

                try:
                    sent_code = await temp_client.send_code(text)
                    session_data["hash"] = sent_code.phone_code_hash
                    session_data["step"] = "waiting_code"
                    await message.reply(
                        "📬 **Verification Code Sent!**\n\n"
                        "Please check your official Telegram app for the login code.\n"
                        "Send the code **with spaces between digits** or normally (e.g., `1 2 3 4 5` or `12345`)."
                    )
                except PhoneNumberInvalid:
                    await temp_client.disconnect()
                    USER_SESSIONS.pop(user_id, None)
                    await message.reply("❌ **Invalid Phone Number provided! Please restart with `/string`.**")
                except ApiIdInvalid:
                    await temp_client.disconnect()
                    USER_SESSIONS.pop(user_id, None)
                    await message.reply("❌ **Invalid API ID or API Hash! Please restart with `/string`.**")

            elif step == "waiting_code":
                # Clean code formatting (remove spaces if user included them)
                code = text.replace(" ", "")
                temp_client = session_data["client"]

                try:
                    await temp_client.sign_in(
                        phone_number=session_data["phone"],
                        phone_code_hash=session_data["hash"],
                        phone_code=code
                    )
                    # If successful, export session string
                    string_session = await temp_client.export_session_string()
                    await temp_client.disconnect()
                    USER_SESSIONS.pop(user_id, None)

                    await message.reply(
                        "🎉 **Session String Generated Successfully!**\n\n"
                        f"```python\n{string_session}\n```\n"
                        "🔒 _Keep this string secure and private! Never share it with anyone._",
                        disable_web_page_preview=True
                    )

                except SessionPasswordNeeded:
                    session_data["step"] = "waiting_password"
                    await message.reply(
                        "🔐 **Two-Step Verification (2FA) is enabled on this account.**\n\n"
                        "Please send your 2FA Cloud Password:"
                    )
                except PhoneCodeInvalid:
                    await message.reply("❌ **The confirmation code you entered is invalid. Try again:**")
                except PhoneCodeExpired:
                    await message.reply("❌ **The confirmation code has expired. Please restart with `/string`.**")
                    await temp_client.disconnect()
                    USER_SESSIONS.pop(user_id, None)

            elif step == "waiting_password":
                password = text
                temp_client = session_data["client"]

                try:
                    await temp_client.check_password(password=password)
                    string_session = await temp_client.export_session_string()
                    await temp_client.disconnect()
                    USER_SESSIONS.pop(user_id, None)

                    await message.reply(
                        "🎉 **Session String Generated Successfully (2FA Passed)!**\n\n"
                        f"```python\n{string_session}\n```\n"
                        "🔒 _Keep this string secure and private!_",
                        disable_web_page_preview=True
                    )
                except Exception as e:
                    await message.reply(f"❌ **Incorrect Password or Error:** `{str(e)}`\n\nPlease try entering your password again:")

        except Exception as e:
            logger.error(f"[StringGen Error]: {e}")
            if user_id in USER_SESSIONS:
                try:
                    await USER_SESSIONS[user_id]["client"].stop()
                except:
                    pass
                USER_SESSIONS.pop(user_id, None)
            await message.reply(f"❌ **An unexpected error occurred during string generation:** `{str(e)}`\n\nPlease restart with `/string`.")
