# ============================================================
# 🎰 UNDERWORLD CASINO & HEIST MODULE (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🎮 ᴜɴᴅᴇʀᴡᴏʀʟᴅ"

__help__ = """
*🎮 ᴜɴᴅᴇʀᴡᴏʀʟᴅ ᴍᴏᴅᴜʟᴇ* — A fun, casual underworld simulation and casino game for your group chat! Test your luck, spin the mafia wheel, and climb the leaderboards.

Commands:
• `/profile` or `/mafiya` — View your criminal profile and balance.
• `/daily` — Claim your daily underground cash bonus.
• `/spin <amount>` — Spin the illegal casino wheel of fortune!
• `/dice <amount>` — Roll high-stakes dice against the house.
• `/top <global/group>` — View top 10 richest players globally or in this group!
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import random

def register_underworld_system(app, db):

    # ============================================================
    # 👤 PROFILE / MAFIYA COMMAND (`/profile` & `/mafiya`)
    # ============================================================
    @app.on_message(filters.command(["profile", "mafiya"]) & filters.group)
    async def profile_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        chat_id = message.chat.id
        user_id = user.id

        user_data = await db.underworld_users.find_one({"user_id": user_id})
        
        if not user_data:
            user_data = {
                "user_id": user_id,
                "name": user.first_name,
                "cash": 1000,
                "bank": 0,
                "level": 1,
                "xp": 0
            }
            await db.underworld_users.update_one(
                {"user_id": user_id},
                {"$set": user_data},
                upsert=True
            )

        # Track user in this group for local leaderboards
        await db.underworld_group_members.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"name": user.first_name}},
            upsert=True
        )

        cash = user_data.get('cash', 1000)
        bank = user_data.get('bank', 0)
        net_worth = cash + bank

        text = (
            f"👤 **UNDERWORLD PROFILE: `{user.first_name}`**\n\n"
            f"💵 **Cash:** `${cash:,}`\n"
            f"🏦 **Bank:** `${bank:,}`\n"
            f"💰 **Net Worth:** `${net_worth:,}`\n"
            f"📊 **Level:** `{user_data.get('level', 1)}`\n"
            f"✨ **XP:** `{user_data.get('xp', 0)}`\n"
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🎁 DAILY BONUS COMMAND (`/daily`)
    # ============================================================
    @app.on_message(filters.command("daily") & filters.group)
    async def daily_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        user_id = user.id
        user_data = await db.underworld_users.find_one({"user_id": user_id})
        if not user_data:
            user_data = {"cash": 1000}

        bonus = 2500
        new_cash = user_data.get("cash", 1000) + bonus

        await db.underworld_users.update_one(
            {"user_id": user_id},
            {"$set": {"name": user.first_name, "cash": new_cash}},
            upsert=True
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(
            f"🎁 `{user.first_name}`, you collected your daily underground allowance of **${bonus:,}**! 💵",
            reply_markup=back_markup
        )

    # ============================================================
    # 🎡 SPIN THE WHEEL CASINO (`/spin <amount>`)
    # ============================================================
    @app.on_message(filters.command("spin") & filters.group)
    async def spin_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        args = message.command
        if len(args) < 2:
            return await message.reply_text("⚠️ **Incorrect usage!** Use `/spin <amount>` (e.g., `/spin 500`)")

        try:
            bet = int(args[1])
        except ValueError:
            return await message.reply_text("❌ **Invalid amount! Must be a valid number.**")

        if bet <= 0:
            return await message.reply_text("❌ **Bet amount must be greater than zero!**")

        user_id = user.id
        user_data = await db.underworld_users.find_one({"user_id": user_id})
        current_cash = user_data.get("cash", 1000) if user_data else 1000

        if current_cash < bet:
            return await message.reply_text(f"❌ **You don't have enough cash!** Your balance: `${current_cash:,}`")

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        # Spin multipliers: 0x, 0.5x, 1x, 2x, 3x, 5x
        multipliers = [0, 0, 0.5, 1, 1, 2, 2, 3, 5]
        mult = random.choice(multipliers)
        winnings = int(bet * mult)
        net_change = winnings - bet

        new_cash = current_cash + net_change
        await db.underworld_users.update_one(
            {"user_id": user_id},
            {"$set": {"cash": max(0, new_cash), "name": user.first_name}},
            upsert=True
        )

        if mult == 0:
            text = f"🎡 `{user.first_name}` spun the wheel, hit a dry spot, and lost **${bet:,}**! 💸"
        elif mult < 1:
            text = f"🎡 `{user.first_name}` spun the wheel, got a partial payout, and lost **${abs(net_change):,}**."
        elif mult == 1:
            text = f"🎡 `{user.first_name}` spun the wheel and broke even on their **${bet:,}** bet!"
        else:
            text = f"🎉 `{user.first_name}` hit a **{mult}x multiplier** on the casino wheel and won **${winnings:,}**! 💵🔥"

        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🎲 HIGH-STAKES DICE (`/dice <amount>`)
    # ============================================================
    @app.on_message(filters.command("dice") & filters.group)
    async def dice_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        args = message.command
        if len(args) < 2:
            return await message.reply_text("⚠️ **Incorrect usage!** Use `/dice <amount>` (e.g., `/dice 500`)")

        try:
            bet = int(args[1])
        except ValueError:
            return await message.reply_text("❌ **Invalid amount! Must be a valid number.**")

        if bet <= 0:
            return await message.reply_text("❌ **Bet amount must be greater than zero!**")

        user_id = user.id
        user_data = await db.underworld_users.find_one({"user_id": user_id})
        current_cash = user_data.get("cash", 1000) if user_data else 1000

        if current_cash < bet:
            return await message.reply_text(f"❌ **You don't have enough cash!** Your balance: `${current_cash:,}`")

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        user_roll = random.randint(1, 6)
        dealer_roll = random.randint(1, 6)

        if user_roll > dealer_roll:
            new_cash = current_cash + bet
            text = f"🎲 `{user.first_name}` rolled a `{user_roll}` vs Dealer's `{dealer_roll}`. You won **${bet:,}**! 🏆"
        elif user_roll < dealer_roll:
            new_cash = current_cash - bet
            text = f"🎲 `{user.first_name}` rolled a `{user_roll}` vs Dealer's `{dealer_roll}`. You lost **${bet:,}**! 💀"
        else:
            new_cash = current_cash
            text = f"🎲 Both rolled a `{user_roll}`! It's a tie, your bet is returned."

        await db.underworld_users.update_one(
            {"user_id": user_id},
            {"$set": {"cash": max(0, new_cash), "name": user.first_name}},
            upsert=True
        )

        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🏆 LEADERBOARD COMMAND (`/top` & `/leaderboard`)
    # ============================================================
    @app.on_message(filters.command(["top", "leaderboard", "underworldtop"]) & filters.group)
    async def leaderboard_cmd(client, message: Message):
        args = message.command
        chat_id = message.chat.id
        mode = args[1].lower() if len(args) > 1 else "global"

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if mode == "global" or mode == "g":
            cursor = db.underworld_users.find().sort("cash", -1).limit(10)
            top_users = await cursor.to_list(length=10)

            if not top_users:
                return await message.reply_text("🏆 **No players found in global records yet!**", reply_markup=back_markup)

            text = "🌍 **TOP 10 GLOBAL CASINO RICH LIST** 👑\n\n"
            for index, u in enumerate(top_users, start=1):
                name = u.get("name", "Unknown")
                cash = u.get("cash", 0)
                level = u.get("level", 1)
                
                medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"#{index}"
                text += f"{medal} **{name}** — Lv. `{level}` | 💵 `${cash:,}`\n"

            text += "\n_Use `/top group` to view rankings for this chat!_"
            await message.reply_text(text, reply_markup=back_markup)

        elif mode == "group" or mode == "local" or mode == "chat":
            group_members = await db.underworld_group_members.find({"chat_id": chat_id}).to_list(length=100)
            member_ids = [m["user_id"] for m in group_members]

            if not member_ids:
                return await message.reply_text("🏆 **No active players registered in this group yet! Use `/daily` to start.**", reply_markup=back_markup)

            cursor = db.underworld_users.find({"user_id": {"$in": member_ids}}).sort("cash", -1).limit(10)
            top_group_users = await cursor.to_list(length=10)

            if not top_group_users:
                return await message.reply_text("🏆 **No financial data found for members of this group!**", reply_markup=back_markup)

            group_title = message.chat.title or "this group"
            text = f"🏠 **TOP 10 RICH LIST IN {group_title.upper()}** 👑\n\n"
            for index, u in enumerate(top_group_users, start=1):
                name = u.get("name", "Unknown")
                cash = u.get("cash", 0)
                level = u.get("level", 1)
                
                medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"#{index}"
                text += f"{medal} **{name}** — Lv. `{level}` | 💵 `${cash:,}`\n"

            text += "\n_Use `/top global` to view worldwide rankings!_"
            await message.reply_text(text, reply_markup=back_markup)

        else:
            await message.reply_text(
                "📊 **LEADERBOARD USAGE**\n\n"
                "• `/top global` — View top 10 richest players across all groups.\n"
                "• `/top group` — View top 10 richest players within this specific group chat.\n\n"
                "_Use `/daily` or `/spin` to build your wealth!_",
                reply_markup=back_markup
            )
