# ============================================================
# 🎨 STICKER & ANIME STICKER UTILITIES (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🎨 sᴛɪᴄᴋᴇʀ"

__help__ = """
*🎨 sᴛɪᴄᴋᴇʀ & ᴀɴɪᴍᴇ sᴛɪᴄᴋᴇʀ ᴛᴏᴏʟs* — Convert media into stickers or anime-style custom stickers seamlessly!

• `/sticker` — Reply to an image, photo, or sticker to convert it into a normal sticker
• `/anisticker` — Reply to a photo or image to generate an enhanced anime-styled glowing sticker
• `/toimage` or `/img` — Reply to a static sticker to convert it into a clear PNG image
"""

from pyrogram import filters
from pyrogram.types import Message
import os
import logging
from PIL import Image, ImageOps, ImageEnhance

def register_sticker_system(app):

    TEMP_DIR = "downloads"
    os.makedirs(TEMP_DIR, exist_ok=True)

    # ============================================================
    # 🖼️ NORMAL STICKER (`/sticker`, `/kang`)
    # ============================================================
    @app.on_message(filters.command(["sticker", "kang"]))
    async def sticker_kang_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to an image, photo, or sticker to convert it!**")

        reply = message.reply_to_message
        if not (reply.photo or reply.document or reply.sticker):
            return await message.reply("❌ **Invalid media type! Reply to a photo, document image, or sticker.**")

        status_msg = await message.reply("🎨 **Processing media into normal sticker format...**")

        try:
            file_path = await reply.download(file_name=TEMP_DIR + "/")
            
            if reply.photo or (reply.document and "image" in str(reply.document.mime_type)):
                img_path = file_path
                webp_filename = f"sticker_{message.id}.webp"
                webp_path = os.path.join(TEMP_DIR, webp_filename)

                with Image.open(img_path) as im:
                    im.thumbnail((512, 512))
                    im.save(webp_path, "WEBP")

                os.remove(img_path)
                file_path = webp_path

            await message.reply_sticker(sticker=file_path)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Sticker Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to process sticker:** `{str(e)}`")

    # ============================================================
    # 🌸 ANIME STICKER (`/anisticker`)
    # ============================================================
    @app.on_message(filters.command("anisticker"))
    async def anime_sticker_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to a photo or image to create an anime-style sticker!**")

        reply = message.reply_to_message
        if not (reply.photo or (reply.document and "image" in str(reply.document.mime_type))):
            return await message.reply("❌ **Please reply to a valid photo or image file!**")

        status_msg = await message.reply("🌸 **Generating Anime-style glowing sticker...**")

        try:
            file_path = await reply.download(file_name=TEMP_DIR + "/")
            ani_webp_filename = f"anisticker_{message.id}.webp"
            ani_webp_path = os.path.join(TEMP_DIR, ani_webp_filename)

            with Image.open(file_path) as im:
                im = im.convert("RGBA")
                # Fit to Telegram 512x512 canvas requirement
                im = ImageOps.fit(im, (512, 512), Image.Resampling.LANCZOS)
                
                # Enhance colors and brightness for vibrant anime aesthetic
                enhancer = ImageEnhance.Color(im)
                im = enhancer.enhance(1.3) # Boost saturation
                
                contrast = ImageEnhance.Contrast(im)
                im = contrast.enhance(1.1)

                im.save(ani_webp_path, "WEBP", quality=95)

            await message.reply_sticker(sticker=ani_webp_path)

            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(ani_webp_path):
                os.remove(ani_webp_path)

            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Anime Sticker Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to create anime sticker:** `{str(e)}`")

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

            with Image.open(file_path) as im:
                im.save(img_path, "PNG")

            await status_msg.edit_text("📤 **Sending converted image...**")
            await message.reply_document(
                document=img_path,
                caption="🖼️ **Converted Sticker to Image**"
            )

            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(img_path):
                os.remove(img_path)
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Sticker to Image Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to convert sticker:** `{str(e)}`")
