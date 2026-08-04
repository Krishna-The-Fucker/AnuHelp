# ============================================================
# 🗄️ BACKUP & RESTORE SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🗄️ ʙᴀᴄᴋᴜᴘs"

__help__ = """
*🗄️ ʙᴀᴄᴋᴜᴘ & ʀᴇsᴛᴏʀᴇ sʏsᴛᴇᴍ* — Easily export and import your group's settings, notes, and custom filters to move them across chats!

• `/export` or `/backup` — Export group settings, filters, and notes as a JSON file.
• `/import` — Reply to a valid Nomad backup JSON file to restore settings.
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging
import json
import io

def register_backups_system(app, db):

    # ============================================================
    # 👑 OWNER/CREATOR CHECK HELPER (Strict for Backups)
    # ============================================================
    async def is_chat_creator(client, message: Message):
        if not message.from_user:
            return False
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            # Only allow group creators to mess with backups to prevent rogue admins from overwriting
            return member.status == ChatMemberStatus.OWNER
        except Exception:
            return False

    # ============================================================
    # 📤 EXPORT / BACKUP COMMAND (`/export`, `/backup`)
    # ============================================================
    @app.on_message(filters.command(["export", "backup"]) & filters.group)
    async def export_backup_cmd(client, message: Message):
        if not await is_chat_creator(client, message):
            return await message.reply("❌ **Only the Group Creator (Owner) can export group data!**")

        chat_id = message.chat.id
        status_msg = await message.reply("⏳ **Gathering group data for export...**")

        try:
            backup_data = {
                "chat_id": chat_id,
                "filters": [],
                "notes": []
            }

            # 1. Fetch Filters
            async for f in db.custom_filters.find({"chat_id": chat_id}):
                backup_data["filters"].append({
                    "keyword": f.get("keyword"),
                    "content": f.get("content")
                })

            # 2. Fetch Notes (Assuming standard notes collection exists)
            async for n in db.notes.find({"chat_id": chat_id}):
                backup_data["notes"].append({
                    "name": n.get("name"),
                    "content": n.get("content")
                })

            # Check if there is anything to backup
            if not backup_data["filters"] and not backup_data["notes"]:
                return await status_msg.edit_text("📭 **There are no filters or notes to backup in this group!**")

            # Convert to JSON and save to in-memory bytes buffer
            json_data = json.dumps(backup_data, indent=4)
            file_buffer = io.BytesIO(json_data.encode("utf-8"))
            file_buffer.name = f"Nomad_Backup_{chat_id}.json"

            caption = (
                f"🗄️ **Nomad Bot — Group Backup Exported!**\n\n"
                f"🏷️ **Filters:** `{len(backup_data['filters'])}`\n"
                f"📝 **Notes:** `{len(backup_data['notes'])}`\n\n"
                f"_Reply to this file with `/import` in another group to restore these settings!_"
            )

            await message.reply_document(
                document=file_buffer,
                caption=caption
            )
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Backup Export Error]: {e}")
            await status_msg.edit_text("❌ **An error occurred while exporting the backup.**")

    # ============================================================
    # 📥 IMPORT / RESTORE COMMAND (`/import`)
    # ============================================================
    @app.on_message(filters.command("import") & filters.group)
    async def import_backup_cmd(client, message: Message):
        if not await is_chat_creator(client, message):
            return await message.reply("❌ **Only the Group Creator (Owner) can import group data!**")

        reply = message.reply_to_message
        if not reply or not reply.document:
            return await message.reply("⚠️ **Please reply to a valid Nomad Backup JSON document to import!**")

        if not reply.document.file_name.endswith(".json"):
            return await message.reply("❌ **Invalid file format! Expected a `.json` backup file.**")

        status_msg = await message.reply("⏳ **Downloading and processing backup file...**")

        try:
            # Download file to memory
            file_bytes = await client.download_media(message=reply, in_memory=True)
            file_data = file_bytes.getvalue().decode("utf-8")
            
            try:
                parsed_data = json.loads(file_data)
            except json.JSONDecodeError:
                return await status_msg.edit_text("❌ **Corrupted JSON file! Cannot read backup data.**")

            chat_id = message.chat.id
            imported_filters = 0
            imported_notes = 0

            # 1. Restore Filters
            if "filters" in parsed_data and isinstance(parsed_data["filters"], list):
                for f in parsed_data["filters"]:
                    if "keyword" in f and "content" in f:
                        await db.custom_filters.update_one(
                            {"chat_id": chat_id, "keyword": f["keyword"]},
                            {"$set": {"content": f["content"]}},
                            upsert=True
                        )
                        imported_filters += 1

            # 2. Restore Notes
            if "notes" in parsed_data and isinstance(parsed_data["notes"], list):
                for n in parsed_data["notes"]:
                    if "name" in n and "content" in n:
                        await db.notes.update_one(
                            {"chat_id": chat_id, "name": n["name"]},
                            {"$set": {"content": n["content"]}},
                            upsert=True
                        )
                        imported_notes += 1

            await status_msg.edit_text(
                f"✅ **Backup Successfully Restored!** ✨\n\n"
                f"📥 **Imported Filters:** `{imported_filters}`\n"
                f"📥 **Imported Notes:** `{imported_notes}`"
            )

        except Exception as e:
            logging.error(f"[Backup Import Error]: {e}")
            await status_msg.edit_text("❌ **An error occurred while importing the backup.**")
