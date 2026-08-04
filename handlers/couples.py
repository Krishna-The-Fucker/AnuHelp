# ============================================================
# 💑 COUPLES MATCHING SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "💑 ᴄᴏᴜᴘʟᴇs"

__help__ = """
*💑 ᴄᴏᴜᴘʟᴇs ᴍᴀᴛᴄʜɪɴg* — Find random cute couples of the day in your group with fun animations and database tracking!

• `/couple` or `/couples` — Find today's matching couple in the group
"""

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime
import random
import logging

def register_couples_system(app, db):

    # ============================================================
    # 🗓️ GET CURRENT DATE STRING (FOR DAILY RESET)
    # ============================================================
    def get_today():
        return datetime.now().strftime("%Y-%m-%d")

    # ============================================================
    # 💑 COUPLE COMMAND HANDLER
    # ============================================================
    @app.on_message(filters.command(["couple", "couples", "shipping"]) & filters.group)
    async def couple_handler(client, message: Message):
        chat_id = message.chat.id
        today = get_today()

        try:
            # Check if couple already exists for today in this chat
            existing_data = await db.couples.find_one({"chat_id": chat_id, "date": today})

            if existing_data:
                user1_id = existing_data["user1_id"]
                user2_id = existing_data["user2_id"]

                try:
                    user1 = await client.get_users(user1_id)
                    user2 = await client.get_users(user2_id)
                    
                    return await message.reply_text(
                        f"💘 **Today's Couple of the Group:** 💘\n\n"
                        f"{user1.mention} ❤️ {user2.mention}\n\n"
                        f"✨ _They were already chosen as the perfect match for today! Come back tomorrow for a new couple._",
                        disable_web_page_preview=True
                    )
                except Exception:
                    pass

            # Fetch active group members or recent message senders to pick from
            # Fallback mechanism: Get chat members if possible, or use message senders cached/collected
            bot_member = await client.get_chat_member(chat_id, (await client.get_me()).id)
            
            # Collecting members from recent history or checking database users
            users_list = []
            async for m in client.get_chat_history(chat_id, limit=100):
                if m.from_user and not m.from_user.is_bot:
                    if m.from_user.id not in users_list:
                        users_list.append(m.from_user.id)

            if len(users_list) < 2:
                return await message.reply_text(
                    "⚠️ **Not enough active members found in this group to choose a couple!**\n"
                    "_Chat a bit more so I can find active participants._"
                )

            # Randomly select two distinct users
            user1_id = random.choice(users_list)
            users_list.remove(user1_id)
            user2_id = random.choice(users_list)

            user1 = await client.get_users(user1_id)
            user2 = await client.get_users(user2_id)

            # Save today's couple in database
            await db.couples.update_one(
                {"chat_id": chat_id, "date": today},
                {
                    "$set": {
                        "user1_id": user1.id,
                        "user2_id": user2.id,
                        "updated_at": datetime.utcnow()
                    }
                },
                upsert=True
            )

            # Fun matching text variations
            match_quotes = [
                "Match made in heaven! ✨",
                "Absolute cuties! 🥰",
                "Looking great together! 🥂",
                "True love is in the air! 💕",
                "The cutest duo of the day! 🌹"
            ]
            selected_quote = random.choice(match_quotes)

            # Interactive loading animation effect
            msg = await message.reply_text("🔄 **Searching for today's perfect match...**")
            await asyncio.sleep(1.5)
            await msg.edit_text("💞 **Mixing hearts and calculating compatibility...**")
            await asyncio.sleep(1.5)

            await msg.edit_text(
                f"🎉 **Couple of the Day** 🎉\n"
                f"📅 **Date:** `{today}`\n\n"
                f"❤️ {user1.mention} + {user2.mention} = **MATCHED!** ❤️\n\n"
                f"__{selected_quote}__",
                disable_web_page_preview=True
            )

        except Exception as e:
            logging.error(f"[Couples System Error]: {e}")
            await message.reply_text("❌ **An error occurred while generating the couple match. Please try again later!**")
