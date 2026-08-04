# ============================================================
# 🎞️ GIF & ANIME GIF CONVERSION UTILITIES (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🎞️ ɢɪꜰ"

__help__ = """
*🎞️ ɢɪғ & ᴀɴɪᴍᴇ ɢɪғ ᴛᴏᴏʟs* — Convert videos or create animated effects seamlessly!

• `/gif` — Reply to a video, video note, or animation to convert it into a normal looping GIF
• `/anigif` — Reply to a video, image sequence, or sticker to generate an enhanced anime-style GIF effect
"""

from pyrogram import filters
from pyrogram.types import Message
import os
import logging
import imageio
from PIL import Image, ImageOps

def register_gif_system(app):

    TEMP_DIR = "downloads"
    os.makedirs(TEMP_DIR, exist_ok=True)

    # ============================================================
    # 🎞️ CONVERT NORMAL MEDIA TO GIF (`/gif`)
    # ============================================================
    @app.on_message(filters.command("gif"))
    async def convert_to_gif_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to a video, video note, or sticker to convert it into a GIF!**")

        reply = message.reply_to_message
        if not (reply.video or reply.video_note or reply.sticker or reply.animation):
            return await message.reply("❌ **Invalid media format! Reply to a video, video note, or sticker.**")

        status_msg = await message.reply("🎞️ **Downloading and converting media to GIF...**")

        try:
            file_path = await reply.download(file_name=TEMP_DIR + "/")
            
            await message.reply_animation(
                animation=file_path,
                caption="🎞️ **Converted Media to Normal GIF**"
            )

            if os.path.exists(file_path):
                os.remove(file_path)

            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Gif Conversion Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to convert media to GIF:** `{str(e)}`")

    # ============================================================
    # 🌸 CREATE ANIME-STYLE GIF (`/anigif`)
    # ============================================================
    @app.on_message(filters.command("anigif"))
    async def create_anime_gif_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to a video, photo, or sticker to create an anime-style GIF!**")

        reply = message.reply_to_message
        status_msg = await message.reply("🌸 **Processing and generating Anime-style GIF...**")

        try:
            file_path = await reply.download(file_name=TEMP_DIR + "/")
            output_gif_path = os.path.join(TEMP_DIR, f"anime_{message.id}.gif")

            # Handle photo / image input into looping aesthetic animated effect
            if reply.photo or (reply.document and "image" in str(reply.document.mime_type)):
                with Image.open(file_path) as im:
                    im = im.convert("RGB")
                    im = ImageOps.fit(im, (400, 400), Image.Resampling.LANCZOS)
                    
                    # Create a multi-frame subtle pulse/zoom effect frames mimicking anime loop
                    frames = []
                    for i in range(10):
                        scale = 1.0 + (i * 0.01 if i < 5 else (10 - i) * 0.01)
                        w, h = int(400 * scale), int(400 * scale)
                        resized = im.resize((w, h), Image.Resampling.LANCZOS)
                        # Crop back to 400x400 center
                        left = (w - 400) // 2
                        top = (h - 400) // 2
                        cropped = resized.crop((left, top, left + 400, top + 400))
                        frames.append(cropped)

                    frames[0].save(
                        output_gif_path,
                        save_all=True,
                        append_images=frames[1:],
                        optimize=True,
                        duration=100,
                        loop=0
                    )
            else:
                # If video/animation, pass through or process using imageio frame extraction
                reader = imageio.get_reader(file_path)
                fps = reader.get_meta_data().get('fps', 15)
                
                frames = []
                for i, im_array in enumerate(reader):
                    if i > 60: # Limit frames for lightweight size
                        break
                    img = Image.fromarray(im_array).resize((320, 320), Image.Resampling.LANCZOS)
                    frames.append(img)
                reader.close()

                if frames:
                    frames[0].save(
                        output_gif_path,
                        save_all=True,
                        append_images=frames[1:],
                        optimize=True,
                        duration=int(1000 / max(fps, 10)),
                        loop=0
                    )
                else:
                    output_gif_path = file_path # fallback

            await message.reply_animation(
                animation=output_gif_path,
                caption="🌸 **Generated Anime-Style GIF**"
            )

            if os.path.exists(file_path):
                os.remove(file_path)
            if os.path.exists(output_gif_path) and output_gif_path != file_path:
                os.remove(output_gif_path)

            await status_msg.delete()

        except Exception as e:
            logging.error(f"[Anime Gif Generation Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to create anime GIF:** `{str(e)}`")
