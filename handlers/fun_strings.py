# ============================================================
# 🎉 FUN STRINGS & TEXT ENHANCEMENT MODULE (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🎉 ғᴜɴ sᴛʀɪɴɢs"

__help__ = """
*🎉 ғᴜɴ sᴛʀɪɴɢs & ᴛᴇxᴛ ᴛᴏᴏʟs* — Fun text effects, reverse typing, vaporwave fonts, and quirky string manipulators!

• `/reverse [text]` — Reverse your text backwards.
• `/vapor [text]` — Convert text into aesthetic vaporwave spacing.
• `/mock [text]` — Spongebob mock text generator (sPoNgEbOb CaSe).
• `/flip [text]` — Flip your text upside down.
"""

from pyrogram import filters
from pyrogram.types import Message
import random

def register_fun_strings_system(app):

    # ============================================================
    # 🔄 REVERSE TEXT (`/reverse`)
    # ============================================================
    @app.on_message(filters.command("reverse"))
    async def reverse_text_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide text or reply to a message to reverse! Example:** `/reverse Hello World`")

        reversed_text = query[::-1]
        await message.reply(f"🔄 **Reversed Text:**\n`{reversed_text}`")

    # ============================================================
    # 📻 VAPORWAVE AESTHETIC TEXT (`/vapor`)
    # ============================================================
    @app.on_message(filters.command("vapor"))
    async def vaporwave_text_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide text or reply to a message for vaporwave effect! Example:** `/vapor Hello`")

        # Convert normal characters to full-width aesthetic Unicode characters
        vapor_chars = []
        for char in query:
            code = ord(char)
            if 33 <= code <= 126:
                vapor_chars.append(chr(code + 65248))
            else:
                vapor_chars.append(char)
        
        vapor_text = " ".join(vapor_chars)
        await message.reply(f"📻 **Aesthetic Vaporwave:**\n`{vapor_text}`")

    # ============================================================
    # 🤪 SPONGEBOB MOCK TEXT (`/mock`)
    # ============================================================
    @app.on_message(filters.command("mock"))
    async def mock_text_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide text or reply to mock! Example:** `/mock stop doing that`")

        mocked_chars = [c.upper() if random.choice([True, False]) else c.lower() for c in query]
        mocked_text = "".join(mocked_chars)
        
        await message.reply(f"🤪 **Mock Text:**\n`{mocked_text}`")

    # ============================================================
    # 🙃 UPSIDE DOWN TEXT (`/flip`)
    # ============================================================
    @app.on_message(filters.command("flip"))
    async def flip_text_cmd(client, message: Message):
        query = " ".join(message.command[1:])
        if not query and message.reply_to_message and message.reply_to_message.text:
            query = message.reply_to_message.text
        if not query:
            return await message.reply("⚠️ **Please provide text or reply to flip! Example:** `/flip Hello`")

        normal = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!"
        flipped = "ɐqɔpǝɟƃɥıɾʞlɯuodbɹsʇnʌʍxʎzⱯᗺƆᗡƎℲ⅁HIſʞ˥WNOԀÒᴚS┴∩ΛMX⅄Z0ƖᄅƐㄣϛ9ㄥ86˙'¡¿"
        
        table = str.maketrans(normal, flipped)
        flipped_text = query.translate(table)[::-1]

        await message.reply(f"🙃 **Flipped Text:**\n`{flipped_text}`")
