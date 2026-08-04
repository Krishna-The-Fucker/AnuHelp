# ============================================================
# 📝 NOTES & SAVED CONTENT SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "📝 ɴᴏᴛᴇs"

__help__ = """
*📝 ɴᴏᴛᴇs sʏsᴛᴇᴍ* — Save text, media, documents, or buttons as notes in your group and retrieve them instantly anytime with keywords!

• `/save <keyword>` — Reply to a message to save it as a note
• `#<keyword>` or `/get <keyword>` — Retrieve and send the saved note
• `/notes` — View all saved notes in the group
• `/delete <keyword>` — Delete a specific note
• `/clearallnotes` — Delete all notes in the group
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ParseMode
import logging

def register_notes_system(app, db):

    # ============================================================
    # 👑 ADMIN CHECK HELPER
    # ============================================================
    async def is_admin(client, message: Message):
        if not message.from_user:
            return False
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except Exception:
            return False

    # ============================================================
    # 💾 SAVE NOTE COMMAND (`/save`)
    # ============================================================
    @app.on_message(filters.command("save") & filters.group)
    async def save_note_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can save notes!**")

        if len(message.command) < 2:
            return await message.reply(
                "⚠️ **Incorrect Usage!**\n"
                "• Reply to any message (text, photo, video, document) with `/save <keyword>`"
            )

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to the message you want to save as a note!**")

        keyword = message.command[1].lower().strip()
        chat_id = message.chat.id
        replied = message.reply_to_message

        # Serialize message content for database storage
        note_data = {
            "chat_id": chat_id,
            "keyword": keyword,
            "text": replied.text or replied.caption or "",
            "media_type": None,
            "file_id": None
        }

        if replied.photo:
            note_data["media_type"] = "photo"
            note_data["file_id"] = replied.photo.file_id
        elif replied.video:
            note_data["media_type"] = "video"
            note_data["file_id"] = replied.video.file_id
        elif replied.document:
            note_data["media_type"] = "document"
            note_data["file_id"] = replied.document.file_id
        elif replied.audio:
            note_data["media_type"] = "audio"
            note_data["file_id"] = replied.audio.file_id
        elif replied.animation:
            note_data["media_type"] = "animation"
            note_data["file_id"] = replied.animation.file_id
        elif replied.sticker:
            note_data["media_type"] = "sticker"
            note_data["file_id"] = replied.sticker.file_id

        try:
            await db.notes.update_one(
                {"chat_id": chat_id, "keyword": keyword},
                {"$set": note_data},
                upsert=True
            )
            await message.reply(f"✅ **Note saved successfully!**\n• **Keyword:** `#{keyword}`")
        except Exception as e:
            logging.error(f"[Notes Save Error]: {e}")
            await message.reply("❌ **Failed to save note to database.**")

    # ============================================================
    # 🔍 GET NOTE COMMAND (`/get` or `#keyword`)
    # ============================================================
    @app.on_message((filters.command("get") | filters.regex(r"^#(.+)")) & filters.group, group=6)
    async def get_note_cmd(client, message: Message):
        chat_id = message.chat.id
        
        if message.command:
            if len(message.command) < 2:
                return
            keyword = message.command[1].lower().strip()
        else:
            # Regex match for #keyword
            match = message.matches[0]
            keyword = match.group(1).lower().strip()

        try:
            note = await db.notes.find_one({"chat_id": chat_id, "keyword": keyword})
            if not note:
                return

            text = note.get("text", "")
            media_type = note.get("media_type")
            file_id = note.get("file_id")

            if media_type == "photo":
                await message.reply_photo(photo=file_id, caption=text)
            elif media_type == "video":
                await message.reply_video(video=file_id, caption=text)
            elif media_type == "document":
                await message.reply_document(document=file_id, caption=text)
            elif media_type == "audio":
                await message.reply_audio(audio=file_id, caption=text)
            elif media_type == "animation":
                await message.reply_animation(animation=file_id, caption=text)
            elif media_type == "sticker":
                await message.reply_sticker(sticker=file_id)
            elif text:
                await message.reply_text(text, disable_web_page_preview=True)

        except Exception as e:
            logging.error(f"[Notes Get Error]: {e}")

    # ============================================================
    # 📋 LIST ALL NOTES (`/notes`)
    # ============================================================
    @app.on_message(filters.command("notes") & filters.group)
    async def list_notes_cmd(client, message: Message):
        chat_id = message.chat.id

        try:
            cursor = db.notes.find({"chat_id": chat_id})
            notes = [doc async for doc in cursor]

            if not notes:
                return await message.reply("📭 **No notes saved in this group yet.**")

            text = "📝 **Saved Group Notes:**\n\n"
            for i, note in enumerate(notes, start=1):
                text += f"{i}. `#{note['keyword']}`\n"

            text += "\n_Type `#keyword` or `/get keyword` to retrieve any note._"
            await message.reply_text(text)

        except Exception as e:
            logging.error(f"[Notes List Error]: {e}")
            await message.reply("❌ **Failed to fetch notes list.**")

    # ============================================================
    # 🗑️ DELETE NOTE COMMAND (`/delete`)
    # ============================================================
    @app.on_message(filters.command("delete") & filters.group)
    async def delete_note_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can delete notes!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Usage:** `/delete <keyword>`")

        keyword = message.command[1].lower().strip()
        chat_id = message.chat.id

        try:
            result = await db.notes.delete_one({"chat_id": chat_id, "keyword": keyword})
            if result.deleted_count > 0:
                await message.reply(f"🗑️ **Note `#{keyword}` successfully deleted!**")
            else:
                await message.reply(f"⚠️ **Note `#{keyword}` not found.**")
        except Exception as e:
            logging.error(f"[Notes Delete Error]: {e}")
            await message.reply("❌ **Failed to delete note.**")

    # ============================================================
    # 🧹 CLEAR ALL NOTES COMMAND (`/clearallnotes`)
    # ============================================================
    @app.on_message(filters.command("clearallnotes") & filters.group)
    async def clear_all_notes_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can clear all notes!**")

        chat_id = message.chat.id
        try:
            await db.notes.delete_many({"chat_id": chat_id})
            await message.reply("🧹 **All saved notes for this group have been completely cleared!** ✨")
        except Exception as e:
            logging.error(f"[Notes Clear All Error]: {e}")
            await message.reply("❌ **Failed to clear notes database.**")
