# ============================================================
# 👥 GROUP MANAGEMENT & UTILITIES SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "👥 ɢʀᴏᴜᴘ"

__help__ = """
*👥 ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ* — Essential administration tools to manage group settings, lock down chats, and fetch group information!

• `/lock <type>` — Lock specific chat permissions (e.g., `text`, `media`, `polls`, `all`)
• `/unlock <type>` — Unlock specific chat permissions
• `/settings` — View current group status and permission locks
• `/setphoto` — Reply to an image to set it as the group profile picture
• `/settitle <new title>` — Change the group title/name
• `/setdescription <description>` — Change the group description
• `/pin` — Reply to a message to pin it (with optional `loud` parameter)
• `/unpin` — Unpin the currently pinned message
• `/purge` — Reply to a message to delete all messages from that point onward
• `/promote` — Promote a user to group administrator
• `/demote` — Demote an administrator back to a regular member
"""

from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ChatType
import logging

def register_group_system(app, db):

    # ============================================================
    # 👑 ADMIN CHECK HELPER
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
    # 🔒 LOCK PERMISSIONS (`/lock`)
    # ============================================================
    @app.on_message(filters.command("lock") & filters.group)
    async def lock_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can lock chat permissions!**")

        if len(message.command) < 2:
            return await message.reply(
                "⚠️ **Please specify what to lock!**\n"
                "• Available options: `text`, `media`, `polls`, `invite`, `pins`, `all`"
            )

        target = message.command[1].lower()
        chat_id = message.chat.id

        try:
            chat = await client.get_chat(chat_id)
            perms = chat.permissions or ChatPermissions()

            # Map existing permissions to dict
            p_dict = {
                "can_send_messages": perms.can_send_messages,
                "can_send_media_messages": perms.can_send_media_messages,
                "can_send_polls": perms.can_send_polls,
                "can_invite_users": perms.can_invite_users,
                "can_pin_messages": perms.can_pin_messages,
                "can_add_web_page_previews": perms.can_add_web_page_previews
            }

            if target == "text":
                p_dict["can_send_messages"] = False
            elif target in ["media", "media_messages"]:
                p_dict["can_send_media_messages"] = False
            elif target == "polls":
                p_dict["can_send_polls"] = False
            elif target in ["invite", "invites"]:
                p_dict["can_invite_users"] = False
            elif target in ["pin", "pins"]:
                p_dict["can_pin_messages"] = False
            elif target == "all":
                for k in p_dict:
                    p_dict[k] = False
            else:
                return await message.reply("❌ **Invalid lock type!** Choose from: `text`, `media`, `polls`, `invite`, `pins`, `all`")

            await client.set_chat_permissions(chat_id, ChatPermissions(**p_dict))
            await message.reply(f"🔒 **Successfully locked `{target}` permissions in this group!**")

        except Exception as e:
            logging.error(f"[Group Lock Error]: {e}")
            await message.reply("❌ **Failed to update chat permissions. Make sure I have enough rights!**")

    # ============================================================
    # 🔓 UNLOCK PERMISSIONS (`/unlock`)
    # ============================================================
    @app.on_message(filters.command("unlock") & filters.group)
    async def unlock_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can unlock chat permissions!**")

        if len(message.command) < 2:
            return await message.reply(
                "⚠️ **Please specify what to unlock!**\n"
                "• Available options: `text`, `media`, `polls`, `invite`, `pins`, `all`"
            )

        target = message.command[1].lower()
        chat_id = message.chat.id

        try:
            chat = await client.get_chat(chat_id)
            perms = chat.permissions or ChatPermissions()

            p_dict = {
                "can_send_messages": perms.can_send_messages,
                "can_send_media_messages": perms.can_send_media_messages,
                "can_send_polls": perms.can_send_polls,
                "can_invite_users": perms.can_invite_users,
                "can_pin_messages": perms.can_pin_messages,
                "can_add_web_page_previews": perms.can_add_web_page_previews
            }

            if target == "text":
                p_dict["can_send_messages"] = True
            elif target in ["media", "media_messages"]:
                p_dict["can_send_media_messages"] = True
            elif target == "polls":
                p_dict["can_send_polls"] = True
            elif target in ["invite", "invites"]:
                p_dict["can_invite_users"] = True
            elif target in ["pin", "pins"]:
                p_dict["can_pin_messages"] = True
            elif target == "all":
                for k in p_dict:
                    p_dict[k] = True
            else:
                return await message.reply("❌ **Invalid unlock type!** Choose from: `text`, `media`, `polls`, `invite`, `pins`, `all`")

            await client.set_chat_permissions(chat_id, ChatPermissions(**p_dict))
            await message.reply(f"🔓 **Successfully unlocked `{target}` permissions in this group!**")

        except Exception as e:
            logging.error(f"[Group Unlock Error]: {e}")
            await message.reply("❌ **Failed to update chat permissions.**")

    # ============================================================
    # 📌 PIN MESSAGE (`/pin`)
    # ============================================================
    @app.on_message(filters.command("pin") & filters.group)
    async def pin_message_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can pin messages!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to the message you want to pin!**")

        loud = len(message.command) > 1 and message.command[1].lower() in ["loud", "notify", "all"]

        try:
            await client.pin_chat_message(
                chat_id=message.chat.id,
                message_id=message.reply_to_message.id,
                disable_notification=not loud
            )
            await message.reply(f"📌 **Message pinned successfully!** {'(Notified members)' if loud else ''}")
        except Exception as e:
            logging.error(f"[Pin Error]: {e}")
            await message.reply("❌ **Failed to pin message. Make sure I have pin permissions!**")

    # ============================================================
    # 📌 UNPIN MESSAGE (`/unpin`)
    # ============================================================
    @app.on_message(filters.command("unpin") & filters.group)
    async def unpin_message_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can unpin messages!**")

        try:
            if message.reply_to_message:
                await client.unpin_chat_message(message.chat.id, message.reply_to_message.id)
            else:
                await client.unpin_chat_message(message.chat.id)
            await message.reply("📌 **Message unpinned successfully!**")
        except Exception as e:
            logging.error(f"[Unpin Error]: {e}")
            await message.reply("❌ **Failed to unpin message.**")

    # ============================================================
    # 🧹 PURGE MESSAGES (`/purge`)
    # ============================================================
    @app.on_message(filters.command("purge") & filters.group)
    async def purge_messages_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can use purge!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to the message from which you want to start purging!**")

        chat_id = message.chat.id
        start_message_id = message.reply_to_message.id
        end_message_id = message.id

        try:
            message_ids = []
            for m_id in range(start_message_id, end_message_id + 1):
                message_ids.append(m_id)
                # Telegram allows batch deleting up to 100 messages at once
                if len(message_ids) == 100:
                    await client.delete_messages(chat_id, message_ids)
                    message_ids = []

            if message_ids:
                await client.delete_messages(chat_id, message_ids)

            status = await message.reply("🗑️ **Purge completed successfully!**")
            # Auto delete status confirmation after 3 seconds
            import asyncio
            await asyncio.sleep(3)
            await status.delete()
        except Exception as e:
            logging.error(f"[Purge Error]: {e}")
            await message.reply("❌ **Failed to purge messages. Messages might be too old (>48 hours)!**")

    # ============================================================
    # 👑 PROMOTE ADMIN (`/promote`)
    # ============================================================
    @app.on_message(filters.command("promote") & filters.group)
    async def promote_user_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can promote members!**")

        user_to_promote = None
        if message.reply_to_message and message.reply_to_message.from_user:
            user_to_promote = message.reply_to_message.from_user
        elif len(message.command) > 1:
            query = message.command[1].strip()
            try:
                if query.isdigit():
                    user_to_promote = await client.get_users(int(query))
                else:
                    user_to_promote = await client.get_users(query)
            except Exception:
                pass

        if not user_to_promote:
            return await message.reply("⚠️ **Please reply to a user or provide their username/ID to promote!**")

        try:
            await client.promote_chat_member(
                chat_id=message.chat.id,
                user_id=user_to_promote.id,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True
            )
            await message.reply(f"👑 **Successfully promoted {user_to_promote.mention} to Administrator!** ✨")
        except Exception as e:
            logging.error(f"[Promote Error]: {e}")
            await message.reply("❌ **Failed to promote user. Check my admin rights!**")

    # ============================================================
    # 📉 DEMOTE ADMIN (`/demote`)
    # ============================================================
    @app.on_message(filters.command("demote") & filters.group)
    async def demote_user_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can demote members!**")

        user_to_demote = None
        if message.reply_to_message and message.reply_to_message.from_user:
            user_to_demote = message.reply_to_message.from_user
        elif len(message.command) > 1:
            query = message.command[1].strip()
            try:
                if query.isdigit():
                    user_to_demote = await client.get_users(int(query))
                else:
                    user_to_demote = await client.get_users(query)
            except Exception:
                pass

        if not user_to_demote:
            return await message.reply("⚠️ **Please reply to an admin or provide their username/ID to demote!**")

        try:
            await client.promote_chat_member(
                chat_id=message.chat.id,
                user_id=user_to_demote.id,
                can_delete_messages=False,
                can_manage_video_chats=False,
                can_restrict_members=False,
                can_invite_users=False,
                can_pin_messages=False,
                can_promote_members=False
            )
            await message.reply(f"📉 **Successfully demoted {user_to_demote.mention} back to a regular member.**")
        except Exception as e:
            logging.error(f"[Demote Error]: {e}")
            await message.reply("❌ **Failed to demote user.**")
