def register_night_mode(app, db, LOG_CHANNEL):

    from pyrogram import filters
    from pyrogram.types import (
        Message,
        InlineKeyboardMarkup,
        InlineKeyboardButton,
        CallbackQuery
    )
    from pyrogram.enums import ChatMemberStatus
    from datetime import datetime
    import asyncio

    NIGHT_CACHE = {}

    # =========================
    # ADMIN CHECK
    # =========================
    async def is_admin(client, chat_id, user_id):
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        ]

    # =========================
    # DB FUNCTIONS
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
            return {"status": False, "start": "23:00", "end": "06:00"}

        NIGHT_CACHE[chat_id] = data
        return data

    # =========================
    # UI PANEL
    # =========================
    def night_keyboard(status):
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🟢 Enable" if not status else "🔴 Disable",
                    callback_data="night_toggle"
                )
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="night_close")
            ]
        ])

    # =========================
    # COMMAND PANEL
    # =========================
    @app.on_message(filters.command("nightmode") & filters.group)
    async def night_panel(client, message: Message):

        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply("❌ Only admins can use this!")

        data = await get_night(message.chat.id)

        await message.reply(
            f"🌙 **Night Mode Panel**\n\n"
            f"Status: {'ON' if data['status'] else 'OFF'}\n"
            f"Time: {data['start']} ➝ {data['end']}",
            reply_markup=night_keyboard(data["status"])
        )

    # =========================
    # BUTTON HANDLER
    # =========================
    @app.on_callback_query(filters.regex("^night_"))
    async def night_buttons(client, query: CallbackQuery):

        chat_id = query.message.chat.id
        user_id = query.from_user.id

        if not await is_admin(client, chat_id, user_id):
            return await query.answer("❌ Not admin!", show_alert=True)

        data = await get_night(chat_id)

        if query.data == "night_toggle":

            new_status = not data["status"]

            await set_night(chat_id, new_status, data["start"], data["end"])

            # LOG
            try:
                await app.send_message(
                    LOG_CHANNEL,
                    f"🌙 Night Mode {'Enabled' if new_status else 'Disabled'}\n"
                    f"Chat: {chat_id}\nBy: {query.from_user.mention}"
                )
            except:
                pass

            await query.message.edit_text(
                f"🌙 **Night Mode Panel**\n\n"
                f"Status: {'ON' if new_status else 'OFF'}\n"
                f"Time: {data['start']} ➝ {data['end']}",
                reply_markup=night_keyboard(new_status)
            )

        elif query.data == "night_close":
            await query.message.delete()

        await query.answer()

    # =========================
    # AUTO WATCHER
    # =========================
    async def night_watcher():

        while True:
            now = datetime.now().strftime("%H:%M")

            chats = await db.night.find({"status": True}).to_list(1000)

            for chat in chats:
                chat_id = chat["chat_id"]
                start = chat["start"]
                end = chat["end"]

                try:
                    # NIGHT START
                    if now == start:
                        await app.set_chat_permissions(chat_id, permissions={})

                        await app.send_message(chat_id, "🌙 Night Mode ON\n🔇 Chat muted!")

                        await app.send_message(
                            LOG_CHANNEL,
                            f"🌙 Night Mode Activated\nChat: {chat_id}"
                        )

                    # NIGHT END
                    if now == end:
                        await app.set_chat_permissions(
                            chat_id,
                            permissions={
                                "can_send_messages": True,
                                "can_send_media_messages": True,
                                "can_send_other_messages": True
                            }
                        )

                        await app.send_message(chat_id, "☀️ Good Morning!\n🔊 Chat unmuted!")

                        await app.send_message(
                            LOG_CHANNEL,
                            f"☀️ Night Mode Ended\nChat: {chat_id}"
                        )

                except Exception as e:
                    print(f"[NightMode Error] {e}")

            await asyncio.sleep(60)

    # START LOOP
    app.loop.create_task(night_watcher())
