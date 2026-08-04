# ============================================================
# 🤖 APPROVAL SYSTEM (ULTIMATE PRO MAX++)
# ============================================================

__mod_name__ = "✅ ᴀᴘᴘʀᴏᴠᴀʟ"

__help__ = """
*✅ ᴀᴘ𝗽𝗿𝗼𝘃𝗮𝗹 sʏsᴛᴇᴍ* — Whitelist trusted users so that group protection systems (Anti-Spam, Lock, Flood, etc.) ignore them!

• `/approve` — Reply to a user or pass user ID to approve them
• `/unapprove` — Remove a user from the approved list
• `/approved` — View the complete list of approved users
• `/clearapproved` — Wipe all approved users from the group database
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
from cachetools import TTLCache
import logging

def register_approval_system(app, db, DEV_LIST):

    # ============================================================
    # ⚡ HIGH-PERFORMANCE TTL CACHE
    # ============================================================
    cache = TTLCache(maxsize=10000, ttl=600)

    def clear_cache(chat_id=None):
        if chat_id:
            keys = [k for k in cache if str(chat_id) in k]
            for k in keys:
                cache.pop(k, None)
        else:
            cache.clear()

    # ============================================================
    # 🔐 ADMIN CHECK HELPER
    # ============================================================
    async def is_admin(client, message: Message):
        if not message.from_user:
            return False
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except Exception:
            return False

    # ============================================================
    # 🔧 DATABASE FUNCTIONS
    # ============================================================
    async def approve_user(chat_id, user_id):
        await db.approvals.update_one(
            {"chat_id": chat_id},
            {"$addToSet": {"users": user_id}},
            upsert=True
        )

    async def unapprove_user(chat_id, user_id):
        await db.approvals.update_one(
            {"chat_id": chat_id},
            {"$pull": {"users": user_id}}
        )

    async def is_approved(chat_id, user_id):
        key = f"{chat_id}:{user_id}"
        if key in cache:
            return cache[key]

        data = await db.approvals.find_one({"chat_id": chat_id})
        result = user_id in data.get("users", []) if data else False

        cache[key] = result
        return result

    async def get_all(chat_id):
        key = f"list:{chat_id}"
        if key in cache:
            return cache[key]

        data = await db.approvals.find_one({"chat_id": chat_id})
        users = data.get("users", []) if data else []

        cache[key] = users
        return users

    async def remove_all(chat_id):
        await db.approvals.update_one(
            {"chat_id": chat_id},
            {"$set": {"users": []}},
            upsert=True
        )

    # ============================================================
    # 🎯 TARGET RESOLVER UTILITY
    # ============================================================
    async def get_target(message: Message):
        if message.reply_to_message:
            if message.reply_to_message.sender_chat:
                return message.reply_to_message.sender_chat.id
            if message.reply_to_message.from_user:
                return message.reply_to_message.from_user.id

        if len(message.command) > 1:
            try:
                return int(message.command[1])
            except Exception:
                return None
        return None

    # ============================================================
    # ✅ APPROVE COMMAND
    # ============================================================
    @app.on_message(filters.command(["approve", "free"]) & filters.group)
    async def approve_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can use this command!**")

        user_id = await get_target(message)
        if not user_id:
            return await message.reply(
                "⚠️ **Incorrect usage!**\n"
                "• Reply to a user's message or provide their User ID.\n"
                "• Example: `/approve 123456789`"
            )

        if message.from_user and user_id == message.from_user.id:
            return await message.reply("🙃 **You cannot approve yourself!**")

        if DEV_LIST and user_id in DEV_LIST:
            return await message.reply("👑 **Developer is already globally approved!**")

        if await is_approved(message.chat.id, user_id):
            return await message.reply("⚠️ **This user is already approved in this group!**")

        await approve_user(message.chat.id, user_id)
        clear_cache(message.chat.id)

        await message.reply(
            f"✅ **User Successfully Approved!**\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **Status:** Exempted from automatic group filters & restrictions 🛡️"
        )

    # ============================================================
    # ❌ UNAPPROVE COMMAND
    # ============================================================
    @app.on_message(filters.command(["unapprove", "unfree"]) & filters.group)
    async def unapprove_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can use this command!**")

        user_id = await get_target(message)
        if not user_id:
            return await message.reply("⚠️ **Please reply to a user or specify a User ID to unapprove.**")

        if not await is_approved(message.chat.id, user_id):
            return await message.reply("⚠️ **This user is not in the approved list!**")

        await unapprove_user(message.chat.id, user_id)
        clear_cache(message.chat.id)

        await message.reply(f"❌ **User Unapproved Successfully:** `{user_id}` 🔴")

    # ============================================================
    # 📜 LIST APPROVED USERS COMMAND
    # ============================================================
    @app.on_message(filters.command("approved") & filters.group)
    async def approved_list(client, message: Message):
        users = await get_all(message.chat.id)

        if not users:
            return await message.reply("📭 **No approved users found in this group.**")

        text = "✅ **Approved Users List:**\n\n"
        for i, user in enumerate(users[:50], start=1):
            text += f"{i}. `ID: {user}`\n"

        if len(users) > 50:
            text += f"\n_Showing first 50 out of {len(users)} approved users._"

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("🗑️ Clear All Approved", callback_data="clear_approved")]
        ])

        await message.reply_text(text, reply_markup=btn)

    # ============================================================
    # 🧹 CLEAR ALL APPROVALS COMMAND
    # ============================================================
    @app.on_message(filters.command("clearapproved") & filters.group)
    async def clear_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can execute this command!**")

        btn = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Clear All", callback_data="clear_approved"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_action")
            ]
        ])

        await message.reply("⚠️ **Are you sure you want to remove all approved users from this group?**", reply_markup=btn)

    # ============================================================
    # 🎮 CALLBACK BUTTON HANDLERS
    # ============================================================
    @app.on_callback_query(filters.regex("^clear_approved$"))
    async def clear_all_cb(client, cq: CallbackQuery):
        if not await is_admin(client, cq.message):
            return await cq.answer("❌ You are not an administrator!", show_alert=True)

        await remove_all(cq.message.chat.id)
        clear_cache(cq.message.chat.id)

        try:
            await cq.message.edit_text("🗑️ **All approved users have been successfully cleared!** ✨")
        except Exception:
            pass
        await cq.answer("Cleared successfully!", show_alert=False)

    @app.on_callback_query(filters.regex("^cancel_action$"))
    async def cancel_cb(client, cq: CallbackQuery):
        try:
            await cq.message.edit_text("❌ **Operation cancelled successfully.**")
        except Exception:
            pass
        await cq.answer("Cancelled", show_alert=False)
