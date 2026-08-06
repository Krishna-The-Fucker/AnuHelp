# ============================================================
# 🏴‍☠️ MAFIYA & LEADERBOARD MODULE (ROSE STYLE & FULL POWER)
# ============================================================

__mod_name__ = "🏴‍☠️ ᴍᴀғɪʏᴀ"

__help__ = """
*🏴‍☠️ ᴍᴀғɪʏᴀ ᴍᴏᴅᴜʟᴇ* — Rise through the criminal underworld, earn cash, level up, and compete on the global and group leaderboards!

Commands:
• `/mafiya` or `/profile` — View your criminal profile, net worth, and stats.
• `/crime` — Commit a risky crime to earn cash and XP.
• `/rob <reply>` — Attempt to rob another user in the chat.
• `/shop` — View the underworld black market shop.
• `/top` or `/leaderboard` — View top 10 global or group criminals!
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random

def register_mafiya_system(app, db):

    # ============================================================
    # 👤 PROFILE / MAFIYA COMMAND (`/mafiya` & `/profile`)
    # ============================================================
    @app.on_message(filters.command(["mafiya", "profile"]) & filters.group)
    async def mafiya_profile_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        chat_id = message.chat.id
        user_id = user.id

        # Fetch user stats from database (Global tracking via user_id, chat tracking optionally)
        user_data = await db.mafiya_users.find_one({"user_id": user_id})
        
        if not user_data:
            user_data = {
                "user_id": user_id,
                "name": user.first_name,
                "cash": 1000,
                "bank": 0,
                "level": 1,
                "xp": 0,
                "reputation": 10,
                "gang": "None"
            }
            await db.mafiya_users.update_one(
                {"user_id": user_id},
                {"$set": user_data},
                upsert=True
            )

        text = (
            f"🏴‍☠️ **MAFIYA PROFILE: `{user.first_name}`**\n\n"
            f"💵 **Cash:** `${user_data.get('cash', 1000):,}`\n"
            f"🏦 **Bank:** `${user_data.get('bank', 0):,}`\n"
            f"📊 **Level:** `{user_data.get('level', 1)}`\n"
            f"✨ **XP:** `{user_data.get('xp', 0)}`\n"
            f"🔥 **Reputation:** `{user_data.get('reputation', 10)}`\n"
            f"⚡ **Syndicate:** `{user_data.get('gang', 'None')}`\n"
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🦹‍♂️ CRIME COMMAND (`/crime`)
    # ============================================================
    crime_scenarios = [
        ("You hacked a central bank ATM and stole", 500, 2000, 25),
        ("You hijacked an armored cash truck and made off with", 1500, 4000, 50),
        ("You looted an underground casino vault and secured", 800, 2500, 30),
        ("You tried to smuggle contraband, but police intercepted and you lost", -200, -500, -10),
        ("You successfully ran a high-stakes scam and earned", 1000, 3000, 35),
    ]

    @app.on_message(filters.command("crime") & filters.group)
    async def crime_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        user_id = user.id
        scenario, min_amt, max_amt, xp_gain = random.choice(crime_scenarios)
        amount = random.randint(min_amt, max_amt)

        # Fetch or initialize user
        user_data = await db.mafiya_users.find_one({"user_id": user_id})
        if not user_data:
            user_data = {"cash": 1000, "xp": 0, "level": 1}

        current_cash = user_data.get("cash", 1000)
        current_xp = user_data.get("xp", 0)
        current_level = user_data.get("level", 1)

        new_cash = max(0, current_cash + amount)
        new_xp = current_xp + max(5, xp_gain)

        # Level up check (every 100 XP)
        new_level = current_level
        if new_xp >= current_level * 100:
            new_level += 1

        await db.mafiya_users.update_one(
            {"user_id": user_id},
            {"$set": {
                "name": user.first_name,
                "cash": new_cash,
                "xp": new_xp,
                "level": new_level
            }},
            upsert=True
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if amount > 0:
            text = f"🕶️ `{user.first_name}` — {scenario} **${amount:,}**! 💵"
        else:
            text = f"🚨 `{user.first_name}` — {scenario} **${abs(amount):,}** fine by federal agents! 🚓"

        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🏆 LEADERBOARD COMMAND (`/top` & `/leaderboard`)
    # ============================================================
    @app.on_message(filters.command(["top", "leaderboard", "mafiyatop"]) & filters.group)
    async def leaderboard_cmd(client, message: Message):
        args = message.command
        mode = args[1].lower() if len(args) > 1 else "global"

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if mode == "global":
            # Fetch top 10 users globally by cash + bank (Net worth)
            cursor = db.mafiya_users.find().sort([("cash", -1), ("level", -1)]).limit(10)
            top_users = await cursor.to_list(length=10)

            if not top_users:
                return await message.reply_text("🏆 **No underworld lords found in global records yet!**", reply_markup=back_markup)

            text = "🌍 **TOP 10 GLOBAL MAFIYA LORDS** 👑\n\n"
            for index, u in enumerate(top_users, start=1):
                name = u.get("name", "Unknown")
                cash = u.get("cash", 0)
                level = u.get("level", 1)
                
                medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"#{index}"
                text += f"{medal} **{name}** — Lv. `{level}` | 💵 `${cash:,}`\n"

            text += "\n_Tip: Use `/crime` to earn cash and climb the leaderboard!_"
            await message.reply_text(text, reply_markup=back_markup)

        else:
            await message.reply_text(
                "📊 **MAFIYA LEADERBOARD USAGE**\n\n"
                "• `/top global` — View top 10 global criminals across all groups.\n"
                "• Use `/crime` or `/rob` to increase your wealth!",
                reply_markup=back_markup
            )

    # ============================================================
    # 🛒 SHOP COMMAND (`/shop`)
    # ============================================================
    @app.on_message(filters.command("shop") & filters.group)
    async def mafiya_shop_cmd(client, message: Message):
        text = (
            "🛒 **UNDERWORLD BLACK MARKET SHOP**\n\n"
            "• **Glock-19** — `$5,000` (Use `/buy glock`)\n"
            "• **Body Armor** — `$10,000` (Use `/buy armor`)\n"
            "• **Master Lockpick** — `$2,500` (Use `/buy lockpick`)\n"
            "• **Encrypted Laptop** — `$15,000` (Use `/buy laptop`)\n\n"
            "_Equip yourself to dominate the streets!_"
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(text, reply_markup=back_markup)
