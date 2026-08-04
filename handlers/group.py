# ============================================================
# 👥 GROUP MANAGEMENT & UTILITIES SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "👥 ɢʀᴏᴜᴘ"

__help__ = """
*👥 ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ* — Essential administration tools to manage group settings and lock down chat permissions!

• `/lock <type>` — Lock specific chat permissions (e.g., `text`, `media`, `polls`, `all`)
• `/unlock <type>` — Unlock specific chat permissions
• `/settings` — View current group status and permission locks
• `/setphoto` — Reply to an image to set it as the group profile picture
• `/settitle <new title>` — Change the group title/name
• `/setdescription <description>` — Change the group description
"""

from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
from pyrogram.enums import ChatMemberStatus
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
