# ============================================================
# 🤖 DATABASE LAYER (ULTRA PRO MAX FINAL++)
# ============================================================

import motor.motor_asyncio
from config import MONGO_URI, DB_NAME
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DB")

# ============================================================
# 🔗 CONNECT
# ============================================================

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[AnuHelp]

logger.info("✅ MongoDB Connected")

# ============================================================
# ⚡ SIMPLE CACHE (SAFE)
# ============================================================

CACHE = {}

def cache_get(key):
    return CACHE.get(key)

def cache_set(key, value):
    CACHE[key] = value

def cache_del(key):
    CACHE.pop(key, None)

def cache_clear_chat(chat_id):
    """Clear all cache of a chat (IMPORTANT 🔥)"""
    keys = [k for k in CACHE if str(chat_id) in k]
    for k in keys:
        CACHE.pop(k, None)

# ============================================================
# ⚙️ DEFAULT SETTINGS
# ============================================================

DEFAULT = {
    "warn_limit": 3,
    "nsfw": False,
    "antiedit": False,
    "welcome": True,
    "locks": [],
    "pinned": None,
    "antibiolink": False,
    "captcha": True,
    "night_mode": False,
    "broadcast": True,
    "chatbot": False
}


# ==========================================================
# 👑 SUDO SYSTEM
# ==========================================================

async def add_sudo(user_id):
    await db.sudo.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def remove_sudo(user_id):
    await db.sudo.delete_one({"user_id": user_id})

async def get_sudo_users():
    return [u["user_id"] async for u in db.sudo.find()]

async def is_sudo_user(user_id):
    return bool(await db.sudo.find_one({"user_id": user_id}))

# ==========================================================
# 🌍 LANGUAGE SYSTEM
# ==========================================================

async def set_language(chat_id, lang):
    await db.language.update_one(
        {"chat_id": chat_id},
        {"$set": {"lang": lang, "updated": datetime.utcnow()}},
        upsert=True
    )
    cache_set(f"lang:{chat_id}", lang)


async def get_language(chat_id):
    if (cached := cache_get(f"lang:{chat_id}")) is not None:
        return cached

    data = await db.language.find_one({"chat_id": chat_id})
    lang = data.get("lang", "en") if data else "en"

    cache_set(f"lang:{chat_id}", lang)
    return lang

# ==========================================================
# 🌙 NIGHT MODE (ENHANCED 🔥)
# ==========================================================

async def set_night(chat_id, status, start="23:00", end="06:00"):
    await db.night.update_one(
        {"chat_id": chat_id},
        {"$set": {
            "status": status,
            "start": start,
            "end": end,
            "updated": datetime.utcnow()
        }},
        upsert=True
    )
    cache_set(f"night:{chat_id}", {"status": status, "start": start, "end": end})

async def get_night(chat_id):
    if (cached := cache_get(f"night:{chat_id}")) is not None:
        return cached

    data = await db.night.find_one({"chat_id": chat_id})
    if not data:
        default_data = {"status": False, "start": "23:00", "end": "06:00"}
        cache_set(f"night:{chat_id}", default_data)
        return default_data

    cache_set(f"night:{chat_id}", data)
    return data

async def set_night_mode(chat_id, status):
    current = await get_night(chat_id)
    await set_night(chat_id, status, current.get("start", "23:00"), current.get("end", "06:00"))

async def get_night_mode(chat_id):
    data = await get_night(chat_id)
    return data.get("status", False)

# ==========================================================
# 🔐 CAPTCHA SYSTEM
# ==========================================================

async def set_captcha(chat_id, status):
    await db.captcha_settings.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )
    cache_set(f"captcha:{chat_id}", status)


async def get_captcha(chat_id):
    if (cached := cache_get(f"captcha:{chat_id}")) is not None:
        return cached

    data = await db.captcha_settings.find_one({"chat_id": chat_id})
    status = data.get("enabled", DEFAULT["captcha"]) if data else DEFAULT["captcha"]

    cache_set(f"captcha:{chat_id}", status)
    return status

# ==========================================================
# 🚫 ANTIBIOLINK
# ==========================================================

async def set_antibiolink(chat_id, status):
    await db.antibiolink.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )
    cache_set(f"antibiolink:{chat_id}", status)


async def get_antibiolink(chat_id):
    if (cached := cache_get(f"antibiolink:{chat_id}")) is not None:
        return cached

    data = await db.antibiolink.find_one({"chat_id": chat_id})
    status = data.get("enabled", DEFAULT["antibiolink"]) if data else DEFAULT["antibiolink"]

    cache_set(f"antibiolink:{chat_id}", status)
    return status

# ==========================================================
# 🤖 CHATBOT SYSTEM TOGGLE
# ==========================================================

async def set_chatbot(chat_id, status):
    await db.ai_toggles.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status, "updated": datetime.utcnow()}},
        upsert=True
    )
    cache_set(f"chatbot:{chat_id}", status)

async def get_chatbot(chat_id):
    if (cached := cache_get(f"chatbot:{chat_id}")) is not None:
        return cached

    data = await db.ai_toggles.find_one({"chat_id": chat_id})
    status = data.get("enabled", DEFAULT["chatbot"]) if data else DEFAULT["chatbot"]

    cache_set(f"chatbot:{chat_id}", status)
    return status

# ==========================================================
# 📌 PINS
# ==========================================================

async def set_pinned(chat_id, message_id):
    await db.pins.update_one(
        {"chat_id": chat_id},
        {"$set": {"message_id": message_id}},
        upsert=True
    )
    cache_set(f"pin:{chat_id}", message_id)


async def get_pinned(chat_id):
    if (cached := cache_get(f"pin:{chat_id}")) is not None:
        return cached

    data = await db.pins.find_one({"chat_id": chat_id})
    msg_id = data.get("message_id") if data else None

    cache_set(f"pin:{chat_id}", msg_id)
    return msg_id

# ==========================================================
# 🔐 LOCKS
# ==========================================================

async def set_locks(chat_id, locks):
    await db.locks.update_one(
        {"chat_id": chat_id},
        {"$set": {"locks": locks}},
        upsert=True
    )
    cache_set(f"locks:{chat_id}", locks)


async def get_locks(chat_id):
    if (cached := cache_get(f"locks:{chat_id}")) is not None:
        return cached

    data = await db.locks.find_one({"chat_id": chat_id})
    locks = data.get("locks", []) if data else []

    cache_set(f"locks:{chat_id}", locks)
    return locks


async def is_locked(chat_id, lock_type):
    return lock_type in await get_locks(chat_id)

# ==========================================================
# ⚠️ WARN SYSTEM
# ==========================================================

async def add_warn(chat_id, user_id):
    data = await db.warns.find_one({"chat_id": chat_id, "user_id": user_id})
    count = data.get("count", 0) + 1 if data else 1

    await db.warns.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"count": count}},
        upsert=True
    )

    cache_set(f"warn:{chat_id}:{user_id}", count)
    return count


async def reset_warn(chat_id, user_id):
    await db.warns.delete_one({"chat_id": chat_id, "user_id": user_id})
    cache_del(f"warn:{chat_id}:{user_id}")

# ==========================================================
# 🔞 NSFW
# ==========================================================

async def set_nsfw(chat_id, status):
    await db.nsfw.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )
    cache_set(f"nsfw:{chat_id}", status)


async def get_nsfw(chat_id):
    cached = cache_get(f"nsfw:{chat_id}")
    if cached is not None:
        return cached

    data = await db.nsfw.find_one({"chat_id": chat_id})
    status = data.get("enabled", DEFAULT["nsfw"]) if data else DEFAULT["nsfw"]

    cache_set(f"nsfw:{chat_id}", status)
    return status

# ==========================================================
# 👤 USER SYSTEM (BROADCAST)
# ==========================================================

async def add_user(user_id, name):
    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"name": name, "updated": datetime.utcnow()}},
        upsert=True
    )


async def get_all_users():
    users = []
    async for user in db.users.find():
        users.append(user["user_id"])
    return users

# ==========================================================
# 📢 LOG CHANNEL
# ==========================================================

async def set_log_channel(chat_id, channel_id):
    await db.logs.update_one(
        {"chat_id": chat_id},
        {"$set": {"channel": channel_id}},
        upsert=True
    )


async def get_log_channel(chat_id):
    data = await db.logs.find_one({"chat_id": chat_id})
    return data.get("channel") if data else None

# ==========================================================
# ✏️ ANTI EDIT
# ==========================================================

async def set_antiedit(chat_id, status):
    await db.antiedit.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )


async def get_antiedit(chat_id):
    data = await db.antiedit.find_one({"chat_id": chat_id})
    return data.get("enabled", DEFAULT["antiedit"]) if data else DEFAULT["antiedit"]

# ==========================================================
# 👋 WELCOME SYSTEM (EXTENDED SUPPORT)
# ==========================================================

async def set_welcome(chat_id, status):
    await db.welcome_toggles.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )
    cache_set(f"welcome_toggle:{chat_id}", status)


async def get_welcome(chat_id):
    if (cached := cache_get(f"welcome_toggle:{chat_id}")) is not None:
        return cached

    data = await db.welcome_toggles.find_one({"chat_id": chat_id})
    status = data.get("enabled", DEFAULT["welcome"]) if data else DEFAULT["welcome"]
    
    cache_set(f"welcome_toggle:{chat_id}", status)
    return status

# ==========================================================
# 🛡 ANTIRAID
# ==========================================================

async def set_antiraid(chat_id, status):
    await db.antiraid.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status}},
        upsert=True
    )


async def get_antiraid(chat_id):
    data = await db.antiraid.find_one({"chat_id": chat_id})
    return data.get("enabled", False) if data else False

# ==========================================================
# 💳 ECONOMY & BANKING MODULE DB METHODS 🔥
# ==========================================================

async def get_bank_account(user_id):
    data = await db.economy.find_one({"user_id": user_id})
    if not data:
        return {"cash": 1000, "bank": 0, "gems": 50}
    return data

async def update_bank_balance(user_id, cash_change=0, bank_change=0, gems_change=0):
    user_data = await get_bank_account(user_id)
    new_cash = max(0, user_data.get("cash", 1000) + cash_change)
    new_bank = max(0, user_data.get("bank", 0) + bank_change)
    new_gems = max(0, user_data.get("gems", 50) + gems_change)

    await db.economy.update_one(
        {"user_id": user_id},
        {"$set": {"cash": new_cash, "bank": new_bank, "gems": new_gems, "updated": datetime.utcnow()}},
        upsert=True
    )
    return {"cash": new_cash, "bank": new_bank, "gems": new_gems}

# ==========================================================
# 🥷 UNDERWORLD, MAFIA & HACKER GAMES DB METHODS 🔥
# ==========================================================

async def get_underworld_profile(user_id):
    data = await db.underworld.find_one({"user_id": user_id})
    if not data:
        return {"respect": 10, "wanted_level": 0, "crew": None, "safehouse": "Alleyway"}
    return data

async def update_underworld_profile(user_id, respect=0, wanted_level=0, crew=None):
    profile = await get_underworld_profile(user_id)
    new_respect = max(0, profile.get("respect", 10) + respect)
    new_wanted = max(0, min(5, profile.get("wanted_level", 0) + wanted_level))
    
    await db.underworld.update_one(
        {"user_id": user_id},
        {"$set": {"respect": new_respect, "wanted_level": new_wanted, "crew": crew or profile.get("crew")}},
        upsert=True
    )

async def get_mafia_syndicate(syndicate_name):
    return await db.mafia_syndicates.find_one({"name": syndicate_name})

async def create_mafia_syndicate(name, boss_id):
    await db.mafia_syndicates.update_one(
        {"name": name},
        {"$set": {"boss_id": boss_id, "vault": 0, "members": [boss_id], "created_at": datetime.utcnow()}},
        upsert=True
    )

async def get_hacker_profile(user_id):
    data = await db.hacker.find_one({"user_id": user_id})
    if not data:
        return {"firewall": 1, "exploit_level": 1, "bitcoins": 0.0}
    return data

async def update_hacker_profile(user_id, firewall_change=0, exploit_change=0, btc_change=0.0):
    hp = await get_hacker_profile(user_id)
    new_fw = max(1, hp.get("firewall", 1) + firewall_change)
    new_exp = max(1, hp.get("exploit_level", 1) + exploit_change)
    new_btc = max(0.0, hp.get("bitcoins", 0.0) + btc_change)

    await db.hacker.update_one(
        {"user_id": user_id},
        {"$set": {"firewall": new_fw, "exploit_level": new_exp, "bitcoins": new_btc}},
        upsert=True
    )

# ==========================================================
# ⚙️ INDEXES
# ==========================================================

async def create_indexes():
    await db.users.create_index("user_id", unique=True)
    
    await db.warns.create_index([
        ("chat_id", 1),
        ("user_id", 1)
    ])

    await db.language.create_index("chat_id", unique=True)
    
    await db.settings.create_index("chat_id", unique=True)
    
    await db.ai_toggles.create_index("chat_id", unique=True)

    # Economy & Game indexes
    await db.economy.create_index("user_id", unique=True)
    await db.underworld.create_index("user_id", unique=True)
    await db.mafia_syndicates.create_index("name", unique=True)
    await db.hacker.create_index("user_id", unique=True)

    # Added indexes for newly integrated features
    await db.feds.create_index("fed_id", unique=True)
    await db.fed_chats.create_index("chat_id", unique=True)
    await db.blacklist_chats.create_index("chat_id", unique=True)
    await db.blacklist_users.create_index("user_id", unique=True)

    logger.info("✅ Database Indexes Created (Including Federation, Blacklist, Economy & Game Collections)")
