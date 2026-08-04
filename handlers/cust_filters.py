# ============================================================
# 🏷️ CUSTOM FILTERS SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🏷️ ᴄᴜsᴛᴏᴍ ғɪʟᴛᴇʀs"

__help__ = """
*🏷️ ᴄᴜsᴛᴏᴍ ғɪʟᴛᴇʀs sʏsᴛᴇᴍ* — Set up automated custom triggers and text/media responses for your group chat!

• `/save <keyword> <reply>` — Save a custom filter (supports text, media, stickers)
• `/filter <keyword>` — Same as save
• `/filters` — List all active custom filters in the group
• `/stop <keyword>` — Delete a specific custom filter
• `/stopall` — Delete all custom filters in the group (Admin only)
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus
import logging

def register_cust_filters_system(app, db):

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
    # 💾 SAVE CUSTOM FILTER (`/save` or `/filter`)
    # ============================================================
    @app.on_message(filters.command(["save", "filter"]) & filters.group)
    async def save_filter_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can create custom filters!**")

        if len(message.command) < 2:
            return await message.reply(
                "⚠️ **Incorrect Usage!**\n"
                "• Reply to a message with `/save <keyword>` or use `/save <keyword> <reply text>`."
            )

        keyword = message.command[1].lower()
        chat_id = message.chat.id
        reply = message.reply_to_message

        # Determine reply content type
        content = {}
        if reply:
            if reply.text:
                content["type"] = "text"
                content["value"] = reply.text
            elif reply.caption:
                content["type"] = "caption"
                content["value"] = reply.caption
            
            if reply.photo:
                content["media_type"] = "photo"
                content["file_id"] = reply.photo.file_id
            elif reply.video:
                content["media_type"] = "video"
                content["file_id"] = reply.video.file_id
            elif reply.document:
                content["media_type"] = "document"
                content["file_id"] = reply.document.file_id
            elif reply.sticker:
                content["media_type"] = "sticker"
                content["file_id"] = reply.sticker.file_id
            elif reply.animation:
                content["media_type"] = "animation"
                content["file_id"] = reply.animation.file_id
            elif reply.audio:
                content["media_type"] = "audio"
                content["file_id"] = reply.audio.file_id
            elif reply.voice:
                content["media_type"] = "voice"
                content["file_id"] = reply.voice.file_id
        else:
            # Inline text argument check
            if len(message.command) < 3:
                return await message.reply("⚠️ **Please provide text to save or reply to a media message!**")
            
            text_val = " ".join(message.command[2:])
            content["type"] = "text"
            content["value"] = text_val

        try:
            await db.custom_filters.update_one(
                {"chat_id": chat_id, "keyword": keyword},
                {"$set": {"content": content}},
                upsert=True
            )
            await message.reply(f"✅ **Filter successfully saved for keyword:** `{keyword}` ✨")
        except Exception as e:
            logging.error(f"[Save Filter DB Error]: {e}")
            await message.reply("❌ **Failed to save custom filter due to a database error.**")

    # ============================================================
    # 📋 LIST ALL FILTERS (`/filters`)
    # ============================================================
    @app.on_message(filters.command("filters") & filters.group)
    async def list_filters_cmd(client, message: Message):
        chat_id = message.chat.id

        try:
            cursor = db.custom_filters.find({"chat_id": chat_id})
            filters_list = [doc["keyword"] async for doc in cursor]

            if not filters_list:
                return await message.reply("📭 **No custom filters saved in this group yet.**")

            formatted_filters = ", ".join([f"`{f}`" for f in filters_list])
            text = (
                f"🏷️ **Nomad Bot — Active Group Filters:**\n\n"
                f"{formatted_filters}\n\n"
                f"_Trigger any of these keywords to see their responses!_"
            )
            await message.reply_text(text)
        except Exception as e:
            logging.error(f"[List Filters Error]: {e}")
            await message.reply("❌ **Failed to retrieve custom filters list.**")

    # ============================================================
    # 🗑️ STOP/DELETE FILTER (`/stop` or `/delfilter`)
    # ============================================================
    @app.on_message(filters.command(["stop", "delfilter", "removefilter"]) & filters.group)
    async def stop_filter_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can delete custom filters!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please specify the keyword you want to stop/delete!** (e.g., `/stop hi`)")

        keyword = message.command[1].lower()
        chat_id = message.chat.id

        try:
            result = await db.custom_filters.delete_one({"chat_id": chat_id, "keyword": keyword})
            if result.deleted_count > 0:
                await message.reply(f"🗑️ **Successfully deleted filter for keyword:** `{keyword}`")
            else:
                await message.reply(f"⚠️ **No filter found for keyword:** `{keyword}`")
        except Exception as e:
            logging.error(f"[Stop Filter Error]: {e}")
            await message.reply("❌ **Failed to delete filter.**")

    # ============================================================
    # 💥 STOP ALL FILTERS (`/stopall`)
    # ============================================================
    @app.on_message(filters.command("stopall") & filters.group)
    async def stop_all_filters_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can clear all custom filters!**")

        chat_id = message.chat.id

        try:
            result = await db.custom_filters.delete_many({"chat_id": chat_id})
            await message.reply(f"🔥 **Cleared all custom filters! Total deleted:** `{result.deleted_count}`")
        except Exception as e:
            logging.error(f"[Stop All Filters Error]: {e}")
            await message.reply("❌ **Failed to clear custom filters.**")

    # ============================================================
    # ⚡ AUTOMATIC FILTER DISPATCHER (TEXT & MEDIA HANDLER)
    # ============================================================
    @app.on_message(filters.text & filters.group & ~filters.bot, group=10)
    async def filter_dispatcher(client, message: Message):
        if not message.text:
            return

        text_content = message.text.strip().lower()
        chat_id = message.chat.id

        # Check exact or word-boundary token matches
        try:
            words = text_content.split()
            if not words:
                return

            # Check individual keywords or complete text phrase
            filter_doc = await db.custom_filters.find_one({"chat_id": chat_id, "keyword": text_content})
            if not filter_doc:
                # Check first word match as well
                filter_doc = await db.custom_filters.find_one({"chat_id": chat_id, "keyword": words[0]})

            if not filter_doc:
                return

            content = filter_doc.get("content", {})
            c_type = content.get("type")
            m_type = content.get("media_type")
            val = content.get("value", "")
            file_id = content.get("file_id")

            # Dispatch media/text response
            if m_type == "photo":
                await message.reply_photo(photo=file_id, caption=val if val else None)
            elif m_type == "video":
                await message.reply_video(video=file_id, caption=val if val else None)
            elif m_type == "document":
                await message.reply_document(document=file_id, caption=val if val else None)
            elif m_type == "sticker":
                await message.reply_sticker(sticker=file_id)
            elif m_type == "animation":
                await message.reply_animation(animation=file_id, caption=val if val else None)
            elif m_type == "audio":
                await message.reply_audio(audio=file_id, caption=val if val else None)
            elif m_type == "voice":
                await message.reply_voice(voice=file_id, caption=val if val else None)
            elif c_type == "text" or val:
                await message.reply_text(val, disable_web_page_preview=True)

        except Exception as e:
            logging.error(f"[Filter Dispatcher Error]: {e}")
