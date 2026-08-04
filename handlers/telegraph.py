# ============================================================
# 📝 TELEGRAPH MEDIA & TEXT PUBLISHING SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name = "📝 ᴛᴇʟᴇɢʀᴀᴘʜ"

__help__ = """
*📝 ᴛᴇʟᴇɢʀᴀᴘʜ ᴛᴏᴏʟs* — Instantly upload text or media to Telegraph and get a clean public web link!

• `/telegraph` or `/tg` — Reply to text, a long message, an image, or a video to publish it to Telegraph and get a shareable link.
"""

from pyrogram import filters
from pyrogram.types import Message
import os
import logging
from telegraph import Telegraph

def register_telegraph_system(app):

    # Initialize Telegraph client
    telegraph = Telegraph()
    try:
        telegraph.create_account(short_name="NomadBot")
    except Exception as e:
        logging.error(f"[Telegraph Init Error]: {e}")

    TEMP_DIR = "downloads"
    os.makedirs(TEMP_DIR, exist_ok=True)

    # ============================================================
    # 🌐 PUBLISH TO TELEGRAPH (`/telegraph`, `/tg`)
    # ============================================================
    @app.on_message(filters.command(["telegraph", "tg"]))
    async def telegraph_upload_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to text, an image, or a video to publish it on Telegraph!**")

        reply = message.reply_to_message
        status_msg = await message.reply("🌐 **Uploading content to Telegraph...**")

        try:
            # Handle text content
            if reply.text or reply.caption:
                content_text = reply.text or reply.caption
                # Convert basic newlines to HTML paragraph breaks for Telegraph
                html_content = "".join([f"<p>{line}</p>" for line in content_text.split("\n") if line.strip()])
                
                title = f"Nomad Post - {message.from_user.first_name if message.from_user else 'User'}"
                response = telegraph.create_page(
                    title=title,
                    html_content=html_content
                )
                
                link = f"https://telegra.ph/{response['path']}"
                await status_msg.edit_text(
                    f"✅ **Successfully published to Telegraph!**\n\n"
                    f"🔗 **Link:** {link}",
                    disable_web_page_preview=False
                )

            # Handle media content (Photos/Videos/Documents)
            elif reply.photo or reply.video or reply.document:
                file_path = await reply.download(file_name=TEMP_DIR + "/")
                
                # Upload file to a telegraph image/media hosting host via upload_file helper
                import requests
                
                with open(file_path, "rb") as f:
                    file_bytes = f.read()

                # Upload to telegraph backend service via multipart form data
                upload_response = requests.post(
                    "https://telegra.ph/upload",
                    files={"file": ("file", file_bytes, "image/jpeg" if reply.photo else "video/mp4")}
                )
                
                res_json = upload_response.json()
                if isinstance(res_json, list) and len(res_json) > 0 and "src" in res_json[0]:
                    media_url = f"https://telegra.ph{res_json[0]['src']}"
                    await status_msg.edit_text(
                        f"✅ **Media successfully uploaded to Telegraph!**\n\n"
                        f"🔗 **Link:** {media_url}",
                        disable_web_page_preview=False
                    )
                else:
                    await status_msg.edit_text("❌ **Failed to upload media file to Telegraph servers.**")

                if os.path.exists(file_path):
                    os.remove(file_path)
            else:
                await status_msg.edit_text("❌ **Unsupported content format for Telegraph publishing.**")

        except Exception as e:
            logging.error(f"[Telegraph Error]: {e}")
            await status_msg.edit_text(f"❌ **An error occurred while publishing to Telegraph:** `{str(e)}`")
