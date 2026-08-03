def register_github_uploader(app):
    from pyrogram import filters
    from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
    import os
    from github import Github

    # =========================
    # 🔐 TOKEN FETCH & VALIDATION
    # =========================
    async def get_github_client(user_id):
        # 1. Pehle database se check karein ki user ne connect kiya hai ya nahi
        try:
            from db import db
            data = await db.github_tokens.find_one({"user_id": user_id})
            if data and data.get("token") and data.get("repo"):
                return data["token"], data["repo"]
        except:
            pass
        return None, None

    # =========================
    # /GITHUB SETTINGS COMMAND (/ghset)
    # =========================
    @app.on_message(filters.command(["ghset", "githubset"]) & filters.private)
    async def github_set_handler(client, message: Message):
        args = message.text.split(None, 2)
        user_id = message.from_user.id

        if len(args) < 3:
            return await message.reply(
                "⚙️ **GitHub Account Configuration**\n\n"
                "Aapko pehle apna GitHub account connect karna hoga!\n"
                "Is format mein command bhejiye:\n"
                "`/ghset <YOUR_GITHUB_TOKEN> <username/repository>`\n\n"
                "> *Example:* `/ghset ghp_xxxxxxx myname/AnuHelp`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("❓ How to get Token?", url="https://github.com/settings/tokens")]
                ])
            )

        token = args[1].strip()
        repo_name = args[2].strip()

        # Status message
        status_msg = await message.reply("🔄 **Connecting and verifying with GitHub...**")

        # Test connection before saving
        try:
            g = Github(token)
            repo = g.get_repo(repo_name)
            repo_check_name = repo.full_name
        except Exception as e:
            return await status_msg.edit_text(f"❌ **Invalid Token or Repository!**\nError: `{str(e)}`")

        # Save securely to MongoDB Database
        try:
            from db import db
            await db.github_tokens.update_one(
                {"user_id": user_id},
                {"$set": {"token": token, "repo": repo_name}},
                upsert=True
            )
        except Exception as e:
            return await status_msg.edit_text(f"❌ **Database Error:** `{str(e)}`")

        await status_msg.edit_text(
            f"✨ **GitHub Connected Successfully!**\n\n"
            f"• **Repository:** `{repo_check_name}`\n"
            f"• **Status:** Active & Locked to your Account 🔒\n\n"
            f"*Ab aap kisi bhi file par reply karke* `/ghupload <path>` *command se seedha upload kar sakte hain!*"
        )

    # =========================
    # /GHUPLOAD COMMAND (STRICT TOKEN CHECK)
    # =========================
    @app.on_message(filters.command(["ghupload", "push", "upload"]) & filters.private)
    async def github_upload_handler(client, message: Message):
        user_id = message.from_user.id

        # 🛑 STRICT CHECK: Jab tak connect nahi hoga, aage nahi badhega
        token, repo_name = await get_github_client(user_id)

        if not token or not repo_name:
            return await message.reply(
                "⛔ **Access Denied: GitHub Not Connected!**\n\n"
                "Aapne abhi tak apna GitHub account connect nahi kiya hai!\n"
                "Bina connect kiye aap koi bhi file upload nahi kar sakte.\n\n"
                "Pehle apna token is command se set karein:\n"
                "`/ghset <TOKEN> <username/repo>`",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⚙️ How to Connect?", callback_data="gh_help_setup")]
                ])
            )

        if not message.reply_to_message or not message.reply_to_message.document:
            return await message.reply(
                "📂 **GitHub Uploader**\n\n"
                "Please **reply to any document/file** you want to push to GitHub with the command:\n"
                "`/ghupload <folder_name/file_name.py>`\n\n"
                "> *Path na dene par file seedha root folder mein save ho jayegi.*"
            )

        status_msg = await message.reply("🔄 **[1/3] Downloading file from Telegram...**")

        file_path = None
        try:
            doc = message.reply_to_message.document
            file_name = doc.file_name
            file_path = await message.reply_to_message.download()

            await status_msg.edit_text(f"⚡ **[2/3] Connecting to your GitHub repo (`{repo_name}`)...**")

            with open(file_path, "rb") as f:
                content = f.read()

            g = Github(token)
            repo = g.get_repo(repo_name)

            input_args = message.text.split(None, 1)
            target_path = input_args[1].strip() if len(input_args) > 1 else file_name

            await status_msg.edit_text(f"🚀 **[3/3] Pushing `{target_path}` to repository...**")

            commit_msg = f"✨ Add/Update {target_path} via AnuHelp Bot"

            action = "Created"
            try:
                existing_file = repo.get_contents(target_path)
                repo.update_file(existing_file.path, commit_msg, content, existing_file.sha)
                action = "Updated"
            except:
                repo.create_file(target_path, commit_msg, content)

            if file_path and os.path.exists(file_path):
                os.remove(file_path)

            file_size_kb = round(doc.file_size / 1024, 2)

            success_text = (
                f"✅ **GitHub Upload Successful!**\n\n"
                f"📂 **File:** `{file_name}`\n"
                f"📏 **Size:** `{file_size_kb} KB`\n"
                f"📍 **Path:** `{target_path}`\n"
                f"🛠 **Action:** `{action}`\n"
                f"🔗 **Repository:** `{repo_name}`\n\n"
                f"🌐 [View on GitHub](https://github.com/{repo_name}/blob/main/{target_path})"
            )

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🌐 Open File Link", url=f"https://github.com/{repo_name}/blob/main/{target_path}")]
            ])

            await status_msg.edit_text(success_text, reply_markup=keyboard, disable_web_page_preview=True)

        except Exception as e:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            await status_msg.edit_text(f"❌ **GitHub Deployment Failed:**\n\n`{str(e)}`")

    # Callback helper
    @app.on_callback_query(filters.regex("^gh_"))
    async def gh_callbacks(client, query: CallbackQuery):
        if query.data == "gh_help_setup":
            await query.message.edit_text(
                "📖 **How to link GitHub with AnuHelp Bot:**\n\n"
                "1. Go to your GitHub Settings -> Developer Settings -> Personal Access Tokens.\n"
                "2. Generate a token with full `repo` permissions.\n"
                "3. Send the command in this format to connect:\n"
                "`/ghset <YOUR_TOKEN> <username/repo_name>`"
            )
            await query.answer()
