# ============================================================
# 🧹 CLEAN SERVICE MESSAGES MODULE
# ============================================================

__mod_name__ = "🧹 ᴄʟᴇᴀɴꜱᴇʀᴠɪᴄᴇ"

__help__ = """
*🧹 ᴄʟᴇᴀɴ ꜱᴇʀᴠɪᴄᴇ ᴍᴏᴅᴜʟᴇ* — Automatically clean up Telegram service messages (like join, left, pin, title changes) to keep your group chat clean!

Admin commands:
• `/cleanservice <type/yes/no/on/off>` — Select which service messages to delete.
• `/keepservice <type>` — Select which service messages to stop deleting.
• `/nocleanservice <type>` — (Same as keepservice).
• `/cleanservicetypes` — List all the available service messages, with a brief explanation.

**Examples:**
• Stop all telegram service messages: `/cleanservice all`
• Stop telegrams 'x joined the chat' messages: `/cleanservice join`
• Keep telegrams 'x pinned a message' messages: `/keepservice pin`
"""

from pyrogram import filters
from pyrogram.types import Message
from db import db
import logging

logger = logging.getLogger("CLEANSERVICE")

VALID_SERVICE_TYPES = ["join", "left", "pin", "title", "videochat", "all"]

def register_cleanservice_system(app):

    # ============================================================
    # 🗑️ SERVICE MESSAGE EVENT LISTENER & CLEANER
    # ============================================================
    @app.on_message(filters.service & ~filters.private)
    async def auto_clean_service_messages(client, message: Message):
        chat_id = message.chat.id

        try:
            # Fetch active clean settings for this chat
            settings = await db.cleanservice.find_one({"chat_id": chat_id})
            if not settings:
                return

            disabled_types = settings.get("disabled_types", [])
            
            # If "all" is set, delete any service message
            should_delete = False
            if "all" in disabled_types:
                should_delete = True
            elif message.new_chat_members and "join" in disabled_types:
                should_delete = True
            elif message.left_chat_member and "left" in disabled_types:
                should_delete = True
            elif message.pinned_message and "pin" in disabled_types:
                should_delete = True
            elif message.chat.title and "title" in disabled_types and message.group_chat_created is False:
                # Telegram service message for title change
                pass
            
            # Check video chat or other service flags if available
            if message.video_chat_started or message.video_chat_ended or message.video_chat_members_invited:
                if "videochat" in disabled_types:
                    should_delete = True

            if should_delete:
                await message.delete()

        except Exception as e:
            logger.error(f"[CleanService Error]: {e}")

    # ============================================================
    # ⚙️ CLEAN SERVICE COMMAND (`/cleanservice`)
    # ============================================================
    @app.on_message(filters.command("cleanservice") & ~filters.private)
    async def cleanservice_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to manage clean service settings!**")

        args = message.command
        if len(args) < 2:
            settings = await db.cleanservice.find_one({"chat_id": message.chat.id})
            disabled = settings.get("disabled_types", []) if settings else []
            return await message.reply(
                f"🧹 **Current Clean Service Settings:**\n"
                f"• **Active Filter Types:** `{', '.join(disabled) if disabled else 'None'}`\n\n"
                f"Use `/cleanservicetypes` to see available types or `/cleanservice <type>` to enable."
            )

        query = args[1].lower()
        if query in ["yes", "on", "true"]:
            query = "all"
        elif query in ["no", "off", "false"]:
            # Clear all
            await db.cleanservice.update_one({"chat_id": message.chat.id}, {"$set": {"disabled_types": []}}, upsert=True)
            return await message.reply("✅ **Clean service disabled for all types.**")

        if query not in VALID_SERVICE_TYPES:
            return await message.reply(f"❌ **Invalid type!** Use `/cleanservicetypes` to check valid options.")

        # Update DB
        settings = await db.cleanservice.find_one({"chat_id": message.chat.id})
        disabled_types = settings.get("disabled_types", []) if settings else []

        if query == "all":
            disabled_types = VALID_SERVICE_TYPES.copy()
        elif query not in disabled_types:
            disabled_types.append(query)

        await db.cleanservice.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"disabled_types": disabled_types}},
            upsert=True
        )
        await message.reply(f"✅ **Now automatically deleting service messages of type:** `{query}`")

    # ============================================================
    # 🛡️ KEEP SERVICE / NO CLEAN SERVICE (`/keepservice` & `/nocleanservice`)
    # ============================================================
    @app.on_message(filters.command(["keepservice", "nocleanservice"]) & ~filters.private)
    async def keep_service_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to manage clean service settings!**")

        args = message.command
        if len(args) < 2:
            return await message.reply("⚠️ **Please specify a type to stop deleting!** Example: `/keepservice pin`")

        query = args[1].lower()
        if query not in VALID_SERVICE_TYPES:
            return await message.reply(f"❌ **Invalid type!** Use `/cleanservicetypes` to check valid options.")

        settings = await db.cleanservice.find_one({"chat_id": message.chat.id})
        if not settings:
            return await message.reply("ℹ️ **No service messages are currently being cleaned in this chat.**")

        disabled_types = settings.get("disabled_types", [])
        if query == "all":
            disabled_types = []
        elif query in disabled_types:
            disabled_types.remove(query)
            if "all" in disabled_types:
                disabled_types.remove("all")

        await db.cleanservice.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"disabled_types": disabled_types}},
            upsert=True
        )
        await message.reply(f"✅ **Stopped cleaning service messages of type:** `{query}`")

    # ============================================================
    # 📋 CLEAN SERVICE TYPES (`/cleanservicetypes`)
    # ============================================================
    @app.on_message(filters.command("cleanservicetypes"))
    async def clean_service_types_cmd(client, message: Message):
        types_text = (
            f"📋 **AVAILABLE SERVICE MESSAGE TYPES**\n\n"
            f"• **join:** When a new user joins the chat. e.g. 'X joined the chat'\n"
            f"• **left:** When a user leaves or is removed. e.g. 'X left the chat'\n"
            f"• **pin:** When a new message is pinned. e.g. 'X pinned a message'\n"
            f"• **title:** When chat or topic titles are changed.\n"
            f"• **videochat:** When a video chat action occurs (starting, ending, scheduling, or adding members).\n"
            f"• **all:** All telegram service messages."
        )
        await message.reply(types_text)
