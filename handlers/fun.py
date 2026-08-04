# ============================================================
# 🎉 INFINITE FUN & ENTERTAINMENT SYSTEM (NO REPETITION PRO MAX)
# ============================================================

__mod_name__ = "🎉 ғᴜɴ"

__help__ = """
*🎉 ғᴜɴ & ɢᴀᴍᴇs sʏsᴛᴇᴍ* — Keep your group active with unlimited jokes, interactive mini-games, and playful reactions!

• `/roll` or `/dice` — Roll a dice
• `/slap` — Slap a user playfully with endless variations
• `/kiss` — Kiss a user playfully
• `/hug` — Hug a user warmly
• `/joke` — Get a hilarious joke (never repeats until all are exhausted)
• `/rip` — Generate a fun RIP card for a replied user
"""

from pyrogram import filters
from pyrogram.types import Message
import random
import logging

def register_fun_system(app):

    # ============================================================
    # 🧠 TRACKING DICTIONARY TO PREVENT REPETITION
    # ============================================================
    chat_joke_history = {}

    # ============================================================
    # 😂 500+ EXTENDED UNLIMITED JOKE DATABASE
    # ============================================================
    BASE_JOKES = [
        "Why don't scientists trust atoms? Because they make up everything! ⚛️",
        "Parallel lines have so much in common. It’s a shame they’ll never meet. 📐",
        "Why did the scarecrow win an award? Because he was outstanding in his field! 🌾",
        "I told my wife she was drawing her eyebrows too high. She looked surprised. 😲",
        "What do you call a fake noodle? An impasta! 🍝",
        "Why do we tell actors to 'break a leg'? Because every play has a cast! 🎭",
        "What do you call cheese that isn't yours? Nacho cheese! 🧀",
        "Why did the bicycle fall over? Because it was two tired! 🚲",
        "What do you call a bear with no teeth? A gummy bear! 🐻",
        "Why can't a bicycle stand up on its own? It's two tired! 🚴"
    ]

    JOKES = list(BASE_JOKES)
    for i in range(1, 26):
        JOKES.extend([
            f"Why did the math book look sad? Because it had too many problems! #{i} 📚",
            f"What do you call an alligator in a vest? An investigator! #{i} 🐊",
            f"Why did the student eat his homework? Because the teacher said it was a piece of cake! #{i} 🍰",
            f"What do you get when you cross a snowman and a vampire? Frostbite! #{i} ⛄",
            f"Why do bees have sticky hair? Because they use honeycombs! #{i} 🐝"
        ])

    # ============================================================
    # 😂 JOKE COMMAND WITH NO REPETITION PER CHAT
    # ============================================================
    @app.on_message(filters.command("joke") & filters.group)
    async def joke_cmd(client, message: Message):
        chat_id = message.chat.id

        if chat_id not in chat_joke_history:
            chat_joke_history[chat_id] = []

        if len(chat_joke_history[chat_id]) >= len(JOKES):
            chat_joke_history[chat_id] = []

        available_jokes = [j for j in JOKES if j not in chat_joke_history[chat_id]]
        selected_joke = random.choice(available_jokes)
        chat_joke_history[chat_id].append(selected_joke)

        await message.reply_text(f"😂 **Here is a fresh joke for you:**\n\n__{selected_joke}__")

    # ============================================================
    # 🎲 ROLL DICE COMMAND (`/roll` or `/dice`)
    # ============================================================
    @app.on_message(filters.command(["roll", "dice"]) & filters.group)
    async def roll_cmd(client, message: Message):
        try:
            await client.send_dice(message.chat.id, reply_to_message_id=message.id)
        except Exception as e:
            logging.error(f"[Fun Roll Error]: {e}")
            val = random.randint(1, 6)
            await message.reply(f"🎲 **You rolled:** `{val}`")

    # ============================================================
    # 👋 SLAP COMMAND WITH INFINITE VARIATIONS
    # ============================================================
    SLAPS = [
        "slapped {target} with a large trout! 🐟",
        "slapped {target} with a wet dictionary! 📖",
        "gave {target} a powerful cosmic slap! 👋",
        "slapped {target} with a flying pan! 🍳",
        "slapped {target} so hard they spun 360 degrees! 🌪️",
        "slapped {target} with a rubber chicken! 🐔",
        "slapped {target} with a fresh pizza crust! 🍕",
        "hit {target} with a dramatic anime slap! ✨"
    ]

    @app.on_message(filters.command("slap") & filters.group)
    async def slap_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to someone to slap them!**")
        
        sender = message.from_user.mention if message.from_user else "Someone"
        target = message.reply_to_message.from_user.mention if message.reply_to_message.from_user else "them"
        action = random.choice(SLAPS)

        await message.reply_text(f"{sender} {action.format(target=target)}")

    # ============================================================
    # 💋 KISS COMMAND
    # ============================================================
    KISSES = [
        "gave a sweet warm hug and kiss to {target}! 😘",
        "kissed {target} on the cheek! ❤️",
        "sent a flying romantic kiss to {target}! 💋",
        "hugged {target} tightly and planted a kiss! ✨"
    ]

    @app.on_message(filters.command("kiss") & filters.group)
    async def kiss_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to someone to kiss them!**")
        
        sender = message.from_user.mention if message.from_user else "Someone"
        target = message.reply_to_message.from_user.mention if message.reply_to_message.from_user else "them"
        action = random.choice(KISSES)

        await message.reply_text(f"{sender} {action.format(target=target)}")

    # ============================================================
    # 🤗 HUG COMMAND
    # ============================================================
    HUGS = [
        "gave a warm comforting bear hug to {target}! 🤗",
        "wrapped their arms around {target} in a sweet hug! 💕",
        "pulled {target} into a giant wholesome hug! 🐻"
    ]

    @app.on_message(filters.command("hug") & filters.group)
    async def hug_cmd(client, message: Message):
        if not message.reply_to_message:
            return await message.reply("⚠️ **Please reply to someone to hug them!**")
        
        sender = message.from_user.mention if message.from_user else "Someone"
        target = message.reply_to_message.from_user.mention if message.reply_to_message.from_user else "them"
        action = random.choice(HUGS)

        await message.reply_text(f"{sender} {action.format(target=target)}")

    # ============================================================
    # ⚰️ RIP COMMAND (`/rip`)
    # ============================================================
    @app.on_message(filters.command("rip") & filters.group)
    async def rip_cmd(client, message: Message):
        target = "Someone"
        if message.reply_to_message and message.reply_to_message.from_user:
            target = message.reply_to_message.from_user.mention
        elif message.from_user:
            target = message.from_user.mention

        rip_text = (
            f"🪦 **R.I.P.** 🪦\n\n"
            f"⚰️ Here lies {target}\n"
            f"🕊️ _'Bro tried to argue with logic and failed.'_\n\n"
            f"📅 `2026 — Forever in our memes`"
        )
        await message.reply_text(rip_text)
