# ============================================================
# 👑 SUDO SYSTEM (ULTRA PRO MAX)
# ============================================================

from pyrogram import filters
from pyrogram.types import Message

# Project ke centralized config, db aur loader architecture ke sath sync kiya gaya hai
from config import OWNER_ID
from db import db

# Database collection for Sudo users
sudo_collection = db.sudo_users

# ============================================================
# 🧠 ASYNC DB HELPERS
# ============================================================

async def add_sudo(user_id: int):
    await sudo_collection.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def remove_sudo(user_id: int):
    await sudo_collection.delete_one({"user_id": user_id})

async def get_sudo_users():
    docs = await sudo_collection.find().to_list(length=None)
    return [d["user_id"] for d in docs] if docs else []

async def is_sudo_user(user_id: int) -> bool:
    if user_id == OWNER_ID:
        return True
    data = await sudo_collection.find_one({"user_id": user_id})
    return bool(data)


# ============================================================
# 🔐 CUSTOM SUDO FILTER
# ============================================================

async def sudo_filter_func(_, __, message: Message):
    if not message.from_user:
        return False
    user_id = message.from_user.id
    if user_id == OWNER_ID:
        return True
    return await is_sudo_user(user_id)

sudo_filter = filters.create(sudo_filter_func)


# ============================================================
# 🔥 HANDLER & COMMANDS REGISTRATION
# ============================================================

def register_sudo_system(app):

    # ➕ ADD SUDO
    @app.on_message(filters.command("addsudo") & filters.private)
    async def add_sudo_cmd(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("❌ **Only Owner can add sudo users!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Reply to a user's message to add them as sudo.**")

        user = message.reply_to_message.from_user
        if not user:
            return await message.reply("❌ Could not fetch user details.")

        if user.id == OWNER_ID:
            return await message.reply("⚠️ **Owner is already supreme 😎**")

        await add_sudo(user.id)

        await message.reply(
            f"✅ **Added to SUDO Successfully!**\n"
            f"👤 **User:** {user.mention}\n"
            f"🆔 **ID:** `{user.id}`"
        )

    # ➖ REMOVE SUDO
    @app.on_message(filters.command("delsudo") & filters.private)
    async def remove_sudo_cmd(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("❌ **Only Owner can remove sudo users!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Reply to a user's message to remove them from sudo.**")

        user = message.reply_to_message.from_user
        if not user:
            return await message.reply("❌ Could not fetch user details.")

        if user.id == OWNER_ID:
            return await message.reply("❌ **Cannot remove the owner!**")

        await remove_sudo(user.id)

        await message.reply(
            f"🚫 **Removed from SUDO Successfully!**\n"
            f"👤 **User:** {user.mention}\n"
            f"🆔 **ID:** `{user.id}`"
        )

    # 📜 LIST SUDO USERS
    @app.on_message(filters.command("sudolist") & filters.private)
    async def list_sudo_cmd(client, message: Message):
        sudo_users = await get_sudo_users()

        if not sudo_users:
            return await message.reply("❌ **No sudo users configured yet!**")

        text = f"👑 **SUDO USERS LIST**\n\n• Owner ID: `{OWNER_ID}`\n\n"

        for idx, user_id in enumerate(sudo_users, 1):
            text += f"{idx}. `👤 {user_id}`\n"

        await message.reply(text)

    # 🔍 CHECK SUDO
    @app.on_message(filters.command("checksudo") & filters.private)
    async def check_sudo_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Reply to a user to check their status.**")

        user = message.reply_to_message.from_user
        if not user:
            return await message.reply("❌ Could not fetch user details.")

        if user.id == OWNER_ID:
            return await message.reply("👑 **This user is the Bot Owner!**")

        if await is_sudo_user(user.id):
            return await message.reply("✅ **This user is a SUDO user.**")
        else:
            return await message.reply("❌ **This user is NOT a sudo user.**")
