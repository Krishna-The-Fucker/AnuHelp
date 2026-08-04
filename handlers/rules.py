# ============================================================
# 📜 CHAT RULES MANAGEMENT SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "📜 ʀᴜʟᴇs"

__help__ = """
*📜 ʀᴜʟᴇs sʏsᴛᴇᴍ* — Set up, customize, and view your group rules easily and professionally!

• `/rules` — Display the current group rules
• `/setrules <text>` — Set or update the rules for this chat (Admin only)
• `/clearrules` — Delete and clear the rules for this chat (Admin only)
"""

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
import logging

def register_rules_system(app, db):

    # Collection for chat-specific rules
    rules_col = db.chat_rules

    # ============================================================
    # 👑 ADMIN CHECK HELPER
    # ============================================================
    async def is_admin(client, message: Message):
        if not message.from_user:
            return False
        try:
            member = await client.get_chat_member(message.chat.id, message.from_user.id)
            return member.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER
            ]
        except Exception:
            return False

    # ============================================================
    # 📜 VIEW RULES (`/rules`)
    # ============================================================
    @app.on_message(filters.command("rules") & filters.group)
    async def get_rules_cmd(client, message: Message):
        try:
            chat_id = message.chat.id
            rule_doc = await rules_col.find_one({"chat_id": chat_id})

            if not rule_doc or not rule_doc.get("rules"):
                return await message.reply("ℹ️ **No rules have been set for this group yet!** Ask an admin to set them using `/setrules`.")

            rules_text = rule_doc["rules"]
            chat_title = message.chat.title or "this chat"

            output = f"📜 **Rules for {chat_title}:**\n\n{rules_text}"
            await message.reply(output, disable_web_page_preview=True)

        except Exception as e:
            logging.error(f"[Rules Get Error]: {e}")
            await message.reply("❌ **An error occurred while fetching the group rules.**")

    # ============================================================
    # 📝 SET RULES (`/setrules`)
    # ============================================================
    @app.on_message(filters.command("setrules") & filters.group)
    async def set_rules_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can set group rules!**")

        if not message.reply_to_message and len(message.command) < 2:
            return await message.reply(
                "⚠️ **Please provide the rules text or reply to a message!**\n"
                "• Usage: `/setrules <your rules text here>`"
            )

        # Get rules content either from reply or command argument
        if message.reply_to_message:
            rules_content = message.reply_to_message.text or message.reply_to_message.caption
            if not rules_content:
                return await message.reply("❌ **The replied message contains no text!**")
        else:
            rules_content = message.text.split(None, 1)[1]

        chat_id = message.chat.id

        try:
            await rules_col.update_one(
                {"chat_id": chat_id},
                {"$set": {"rules": rules_content}},
                upsert=True
            )
            await message.reply("✅ **Group rules have been successfully updated!** Use `/rules` to view them.")
        except Exception as e:
            logging.error(f"[Rules Set Error]: {e}")
            await message.reply("❌ **Failed to save the group rules to database.**")

    # ============================================================
    # ❌ CLEAR RULES (`/clearrules`, `/delrules`)
    # ============================================================
    @app.on_message(filters.command(["clearrules", "delrules"]) & filters.group)
    async def clear_rules_cmd(client, message: Message):
        if not await is_admin(client, message):
            return await message.reply("❌ **Only administrators can clear group rules!**")

        chat_id = message.chat.id

        try:
            result = await rules_col.delete_one({"chat_id": chat_id})
            if result.deleted_count > 0:
                await message.reply("🗑️ **Group rules have been cleared successfully!**")
            else:
                await message.reply("ℹ️ **There were no active rules set for this group.**")
        except Exception as e:
            logging.error(f"[Rules Clear Error]: {e}")
            await message.reply("❌ **Failed to clear the group rules.**")
