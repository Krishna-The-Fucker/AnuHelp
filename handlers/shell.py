# ============================================================
# 💻 SHELL EXECUTOR MODULE (DEVELOPER ONLY 👑)
# ============================================================

__mod_name__ = "💻 sʜᴇʟʟ"

__help__ = """
*💻 ꜱʜᴇʟʟ ᴇxᴇᴄᴜᴛᴏʀ* — Execute system shell commands directly from Telegram (Restricted to Owner/Devs only).

• `/sh [command]` — Run a terminal command and get the output.
"""

from pyrogram import filters
from pyrogram.types import Message
import asyncio
import traceback
import sys
import io
from config import DEV_LIST, OWNER_ID

def register_shell_system(app):

    @app.on_message(filters.command("sh") & filters.user(DEV_LIST + [OWNER_ID]))
    async def shell_execution_cmd(client, message: Message):
        if len(message.command) < 2:
            return await message.reply("⚠️ **Please provide a shell command to execute! Example:** `/sh ls -la`")

        cmd_text = message.text.split(None, 1)[1]
        status_msg = await message.reply("⚡ **Executing shell command...**")

        try:
            # Run bash/shell process asynchronously
            process = await asyncio.create_subprocess_shell(
                cmd_text,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()

            output = stdout.decode().strip()
            error = stderr.decode().strip()

            result = ""
            if output:
                result += f"📤 **STDOUT:**\n```bash\n{output}\n```\n"
            if error:
                result += f"❌ **STDERR:**\n```bash\n{error}\n```\n"

            if not result:
                result = "✅ **Command executed successfully with no output.**"

            # Truncate if too long for telegram message limits
            if len(result) > 4000:
                file_io = io.BytesIO(result.encode("utf-8"))
                file_io.name = "shell_output.txt"
                await message.reply_document(file_io, caption=f"📄 **Output too long for message. Sent as file.**")
                await status_msg.delete()
            else:
                await status_msg.edit_text(result)

        except Exception as e:
            tb = traceback.format_exc()
            await status_msg.edit_text(f"❌ **Execution Failed:**\n```python\n{tb}\n```")
