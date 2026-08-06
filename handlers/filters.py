# ============================================================
# 🔍 FILTERS MODULE (ROSE STYLE)
# ============================================================

__mod_name__ = "🔍 ꜰɪʟᴛᴇʀꜱ"

__help__ = """
*🔍 ꜰɪʟᴛᴇʀꜱ ᴍᴏᴅᴜʟᴇ* — Make your chat more lively with filters; The bot will reply to certain words!

Filters are case insensitive; every time someone says your trigger words, the bot will reply something else! Can be used to create your own commands, if desired.

Commands:
• `/filter <trigger> <reply>` — Every time someone says "trigger", the bot will reply with "sentence". For multiple word filters, quote the trigger.
• `/filters` — List all chat filters.
• `/stop <trigger>` — Stop the bot from replying to "trigger".
• `/stopall` — Stop ALL filters in the current chat. This cannot be undone.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import db
import logging
import re

logger = logging.getLogger("FILTERS")

def register_filters_system(app):

    # ============================================================
    # 💬 TEXT MESSAGE INTERCEPTOR FOR FILTERS
    # ============================================================
    @app.on_message(filters.text & ~filters.private & ~filters.bot, group=2)
    async def trigger_filters(client, message: Message):
        chat_id = message.chat.id
        text = message.text.strip()

        try:
            # Fetch filters for this chat from DB
            chat_filters = await db.filters.find({"chat_id": chat_id}).to_list(length=None)
            if not chat_filters:
                return

            for f in chat_filters:
                keyword = f["trigger"]
                # Case-insensitive exact or word boundary matching
                pattern = r(^|\s){}(?=\s|$)(?i)
                # Simple lower case text match or regex match
                if keyword.lower() == text.lower() or re.search(rf"\b{re.escape(keyword)}\b", text, re.IGNORECASE):
                    reply_text = f.get("reply", "")
                    photo_id = f.get("photo_id")
                    buttons = f.get("buttons", [])

                    keyboard = None
                    if buttons:
                        keyboard = InlineKeyboardMarkup(
                            [
                                [InlineKeyboardButton(btn["text"], url=btn.get("url"), callback_data=btn.get("callback_data")) for btn in row]
                                for row in buttons
                            ]
                        )

                    if photo_id:
                        await message.reply_photo(photo=photo_id, caption=reply_text, reply_markup=keyboard)
                    else:
                        await message.reply(reply_text, reply_markup=keyboard, disable_web_page_preview=True)
                    break

        except Exception as e:
            logger.error(f"[Filter Trigger Error]: {e}")

    # ============================================================
    # ➕ ADD FILTER (`/filter <trigger> <reply>`)
    # ============================================================
    @app.on_message(filters.command("filter") & ~filters.private)
    async def add_filter_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to add filters!**")

        args = message.text.split(None, 2)
        if len(args) < 3 and not message.reply_to_message:
            return await message.reply(
                "⚠️ **Invalid syntax!** Use:\n"
                "`/filter <trigger> <reply>` or reply to a message/photo with `/filter <trigger>`"
            )

        chat_id = message.chat.id
        trigger = ""
        reply_text = ""
        photo_id = None
        reply_msg = message.reply_to_message

        # Handle quoted triggers e.g., /filter "hello world" hi there
        text_content = message.text
        if '"' in text_content or "'" in text_content:
            match = re.search(r'["\'](.+?)["\']\s*(.*)', text_content, re.DOTALL)
            if match:
                trigger = match.group(1).strip()
                reply_text = match.group(2).strip()

        if not trigger:
            if len(args) >= 2:
                trigger = args[1].strip()
                if len(args) >= 3:
                    reply_text = args[2].strip()

        # Handle replied message / media
        if reply_msg:
            if reply_msg.photo:
                photo_id = reply_msg.photo.file_id
            elif reply_msg.document and reply_msg.document.mime_type and "image" in reply_msg.document.mime_type:
                photo_id = reply_msg.document.file_id
            if not reply_text and reply_msg.caption:
                reply_text = reply_msg.caption
            elif not reply_text and reply_msg.text:
                reply_text = reply_msg.text

        if not trigger or (not reply_text and not photo_id):
            return await message.reply("⚠️ **Please provide both a trigger and a reply text/media for the filter!**")

        # Parse inline buttons if present in reply text (button:Text:URL syntax)
        buttons = []
        clean_lines = []
        for line in reply_text.split("\n"):
            if line.strip().startswith("button:"):
                parts = line.strip().split(":", 2)
                if len(parts) == 3:
                    buttons.append([{"text": parts[1].strip(), "url": parts[2].strip()}])
            else:
                clean_lines.append(line)

        final_reply_text = "\n".join(clean_lines).strip()

        try:
            # Upsert filter into DB
            await db.filters.update_one(
                {"chat_id": chat_id, "trigger": trigger.lower()},
                {
                    "$set": {
                        "trigger": trigger.lower(),
                        "raw_trigger": trigger,
                        "reply": final_reply_text,
                        "photo_id": photo_id,
                        "buttons": buttons
                    }
                },
                upsert=True
            )
            await message.reply(f"✅ **Saved filter:** `{trigger}`")
        except Exception as e:
            await message.reply(f"❌ **Failed to save filter:** `{str(e)}`")

    # ============================================================
    # 📋 LIST FILTERS (`/filters`)
    # ============================================================
    @app.on_message(filters.command("filters") & ~filters.private)
    async def list_filters_cmd(client, message: Message):
        chat_id = message.chat.id
        try:
            chat_filters = await db.filters.find({"chat_id": chat_id}).to_list(length=None)
            if not chat_filters:
                return await message.reply("ℹ️ **No filters are currently saved in this chat.**")

            filter_list = "\n".join([f"• `{f.get('raw_trigger', f['trigger'])}`" for f in chat_filters])
            await message.reply(f"🔍 **List of active filters in this chat:**\n\n{filter_list}")
        except Exception as e:
            await message.reply(f"❌ **Error fetching filters:** `{str(e)}`")

    # ============================================================
    # 🛑 STOP FILTER (`/stop <trigger>`)
    # ============================================================
    @app.on_message(filters.command("stop") & ~filters.private)
    async def stop_filter_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to stop filters!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please specify which filter you want to stop!** Example: `/stop hello`")

        trigger = message.text.split(None, 1)[1].strip().lower()
        chat_id = message.chat.id

        try:
            result = await db.filters.delete_one({"chat_id": chat_id, "trigger": trigger})
            if result.deleted_count > 0:
                await message.reply(f"✅ **Successfully stopped filter:** `{trigger}`")
            else:
                await message.reply(f"ℹ️ **No such filter found:** `{trigger}`")
        except Exception as e:
            await message.reply(f"❌ **Error deleting filter:** `{str(e)}`")

    # ============================================================
    # ⚠️ STOP ALL FILTERS (`/stopall`)
    # ============================================================
    @app.on_message(filters.command("stopall") & ~filters.private)
    async def stopall_filters_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to stop all filters!**")

        chat_id = message.chat.id
        try:
            result = await db.filters.delete_many({"chat_id": chat_id})
            if result.deleted_count > 0:
                await message.reply(f"✅ **Successfully deleted all `{result.deleted_count}` filters in this chat. This cannot be undone!**")
            else:
                await message.reply("ℹ️ **There are no filters saved in this chat to delete.**")
        except Exception as e:
            await message.reply(f"❌ **Error clearing filters:** `{str(e)}`")
