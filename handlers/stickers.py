# ============================================================
# 🎨 STICKER UTILITIES & CONVERSION SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🎨 sᴛɪᴄᴋᴇʀ"

__help__ = """
*🎨 sᴛɪᴄᴋᴇʀ ᴛᴏᴏʟs* — Convert images to stickers, stickers to images, or pack them seamlessly!

• `/sticker` or `/kang` — Reply to an image, photo, or sticker to convert/add it to your personal sticker pack
• `/toimage` — Reply to a static sticker to convert it into a clear PNG image
"""

from pyrogram import filters
from pyrogram.types import Message
import os
import logging
from PIL import Image

def register_sticker_system(app):

    TEMP_DIR = "downloads"
    os.makedirs(TEMP_DIR, exist_ok=True)

    # ============================================================
    # 🖼️ STICKER / KANG (`/sticker`, `/kang`)
    # ============================================================
    @app.on_message(filters.command(["sticker", "kang"]))
    async def sticker_kang_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to an image, photo, or sticker to convert it!**")

        reply = message.reply_to_message
        if not (reply.photo or reply.document or reply.sticker):
            return await message.reply("❌ **Invalid media type! Reply to a photo, document image, or sticker.**")

        status_msg = await message.reply("🎨 **Processing media into sticker format...**")

        try:
            # Download media file
            file_path = await reply.download(file_name=TEMP_DIR + "/")
            
            # Convert image to PNG/WebP suitable for Telegram stickers if necessary
            if reply.photo or (reply.document and "image" in str(reply.document.mime_type)):
                img_path = file_path
                webp_filename = f"sticker_{message.id}.webp"
                webp_path = os.path.join(TEMP_DIR, webp_filename)

                # Resize and save as webp (Telegram sticker requirement: 512x512 max)
                with Image.open(img_path) as im:
                    im.thumbnail((512, 512))
                    im.save(webp_path, "WEBP")

                os.remove(img_path)
                file_path = webp_path

            # Send back as sticker
            await message.reply_sticker(sticker=file_path)
            
            os.remove(file_path)
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Sticker Kang Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to process sticker:** `{str(e)}`")

    # ============================================================
    # 📷 STICKER TO IMAGE (`/toimage`, `/img`)
    # ============================================================
    @app.on_message(filters.command(["toimage", "img"]))
    async def sticker_to_image_cmd(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.sticker:
            return await message.reply("⚠️ **Please reply to a static sticker to convert it into an image!**")

        sticker = message.reply_to_message.sticker
        if sticker.is_animated or sticker.is_video:
            return await message.reply("❌ **Animated and video stickers cannot be converted to static images directly!**")

        status_msg = await message.reply("📥 **Downloading sticker...**")

        try:
            file_path = await message.reply_to_message.download(file_name=TEMP_DIR + "/")
            img_filename = f"img_{message.id}.png"
            img_path = os.path.join(TEMP_DIR, img_filename)

            # Convert webp sticker to png image
            with Image.open(file_path) as im:
                im.save(img_path, "PNG")

            await status_msg.edit_text("📤 **Sending converted image...**")
            await message.reply_document(
                document=img_path,
                caption="🖼️ **Converted Sticker to Image**"
            )

            os.remove(file_path)
            os.remove(img_path)
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Sticker to Image Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to convert sticker:** `{str(e)}`")
