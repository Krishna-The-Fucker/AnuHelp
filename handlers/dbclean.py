# ============================================================
# 🧹 DATABASE CLEANUP & MAINTENANCE SYSTEM (ULTIMATE PRO MAX)
# ============================================================

__mod_name__ = "🧹 ᴅʙ ᴄʟᴇᴀɴ"

__help__ = """
*🧹 ᴅʙ ᴄʟᴇᴀɴ sʏsᴛᴇᴍ* — Admin tool to purge orphaned or stale data from the database for optimal bot performance!

• `/dbclean` — Run a system-wide database maintenance and cleanup check (Bot Owner / Global Admin only).
"""

from pyrogram import filters
from pyrogram.types import Message
import logging

def register_db_clean_system(app, db, OWNER_ID: int):

    # ============================================================
    # 🧹 CLEANUP COMMAND (`/dbclean`)
    # ============================================================
    @app.on_message(filters.command("dbclean") & filters.private)
    async def db_clean_cmd(client, message: Message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("❌ **This command is strictly restricted to the Bot Owner!**")

        status_msg = await message.reply("🧹 **Starting database maintenance and cleanup scan...**")

        try:
            purged_stats = {
                "empty_filters": 0,
                "stale_afk": 0,
                "empty_blacklists": 0
            }

            # 1. Clean up empty/broken custom filters collection entries
            filter_result = await db.custom_filters.delete_many({
                "$or": [
                    {"content": {"$exists": False}},
                    {"keyword": {"$exists": False}}
                ]
            })
            purged_stats["empty_filters"] = filter_result.deleted_count

            # 2. Clean up empty blacklist settings documents
            blacklist_result = await db.blacklist_settings.delete_many({
                "$or": [
                    {"words": {"$exists": False}},
                    {"words": []}
                ]
            })
            purged_stats["empty_blacklists"] = blacklist_result.deleted_count

            # 3. Optional: Clear stale AFK records older than 7 days if any left hanging
            import time
            seven_days_ago = time.time() - (7 * 24 * 60 * 60)
            afk_result = await db.afk_users.delete_many({
                "time": {"$lt": seven_days_ago}
            })
            purged_stats["stale_afk"] = afk_result.deleted_count

            total_purged = sum(purged_stats.values())

            report_text = (
                f"✅ **Database Maintenance Completed Successfully!** ✨\n\n"
                f"🗑️ **Purged Empty Filters:** `{purged_stats['empty_filters']}`\n"
                f"🗑️ **Purged Empty Blacklist Docs:** `{purged_stats['empty_blacklists']}`\n"
                f"🗑️ **Purged Stale AFK Records:** `{purged_stats['stale_afk']}`\n\n"
                f"📊 **Total Cleaned Documents:** `{total_purged}`"
            )

            await status_msg.edit_text(report_text)

        except Exception as e:
            logging.error(f"[Database Clean Error]: {e}")
            await status_msg.edit_text("❌ **An error occurred while running the database cleanup.**")
