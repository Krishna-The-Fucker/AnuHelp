# ============================================================
# 📢 BROADCAST SYSTEM (PRO VERSION)
# ============================================================

from pyrogram import filters
from pyrogram.types import Message
from config import OWNER_ID, LOG_CHANNEL
import db
import asyncio

# ============================================================
# 🔥 REGISTER
# ============================================================
def register_broadcast(app):

    # ==========================================================
    # 📢 LOG FUNCTION
    # ==========================================================
    async def log_action(client, text):
        try:
            await client.send_message(LOG_CHANNEL, text)
        except:
            pass

    # ==========================================================
    # 📢 BROADCAST COMMAND
    # ==========================================================
    @app.on_message(filters.private & filters.command("broadcast"))
    async def broadcast_handler(client, message: Message):

        # ❌ Only Owner
        if message.from_user.id != OWNER_ID:
            return await message.reply_text("❌ Only bot owner can use this command")

        # ❌ Must reply
        if not message.reply_to_message:
            return await message.reply_text("⚠️ Reply to a message to broadcast")

        users = await db.get_all_users()

        if not users:
            return await message.reply_text("⚠️ No users found in database")

        total = len(users)
        sent = 0
        failed = 0

        status = await message.reply_text(f"📢 Broadcasting to {total} users...")

        # ======================================================
        # 🚀 FAST LOOP (SAFE)
        # ======================================================
        for i, user_id in enumerate(users, start=1):
            try:
                await message.reply_to_message.copy(user_id)
                sent += 1
            except:
                failed += 1

            # ⏱ Small delay to avoid flood
            await asyncio.sleep(0.05)

            # 🔄 Update progress every 50 users
            if i % 50 == 0:
                try:
                    await status.edit_text(
                        f"📢 Broadcasting...\n\n"
                        f"👤 Total: {total}\n"
                        f"✔ Sent: {sent}\n"
                        f"❌ Failed: {failed}"
                    )
                except:
                    pass

        # ======================================================
        # ✅ FINAL RESULT
        # ======================================================
        await status.edit_text(
            f"✅ Broadcast Completed\n\n"
            f"👤 Total Users: {total}\n"
            f"✔ Sent: {sent}\n"
            f"❌ Failed: {failed}"
        )

        # ======================================================
        # 🧾 LOG
        # ======================================================
        await log_action(
            client,
            f"📢 Broadcast Done\n"
            f"By: {message.from_user.id}\n"
            f"Total: {total}\n"
            f"Sent: {sent}\n"
            f"Failed: {failed}"
        )
