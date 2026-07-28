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
db = client[DB_NAME]

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
    "night_mode": False
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
# 🌙 NIGHT MODE (NEW 🔥)
# ==========================================================

async def set_night_mode(chat_id, status):
    await db.night_mode.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": status, "updated": datetime.utcnow()}},
        upsert=True
    )
    cache_set(f"night:{chat_id}", status)


async def get_night_mode(chat_id):
    if (cached := cache_get(f"night:{chat_id}")) is not None:
        return cached

    data = await db.night_mode.find_one({"chat_id": chat_id})
    status = data.get("enabled", DEFAULT["night_mode"]) if data else DEFAULT["night_mode"]

    cache_set(f"night:{chat_id}", status)
    return status

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
# 🔐 LOCKS (FIX ADDED 🔥)
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
        {
            "$set": {
                "enabled": status
            }
        },
        upsert=True
    )

    cache_set(f"nsfw:{chat_id}", status)



async def get_nsfw(chat_id):

    cached = cache_get(f"nsfw:{chat_id}")

    if cached is not None:
        return cached


    data = await db.nsfw.find_one(
        {"chat_id": chat_id}
    )


    status = data.get(
        "enabled",
        DEFAULT["nsfw"]
    ) if data else DEFAULT["nsfw"]


    cache_set(
        f"nsfw:{chat_id}",
        status
    )

    return status



# ==========================================================
# 👤 USER SYSTEM (BROADCAST)
# ==========================================================

async def add_user(user_id, name):

    await db.users.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "name": name,
                "updated": datetime.utcnow()
            }
        },
        upsert=True
    )



async def get_all_users():

    users = []

    async for user in db.users.find():

        users.append(
            user["user_id"]
        )

    return users



# ==========================================================
# 📢 LOG CHANNEL
# ==========================================================

async def set_log_channel(chat_id, channel_id):

    await db.logs.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "channel": channel_id
            }
        },
        upsert=True
    )



async def get_log_channel(chat_id):

    data = await db.logs.find_one(
        {"chat_id": chat_id}
    )

    return data.get(
        "channel"
    ) if data else None



# ==========================================================
# ✏️ ANTI EDIT
# ==========================================================

async def set_antiedit(chat_id, status):

    await db.antiedit.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "enabled": status
            }
        },
        upsert=True
    )



async def get_antiedit(chat_id):

    data = await db.antiedit.find_one(
        {"chat_id": chat_id}
    )

    return data.get(
        "enabled",
        DEFAULT["antiedit"]
    ) if data else DEFAULT["antiedit"]



# ==========================================================
# 👋 WELCOME SYSTEM
# ==========================================================

async def set_welcome(chat_id, status):

    await db.welcome.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "enabled": status
            }
        },
        upsert=True
    )



async def get_welcome(chat_id):

    data = await db.welcome.find_one(
        {"chat_id": chat_id}
    )

    return data.get(
        "enabled",
        DEFAULT["welcome"]
    ) if data else DEFAULT["welcome"]



# ==========================================================
# 🛡 ANTIRAID
# ==========================================================

async def set_antiraid(chat_id, status):

    await db.antiraid.update_one(
        {"chat_id": chat_id},
        {
            "$set": {
                "enabled": status
            }
        },
        upsert=True
    )



async def get_antiraid(chat_id):

    data = await db.antiraid.find_one(
        {"chat_id": chat_id}
    )

    return data.get(
        "enabled",
        False
    ) if data else False



# ==========================================================
# ⚙️ INDEXES
# ==========================================================

async def create_indexes():

    await db.users.create_index(
        "user_id",
        unique=True
    )

    await db.warns.create_index(
        [
            ("chat_id", 1),
            ("user_id", 1)
        ]
    )

    await db.language.create_index(
        "chat_id",
        unique=True
    )

    await db.night_mode.create_index(
        "chat_id",
        unique=True
    )

    await db.settings.create_index(
        "chat_id",
        unique=True
    )

    logger.info(
        "✅ Database Indexes Created"
    )
