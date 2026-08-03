def register_userinfo(app):
    from pyrogram import filters
    from pyrogram.types import Message
    from pyrogram.enums import UserStatus

    @app.on_message(filters.command(["userinfo", "info", "whois"]) & (filters.group | filters.private))
    async def user_info_handler(client, message: Message):
        # Target user decide karna (Reply kiya ho ya username/id diya ho, warna khud ka info)
        user = None
        
        if message.reply_to_message:
            user = message.reply_to_message.from_user
        elif len(message.command) > 1:
            try:
                user_input = message.command[1]
                user = await client.get_users(user_input)
            except Exception:
                return await message.reply("❌ **User not found!** Please check the username or ID.")
        else:
            user = message.from_user

        if not user:
            return await message.reply("❌ **Unable to fetch user information.**")

        # Status formatting
        status_text = "Offline"
        if user.status == UserStatus.ONLINE:
            status_text = "🟢 Online"
        elif user.status == UserStatus.OFFLINE:
            status_text = "🔴 Offline"
        elif user.status == UserStatus.RECENTLY:
            status_text = "🟡 Recently"
        elif user.status == UserStatus.LONG_AGO:
            status_text = "⚫ A long time ago"

        # Full details fetch karna
        try:
            full_user = await client.get_chat(user.id)
            bio = full_user.bio or "Not Provided"
            common_chats = await client.get_common_chats(user.id)
            common_count = len(common_chats)
        except Exception:
            bio = "Hidden / Not Accessible"
            common_count = 0

        # Profile Photo check
        has_photo = bool(user.photo)

        info_msg = (
            f"👤 **User Information**\n\n"
            f"• **First Name:** {user.first_name or 'None'}\n"
            f"• **Last Name:** {user.last_name or 'None'}\n"
            f"• **Username:** {f'@{user.username}' if user.username else 'None'}\n"
            f"• **User ID:** `{user.id}`\n"
            f"• **DC ID:** `{user.dc_id or 'Unknown'}`\n"
            f"• **Profile Photo:** {'Yes 🖼️' if has_photo else 'No ❌'}\n"
            f"• **Status:** {status_text}\n"
            f"• **Bio:** {bio}\n"
            f"• **Common Groups:** {common_count}\n"
            f"• **Mention:** {user.mention('link')}"
        )

        # Agar profile pic hai toh photo ke sath send karna, warna text
        if has_photo:
            try:
                async for photo in client.get_chat_photos(user.id, limit=1):
                    await message.reply_photo(
                        photo.file_id,
                        caption=info_msg
                    )
                    return
            except Exception:
                pass

        await message.reply(info_msg)
