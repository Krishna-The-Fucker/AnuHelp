# ============================================================
# 🤖 HANDLERS LOADER (ULTRA PRO MAX FINAL + NIGHT MODE ADDED)
# ============================================================

import logging
import importlib
import time

# ============================================================
# 🎨 LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("ULTRA-BOT")

# ============================================================
# 🛡 SAFE IMPORT FUNCTION
# ============================================================

def safe_import(module_name: str, func_name: str):
    try:
        module = importlib.import_module(module_name)
        func = getattr(module, func_name)
        return func
    except ModuleNotFoundError:
        logger.warning(f"⚠️ Module not found → {module_name}")
    except AttributeError:
        logger.warning(f"⚠️ Function not found → {module_name}.{func_name}")
    except Exception as e:
        logger.warning(f"⚠️ Import error → {module_name} → {e}")
    return None


# ============================================================
# 📦 MODULES LIST (UPDATED)
# ============================================================

MODULES = [

    # ================= BASIC =================
    ("Start System", "handlers.start", "register_handlers"),
    ("Group Commands", "handlers.group_commands", "register_group_commands"),
    ("Repo System", "handlers.repo", "register_repo_handler"),

    # ================= CORE =================
    ("Pins System", "handlers.pins", "register_pins"),
    ("Locks System", "handlers.locks", "register_locks"),
    ("Anti Bio Link", "handlers.antibiolink", "register_antibiolink"),

    # ================= 🌙 NIGHT MODE =================
    ("Night Mode", "handlers.night_mode", "register_night_mode"),

    # ================= 🌍 LANGUAGE =================
    ("Language System", "handlers.language_handler", "register_language"),

    # ================= SECURITY =================
    ("Captcha System", "handlers.captcha", "register_captcha"),
    ("Anti-Spam", "handlers.auto_spam_detection", "register_auto_spam"),
    ("Abuse Filter", "handlers.abuse", "register_abuse_system"),

    # ================= ANTIFLOOD =================
    ("AntiFlood Core", "handlers.antiflood", "register_antiflood"),
    ("AntiFlood Commands", "handlers.antiflood", "register_antiflood_commands"),

    # ================= NSFW =================
    ("NSFW Filter", "handlers.nsfw", "register_nsfw_filter"),
    ("NSFW Commands", "handlers.nsfw_commands", "register_nsfw_commands"),

    # ================= ADMIN =================
    ("Admin Panel", "handlers.adminpanel", "register_admin_panel"),
    ("Approval System", "handlers.approve", "register_approval_handlers"),

    # ================= 👑 SUDO =================
    ("Sudo System", "handlers.sudo", "register"),

    # ================= UTIL =================
    ("Support System", "handlers.help_support", "register_help_handler"),
    ("Anti-Edit", "handlers.antiedit", "register_antiedit"),
    ("Auto Clean", "handlers.intel", "register_autoclean"),
    ("AniQuote", "handlers.aniquote", "register_aniquote"),
]

# ============================================================
# 🚨 SPECIAL HANDLERS
# ============================================================

SPECIAL_HANDLERS = [
    ("AntiRaid Core", "handlers.antiraid", "antiraid"),
    ("Auto AntiRaid", "handlers.antiraid", "auto_antiraid"),
    ("AntiRaid Join", "handlers.antiraid", "anti_raid_join"),
]

# ============================================================
# 🧠 MAIN LOADER (UPDATED FOR NIGHT MODE)
# ============================================================

def register_all_handlers(app, db, LOG_CHANNEL):

    logger.info("🚀 Booting Ultra Bot System...\n")
    start_time = time.time()

    loaded = 0
    failed = 0
    loaded_modules = set()

    # ================= LOAD MODULES =================
    for name, module, func_name in MODULES:

        if module in loaded_modules:
            logger.warning(f"⚠️ Duplicate skipped → {module}")
            continue

        logger.info(f"🔄 Loading → {name}")

        func = safe_import(module, func_name)

        if not func:
            logger.warning(f"⚠️ Skipped → {name}")
            failed += 1
            continue

        try:
            t1 = time.time()

            # 🔥 SPECIAL CASE FOR NIGHT MODE
            if module == "handlers.night_mode":
                func(app, db, LOG_CHANNEL)
            else:
                func(app)

            t2 = time.time()

            logger.info(f"✅ Loaded → {name} ({round(t2 - t1, 3)}s)")
            loaded += 1
            loaded_modules.add(module)

        except Exception as e:
            logger.error(f"❌ Crash → {name} → {e}")
            failed += 1

    # ================= SPECIAL HANDLERS =================
    for name, module, handler_name in SPECIAL_HANDLERS:

        logger.info(f"🔥 Adding → {name}")

        handler = safe_import(module, handler_name)

        if not handler:
            logger.warning(f"⚠️ Missing → {name}")
            failed += 1
            continue

        try:
            app.add_handler(handler)
            logger.info(f"🔥 Added → {name}")
            loaded += 1

        except Exception as e:
            logger.error(f"❌ Error → {name} → {e}")
            failed += 1

    # ================= FINAL REPORT =================
    total_time = round(time.time() - start_time, 2)

    logger.info("\n" + "=" * 50)
    logger.info("🚀 BOT LOADING COMPLETE")
    logger.info(f"✅ Loaded Modules : {loaded}")
    logger.info(f"❌ Failed Modules : {failed}")
    logger.info(f"⏱ Total Time     : {total_time}s")
    logger.info("=" * 50 + "\n")
