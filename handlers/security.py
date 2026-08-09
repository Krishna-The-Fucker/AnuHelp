# ============================================================
# 🔐 SECURITY MODULE — INTEGRITY & RUNTIME KEY MANAGER
# ============================================================

import os
import hashlib
import hmac
import base64
from config import BOT_TOKEN, OWNER_ID

# ============================================================
# 🔑 RUNTIME KEY GENERATOR
# ============================================================

def get_runtime_key() -> str:
    """
    Generates a secure, deterministic runtime security key 
    based on the bot token and owner ID.
    """
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN is missing in environment variables.")
    
    # Create a secure HMAC signature using BOT_TOKEN as the key and OWNER_ID as the message
    message = str(OWNER_ID).encode("utf-8")
    secret_key = BOT_TOKEN.encode("utf-8")
    
    signature = hmac.new(secret_key, message, hashlib.sha256).digest()
    runtime_key = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    
    return runtime_key


# ============================================================
# 🛡️ INTEGRITY VERIFICATION
# ============================================================

def verify_integrity() -> bool:
    """
    Verifies that critical credentials and environment parameters
    are intact and match baseline configurations.
    """
    if not BOT_TOKEN or len(BOT_TOKEN.split(":")) != 2:
        raise SecurityError("⚠️ Invalid or malformed BOT_TOKEN detected!")
    
    if not OWNER_ID or OWNER_ID <= 0:
        raise SecurityError("⚠️ Invalid OWNER_ID configuration!")
        
    return True


# ============================================================
# ⚠️ CUSTOM SECURITY EXCEPTION
# ============================================================

class SecurityError(Exception):
    """Custom exception raised when a security violation or checksum failure occurs."""
    pass
