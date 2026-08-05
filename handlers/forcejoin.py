# ============================================================
# 📢 FORCE JOIN SYSTEM MODULE (CHANNEL MEMBERSHIP ENFORCEMENT)
# ============================================================

__mod_name__ = "📢 ꜰᴏʀᴄᴇ ᴊᴏɪɴ"

__help__ = """
*📢 ꜰᴏʀᴄᴇ ᴊᴏɪɴ ᴍᴏᴅᴜʟᴇ* — Require users to join your official update channel/group before they can chat or use the bot!

• `/setfjoin [channel_username/id]` — Enable and link a force-join channel.
• `/fjoin` — Check current force-join settings for the chat.
• `/delfjoin` — Disable and remove force-join enforcement.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant, ChatAdminRequired
from db import db
import logging

logger = logging.getLogger("FORCE_JOIN")

def register_forcejoin_system(app):

    # ============================================================
    # 🛡️ FORCE JOIN MIDDLEWARE (CHECK MEMBERSHIP ON MESSAGES)
    # ============================================================
    @app.on_message(filters.group & ~filters.service & ~filters.bot, group=1)
    async def force_join_middleware(client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id
        user_id = message.from_user.id

        try:
            # Fetch force-join configuration for this group
            fjoin_data = await db.force_join.find_one({"chat_id": chat_id})
            if not fjoin_data or not fjoin_data.get("enabled", False):
                return

            channel = fjoin_data["channel"]

            # Bypass check if user is chat admin or owner
            user_member = await client.get_chat_member(chat_id, user_id)
            if user_member.status in ["creator", "administrator"]:
                return

            # Check if user is a member of the target channel
            try:
                await client.get_chat_member(channel, user_id)
            except UserNotParticipant:
                # User has not joined the channel! Delete message and warn.
                try:
                    await message.delete()
                except Exception:
                    pass

                # Resolve channel invite link or username for button
                chat_info = await client.get_chat(channel)
                channel_name = chat_info.title or "Update Channel"
                channel_invite = chat_info.invite_link or f"https://t.me/{chat_info.username}" if chat_info.username else f"https://t.me/{channel}"

                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"🔔 Join {channel_name}", url=channel_invite)],
                    [InlineKeyboardButton("🔄 Verify Membership", callback_data=f"fjoin_verify_{user_id}")]
                ])

                warn_msg = await message.reply(
                    f"⚠️ **Hello {message.from_user.mention}!**\n\n"
                    f"You must join our official channel to send messages in this group.",
                    reply_markup=keyboard
                )
                
                message.stop_propagation()

        except Exception as e:
            logger.error(f"[ForceJoin Middleware Error]: {e}")

    # ============================================================
    # 🔘 CALLBACK QUERY HANDLER FOR VERIFICATION BUTTON
    # ============================================================
    @app.on_callback_query(filters.regex(r"^fjoin_verify_"))
    async def verify_force_join_callback(client, callback_query):
        data_parts = callback_query.data.split("_")
        target_user_id = int(data_parts[2])
        user_id = callback_query.from_user.id
        chat_id = callback_query.message.chat.id

        if user_id != target_user_id:
            return await callback_query.answer("⚠️ This button is not for you!", show_alert=True)

        try:
            fjoin_data = await db.force_join.find_one({"chat_id": chat_id})
            if not fjoin_data:
                return await callback_query.answer("❌ Force join is no longer active.", show_alert=True)

            channel = fjoin_data["channel"]
            
            # Recheck membership
            await client.get_chat_member(channel, user_id)
            
            # If successful, delete warning message
            await callback_query.message.delete()
            await callback_query.answer("✅ Verification successful! You can now chat.", show_alert=True)

        except UserNotParticipant:
            await callback_query.answer("❌ You still haven't joined the channel! Please join first.", show_alert=True)
        except Exception as e:
            logger.error(f"[ForceJoin Verify Error]: {e}")
            await callback_query.answer("❌ An error occurred during verification.", show_alert=True)

    # ============================================================
    # ⚙️ SET FORCE JOIN (`/setfjoin`)
    # ============================================================
    @app.on_message(filters.command("setfjoin") & filters.group)
    async def set_force_join_cmd(client, message: Message):
        user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_member.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to configure Force Join!**")

        args = message.command
        if len(args) < 2:
            return await message.reply("⚠️ **Please provide a channel username or ID! Example:** `/setfjoin @YourChannel`")

        channel = args[1].strip()

        try:
            # Test if bot has access/admin rights in target channel
            chat_info = await client.get_chat(channel)
            bot_member = await client.get_chat_member(channel, (await client.get_me()).id)
            if bot_member.status not in ["creator", "administrator"]:
                return await message.reply("❌ **Bot must be an administrator in the target channel with rights to add members/invite users!**")

            await db.force_join.update_one(
                {"chat_id": message.chat.id},
                {"$set": {"channel": channel, "enabled": True}},
                upsert=True
            )

            await message.reply(f"✅ **Force Join successfully enabled!** Linked channel: `{chat_info.title}` (`{channel}`)")

        except Exception as e:
            logger.error(f"[SetFJoin Error]: {e}")
            await message.reply(f"❌ **Failed to set force join channel:** `{str(e)}`\nMake sure the bot is an admin in that channel.")

    # ============================================================
    # 👀 VIEW FORCE JOIN STATUS (`/fjoin`)
    # ============================================================
    @app.on_message(filters.command("fjoin") & filters.group)
    async def view_force_join_cmd(client, message: Message):
        try:
            fjoin_data = await db.force_join.find_one({"chat_id": message.chat.id})
            if not fjoin_data or not fjoin_data.get("enabled", False):
                return await message.reply("ℹ️ **Force Join is currently disabled for this group.**")

            channel = fjoin_data["channel"]
            await message.reply(f"📢 **Active Force Join Channel:** `{channel}`")
        except Exception as e:
            logger.error(f"[ViewFJoin Error]: {e}")
            await message.reply(f"❌ **Failed to fetch settings:** `{str(e)}`")

    # ============================================================
    # ❌ DELETE FORCE JOIN (`/delfjoin`)
    # ============================================================
    @app.on_message(filters.command("delfjoin") & filters.group)
    async def delete_force_join_cmd(client, message: Message):
        user_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user_member.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to disable Force Join!**")

        try:
            result = await db.force_join.delete_one({"chat_id": message.chat.id})
            if result.deleted_count > 0:
                await message.reply("🗑️ **Force Join has been disabled and removed for this group.**")
            else:
                await message.reply("ℹ️ **Force Join was not configured in this chat.**")
        except Exception as e:
            logger.error(f"[DelFJoin Error]: {e}")
            await message.reply(f"❌ **Failed to disable force join:** `{str(e)}`")
