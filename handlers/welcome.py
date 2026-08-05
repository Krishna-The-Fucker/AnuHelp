# ============================================================
# 👋 WELCOME & GREETINGS MANAGEMENT MODULE (WITH MEDIA & BUTTONS)
# ============================================================

__mod_name__ = "👋 ᴡᴇʟᴄᴏᴍᴇ"

__help__ = """
*👋 ᴡᴇʟᴄᴏᴍᴇ ᴍᴏᴅᴜʟᴇ* — Customize and manage greeting messages and welcome photos for new members joining your group, complete with custom inline buttons!

• `/setwelcome [text]` — Reply to a photo or text with this command to set a custom welcome message and optional inline buttons.
• `/welcome` — View the currently active welcome message and preview its settings.
• `/delwelcome` — Delete/Reset the custom welcome message and photo.
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
    # ⚙️ SET CUSTOM WELCOME (`/setwelcome`)
    # ============================================================
    @app.on_message(filters.command("setwelcome") & ~filters.private)
    async def set_welcome_cmd(client, message: Message):
        # Check if user is admin/creator in the chat
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to set the welcome message!**")

        # Check if the command is a reply to a photo or has text provided
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
                "`/setwelcome Hello {name}! Welcome to {title}.\n\nbutton:Support:https://t.me/your_support`\n\n"
                "*(You can also send/reply with a photo along with this command!)*"
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

        # If existing data has a photo and user didn't provide a new one via command/reply, retain the old one unless explicitly wanted otherwise
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
    # 👀 VIEW CURRENT WELCOME (`/welcome`)
    # ============================================================
    @app.on_message(filters.command("welcome") & ~filters.private)
    async def view_welcome_cmd(client, message: Message):
        try:
            welcome_data = await db.welcome.find_one({"chat_id": message.chat.id})
            if not welcome_data:
                return await message.reply("ℹ️ **No custom welcome message is set for this group yet.** Use `/setwelcome` to create one.")

            raw_text = welcome_data.get("text", "")
            buttons = welcome_data.get("buttons", [])
            photo_id = welcome_data.get("photo_id")

            # Preview substitution using requester's info
            preview_text = raw_text.format(
                name=message.from_user.first_name,
                mention=message.from_user.mention,
                title=message.chat.title,
                id=message.from_user.id
            )

            keyboard = None
            if buttons:
                keyboard = InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(btn["text"], url=btn["url"]) for btn in row]
                        for row in buttons
                    ]
                )

            full_caption = f"📋 **Current Active Welcome Message Preview:**\n\n--------------------\n{preview_text}"

            if photo_id:
                await message.reply_photo(
                    photo=photo_id,
                    caption=full_caption,
                    reply_markup=keyboard
                )
            else:
                await message.reply(
                    full_caption,
                    reply_markup=keyboard,
                    disable_web_page_preview=True
                )
        except Exception as e:
            await message.reply(f"❌ **Failed to fetch welcome message:** `{str(e)}`")

    # ============================================================
    # ❌ DELETE WELCOME (`/delwelcome`)
    # ============================================================
    @app.on_message(filters.command("delwelcome") & ~filters.private)
    async def delete_welcome_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to delete the welcome message!**")

        try:
            result = await db.welcome.delete_one({"chat_id": message.chat.id})
            if result.deleted_count > 0:
                await message.reply("🗑️ **Custom welcome message and photo deleted! Default text greeting restored.**")
            else:
                await message.reply("ℹ️ **There is no custom welcome message configured in this chat.**")
        except Exception as e:
            await message.reply(f"❌ **Failed to delete:** `{str(e)}`")
