# ============================================================
# 🤖 GEMINI AI INTEGRATION SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🤖 ɢᴇᴍɪɴɪ"

__help__ = """
*🤖 ɢᴇᴍɪɴɪ ᴀɪ sʏsᴛᴇᴍ* — Chat with Google's advanced Gemini AI directly inside your group chat or private messages!

• `/gemini <prompt>` or `/ai <prompt>` — Ask Gemini AI anything
• Reply to any message with `/gemini` or `/ai` to ask about or translate that message
"""

from pyrogram import filters
from pyrogram.types import Message
import google.generativeai as genai
import logging
import os

def register_gemini_system(app, db):
    # Configure Gemini API using environment variable
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    if GEMINI_API_KEY:
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            # Using standard gemini model configuration
            generation_config = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
            ai_model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=generation_config
            )
        except Exception as e:
            logging.error(f"[Gemini Setup Error]: {e}")
            ai_model = None
    else:
        ai_model = None

    # ============================================================
    # 🧠 GEMINI AI QUERY COMMAND (`/gemini`, `/ai`)
    # ============================================================
    @app.on_message(filters.command(["gemini", "ai", "ask"]))
    async def gemini_query_cmd(client, message: Message):
        if not ai_model:
            return await message.reply("❌ **Gemini AI is not configured!**\n_Please make sure `GEMINI_API_KEY` is set in your environment variables._")

        prompt = ""
        
        # Check if replying to a message
        if message.reply_to_message:
            replied_text = message.reply_to_message.text or message.reply_to_message.caption
            user_prompt = " ".join(message.command[1:]) if len(message.command) > 1 else "Explain or summarize this message."
            if replied_text:
                prompt = f"{user_prompt}\n\nContext Message:\n\"{replied_text}\""
            else:
                prompt = user_prompt
        elif len(message.command) > 1:
            prompt = " ".join(message.command[1:])
        else:
            return await message.reply(
                "⚠️ **Please provide a prompt or reply to a message!**\n"
                "• Usage: `/gemini <your question>`\n"
                "• Or reply to a message with `/gemini`"
            )

        status_msg = await message.reply("🤖 **Thinking...**")

        try:
            # Generate response asynchronously using google-generativeai
            response = await ai_model.generate_content_async(prompt)
            answer = response.text

            if not answer:
                return await status_msg.edit_text("⚠️ **Gemini returned an empty response.**")

            output_text = f"🤖 **Gemini AI Response:**\n\n{answer}"

            # Handle Telegram's 4096 character limit cleanly
            if len(output_text) > 4096:
                import io
                file_buffer = io.BytesIO(output_text.encode("utf-8"))
                file_buffer.name = "gemini_response.txt"
                await message.reply_document(
                    document=file_buffer,
                    caption="📁 **Response exceeded message limit. Attached as a file.**"
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text(output_text, disable_web_page_preview=True)

        except Exception as e:
            logging.error(f"[Gemini Query Error]: {e}")
            await status_msg.edit_text("❌ **An error occurred while communicating with Gemini AI.**")
