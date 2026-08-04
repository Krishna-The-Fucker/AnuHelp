# ============================================================
# 🤖 SMART AI CHATBOT SYSTEM WITH /CHATBOT TOGGLE & OWNER PERSONA
# ============================================================

__mod_name__ = "🤖 ᴀɪ ᴄʜᴀᴛ"

__help__ = """
*🤖 sᴍᴀʀᴛ ᴀɪ ᴄʜᴀᴛʙᴏᴛ* — Real-time conversational AI with auto-chat toggle, custom owner identity, and anti-repeat memory!

• `/chatbot on` or `/chatbot off` — Enable or disable automatic chatting in this group (Admin only).
• `/ai [message]` or `/chat [message]` — Chat directly with the AI anytime.
"""

from pyrogram import filters
from pyrogram.types import Message
import os
import logging
import aiohttp
import google.generativeai as genai
from cachetools import TTLCache
from motor.motor_asyncio import AsyncIOMotorClient

def register_ai_chat_system(app):

    # Database connection for chat toggles per chat ID
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    db_client = AsyncIOMotorClient(MONGO_URI)
    db = db_client["NomadBot"]
    ai_toggles_col = db["ai_toggles"]

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    DEEP_AI_API_KEY = os.getenv("DEEP_AI_API_KEY", "")

    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)

    user_response_cache = TTLCache(maxsize=1000, ttl=300)

    # ============================================================
    # ⚙️ TOGGLE COMMAND (`/chatbot on` / `/chatbot off`)
    # ============================================================
    @app.on_message(filters.command("chatbot") & ~filters.private)
    async def toggle_chatbot_cmd(client, message: Message):
        # Check if user is admin
        user = await message.chat.get_member(message.from_user.id)
        if user.status not in ["administrator", "creator"]:
            return await message.reply("⚠️ **Only group administrators can toggle the chatbot system!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Usage:** `/chatbot on` or `/chatbot off`")

        action = message.command[1].lower()
        chat_id = message.chat.id

        if action == "on":
            await ai_toggles_col.update_one(
                {"chat_id": chat_id},
                {"$set": {"enabled": True}},
                upsert=True
            )
            await message.reply("✅ **Chatbot has been enabled in this group! I will respond to conversations now.**")
        elif action == "off":
            await ai_toggles_col.update_one(
                {"chat_id": chat_id},
                {"$set": {"enabled": False}},
                upsert=True
            )
            await message.reply("❌ **Chatbot has been disabled in this group.**")
        else:
            await message.reply("⚠️ **Invalid option! Use:** `/chatbot on` or `/chatbot off`")

    # ============================================================
    # 🧠 AI GENERATION CORE (OWNER & PERSONA RULES)
    # ============================================================
    async def fetch_ai_response(prompt: str, user_id: int) -> str:
        persona = (
            "You are a friendly, sweet, and realistic human girl chatting on Telegram. "
            "Keep your responses natural, engaging, expressive, and slightly casual with emojis. "
            "IMPORTANT RULE: If anyone asks who your owner, creator, or developer is, you must proudly say: "
            "'ᴋʀɪꜱʜɴᴀ 🥺' or mention Krishna as your owner. Never mention any other developer or company. "
            "Keep responses concise."
        )

        reply_text = ""

        # 1. Try Gemini API
        if GEMINI_API_KEY:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=persona)
                response = model.generate_content(prompt)
                if response and response.text:
                    reply_text = response.text.strip()
            except Exception as e:
                logging.error(f"[Gemini AI Error]: {e}")

        # 2. Fallback to DeepAI
        if not reply_text and DEEP_AI_API_KEY:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://api.deepai.org/api/text-generator",
                        data={"text": f"{persona}\nUser: {prompt}\nGirl:"},
                        headers={"api-key": DEEP_AI_API_KEY}
                    ) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            reply_text = data.get("output", "").strip()
            except Exception as e:
                logging.error(f"[DeepAI Error]: {e}")

        if not reply_text:
            reply_text = "Aww, thoda network issue ho gaya ya APIs busy hain! Phir se bolo na? 🙈"

        # Anti-Repeat Check
        last_response = user_response_cache.get(user_id)
        if reply_text == last_response:
            reply_text += " ✨"

        user_response_cache[user_id] = reply_text
        return reply_text

    # ============================================================
    # 💬 GROUP & PRIVATE CHAT LISTENER
    # ============================================================
    @app.on_message(filters.command(["ai", "chat", "ask"]) | (filters.text & ~filters.bot))
    async def ai_chatbot_handler(client, message: Message):
        is_command = message.command is not None and len(message.command) > 0
        
        if is_command:
            query = " ".join(message.command[1:])
            if not query and message.reply_to_message and message.reply_to_message.text:
                query = message.reply_to_message.text
            if not query:
                return await message.reply("⚠️ **Please provide a message for the AI! Example:** `/ai Hello`")
        else:
            # Group chat auto-check logic
            if message.chat.type.value != "private":
                toggle_doc = await ai_toggles_col.find_one({"chat_id": message.chat.id})
                is_enabled = toggle_doc.get("enabled", False) if toggle_doc else False
                
                # If toggle is off, ignore unless bot is replied to or mentioned
                me = await client.get_me()
                is_replied = message.reply_to_message and message.reply_to_message.from_user.id == me.id
                
                if not is_enabled and not is_replied:
                    return

            query = message.text

        user = message.from_user
        user_name = user.first_name if user else "Friend"
        user_mention = user.mention if user else user_name

        raw_response = await fetch_ai_response(query, user.id if user else 0)
        final_output = f"{user_mention}, {raw_response}"

        await message.reply_text(final_output, disable_web_page_preview=True)
