# ============================================================
# 🌐 FEDERATION SYSTEM MODULE (ULTRA PRO MAX + MONGODB)
# ============================================================

__mod_name__ = "🌐 ꜰᴇᴅᴇʀᴀᴛɪᴏɴ"

__help__ = """
*🌐 ꜰᴇᴅᴇʀᴀᴛɪᴏɴ ᴍᴏᴅᴜʟᴇ* — Cross-group banning and administrative security network across multiple Telegram chats!

• `/newfed [name]` — Create a new Federation (Private chat only).
• `/joinfed [fed_id]` — Connect your group to a Federation (Admin only).
• `/leavefed` — Disconnect your group from its current Federation.
• `/gban` — Globally ban a user across all chats in the federation (Reply to user).
• `/ungban` — Remove a user from the global ban list (Reply to user).
• `/fedinfo` — View statistics and details of the current federation.
"""

from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID, DEV_LIST
from db import db
import logging

logger = logging.getLogger("FEDERATION")

def register_fed_system(app):

    # ============================================================
    # 🧠 HELPERS (MONGODB BACKED)
    # ============================================================
    async def is_fed_admin(user_id: int, fed_id: str) -> bool:
        if user_id in DEV_LIST or user_id == OWNER_ID:
            return True
        fed = await db.feds.find_one({"fed_id": fed_id})
        if not fed:
            return False
        return user_id == fed.get("owner") or user_id in fed.get("admins", [])

    # ============================================================
    # 🆕 CREATE FEDERATION (`/newfed`)
    # ============================================================
    @app.on_message(filters.command("newfed") & filters.private)
    async def new_fed_cmd(client, message: Message):
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            return await message.reply_text("❌ **Please provide a Federation name! Example:** `newfed GlobalGuard`")

        fed_name = args[1].strip()
        user_id = message.from_user.id

        # Check if user already owns a federation
        existing_fed = await db.feds.find_one({"owner": user_id})
        if existing_fed and user_id not in DEV_LIST and user_id != OWNER_ID:
            return await message.reply_text(f"⚠️ **You already own a Federation:** `{existing_fed['fed_id']}` ({existing_fed['name']})")

        # Generate unique federation ID
        count = await db.feds.count_documents({})
        fed_id = f"FED-{count + 101}"

        try:
            await db.feds.insert_one({
                "fed_id": fed_id,
                "name": fed_name,
                "owner": user_id,
                "admins": [],
                "gbanned": []
            })

            await message.reply_text(
                f"✅ **Federation Created Successfully!**\n\n"
                f"🆔 **Fed ID:** `{fed_id}`\n"
                f"📛 **Name:** `{fed_name}`\n"
                f"👑 **Owner:** `{user_id}`\n\n"
                f"_Use `/joinfed {fed_id}` in your group chats to link them!_"
            )
        except Exception as e:
            logger.error(f"[NewFed Error]: {e}")
            await message.reply_text(f"❌ **Failed to create federation:** `{str(e)}`")

    # ============================================================
    # 🔗 JOIN FEDERATION (`/joinfed`)
    # ============================================================
    @app.on_message(filters.command("joinfed") & filters.group)
    async def join_fed_cmd(client, message: Message):
        # Admin validation
        user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_member.status not in ["creator", "administrator"] and message.from_user.id not in (DEV_LIST + [OWNER_ID]):
            return await message.reply_text("⚠️ **You must be an administrator to link this chat to a Federation!**")

        args = message.command
        if len(args) < 2:
            return await message.reply_text("❌ **Please provide the Federation ID! Example:** `/joinfed FED-101`")

        fed_id = args[1].upper().strip()
        fed = await db.feds.find_one({"fed_id": fed_id})

        if not fed:
            return await message.reply_text(f"❌ **Federation ID `{fed_id}` does not exist!**")

        try:
            await db.fed_chats.update_one(
                {"chat_id": message.chat.id},
                {"$set": {"fed_id": fed_id}},
                upsert=True
            )
            await message.reply_text(f"✅ **This group has been successfully linked to Federation:** `{fed['name']}` (`{fed_id}`)")
        except Exception as e:
            logger.error(f"[JoinFed Error]: {e}")
            await message.reply_text(f"❌ **Failed to join federation:** `{str(e)}`")

    # ============================================================
    # 🚪 LEAVE FEDERATION (`/leavefed`)
    # ============================================================
    @app.on_message(filters.command("leavefed") & filters.group)
    async def leave_fed_cmd(client, message: Message):
        user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_member.status not in ["creator", "administrator"] and message.from_user.id not in (DEV_LIST + [OWNER_ID]):
            return await message.reply_text("⚠️ **You must be an administrator to unlink this chat from its Federation!**")

        try:
            result = await db.fed_chats.delete_one({"chat_id": message.chat.id})
            if result.deleted_count > 0:
                await message.reply_text("🚪 **Successfully disconnected this group from the Federation.**")
            else:
                await message.reply_text("ℹ️ **This group is not currently part of any Federation.**")
        except Exception as e:
            logger.error(f"[LeaveFed Error]: {e}")
            await message.reply_text(f"❌ **Failed to leave federation:** `{str(e)}`")

    # ============================================================
    # 🔨 GLOBAL BAN (`/gban`)
    # ============================================================
    @app.on_message(filters.command("gban") & filters.group)
    async def gban_user_cmd(client, message: Message):
        chat_link = await db.fed_chats.find_one({"chat_id": message.chat.id})
        if not chat_link:
            return await message.reply_text("❌ **This group is not linked to any Federation!**")

        fed_id = chat_link["fed_id"]
        if not await is_fed_admin(message.from_user.id, fed_id):
            return await message.reply_text("❌ **You are not authorized to execute global bans in this Federation!**")

        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("❌ **Please reply to the user you want to globally ban!**")

        target_user = message.reply_to_message.from_user
        target_id = target_user.id

        if target_id in DEV_LIST or target_id == OWNER_ID:
            return await message.reply_text("⚠️ **You cannot globally ban a Developer or Bot Owner!**")

        try:
            fed = await db.feds.find_one({"fed_id": fed_id})
            gbanned_list = fed.get("gbanned", [])

            if target_id in gbanned_list:
                return await message.reply_text(f"ℹ️ **User `{target_id}` is already globally banned in this Federation.**")

            await db.feds.update_one(
                {"fed_id": fed_id},
                {"$push": {"gbanned": target_id}}
            )

            await message.reply_text(
                f"🔨 **Federation Global Ban Enforced**\n\n"
                f"• **User:** {target_user.mention} (`{target_id}`)\n"
                f"• **Federation:** `{fed['name']}` (`{fed_id}`)"
            )
        except Exception as e:
            logger.error(f"[GBan Error]: {e}")
            await message.reply_text(f"❌ **Failed to execute gban:** `{str(e)}`")

    # ============================================================
    # ♻️ UNGBAN (`/ungban`)
    # ============================================================
    @app.on_message(filters.command("ungban") & filters.group)
    async def ungban_user_cmd(client, message: Message):
        chat_link = await db.fed_chats.find_one({"chat_id": message.chat.id})
        if not chat_link:
            return await message.reply_text("❌ **This group is not linked to any Federation!**")

        fed_id = chat_link["fed_id"]
        if not await is_fed_admin(message.from_user.id, fed_id):
            return await message.reply_text("❌ **You are not authorized to unban users in this Federation!**")

        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("❌ **Please reply to the user you want to unban!**")

        target_user = message.reply_to_message.from_user
        target_id = target_user.id

        try:
            await db.feds.update_one(
                {"fed_id": fed_id},
                {"$pull": {"gbanned": target_id}}
            )

            await message.reply_text(
                f"♻️ **User Globally Unbanned**\n\n"
                f"• **User:** {target_user.mention} (`{target_id}`)\n"
                f"• **Federation ID:** `{fed_id}`"
            )
        except Exception as e:
            logger.error(f"[UnGBan Error]: {e}")
            await message.reply_text(f"❌ **Failed to execute ungban:** `{str(e)}`")

    # ============================================================
    # 🚫 AUTO-BAN ENFORCEMENT MIDDLEWARE
    # ============================================================
    @app.on_message(filters.group, group=2)
    async def enforce_gban_middleware(client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        try:
            chat_link = await db.fed_chats.find_one({"chat_id": chat_id})
            if not chat_link:
                return

            fed_id = chat_link["fed_id"]
            fed = await db.feds.find_one({"fed_id": fed_id})
            if not fed:
                return

            if user_id in fed.get("gbanned", []):
                await message.chat.ban_member(user_id)
                await message.reply_text(
                    f"🚫 **Federation Security Shield Triggered**\n\n"
                    f"• **User:** {message.from_user.mention} (`{user_id}`)\n"
                    f"• **Reason:** Globally Banned in Federation `{fed['name']}` (`{fed_id}`)"
                )
        except Exception as e:
            # Bot might lack ban permissions in group
            pass

    # ============================================================
    # 📊 FEDERATION INFO (`/fedinfo`)
    # ============================================================
    @app.on_message(filters.command("fedinfo"))
    async def fed_info_cmd(client, message: Message):
        fed_id = None

        if message.chat.type.name != "PRIVATE":
            chat_link = await db.fed_chats.find_one({"chat_id": message.chat.id})
            if chat_link:
                fed_id = chat_link["fed_id"]

        if not fed_id and len(message.command) > 1:
            fed_id = message.command[1].upper().strip()

        if not fed_id:
            return await message.reply_text("❌ **Please specify a Federation ID or use this command inside a linked group chat! Example:** `/fedinfo FED-101`")

        fed = await db.feds.find_one({"fed_id": fed_id})
        if not fed:
            return await message.reply_text(f"❌ **Federation ID `{fed_id}` not found!**")

        linked_chats_count = await db.fed_chats.count_documents({"fed_id": fed_id})
        gbanned_count = len(fed.get("gbanned", []))
        admins_count = len(fed.get("admins", []))

        info_text = (
            f"╔═══❰ 🌐 FEDERATION INFO ❱═══╗\n\n"
            f"🆔 **Fed ID:** `{fed_id}`\n"
            f"📛 **Name:** `{fed['name']}`\n"
            f"👑 **Owner ID:** `{fed['owner']}`\n"
            f"🛡 **Extra Admins:** `{admins_count}`\n"
            f"💬 **Linked Groups:** `{linked_chats_count}`\n"
            f"🚫 **Globally Banned Users:** `{gbanned_count}`\n\n"
            f"╚══════════════════════════╝"
        )

        await message.reply_text(info_text)
