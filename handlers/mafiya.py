# ============================================================
# 🏴‍☠️ MAFIYA & LEADERBOARD MODULE (ROSE STYLE & FULL POWER)
# ============================================================

__mod_name__ = "🏴‍☠️ ᴍᴀғɪʏᴀ"

__help__ = """
*🏴‍☠️ ᴍᴀғɪʏᴀ ᴍᴏᴅᴜʟᴇ* — Rise through the criminal underworld, earn cash, level up, and compete on the global and group leaderboards!

Commands:
• `/mafiya` or `/profile` — View your criminal profile, net worth, and stats.
• `/crime` — Commit a risky crime to earn cash and XP.
• `/chori <reply>` — Attempt to pickpocket/rob another user in the chat.
• `/shop` — View the underworld black market shop.
• `/top` or `/leaderboard` — View top 10 global criminals!
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

        user_id = user.id

        # Fetch user stats from database
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
    # 🥷 CHORI / PICKPOCKET COMMAND (`/chori`)
    # ============================================================
    @app.on_message(filters.command("chori") & filters.group)
    async def chori_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("⚠️ **Please reply to someone's message to do `chori` (rob) from them!**")

        target_user = message.reply_to_message.from_user
        if target_user.id == user.id:
            return await message.reply_text("❌ **Arey bhai, khud ki hi jeb kaatoge kya? Kisi aur ko target karo!** 🤡")

        if target_user.is_bot:
            return await message.reply_text("❌ **Bots ke paas cash nahi hota dost!** 🤖")

        # Fetch robber data
        robber_data = await db.mafiya_users.find_one({"user_id": user.id})
        if not robber_data:
            robber_data = {"cash": 1000, "xp": 0, "level": 1}
            await db.mafiya_users.update_one({"user_id": user.id}, {"$set": robber_data}, upsert=True)

        # Fetch target data
        target_data = await db.mafiya_users.find_one({"user_id": target_user.id})
        if not target_data:
            target_data = {"cash": 1000, "xp": 0, "level": 1}
            await db.mafiya_users.update_one({"user_id": target_user.id}, {"$set": target_data}, upsert=True)

        target_cash = target_data.get("cash", 1000)
        if target_cash < 200:
            return await message.reply_text(f"⚠️ **{target_user.first_name} ke paas chori karne ke liye kafi cash nahi hai!** 🪙")

        # Success rate calculation (50% chance)
        success = random.choice([True, False])
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if success:
            steal_amount = random.randint(100, min(800, target_cash // 2))
            
            # Update robber cash
            await db.mafiya_users.update_one(
                {"user_id": user.id},
                {"$inc": {"cash": steal_amount, "xp": 15}}
            )
            # Update target cash
            await db.mafiya_users.update_one(
                {"user_id": target_user.id},
                {"$inc": {"cash": -steal_amount}}
            )

            await message.reply_text(
                f"🥷✨ **Successful Chori!**\n\n"
                f"• `{user.first_name}` ne chupke se `{target_user.first_name}` ki jeb se **${steal_amount:,}** chura liye! 💵💸",
                reply_markup=back_markup
            )
        else:
            penalty = random.randint(100, 300)
            # Update robber penalty
            await db.mafiya_users.update_one(
                {"user_id": user.id},
                {"$inc": {"cash": -penalty}}
            )

            await message.reply_text(
                f"🚨👮‍♂️ **Chori Failed!**\n\n"
                f"• `{target_user.first_name}` ne pakad liya! `{user.first_name}` ko bhaagte waqt fine ke roop me **${penalty:,}** gavane pade! 🏃‍♂️💨",
                reply_markup=back_markup
            )

    # ============================================================
    # 🏆 LEADERBOARD COMMAND (`/top` & `/leaderboard`)
    # ============================================================
    @app.on_message(filters.command(["top", "leaderboard", "mafiyatop"]) & filters.group)
    async def leaderboard_cmd(client, message: Message):
        args = message.command
        mode = args[1].lower() if len(args) > 1 else "global"

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if mode == "global":
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

            text += "\n_Tip: Use `/crime` or `/chori` to earn cash and climb the leaderboard!_"
            await message.reply_text(text, reply_markup=back_markup)

        else:
            await message.reply_text(
                "📊 **MAFIYA LEADERBOARD USAGE**\n\n"
                "• `/top global` — View top 10 global criminals across all groups.\n"
                "• Use `/crime` or `/chori` to increase your wealth!",
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
