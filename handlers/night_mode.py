# ============================================================
# 🌙 ADVANCED NIGHT MODE SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🌙 ɴɪɢʜᴛ ᴍᴏᴅᴇ"

__help__ = """
*🌙 ɴɪɢʜᴛ ᴍᴏᴅᴇ* — Automatically lock/mute your group at night and unlock in the morning!

• `/nightmode` — Open Night Mode Control Panel
"""

from pyrogram import filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    ChatPermissions
)
from pyrogram.enums import ChatMemberStatus
from datetime import datetime
import asyncio
import logging

def register_night_mode(app, db, LOG_CHANNEL):

    NIGHT_CACHE = {}

    # =========================
    # 👑 ADMIN CHECK
    # =========================
    async def is_admin(client, chat_id, user_id):
        try:
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except:
            return False

    # =========================
    # 🗄️ DB FUNCTIONS
    # =========================
    async def set_night(chat_id, status, start, end):
        await db.night.update_one(
            {"chat_id": chat_id},
            {"$set": {
                "status": status,
                "start": start,
                "end": end
            }},
            upsert=True
        )
        NIGHT_CACHE[chat_id] = {
            "status": status,
            "start": start,
            "end": end
        }

    async def get_night(chat_id):
        if chat_id in NIGHT_CACHE:
            return NIGHT_CACHE[chat_id]

        data = await db.night.find_one({"chat_id": chat_id})
        if not data:
            default_data = {"status": False, "start": "23:00", "end": "06:00"}
            return default_data

        NIGHT_CACHE[chat_id] = data
        return data

    # =========================
    # 🎛️ ADVANCED UI PANEL
    # =========================
    def night_keyboard(status):
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🟢 Enabled" if status else "🔴 Disabled",
                    callback_data="night_toggle"
                )
            ],
            [
                InlineKeyboardButton("⏱️ Change Schedule", callback_data="night_schedule")
            ],
            [
                InlineKeyboardButton("❌ Close Panel", callback_data="night_close")
            ]
        ])

    # =========================
    # ⚙️ COMMAND PANEL
    # =========================
    @app.on_message(filters.command("nightmode") & filters.group)
    async def night_panel(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ **Only admins can use this panel!**")

        data = await get_night(message.chat.id)

        await message.reply(
            f"🌙 **Advanced Night Mode Control Panel**\n\n"
            f"• **Status:** `{'ACTIVE 🟢' if data['status'] else 'INACTIVE 🔴'}`\n"
            f"• **Lock Schedule:** `{data.get('start', '23:00')} ➝ {data.get('end', '06:00')}`\n\n"
            f"_Use the buttons below to toggle state or configure settings._",
            reply_markup=night_keyboard(data["status"])
        )

    # =========================
    # 🎮 CALLBACK BUTTON HANDLER
    # =========================
    @app.on_callback_query(filters.regex("^night_"))
    async def night_buttons(client, query: CallbackQuery):
        chat_id = query.message.chat.id
        user_id = query.from_user.id

        if not await is_admin(client, chat_id, user_id):
            return await query.answer("❌ You are not an admin in this chat!", show_alert=True)

        data = await get_night(chat_id)

        if query.data == "night_toggle":
            new_status = not data["status"]
            start_time = data.get("start", "23:00")
            end_time = data.get("end", "06:00")

            await set_night(chat_id, new_status, start_time, end_time)

            # LOG SYSTEM INTEGRATION
            try:
                await app.send_message(
                    LOG_CHANNEL,
                    f"🌙 **Night Mode State Changed**\n"
                    f"• **Status:** `{'Enabled 🟢' if new_status else 'Disabled 🔴'}`\n"
                    f"• **Chat ID:** `{chat_id}`\n"
                    f"• **Action By:** {query.from_user.mention}"
                )
            except:
                pass

            await query.message.edit_text(
                f"🌙 **Advanced Night Mode Control Panel**\n\n"
                f"• **Status:** `{'ACTIVE 🟢' if new_status else 'INACTIVE 🔴'}`\n"
                f"• **Lock Schedule:** `{start_time} ➝ {end_time}`\n\n"
                f"_Settings updated successfully!_",
                reply_markup=night_keyboard(new_status)
            )

        elif query.data == "night_schedule":
            await query.answer(
                "ℹ️ Default schedule is set from 23:00 to 06:00 IST/UTC.",
                show_alert=True
            )
            return

        elif query.data == "night_close":
            await query.message.delete()
            return

        await query.answer("✨ Updated successfully!")

    # =========================
    # 🔄 BACKGROUND AUTO WATCHER
    # =========================
    async def night_watcher():
        await asyncio.sleep(5)  # Initial delay to let client boot up
        while True:
            try:
                now = datetime.now().strftime("%H:%M")
                chats = await db.night.find({"status": True}).to_list(None)

                for chat in chats:
                    chat_id = chat["chat_id"]
                    start = chat.get("start", "23:00")
                    end = chat.get("end", "06:00")

                    try:
                        # 🌙 NIGHT START (LOCK CHAT)
                        if now == start:
                            await app.set_chat_permissions(
                                chat_id,
                                permissions=ChatPermissions(
                                    can_send_messages=False,
                                    can_send_media_messages=False,
                                    can_send_other_messages=False,
                                    can_add_web_page_previews=False
                                )
                            )
                            await app.send_message(
                                chat_id,
                                "🌙 **Night Mode Activated!**\n🔇 _The group has been muted for the night to prevent spam._"
                            )
                            try:
                                await app.send_message(
                                    LOG_CHANNEL,
                                    f"🌙 **Night Mode Auto-Activated**\n• **Chat ID:** `{chat_id}`"
                                )
                            except:
                                pass

                        # ☀️ NIGHT END (UNLOCK CHAT)
                        elif now == end:
                            await app.set_chat_permissions(
                                chat_id,
                                permissions=ChatPermissions(
                                    can_send_messages=True,
                                    can_send_media_messages=True,
                                    can_send_polls=True,
                                    can_send_other_messages=True,
                                    can_add_web_page_previews=True,
                                    can_invite_users=True
                                )
                            )
                            await app.send_message(
                                chat_id,
                                "☀️ **Good Morning everyone!**\n🔊 _Night Mode ended. Chat has been unmuted._"
                            )
                            try:
                                await app.send_message(
                                    LOG_CHANNEL,
                                    f"☀️ **Night Mode Auto-Ended**\n• **Chat ID:** `{chat_id}`"
                                )
                            except:
                                pass

                    except Exception as err:
                        logging.error(f"[NightMode Loop Error for chat {chat_id}]: {err}")

            except Exception as e:
                logging.error(f"[NightMode Watcher Exception]: {e}")

            await asyncio.sleep(60)

    # 🚀 START BACKGROUND LOOP TASK SAFELY
    try:
        app.loop.create_task(night_watcher())
    except Exception:
        asyncio.create_task(night_watcher())
