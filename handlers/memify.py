# ============================================================
# 🖼️ MEMIFY & IMAGE CAPTIONING MODULE (ULTRA PRO MAX)
# ============================================================

__mod_name__ = "🖼️ ᴍᴇᴍɪꜰʏ"

__help__ = """
*🖼️ ᴍᴇᴍɪꜰʏ ᴍᴏᴅᴜʟᴇ* — Turn any photo or sticker into a custom meme instantly!

• `/memify [top text] ; [bottom text]` — Reply to a photo, sticker, or animated media to create a custom meme with custom text.
"""

from pyrogram import filters
from pyrogram.types import Message
import io
import os
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("MEMIFY")

def register_memify_system(app):

    def get_meme_font(size: int):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    @app.on_message(filters.command("memify"))
    async def memify_cmd(client, message: Message):
        reply = message.reply_to_message
        if not reply or not (reply.photo or reply.sticker):
            return await message.reply("⚠️ **Please reply to a photo or sticker to memify it! Example:** `/memify Top Text ; Bottom Text`")

        args = " ".join(message.command[1:])
        if not args:
            top_text = ""
            bottom_text = message.reply_to_message.text or "MEME"
        else:
            if ";" in args:
                parts = args.split(";", 1)
                top_text = parts[0].strip()
                bottom_text = parts[1].strip()
            else:
                top_text = args.strip()
                bottom_text = ""

        status_msg = await message.reply("🖼️ **Generating your custom meme... Please wait.**")

        try:
            # Download file to memory
            file_path = await client.download_media(reply, file_name="memify_temp.png")
            
            image = Image.open(file_path).convert("RGB")
            width, height = image.size

            draw = ImageDraw.Draw(image)
            font_size = int(height / 10) if height > 200 else 24
            font = get_meme_font(font_size)

            # Helper function to draw text with black outline/stroke for meme readability
            def draw_meme_text(text, y_pos):
                if not text:
                    return
                # Measure text width roughly
                bbox = draw.textbbox((0, 0), text.upper(), font=font)
                text_width = bbox[2] - bbox[0]
                x_pos = (width - text_width) / 2

                # Draw thick outline (shadow effect)
                offset = max(2, int(font_size / 15))
                for ox in range(-offset, offset + 1):
                    for oy in range(-offset, offset + 1):
                        draw.text((x_pos + ox, y_pos + oy), text.upper(), font=font, fill=(0, 0, 0))

                # Draw main white text
                draw.text((x_pos, y_pos), text.upper(), font=font, fill=(255, 255, 255))

            # Draw Top Text
            if top_text:
                draw_meme_text(top_text, 10)

            # Draw Bottom Text
            if bottom_text:
                bbox = draw.textbbox((0, 0), bottom_text.upper(), font=font)
                text_height = bbox[3] - bbox[1]
                draw_meme_text(bottom_text, height - text_height - 20)

            # Save to output stream
            output = io.BytesIO()
            output.name = "meme.png"
            image.save(output, "PNG")
            output.seek(0)

            await message.reply_photo(photo=output, caption="✨ **Here is your freshly baked meme!**")
            await status_msg.delete()

            # Clean up local downloaded file
            if os.path.exists(file_path):
                os.remove(file_path)

        except Exception as e:
            logger.error(f"[Memify Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to generate meme:** `{str(e)}`")
