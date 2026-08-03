# ============================================================
# 📢 BROADCAST SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "📢 ʙʀᴏᴀᴅᴄᴀsᴛ"

__help__ = """
*📢 ʙʀᴏᴀᴅᴄᴀsᴛ sʏsᴛᴇᴍ* — Broadcast announcements, updates, or media messages to all registered users or groups seamlessly!

• `/broadcast` — Reply to any message in private to broadcast it to all users with live progress tracking.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
import logging

def register_broadcast(app, db, OWNER_ID, LOG_CHANNEL):

    # ==========================================================
    # 📢 LOG HELPER FUNCTION
    # ==========================================================
    async def log_action(client, text):
        try:
            await client.send_message(LOG_CHANNEL, text)
        except Exception:
            pass

    # ==========================================================
    # 📢 BROADCAST COMMAND HANDLER
    # ==========================================================
    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_handler(client, message: Message):
        # ❌ Owner Security Check
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ **Access Denied!** Only the bot owner can execute broadcasts.")

        # ❌ Message Reply Check
        if not message.reply_to_message:
            return await message.reply_text(
                "⚠️ **Incorrect Usage!**\n"
                "• Reply to any message (text, media, audio, etc.) with `/broadcast` to initiate."
            )

        # 📥 Fetch all users from database
        try:
            users = await db.get_all_users()
        except Exception as e:
            return await message.reply_text(f"❌ **Database Error:** `{e}`")

        if not users:
            return await message.reply_text("⚠️ **Database Warning:** No users found to broadcast.")

        total = len(users)
        sent = 0
        failed = 0
        blocked = 0
        deleted = 0

        # Initial Status Message with UI vibe
        status = await message.reply_text(
            f"🚀 **Broadcast Initialization...**\n\n"
            f"• **Target Users:** `{total}`\n"
            f"• **Status:** `In Progress 🟢`"
        )

        start_time = asyncio.get_event_loop().time()

        # ======================================================
        # 🚀 HIGH PERFORMANCE SAFE LOOP
        # ======================================================
        for i, user_data in enumerate(users, start=1):
            # Support both list of integer IDs or list of dicts containing user_id
            user_id = user_data.get("user_id") if isinstance(user_data, dict) else user_data

            if not user_id:
                continue

            try:
                await message.reply_to_message.copy(user_id)
                sent += 1
            except Exception as err:
                failed += 1
                err_str = str(err).lower()
                if "blocked" in err_str:
                    blocked += 1
                elif "deactivated" in err_str or "deleted" in err_str:
                    deleted += 1

            # ⏱ Balanced delay to completely prevent Telegram FloodWait limits
            await asyncio.sleep(0.04)

            # 🔄 Live progress update interval every 25 users
            if i % 25 == 0 or i == total:
                try:
                    await status.edit_text(
                        f"📢 **Broadcasting in Progress...**\n\n"
                        f"👤 **Total Users:** `{total}`\n"
                        f"✔ **Successful:** `{sent}`\n"
                        f"❌ **Failed:** `{failed}`\n"
                        f"⏳ **Progress:** `{int((i / total) * 100)}%`"
                    )
                except Exception:
                    pass

        end_time = asyncio.get_event_loop().time()
        elapsed_time = round(end_time - start_time, 2)

        # ======================================================
        # ✅ FINAL RESULT REPORT PANEL
        # ======================================================
        final_report = (
            f"✅ **Broadcast Completed Successfully!**\n\n"
            f"👤 **Total Users:** `{total}`\n"
            f"✔ **Successfully Sent:** `{sent}`\n"
            f"❌ **Failed Delivery:** `{failed}`\n"
            f"🚫 **Blocked Users:** `{blocked}`\n"
            f"🗑️ **Deleted Accounts:** `{deleted}`\n"
            f"⏱️ **Time Elapsed:** `{elapsed_time} seconds`"
        )

        await status.edit_text(final_report)

        # ======================================================
        # 🧾 LOG ACTION TO LOG CHANNEL
        # ======================================================
        await log_action(
            client,
            f"📢 **Broadcast Report Finished**\n\n"
            f"• **Triggered By:** {message.from_user.mention} (`{message.from_user.id}`)\n"
            f"• **Total Target:** `{total}`\n"
            f"• **Sent:** `{sent}` | **Failed:** `{failed}`\n"
            f"• **Duration:** `{elapsed_time}s`"
        )
