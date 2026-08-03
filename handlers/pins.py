# ============================================================
# 📌 PIN SYSTEM (ULTIMATE MODERN VERSION)
# ============================================================

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired

# Project ke centralized db structure ke sath sync kiya gaya hai
from db import db

# ============================================================
# 🔧 AUTO PIN DB FUNCTIONS
# ============================================================

async def set_auto_pin(chat_id: int, status: bool):
    await db.pins_settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"auto_pin": status}},
        upsert=True
    )

async def get_auto_pin(chat_id: int) -> bool:
    data = await db.pins_settings.find_one({"chat_id": chat_id})
    return data.get("auto_pin", False) if data else False


# ============================================================
# 🔥 HANDLER & COMMANDS REGISTRATION
# ============================================================

def register_pin_system(app):

    # 📌 PIN COMMAND
    @app.on_message(filters.command("pin") & filters.group)
    async def pin_message(client, message: Message):
        if not message.reply_to_message:
            return await message.reply_text("❌ **Reply to a message to pin it!**")

        try:
            await message.reply_to_message.pin(disable_notification=False)
            await message.reply_text("📌 **Message pinned successfully!** 🟢")
        except ChatAdminRequired:
            await message.reply_text("❌ **I need admin rights (Pin Messages) to perform this action!**")
        except Exception as e:
            await message.reply_text(f"❌ **Failed to pin message:** `{e}`")

    # 🔕 SILENT PIN COMMAND
    @app.on_message(filters.command("pinloud") & filters.group)
    async def pin_loud(client, message: Message):
        if not message.reply_to_message:
            return await message.reply_text("❌ **Reply to a message to pin it silently!**")

        try:
            await message.reply_to_message.pin(disable_notification=True)
            await message.reply_text("📌 **Message pinned silently!** 🔇")
        except ChatAdminRequired:
            await message.reply_text("❌ **I need admin rights to pin messages!**")
        except Exception as e:
            await message.reply_text(f"❌ **Failed to pin message:** `{e}`")

    # 📌 UNPIN COMMAND
    @app.on_message(filters.command("unpin") & filters.group)
    async def unpin_message(client, message: Message):
        try:
            if message.reply_to_message:
                await message.reply_to_message.unpin()
            else:
                await client.unpin_chat_message(message.chat.id)
            await message.reply_text("📌❌ **Message unpinned successfully!**")
        except ChatAdminRequired:
            await message.reply_text("❌ **I need admin rights to unpin messages!**")
        except Exception as e:
            await message.reply_text(f"❌ **Failed to unpin:** `{e}`")

    # 🧹 UNPIN ALL COMMAND
    @app.on_message(filters.command("unpinall") & filters.group)
    async def unpin_all(client, message: Message):
        try:
            await client.unpin_all_chat_messages(message.chat.id)
            await message.reply_text("🧹 **All pinned messages have been removed!** ✨")
        except ChatAdminRequired:
            await message.reply_text("❌ **I need admin rights to unpin messages!**")
        except Exception as e:
            await message.reply_text(f"❌ **Failed to unpin all messages:** `{e}`")

    # ⚙️ AUTO PIN TOGGLE COMMAND
    @app.on_message(filters.command("autopin") & filters.group)
    async def auto_pin_toggle(client, message: Message):
        if len(message.command) < 2:
            return await message.reply_text(
                "⚙️ **Auto Pin Configuration:**\n"
                "• `/autopin on` — Enable auto pin for media/text\n"
                "• `/autopin off` — Disable auto pin"
            )

        arg = message.command[1].lower()

        if arg == "on":
            await set_auto_pin(message.chat.id, True)
            await message.reply_text("✅ **Auto Pin System:** Enabled 🟢")
        elif arg == "off":
            await set_auto_pin(message.chat.id, False)
            await message.reply_text("❌ **Auto Pin System:** Disabled 🔴")
        else:
            await message.reply_text("❌ **Invalid option!** Use `on` or `off`.")

    # 🤖 AUTO PIN HANDLER (Fixed & Completed)
    @app.on_message(filters.group & ~filters.service & ~filters.bot, group=7)
    async def auto_pin_handler(client, message: Message):
        try:
            if not await get_auto_pin(message.chat.id):
                return

            # Optional: Check if bot has admin rights before trying to pin
            await message.pin(disable_notification=False)
        except ChatAdminRequired:
            pass
        except Exception:
            pass
