# ============================================================
# 🎮 QUICK GAMES MODULE (INTERACTIVE MINI GAMES)
# ============================================================

__mod_name__ = "🎮 ǫᴜɪᴄᴋ ɢᴀᴍᴇꜱ"

__help__ = """
*🎮 ǫᴜɪᴄᴋ ɢᴀᴍᴇꜱ ᴍᴏᴅᴜʟᴇ* — Enjoy quick interactive mini-games right inside your group chats or private chat!

• `/dice` — Roll a 6-sided dice 🎲
• `/dart` — Throw a dart at the target 🎯
• `/basket` or `/ball` — Shoot a basketball 🏀
• `/football` or `/goal` — Kick a football ⚽
• `/slot` or `/casino` — Spin the slot machine 🎰
• `/bowling` — Roll a bowling ball 🎳
"""

from pyrogram import filters
from pyrogram.types import Message
import logging

logger = logging.getLogger("QUICK_GAMES")

def register_quick_games_system(app):

    # ============================================================
    # 🎲 DICE GAME (`/dice`)
    # ============================================================
    @app.on_message(filters.command("dice"))
    async def dice_game(client, message: Message):
        try:
            await message.reply_dice(emoji="🎲")
        except Exception as e:
            logger.error(f"[Dice Error]: {e}")
            await message.reply("❌ **Failed to roll dice!**")

    # ============================================================
    # 🎯 DART GAME (`/dart`)
    # ============================================================
    @app.on_message(filters.command("dart"))
    async def dart_game(client, message: Message):
        try:
            await message.reply_dice(emoji="🎯")
        except Exception as e:
            logger.error(f"[Dart Error]: {e}")
            await message.reply("❌ **Failed to throw dart!**")

    # ============================================================
    # 🏀 BASKETBALL GAME (`/basket`, `/ball`)
    # ============================================================
    @app.on_message(filters.command(["basket", "ball"]))
    async def basketball_game(client, message: Message):
        try:
            await message.reply_dice(emoji="🏀")
        except Exception as e:
            logger.error(f"[Basketball Error]: {e}")
            await message.reply("❌ **Failed to shoot basketball!**")

    # ============================================================
    # ⚽ FOOTBALL GAME (`/football`, `/goal`)
    # ============================================================
    @app.on_message(filters.command(["football", "goal"]))
    async def football_game(client, message: Message):
        try:
            await message.reply_dice(emoji="⚽")
        except Exception as e:
            logger.error(f"[Football Error]: {e}")
            await message.reply("❌ **Failed to kick football!**")

    # ============================================================
    # 🎰 SLOT MACHINE GAME (`/slot`, `/casino`)
    # ============================================================
    @app.on_message(filters.command(["slot", "casino"]))
    async def slot_game(client, message: Message):
        try:
            await message.reply_dice(emoji="🎰")
        except Exception as e:
            logger.error(f"[Slot Error]: {e}")
            await message.reply("❌ **Failed to spin slot machine!**")

    # ============================================================
    # 🎳 BOWLING GAME (`/bowling`)
    # ============================================================
    @app.on_message(filters.command("bowling"))
    async def bowling_game(client, message: Message):
        try:
            await message.reply_dice(emoji="🎳")
        except Exception as e:
            logger.error(f"[Bowling Error]: {e}")
            await message.reply("❌ **Failed to roll bowling ball!**")
