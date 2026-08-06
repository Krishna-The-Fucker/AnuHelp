# ============================================================
# 🔒 LOCK SYSTEM (ROSE STYLE & FULL POWER)
# ============================================================

__mod_name__ = "🔒 ʟᴏᴄᴋs"

__help__ = """
*🔒 ʟᴏᴄᴋs ᴍᴏᴅᴜʟᴇ* — Lock specific items, media types, links, or contents so only admins can use them!

Admin commands:
• `/lock <item(s)>` — Lock one or more items. Now, only admins can use this type!
• `/unlock <item(s)>` — Unlock one or more items. Everyone can use this type again!
• `/locks` — List currently locked items.
• `/lockwarns <yes/no/on/off>` — Enable or disable whether a user should be warned when using a locked item.
• `/locktypes` — Show the list of all lockable items.
• `/allowlist <url/id/command/@username(s)>` — Allowlist a URL, group ID, channel @, bot @, command, cashtag, or stickerpack link to stop them being deleted by locks. Separate with a space to add multiple items. If no arguments are given, returns the current allowlist.
• `/rmallowlist <url/id/@channelname(s)>` — Remove an item from the allowlist. Separate with a space to remove multiple items.
• `/rmallowlistall` — Remove all allowlisted items.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ChatMemberStatus
import re

LOCK_TYPES = [
    "all", "media", "photo", "video", "audio", "voice",
    "document", "sticker", "gif", "animation",
    "link", "url", "forward", "bots", "bot",
    "inline", "game", "location", "contact",
    "poll", "service", "text", "hashtag"
]

def register_lock_system(app, db):

    async def is_admin(client, chat_id, user_id):
        if not user_id:
            return False
        try:
            member = await client.get_chat_member(chat_id, user_id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except:
            return False

    async def set_lock(chat_id: int, lock_type: str, status: bool):
        await db.locks.update_one(
            {"chat_id": chat_id},
            {"$set": {lock_type: status}},
            upsert=True
        )

    async def get_locks(chat_id: int) -> dict:
        data = await db.locks.find_one({"chat_id": chat_id})
        return data if data else {}

    # ============================================================
    # 🔒 LOCK COMMAND (`/lock <item(s)>`)
    # ============================================================
    @app.on_message(filters.command("lock") & filters.group)
    async def lock_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        if len(message.command) < 2:
            return await message.reply_text(
                "❌ **Incorrect usage!**\n"
                "• Usage: `/lock <item>`\n"
                "• Example: `/lock link` or `/lock sticker`"
            )

        items = message.command[1:]
        chat_id = message.chat.id
        locked_successfully = []
        invalid_items = []

        for lock_type in items:
            lock_type = lock_type.lower()
            if lock_type not in LOCK_TYPES:
                invalid_items.append(lock_type)
            else:
                await set_lock(chat_id, lock_type, True)
                locked_successfully.append(lock_type)

        response_text = ""
        if locked_successfully:
            response_text += f"🔒 **Locked Successfully:** `{', '.join(locked_successfully)}` 🟢\n"
        if invalid_items:
            response_text += f"❌ **Invalid lock type(s):** `{', '.join(invalid_items)}`. Use `/locktypes` to view all valid types."

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(response_text.strip(), reply_markup=back_markup)

    # ============================================================
    # 🔓 UNLOCK COMMAND (`/unlock <item(s)>`)
    # ============================================================
    @app.on_message(filters.command("unlock") & filters.group)
    async def unlock_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        if len(message.command) < 2:
            return await message.reply_text(
                "❌ **Incorrect usage!**\n"
                "• Usage: `/unlock <item>`\n"
                "• Example: `/unlock link`"
            )

        items = message.command[1:]
        chat_id = message.chat.id
        unlocked_successfully = []
        invalid_items = []

        for lock_type in items:
            lock_type = lock_type.lower()
            if lock_type not in LOCK_TYPES:
                invalid_items.append(lock_type)
            else:
                await set_lock(chat_id, lock_type, False)
                unlocked_successfully.append(lock_type)

        response_text = ""
        if unlocked_successfully:
            response_text += f"🔓 **Unlocked Successfully:** `{', '.join(unlocked_successfully)}` 🔴\n"
        if invalid_items:
            response_text += f"❌ **Invalid lock type(s):** `{', '.join(invalid_items)}`"

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(response_text.strip(), reply_markup=back_markup)

    # ============================================================
    # 📋 LIST LOCK TYPES (`/locktypes`)
    # ============================================================
    @app.on_message(filters.command("locktypes") & filters.group)
    async def locktypes_cmd(client, message: Message):
        formatted_types = ", ".join([f"`{lt}`" for lt in LOCK_TYPES])
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(
            f"📋 **All Lockable Items:**\n\n{formatted_types}\n\n"
            f"Use `/lock <item>` to lock any of these.",
            reply_markup=back_markup
        )

    # ============================================================
    # 📊 LOCK STATUS PANEL (`/locks`)
    # ============================================================
    @app.on_message(filters.command("locks") & filters.group)
    async def locks_status(client, message: Message):
        data = await get_locks(message.chat.id)

        text = "🔒 **Current Locked Items in this chat:**\n\n"
        active_locks = [lock for lock in LOCK_TYPES if data.get(lock)]

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if not active_locks:
            return await message.reply_text("🔓 **No items are currently locked in this chat.**", reply_markup=back_markup)

        for lock in active_locks:
            text += f"• `{lock}`\n"

        text += "\n_Use `/lock <item>` or `/unlock <item>` to change settings._"
        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # ⚠️ TOGGLE LOCK WARNS (`/lockwarns <yes/no/on/off>`)
    # ============================================================
    @app.on_message(filters.command("lockwarns") & filters.group)
    async def lockwarns_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        args = message.command
        chat_id = message.chat.id
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if len(args) < 2:
            setting = await db.lockwarns.find_one({"chat_id": chat_id})
            status = setting.get("enabled", False) if setting else False
            return await message.reply_text(
                f"ℹ️ **Lock warns status:** `{'Enabled' if status else 'Disabled'}`\n"
                "Use `/lockwarns on` or `/lockwarns off` to change.",
                reply_markup=back_markup
            )

        choice = args[1].lower()
        if choice in ["yes", "on", "true"]:
            status = True
        elif choice in ["no", "off", "false"]:
            status = False
        else:
            return await message.reply_text("⚠️ **Invalid argument!** Use `/lockwarns on` or `/lockwarns off`.", reply_markup=back_markup)

        await db.lockwarns.update_one(
            {"chat_id": chat_id},
            {"$set": {"enabled": status}},
            upsert=True
        )
        await message.reply_text(f"✅ **Lock warns turned:** `{'ON' if status else 'OFF'}`", reply_markup=back_markup)

    # ============================================================
    # 🔗 ALLOWLIST MANAGEMENT (`/allowlist`, `/rmallowlist`, `/rmallowlistall`)
    # ============================================================
    @app.on_message(filters.command("allowlist") & filters.group)
    async def allowlist_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        chat_id = message.chat.id
        args = message.command[1:]
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if not args:
            data = await db.allowlist.find_one({"chat_id": chat_id})
            items = data.get("items", []) if data else []
            if not items:
                return await message.reply_text("ℹ️ **The allowlist for this chat is currently empty.**", reply_markup=back_markup)
            formatted = ", ".join([f"`{i}`" for i in items])
            return await message.reply_text(f"📋 **Allowlisted items in this chat:**\n\n{formatted}", reply_markup=back_markup)

        try:
            await db.allowlist.update_one(
                {"chat_id": chat_id},
                {"$addToSet": {"items": {"$each": args}}},
                upsert=True
            )
            await message.reply_text(f"✅ **Successfully added `{len(args)}` item(s) to the allowlist.**", reply_markup=back_markup)
        except Exception as e:
            await message.reply_text(f"❌ **Error updating allowlist:** `{str(e)}`", reply_markup=back_markup)

    @app.on_message(filters.command("rmallowlist") & filters.group)
    async def rmallowlist_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        chat_id = message.chat.id
        args = message.command[1:]
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if not args:
            return await message.reply_text("⚠️ **Please specify items to remove from the allowlist!**", reply_markup=back_markup)

        try:
            await db.allowlist.update_one(
                {"chat_id": chat_id},
                {"$pull": {"items": {"$in": args}}}
            )
            await message.reply_text(f"✅ **Successfully removed specified item(s) from the allowlist.**", reply_markup=back_markup)
        except Exception as e:
            await message.reply_text(f"❌ **Error removing allowlist items:** `{str(e)}`", reply_markup=back_markup)

    @app.on_message(filters.command("rmallowlistall") & filters.group)
    async def rmallowlistall_cmd(client, message: Message):
        if not await is_admin(client, message.chat.id, message.from_user.id):
            return await message.reply_text("❌ **Only admins can use this command!**")

        chat_id = message.chat.id
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        try:
            await db.allowlist.delete_one({"chat_id": chat_id})
            await message.reply_text("🗑️ **Successfully removed all allowlisted items in this chat.**", reply_markup=back_markup)
        except Exception as e:
            await message.reply_text(f"❌ **Error clearing allowlist:** `{str(e)}`", reply_markup=back_markup)

    # ============================================================
    # 🚫 LINK & PATTERN DETECTION ENGINE
    # ============================================================
    LINK_REGEX = re.compile(r"(https?://|t\.me/|www\.|[a-zA-Z0-9][-a-zA-Z0-90-9]*\.[a-zA-Z]{2,}(/.*)?)")

    def has_link(text):
        return bool(text and LINK_REGEX.search(text))

    # ============================================================
    # 🚨 AUTOMATIC LOCK FILTER & ENFORCEMENT
    # ============================================================
    @app.on_message(filters.group & ~filters.service, group=5)
    async def lock_filter(client, message: Message):
        if not message.from_user:
            return

        chat_id = message.chat.id

        # Skip check for group admins
        if await is_admin(client, chat_id, message.from_user.id):
            return

        locks = await get_locks(chat_id)
        if not locks:
            return

        # Check allowlist
        text_content = message.text or message.caption or ""
        allow_data = await db.allowlist.find_one({"chat_id": chat_id})
        allow_items = allow_data.get("items", []) if allow_data else []
        
        if any(item in text_content for item in allow_items):
            return

        should_delete = False

        if locks.get("all"):
            should_delete = True
        elif locks.get("media") and message.media:
            should_delete = True
        elif locks.get("photo") and message.photo:
            should_delete = True
        elif locks.get("video") and message.video:
            should_delete = True
        elif locks.get("audio") and message.audio:
            should_delete = True
        elif locks.get("voice") and message.voice:
            should_delete = True
        elif locks.get("document") and message.document:
            should_delete = True
        elif locks.get("sticker") and message.sticker:
            should_delete = True
        elif (locks.get("gif") or locks.get("animation")) and message.animation:
            should_delete = True
        elif locks.get("text") and message.text:
            should_delete = True
        elif (locks.get("link") or locks.get("url")) and (has_link(message.text) or has_link(message.caption)):
            should_delete = True
        elif locks.get("hashtag") and message.text and "#" in message.text:
            should_delete = True
        elif locks.get("forward") and message.forward_date:
            should_delete = True
        elif (locks.get("bots") or locks.get("bot")) and message.from_user.is_bot:
            should_delete = True
        elif locks.get("inline") and message.via_bot:
            should_delete = True
        elif locks.get("contact") and message.contact:
            should_delete = True
        elif locks.get("location") and message.location:
            should_delete = True
        elif locks.get("poll") and message.poll:
            should_delete = True
        elif locks.get("game") and message.game:
            should_delete = True

        if should_delete:
            try:
                await message.delete()
                # Check if lockwarns is enabled
                warns_setting = await db.lockwarns.find_one({"chat_id": chat_id})
                if warns_setting and warns_setting.get("enabled", False):
                    await message.reply_text(f"⚠️ `{message.from_user.first_name}` , you are not allowed to send this content here!")
            except Exception:
                pass
