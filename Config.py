# ============================================================
# 🤖 Group Manager Bot - FINAL CONFIG (ULTRA PRO MAX++)
# ============================================================

import os
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# 🔑 BOT CREDENTIALS & APIs
# ============================================================

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- 🤖 ADDED FOR DEEP AI INTEGRATION ---
DEEP_AI_API_KEY = os.getenv("DEEP_AI_API_KEY", "")

# ============================================================
# 🗄️ DATABASE
# ============================================================

MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("DB_NAME", "AnuDB")

# ============================================================
# 👑 OWNER / BOT INFO
# ============================================================

OWNER_ID = int(os.getenv("OWNER_ID", "8315627692"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "Anu_helpbot")

# ============================================================
# 👑 DEV / SUDO SYSTEM
# ============================================================

DEV_LIST = list(map(int, os.getenv("DEV_LIST", str(OWNER_ID)).split()))
SUDO_USERS = list(map(int, os.getenv("SUDO_USERS", str(OWNER_ID)).split()))

AUTO_APPROVE_ADMINS = os.getenv("AUTO_APPROVE_ADMINS", "True") == "True"
IGNORE_DEVS = os.getenv("IGNORE_DEVS", "True") == "True"
IGNORE_SUDO = os.getenv("IGNORE_SUDO", "True") == "True"

# ============================================================
# 📢 CHANNEL / LOGS & STARTUP MEDIA
# ============================================================

SUPPORT_CHAT = int(os.getenv("SUPPORT_CHAT", "-1003936239127"))
LOG_CHANNEL = int(os.getenv("LOG_CHANNEL", "-1003936239127"))
START_VIDEO_URL = os.getenv("START_VIDEO_URL", "https://n.uguu.se/nQlDgtaT.mp4")

# ============================================================
# ⚠️ WARN SYSTEM
# ============================================================

MAX_WARNS = int(os.getenv("MAX_WARNS", "3"))
WARN_ACTION = os.getenv("WARN_ACTION", "mute")  # mute/kick/ban
WARN_RESET_TIME = int(os.getenv("WARN_RESET_TIME", "0"))  # optional

# ============================================================
# 🔞 NSFW SYSTEM
# ============================================================

NSFW_DEFAULT = os.getenv("NSFW_DEFAULT", "False") == "True"
NSFW_THRESHOLD = float(os.getenv("NSFW_THRESHOLD", "0.7"))

# ============================================================
# 🔐 CAPTCHA SYSTEM
# ============================================================

CAPTCHA_DEFAULT = os.getenv("CAPTCHA_DEFAULT", "True") == "True"
CAPTCHA_TIMEOUT = int(os.getenv("CAPTCHA_TIMEOUT", "120"))
CAPTCHA_MODE = os.getenv("CAPTCHA_MODE", "math")  # math/button

# ============================================================
# 🚫 ANTIBIOLINK SYSTEM (FULL ADVANCED 🔥)
# ============================================================

ANTIBIOLINK_DEFAULT = os.getenv("ANTIBIOLINK_DEFAULT", "False") == "True"
ANTIBIOLINK_WARN_LIMIT = int(os.getenv("ANTIBIOLINK_WARN_LIMIT", "3"))
ANTIBIOLINK_MUTE_TIME = int(os.getenv("ANTIBIOLINK_MUTE_TIME", "600"))
ANTIBIOLINK_PUNISHMENT = os.getenv("ANTIBIOLINK_PUNISHMENT", "mute")

ANTIBIOLINK_IGNORE_ADMINS = os.getenv("ANTIBIOLINK_IGNORE_ADMINS", "True") == "True"
ANTIBIOLINK_IGNORE_DEVS = os.getenv("ANTIBIOLINK_IGNORE_DEVS", "True") == "True"
ANTIBIOLINK_IGNORE_SUDO = os.getenv("ANTIBIOLINK_IGNORE_SUDO", "True") == "True"

ANTIBIOLINK_STRICT_MODE = os.getenv("ANTIBIOLINK_STRICT_MODE", "True") == "True"

WHITELIST_DOMAINS = os.getenv(
    "WHITELIST_DOMAINS",
    "t.me,telegram.me,youtube.com,youtu.be"
).split(",")

BIO_LINK_KEYWORDS = os.getenv(
    "BIO_LINK_KEYWORDS",
    "http,www,.com,.net,.org,t.me,telegram,wa.me,instagram"
).split(",")

DELETE_ON_DETECT = os.getenv("DELETE_ON_DETECT", "True") == "True"
WARN_ON_DETECT = os.getenv("WARN_ON_DETECT", "True") == "True"

# ============================================================
# 🚨 ANTIRAID SYSTEM
# ============================================================

ANTIRAID_DEFAULT = os.getenv("ANTIRAID_DEFAULT", "False") == "True"
ANTIRAID_DURATION = int(os.getenv("ANTIRAID_DURATION", "600"))

# ============================================================
# 🔐 LOCK SYSTEM
# ============================================================

LOCK_TYPES = [
    "all", "photo", "video", "gif", "sticker",
    "link", "forward", "bots", "audio",
    "voice", "document", "poll",
    "emoji", "url", "hashtag", "edit", "file",
]

# ============================================================
# 📌 PIN SYSTEM
# ============================================================

AUTO_PIN = os.getenv("AUTO_PIN", "False") == "True"

# ============================================================
# ⚡ CACHE SYSTEM (DB.py compatible 🔥)
# ============================================================

CACHE_ENABLED = os.getenv("CACHE_ENABLED", "True") == "True"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
CACHE_LIMIT = int(os.getenv("CACHE_LIMIT", "10000"))

# ============================================================
# 🔄 AUTO DELETE / CLEANUP
# ============================================================

AUTO_DELETE_TIME = int(os.getenv("AUTO_DELETE_TIME", "0"))

# ============================================================
# 🌍 LANGUAGE SYSTEM (DB CONNECTED 🔥)
# ============================================================

DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

AUTO_TRANSLATE = os.getenv("AUTO_TRANSLATE", "True") == "True"
TRANSLATE_MODE = os.getenv("TRANSLATE_MODE", "reply")  # reply/replace/off
TRANSLATE_TIMEOUT = int(os.getenv("TRANSLATE_TIMEOUT", "5"))
TRANSLATE_RETRIES = int(os.getenv("TRANSLATE_RETRIES", "2"))

IGNORE_COMMANDS_IN_TRANSLATE = os.getenv(
    "IGNORE_COMMANDS_IN_TRANSLATE", "True"
) == "True"

# ============================================================
# 👋 WELCOME SYSTEM CONFIGS
# ============================================================

WELCOME_DEFAULT_MODE = os.getenv("WELCOME_DEFAULT_MODE", "text") # text/media
WELCOME_CLEAN_SERVICE = os.getenv("WELCOME_CLEAN_SERVICE", "True") == "True"

# ============================================================
# 📝 ANI-QUOTE SYSTEM CONFIGS
# ============================================================

ANIQUOTE_DEFAULT_LIMIT = int(os.getenv("ANIQUOTE_DEFAULT_LIMIT", "5"))

# ============================================================
# 🚫 ANTI-EDIT SYSTEM CONFIGS
# ============================================================

ANTI_EDIT_DEFAULT = os.getenv("ANTI_EDIT_DEFAULT", "False") == "True"
ANTI_EDIT_ALERT_TIMEOUT = int(os.getenv("ANTI_EDIT_ALERT_TIMEOUT", "4"))

# ============================================================
# 🌐 FEDERATION SYSTEM CONFIGS
# ============================================================

FEDERATION_ENABLED = os.getenv("FEDERATION_ENABLED", "True") == "True"
MAX_FEDS_PER_USER = int(os.getenv("MAX_FEDS_PER_USER", "1"))

# ============================================================
# 🚫 BLACKLIST SYSTEM CONFIGS (CHATS & USERS)
# ============================================================

AUTO_LEAVE_BLACKLIST_CHATS = os.getenv("AUTO_LEAVE_BLACKLIST_CHATS", "True") == "True"
BLOCK_BLACKLIST_USERS = os.getenv("BLOCK_BLACKLIST_USERS", "True") == "True"

# ============================================================
# 🧶 STRING GENERATOR SYSTEM CONFIGS
# ============================================================

STRING_GEN_TIMEOUT = int(os.getenv("STRING_GEN_TIMEOUT", "300"))

# ============================================================
# 🎮 QUICK GAMES SYSTEM CONFIGS
# ============================================================

GAMES_ENABLED = os.getenv("GAMES_ENABLED", "True") == "True"

# ============================================================
# 💳 ECONOMY & BANKING MODULE CONFIGS
# ============================================================

ECONOMY_ENABLED = os.getenv("ECONOMY_ENABLED", "True") == "True"
STARTING_CASH = int(os.getenv("STARTING_CASH", "100000"))
DAILY_BONUS_AMOUNT = int(os.getenv("DAILY_BONUS_AMOUNT", "300000"))

# ============================================================
# 🥷 UNDERWORLD / MAFIA & HACKER GAME CONFIGS (ADDED 🔥)
# ============================================================

UNDERWORLD_ENABLED = os.getenv("UNDERWORLD_ENABLED", "True") == "True"
MAFIA_GAME_ENABLED = os.getenv("MAFIA_GAME_ENABLED", "True") == "True"
HACKER_GAME_ENABLED = os.getenv("HACKER_GAME_ENABLED", "True") == "True"

# Game specific configs
ROB_SUCCESS_CHANCE = float(os.getenv("ROB_SUCCESS_CHANCE", "0.5"))
MAX_ROB_PERCENT = float(os.getenv("MAX_ROB_PERCENT", "0.3"))
STARTING_GEMS = int(os.getenv("STARTING_GEMS", "100"))
HACK_SUCCESS_CHANCE = float(os.getenv("HACK_SUCCESS_CHANCE", "0.6"))

# ============================================================
# 🧠 SECURITY FLAGS
# ============================================================

STRICT_MODE = os.getenv("STRICT_MODE", "True") == "True"
IGNORE_PRIVATE = os.getenv("IGNORE_PRIVATE", "True") == "True"

# ============================================================
# 🧠 DEBUG / LOGGING
# ============================================================

DEBUG = os.getenv("DEBUG", "True") == "True"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ============================================================
# 🚀 STARTUP FLAGS
# ============================================================

AUTO_CREATE_INDEXES = True
AUTO_LOAD_MODULES = True

# ============================================================
# ❌ VALIDATION
# ============================================================

if not API_ID or not API_HASH or not BOT_TOKEN:
    raise ValueError("❌ API_ID, API_HASH, BOT_TOKEN required!")

if not MONGO_URI:
    raise ValueError("❌ MONGO_URI required!")

print("✅ CONFIG LOADED SUCCESSFULLY (COMPLETE WITH UNDERWORLD, MAFIA & HACKER GAMES) 🚀")
