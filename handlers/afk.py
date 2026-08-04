# ============================================================
# 💤 AFK SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "💤 ᴀғᴋ"

__help__ = """
*💤 ᴀғᴋ sʏsᴛᴇᴍ* — Let others know when you are away from keyboard! The bot will automatically notify anyone who tags or replies to you while you're AFK.

• `/afk [reason]` — Set yourself as AFK with an optional reason
• Just send a message in chat to automatically remove your AFK status.
"""

from pyrogram import filters
from pyrogram.types import Message
import logging
import time

def register_afk_system(app, db):

    # ============================================================
    # 💤 SET AFK COMMAND (`/afk`)
    # ============================================================
    @app.on_message(filters.command("afk") & filters.group)
    async def set_afk_cmd(client, message: Message):
        if not message.from_user:
            return

        user_id = message.from_user.id
        reason = " ".join(message.command[1:]) if len(message.command) > 1 else "Busy"
        current_time = time.time()

        try:
            await db.afk_users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "reason": reason,
                        "time": current_time,
                        "name": message.from_user.first_name
                    }
                },
                upsert=True
            )
            await message.reply(
                f"💤 **{message.from_user.mention} is now AFK!**\n"
                f"📝 **Reason:** `{reason}`"
            )
        except Exception as e:
            logging.error(f"[AFK Set Error]: {e}")
            await message.reply("❌ **Failed to set AFK status due to a database error.**")

    # ============================================================
    # 🏃 REMOVE AFK ON SENDING MESSAGE
    # ============================================================
    @app.on_message(filters.group & ~filters.bot, group=6)
    async def remove_afk_watcher(client, message: Message):
        if not message.from_user:
            return

        user_id = message.from_user.id

        try:
            afk_doc = await db.afk_users.find_one({"user_id": user_id})
            if afk_doc:
                await db.afk_users.delete_one({"user_id": user_id})
                
                # Calculate total time spent AFK
                start_time = afk_doc.get("time", time.time())
                duration_sec = int(time.time() - start_time)
                
                hours, remainder = divmod(duration_sec, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                duration_str = ""
                if hours > 0:
                    duration_str += f"{hours}h "
                if minutes > 0:
                    duration_str += f"{minutes}m "
                duration_str += f"{seconds}s"

                await message.reply(
                    f"👋 **Welcome back, {message.from_user.mention}!**\n"
                    f"⏱️ **You were AFK for:** `{duration_str}`",
                    disable_web_page_preview=True
                )
        except Exception as e:
            logging.error(f"[AFK Remove Watcher Error]: {e}")

    # ============================================================
    # 👀 CHECK AFK MENTIONS & REPLIES WATCHER
    # ============================================================
    @app.on_message(filters.group & ~filters.bot, group=7)
    async def check_afk_mentions(client, message: Message):
        target_users = set()

        # Check mentioned users
        if message.entities:
            for entity in message.entities:
                if entity.type.name == "MENTION":
                    # Extract username text from message
                    username = message.text[entity.offset:entity.offset + entity.length].strip("@")
                    try:
                        user = await client.get_users(username)
                        if user:
                            target_users.add(user.id)
                    except Exception:
                        pass
                elif entity.type.name == "TEXT_MENTION" and entity.user:
                    target_users.add(entity.user.id)

        # Check replied-to user
        if message.reply_to_message and message.reply_to_message.from_user:
            target_users.add(message.reply_to_message.from_user.id)

        if not target_users:
            return

        try:
            for u_id in target_users:
                # Don't notify if user tags themselves
                if message.from_user and message.from_user.id == u_id:
                    continue

                afk_doc = await db.afk_users.find_one({"user_id": u_id})
                if afk_doc:
                    reason = afk_doc.get("reason", "Busy")
                    start_time = afk_doc.get("time", time.time())
                    
                    duration_sec = int(time.time() - start_time)
                    hours, remainder = divmod(duration_sec, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    
                    duration_str = ""
                    if hours > 0:
                        duration_str += f"{hours}h "
                    if minutes > 0:
                        duration_str += f"{minutes}m "
                    duration_str += f"{seconds}s"

                    name = afk_doc.get("name", "User")
                    await message.reply(
                        f"💤 **{name} is currently AFK!**\n"
                        f"📝 **Reason:** `{reason}`\n"
                        f"⏱️ **Away for:** `{duration_str}`",
                        disable_web_page_preview=True
                    )
        except Exception as e:
            logging.error(f"[AFK Mentions Check Error]: {e}")
