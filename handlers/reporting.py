# ============================================================
# 🚨 USER REPORTING SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🚨 ʀᴇᴘᴏʀᴛ"

__help__ = """
*🚨 ʀᴇᴘᴏʀᴛ sʏsᴛᴇᴍ* — Alert group administrators instantly when a user misbehaves by tagging them with `/report` or `@admin`!

• Reply to any bad message with `/report` or `@admin` to notify all online group admins
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging

def register_reporting_system(app, db):

    # ============================================================
    # 📢 REPORT COMMAND (`/report`, `@admin`, `@admins`)
    # ============================================================
    @app.on_message(filters.command(["report", "admin", "admins"]) & filters.group)
    async def report_user_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply(
                "⚠️ **Please reply to the message you want to report!**\n"
                "• Usage: Reply with `/report` or `@admin`"
            )

        reported_msg = message.reply_to_message
        reporter = message.from_user
        bad_user = reported_msg.from_user

        # Prevent reporting yourself or bots
        if bad_user and reporter and bad_user.id == reporter.id:
            return await message.reply("⚠️ **You cannot report your own message!**")
        
        if bad_user and bad_user.is_bot:
            return await message.reply("⚠️ **You cannot report a bot's message!**")

        try:
            # Fetch group administrators
            admins = []
            async for member in client.get_chat_members(message.chat.id, filter="administrators"):
                if not member.user.is_bot and not member.user.is_deleted:
                    admins.append(member.user)

            if not admins:
                return await message.reply("⚠️ **No active administrators found to notify!**")

            # Build admin mention string securely
            admin_mentions = []
            for admin in admins:
                mention_name = admin.first_name[:20] # Truncate long names for safety
                admin_mentions.append(f"[{mention_name}](tg://user?id={admin.id})")

            # Format mention chunks (Telegram allows clean inline tagging)
            mentions_text = ", ".join(admin_mentions)

            # Build report notification report
            bad_username = f"@{bad_user.username}" if bad_user.username else f"`{bad_user.id}`"
            reporter_name = f"@{reporter.username}" if reporter.username else f"`{reporter.id}`"

            report_text = (
                f"🚨 **Attention Administrators!** 🚨\n\n"
                f"• **Reported User:** {bad_username} (`{bad_user.id}`)\n"
                f"• **Reported By:** {reporter_name}\n"
                f"• **Chat:** `{message.chat.title}`\n\n"
                f"🔗 [Jump to Reported Message]({reported_msg.link})\n\n"
                f"Notify tags: {mentions_text}"
            )

            # Send alert to the group chat (or log channel if desired, but group alert is standard)
            await message.reply(
                report_text,
                disable_web_page_preview=True
            )

            # Optionally delete the user's report trigger command to keep chat clean
            try:
                await message.delete()
            except Exception:
                pass

        except Exception as e:
            logging.error(f"[Report System Error]: {e}")
            await message.reply("❌ **Failed to dispatch report notification to administrators.**")
