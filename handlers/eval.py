# ============================================================
# 💻 PYTHON EVALUATOR SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "💻 ᴇᴠᴀʟ"

__help__ = """
*💻 ᴇᴠᴀʟ sʏsᴛᴇᴍ* — Run arbitrary Python code or terminal shell commands directly from Telegram (Bot Owner only)!

• `/eval <code>` — Execute a Python code snippet asynchronously
• `/shell <command>` — Run a system shell terminal command
"""

from pyrogram import filters
from pyrogram.types import Message
import traceback
import subprocess
import sys
import io
import os

def register_eval_system(app, db, OWNER_ID: int):

    # ============================================================
    # 💻 PYTHON EVALUATOR (`/eval`, `/e`)
    # ============================================================
    @app.on_message(filters.command(["eval", "e"]) & filters.private)
    async def eval_python_cmd(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("❌ **This command is strictly restricted to the Bot Owner!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please provide Python code to evaluate!**")

        code = message.text.split(None, 1)[1]
        
        status_msg = await message.reply("⏳ **Executing Python code...**")

        # Capture standard output and error streams
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = io.StringIO()
        redirected_error = io.StringIO()
        
        sys.stdout = redirected_output
        sys.stderr = redirected_error

        # Async wrapper function builder to support `await` syntax directly
        async def __async_exec():
            # Provide useful local context variables
            locals = {
                "client": client,
                "app": app,
                "db": db,
                "message": message,
                "chat": message.chat,
                "user": message.from_user
            }
            # Wrap in async def block
            indented_code = "\n".join([f"    {line}" for line in code.splitlines()])
            exec_code = f"async def __ex():\n{indented_code}"
            
            try:
                exec(exec_code, globals(), locals)
                return await locals["__ex"]()
            except Exception:
                raise

        try:
            result = await __async_exec()
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            stdout_val = redirected_output.getvalue()
            stderr_val = redirected_error.getvalue()

            output_text = "💻 **Python Evaluation Results:**\n\n"
            
            if stdout_val:
                output_text += f"📤 **Stdout:**\n```python\n{stdout_val.strip()}\n```\n"
            if stderr_val:
                output_text += f"⚠️ **Stderr:**\n```python\n{stderr_val.strip()}\n```\n"
            if result is not None:
                output_text += f"📥 **Returned:**\n```python\n{str(result)}\n```"

            if not stdout_val and not stderr_val and result is None:
                output_text += "_Code executed successfully with no output._"

            # If text is too long for a single message, save to file/buffer or truncate cleanly
            if len(output_text) > 4096:
                file_buffer = io.BytesIO(output_text.encode("utf-8"))
                file_buffer.name = "eval_output.txt"
                await message.reply_document(document=file_buffer, caption="📁 **Output exceeded message limit. Attached as file.**")
                await status_msg.delete()
            else:
                await status_msg.edit_text(output_text)

        except Exception:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            err_trace = traceback.format_exc()
            error_text = f"❌ **Evaluation Failed:**\n```python\n{err_trace.strip()}\n```"
            
            if len(error_text) > 4096:
                file_buffer = io.BytesIO(error_text.encode("utf-8"))
                file_buffer.name = "eval_error.txt"
                await message.reply_document(document=file_buffer, caption="📁 **Error trace exceeded limit. Attached as file.**")
                await status_msg.delete()
            else:
                await status_msg.edit_text(error_text)

    # ============================================================
    # ⚙️ SHELL TERMINAL EXECUTOR (`/shell`, `/sh`)
    # ============================================================
    @app.on_message(filters.command(["shell", "sh"]) & filters.private)
    async def shell_terminal_cmd(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("❌ **This command is strictly restricted to the Bot Owner!**")

        if len(message.command) < 2:
            return await message.reply("⚠️ **Please provide a shell command to execute!**")

        cmd = message.text.split(None, 1)[1]
        status_msg = await message.reply(f"⏳ **Running shell command:** `{cmd}`...")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                text=True
            )
            stdout, stderr = process.communicate()

            output_text = f"⚙️ **Shell Terminal Execution:**\n`$ {cmd}`\n\n"
            
            if stdout:
                output_text += f"📤 **Output:**\n```bash\n{stdout.strip()}\n```\n"
            if stderr:
                output_text += f"⚠️ **Error:**\n```bash\n{stderr.strip()}\n```\n"

            if not stdout and not stderr:
                output_text += "_Command executed with no output returned._"

            if len(output_text) > 4096:
                file_buffer = io.BytesIO(output_text.encode("utf-8"))
                file_buffer.name = "shell_output.txt"
                await message.reply_document(document=file_buffer, caption="📁 **Shell output exceeded limit. Attached as file.**")
                await status_msg.delete()
            else:
                await status_msg.edit_text(output_text)

        except Exception as e:
            logging.error(f"[Shell Execution Error]: {e}")
            await status_msg.edit_text(f"❌ **Shell execution failed:** `{str(e)}`")
