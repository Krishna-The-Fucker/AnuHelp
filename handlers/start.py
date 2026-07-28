# ============================================================
# 🤖 Nomad Group Manager Bot - Start Handler FINAL
# ============================================================

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto
)

from config import (
    BOT_USERNAME,
    SUPPORT_GROUP,
    UPDATE_CHANNEL,
    START_IMAGE,
    OWNER_ID,
    LOG_CHANNEL
)

import db
import asyncio


# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_handlers(app: Client):


    # ========================================================
    # LOG SYSTEM
    # ========================================================

    async def send_log(client, text):
        try:
            await client.send_message(
                LOG_CHANNEL,
                text
            )
        except:
            pass



    # ========================================================
    # START MENU
    # ========================================================

    async def start_menu(message, name):

        text = f"""
Hello {name} 👋

I am Nomad 🤖

Features:
• Anti Spam
• Locks System
• Admin Tools
• Warning System
• Security System
"""


        buttons = InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "Add Me",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                )
            ],

            [
                InlineKeyboardButton(
                    "Support",
                    url=SUPPORT_GROUP
                ),
                InlineKeyboardButton(
                    "Updates",
                    url=UPDATE_CHANNEL
                )
            ],

            [
                InlineKeyboardButton(
                    "Owner",
                    url=f"tg://user?id={OWNER_ID}"
                )
            ],

            [
                InlineKeyboardButton(
                    "Help",
                    callback_data="help"
                )
            ]

        ])


        try:

            if message.text:

                await message.reply_photo(
                    START_IMAGE,
                    caption=text,
                    reply_markup=buttons
                )

            else:

                await message.edit_media(
                    InputMediaPhoto(
                        START_IMAGE,
                        caption=text
                    ),
                    reply_markup=buttons
                )

        except:

            await message.reply_text(
                text,
                reply_markup=buttons
            )



    # ========================================================
    # START COMMAND
    # ========================================================

    @app.on_message(
        filters.private &
        filters.command("start")
    )

    async def start_command(client, message):

        user = message.from_user

        await db.add_user(
            user.id,
            user.first_name
        )


        await start_menu(
            message,
            user.first_name
        )


        await send_log(
            client,
            f"New user started bot\nID: {user.id}"
        )



    # ========================================================
    # HELP MENU
    # ========================================================

    async def help_menu(message):

        buttons = InlineKeyboardMarkup([

            [
                InlineKeyboardButton(
                    "Welcome",
                    callback_data="welcome_help"
                ),

                InlineKeyboardButton(
                    "Locks",
                    callback_data="locks_help"
                )
            ],

            [
                InlineKeyboardButton(
                    "Moderation",
                    callback_data="mod_help"
                )
            ],

            [
                InlineKeyboardButton(
                    "Back",
                    callback_data="back_start"
                )
            ]

        ])


        await message.edit_media(
            InputMediaPhoto(
                START_IMAGE,
                caption="Help Menu\n\nChoose category"
            ),
            reply_markup=buttons
        )



    # ========================================================
    # CALLBACK SYSTEM
    # ========================================================

    @app.on_callback_query()

    async def callback_handler(client, query):

        data = query.data


        if data == "help":

            await help_menu(
                query.message
            )


        elif data == "back_start":

            await start_menu(
                query.message,
                query.from_user.first_name
            )


        elif data == "welcome_help":

            await query.message.edit_media(
                InputMediaPhoto(
                    START_IMAGE,
                    caption="""
Welcome System

/welcome on
/welcome off

/setwelcome text
"""
                )
            )


        elif data == "locks_help":

            await query.message.edit_media(
                InputMediaPhoto(
                    START_IMAGE,
                    caption="""
Locks System

/lock type
/unlock type

Types:
url
media
sticker
username
"""
                )
            )


        elif data == "mod_help":

            await query.message.edit_media(
                InputMediaPhoto(
                    START_IMAGE,
                    caption="""
Moderation

/ban
/unban
/mute
/unmute
/warn
/promote
/demote
"""
                )
            )


        await query.answer()



    # ========================================================
    # BROADCAST SYSTEM
    # ========================================================

    @app.on_message(
        filters.private &
        filters.command("broadcast")
    )

    async def broadcast(client, message):

        if message.from_user.id != OWNER_ID:
            return await message.reply_text(
                "Only owner can use this."
            )


        if not message.reply_to_message:
            return await message.reply_text(
                "Reply to a message."
            )


        users = await db.get_all_users()


        sent = 0
        failed = 0


        status = await message.reply_text(
            "Broadcast started..."
        )


        for user_id in users:

            try:

                await message.reply_to_message.copy(
                    user_id
                )

                sent += 1


            except:

                failed += 1


            await asyncio.sleep(0.05)



        await status.edit_text(
            f"""
Broadcast Complete

Total: {len(users)}

Sent: {sent}

Failed: {failed}
"""
        )


        await send_log(
            client,
            f"""
Broadcast Done

Owner:
{message.from_user.id}

Sent:
{sent}

Failed:
{failed}
"""
        )



    # ========================================================
    # STATS
    # ========================================================

    @app.on_message(
        filters.private &
        filters.command("stats")
    )

    async def stats(client, message):

        if message.from_user.id != OWNER_ID:
            return


        users = await db.get_all_users()


        await message.reply_text(
            f"""
Bot Stats

Users:
{len(users)}

Status:
Running
"""
        )
