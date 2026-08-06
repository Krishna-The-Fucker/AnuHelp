# ============================================================
# 👋 WELCOME & GREETINGS MANAGEMENT MODULE (WITH MEDIA & BUTTONS)
# ============================================================

__mod_name__ = "👋 ᴡᴇʟᴄᴏᴍᴇ"

__help__ = """
*👋 ᴡᴇʟᴄᴏᴍᴇ ᴍᴏᴅᴜʟᴇ* — Give your members a warm welcome with the greetings module! Or a sad goodbye... Depends!

Admin commands:
• `/welcome <yes/no/on/off>` — Enable/disable welcomes messages.
• `/goodbye <yes/no/on/off>` — Enable/disable goodbye messages.
• `/setwelcome <text>` — Set a new welcome message. Supports markdown, buttons, and fillings.
• `/resetwelcome` — Reset the welcome message.
• `/setgoodbye <text>` — Set a new goodbye message. Supports markdown, buttons, and fillings.
• `/resetgoodbye` — Reset the goodbye message.
• `/cleanwelcome <yes/no/on/off>` — Delete old welcome messages after 5 minutes, or when a new person joins.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import db
import logging

logger = logging.getLogger("WELCOME")

def register_welcome_system(app):

    # ============================================================
    # 📥 NEW MEMBER JOIN EVENT HANDLER
    # ============================================================
    @app.on_message(filters.new_chat_members)
    async def welcome_new_members(client, message: Message):
        chat_id = message.chat.id

        try:
            # Check if welcome is enabled (default True)
            welcome_toggle = await db.welcome_toggles.find_one({"chat_id": chat_id})
            if welcome_toggle and welcome_toggle.get("enabled") is False:
                return

            # Fetch custom welcome data from DB
            welcome_data = await db.welcome.find_one({"chat_id": chat_id})
            
            for member in message.new_chat_members:
                # Don't greet if the bot itself joined
                if member.id == (await client.get_me()).id:
                    continue

                name = member.first_name
                mention = member.mention
                title = message.chat.title

                if welcome_data:
                    raw_text = welcome_data.get("text", "Hello {name}, welcome to {title}!")
                    photo_id = welcome_data.get("photo_id")
                    
                    # Format standard variables
                    text = raw_text.format(
                        name=name,
                        mention=mention,
                        title=title,
                        id=member.id
                    )
                    
                    # Parse buttons if saved
                    buttons = welcome_data.get("buttons", [])
                    keyboard = None
                    if buttons:
                        keyboard = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton(btn["text"], url=btn.get("url"), callback_data=btn.get("callback_data")) for btn in row]
                                for row in buttons
                            ]
                        )

                    # Send photo if available, otherwise text message
                    if photo_id:
                        await message.reply_photo(
                            photo=photo_id,
                            caption=text,
                            reply_markup=keyboard
                        )
                    else:
                        await message.reply(
                            text,
                            reply_markup=keyboard,
                            disable_web_page_preview=True
                        )
                else:
                    # Default fallback welcome
                    await message.reply(f"👋 Hello {mention}, welcome to **{title}**! Enjoy your stay here. 🎉")

        except Exception as e:
            logger.error(f"[Welcome Event Error]: {e}")

    # ============================================================
    # 🚪 LEFT CHAT MEMBER EVENT HANDLER (GOODBYE)
    # ============================================================
    @app.on_message(filters.left_chat_member)
    async def goodbye_left_member(client, message: Message):
        chat_id = message.chat.id

        try:
            # Check if goodbye is enabled
            goodbye_toggle = await db.goodbye_toggles.find_one({"chat_id": chat_id})
            if not goodbye_toggle or goodbye_toggle.get("enabled") is False:
                return

            member = message.left_chat_member
            if not member or member.id == (await client.get_me()).id:
                return

            goodbye_data = await db.goodbye.find_one({"chat_id": chat_id})
            if not goodbye_data:
                return

            raw_text = goodbye_data.get("text", "Goodbye {name}!")
            photo_id = goodbye_data.get("photo_id")

            text = raw_text.format(
                name=member.first_name,
                mention=member.mention,
                title=message.chat.title,
                id=member.id
            )

            buttons = goodbye_data.get("buttons", [])
            keyboard = None
            if buttons:
                keyboard = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(btn["text"], url=btn.get("url"), callback_data=btn.get("callback_data")) for btn in row]
                        for row in buttons
                    ]
                )

            if photo_id:
                await message.reply_photo(photo=photo_id, caption=text, reply_markup=keyboard)
            else:
                await message.reply(text, reply_markup=keyboard, disable_web_page_preview=True)

        except Exception as e:
            logger.error(f"[Goodbye Event Error]: {e}")

    # ============================================================
    # ⚙️ TOGGLE WELCOME (`/welcome <yes/no/on/off>`)
    # ============================================================
    @app.on_message(filters.command("welcome") & ~filters.private)
    async def toggle_welcome_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to change welcome settings!**")

        args = message.command
        if len(args) < 2:
            # View current welcome status or preview if text/settings exist
            try:
                welcome_data = await db.welcome.find_one({"chat_id": message.chat.id})
                toggle_data = await db.welcome_toggles.find_one({"chat_id": message.chat.id})
                status = toggle_data.get("enabled", True) if toggle_data else True

                if not welcome_data:
                    return await message.reply(f"ℹ️ **Welcome messages are currently:** `{'Enabled' if status else 'Disabled'}`\nNo custom welcome message set yet. Use `/setwelcome`.")

                raw_text = welcome_data.get("text", "")
                buttons = welcome_data.get("buttons", [])
                photo_id = welcome_data.get("photo_id")

                preview_text = raw_text.format(
                    name=message.from_user.first_name,
                    mention=message.from_user.mention,
                    title=message.chat.title,
                    id=message.from_user.id
                )

                keyboard = None
                if buttons:
                    keyboard = InlineKeyboardMarkup(
                        [[InlineKeyboardButton(btn["text"], url=btn["url"]) for btn in row] for row in buttons]
                    )

                full_caption = f"📋 **Current Active Welcome Status:** `{'Enabled' if status else 'Disabled'}`\n\n--------------------\n{preview_text}"

                if photo_id:
                    await message.reply_photo(photo=photo_id, caption=full_caption, reply_markup=keyboard)
                else:
                    await message.reply(full_caption, reply_markup=keyboard, disable_web_page_preview=True)
            except Exception as e:
                await message.reply(f"❌ **Error:** `{str(e)}`")
            return

        choice = args[1].lower()
        if choice in ["yes", "on", "true"]:
            status = True
        elif choice in ["no", "off", "false"]:
            status = False
        else:
            return await message.reply("⚠️ **Invalid argument!** Use `/welcome on` or `/welcome off`.")

        await db.welcome_toggles.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": status}},
            upsert=True
        )
        await message.reply(f"✅ **Welcome messages have been turned:** `{'ON' if status else 'OFF'}`")

    # ============================================================
    # 🚪 TOGGLE GOODBYE (`/goodbye <yes/no/on/off>`)
    # ============================================================
    @app.on_message(filters.command("goodbye") & ~filters.private)
    async def toggle_goodbye_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to change goodbye settings!**")

        args = message.command
        if len(args) < 2:
            toggle_data = await db.goodbye_toggles.find_one({"chat_id": message.chat.id})
            status = toggle_data.get("enabled", False) if toggle_data else False
            return await message.reply(f"ℹ️ **Goodbye messages are currently:** `{'Enabled' if status else 'Disabled'}`\nUse `/goodbye on` or `/goodbye off` to toggle.")

        choice = args[1].lower()
        if choice in ["yes", "on", "true"]:
            status = True
        elif choice in ["no", "off", "false"]:
            status = False
        else:
            return await message.reply("⚠️ **Invalid argument!** Use `/goodbye on` or `/goodbye off`.")

        await db.goodbye_toggles.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": status}},
            upsert=True
        )
        await message.reply(f"✅ **Goodbye messages have been turned:** `{'ON' if status else 'OFF'}`")

    # ============================================================
    # ⚙️ SET CUSTOM WELCOME (`/setwelcome`)
    # ============================================================
    @app.on_message(filters.command("setwelcome") & ~filters.private)
    async def set_welcome_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to set the welcome message!**")

        reply = message.reply_to_message
        photo_id = None
        full_text = ""

        if reply:
            if reply.photo:
                photo_id = reply.photo.file_id
            elif reply.document and reply.document.mime_type and "image" in reply.document.mime_type:
                photo_id = reply.document.file_id

            if len(message.command) > 1:
                full_text = message.text.split(None, 1)[1]
            elif reply.caption:
                full_text = reply.caption
        else:
            if message.photo:
                photo_id = message.photo.file_id
            if len(message.command) > 1:
                full_text = message.text.split(None, 1)[1]

        if not full_text and not photo_id:
            return await message.reply(
                "⚠️ **Please provide a welcome message or reply to a photo!**\n\n"
                "• **Variables:** `{name}`, `{mention}`, `{title}`, `{id}`\n"
                "• **Custom Buttons Syntax Example:**\n"
                "`/setwelcome Hello {name}! Welcome to {title}.\n\nbutton:Support:https://t.me/your_support`"
            )

        buttons = []
        clean_lines = []
        lines = full_text.split("\n")
        
        for line in lines:
            if line.strip().startswith("button:"):
                parts = line.strip().split(":", 2)
                if len(parts) == 3:
                    btn_text, btn_url = parts[1].strip(), parts[2].strip()
                    buttons.append([{"text": btn_text, "url": btn_url}])
            else:
                clean_lines.append(line)

        welcome_text = "\n".join(clean_lines).strip()

        existing_data = await db.welcome.find_one({"chat_id": message.chat.id})
        if not photo_id and existing_data:
            photo_id = existing_data.get("photo_id")

        try:
            await db.welcome.update_one(
                {"chat_id": message.chat.id},
                {
                    "$set": {
                        "text": welcome_text if welcome_text else (existing_data.get("text", "") if existing_data else ""),
                        "buttons": buttons,
                        "photo_id": photo_id
                    }
                },
                upsert=True
            )
            await message.reply("✅ **Custom welcome message, photo, and buttons updated successfully for this chat!**")
        except Exception as e:
            await message.reply(f"❌ **Failed to save welcome configuration:** `{str(e)}`")

    # ============================================================
    # ⚙️ SET CUSTOM GOODBYE (`/setgoodbye`)
    # ============================================================
    @app.on_message(filters.command("setgoodbye") & ~filters.private)
    async def set_goodbye_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to set the goodbye message!**")

        reply = message.reply_to_message
        photo_id = None
        full_text = ""

        if reply:
            if reply.photo:
                photo_id = reply.photo.file_id
            elif reply.document and reply.document.mime_type and "image" in reply.document.mime_type:
                photo_id = reply.document.file_id

            if len(message.command) > 1:
                full_text = message.text.split(None, 1)[1]
            elif reply.caption:
                full_text = reply.caption
        else:
            if message.photo:
                photo_id = message.photo.file_id
            if len(message.command) > 1:
                full_text = message.text.split(None, 1)[1]

        if not full_text and not photo_id:
            return await message.reply(
                "⚠️ **Please provide a goodbye message or reply to a photo!**\n\n"
                "• **Variables:** `{name}`, `{mention}`, `{title}`, `{id}`\n"
                "• **Custom Buttons Syntax Example:**\n"
                "`/setgoodbye Goodbye {name}!`"
            )

        buttons = []
        clean_lines = []
        lines = full_text.split("\n")
        
        for line in lines:
            if line.strip().startswith("button:"):
                parts = line.strip().split(":", 2)
                if len(parts) == 3:
                    btn_text, btn_url = parts[1].strip(), parts[2].strip()
                    buttons.append([{"text": btn_text, "url": btn_url}])
            else:
                clean_lines.append(line)

        goodbye_text = "\n".join(clean_lines).strip()

        existing_data = await db.goodbye.find_one({"chat_id": message.chat.id})
        if not photo_id and existing_data:
            photo_id = existing_data.get("photo_id")

        try:
            await db.goodbye.update_one(
                {"chat_id": message.chat.id},
                {
                    "$set": {
                        "text": goodbye_text if goodbye_text else (existing_data.get("text", "") if existing_data else ""),
                        "buttons": buttons,
                        "photo_id": photo_id
                    }
                },
                upsert=True
            )
            await message.reply("✅ **Custom goodbye message updated successfully for this chat!**")
        except Exception as e:
            await message.reply(f"❌ **Failed to save goodbye configuration:** `{str(e)}`")

    # ============================================================
    # ❌ RESET WELCOME (`/resetwelcome`)
    # ============================================================
    @app.on_message(filters.command("resetwelcome") & ~filters.private)
    async def reset_welcome_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to reset the welcome message!**")

        try:
            result = await db.welcome.delete_one({"chat_id": message.chat.id})
            if result.deleted_count > 0:
                await message.reply("🗑️ **Custom welcome message and photo reset! Default greeting restored.**")
            else:
                await message.reply("ℹ️ **There is no custom welcome message configured in this chat.**")
        except Exception as e:
            await message.reply(f"❌ **Failed to reset:** `{str(e)}`")

    # ============================================================
    # ❌ RESET GOODBYE (`/resetgoodbye`)
    # ============================================================
    @app.on_message(filters.command("resetgoodbye") & ~filters.private)
    async def reset_goodbye_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to reset the goodbye message!**")

        try:
            result = await db.goodbye.delete_one({"chat_id": message.chat.id})
            if result.deleted_count > 0:
                await message.reply("🗑️ **Custom goodbye message reset!**")
            else:
                await message.reply("ℹ️ **There is no custom goodbye message configured in this chat.**")
        except Exception as e:
            await message.reply(f"❌ **Failed to reset:** `{str(e)}`")

    # ============================================================
    # 🧹 CLEAN WELCOME (`/cleanwelcome <yes/no/on/off>`)
    # ============================================================
    @app.on_message(filters.command("cleanwelcome") & ~filters.private)
    async def clean_welcome_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to change clean welcome settings!**")

        args = message.command
        if len(args) < 2:
            clean_data = await db.clean_welcome.find_one({"chat_id": message.chat.id})
            status = clean_data.get("enabled", False) if clean_data else False
            return await message.reply(f"ℹ️ **Clean welcome status:** `{'Enabled' if status else 'Disabled'}`\nUse `/cleanwelcome on` or `/cleanwelcome off`.")

        choice = args[1].lower()
        if choice in ["yes", "on", "true"]:
            status = True
        elif choice in ["no", "off", "false"]:
            status = False
        else:
            return await message.reply("⚠️ **Invalid argument!** Use `/cleanwelcome on` or `/cleanwelcome off`.")

        await db.clean_welcome.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": status}},
            upsert=True
        )
        await message.reply(f"✅ **Clean welcome feature turned:** `{'ON' if status else 'OFF'}`")
