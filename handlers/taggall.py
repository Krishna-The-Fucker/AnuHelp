def register_taggall(app, db, LOG_CHANNEL):

    from pyrogram import filters
    from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
    from pyrogram.enums import ChatMemberStatus
    import asyncio

    # Active tag tasks ko track karne ke liye dictionary (Stop button ke liye)
    ACTIVE_TAGS = {}

    # =========================
    # ADMIN CHECK
    # =========================
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
    # TAGALL COMMAND
    # =========================
    @app.on_message(filters.command(["tagall", "mention"]) & filters.group)
    async def tag_all_users(client, message: Message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        # 1. Admin Verification
        if not await is_admin(client, chat_id, user_id):
            return await message.reply("❌ **Only admins can use this command!**")

        # 2. Check if already tagging is running in this chat
        if ACTIVE_TAGS.get(chat_id):
            return await message.reply("⚠️ **A tagall process is already running in this group! Use /canceltag to stop it.**")

        # 3. Extract custom reason/message if provided
        # Format: /tagall Good morning everyone!
        input_text = message.text.split(None, 1)
        custom_msg = input_text[1] if len(input_text) > 1 else "Hey everyone! 👋"

        status_msg = await message.reply("🔄 **Fetching group members...**")

        try:
            # Members collect karna
            members = []
            async for member in client.get_chat_members(chat_id):
                # Bots aur deleted accounts ko chhod kar sirf real users ko tag karna
                if not member.user.is_bot and not member.user.is_deleted:
                    members.append(member.user)

            if not members:
                return await status_msg.edit_text("❌ **No members found to tag!**")

            ACTIVE_TAGS[chat_id] = True
            await status_msg.edit_text(
                f"🚀 **Tagging started!** Total members: {len(members)}\n\n"
                f"📝 **Message:** {custom_msg}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🛑 Stop Tagging", callback_data="stop_tagall")]
                ])
            )

            # Log send karna
            try:
                await client.send_message(
                    LOG_CHANNEL,
                    f"📢 **TagAll Started**\nChat: {message.chat.title} (`{chat_id}`)\nBy: {message.from_user.mention}"
                )
            except:
                pass

            # Batch wise tagging (FloodWait se bachne ke liye)
            # Ek baar mein 5 members ko mention karke loop chalana best rehta hai
            batch_size = 5
            tagged_count = 0

            for i in range(0, len(members), batch_size):
                if not ACTIVE_TAGS.get(chat_id):
                    break # Agar cancel hua ho toh loop tod do

                batch = members[i:i + batch_size]
                mentions = " ".join([user.mention for user in batch])
                
                text = f"{custom_msg}\n\n{mentions}"
                
                try:
                    await client.send_message(chat_id, text)
                    tagged_count += len(batch)
                    await asyncio.sleep(3) # Floodwait protection delay
                except Exception as e:
                    print(f"[TagAll Error] {e}")
                    await asyncio.sleep(5)

            # Complete hone par
            if ACTIVE_TAGS.get(chat_id):
                ACTIVE_TAGS.pop(chat_id, None)
                await client.send_message(chat_id, f"✅ **Tagging completed successfully!** Tagged {tagged_count} members.")
                try:
                    await status_msg.delete()
                except:
                    pass

        except Exception as e:
            ACTIVE_TAGS.pop(chat_id, None)
            await status_msg.edit_text(f"❌ **An error occurred:** `{str(e)}`")

    # =========================
    # STOP / CANCEL COMMAND
    # =========================
    @app.on_message(filters.command(["canceltag", "stoptag"]) & filters.group)
    async def cancel_tagging(client, message: Message):
        chat_id = message.chat.id
        
        if not await is_admin(client, chat_id, message.from_user.id):
            return await message.reply("❌ **Only admins can stop tagging!**")

        if chat_id in ACTIVE_TAGS:
            ACTIVE_TAGS[chat_id] = False
            ACTIVE_TAGS.pop(chat_id, None)
            await message.reply("🛑 **Tagging process has been stopped successfully!**")
        else:
            await message.reply("⚠️ **No active tagging process is running in this chat.**")

    # =========================
    # CALLBACK QUERY (STOP BUTTON)
    # =========================
    @app.on_callback_query(filters.regex("^stop_tagall$"))
    async def stop_tag_callback(client, query: CallbackQuery):
        chat_id = query.message.chat.id

        if not await is_admin(client, chat_id, query.from_user.id):
            return await query.answer("❌ Only admins can stop this!", show_alert=True)

        if chat_id in ACTIVE_TAGS:
            ACTIVE_TAGS[chat_id] = False
            ACTIVE_TAGS.pop(chat_id, None)
            await query.message.edit_text("🛑 **Tagging process was stopped by admin.**")
            await query.answer("Stopped successfully!", show_alert=True)
        else:
            await query.answer("No active process found!", show_alert=True)
