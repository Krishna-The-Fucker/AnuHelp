# ============================================================
# 🛡️ ADVANCED ADMINISTRATION & GROUP MANAGEMENT MODULE
# ============================================================

__mod_name__ = "🛡️ ᴀᴅᴍɪɴ"

__help__ = """
*🛡️ ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs* — Powerful group administration tools to manage users, moderation, and chat security seamlessly.

• `/ban` — Ban a user from the group.
• `/unban` — Unban a user from the group.
• `/kick` — Kick a user from the group.
• `/mute` — Mute a user in the group.
• `/unmute` — Unmute a user in the group.
• `/pin` — Pin a message in the chat.
• `/unpin` — Unpin a message in the chat.
• `/promote` — Promote a user to group administrator.
• `/demote` — Demote an administrator back to regular user.
• `/staff` or `/admins` — List all group administrators.
"""

from pyrogram import filters
from pyrogram.types import Message, ChatPermissions
import logging

def register_admin_system(app):

    # Helper function to check if user is admin/creator and bot has rights
    async def check_admin_rights(message: Message, perm_attr: str = None):
        if message.chat.type.value == "private":
            await message.reply("⚠️ **This command can only be used in groups!**")
            return False

        # Check bot permissions
        bot_member = await message.chat.get_member(app.me.id)
        if not bot_member.status in ["administrator", "creator"]:
            await message.reply("❌ **I need to be an administrator with proper permissions to execute this command!**")
            return False

        if perm_attr and not getattr(bot_member, perm_attr, False):
            await message.reply(f"❌ **I don't have the required permission (`{perm_attr}`) to perform this action!**")
            return False

        # Check user permissions
        user = await message.chat.get_member(message.from_user.id)
        if user.status not in ["administrator", "creator"]:
            await message.reply("⚠️ **Only group administrators can use this command!**")
            return False

        return True

    # ============================================================
    # 🔨 BAN USER (`/ban`)
    # ============================================================
    @app.on_message(filters.command("ban") & ~filters.private)
    async def ban_user_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_restrict_members"):
            return

        user_id, reason = None, "No reason provided"
        if message.reply_to_message and message.reply_to_message.from_user:
            user_id = message.reply_to_message.from_user.id
            if len(message.command) > 1:
                reason = " ".join(message.command[1:])
        elif len(message.command) > 1:
            try:
                user_id = int(message.command[1])
                if len(message.command) > 2:
                    reason = " ".join(message.command[2:])
            except ValueError:
                user_id = message.command[1] # Username or mention

        if not user_id:
            return await message.reply("⚠️ **Please reply to a user or provide their username/ID to ban!**")

        try:
            target = await client.get_users(user_id)
            await message.chat.ban_member(target.id)
            await message.reply(
                f"🔨 **User Banned Successfully!**\n\n"
                f"• **User:** {target.mention} (`{target.id}`)\n"
                f"• **Reason:** `{reason}`"
            )
        except Exception as e:
            logging.error(f"[Ban Error]: {e}")
            await message.reply(f"❌ **Failed to ban user:** `{str(e)}`")

    # ============================================================
    # 🔓 UNBAN USER (`/unban`)
    # ============================================================
    @app.on_message(filters.command("unban") & ~filters.private)
    async def unban_user_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_restrict_members"):
            return

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("⚠️ **Please reply to a user or provide their ID/username to unban!**")

        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]

        try:
            target = await client.get_users(user_id)
            await message.chat.unban_member(target.id)
            await message.reply(f"🔓 **User Unbanned:** {target.mention} (`{target.id}`) can now join the group again.")
        except Exception as e:
            logging.error(f"[Unban Error]: {e}")
            await message.reply(f"❌ **Failed to unban user:** `{str(e)}`")

    # ============================================================
    # 🥾 KICK USER (`/kick`)
    # ============================================================
    @app.on_message(filters.command("kick") & ~filters.private)
    async def kick_user_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_restrict_members"):
            return

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("⚠️ **Please reply to a user or provide their username/ID to kick!**")

        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]

        try:
            target = await client.get_users(user_id)
            # Kick by banning then immediately unbanning
            await message.chat.ban_member(target.id)
            await message.chat.unban_member(target.id)
            await message.reply(f"🥾 **User Kicked:** {target.mention} (`{target.id}`) has been removed from the group.")
        except Exception as e:
            logging.error(f"[Kick Error]: {e}")
            await message.reply(f"❌ **Failed to kick user:** `{str(e)}`")

    # ============================================================
    # 🔇 MUTE USER (`/mute`)
    # ============================================================
    @app.on_message(filters.command("mute") & ~filters.private)
    async def mute_user_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_restrict_members"):
            return

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("⚠️ **Please reply to a user or provide their ID/username to mute!**")

        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]
        reason = " ".join(message.command[2:]) if message.reply_to_message and len(message.command) > 1 else " ".join(message.command[2:]) or "No reason provided"

        try:
            target = await client.get_users(user_id)
            await message.chat.restrict_member(target.id, ChatPermissions(can_send_messages=False))
            await message.reply(
                f"🔇 **User Muted Successfully!**\n\n"
                f"• **User:** {target.mention} (`{target.id}`)\n"
                f"• **Reason:** `{reason}`"
            )
        except Exception as e:
            logging.error(f"[Mute Error]: {e}")
            await message.reply(f"❌ **Failed to mute user:** `{str(e)}`")

    # ============================================================
    # 🔊 UNMUTE USER (`/unmute`)
    # ============================================================
    @app.on_message(filters.command("unmute") & ~filters.private)
    async def unmute_user_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_restrict_members"):
            return

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("⚠️ **Please reply to a user or provide their ID/username to unmute!**")

        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]

        try:
            target = await client.get_users(user_id)
            await message.chat.restrict_member(
                target.id,
                ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            await message.reply(f"🔊 **User Unmuted:** {target.mention} (`{target.id}`) can speak again.")
        except Exception as e:
            logging.error(f"[Unmute Error]: {e}")
            await message.reply(f"❌ **Failed to unmute user:** `{str(e)}`")

    # ============================================================
    # 📌 PIN & UNPIN MESSAGES (`/pin`, `/unpin`)
    # ============================================================
    @app.on_message(filters.command("pin") & ~filters.private)
    async def pin_message_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_pin_messages"):
            return

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to the message you want to pin!**")

        try:
            disable_notification = "loud" not in message.text.lower()
            await message.reply_to_message.pin(disable_notification=disable_notification)
            await message.reply("📌 **Message pinned successfully!**")
        except Exception as e:
            logging.error(f"[Pin Error]: {e}")
            await message.reply(f"❌ **Failed to pin message:** `{str(e)}`")

    @app.on_message(filters.command("unpin") & ~filters.private)
    async def unpin_message_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_pin_messages"):
            return

        try:
            if message.reply_to_message:
                await message.reply_to_message.unpin()
            else:
                await message.chat.unpin_all_messages()
            await message.reply("📌 **Message(s) unpinned successfully!**")
        except Exception as e:
            logging.error(f"[Unpin Error]: {e}")
            await message.reply(f"❌ **Failed to unpin message:** `{str(e)}`")

    # ============================================================
    # 👑 PROMOTE & DEMOTE (`/promote`, `/demote`)
    # ============================================================
    @app.on_message(filters.command("promote") & ~filters.private)
    async def promote_user_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_promote_members"):
            return

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("⚠️ **Please reply to a user or provide their ID/username to promote!**")

        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]
        title = "Admin" if len(message.command) <= 2 or message.reply_to_message else " ".join(message.command[2:])

        try:
            target = await client.get_users(user_id)
            await message.chat.promote_member(
                target.id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_manage_video_chats=True
            )
            await message.set_administrator_title(target.id, title)
            await message.reply(f"👑 **User Promoted:** {target.mention} is now an administrator with title `{title}`!")
        except Exception as e:
            logging.error(f"[Promote Error]: {e}")
            await message.reply(f"❌ **Failed to promote user:** `{str(e)}`")

    @app.on_message(filters.command("demote") & ~filters.private)
    async def demote_user_cmd(client, message: Message):
        if not await check_admin_rights(message, "can_promote_members"):
            return

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply("⚠️ **Please reply to a user or provide their ID/username to demote!**")

        user_id = message.reply_to_message.from_user.id if message.reply_to_message else message.command[1]

        try:
            target = await client.get_users(user_id)
            await message.chat.promote_member(
                target.id,
                can_change_info=False,
                can_delete_messages=False,
                can_invite_users=False,
                can_restrict_members=False,
                can_pin_messages=False,
                can_manage_video_chats=False
            )
            await message.reply(f"📉 **User Demoted:** {target.mention} is no longer an administrator.")
        except Exception as e:
            logging.error(f"[Demote Error]: {e}")
            await message.reply(f"❌ **Failed to demote user:** `{str(e)}`")

    # ============================================================
    # 👥 LIST ADMINS (`/staff` or `/admins`)
    # ============================================================
    @app.on_message(filters.command(["staff", "admins"]) & ~filters.private)
    async def list_admins_cmd(client, message: Message):
        try:
            creators = []
            admins = []
            async for member in message.chat.get_members(filter="administrators"):
                if member.status == "creator":
                    creators.append(member.user.mention)
                else:
                    admins.append(member.user.mention)

            creator_str = ", ".join(creators) if creators else "None"
            admin_str = "\n".join([f"• {a}" for a in admins]) if admins else "No additional admins."

            await message.reply(
                f"🛡️ **Group Administrators — {message.chat.title}**\n\n"
                f"👑 **Creator:**\n• {creator_str}\n\n"
                f"🛡️ **Administrators:**\n{admin_str}"
            )
        except Exception as e:
            logging.error(f"[Staff Error]: {e}")
            await message.reply(f"❌ **Failed to fetch group staff list:** `{str(e)}`")
