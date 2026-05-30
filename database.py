import json
import os
from pathlib import Path

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

SHOP_FILE    = DATA_DIR / "shop.json"
PLAYERS_FILE = DATA_DIR / "players.json"

# ─── Default Data ────────────────────────────────────────────────────
DEFAULT_SHOP = {
    "items": {
        "health_potion": {
            "name": "🧪 Health Potion",
            "desc": "คืน HP 2d4+2 (เฉลี่ย 7 HP)",
            "price": 50,
            "category": "potion",
            "stock": -1  # -1 = ไม่จำกัด
        },
        "greater_health_potion": {
            "name": "🫙 Greater Health Potion",
            "desc": "คืน HP 4d4+4 (เฉลี่ย 14 HP)",
            "price": 150,
            "category": "potion",
            "stock": -1
        },
        "antitoxin": {
            "name": "💊 Antitoxin",
            "desc": "+Advantage ต้าน Poison saves 1 ชั่วโมง",
            "price": 50,
            "category": "potion",
            "stock": -1
        },
        "torch": {
            "name": "🔦 Torch",
            "desc": "ให้แสงสว่าง Bright 20ft / Dim 20ft นาน 1 ชั่วโมง",
            "price": 1,
            "category": "adventuring",
            "stock": -1
        },
        "rope_50ft": {
            "name": "🪢 Hemp Rope (50ft)",
            "desc": "เชือกกัญชา 50 ฟุต",
            "price": 1,
            "category": "adventuring",
            "stock": -1
        },
        "rations": {
            "name": "🍖 Rations (1 day)",
            "desc": "อาหารสำหรับ 1 วัน",
            "price": 5,
            "category": "adventuring",
            "stock": -1
        },
        "shortsword": {
            "name": "⚔️ Shortsword",
            "desc": "1d6 Piercing | Finesse, Light",
            "price": 10,
            "category": "weapon",
            "stock": 5
        },
        "longsword": {
            "name": "🗡️ Longsword",
            "desc": "1d8 Slashing (1d10 two-handed) | Versatile",
            "price": 15,
            "category": "weapon",
            "stock": 3
        },
        "handaxe": {
            "name": "🪓 Handaxe",
            "desc": "1d6 Slashing | Light, Thrown (20/60)",
            "price": 5,
            "category": "weapon",
            "stock": -1
        },
        "leather_armor": {
            "name": "🛡️ Leather Armor",
            "desc": "AC 11 + DEX mod | Light Armor",
            "price": 10,
            "category": "armor",
            "stock": 3
        },
        "chain_mail": {
            "name": "⛓️ Chain Mail",
            "desc": "AC 16 | Heavy Armor | STR 13 required",
            "price": 75,
            "category": "armor",
            "stock": 2
        },
        "shield": {
            "name": "🔰 Shield",
            "desc": "+2 AC",
            "price": 10,
            "category": "armor",
            "stock": 5
        },
        "spellbook": {
            "name": "📖 Spellbook (Blank)",
            "desc": "สมุดเวทย์เปล่า 100 หน้า",
            "price": 50,
            "category": "magic",
            "stock": 2
        },
        "scroll_identify": {
            "name": "📜 Scroll of Identify",
            "desc": "ระบุ properties ของ magic item",
            "price": 100,
            "category": "magic",
            "stock": 3
        },
    }
}

DEFAULT_PLAYER = {
    "gold": 100,
    "inventory": {}  # { item_id: quantity }
}

# ─── Shop Functions ───────────────────────────────────────────────────
def load_shop() -> dict:
    if not SHOP_FILE.exists():
        save_shop(DEFAULT_SHOP)
        return DEFAULT_SHOP.copy()
    with open(SHOP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_shop(data: dict):
    with open(SHOP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ─── Player Functions ─────────────────────────────────────────────────
def load_players() -> dict:
    if not PLAYERS_FILE.exists():
        save_players({})
        return {}
    with open(PLAYERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_players(data: dict):
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_player(user_id: int) -> dict:
    players = load_players()
    uid = str(user_id)
    if uid not in players:
        players[uid] = DEFAULT_PLAYER.copy()
        players[uid]["inventory"] = {}
        save_players(players)
    return players[uid]

def save_player(user_id: int, data: dict):
    players = load_players()
    players[str(user_id)] = data
    save_players(players)

def add_gold(user_id: int, amount: int) -> int:
    """เพิ่มทอง คืนค่าทองคงเหลือ"""
    player = get_player(user_id)
    player["gold"] = max(0, player["gold"] + amount)
    save_player(user_id, player)
    return player["gold"]

def set_gold(user_id: int, amount: int) -> int:
    player = get_player(user_id)
    player["gold"] = max(0, amount)
    save_player(user_id, player)
    return player["gold"]
