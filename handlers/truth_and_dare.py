def register_truth_and_dare(app):
    from pyrogram import filters
    from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
    import random

    # Massive Question & Dare Database (Kabhi khatm na ho)
    TRUTHS = [
        "What is your most embarrassing moment in public?",
        "What is the weirdest habit you have?",
        "If you could swap lives with anyone for a day, who would it be?",
        "What is the biggest lie you've ever told your parents?",
        "What is your secret crush right now?",
        "What was the last thing you searched for on your phone?",
        "Have you ever talked to yourself in the mirror? What did you say?",
        "What is the most childish thing you still do?",
        "If you were invisible for a day, what would you do?",
        "What is something you are glad your family doesn't know about you?",
        "What is the most awkward text you've ever sent to the wrong person?",
        "If you had to live in a movie world, which one would you choose?",
        "What is your biggest fear that you rarely tell anyone?",
        "Have you ever blamed someone else for something you did?",
        "What is the weirdest food combination you secretly love?",
        "If you won a million dollars today, what is the first thing you would buy?",
        "What is a secret talent you possess that nobody knows about?",
        "Who is the most annoying person in this group chat?",
        "What is the funniest nickname you've ever had?",
        "If you could change one thing about your past, what would it be?"
    ]

    DARES = [
        "Send a random emoji to the last person you chatted with on Telegram.",
        "Type your entire message using only your nose for the next 10 minutes.",
        "Change your profile bio to something funny chosen by the group.",
        "Sing a song of your choice and send a short audio or voice note in the group.",
        "Send a funny selfie or a photo of your current view right now.",
        "Compliment the person above you in the chat in the weirdest way possible.",
        "Speak in a funny accent for your next 3 messages.",
        "Admit a silly secret out loud in the group.",
        "Do 10 push-ups right now and send a proof message.",
        "Send a meme that perfectly describes your current mood.",
        "Write a romantic poem praising a random object on your desk.",
        "Send a voice note laughing like a villain for 5 seconds.",
        "Change your chat username/display name to a funny cartoon character for 1 hour.",
        "Pretend to be a news reporter and report live about what is happening around you in a voice note.",
        "Send the 5th photo from your phone's gallery without looking at it first.",
        "Type your name backwards and send it in the chat.",
        "Pretend to be a cat and reply 'Meow' to the next 3 messages you receive.",
        "Write an apology letter to a fictional character for something stupid.",
        "Ask a random stranger on another app or group a totally weird question.",
        "Do your best impression of a famous celebrity and send an audio."
    ]

    # Users ki history track karne ke liye dictionary
    USER_HISTORY = {}

    def get_unique_question(user_id, category_type):
        if user_id not in USER_HISTORY:
            USER_HISTORY[user_id] = {"truths": [], "dares": []}

        if category_type == "truth":
            source_list = TRUTHS
            used_list = USER_HISTORY[user_id]["truths"]
        else:
            source_list = DARES
            used_list = USER_HISTORY[user_id]["dares"]

        # Agar saare questions/dares khatm ho gaye hain, toh history clear kar do (Infinite Loop / Never Ends)
        if len(used_list) >= len(source_list):
            used_list.clear()

        # Bachen hue un-used items me se random chuno
        available_items = [item for item in source_list if item not in used_list]
        selected_item = random.choice(available_items)
        
        used_list.append(selected_item)
        return selected_item

    # =========================
    # /TRUTH COMMAND
    # =========================
    @app.on_message(filters.command("truth") & (filters.group | filters.private))
    async def truth_handler(client, message: Message):
        user = message.from_user
        question = get_unique_question(user.id, "truth")

        text = (
            f"🎯 **Truth for {user.mention}**\n\n"
            f"💬 *{question}*"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Another Truth", callback_data="td_truth"),
                InlineKeyboardButton("🔥 Dare Instead", callback_data="td_dare")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="td_close")
            ]
        ])

        await message.reply(text, reply_markup=keyboard)

    # =========================
    # /DARE COMMAND
    # =========================
    @app.on_message(filters.command("dare") & (filters.group | filters.private))
    async def dare_handler(client, message: Message):
        user = message.from_user
        dare_task = get_unique_question(user.id, "dare")

        text = (
            f"🔥 **Dare for {user.mention}**\n\n"
            f"⚡ *{dare_task}*"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎯 Truth Instead", callback_data="td_truth"),
                InlineKeyboardButton("🔄 Another Dare", callback_data="td_dare")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="td_close")
            ]
        ])

        await message.reply(text, reply_markup=keyboard)

    # =========================
    # /TD COMMAND
    # =========================
    @app.on_message(filters.command(["td", "truthordare"]) & (filters.group | filters.private))
    async def td_handler(client, message: Message):
        user = message.from_user
        
        text = (
            f"🎲 **Truth or Dare Game**\n\n"
            f"Hey {user.mention}, choose your path!"
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎯 Truth", callback_data="td_truth"),
                InlineKeyboardButton("🔥 Dare", callback_data="td_dare")
            ],
            [
                InlineKeyboardButton("❌ Close", callback_data="td_close")
            ]
        ])

        await message.reply(text, reply_markup=keyboard)

    # =========================
    # CALLBACK HANDLERS
    # =========================
    @app.on_callback_query(filters.regex("^td_"))
    async def td_callbacks(client, query: CallbackQuery):
        data = query.data
        user = query.from_user

        if data == "td_truth":
            question = get_unique_question(user.id, "truth")
            text = (
                f"🎯 **Truth for {user.mention}**\n\n"
                f"💬 *{question}*"
            )
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🔄 Another Truth", callback_data="td_truth"),
                    InlineKeyboardButton("🔥 Dare Instead", callback_data="td_dare")
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="td_close")
                ]
            ])
            await query.message.edit_text(text, reply_markup=keyboard)
            await query.answer("Here is your fresh Truth!")

        elif data == "td_dare":
            dare_task = get_unique_question(user.id, "dare")
            text = (
                f"🔥 **Dare for {user.mention}**\n\n"
                f"⚡ *{dare_task}*"
            )
            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🎯 Truth Instead", callback_data="td_truth"),
                    InlineKeyboardButton("🔄 Another Dare", callback_data="td_dare")
                ],
                [
                    InlineKeyboardButton("❌ Close", callback_data="td_close")
                ]
            ])
            await query.message.edit_text(text, reply_markup=keyboard)
            await query.answer("Here is your fresh Dare!")

        elif data == "td_close":
            await query.message.delete()
            await query.answer("Game closed!")
