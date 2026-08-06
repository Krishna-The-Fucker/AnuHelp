# ============================================================
# 🚫 COMMAND DISABLER MODULE (ROSE STYLE)
# ============================================================

__mod_name__ = "🚫 ᴅɪꜱᴀʙʟᴇ"

__help__ = """
*🚫 ᴅɪꜱᴀʙʟᴇ ᴍᴏᴅᴜʟᴇ* — Stop users from using certain commands in your group.

Admin commands:
• `/disable <commandname>` — Stop users from using "commandname" in this group.
• `/enable <commandname>` — Allow users from using "commandname" in this group.
• `/disableable` — List all disableable commands.
• `/disabled` — List the disabled commands in this chat.
• `/disabledel <yes/no/on/off>` — Delete disabled commands when used by non-admins.
• `/disableadmin <yes/no/on/off>` — Stop admins from using disabled commands too.

**Note:** By default, disabling a command only disables it for non-admins. To stop admins from using disabled commands too, check the `/disableadmin` toggle. Disabled commands are still accessible through the `/connect` feature.
"""

from pyrogram import filters
from pyrogram.types import Message
from db import db
import logging

logger = logging.getLogger("DISABLE")

# List of commands that are allowed to be disabled
DISABLEABLE_COMMANDS = [
    "runs", "id", "info", "donate", "limits", "welcome", "goodbye", 
    "notes", "filters", "warns", "rules", "pins", "misc"
]

def register_disable_system(app):

    # ============================================================
    # 🛑 GLOBAL COMMAND INTERCEPTOR (CHECK DISABLED STATUS)
    # ============================================================
    @app.on_message(filters.command & ~filters.private, group=-1)
    async def check_disabled_commands(client, message: Message):
        chat_id = message.chat.id
        cmd = message.command[0].lower()

        if cmd not in DISABLEABLE_COMMANDS:
            return

        try:
            # Check if command is disabled in this chat
            disabled_data = await db.disabled_commands.find_one({"chat_id": chat_id})
            if not disabled_data or cmd not in disabled_data.get("commands", []):
                return

            # Check if user is admin
            is_admin = False
            try:
                member = await client.get_chat_member(chat_id, message.from_user.id)
                if member.status in ["creator", "administrator"]:
                    is_admin = True
            except Exception:
                pass

            # Check if admin restriction is active
            admin_setting = await db.disable_admin.find_one({"chat_id": chat_id})
            block_admins = admin_setting.get("enabled", False) if admin_setting else False

            if is_admin and not block_admins:
                return  # Admins can use it if disableadmin is off

            # If blocked, stop execution
            message.stop_propagation()

            # Check if deletion of disabled command message is enabled
            del_setting = await db.disable_del.find_one({"chat_id": chat_id})
            if del_setting and del_setting.get("enabled", False):
                try:
                    await message.delete()
                except Exception:
                    pass

        except Exception as e:
            logger.error(f"[Disable Interceptor Error]: {e}")

    # ============================================================
    # 🚫 DISABLE COMMAND (`/disable <commandname>`)
    # ============================================================
    @app.on_message(filters.command("disable") & ~filters.private)
    async def disable_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to use /disable!**")

        args = message.command
        if len(args) < 2:
            return await message.reply("⚠️ **Please specify a command to disable!** Example: `/disable info`")

        target_cmd = args[1].lower().lstrip("/")
        if target_cmd == "all":
            await db.disabled_commands.update_one(
                {"chat_id": message.chat.id},
                {"$set": {"commands": DISABLEABLE_COMMANDS.copy()}},
                upsert=True
            )
            return await message.reply("✅ **Disabled all disableable commands in this chat!**")

        if target_cmd not in DISABLEABLE_COMMANDS:
            return await message.reply(f"❌ **Command `{target_cmd}` cannot be disabled or does not exist.** Use `/disableable` to see valid commands.")

        settings = await db.disabled_commands.find_one({"chat_id": message.chat.id})
        cmds = settings.get("commands", []) if settings else []

        if target_cmd in cmds:
            return await message.reply(f"ℹ️ **Command `{target_cmd}` is already disabled in this chat.**")

        cmds.append(target_cmd)
        await db.disabled_commands.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"commands": cmds}},
            upsert=True
        )
        await message.reply(f"✅ **Successfully disabled command:** `{target_cmd}`")

    # ============================================================
    # ✅ ENABLE COMMAND (`/enable <commandname>`)
    # ============================================================
    @app.on_message(filters.command("enable") & ~filters.private)
    async def enable_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to use /enable!**")

        args = message.command
        if len(args) < 2:
            return await message.reply("⚠️ **Please specify a command to enable!** Example: `/enable info`")

        target_cmd = args[1].lower().lstrip("/")
        settings = await db.disabled_commands.find_one({"chat_id": message.chat.id})
        if not settings or target_cmd not in settings.get("commands", []):
            return await message.reply(f"ℹ️ **Command `{target_cmd}` is not disabled in this chat.**")

        cmds = settings.get("commands", [])
        if target_cmd in cmds:
            cmds.remove(target_cmd)

        await db.disabled_commands.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"commands": cmds}},
            upsert=True
        )
        await message.reply(f"✅ **Successfully enabled command:** `{target_cmd}`")

    # ============================================================
    # 📋 LIST DISABLEABLE COMMANDS (`/disableable`)
    # ============================================================
    @app.on_message(filters.command("disableable") & ~filters.private)
    async def disableable_list_cmd(client, message: Message):
        formatted_cmds = ", ".join([f"`/{c}`" for c in DISABLEABLE_COMMANDS])
        await message.reply(
            f"📋 **LIST OF DISABLEABLE COMMANDS**\n\n"
            f"{formatted_cmds}\n\n"
            f"Use `/disable <command>` to disable any of these in this chat."
        )

    # ============================================================
    # 📋 LIST DISABLED COMMANDS (`/disabled`)
    # ============================================================
    @app.on_message(filters.command("disabled") & ~filters.private)
    async def disabled_list_cmd(client, message: Message):
        try:
            settings = await db.disabled_commands.find_one({"chat_id": message.chat.id})
            cmds = settings.get("commands", []) if settings else []
            if not cmds:
                return await message.reply("ℹ️ **No commands are currently disabled in this chat.**")

            formatted_cmds = ", ".join([f"`/{c}`" for c in cmds])
            await message.reply(f"🚫 **Disabled Commands in this chat:**\n\n{formatted_cmds}")
        except Exception as e:
            await message.reply(f"❌ **Error:** `{str(e)}`")

    # ============================================================
    # 🗑️ TOGGLE DISABLE DEL (`/disabledel <yes/no/on/off>`)
    # ============================================================
    @app.on_message(filters.command("disabledel") & ~filters.private)
    async def disabledel_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to change this setting!**")

        args = message.command
        if len(args) < 2:
            del_setting = await db.disable_del.find_one({"chat_id": message.chat.id})
            status = del_setting.get("enabled", False) if del_setting else False
            return await message.reply(f"ℹ️ **Delete disabled commands status:** `{'Enabled' if status else 'Disabled'}`\nUse `/disabledel on` or `/disabledel off`.")

        choice = args[1].lower()
        if choice in ["yes", "on", "true"]:
            status = True
        elif choice in ["no", "off", "false"]:
            status = False
        else:
            return await message.reply("⚠️ **Invalid argument!** Use `/disabledel on` or `/disabledel off`.")

        await db.disable_del.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": status}},
            upsert=True
        )
        await message.reply(f"✅ **Delete disabled commands turned:** `{'ON' if status else 'OFF'}`")

    # ============================================================
    # 🛡️ TOGGLE DISABLE ADMIN (`/disableadmin <yes/no/on/off>`)
    # ============================================================
    @app.on_message(filters.command("disableadmin") & ~filters.private)
    async def disableadmin_cmd(client, message: Message):
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in ["creator", "administrator"]:
            return await message.reply("⚠️ **You must be an administrator to change this setting!**")

        args = message.command
        if len(args) < 2:
            admin_setting = await db.disable_admin.find_one({"chat_id": message.chat.id})
            status = admin_setting.get("enabled", False) if admin_setting else False
            return await message.reply(f"ℹ️ **Disable commands for admins status:** `{'Enabled' if status else 'Disabled'}`\nUse `/disableadmin on` or `/disableadmin off`.")

        choice = args[1].lower()
        if choice in ["yes", "on", "true"]:
            status = True
        elif choice in ["no", "off", "false"]:
            status = False
        else:
            return await message.reply("⚠️ **Invalid argument!** Use `/disableadmin on` or `/disableadmin off`.")

        await db.disable_admin.update_one(
            {"chat_id": message.chat.id},
            {"$set": {"enabled": status}},
            upsert=True
        )
        await message.reply(f"✅ **Disable commands for admins turned:** `{'ON' if status else 'OFF'}`")
