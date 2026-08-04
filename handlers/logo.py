# ============================================================
# 🎨 LOGO & BANNER GENERATOR MODULE (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🎨 ʟᴏɢᴏ"

__help__ = """
*🎨 ʟᴏɢᴏ ɢᴇɴᴇʀᴀᴛᴏʀ* — Create stunning custom text logos, badges, and profile banners instantly with custom fonts and styles!

• `/logo [your text]` — Generate a cool custom text logo or badge image.
• `/banner [text]` — Generate a stylish banner for your channel or group profile.
"""

from pyrogram import filters
from pyrogram.types import Message
import io
import os
import logging
from PIL import Image, ImageDraw, ImageFont
import random

def register_logo_system(app):

    # Helper function to load a system or default TrueType font safely
    def get_font(size: int):
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

    # ============================================================
    # 🎨 LOGO GENERATOR (`/logo`)
    # ============================================================
    @app.on_message(filters.command("logo"))
    async def logo_generator_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide text for the logo! Example:** `/logo Nomad Bot`")

        status_msg = await message.reply("🎨 **Designing your custom logo... Please wait.**")

        try:
            # Image Dimensions
            width, height = 800, 800
            
            # Generate random vivid gradient background
            bg_color_1 = (random.randint(10, 50), random.randint(10, 50), random.randint(30, 90))
            bg_color_2 = (random.randint(180, 255), random.randint(50, 150), random.randint(100, 255))
            
            image = Image.new("RGB", (width, height), bg_color_1)
            draw = ImageDraw.Draw(image)

            # Simple gradient effect simulation
            for x in range(width):
                r = int(bg_color_1[0] + (bg_color_2[0] - bg_color_1[0]) * (x / width))
                g = int(bg_color_1[1] + (bg_color_2[1] - bg_color_1[1]) * (x / width))
                b = int(bg_color_1[2] + (bg_color_2[2] - bg_color_1[2]) * (x / width))
                draw.line([(x, 0), (x, height)], fill=(r, g, b))

            # Draw decorative circular badge border
            margin = 50
            draw.ellipse([margin, margin, width - margin, height - margin], outline=(255, 255, 255), width=8)

            # Load Font & Calculate Text Wrapping/Positioning
            font_size = 65
            font = get_font(font_size)

            # Word wrap text if too long
            words = query.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = f"{current_line} {word}".strip()
                # Approximate bounding box check using length
                if len(test_line) * (font_size / 2) < (width - 200):
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)

            final_text_block = "\n".join(lines)

            # Draw text shadow for depth
            text_x, text_y = width / 2, height / 2
            draw.multiline_text(
                (text_x + 4, text_y + 4),
                final_text_block,
                font=font,
                fill=(0, 0, 0),
                anchor="mm",
                align="center"
            )

            # Draw main foreground white text
            draw.multiline_text(
                (text_x, text_y),
                final_text_block,
                font=font,
                fill=(255, 255, 255),
                anchor="mm",
                align="center"
            )

            # Save to BytesIO stream
            output = io.BytesIO()
            output.name = "logo.png"
            image.save(output, "PNG")
            output.seek(0)

            await message.reply_photo(
                photo=output,
                caption=f"🎨 **Here is your custom logo for:** `{query}` ✨"
            )
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Logo Generator Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to generate logo:** `{str(e)}`")

    # ============================================================
    # 🖼️ BANNER GENERATOR (`/banner`)
    # ============================================================
    @app.on_message(filters.command("banner"))
    async def banner_generator_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide text for the banner! Example:** `/banner Nomad Group`")

        status_msg = await message.reply("🖼️ **Designing your custom banner... Please wait.**")

        try:
            # Banner Landscape Dimensions (YouTube/Telegram Header standard ratio)
            width, height = 1200, 400
            
            image = Image.new("RGB", (width, height), (20, 20, 35))
            draw = ImageDraw.Draw(image)

            # Draw sleek geometric background accents
            for _ in range(15):
                x1 = random.randint(0, width)
                y1 = random.randint(0, height)
                x2 = x1 + random.randint(50, 300)
                y2 = y1 + random.randint(20, 100)
                draw.rectangle([x1, y1, x2, y2], outline=(random.randint(50, 150), random.randint(50, 150), 200), width=2)

            font = get_font(55)
            text_x, text_y = width / 2, height / 2

            # Banner Shadow & Text
            draw.text((text_x + 3, text_y + 3), query.upper(), font=font, fill=(0, 0, 0), anchor="mm")
            draw.text((text_x, text_y), query.upper(), font=font, fill=(0, 220, 255), anchor="mm")

            output = io.BytesIO()
            output.name = "banner.png"
            image.save(output, "PNG")
            output.seek(0)

            await message.reply_photo(
                photo=output,
                caption=f"🖼️ **Here is your custom banner for:** `{query}` ✨"
            )
            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Banner Generator Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to generate banner:** `{str(e)}`")
