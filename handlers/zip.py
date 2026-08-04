# ============================================================
# 📦 FILE ARCHIVE & ZIP UTILITY SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "📦 ᴢɪᴘ"

__help__ = """
*📦 ᴢɪᴘ & ᴀʀᴄʜɪᴠᴇ ᴛᴏᴏʟs* — Compress files, folders, or extract archives easily with bot commands!

• `/zip <reply to file>` — Compress a replied file or document into a `.zip` archive
• `/unzip <reply to zip>` — Extract a replied `.zip` archive into individual files
"""

from pyrogram import filters
from pyrogram.types import Message
import os
import zipfile
import shutil
import logging

def register_zip_system(app, OWNER_ID: int):

    # Temporary directory for handling archives
    DOWNLOAD_DIR = "downloads"
    EXTRACT_DIR = "extracted"

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    os.makedirs(EXTRACT_DIR, exist_ok=True)

    # ============================================================
    # 🗜️ COMPRESS FILE TO ZIP (`/zip`)
    # ============================================================
    @app.on_message(filters.command("zip"))
    async def zip_file_cmd(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("❌ **This command is restricted to the Bot Owner!**")

        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply("⚠️ **Please reply to a document/file you want to compress into a ZIP!**")

        status_msg = await message.reply("📦 **Downloading file for compression...**")
        
        try:
            # Download file
            file_path = await message.reply_to_message.download(file_name=DOWNLOAD_DIR + "/")
            base_name = os.path.basename(file_path)
            zip_filename = f"{os.path.splitext(base_name)[0]}.zip"
            zip_filepath = os.path.join(DOWNLOAD_DIR, zip_filename)

            await status_msg.edit_text("🗜️ **Compressing file into ZIP format...**")

            # Create ZIP archive
            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(file_path, arcname=base_name)

            await status_msg.edit_text("📤 **Uploading generated ZIP archive...**")
            
            # Send zip file
            await message.reply_document(
                document=zip_filepath,
                caption=f"📦 **Compressed Archive:** `{zip_filename}`"
            )

            # Cleanup files
            os.remove(file_path)
            os.remove(zip_filepath)
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Zip Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to create ZIP archive:** `{str(e)}`")

    # ============================================================
    # 📂 EXTRACT ZIP ARCHIVE (`/unzip`)
    # ============================================================
    @app.on_message(filters.command("unzip"))
    async def unzip_file_cmd(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("❌ **This command is restricted to the Bot Owner!**")

        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply("⚠️ **Please reply to a `.zip` archive file to extract!**")

        doc = message.reply_to_message.document
        if not doc.file_name.endswith(".zip"):
            return await message.reply("❌ **The replied file is not a valid `.zip` archive!**")

        status_msg = await message.reply("📥 **Downloading ZIP archive...**")

        try:
            # Download zip file
            zip_path = await message.reply_to_message.download(file_name=DOWNLOAD_DIR + "/")
            extract_path = os.path.join(EXTRACT_DIR, str(message.id))
            os.makedirs(extract_path, exist_ok=True)

            await status_msg.edit_text("📂 **Extracting archive contents...**")

            # Extract contents safely
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            extracted_files = os.listdir(extract_path)
            if not extracted_files:
                return await status_msg.edit_text("❌ **The ZIP archive is empty!**")

            await status_msg.edit_text(f"📤 **Uploading {len(extracted_files)} extracted files...**")

            # Send extracted files one by one (or as a batch report)
            for file_name in extracted_files[:10]: # Limit to 10 files to prevent flood
                file_full_path = os.path.join(extract_path, file_name)
                if os.path.isfile(file_full_path):
                    await message.reply_document(document=file_full_path)

            # Cleanup
            os.remove(zip_path)
            shutil.rmtree(extract_path, ignore_errors=True)
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Unzip Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to extract ZIP archive:** `{str(e)}`")
