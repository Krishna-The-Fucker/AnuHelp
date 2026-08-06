# ============================================================
# 🎰 UNDERWORLD GAME MODULE (ROSE STYLE & FULL POWER)
# ============================================================

__mod_name = "🎮 ᴜɴᴅᴇʀᴡᴏʀʟᴅ"

__help__ = """
*🎮 ᴜɴᴅᴇʀᴡᴏʀʟᴅ ᴍᴏᴅᴜʟᴇ* — A crime and underworld-themed simulation game for your group chat! Build your empire, commit crimes, and rule the streets.

Commands:
• `/crime` — Commit a risky crime to earn cash and XP.
• `/profile` — View your criminal profile, level, balance, and stats.
• `/rob <reply>` — Attempt to rob another user in the chat.
• `/shop` — View the underworld black market shop for gear.
• `/gang` — Create or manage your own criminal syndicate.
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random
import time

def register_underworld_system(app, db):

    # ============================================================
    # 👤 PROFILE COMMAND (`/profile`)
    # ============================================================
    @app.on_message(filters.command("profile") & filters.group)
    async def profile_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        chat_id = message.chat.id
        user_id = user.id

        # Fetch user stats from database (or defaults)
        user_data = await db.underworld_users.find_one({"chat_id": chat_id, "user_id": user_id})
        
        if not user_data:
            user_data = {
                "cash": 1000,
                "bank": 0,
                "level": 1,
                "xp": 0,
                "reputation": 10,
                "gang": "None"
            }
            await db.underworld_users.update_one(
                {"chat_id": chat_id, "user_id": user_id},
                {"$set": user_data},
                upsert=True
            )

        text = (
            f"👤 **CRIMINAL PROFILE: `{user.first_name}`**\n\n"
            f"💵 **Cash:** `${user_data.get('cash', 0):,}`\n"
            f"🏦 **Bank:** `${user_data.get('bank', 0):,}`\n"
            f"📊 **Level:** `{user_data.get('level', 1)}`\n"
            f"✨ **XP:** `{user_data.get('xp', 0)}`\n"
            f"🔥 **Reputation:** `{user_data.get('reputation', 10)}`\n"
            f"🏴‍☠️ **Syndicate:** `{user_data.get('gang', 'None')}`\n"
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🦹‍♂️ CRIME COMMAND (`/crime`)
    # ============================================================
    crime_scenarios = [
        ("You hacked a local bank ATM and stole", 500, 1500, 20),
        ("You hijacked a luxury sports car and sold it for", 1000, 3000, 40),
        ("You looted a convenience store cash register and got", 200, 600, 10),
        ("You tried to pickpocket a tourist, but got caught and lost", -100, -300, -5),
        ("You successfully ran an underground poker game and made", 800, 2000, 30),
    ]

    @app.on_message(filters.command("crime") & filters.group)
    async def crime_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        chat_id = message.chat.id
        user_id = user.id

        scenario, min_amt, max_amt, xp_gain = random.choice(crime_scenarios)
        amount = random.randint(min_amt, max_amt)

        # Update user stats
        user_data = await db.underworld_users.find_one({"chat_id": chat_id, "user_id": user_id})
        current_cash = user_data.get("cash", 1000) if user_data else 1000
        current_xp = user_data.get("xp", 0) if user_data else 0

        new_cash = max(0, current_cash + amount)
        new_xp = current_xp + max(5, xp_gain)

        await db.underworld_users.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"cash": new_cash, "xp": new_xp}},
            upsert=True
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if amount > 0:
            text = f"🕶️ `{user.first_name}` — {scenario} **${amount:,}**! 💵"
        else:
            text = f"🚨 `{user.first_name}` — {scenario} **${abs(amount):,}** by the cops! 🚓"

        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🛒 SHOP COMMAND (`/shop`)
    # ============================================================
    @app.on_message(filters.command("shop") & filters.group)
    async def shop_cmd(client, message: Message):
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

    # ============================================================
    # 🏴‍☠️ GANG COMMAND (`/gang`)
    # ============================================================
    @app.on_message(filters.command("gang") & filters.group)
    async def gang_cmd(client, message: Message):
        text = (
            "🏴‍☠️ **UNDERWORLD SYNDICATES (GANGS)**\n\n"
            "Build your criminal empire with your friends!\n\n"
            "• `/creategang <name>` — Create a gang for `$50,000`\n"
            "• `/ganginfo` — View your gang status\n"
            "• `/gorg` — Join an existing public syndicate"
        )
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(text, reply_markup=back_markup)
