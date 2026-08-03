# ============================================================
# 🚫 ANTI BIO LINK SYSTEM (ULTRA PRO MAX VERSION)
# ============================================================

import re
from pyrogram import filters
from pyrogram.types import ChatPermissions
from pyrogram.errors import UserNotParticipant

# Project ke centralized db structure ke sath sync kiya gaya hai
from db import db

# ============================================================
# ⚙️ CONFIG & COLLECTIONS
# ============================================================

BIO_LINK_REGEX = r"(https?://|t\.me/|@\w+|www\.)"
DEFAULT_WARN_LIMIT = 3

antibiolink_settings = db.antibiolink_settings
antibiolink_warns = db.antibiolink_warns

# ============================================================
# 🧠 HELPER FUNCTIONS (DB MANAGEMENT)
# ============================================================

async def set_antibiolink(chat_id: int, status: bool):
    await antibiolink_settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )

async def get_antibiolink(chat_id: int) -> bool:
    data = await antibiolink_settings.find_one({"chat_id": chat_id})
    return data.get("enabled", False) if data else False

async def add_bio_warn(chat_id: int, user_id: int) -> int:
    res = await antibiolink_warns.find_one_and_update(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"count": 1}},
        upsert=True,
        return_document=True
    )
    return res.get("count", 1)


# ============================================================
# 🔥 HANDLER & COMMANDS REGISTRATION
# ============================================================

def register_antibiolink(app):

    # 1. ⚙️ TOGGLE COMMAND (/antibiolink on/off)
    @app.on_message(filters.command("antibiolink") & filters.group)
    async def toggle(client, message):
        if len(message.command) < 2:
            return await message.reply("⚠️ **Usage:** `/antibiolink on` or `/antibiolink off`")

        arg = message.command[1].lower()

        if arg == "on":
            await set_antibiolink(message.chat.id, True)
            await message.reply("🚫 **Anti Bio Link System:** Enabled 🟢")

        elif arg == "off":
            await set_antibiolink(message.chat.id, False)
            await message.reply("✅ **Anti Bio Link System:** Disabled 🔴")

        else:
            await message.reply("❌ **Invalid argument!** Use `on` or `off`.")

    # 2. 🚨 MAIN BIO CHECK HANDLER
    @app.on_message(filters.group & filters.text & ~filters.bot, group=4)
    async def check_bio(client, message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        user = message.from_user

        # Check if feature is enabled for this chat
        if not await get_antibiolink(chat_id):
            return

        # Skip check for admins/creators to prevent self-lockouts
        try:
            member = await client.get_chat_member(chat_id, user.id)
            if member.status in ["administrator", "creator"]:
                return
        except:
            pass

        # 🔍 Fetch User Bio via Full Profile
        try:
            full_profile = await client.get_chat(user.id)
            bio = full_profile.bio or ""
        except UserNotParticipant:
            return
        except Exception:
            return

        # 🔗 Check if Bio contains Links / Usernames
        if not re.search(BIO_LINK_REGEX, bio.lower()):
            return

        # ❌ Delete Offending Message
        try:
            await message.delete()
        except:
            pass

        # ⚠️ Warn & Action System
        warns = await add_bio_warn(chat_id, user.id)

        if warns >= DEFAULT_WARN_LIMIT:
            try:
                await client.restrict_chat_member(
                    chat_id,
                    user.id,
                    ChatPermissions() # Completely Muted
                )
                await message.reply(
                    f"🔕 **User Muted!**\n"
                    f"👤 **User:** {user.mention}\n"
                    f"reason: `Promotional Link in Bio`\n"
                    f"⚠️ **Total Warns:** `{warns}/{DEFAULT_WARN_LIMIT}`"
                )
            except Exception as e:
                await message.reply(f"❌ Failed to mute user: `{e}`")
        else:
            await message.reply(
                f"⚠️ **Bio Link Prohibited!**\n"
                f"👤 **User:** {user.mention}\n"
                f"⚠️ **Warns:** `{warns}/{DEFAULT_WARN_LIMIT}`"
            )
