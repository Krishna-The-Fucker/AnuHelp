# ============================================================
# 🔗 CONNECTIONS MODULE (ROSE STYLE GROUP MANAGEMENT VIA PM)
# ============================================================

__mod_name__ = "🔗 ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ"

__help__ = """
*🔗 ᴄᴏɴɴᴇᴄᴛɪᴏɴꜱ ᴍᴏᴅᴜʟᴇ* — Connect your private chat (PM) to a group to manage its settings remotely, just like MissRose!

• `/connect [chat_id / username]` — Connect your PM to a specific group.
• `/reconnect` — Automatically reconnect to your previously linked group.
• `/disconnect` — Disconnect from the currently linked group.
• `/connection` — Check which group you are currently connected to.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from db import db
import logging

logger = logging.getLogger("CONNECTIONS")

def register_connection_system(app):

    # ============================================================
    # 📌 HELPER: GET CURRENT CONNECTED CHAT FOR A USER
    # ============================================================
    async def get_user_connection(user_id: int):
        data = await db.connections.find_one({"user_id": user_id})
        return data.get("chat_id") if data else None

    # ============================================================
    # 🔗 CONNECT COMMAND (`/connect`)
    # ============================================================
    @app.on_message(filters.command("connect"))
    async def connect_cmd(client, message: Message):
        user_id = message.from_user.id
        args = message.command

        # Case 1: Used inside a group -> Generate button to connect via PM
        if message.chat.type in ["supergroup", "group"]:
            # Check if user is admin or creator
            try:
                member = await client.get_chat_member(message.chat.id, user_id)
                if member.status not in ["creator", "administrator"]:
                    return await message.reply("⚠️ **You must be an administrator to connect to this chat!**")
            except Exception:
                return await message.reply("⚠️ **Failed to verify your admin permissions.**")

            bot_username = (await client.get_me()).username
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Connect in PM", url=f"https://t.me/{bot_username}?start=connect_{message.chat.id}")]
            ])
            return await message.reply(
                f"📂 **Connection Setup for {message.chat.title}**\n\n"
                f"Click the button below to connect your private chat to this group and manage settings easily!",
                reply_markup=keyboard
            )

        # Case 2: Used in Private Chat (PM)
        if len(args) < 2:
            # List recent connections if no argument provided
            data = await db.connections.find_one({"user_id": user_id})
            current_conn = data.get("chat_id") if data else None
            if current_conn:
                try:
                    chat_info = await client.get_chat(current_conn)
                    return await message.reply(
                        f"🔗 **Current Connection:** `{chat_info.title}` (`{current_conn}`)\n\n"
                        f"Use `/disconnect` to disconnect, `/reconnect` to reconnect, or `/connect <chat_id>` to switch."
                    )
                except Exception:
                    pass
            return await message.reply("⚠️ **Please provide a group ID or username!**\nExample: `/connect -100123456789` or `/connect @GroupUsername`")

        target_input = args[1].strip()
        try:
            # Resolve chat id or username
            chat_obj = await client.get_chat(target_input)
            chat_id = chat_obj.id
            chat_title = chat_obj.title

            # Verify if user is admin in that chat
            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in ["creator", "administrator"]:
                return await message.reply("❌ **You are not an administrator in that chat!**")

            # Verify if bot is in that chat and has rights
            bot_member = await client.get_chat_member(chat_id, (await client.get_me()).id)
            if not bot_member:
                return await message.reply("❌ **I am not a member of that group! Add me first.**")

            # Save connection in DB
            await db.connections.update_one(
                {"user_id": user_id},
                {"$set": {"chat_id": chat_id, "title": chat_title}},
                upsert=True
            )

            await message.reply(f"✅ **Successfully connected to:** `{chat_title}` (`{chat_id}`)\nYou can now manage group settings directly from here!")

        except Exception as e:
            logger.error(f"[Connect Error]: {e}")
            await message.reply(f"❌ **Failed to connect:** `{str(e)}`\nMake sure the ID/username is correct and I am added as an admin in the group.")

    # ============================================================
    # 🔄 RECONNECT COMMAND (`/reconnect`)
    # ============================================================
    @app.on_message(filters.command("reconnect") & filters.private)
    async def reconnect_cmd(client, message: Message):
        user_id = message.from_user.id
        
        # Fetch last saved connection data from DB
        data = await db.connections.find_one({"user_id": user_id})
        if not data or not data.get("chat_id"):
            return await message.reply("ℹ️ **No previous connection found!** Use `/connect <chat_id>` or `/connect` inside a group first.")

        chat_id = data["chat_id"]
        
        try:
            # Re-verify chat existence and user admin status
            chat_obj = await client.get_chat(chat_id)
            chat_title = chat_obj.title

            member = await client.get_chat_member(chat_id, user_id)
            if member.status not in ["creator", "administrator"]:
                return await message.reply(f"❌ **Reconnection failed:** You are no longer an administrator in `{chat_title}`.")

            # Update the title just in case it changed
            await db.connections.update_one(
                {"user_id": user_id},
                {"$set": {"title": chat_title}},
                upsert=True
            )

            await message.reply(f"🔄 **Successfully reconnected to:** `{chat_title}` (`{chat_id}`)")

        except Exception as e:
            logger.error(f"[Reconnect Error]: {e}")
            await message.reply(f"❌ **Failed to reconnect:** `{str(e)}`\nMake sure I am still an admin in the target group.")

    # ============================================================
    # ❌ DISCONNECT COMMAND (`/disconnect`)
    # ============================================================
    @app.on_message(filters.command("disconnect") & filters.private)
    async def disconnect_cmd(client, message: Message):
        user_id = message.from_user.id
        result = await db.connections.delete_one({"user_id": user_id})
        if result.deleted_count > 0:
            await message.reply("🔌 **Successfully disconnected from the group.** Use `/reconnect` anytime to link back.")
        else:
            await message.reply("ℹ️ **You are not connected to any group currently.**")

    # ============================================================
    # 👀 VIEW CONNECTION COMMAND (`/connection`)
    # ============================================================
    @app.on_message(filters.command("connection") & filters.private)
    async def view_connection_cmd(client, message: Message):
        user_id = message.from_user.id
        chat_id = await get_user_connection(user_id)
        if not chat_id:
            return await message.reply("ℹ️ **You are not connected to any group.** Use `/connect` to link one.")

        try:
            chat_info = await client.get_chat(chat_id)
            await message.reply(f"🔗 **Connected Chat:** `{chat_info.title}` (`{chat_id}`)")
        except Exception:
            await message.reply(f"🔗 **Connected Chat ID:** `{chat_id}`")

    # ============================================================
    # 📥 START DEEP LINK HANDLER FOR CONNECTIONS (`/start connect_xxx`)
    # ============================================================
    @app.on_message(filters.command("start") & filters.private)
    async def connection_start_handler(client, message: Message):
        if len(message.command) > 1 and message.command[1].startswith("connect_"):
            try:
                chat_id = int(message.command[1].split("_")[1])
                user_id = message.from_user.id

                # Check admin status
                member = await client.get_chat_member(chat_id, user_id)
                if member.status not in ["creator", "administrator"]:
                    return await message.reply("❌ **You must be an administrator in the target group to connect!**")

                chat_obj = await client.get_chat(chat_id)
                await db.connections.update_one(
                    {"user_id": user_id},
                    {"$set": {"chat_id": chat_id, "title": chat_obj.title}},
                    upsert=True
                )

                await message.reply(f"✅ **Successfully connected to:** `{chat_obj.title}` (`{chat_id}`)\nYou can now manage group settings from your PM!")
            except Exception as e:
                logger.error(f"[Start Connect Error]: {e}")
                await message.reply(f"❌ **Connection failed:** `{str(e)}`")
