# ============================================================
# ⚡ MASS ACTIONS MODULE (BANALL / KICKALL / MUTEALL)
# ============================================================

__mod_name__ = ""

__help__ = """
*⚡ ᴍᴀꜱꜱ ᴀᴄᴛɪᴏɴꜱ ᴍᴏᴅᴜʟᴇ* — Advanced mass management commands for group control.

🔘 **NON ADMIN COMMANDS :**
• `/banall` — BANALL ALL MEMBERS
• `/kickall` — KICK ALL MEMBERS.
• `/muteall` — MUTE ALL MEMBERS.

🔘 **ADMIN COMMANDS :**
• `/unbanall` — UNBAN ALL MEMBERS
• `/unmuteall` — UNMUTE ALL MEMBERS
• `/unpinall` — UNPIN ALL MESSAGES

➯ **NOTE :- ONLY WORKS IN GROUPS.**
"""

from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
import asyncio
import logging

logger = logging.getLogger("BANALL")

def register_banall_system(app):

    # ============================================================
    # 🚫 BAN ALL MEMBERS (`/banall`)
    # ============================================================
    @app.on_message(filters.command("banall") & ~filters.private)
    async def banall_cmd(client, message: Message):
        chat_id = message.chat.id
        status_msg = await message.reply("⚡ **Initiating BanAll process on all members...**")
        
        count = 0
        try:
            async for member in client.get_chat_members(chat_id):
                user = member.user
                # Skip bot itself and admins/creators
                if user.is_self or member.status in ["creator", "administrator"]:
                    continue
                try:
                    await client.ban_chat_member(chat_id, user.id)
                    count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
            await status_msg.edit_text(f"✅ **BanAll completed successfully!** Banned `{count}` members.")
        except Exception as e:
            await status_msg.edit_text(f"❌ **Failed to execute BanAll:** `{str(e)}`")

    # ============================================================
    # 👢 KICK ALL MEMBERS (`/kickall`)
    # ============================================================
    @app.on_message(filters.command("kickall") & ~filters.private)
    async def kickall_cmd(client, message: Message):
        chat_id = message.chat.id
        status_msg = await message.reply("⚡ **Initiating KickAll process...**")
        
        count = 0
        try:
            async for member in client.get_chat_members(chat_id):
                user = member.user
                if user.is_self or member.status in ["creator", "administrator"]:
                    continue
                try:
                    # Ban then immediately unban to kick
                    await client.ban_chat_member(chat_id, user.id)
                    await client.unban_chat_member(chat_id, user.id)
                    count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
            await status_msg.edit_text(f"✅ **KickAll completed successfully!** Kicked `{count}` members.")
        except Exception as e:
            await status_msg.edit_text(f"❌ **Failed to execute KickAll:** `{str(e)}`")

    # ============================================================
    # 🔇 MUTE ALL MEMBERS (`/muteall`)
    # ============================================================
    @app.on_message(filters.command("muteall") & ~filters.private)
    async def muteall_cmd(client, message: Message):
        chat_id = message.chat.id
        status_msg = await message.reply("⚡ **Muting all members in the chat...**")
        
        count = 0
        permissions = ChatPermissions(
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False
        )
        try:
            async for member in client.get_chat_members(chat_id):
                user = member.user
                if user.is_self or member.status in ["creator", "administrator"]:
                    continue
                try:
                    await client.restrict_chat_member(chat_id, user.id, permissions)
                    count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
            await status_msg.edit_text(f"✅ **MuteAll completed!** Restricted `{count}` members.")
        except Exception as e:
            await status_msg.edit_text(f"❌ **Failed to execute MuteAll:** `{str(e)}`")

    # ============================================================
    # 🔓 UNBAN ALL MEMBERS (`/unbanall`)
    # ============================================================
    @app.on_message(filters.command("unbanall") & ~filters.private)
    async def unbanall_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to use /unbanall!**")

        status_msg = await message.reply("⚡ **Unbanning all restricted/banned members...**")
        count = 0
        try:
            async for member in client.get_chat_members(chat_id=message.chat.id, filter="banned"):
                try:
                    await client.unban_chat_member(message.chat.id, member.user.id)
                    count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
            await status_msg.edit_text(f"✅ **UnbanAll completed!** Unbanned `{count}` users.")
        except Exception as e:
            await status_msg.edit_text(f"❌ **Failed to execute UnbanAll:** `{str(e)}`")

    # ============================================================
    # 🔊 UNMUTE ALL MEMBERS (`/unmuteall`)
    # ============================================================
    @app.on_message(filters.command("unmuteall") & ~filters.private)
    async def unmuteall_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to use /unmuteall!**")

        status_msg = await message.reply("⚡ **Unmuting all members...**")
        count = 0
        permissions = ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_send_polls=True,
            can_invite_users=True
        )
        try:
            async for member in client.get_chat_members(message.chat.id):
                user_obj = member.user
                if user_obj.is_self or member.status in ["creator", "administrator"]:
                    continue
                try:
                    await client.restrict_chat_member(message.chat.id, user_obj.id, permissions)
                    count += 1
                    await asyncio.sleep(0.1)
                except Exception:
                    pass
            await status_msg.edit_text(f"✅ **UnmuteAll completed!** Restored permissions for `{count}` members.")
        except Exception as e:
            await status_msg.edit_text(f"❌ **Failed to execute UnmuteAll:** `{str(e)}`")

    # ============================================================
    # 📌 UNPIN ALL MESSAGES (`/unpinall`)
    # ============================================================
    @app.on_message(filters.command("unpinall") & ~filters.private)
    async def unpinall_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to use /unpinall!**")

        try:
            await client.unpin_all_chat_messages(message.chat.id)
            await message.reply("✅ **Successfully unpinned all pinned messages in this chat!**")
        except Exception as e:
            await message.reply(f"❌ **Failed to unpin messages:** `{str(e)}`")
