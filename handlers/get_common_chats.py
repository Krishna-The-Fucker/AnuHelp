# ============================================================
# 👥 COMMON CHATS MANAGEMENT MODULE (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "👥 ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs"

__help__ = """
*👥 ᴄᴏᴍᴍᴏɴ ᴄʜᴀᴛs* — Check mutual group chats between you and the bot or other users securely (Developer/Sudo & Owner utility).

• `/common [user_id]` — Find mutual groups shared between you (or a replied user) and the bot.
"""

from pyrogram import filters
from pyrogram.types import Message
import logging
from config import DEV_LIST, SUDO_USERS, OWNER_ID

def register_common_chats_system(app):

    # ============================================================
    # 👥 GET COMMON CHATS (`/common`)
    # ============================================================
    @app.on_message(filters.command("common"))
    async def get_common_chats_cmd(client, message: Message):
        user_id = message.from_user.id if message.from_user else 0
        
        # Restrict command to Sudo/Devs/Owner for privacy & security reasons
        if user_id not in DEV_LIST and user_id not in SUDO_USERS and user_id != OWNER_ID:
            return await message.reply("⚠️ **This command is restricted to Developers and Sudo users only!**")

        target_id = None
        if message.reply_to_message and message.reply_to_message.from_user:
            target_id = message.reply_to_message.from_user.id
        elif len(message.command) > 1:
            try:
                target_id = int(message.command[1])
            except ValueError:
                return await message.reply("⚠️ **Invalid user ID provided! Please provide a valid numeric Telegram user ID.**")
        else:
            target_id = user_id

        status_msg = await message.reply("👥 **Scanning mutual group chats... Please wait.**")

        try:
            target_user = await client.get_users(target_id)
            common_chats = []

            # Iterate through dialogs of the bot to find mutual group memberships
            async for dialog in client.get_dialogs():
                chat = dialog.chat
                if chat.type.value in ["group", "supergroup"]:
                    try:
                        member = await chat.get_member(target_user.id)
                        if member and member.status not in ["left", "banned"]:
                            common_chats.append(f"• {chat.title} (`{chat.id}`)")
                    except Exception:
                        pass # User is not in this group or bot lacks access

            if not common_chats:
                return await status_msg.edit_text(f"❌ **No common groups found with user** {target_user.mention} (`{target_user.id}`)!")

            # Format the output with truncation if too many chats
            max_display = 25
            display_chats = common_chats[:max_display]
            output_list = "\n".join(display_chats)
            
            footer = f"\n\n_Showing {len(display_chats)} of {len(common_chats)} common chats._" if len(common_chats) > max_display else f"\n\n_Total Mutual Groups: {len(common_chats)}_"

            await status_msg.edit_text(
                f"👥 **Mutual Groups with {target_user.mention} (`{target_user.id}`):**\n\n"
                f"{output_list}{footer}"
            )

        except Exception as e:
            logging.error(f"[Common Chats Error]: {e}")
            await status_msg.edit_text(f"❌ **Failed to retrieve common chats:** `{str(e)}`")
