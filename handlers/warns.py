def register_warns(app, db, LOG_CHANNEL):
    from pyrogram import filters
    from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
    from pyrogram.enums import ChatMemberStatus
    from datetime import datetime

    # Default settings agar database mein na ho
    DEFAULT_WARN_LIMIT = 3
    DEFAULT_ACTION = "ban" # ban, mute, kick

    async def is_admin(client, chat_id, user_id):
        try:
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except:
            return False

    # =========================
    # DB HELPERS FOR WARNS
    # =========================
    async def get_warn_settings(chat_id):
        data = await db.warn_settings.find_one({"chat_id": chat_id})
        if not data:
            return {"limit": DEFAULT_WARN_LIMIT, "action": DEFAULT_ACTION}
        return data

    async def set_warn_limit_db(chat_id, limit):
        await db.warn_settings.update_one(
            {"chat_id": chat_id},
            {"$set": {"limit": limit}},
            upsert=True
        )

    async def set_warn_action_db(chat_id, action):
        await db.warn_settings.update_one(
            {"chat_id": chat_id},
            {"$set": {"action": action}},
            upsert=True
        )

    # =========================
    # /WARN COMMAND
    # =========================
    @app.on_message(filters.command("warn") & filters.group)
    async def warn_user(client, message: Message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if not await is_admin(client, chat_id, user_id):
            return await message.reply("❌ **Only admins can use the warn command!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to a user's message to warn them!**")

        target_user = message.reply_to_message.from_user
        target_id = target_user.id

        # Admins ko warn na kiya ja sake
        if await is_admin(client, chat_id, target_id):
            return await message.reply("❌ **You cannot warn an administrator!**")

        # Custom reason extract karna
        input_text = message.text.split(None, 1)
        reason = input_text[1] if len(input_text) > 1 else "No reason provided."

        # Database mein warn count badhana
        data = await db.warns.find_one({"chat_id": chat_id, "user_id": target_id})
        count = data.get("count", 0) + 1 if data else 1

        await db.warns.update_one(
            {"chat_id": chat_id, "user_id": target_id},
            {"$set": {"count": count, "updated": datetime.utcnow()}},
            upsert=True
        )

        settings = await get_warn_settings(chat_id)
        limit = settings["limit"]
        action = settings["action"]

        warn_text = (
            f"⚠️ **User Warned!**\n\n"
            f"• **User:** {target_user.mention}\n"
            f"• **Admin:** {message.from_user.mention}\n"
            f"• **Warnings:** `{count}/{limit}`\n"
            f"• **Reason:** {reason}"
        )

        # Agar limit cross ho jaye
        if count >= limit:
            try:
                if action == "ban":
                    await client.ban_chat_member(chat_id, target_id)
                    warn_text += f"\n\n🚨 **Limit reached! User has been BANNED.**"
                elif action == "mute":
                    from pyrogram.types import ChatPermissions
                    await client.restrict_chat_member(chat_id, target_id, ChatPermissions(can_send_messages=False))
                    warn_text += f"\n\n🚨 **Limit reached! User has been MUTED.**"
                elif action == "kick":
                    await client.ban_chat_member(chat_id, target_id)
                    await client.unban_chat_member(chat_id, target_id)
                    warn_text += f"\n\n🚨 **Limit reached! User has been KICKED.**"
                
                # Warn count reset karna action ke baad
                await db.warns.delete_one({"chat_id": chat_id, "user_id": target_id})
            except Exception as e:
                warn_text += f"\n\n❌ **Failed to execute action:** `{e}`"

        await message.reply(
            warn_text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Reset Warnings", callback_data=f"reset_warns_{target_id}")]
            ])
        )

        # Log channel par send karna
        try:
            await client.send_message(
                LOG_CHANNEL,
                f"⚠️ **New Warning Issued**\nChat: {message.chat.title} (`{chat_id}`)\nTarget: {target_user.mention}\nCount: `{count}/{limit}`"
            )
        except:
            pass

    # =========================
    # /UNWARN COMMAND
    # =========================
    @app.on_message(filters.command("unwarn") & filters.group)
    async def unwarn_user(client, message: Message):
        chat_id = message.chat.id
        if not await is_admin(client, chat_id, message.from_user.id):
            return await message.reply("❌ **Only admins can use this!**")

        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to the user you want to unwarn!**")

        target_id = message.reply_to_message.from_user.id

        data = await db.warns.find_one({"chat_id": chat_id, "user_id": target_id})
        if not data or data.get("count", 0) == 0:
            return await message.reply("ℹ️ **This user has no warnings.**")

        new_count = max(0, data["count"] - 1)
        if new_count == 0:
            await db.warns.delete_one({"chat_id": chat_id, "user_id": target_id})
        else:
            await db.warns.update_one({"chat_id": chat_id, "user_id": target_id}, {"$set": {"count": new_count}})

        await message.reply(f"✅ **Warning removed!** Current warnings for user: `{new_count}`")

    # =========================
    # /WARNINGS COMMAND (CHECK)
    # =========================
    @app.on_message(filters.command(["warnings", "warns"]) & filters.group)
    async def check_warns(client, message: Message):
        chat_id = message.chat.id
        target_user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
        
        data = await db.warns.find_one({"chat_id": chat_id, "user_id": target_user.id})
        count = data.get("count", 0) if data else 0
        settings = await get_warn_settings(chat_id)

        await message.reply(f"📊 **Warning Status**\n\n• **User:** {target_user.mention}\n• **Warnings:** `{count}/{settings['limit']}`\n• **Action on limit:** `{settings['action'].upper()}`")

    # =========================
    # /SETWARNLIMIT & /SETWARNACTION
    # =========================
    @app.on_message(filters.command("setwarnlimit") & filters.group)
    async def set_warn_limit_cmd(client, message: Message):
        chat_id = message.chat.id
        if not await is_admin(client, chat_id, message.from_user.id):
            return await message.reply("❌ **Only admins can change settings!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Usage:** `/setwarnlimit 3` (Enter a number between 1 and 10)")

        try:
            limit = int(message.command[1])
            if not (1 <= limit <= 10):
                raise ValueError()
        except:
            return await message.reply("❌ **Invalid limit!** Please provide a number between 1 and 10.")

        await set_warn_limit_db(chat_id, limit)
        await message.reply(f"✅ **Warn limit updated successfully to:** `{limit}`")

    @app.on_message(filters.command("setwarnaction") & filters.group)
    async def set_warn_action_cmd(client, message: Message):
        chat_id = message.chat.id
        if not await is_admin(client, chat_id, message.from_user.id):
            return await message.reply("❌ **Only admins can change settings!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Usage:** `/setwarnaction ban` (Options: `ban`, `mute`, `kick`)")

        action = message.command[1].lower()
        if action not in ["ban", "mute", "kick"]:
            return await message.reply("❌ **Invalid action!** Choose from: `ban`, `mute`, `kick`")

        await set_warn_action_db(chat_id, action)
        await message.reply(f"✅ **Warn action updated successfully to:** `{action.upper()}`")

    # =========================
    # CALLBACK HANDLER (RESET BUTTON)
    # =========================
    @app.on_callback_query(filters.regex("^reset_warns_"))
    async def reset_warns_callback(client, query: CallbackQuery):
        chat_id = query.message.chat.id
        if not await is_admin(client, chat_id, query.from_user.id):
            return await query.answer("❌ Only admins can do this!", show_alert=True)

        target_id = int(query.data.split("_")[2])
        await db.warns.delete_one({"chat_id": chat_id, "user_id": target_id})
        
        await query.message.edit_text("✅ **All warnings for this user have been reset by admin.**")
        await query.answer("Warnings reset successfully!", show_alert=True)
