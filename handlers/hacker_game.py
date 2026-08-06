# ============================================================
# 💻 HACKER GAME MODULE (ROSE STYLE & FULL POWER)
# ============================================================

__mod_name__ = "💻 ʜᴀᴄᴋᴇʀ"

__help__ = """
*💻 ʜᴀᴄᴋᴇʀ ᴍᴏᴅᴜʟᴇ* — Test your cybersecurity skills, breach mainframe servers, and extract corporate data for bounty cash!

Commands:
• `/hack` — Play The Hackers Game to breach corporate servers and earn cash and XP.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random

def register_hacker_system(app, db):

    # ============================================================
    # 💻 HACKING GAME COMMAND (`/hack`)
    # ============================================================
    hack_scenarios = [
        ("You bypassed the mainframe firewall of a mega-corp and extracted crypto worth", 1000, 3000, 35),
        ("You infiltrated an encrypted defense server and downloaded classified files sold for", 1500, 4500, 50),
        ("You cracked the database of an underground casino and drained", 800, 2500, 25),
        ("You triggered an active ICE security countermeasure, got locked out, and lost", -300, -700, -10),
        ("You executed a zero-day exploit on a banking gateway and siphoned", 1200, 3500, 40),
    ]

    @app.on_message(filters.command("hack") & filters.group)
    async def hack_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        user_id = user.id
        chat_id = message.chat.id

        scenario, min_amt, max_amt, xp_gain = random.choice(hack_scenarios)
        amount = random.randint(min_amt, max_amt)

        # Fetch or initialize user in database
        user_data = await db.underworld_users.find_one({"user_id": user_id})
        if not user_data:
            user_data = {"cash": 1000, "xp": 0, "level": 1}

        current_cash = user_data.get("cash", 1000)
        current_xp = user_data.get("xp", 0)
        current_level = user_data.get("level", 1)

        new_cash = max(0, current_cash + amount)
        new_xp = current_xp + max(5, xp_gain)

        # Level up check
        new_level = current_level
        if new_xp >= current_level * 150:
            new_level += 1

        await db.underworld_users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": user.first_name,
                "cash": new_cash,
                "xp": new_xp,
                "level": new_level
            }},
            upsert=True
        )

        # Track group membership for local leaderboards
        await db.underworld_group_members.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"name": user.first_name}},
            upsert=True
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if amount > 0:
            text = f"💻 `{user.first_name}` — {scenario} **${amount:,}**! ⚡"
        else:
            text = f"🚨 `{user.first_name}` — {scenario} **${abs(amount):,}** in server damage penalties! 🛑"

        await message.reply_text(text, reply_markup=back_markup)
