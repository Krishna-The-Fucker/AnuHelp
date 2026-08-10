# ============================================================
# 🤖 HANDLERS LOADER 
# ============================================================

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BOT")

# ============================================================
# 📦 SAFE IMPORT FUNCTION
# ============================================================

def safe_import(name, func_name):
    try:
        module = __import__(name, fromlist=[func_name])
        return getattr(module, func_name)
    except Exception as e:
        logger.warning(f"⚠️ Failed to load {name}: {e}")
        return None

# ============================================================
# 📂 LOAD ALL MODULES SAFELY
# ============================================================

# BASIC
register_handlers = safe_import("handlers.start", "register_handlers")
register_group_commands = safe_import("handlers.group_commands", "register_group_commands")
register_repo_handler = safe_import("handlers.repo", "register_repo_handler")

# HELP
register_help_handler = safe_import("handlers.help_support", "register_help_handler")

# SYSTEMS
register_auto_spam = safe_import("handlers.auto_spam_detection", "register_auto_spam")
register_admin_panel = safe_import("handlers.adminpanel", "register_admin_panel")
register_abuse_system = safe_import("handlers.abuse", "register_abuse_system")

# ANTIFLOOD
register_antiflood = safe_import("handlers.antiflood", "register_antiflood")
register_antiflood_commands = safe_import("handlers.antiflood", "register_antiflood_commands")

# NSFW
register_nsfw_filter = safe_import("handlers.nsfw", "register_nsfw_filter")
register_nsfw_commands = safe_import("handlers.nsfw_commands", "register_nsfw_commands")

# OTHER SYSTEMS
register_antiedit = safe_import("handlers.antiedit", "register_antiedit")
register_autoclean = safe_import("handlers.intel", "register_autoclean")
register_aniquote = safe_import("handlers.aniquote", "register_aniquote")

# ANTIRAID
antiraid = safe_import("handlers.antiraid", "antiraid")
auto_antiraid = safe_import("handlers.antiraid", "auto_antiraid")
anti_raid_join = safe_import("handlers.antiraid", "anti_raid_join")

# APPROVAL
register_approval_handlers = safe_import("handlers.approve", "register_approval_handlers")


# ============================================================
# 🧠 REGISTER FUNCTION WRAPPER
# ============================================================

def safe_register(func, app, name):
    if func:
        try:
            func(app)
            logger.info(f"✅ {name} Loaded")
        except Exception as e:
            logger.error(f"❌ {name} Error: {e}")
    else:
        logger.warning(f"⚠️ {name} Missing")

# ============================================================
# 🚀 REGISTER ALL HANDLERS
# ============================================================

def register_all_handlers(app):

    logger.info("🚀 Initializing Bot Modules...\n")

    # =========================
    # BASIC
    # =========================
    safe_register(register_handlers, app, "Start System")
    safe_register(register_repo_handler, app, "Repo System")

    # =========================
    # COMMANDS
    # =========================
    safe_register(register_group_commands, app, "Group Commands")

    # =========================
    # HELP
    # =========================
    safe_register(register_help_handler, app, "Support System")

    # =========================
    # ADMIN
    # =========================
    safe_register(register_admin_panel, app, "Admin Panel")

    # =========================
    # APPROVAL
    # =========================
    safe_register(register_approval_handlers, app, "Approval System")

    # =========================
    # SECURITY SYSTEMS
    # =========================
    safe_register(register_auto_spam, app, "Anti-Spam")
    safe_register(register_abuse_system, app, "Abuse Filter")

    # =========================
    # ANTIFLOOD
    # =========================
    safe_register(register_antiflood, app, "AntiFlood")
    safe_register(register_antiflood_commands, app, "AntiFlood Commands")

    # =========================
    # NSFW
    # =========================
    safe_register(register_nsfw_filter, app, "NSFW Filter")
    safe_register(register_nsfw_commands, app, "NSFW Commands")

    # =========================
    # OTHER
    # =========================
    safe_register(register_antiedit, app, "Anti-Edit")
    safe_register(register_autoclean, app, "Auto Clean")
    safe_register(register_aniquote, app, "AniQuote")

    # =========================
    # ANTIRAID (SPECIAL HANDLERS)
    # =========================
    if antiraid:
        app.add_handler(antiraid)
        logger.info("✅ AntiRaid Core Loaded")

    if auto_antiraid:
        app.add_handler(auto_antiraid)
        logger.info("✅ Auto AntiRaid Loaded")

    if anti_raid_join:
        app.add_handler(anti_raid_join)
        logger.info("✅ AntiRaid Join Protection Loaded")

    # ============================================================
    # 🎉 FINAL STATUS
    # ============================================================
    logger.info("""
╔══════════════════════════════╗
║   🤖 BOT SUCCESSFULLY LOADED ║
╠══════════════════════════════╣
║ ✅ All Core Systems Active        ║
╚══════════════════════════════╝
""")
