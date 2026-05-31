import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import json, os, random
from pathlib import Path

# ─── Database ─────────────────────────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SHOP_FILE    = DATA_DIR / "shop.json"
PLAYERS_FILE = DATA_DIR / "players.json"
ROLLS_FILE   = DATA_DIR / "quest_rolls.json"   # { user_id: { rank: [items], timestamp } }

GUILD_ID   = 1460585900504387657
SHOP_NAME  = "The Iron Bastion"
SHOP_COLOR = 0xB7410E

# ─── Magic Item Tables (5.5e 2024 PHB) ───────────────────────────────
# format: { id: { name, type, rarity, attune, desc, price } }
MAGIC_ITEMS = {
    # ── Common ────────────────────────────────────────────────────────
    "potion_healing":       {"name":"Potion of Healing",          "type":"Potion",       "rarity":"Common",    "attune":False, "desc":"คืน HP 2d4+2",                                     "price":50},
    "candle_invocation":    {"name":"Candle of the Deep",         "type":"Wondrous",     "rarity":"Common",    "attune":False, "desc":"เทียนใต้น้ำ ติดไฟได้แม้ใต้น้ำ 1 ชม.",              "price":25},
    "hat_disguise":         {"name":"Hat of Disguise",            "type":"Wondrous",     "rarity":"Common",    "attune":True,  "desc":"ร่ายคาถา Disguise Self ได้ตามต้องการ",             "price":100},
    "sending_stones":       {"name":"Sending Stones",             "type":"Wondrous",     "rarity":"Common",    "attune":False, "desc":"ส่งข้อความหากันได้ไม่จำกัดระยะ วันละ 1 ครั้ง",     "price":150},
    "potion_climbing":      {"name":"Potion of Climbing",         "type":"Potion",       "rarity":"Common",    "attune":False, "desc":"ได้รับ Climbing Speed = Walking Speed 1 ชม.",       "price":75},
    "spell_scroll_c0":      {"name":"Spell Scroll (Cantrip)",     "type":"Scroll",       "rarity":"Common",    "attune":False, "desc":"ม้วนคาถา Cantrip",                                  "price":30},
    "spell_scroll_l1":      {"name":"Spell Scroll (1st Level)",   "type":"Scroll",       "rarity":"Common",    "attune":False, "desc":"ม้วนคาถาระดับ 1",                                   "price":75},
    "silvered_weapon":      {"name":"Silvered Weapon",            "type":"Weapon",       "rarity":"Common",    "attune":False, "desc":"อาวุธเคลือบเงิน เอาชนะ damage resistance ของ lycanthrope/devil","price":100},
    # ── Uncommon ──────────────────────────────────────────────────────
    "potion_greater_healing":{"name":"Potion of Greater Healing", "type":"Potion",       "rarity":"Uncommon",  "attune":False, "desc":"คืน HP 4d4+4",                                      "price":150},
    "bag_of_holding":        {"name":"Bag of Holding",            "type":"Wondrous",     "rarity":"Uncommon",  "attune":False, "desc":"กระเป๋าเก็บของ 500 lb / 64 cubic ft",              "price":400},
    "boots_elvenkind":       {"name":"Boots of Elvenkind",        "type":"Wondrous",     "rarity":"Uncommon",  "attune":False, "desc":"Advantage บน Stealth checks ที่เกี่ยวกับเสียงก้าว", "price":500},
    "cloak_elvenkind":       {"name":"Cloak of Elvenkind",        "type":"Wondrous",     "rarity":"Uncommon",  "attune":True,  "desc":"Advantage บน Stealth / Disadvantage ต่อ Perception ที่เจอคุณ","price":500},
    "adamantine_armor":      {"name":"Adamantine Armor",          "type":"Armor",        "rarity":"Uncommon",  "attune":False, "desc":"Critical Hit กลายเป็น Normal Hit",                  "price":500},
    "weapon_plus1":          {"name":"Weapon +1",                 "type":"Weapon",       "rarity":"Uncommon",  "attune":False, "desc":"+1 bonus ต่อ attack rolls และ damage rolls",         "price":500},
    "ammo_plus1":            {"name":"Ammunition +1 (×20)",       "type":"Ammunition",   "rarity":"Uncommon",  "attune":False, "desc":"+1 bonus ต่อ attack/damage 20 ชิ้น",                "price":250},
    "helm_comprehend_lang":  {"name":"Helm of Comprehending Languages","type":"Wondrous","rarity":"Uncommon",  "attune":False, "desc":"ร่าย Comprehend Languages ได้ตามต้องการ",           "price":500},
    "pearl_of_power":        {"name":"Pearl of Power",            "type":"Wondrous",     "rarity":"Uncommon",  "attune":True,  "desc":"คืน spell slot ระดับ 3 หรือต่ำกว่า 1 ครั้ง/วัน",   "price":600},
    "spell_scroll_l2":       {"name":"Spell Scroll (2nd Level)",  "type":"Scroll",       "rarity":"Uncommon",  "attune":False, "desc":"ม้วนคาถาระดับ 2",                                   "price":250},
    "spell_scroll_l3":       {"name":"Spell Scroll (3rd Level)",  "type":"Scroll",       "rarity":"Uncommon",  "attune":False, "desc":"ม้วนคาถาระดับ 3",                                   "price":500},
    "ring_protection":       {"name":"Ring of Protection",        "type":"Ring",         "rarity":"Uncommon",  "attune":True,  "desc":"+1 AC และ +1 ต่อ Saving Throws ทั้งหมด",           "price":3500},
    "bracers_archery":       {"name":"Bracers of Archery",        "type":"Wondrous",     "rarity":"Uncommon",  "attune":True,  "desc":"+2 damage ต่อ ranged weapon attacks",               "price":1500},
    "cloak_protection":      {"name":"Cloak of Protection",       "type":"Wondrous",     "rarity":"Uncommon",  "attune":True,  "desc":"+1 AC และ +1 ต่อ Saving Throws",                    "price":3500},
    # ── Rare ──────────────────────────────────────────────────────────
    "potion_superior_healing":{"name":"Potion of Superior Healing","type":"Potion",      "rarity":"Rare",      "attune":False, "desc":"คืน HP 8d4+8",                                      "price":1000},
    "armor_plus1":           {"name":"Armor +1",                  "type":"Armor",        "rarity":"Rare",      "attune":False, "desc":"+1 AC",                                              "price":2500},
    "weapon_plus2":          {"name":"Weapon +2",                 "type":"Weapon",       "rarity":"Rare",      "attune":False, "desc":"+2 bonus ต่อ attack rolls และ damage rolls",         "price":2000},
    "ring_spell_storing":    {"name":"Ring of Spell Storing",     "type":"Ring",         "rarity":"Rare",      "attune":True,  "desc":"เก็บ spell ได้สูงสุด 5 level ใช้ได้ทุกคน",         "price":3500},
    "necklace_adaptation":   {"name":"Necklace of Adaptation",    "type":"Wondrous",     "rarity":"Rare",      "attune":True,  "desc":"หายใจในสภาพแวดล้อมอันตรายได้ Adv. ต้าน inhaled poison","price":1500},
    "spell_scroll_l4":       {"name":"Spell Scroll (4th Level)",  "type":"Scroll",       "rarity":"Rare",      "attune":False, "desc":"ม้วนคาถาระดับ 4",                                   "price":2000},
    "spell_scroll_l5":       {"name":"Spell Scroll (5th Level)",  "type":"Scroll",       "rarity":"Rare",      "attune":False, "desc":"ม้วนคาถาระดับ 5",                                   "price":3000},
    "flame_tongue":          {"name":"Flame Tongue",              "type":"Magic Weapon", "rarity":"Rare",      "attune":True,  "desc":"ดาบไฟ เปิดใช้งาน: +2d6 fire damage",               "price":5000},
    "ring_free_action":      {"name":"Ring of Free Action",       "type":"Ring",         "rarity":"Rare",      "attune":True,  "desc":"Immune ต่อ paralyzed, restrained จาก non-magic",    "price":5000},
    "wand_fireballs":        {"name":"Wand of Fireballs",         "type":"Wand",         "rarity":"Rare",      "attune":True,  "desc":"7 charges | Fireball (DC 15) ใช้ 3 charges",        "price":4000},
    "staff_healing":         {"name":"Staff of Healing",          "type":"Staff",        "rarity":"Rare",      "attune":True,  "desc":"10 charges | Cure Wounds, Lesser Restoration, Mass Cure Wounds","price":4500},
    "amulet_health":         {"name":"Amulet of Health",          "type":"Wondrous",     "rarity":"Rare",      "attune":True,  "desc":"CON score = 19 ตราบใดที่สวมอยู่",                   "price":8000},
    # ── Very Rare ─────────────────────────────────────────────────────
    "potion_supreme_healing": {"name":"Potion of Supreme Healing","type":"Potion",       "rarity":"Very Rare", "attune":False, "desc":"คืน HP 10d4+20",                                    "price":5000},
    "armor_plus2":            {"name":"Armor +2",                 "type":"Armor",        "rarity":"Very Rare", "attune":False, "desc":"+2 AC",                                              "price":10000},
    "weapon_plus3":           {"name":"Weapon +3",                "type":"Weapon",       "rarity":"Very Rare", "attune":False, "desc":"+3 bonus ต่อ attack rolls และ damage rolls",         "price":8000},
    "dancing_sword":          {"name":"Dancing Sword",            "type":"Magic Weapon", "rarity":"Very Rare", "attune":True,  "desc":"โยนดาบขึ้นบินสู้แทน 4 rounds",                     "price":9000},
    "sword_life_stealing":    {"name":"Sword of Life Stealing",   "type":"Magic Weapon", "rarity":"Very Rare", "attune":True,  "desc":"crit: ดูด 10 HP จากเป้าหมาย",                       "price":8000},
    "spell_scroll_l6":        {"name":"Spell Scroll (6th Level)", "type":"Scroll",       "rarity":"Very Rare", "attune":False, "desc":"ม้วนคาถาระดับ 6",                                   "price":6000},
    "spell_scroll_l7":        {"name":"Spell Scroll (7th Level)", "type":"Scroll",       "rarity":"Very Rare", "attune":False, "desc":"ม้วนคาถาระดับ 7",                                   "price":10000},
    "ring_regeneration":      {"name":"Ring of Regeneration",     "type":"Ring",         "rarity":"Very Rare", "attune":True,  "desc":"คืน HP 1d6/10 min + ฟื้น limb ที่ขาดได้",          "price":15000},
    "manual_golems":          {"name":"Manual of Golems",         "type":"Wondrous",     "rarity":"Very Rare", "attune":False, "desc":"คู่มือสร้าง Golem (Clay/Iron/Stone/Flesh)",          "price":12000},
    # ── Legendary ─────────────────────────────────────────────────────
    "vorpal_sword":           {"name":"Vorpal Sword",             "type":"Magic Weapon", "rarity":"Legendary", "attune":True,  "desc":"crit: ตัดหัวทันที + +3 attack/damage",              "price":50000},
    "armor_invulnerability":  {"name":"Armor of Invulnerability", "type":"Armor",        "rarity":"Legendary", "attune":True,  "desc":"Resistance ต่อ nonmagical damage, 10 min/day: Immune","price":40000},
    "armor_plus3":            {"name":"Armor +3",                 "type":"Armor",        "rarity":"Legendary", "attune":False, "desc":"+3 AC",                                              "price":30000},
    "belt_giant_strength":    {"name":"Belt of Giant Strength",   "type":"Wondrous",     "rarity":"Legendary", "attune":True,  "desc":"STR = 29 (Storm Giant)",                             "price":45000},
    "cloak_invisibility":     {"name":"Cloak of Invisibility",    "type":"Wondrous",     "rarity":"Legendary", "attune":True,  "desc":"Invisible ตราบใดที่สวม สูงสุด 2 ชม./วัน",           "price":80000},
    "holy_avenger":           {"name":"Holy Avenger",             "type":"Magic Weapon", "rarity":"Legendary", "attune":True,  "desc":"Paladin only | +3 atk/dmg | 10d10 radiant ต่อ undead/fiend","price":70000},
    "ring_djinni":            {"name":"Ring of Djinni Summoning", "type":"Ring",         "rarity":"Legendary", "attune":True,  "desc":"เรียก Djinni 1 ชม./วัน ใช้คำสั่งได้",              "price":75000},
    "staff_magi":             {"name":"Staff of the Magi",        "type":"Staff",        "rarity":"Legendary", "attune":True,  "desc":"50 charges | ดูดซับ spell | ระเบิดได้",             "price":100000},
}

# ── Quest Rank → Rarity Weight Table ──────────────────────────────────
# rank: { rarity: weight }
RANK_TABLES = {
    "S": {"Common":0, "Uncommon":5,  "Rare":20,  "Very Rare":45, "Legendary":30},
    "A": {"Common":0, "Uncommon":10, "Rare":35,  "Very Rare":45, "Legendary":10},
    "B": {"Common":5, "Uncommon":20, "Rare":50,  "Very Rare":25, "Legendary":0},
    "C": {"Common":10,"Uncommon":45, "Rare":40,  "Very Rare":5,  "Legendary":0},
    "D": {"Common":30,"Uncommon":55, "Rare":15,  "Very Rare":0,  "Legendary":0},
    "E": {"Common":65,"Uncommon":30, "Rare":5,   "Very Rare":0,  "Legendary":0},
    "F": {"Common":90,"Uncommon":10, "Rare":0,   "Very Rare":0,  "Legendary":0},
}

RANK_COLORS = {"S":0xFFD700,"A":0xFF6B35,"B":0xE74C3C,"C":0x9B59B6,"D":0x3498DB,"E":0x2ECC71,"F":0x95A5A6}
RARITY_COLORS = {"Common":0x95A5A6,"Uncommon":0x2ECC71,"Rare":0x3498DB,"Very Rare":0x9B59B6,"Legendary":0xFFD700}
RARITY_EMOJI  = {"Common":"⚪","Uncommon":"🟢","Rare":"🔵","Very Rare":"🟣","Legendary":"🟡"}

# ─── Weapon list (ย่อ) ────────────────────────────────────────────────
DEFAULT_SHOP = {"items": {
    "club":          {"name":"Club",          "desc":"1d4 Bludgeoning | Light | Mastery: Slow",                       "price":0.1,  "category":"simple_melee",   "stock":-1},
    "dagger":        {"name":"Dagger",        "desc":"1d4 Piercing | Finesse, Light, Thrown 20/60 | Mastery: Nick",  "price":2,    "category":"simple_melee",   "stock":-1},
    "greatclub":     {"name":"Greatclub",     "desc":"1d8 Bludgeoning | Two-Handed | Mastery: Push",                 "price":0.2,  "category":"simple_melee",   "stock":-1},
    "handaxe":       {"name":"Handaxe",       "desc":"1d6 Slashing | Light, Thrown 20/60 | Mastery: Vex",            "price":5,    "category":"simple_melee",   "stock":-1},
    "javelin":       {"name":"Javelin",       "desc":"1d6 Piercing | Thrown 30/120 | Mastery: Slow",                 "price":0.5,  "category":"simple_melee",   "stock":-1},
    "light_hammer":  {"name":"Light Hammer",  "desc":"1d4 Bludgeoning | Light, Thrown 20/60 | Mastery: Nick",        "price":2,    "category":"simple_melee",   "stock":-1},
    "mace":          {"name":"Mace",          "desc":"1d6 Bludgeoning | Mastery: Sap",                               "price":5,    "category":"simple_melee",   "stock":-1},
    "quarterstaff":  {"name":"Quarterstaff",  "desc":"1d6 Bludgeoning | Versatile (1d8) | Mastery: Topple",          "price":0.2,  "category":"simple_melee",   "stock":-1},
    "sickle":        {"name":"Sickle",        "desc":"1d4 Slashing | Light | Mastery: Nick",                         "price":1,    "category":"simple_melee",   "stock":-1},
    "spear":         {"name":"Spear",         "desc":"1d6 Piercing | Thrown 20/60, Versatile (1d8) | Mastery: Sap",  "price":1,    "category":"simple_melee",   "stock":-1},
    "dart":          {"name":"Dart",          "desc":"1d4 Piercing | Finesse, Thrown 20/60 | Mastery: Vex",          "price":0.05, "category":"simple_ranged",  "stock":-1},
    "light_crossbow":{"name":"Light Crossbow","desc":"1d8 Piercing | Ammo (Bolt) 80/320, Loading | Mastery: Slow",   "price":25,   "category":"simple_ranged",  "stock":-1},
    "shortbow":      {"name":"Shortbow",      "desc":"1d6 Piercing | Ammo (Arrow) 80/320 | Mastery: Vex",            "price":25,   "category":"simple_ranged",  "stock":-1},
    "sling":         {"name":"Sling",         "desc":"1d4 Bludgeoning | Ammo (Bullet) 30/120 | Mastery: Slow",       "price":0.1,  "category":"simple_ranged",  "stock":-1},
    "battleaxe":     {"name":"Battleaxe",     "desc":"1d8 Slashing | Versatile (1d10) | Mastery: Topple",            "price":10,   "category":"martial_melee",  "stock":-1},
    "flail":         {"name":"Flail",         "desc":"1d8 Bludgeoning | Mastery: Sap",                               "price":10,   "category":"martial_melee",  "stock":-1},
    "glaive":        {"name":"Glaive",        "desc":"1d10 Slashing | Heavy, Reach, Two-Handed | Mastery: Graze",    "price":20,   "category":"martial_melee",  "stock":-1},
    "greataxe":      {"name":"Greataxe",      "desc":"1d12 Slashing | Heavy, Two-Handed | Mastery: Cleave",          "price":30,   "category":"martial_melee",  "stock":-1},
    "greatsword":    {"name":"Greatsword",    "desc":"2d6 Slashing | Heavy, Two-Handed | Mastery: Graze",            "price":50,   "category":"martial_melee",  "stock":-1},
    "halberd":       {"name":"Halberd",       "desc":"1d10 Slashing | Heavy, Reach, Two-Handed | Mastery: Cleave",   "price":20,   "category":"martial_melee",  "stock":-1},
    "lance":         {"name":"Lance",         "desc":"1d10 Piercing | Heavy, Reach | Mastery: Topple",               "price":10,   "category":"martial_melee",  "stock":-1},
    "longsword":     {"name":"Longsword",     "desc":"1d8 Slashing | Versatile (1d10) | Mastery: Sap",               "price":15,   "category":"martial_melee",  "stock":-1},
    "maul":          {"name":"Maul",          "desc":"2d6 Bludgeoning | Heavy, Two-Handed | Mastery: Topple",        "price":10,   "category":"martial_melee",  "stock":-1},
    "morningstar":   {"name":"Morningstar",   "desc":"1d8 Piercing | Mastery: Sap",                                  "price":15,   "category":"martial_melee",  "stock":-1},
    "pike":          {"name":"Pike",          "desc":"1d10 Piercing | Heavy, Reach, Two-Handed | Mastery: Push",     "price":5,    "category":"martial_melee",  "stock":-1},
    "rapier":        {"name":"Rapier",        "desc":"1d8 Piercing | Finesse | Mastery: Vex",                        "price":25,   "category":"martial_melee",  "stock":-1},
    "scimitar":      {"name":"Scimitar",      "desc":"1d6 Slashing | Finesse, Light | Mastery: Nick",                "price":25,   "category":"martial_melee",  "stock":-1},
    "shortsword":    {"name":"Shortsword",    "desc":"1d6 Piercing | Finesse, Light | Mastery: Vex",                 "price":10,   "category":"martial_melee",  "stock":-1},
    "trident":       {"name":"Trident",       "desc":"1d8 Piercing | Thrown 20/60, Versatile (1d10) | Mastery: Topple","price":5, "category":"martial_melee",  "stock":-1},
    "warhammer":     {"name":"Warhammer",     "desc":"1d8 Bludgeoning | Versatile (1d10) | Mastery: Push",           "price":15,   "category":"martial_melee",  "stock":-1},
    "war_pick":      {"name":"War Pick",      "desc":"1d8 Piercing | Versatile (1d10) | Mastery: Sap",               "price":5,    "category":"martial_melee",  "stock":-1},
    "whip":          {"name":"Whip",          "desc":"1d4 Slashing | Finesse, Reach | Mastery: Slow",                "price":2,    "category":"martial_melee",  "stock":-1},
    "blowgun":       {"name":"Blowgun",       "desc":"1 Piercing | Ammo (Needle) 25/100, Loading | Mastery: Vex",    "price":10,   "category":"martial_ranged", "stock":-1},
    "hand_crossbow": {"name":"Hand Crossbow", "desc":"1d6 Piercing | Ammo (Bolt) 30/120, Light, Loading | Mastery: Vex","price":75,"category":"martial_ranged", "stock":-1},
    "heavy_crossbow":{"name":"Heavy Crossbow","desc":"1d10 Piercing | Ammo (Bolt) 100/400, Heavy, Two-Handed | Mastery: Push","price":50,"category":"martial_ranged","stock":-1},
    "longbow":       {"name":"Longbow",       "desc":"1d8 Piercing | Ammo (Arrow) 150/600, Heavy, Two-Handed | Mastery: Slow","price":50,"category":"martial_ranged","stock":-1},
}}

SHOP_CATEGORIES = {
    "simple_melee":   ("⚔️",  "Simple Melee Weapons",   0xE67E22),
    "simple_ranged":  ("🏹",  "Simple Ranged Weapons",  0xE67E22),
    "martial_melee":  ("🗡️",  "Martial Melee Weapons",  0xE74C3C),
    "martial_ranged": ("🎯",  "Martial Ranged Weapons", 0xE74C3C),
}

# ─── DB Helpers ───────────────────────────────────────────────────────
def load_shop():
    if not SHOP_FILE.exists():
        with open(SHOP_FILE,"w",encoding="utf-8") as f: json.dump(DEFAULT_SHOP,f,ensure_ascii=False,indent=2)
        return DEFAULT_SHOP.copy()
    with open(SHOP_FILE,encoding="utf-8") as f: return json.load(f)
def save_shop(d):
    with open(SHOP_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)
def load_players():
    if not PLAYERS_FILE.exists():
        with open(PLAYERS_FILE,"w",encoding="utf-8") as f: json.dump({},f)
        return {}
    with open(PLAYERS_FILE,encoding="utf-8") as f: return json.load(f)
def save_players(d):
    with open(PLAYERS_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)
def get_player(uid):
    players=load_players(); key=str(uid)
    if key not in players:
        players[key]={"gold":100,"inventory":{}}; save_players(players)
    return players[key]
def save_player(uid,data):
    players=load_players(); players[str(uid)]=data; save_players(players)
def load_rolls():
    if not ROLLS_FILE.exists():
        with open(ROLLS_FILE,"w",encoding="utf-8") as f: json.dump({},f)
        return {}
    with open(ROLLS_FILE,encoding="utf-8") as f: return json.load(f)
def save_rolls(d):
    with open(ROLLS_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

def fmt_price(p):
    if p < 0.01: return f"{round(p*100)} CP"
    if p < 1:    return f"{round(p*10)} SP"
    return f"{int(p):,} GP"

# ─── Random Roll Helpers ──────────────────────────────────────────────
def weighted_rarity(rank: str) -> str:
    weights = RANK_TABLES[rank]
    pool = [r for r, w in weights.items() for _ in range(w)]
    return random.choice(pool)

def roll_magic_items(rank: str, count: int = 5) -> list:
    results = []
    for _ in range(count):
        rarity = weighted_rarity(rank)
        pool = [iid for iid, item in MAGIC_ITEMS.items() if item["rarity"] == rarity]
        if not pool:
            rarity = "Common"
            pool = [iid for iid, item in MAGIC_ITEMS.items() if item["rarity"] == rarity]
        iid = random.choice(pool)
        results.append(iid)
    return results

# ─── Bot ──────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator or \
               any(r.name in ("DM","Admin","Game Master") for r in interaction.user.roles)
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    try:
        # ล้าง Global commands เก่าออกก่อน (แก้ปัญหา duplicate slash commands)
        bot.tree.clear_commands(guild=None)
        await bot.tree.sync()
        # sync Guild-specific commands
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🌿 Synced {len(synced)} guild command(s) | Global commands cleared")
    except Exception as e: print(f"❌ {e}")
    print(f"⚔️  {bot.user} พร้อมใช้งานแล้ว!")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name="🎲 Quest Rewards | /shop"))

# ─── Shop UI ──────────────────────────────────────────────────────────
def make_shop_embed():
    embed = discord.Embed(
        title=f"⚒️  {SHOP_NAME}",
        description="ยินดีต้อนรับสู่ร้านของช่างตีเหล็กผู้เชี่ยวชาญ "
                    "ที่นี่มีอาวุธคุณภาพสูงพร้อมจำหน่ายทุกชนิด",
        color=SHOP_COLOR
    )
    embed.set_footer(text="เลือกหมวดจาก dropdown • /buy <id> เพื่อซื้อ • /roll_reward สำหรับ Magic Items")
    return embed

def make_category_embed(cat_key):
    items = load_shop()["items"]
    cat_items = {k:v for k,v in items.items() if v["category"]==cat_key}
    emoji, label, color = SHOP_CATEGORIES[cat_key]
    embed = discord.Embed(title=f"{emoji}  {label}", color=color)
    lines = [f"**{v['name']}** `{k}` — **{fmt_price(v['price'])}**\n> {v['desc']}" for k,v in cat_items.items()]
    embed.description = "\n\n".join(lines) if lines else "*ไม่มีสินค้า*"
    embed.set_footer(text="ซื้อ: /buy <id> <จำนวน>")
    return embed

class CategorySelect(discord.ui.Select):
    def __init__(self):
        super().__init__(placeholder="เลือกหมวดหมู่สินค้า...", options=[
            discord.SelectOption(label="Simple Melee Weapons",   value="simple_melee",   emoji="⚔️",  description="Club, Dagger, Handaxe, Spear..."),
            discord.SelectOption(label="Simple Ranged Weapons",  value="simple_ranged",  emoji="🏹",  description="Shortbow, Crossbow, Sling, Dart..."),
            discord.SelectOption(label="Martial Melee Weapons",  value="martial_melee",  emoji="🗡️",  description="Longsword, Greatsword, Rapier..."),
            discord.SelectOption(label="Martial Ranged Weapons", value="martial_ranged", emoji="🎯",  description="Longbow, Hand Crossbow, Blowgun..."),
        ])
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=make_category_embed(self.values[0]), ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategorySelect())
    @discord.ui.button(label="Check Coinpurse", style=discord.ButtonStyle.success, emoji="🪙", custom_id="shop:coinpurse")
    async def coinpurse(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = get_player(interaction.user.id)
        embed = discord.Embed(title=f"🪙 Coinpurse ของ {interaction.user.display_name}",
            description=f"**{fmt_price(player['gold'])}**", color=0xF1C40F)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    @discord.ui.button(label="List of Items", style=discord.ButtonStyle.primary, emoji="📋", custom_id="shop:inventory")
    async def inv_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = get_player(interaction.user.id); inv = player.get("inventory",{})
        shop_items = load_shop()["items"]
        embed = discord.Embed(title=f"🎒 Inventory ของ {interaction.user.display_name}", color=0x3498DB)
        embed.add_field(name="🪙 ทอง", value=f"**{fmt_price(player['gold'])}**", inline=False)
        if not inv:
            embed.add_field(name="📦 สิ่งของ", value="*กระเป๋าว่างเปล่า...*", inline=False)
        else:
            lines = []
            for iid,qty in inv.items():
                it = shop_items.get(iid) or MAGIC_ITEMS.get(iid)
                name = it["name"] if it else iid
                lines.append(f"**{name}** × {qty}")
            embed.add_field(name=f"📦 สิ่งของ ({len(inv)} ชนิด)", value="\n".join(lines), inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ─── Quest Roll UI ────────────────────────────────────────────────────
def make_roll_embed(rank: str, item_ids: list, quest_name: str = None):
    color = RANK_COLORS[rank]
    title = f"🎲 Random 5 items from Quest Rank {rank}"
    embed = discord.Embed(title=title, color=color)
    if quest_name:
        embed.add_field(name="Quest", value=f'*"{quest_name}"*', inline=False)
    for i, iid in enumerate(item_ids, 1):
        item = MAGIC_ITEMS.get(iid)
        if not item: continue
        re = RARITY_EMOJI.get(item["rarity"],"❓")
        attune = " *(ต้อง Attune)*" if item.get("attune") else ""
        embed.add_field(
            name=f"Item {i} : {item['name']}",
            value=f"**Type :** {item['type']}\n**Rarity :** {re} {item['rarity']}{attune}\n**Price :** {fmt_price(item['price'])}\n> {item['desc']}",
            inline=False
        )
    embed.set_footer(text="เลือกไอเทมจาก dropdown ด้านล่างเพื่อซื้อ")
    return embed

class BuyRollSelect(discord.ui.Select):
    def __init__(self, item_ids: list):
        self.item_ids = item_ids
        options = []
        for iid in item_ids:
            item = MAGIC_ITEMS.get(iid)
            if item:
                re = RARITY_EMOJI.get(item["rarity"],"")
                options.append(discord.SelectOption(
                    label=item["name"],
                    value=iid,
                    emoji=re,
                    description=f"{item['rarity']} | {fmt_price(item['price'])}"
                ))
        super().__init__(placeholder="เลือกซื้อไอเทม...", options=options, min_values=1, max_values=len(options))
    async def callback(self, interaction: discord.Interaction):
        player = get_player(interaction.user.id)
        bought = []; failed = []
        for iid in self.values:
            item = MAGIC_ITEMS.get(iid)
            if not item: continue
            if player["gold"] >= item["price"]:
                player["gold"] -= item["price"]
                player["inventory"][iid] = player["inventory"].get(iid, 0) + 1
                bought.append(item["name"])
            else:
                failed.append(f"{item['name']} (ต้องการ {fmt_price(item['price'])})")
        save_player(interaction.user.id, player)
        embed = discord.Embed(title="🛍️ ผลการซื้อ", color=0x2ECC71 if bought else 0xE74C3C)
        if bought: embed.add_field(name="✅ ซื้อสำเร็จ", value="\n".join(f"• {n}" for n in bought), inline=False)
        if failed: embed.add_field(name="❌ ทองไม่พอ",   value="\n".join(f"• {n}" for n in failed), inline=False)
        embed.add_field(name="🪙 ทองคงเหลือ", value=fmt_price(player["gold"]), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RollView(discord.ui.View):
    def __init__(self, item_ids: list):
        super().__init__(timeout=300)
        self.add_item(BuyRollSelect(item_ids))

# ─── Commands ─────────────────────────────────────────────────────────
@bot.tree.command(name="shop", description="🏪 เปิดร้านค้า The Iron Bastion", guild=discord.Object(id=GUILD_ID))
async def shop(interaction: discord.Interaction):
    await interaction.response.send_message(embed=make_shop_embed(), view=ShopView())

@bot.tree.command(name="roll_reward", description="🎲 สุ่ม Magic Items จาก Quest Rank (DM ใช้)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(rank="Quest Rank", quest_name="ชื่อเควส (ไม่บังคับ)", count="จำนวนไอเทม (default 5)")
@app_commands.choices(rank=[
    app_commands.Choice(name="🟡 S — Legendary/Very Rare", value="S"),
    app_commands.Choice(name="🟠 A — Very Rare/Rare",      value="A"),
    app_commands.Choice(name="🔴 B — Rare",                value="B"),
    app_commands.Choice(name="🟣 C — Rare/Uncommon",       value="C"),
    app_commands.Choice(name="🔵 D — Uncommon",            value="D"),
    app_commands.Choice(name="🟢 E — Common/Uncommon",     value="E"),
    app_commands.Choice(name="⚪ F — Common",              value="F"),
])
@is_admin()
async def roll_reward(interaction: discord.Interaction, rank: str, quest_name: str = None, count: int = 5):
    count = max(1, min(count, 10))
    item_ids = roll_magic_items(rank, count)
    embed = make_roll_embed(rank, item_ids, quest_name)
    view = RollView(item_ids)
    await interaction.response.send_message(embed=embed, view=view)

@bot.tree.command(name="buy", description="🛒 ซื้อสินค้าจากร้าน", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า", quantity="จำนวน")
async def buy(interaction: discord.Interaction, item_id: str, quantity: int = 1):
    if quantity <= 0:
        await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True); return
    shop_data = load_shop()
    item = shop_data["items"].get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบสินค้า `{item_id}`\nใช้ `/shop` เพื่อดู ID", ephemeral=True); return
    if item["stock"] != -1 and item["stock"] < quantity:
        await interaction.response.send_message(f"❌ stock ไม่พอ! เหลือ **{item['stock']} ชิ้น**", ephemeral=True); return
    total = item["price"] * quantity
    player = get_player(interaction.user.id)
    if player["gold"] < total:
        await interaction.response.send_message(
            f"❌ ทองไม่พอ!\nต้องการ **{fmt_price(total)}** | มี **{fmt_price(player['gold'])}**", ephemeral=True); return
    player["gold"] -= total
    player["inventory"][item_id] = player["inventory"].get(item_id, 0) + quantity
    save_player(interaction.user.id, player)
    if item["stock"] != -1:
        shop_data["items"][item_id]["stock"] -= quantity; save_shop(shop_data)
    embed = discord.Embed(title="✅ ซื้อสำเร็จ!", color=0x2ECC71)
    embed.add_field(name="🛍️ สินค้า",  value=f"**{item['name']}** × {quantity}", inline=True)
    embed.add_field(name="💸 จ่ายไป",  value=f"**{fmt_price(total)}**",            inline=True)
    embed.add_field(name="🪙 คงเหลือ", value=f"**{fmt_price(player['gold'])}**",   inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="sell", description="💱 ขายสินค้า (ได้ 50%)", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า", quantity="จำนวน")
async def sell(interaction: discord.Interaction, item_id: str, quantity: int = 1):
    if quantity <= 0:
        await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True); return
    player = get_player(interaction.user.id)
    have = player["inventory"].get(item_id, 0)
    if have < quantity:
        await interaction.response.send_message(f"❌ มี `{item_id}` แค่ **{have} ชิ้น**", ephemeral=True); return
    item = load_shop()["items"].get(item_id) or MAGIC_ITEMS.get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบข้อมูลสินค้า `{item_id}`", ephemeral=True); return
    earned = item["price"] * quantity / 2
    player["inventory"][item_id] -= quantity
    if player["inventory"][item_id] <= 0: del player["inventory"][item_id]
    player["gold"] += earned; save_player(interaction.user.id, player)
    embed = discord.Embed(title="💱 ขายสำเร็จ!", color=0xE67E22)
    embed.add_field(name="🛍️ สินค้า",  value=f"**{item['name']}** × {quantity}", inline=True)
    embed.add_field(name="🪙 ได้รับ",   value=f"**{fmt_price(earned)}**",          inline=True)
    embed.add_field(name="💼 คงเหลือ",  value=f"**{fmt_price(player['gold'])}**",  inline=True)
    await interaction.response.send_message(embed=embed)

# ─── Admin Commands ───────────────────────────────────────────────────
@bot.tree.command(name="admin_gold", description="[DM] ปรับทองของผู้เล่น", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น", action="add/remove/set", amount="จำนวน GP")
@app_commands.choices(action=[
    app_commands.Choice(name="➕ เพิ่ม", value="add"),
    app_commands.Choice(name="➖ ลด",   value="remove"),
    app_commands.Choice(name="🔧 กำหนด", value="set"),
])
@is_admin()
async def admin_gold(interaction: discord.Interaction, member: discord.Member, action: str, amount: float):
    player=get_player(member.id); old=player["gold"]
    if action=="add":    player["gold"]=max(0,player["gold"]+amount); verb=f"+{fmt_price(amount)}"; color=0x2ECC71
    elif action=="remove": player["gold"]=max(0,player["gold"]-amount); verb=f"-{fmt_price(amount)}"; color=0xE74C3C
    else:                player["gold"]=max(0,amount); verb=f"= {fmt_price(amount)}"; color=0x3498DB
    save_player(member.id,player)
    embed=discord.Embed(title="💰 ปรับทองสำเร็จ",color=color)
    embed.add_field(name="👤 ผู้เล่น",     value=member.mention,                              inline=True)
    embed.add_field(name="🔧 การเปลี่ยน", value=verb,                                         inline=True)
    embed.add_field(name="💼 ก่อน→หลัง",  value=f"{fmt_price(old)} → {fmt_price(player['gold'])}",inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_give_item", description="[DM] มอบไอเทมให้ผู้เล่น", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น", item_id="ID ไอเทม", quantity="จำนวน")
@is_admin()
async def admin_give_item(interaction: discord.Interaction, member: discord.Member, item_id: str, quantity: int=1):
    item=load_shop()["items"].get(item_id) or MAGIC_ITEMS.get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`",ephemeral=True); return
    player=get_player(member.id)
    player["inventory"][item_id]=player["inventory"].get(item_id,0)+quantity
    save_player(member.id,player)
    embed=discord.Embed(title="🎁 มอบไอเทมสำเร็จ",color=0x9B59B6)
    embed.add_field(name="👤 ผู้รับ",value=member.mention,inline=True)
    embed.add_field(name="📦 ไอเทม",value=f"**{item['name']}** × {quantity}",inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_take_item", description="[DM] เอาไอเทมจากผู้เล่น", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น", item_id="ID ไอเทม", quantity="จำนวน")
@is_admin()
async def admin_take_item(interaction: discord.Interaction, member: discord.Member, item_id: str, quantity: int=1):
    player=get_player(member.id); have=player["inventory"].get(item_id,0)
    if have<quantity:
        await interaction.response.send_message(f"❌ {member.display_name} มี `{item_id}` แค่ {have} ชิ้น",ephemeral=True); return
    player["inventory"][item_id]-=quantity
    if player["inventory"][item_id]<=0: del player["inventory"][item_id]
    save_player(member.id,player)
    await interaction.response.send_message(f"🗑️ เอา `{item_id}` × {quantity} จาก {member.mention} ออกแล้ว")

@bot.tree.command(name="admin_add_magic", description="[DM] เพิ่ม Magic Item ใหม่เข้าตาราง", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID (ไม่มีช่องว่าง)", name="ชื่อ", item_type="ประเภท (Weapon/Armor/...)", rarity="Rarity", attune="ต้อง Attune?", desc="คำอธิบาย", price="ราคา GP")
@app_commands.choices(rarity=[
    app_commands.Choice(name="⚪ Common",    value="Common"),
    app_commands.Choice(name="🟢 Uncommon", value="Uncommon"),
    app_commands.Choice(name="🔵 Rare",     value="Rare"),
    app_commands.Choice(name="🟣 Very Rare",value="Very Rare"),
    app_commands.Choice(name="🟡 Legendary",value="Legendary"),
])
@is_admin()
async def admin_add_magic(interaction: discord.Interaction, item_id: str, name: str, item_type: str, rarity: str, attune: bool, desc: str, price: float):
    if " " in item_id:
        await interaction.response.send_message("❌ item_id ต้องไม่มีช่องว่าง",ephemeral=True); return
    if item_id in MAGIC_ITEMS:
        await interaction.response.send_message(f"❌ มี `{item_id}` อยู่แล้วในตาราง",ephemeral=True); return
    MAGIC_ITEMS[item_id]={"name":name,"type":item_type,"rarity":rarity,"attune":attune,"desc":desc,"price":price}
    re=RARITY_EMOJI.get(rarity,"")
    await interaction.response.send_message(f"✅ เพิ่ม {re} **{name}** (`{item_id}`) [{rarity}] ราคา {fmt_price(price)} เข้าตารางสุ่มแล้ว!")

# ─── Run ──────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN: print("❌ ไม่พบ DISCORD_TOKEN!")
else: bot.run(TOKEN)
