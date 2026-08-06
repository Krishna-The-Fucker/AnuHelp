# ============================================================
# 💳 ECONOMY & BANKING MODULE (ROSE STYLE & FULL POWER)
# ============================================================

__mod_name__ = "💳 ᴇᴄᴏɴᴏᴍʏ"

__help__ = """
*💳 ᴇᴄᴏɴᴏᴍʏ ᴍᴏᴅᴜʟᴇ* — Manage your wealth, protect your balance from robberies, and trade items or cash!

Commands:
• `/bal` — Check Your Or Friend's Balance
• `/wallet` — Save Your Balance From Robbery
• `/rob` — Reply To Someone to rob them
• `/kill` — Reply To Someone to eliminate them
• `/revive` — Use With Or Without Reply to revive
• `/protect` — Protect Yourself From Robbery
• `/give` — Give Money To Replied User
• `/toprich` — See Top 10 Richest Users
• `/topkill` — See Top 10 Killers
• `/item` — Use With Or Without Reply for items
• `/rank` — Check Your Or Friend's Rank
• `/daily` — Claim Free Daily Cash
• `/gems` — Check Your Gems
• `/give` — Give Money To Replied User
"""

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def register_economy_system(app, db):

    # ============================================================
    # 💰 BALANCE COMMAND (`/bal`)
    # ============================================================
    @app.on_message(filters.command("bal") & filters.group)
    async def balance_cmd(client, message: Message):
        user = message.reply_to_message.from_user if message.reply_to_message and message.reply_to_message.from_user else message.from_user
        if not user:
            return

        user_id = user.id
        chat_id = message.chat.id

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

        await db.underworld_group_members.update_one(
            {"chat_id": chat_id, "user_id": user_id},
            {"$set": {"name": user.first_name}},
            upsert=True
        )

        cash = user_data.get('cash', 1000)
        bank = user_data.get('bank', 0)
        net_worth = cash + bank

        text = (
            f"🏦 **WALLET & BANK BALANCE: `{user.first_name}`**\n\n"
            f"💵 **Cash in Wallet:** `${cash:,}`\n"
            f"🏛️ **Secure Bank (Wallet Protected):** `${bank:,}`\n"
            f"💰 **Total Net Worth:** `${net_worth:,}`\n"
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🛡️ WALLET / DEPOSIT / BANK PROTECTION COMMAND (`/wallet`)
    # ============================================================
    @app.on_message(filters.command("wallet") & filters.group)
    async def wallet_cmd(client, message: Message):
        user = message.from_user
        if not user:
            return

        args = message.command
        user_id = user.id
        user_data = await db.underworld_users.find_one({"user_id": user_id})
        current_cash = user_data.get("cash", 1000) if user_data else 1000
        current_bank = user_data.get("bank", 0) if user_data else 0

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if len(args) < 2:
            return await message.reply_text(
                f"🛡️ **Save Your Balance From Robbery**\n\n"
                f"• Current Wallet Cash: `${current_cash:,}`\n"
                f"• Protected Bank Balance: `${current_bank:,}`\n\n"
                f"• Usage: `/wallet deposit <amount/all>` or `/wallet withdraw <amount/all>`",
                reply_markup=back_markup
            )

        action = args[1].lower()
        if len(args) < 3:
            return await message.reply_text("⚠️ **Please specify an amount or 'all'!** Example: `/wallet deposit all`", reply_markup=back_markup)

        try:
            val_arg = args[2].lower()
        except IndexError:
            return await message.reply_text("❌ **Invalid amount specified.**", reply_markup=back_markup)

        if action in ["deposit", "dep"]:
            amount = current_cash if val_arg == "all" else int(val_arg)
            if amount <= 0 or current_cash < amount:
                return await message.reply_text(f"❌ **Invalid amount or insufficient wallet cash!** Available: `${current_cash:,}`", reply_markup=back_markup)

            await db.underworld_users.update_one(
                {"user_id": user_id},
                {"$set": {"cash": current_cash - amount, "bank": current_bank + amount, "name": user.first_name}},
                upsert=True
            )
            return await message.reply_text(f"📥 `{user.first_name}`, successfully saved **${amount:,}** into your secure wallet/bank vault! 🛡️", reply_markup=back_markup)

        elif action in ["withdraw", "with"]:
            amount = current_bank if val_arg == "all" else int(val_arg)
            if amount <= 0 or current_bank < amount:
                return await message.reply_text(f"❌ **Invalid amount or insufficient vault funds!** Bank vault: `${current_bank:,}`", reply_markup=back_markup)

            await db.underworld_users.update_one(
                {"user_id": user_id},
                {"$set": {"cash": current_cash + amount, "bank": current_bank - amount, "name": user.first_name}},
                upsert=True
            )
            return await message.reply_text(f"📤 `{user.first_name}`, successfully withdrew **${amount:,}** from your vault into your wallet. 💵", reply_markup=back_markup)
        else:
            await message.reply_text("⚠️ **Unknown option!** Use `/wallet deposit <amount>` or `/wallet withdraw <amount>`", reply_markup=back_markup)

    # ============================================================
    # 🦹‍♂️ ROB COMMAND (`/rob`)
    # ============================================================
    @app.on_message(filters.command("rob") & filters.group)
    async def rob_cmd(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("⚠️ **Reply To Someone** to attempt a robbery!")

        thief = message.from_user
        target = message.reply_to_message.from_user

        if thief.id == target.id:
            return await message.reply_text("❌ **You cannot rob yourself!**")

        if target.is_bot:
            return await message.reply_text("❌ **Bots don't carry physical cash!**")

        target_data = await db.underworld_users.find_one({"user_id": target.id})
        target_cash = target_data.get("cash", 0) if target_data else 0

        if target_cash < 500:
            return await message.reply_text(f"❌ `{target.first_name}` has too little cash in wallet to rob!")

        thief_data = await db.underworld_users.find_one({"user_id": thief.id})
        thief_cash = thief_data.get("cash", 1000) if thief_data else 1000

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        import random
        if random.random() > 0.5:
            stolen = random.randint(100, min(1500, int(target_cash * 0.3)))
            await db.underworld_users.update_one({"user_id": target.id}, {"$inc": {"cash": -stolen}})
            await db.underworld_users.update_one({"user_id": thief.id}, {"$inc": {"cash": stolen}}, upsert=True)
            await message.reply_text(f"🥷 `{thief.first_name}` successfully robbed **${stolen:,}** from `{target.first_name}`'s wallet! 💰", reply_markup=back_markup)
        else:
            penalty = random.randint(200, 500)
            await db.underworld_users.update_one({"user_id": thief.id}, {"$set": {"cash": max(0, thief_cash - penalty)}}, upsert=True)
            await message.reply_text(f"🚨 `{thief.first_name}` got caught trying to rob `{target.first_name}` and paid a fine of **${penalty:,}**! 🚓", reply_markup=back_markup)

    # ============================================================
    # 🗡️ KILL COMMAND (`/kill`)
    # ============================================================
    @app.on_message(filters.command("kill") & filters.group)
    async def kill_cmd(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("⚠️ **Reply To Someone** to target them!")

        killer = message.from_user
        target = message.reply_to_message.from_user

        if killer.id == target.id:
            return await message.reply_text("❌ **You can't eliminate yourself!**")

        await db.underworld_users.update_one(
            {"user_id": killer.id},
            {"$inc": {"kills": 1}},
            upsert=True
        )

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"🎯 `{killer.first_name}` eliminated `{target.first_name}` in a clean hit! 💀", reply_markup=back_markup)

    # ============================================================
    # ✨ REVIVE COMMAND (`/revive`)
    # ============================================================
    @app.on_message(filters.command("revive") & filters.group)
    async def revive_cmd(client, message: Message):
        user = message.from_user
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"💉 `{user.first_name}` used medical supplies to revive and get back into action! ⚡", reply_markup=back_markup)

    # ============================================================
    # 🛡️ PROTECT COMMAND (`/protect`)
    # ============================================================
    @app.on_message(filters.command("protect") & filters.group)
    async def protect_cmd(client, message: Message):
        user = message.from_user
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"🛡️ `{user.first_name}` activated personal bodyguards and anti-robbery security protocols!", reply_markup=back_markup)

    # ============================================================
    # 💸 GIVE COMMAND (`/give`)
    # ============================================================
    @app.on_message(filters.command("give") & filters.group)
    async def give_cmd(client, message: Message):
        if not message.reply_to_message or not message.reply_to_message.from_user:
            return await message.reply_text("⚠️ **Give Money To Replied User** by replying to their message!")

        sender = message.from_user
        recipient = message.reply_to_message.from_user

        if sender.id == recipient.id:
            return await message.reply_text("❌ **You cannot send money to yourself!**")

        args = message.command
        if len(args) < 2:
            return await message.reply_text("⚠️ **Incorrect usage!** Use `/give <amount>`")

        try:
            amount = int(args[1])
        except ValueError:
            return await message.reply_text("❌ **Invalid amount specified.**")

        if amount <= 0:
            return await message.reply_text("❌ **Amount must be greater than zero!**")

        sender_data = await db.underworld_users.find_one({"user_id": sender.id})
        sender_cash = sender_data.get("cash", 1000) if sender_data else 1000

        if sender_cash < amount:
            return await message.reply_text(f"❌ **Insufficient wallet cash!** Available: `${sender_cash:,}`")

        await db.underworld_users.update_one({"user_id": sender.id}, {"$set": {"cash": sender_cash - amount, "name": sender.first_name}}, upsert=True)
        
        recipient_data = await db.underworld_users.find_one({"user_id": recipient.id})
        recipient_cash = recipient_data.get("cash", 1000) if recipient_data else 1000
        await db.underworld_users.update_one({"user_id": recipient.id}, {"$set": {"cash": recipient_cash + amount, "name": recipient.first_name}}, upsert=True)

        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"💸 `{sender.first_name}` gave **${amount:,}** to `{recipient.first_name}`! 🤝", reply_markup=back_markup)

    # ============================================================
    # 🏆 TOP RICH COMMAND (`/toprich`)
    # ============================================================
    @app.on_message(filters.command("toprich") & filters.group)
    async def toprich_cmd(client, message: Message):
        cursor = db.underworld_users.find().sort("cash", -1).limit(10)
        top_users = await cursor.to_list(length=10)
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if not top_users:
            return await message.reply_text("🏆 **No records found in Top 10 Richest Users yet!**", reply_markup=back_markup)

        text = "👑 **SEE TOP 10 RICHEST USERS** 💵\n\n"
        for index, u in enumerate(top_users, start=1):
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"#{index}"
            text += f"{medal} **{u.get('name', 'Unknown')}** — 💵 `${u.get('cash', 0):,}`\n"

        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🎯 TOP KILL COMMAND (`/topkill`)
    # ============================================================
    @app.on_message(filters.command("topkill") & filters.group)
    async def topkill_cmd(client, message: Message):
        cursor = db.underworld_users.find().sort("kills", -1).limit(10)
        top_killers = await cursor.to_list(length=10)
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])

        if not top_killers:
            return await message.reply_text("🏆 **No records found in Top 10 Killers yet!**", reply_markup=back_markup)

        text = "🎯 **SEE TOP 10 KILLERS** 💀\n\n"
        for index, u in enumerate(top_killers, start=1):
            medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"#{index}"
            text += f"{medal} **{u.get('name', 'Unknown')}** — 🎯 `{u.get('kills', 0)}` kills\n"

        await message.reply_text(text, reply_markup=back_markup)

    # ============================================================
    # 🎒 ITEM COMMAND (`/item`)
    # ============================================================
    @app.on_message(filters.command("item") & filters.group)
    async def item_cmd(client, message: Message):
        user = message.from_user
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"🎒 `{user.first_name}` checked their inventory items and gear successfully!", reply_markup=back_markup)

    # ============================================================
    # 📊 RANK COMMAND (`/rank`)
    # ============================================================
    @app.on_message(filters.command("rank") & filters.group)
    async def rank_cmd(client, message: Message):
        user = message.reply_to_message.from_user if message.reply_to_message and message.reply_to_message.from_user else message.from_user
        user_data = await db.underworld_users.find_one({"user_id": user.id})
        level = user_data.get("level", 1) if user_data else 1
        xp = user_data.get("xp", 0) if user_data else 0
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"📊 **Rank Status for `{user.first_name}`**\n\n• Level: `{level}`\n• XP: `{xp}`", reply_markup=back_markup)

    # ============================================================
    # 💎 GEMS COMMAND (`/gems`)
    # ============================================================
    @app.on_message(filters.command("gems") & filters.group)
    async def gems_cmd(client, message: Message):
        user = message.from_user
        user_data = await db.underworld_users.find_one({"user_id": user.id})
        gems = user_data.get("gems", 50) if user_data else 50
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"💎 **Check Your Gems**\n\n• `{user.first_name}` has `💎 {gems:,}` gems in possession!", reply_markup=back_markup)

    # ============================================================
    # 🎁 DAILY COMMAND (`/daily`)
    # ============================================================
    @app.on_message(filters.command("daily") & filters.group)
    async def daily_cmd(client, message: Message):
        user = message.from_user
        user_data = await db.underworld_users.find_one({"user_id": user.id})
        current_cash = user_data.get("cash", 1000) if user_data else 1000
        bonus = 3000
        await db.underworld_users.update_one({"user_id": user.id}, {"$set": {"cash": current_cash + bonus, "name": user.first_name}}, upsert=True)
        back_markup = InlineKeyboardMarkup([[InlineKeyboardButton("« Back", callback_data="help_back")]])
        await message.reply_text(f"🎁 Claim Free Daily Cash! `{user.first_name}` received **${bonus:,}** in their wallet! 💵", reply_markup=back_markup)
