import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import json, os, random
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────
GUILD_ID   = 1460585900504387657
DATA_DIR   = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SHOP_FILE    = DATA_DIR / "shop.json"
PLAYERS_FILE = DATA_DIR / "players.json"
SETUP_FILE   = DATA_DIR / "setup.json"    # { shop_key: {channel_id, thread_id, message_id} }

# ─── Magic Items (Random Roll Pool) ───────────────────────────────────
MAGIC_ITEMS = {
    "potion_healing":        {"name":"Potion of Healing",           "type":"Potion",       "rarity":"Common",    "attune":False,"desc":"คืน HP 2d4+2",                                              "price":50},
    "candle_invocation":     {"name":"Candle of the Deep",          "type":"Wondrous",     "rarity":"Common",    "attune":False,"desc":"เทียนใต้น้ำ ติดไฟได้แม้ใต้น้ำ 1 ชม.",                       "price":30},
    "hat_disguise":          {"name":"Hat of Disguise",             "type":"Wondrous",     "rarity":"Common",    "attune":True, "desc":"ร่าย Disguise Self ได้ตามต้องการ",                          "price":65},
    "sending_stones":        {"name":"Sending Stones",              "type":"Wondrous",     "rarity":"Common",    "attune":False,"desc":"ส่งข้อความไม่จำกัดระยะ วันละ 1 ครั้ง",                      "price":75},
    "potion_climbing":       {"name":"Potion of Climbing",          "type":"Potion",       "rarity":"Common",    "attune":False,"desc":"Climbing Speed = Walking Speed 1 ชม.",                       "price":40},
    "spell_scroll_c0":       {"name":"Spell Scroll (Cantrip)",      "type":"Scroll",       "rarity":"Common",    "attune":False,"desc":"ม้วนคาถา Cantrip",                                           "price":30},
    "spell_scroll_l1":       {"name":"Spell Scroll (1st Level)",    "type":"Scroll",       "rarity":"Common",    "attune":False,"desc":"ม้วนคาถาระดับ 1",                                            "price":50},
    "silvered_weapon":       {"name":"Silvered Weapon",             "type":"Weapon",       "rarity":"Common",    "attune":False,"desc":"เอาชนะ resistance ของ lycanthrope/devil",                    "price":60},
    "potion_greater_healing":{"name":"Potion of Greater Healing",   "type":"Potion",       "rarity":"Uncommon",  "attune":False,"desc":"คืน HP 4d4+4",                                              "price":150},
    "bag_of_holding":        {"name":"Bag of Holding",              "type":"Wondrous",     "rarity":"Uncommon",  "attune":False,"desc":"กระเป๋าเก็บของ 500 lb / 64 cubic ft",                       "price":500},
    "boots_elvenkind":       {"name":"Boots of Elvenkind",          "type":"Wondrous",     "rarity":"Uncommon",  "attune":False,"desc":"Advantage บน Stealth (เสียงก้าว)",                          "price":400},
    "cloak_elvenkind":       {"name":"Cloak of Elvenkind",          "type":"Wondrous",     "rarity":"Uncommon",  "attune":True, "desc":"Advantage Stealth / Disadv. ต่อ Perception",                "price":450},
    "adamantine_armor":      {"name":"Adamantine Armor",            "type":"Armor",        "rarity":"Uncommon",  "attune":False,"desc":"Critical Hit กลายเป็น Normal Hit",                          "price":400},
    "weapon_plus1":          {"name":"Weapon +1",                   "type":"Weapon",       "rarity":"Uncommon",  "attune":False,"desc":"+1 attack & damage rolls",                                   "price":500},
    "ammo_plus1":            {"name":"Ammunition +1 (×20)",         "type":"Ammunition",   "rarity":"Uncommon",  "attune":False,"desc":"+1 attack/damage 20 ชิ้น",                                  "price":250},
    "helm_comprehend_lang":  {"name":"Helm of Comprehending Languages","type":"Wondrous",  "rarity":"Uncommon",  "attune":False,"desc":"ร่าย Comprehend Languages ได้ตามต้องการ",                    "price":300},
    "pearl_of_power":        {"name":"Pearl of Power",              "type":"Wondrous",     "rarity":"Uncommon",  "attune":True, "desc":"คืน spell slot ≤3 วันละ 1 ครั้ง",                           "price":400},
    "spell_scroll_l2":       {"name":"Spell Scroll (2nd Level)",    "type":"Scroll",       "rarity":"Uncommon",  "attune":False,"desc":"ม้วนคาถาระดับ 2",                                            "price":150},
    "spell_scroll_l3":       {"name":"Spell Scroll (3rd Level)",    "type":"Scroll",       "rarity":"Uncommon",  "attune":False,"desc":"ม้วนคาถาระดับ 3",                                            "price":300},
    "ring_protection":       {"name":"Ring of Protection",          "type":"Ring",         "rarity":"Uncommon",  "attune":True, "desc":"+1 AC และ +1 Saving Throws",                                 "price":500},
    "bracers_archery":       {"name":"Bracers of Archery",          "type":"Wondrous",     "rarity":"Uncommon",  "attune":True, "desc":"+2 damage ต่อ ranged attacks",                               "price":400},
    "cloak_protection":      {"name":"Cloak of Protection",         "type":"Wondrous",     "rarity":"Uncommon",  "attune":True, "desc":"+1 AC และ +1 Saving Throws",                                 "price":450},
    "potion_superior_healing":{"name":"Potion of Superior Healing", "type":"Potion",       "rarity":"Rare",      "attune":False,"desc":"คืน HP 8d4+8",                                              "price":600},
    "armor_plus1":           {"name":"Armor +1",                    "type":"Armor",        "rarity":"Rare",      "attune":False,"desc":"+1 AC",                                                       "price":1500},
    "weapon_plus2":          {"name":"Weapon +2",                   "type":"Weapon",       "rarity":"Rare",      "attune":False,"desc":"+2 attack & damage rolls",                                   "price":1200},
    "ring_spell_storing":    {"name":"Ring of Spell Storing",       "type":"Ring",         "rarity":"Rare",      "attune":True, "desc":"เก็บ spell ≤5 level ใช้ได้ทุกคน",                           "price":1500},
    "necklace_adaptation":   {"name":"Necklace of Adaptation",      "type":"Wondrous",     "rarity":"Rare",      "attune":True, "desc":"หายใจในสภาพอันตราย + Adv. ต้าน inhaled poison",             "price":800},
    "spell_scroll_l4":       {"name":"Spell Scroll (4th Level)",    "type":"Scroll",       "rarity":"Rare",      "attune":False,"desc":"ม้วนคาถาระดับ 4",                                            "price":800},
    "spell_scroll_l5":       {"name":"Spell Scroll (5th Level)",    "type":"Scroll",       "rarity":"Rare",      "attune":False,"desc":"ม้วนคาถาระดับ 5",                                            "price":1200},
    "flame_tongue":          {"name":"Flame Tongue",                "type":"Magic Weapon", "rarity":"Rare",      "attune":True, "desc":"ดาบไฟ เปิดใช้งาน: +2d6 fire damage",                        "price":2000},
    "ring_free_action":      {"name":"Ring of Free Action",         "type":"Ring",         "rarity":"Rare",      "attune":True, "desc":"Immune paralyzed/restrained จาก nonmagic",                   "price":2000},
    "wand_fireballs":        {"name":"Wand of Fireballs",           "type":"Wand",         "rarity":"Rare",      "attune":True, "desc":"7 charges | Fireball DC 15 ใช้ 3 charges",                  "price":1500},
    "staff_healing":         {"name":"Staff of Healing",            "type":"Staff",        "rarity":"Rare",      "attune":True, "desc":"10 charges | Cure Wounds, Lesser Restoration",               "price":1800},
    "amulet_health":         {"name":"Amulet of Health",            "type":"Wondrous",     "rarity":"Rare",      "attune":True, "desc":"CON = 19 ตราบใดที่สวม",                                      "price":2500},
    "potion_supreme_healing":{"name":"Potion of Supreme Healing",   "type":"Potion",       "rarity":"Very Rare", "attune":False,"desc":"คืน HP 10d4+20",                                            "price":1500},
    "armor_plus2":           {"name":"Armor +2",                    "type":"Armor",        "rarity":"Very Rare", "attune":False,"desc":"+2 AC",                                                       "price":4000},
    "weapon_plus3":          {"name":"Weapon +3",                   "type":"Weapon",       "rarity":"Very Rare", "attune":False,"desc":"+3 attack & damage rolls",                                   "price":3500},
    "dancing_sword":         {"name":"Dancing Sword",               "type":"Magic Weapon", "rarity":"Very Rare", "attune":True, "desc":"โยนดาบขึ้นบินสู้แทน 4 rounds",                              "price":4000},
    "sword_life_stealing":   {"name":"Sword of Life Stealing",      "type":"Magic Weapon", "rarity":"Very Rare", "attune":True, "desc":"crit: ดูด 10 HP จากเป้าหมาย",                               "price":3500},
    "spell_scroll_l6":       {"name":"Spell Scroll (6th Level)",    "type":"Scroll",       "rarity":"Very Rare", "attune":False,"desc":"ม้วนคาถาระดับ 6",                                            "price":2500},
    "spell_scroll_l7":       {"name":"Spell Scroll (7th Level)",    "type":"Scroll",       "rarity":"Very Rare", "attune":False,"desc":"ม้วนคาถาระดับ 7",                                            "price":4000},
    "ring_regeneration":     {"name":"Ring of Regeneration",        "type":"Ring",         "rarity":"Very Rare", "attune":True, "desc":"คืน HP 1d6/10 min + ฟื้น limb ที่ขาดได้",                  "price":6000},
    "manual_golems":         {"name":"Manual of Golems",            "type":"Wondrous",     "rarity":"Very Rare", "attune":False,"desc":"คู่มือสร้าง Golem",                                          "price":5000},
    "vorpal_sword":          {"name":"Vorpal Sword",                "type":"Magic Weapon", "rarity":"Legendary", "attune":True, "desc":"crit: ตัดหัวทันที + +3 attack/damage",                       "price":15000},
    "armor_invulnerability": {"name":"Armor of Invulnerability",    "type":"Armor",        "rarity":"Legendary", "attune":True, "desc":"Resistance nonmagical dmg | 10min/day: Immune",              "price":12000},
    "armor_plus3":           {"name":"Armor +3",                    "type":"Armor",        "rarity":"Legendary", "attune":False,"desc":"+3 AC",                                                       "price":10000},
    "belt_giant_strength":   {"name":"Belt of Giant Strength",      "type":"Wondrous",     "rarity":"Legendary", "attune":True, "desc":"STR = 29 (Storm Giant)",                                     "price":14000},
    "cloak_invisibility":    {"name":"Cloak of Invisibility",       "type":"Wondrous",     "rarity":"Legendary", "attune":True, "desc":"Invisible ตราบใดที่สวม สูงสุด 2 ชม./วัน",                   "price":20000},
    "holy_avenger":          {"name":"Holy Avenger",                "type":"Magic Weapon", "rarity":"Legendary", "attune":True, "desc":"Paladin only | +3 | 10d10 radiant vs undead/fiend",          "price":18000},
    "ring_djinni":           {"name":"Ring of Djinni Summoning",    "type":"Ring",         "rarity":"Legendary", "attune":True, "desc":"เรียก Djinni 1 ชม./วัน",                                     "price":20000},
    "staff_magi":            {"name":"Staff of the Magi",           "type":"Staff",        "rarity":"Legendary", "attune":True, "desc":"50 charges | ดูดซับ spell | ระเบิดได้",                      "price":25000},
}

RANK_TABLES = {
    "S": {"Common":0,  "Uncommon":5,  "Rare":20, "Very Rare":45,"Legendary":30},
    "A": {"Common":0,  "Uncommon":10, "Rare":35, "Very Rare":45,"Legendary":10},
    "B": {"Common":5,  "Uncommon":20, "Rare":50, "Very Rare":25,"Legendary":0},
    "C": {"Common":10, "Uncommon":45, "Rare":40, "Very Rare":5, "Legendary":0},
    "D": {"Common":30, "Uncommon":55, "Rare":15, "Very Rare":0, "Legendary":0},
    "E": {"Common":65, "Uncommon":30, "Rare":5,  "Very Rare":0, "Legendary":0},
    "F": {"Common":90, "Uncommon":10, "Rare":0,  "Very Rare":0, "Legendary":0},
}
RANK_COLORS   = {"S":0xFFD700,"A":0xFF6B35,"B":0xE74C3C,"C":0x9B59B6,"D":0x3498DB,"E":0x2ECC71,"F":0x95A5A6}
RARITY_EMOJI  = {"Common":"⚪","Uncommon":"🟢","Rare":"🔵","Very Rare":"🟣","Legendary":"🟡"}

# ─── Shop Definitions ─────────────────────────────────────────────────
SHOPS = {
    "blacksmith": {
        "name": "Brightsteel Forge",
        "npc":  "Brakk Ironbelly",
        "desc": "ยินดีต้อนรับสู่ร้านของช่างตีเหล็กผู้เชี่ยวชาญ "
                "อาวุธและเกราะทุกชิ้นถูกตีขึ้นด้วยมือ คุณภาพรับประกัน",
        "emoji": "⚒️",
        "color": 0xB7410E,
        "categories": {
            "simple_melee":   ("⚔️",  "Simple Melee Weapons"),
            "simple_ranged":  ("🏹",  "Simple Ranged Weapons"),
            "martial_melee":  ("🗡️",  "Martial Melee Weapons"),
            "martial_ranged": ("🎯",  "Martial Ranged Weapons"),
        },
    },
    "alchemist": {
        "name": "The Mystic Vial",
        "npc":  "Seraphine Duskwhisper",
        "desc": "ยาสมุนไพร ยาพิษ และอาวุธเวทย์ทุกชนิด "
                "ทุกขวดผ่านการกลั่นด้วยความประณีตจากอาจารย์ผู้เชี่ยวชาญ",
        "emoji": "🧪",
        "color": 0x8E44AD,
        "categories": {
            "potion":    ("🧪", "Potions & Elixirs"),
            "alch_gear": ("⚗️", "Alchemical Gear"),
        },
    },
    "general": {
        "name": "The Wanderer's Pack",
        "npc":  "Mabel “Mabs” Thornwick",
        "desc": "ทุกอย่างที่นักผจญภัยต้องการ ตั้งแต่เชือก ไปจนถึงเสื้อคลุม "
                "ราคายุติธรรม ของครบ ไม่ว่าคุณจะออกเดินทางไปไหนก็ตาม",
        "emoji": "🎒",
        "color": 0x27AE60,
        "categories": {
            "gear":     ("🎒", "Adventuring Gear"),
            "food":     ("🍳", "Food & Cooking"),
            "tools":    ("🔧", "Tools & Kits"),
            "clothing": ("👕", "Clothing & Apparel"),
        },
    },
}

# ─── Default Items (2024 PHB Official) ──────────────────────────────
DEFAULT_SHOP = {"items": {
    # ══ BLACKSMITH ══════════════════════════════════════════════════
    # Simple Melee Weapons
    "club":          {"name":"Club",          "desc":"1d4 Bludgeoning | Light | Mastery: Slow",                        "price":0.1,  "category":"simple_melee",  "stock":-1},
    "dagger":        {"name":"Dagger",        "desc":"1d4 Piercing | Finesse, Light, Thrown 20/60 | Mastery: Nick",   "price":2,    "category":"simple_melee",  "stock":-1},
    "greatclub":     {"name":"Greatclub",     "desc":"1d8 Bludgeoning | Two-Handed | Mastery: Push",                  "price":0.2,  "category":"simple_melee",  "stock":-1},
    "handaxe":       {"name":"Handaxe",       "desc":"1d6 Slashing | Light, Thrown 20/60 | Mastery: Vex",             "price":5,    "category":"simple_melee",  "stock":-1},
    "javelin":       {"name":"Javelin",       "desc":"1d6 Piercing | Thrown 30/120 | Mastery: Slow",                  "price":0.5,  "category":"simple_melee",  "stock":-1},
    "light_hammer":  {"name":"Light Hammer",  "desc":"1d4 Bludgeoning | Light, Thrown 20/60 | Mastery: Nick",         "price":2,    "category":"simple_melee",  "stock":-1},
    "mace":          {"name":"Mace",          "desc":"1d6 Bludgeoning | Mastery: Sap",                                "price":5,    "category":"simple_melee",  "stock":-1},
    "quarterstaff":  {"name":"Quarterstaff",  "desc":"1d6 Bludgeoning | Versatile 1d8 | Mastery: Topple",             "price":0.2,  "category":"simple_melee",  "stock":-1},
    "sickle":        {"name":"Sickle",        "desc":"1d4 Slashing | Light | Mastery: Nick",                          "price":1,    "category":"simple_melee",  "stock":-1},
    "spear":         {"name":"Spear",         "desc":"1d6 Piercing | Thrown 20/60, Versatile 1d8 | Mastery: Sap",     "price":1,    "category":"simple_melee",  "stock":-1},
    # Simple Ranged Weapons
    "dart":          {"name":"Dart",          "desc":"1d4 Piercing | Finesse, Thrown 20/60 | Mastery: Vex",           "price":0.05, "category":"simple_ranged", "stock":-1},
    "light_crossbow":{"name":"Light Crossbow","desc":"1d8 Piercing | Ammo (Bolt) 80/320, Loading, Two-Handed | Mastery: Slow", "price":25, "category":"simple_ranged", "stock":-1},
    "shortbow":      {"name":"Shortbow",      "desc":"1d6 Piercing | Ammo (Arrow) 80/320, Two-Handed | Mastery: Vex", "price":25,   "category":"simple_ranged", "stock":-1},
    "sling":         {"name":"Sling",         "desc":"1d4 Bludgeoning | Ammo (Bullet) 30/120 | Mastery: Slow",        "price":0.1,  "category":"simple_ranged", "stock":-1},
    # Martial Melee Weapons
    "battleaxe":     {"name":"Battleaxe",     "desc":"1d8 Slashing | Versatile 1d10 | Mastery: Topple",               "price":10,   "category":"martial_melee", "stock":-1},
    "flail":         {"name":"Flail",         "desc":"1d8 Bludgeoning | Mastery: Sap",                                "price":10,   "category":"martial_melee", "stock":-1},
    "glaive":        {"name":"Glaive",        "desc":"1d10 Slashing | Heavy, Reach, Two-Handed | Mastery: Graze",     "price":20,   "category":"martial_melee", "stock":-1},
    "greataxe":      {"name":"Greataxe",      "desc":"1d12 Slashing | Heavy, Two-Handed | Mastery: Cleave",           "price":30,   "category":"martial_melee", "stock":-1},
    "greatsword":    {"name":"Greatsword",    "desc":"2d6 Slashing | Heavy, Two-Handed | Mastery: Graze",             "price":50,   "category":"martial_melee", "stock":-1},
    "halberd":       {"name":"Halberd",       "desc":"1d10 Slashing | Heavy, Reach, Two-Handed | Mastery: Cleave",    "price":20,   "category":"martial_melee", "stock":-1},
    "lance":         {"name":"Lance",         "desc":"1d10 Piercing | Heavy, Reach, Two-Handed* | Mastery: Topple",   "price":10,   "category":"martial_melee", "stock":-1},
    "longsword":     {"name":"Longsword",     "desc":"1d8 Slashing | Versatile 1d10 | Mastery: Sap",                  "price":15,   "category":"martial_melee", "stock":-1},
    "maul":          {"name":"Maul",          "desc":"2d6 Bludgeoning | Heavy, Two-Handed | Mastery: Topple",         "price":10,   "category":"martial_melee", "stock":-1},
    "morningstar":   {"name":"Morningstar",   "desc":"1d8 Piercing | Mastery: Sap",                                   "price":15,   "category":"martial_melee", "stock":-1},
    "pike":          {"name":"Pike",          "desc":"1d10 Piercing | Heavy, Reach, Two-Handed | Mastery: Push",      "price":5,    "category":"martial_melee", "stock":-1},
    "rapier":        {"name":"Rapier",        "desc":"1d8 Piercing | Finesse | Mastery: Vex",                         "price":25,   "category":"martial_melee", "stock":-1},
    "scimitar":      {"name":"Scimitar",      "desc":"1d6 Slashing | Finesse, Light | Mastery: Nick",                 "price":25,   "category":"martial_melee", "stock":-1},
    "shortsword":    {"name":"Shortsword",    "desc":"1d6 Piercing | Finesse, Light | Mastery: Vex",                  "price":10,   "category":"martial_melee", "stock":-1},
    "trident":       {"name":"Trident",       "desc":"1d8 Piercing | Thrown 20/60, Versatile 1d10 | Mastery: Topple", "price":5,    "category":"martial_melee", "stock":-1},
    "warhammer":     {"name":"Warhammer",     "desc":"1d8 Bludgeoning | Versatile 1d10 | Mastery: Push",              "price":15,   "category":"martial_melee", "stock":-1},
    "war_pick":      {"name":"War Pick",      "desc":"1d8 Piercing | Versatile 1d10 | Mastery: Sap",                  "price":5,    "category":"martial_melee", "stock":-1},
    "whip":          {"name":"Whip",          "desc":"1d4 Slashing | Finesse, Reach | Mastery: Slow",                 "price":2,    "category":"martial_melee", "stock":-1},
    # Martial Ranged Weapons
    "blowgun":       {"name":"Blowgun",       "desc":"1 Piercing | Ammo (Needle) 25/100, Loading | Mastery: Vex",     "price":10,   "category":"martial_ranged","stock":-1},
    "hand_crossbow": {"name":"Hand Crossbow", "desc":"1d6 Piercing | Ammo (Bolt) 30/120, Light, Loading | Mastery: Vex","price":75, "category":"martial_ranged","stock":-1},
    "heavy_crossbow":{"name":"Heavy Crossbow","desc":"1d10 Piercing | Ammo (Bolt) 100/400, Heavy, Two-Handed | Mastery: Push","price":50,"category":"martial_ranged","stock":-1},
    "longbow":       {"name":"Longbow",       "desc":"1d8 Piercing | Ammo (Arrow) 150/600, Heavy, Two-Handed | Mastery: Slow","price":50,"category":"martial_ranged","stock":-1},
    # Ammunition
    "arrows_20":     {"name":"Arrows (×20)",          "desc":"กระสุนสำหรับ Shortbow / Longbow",             "price":1,    "category":"martial_ranged","stock":-1},
    "bolts_20":      {"name":"Crossbow Bolts (×20)",  "desc":"กระสุนสำหรับ Crossbow ทุกชนิด",              "price":1,    "category":"martial_ranged","stock":-1},
    "bullets_sling": {"name":"Sling Bullets (×20)",   "desc":"กระสุนสำหรับ Sling",                         "price":0.04, "category":"simple_ranged", "stock":-1},
    "needles_50":    {"name":"Blowgun Needles (×50)", "desc":"กระสุนสำหรับ Blowgun",                       "price":1,    "category":"martial_ranged","stock":-1},
    # ══ ALCHEMIST ═══════════════════════════════════════════════════
    # Potions
    "pot_heal":      {"name":"Potion of Healing",         "desc":"Bonus Action: คืน 2d4+2 HP (50 GP)",      "price":50,   "category":"potion",        "stock":-1},
    "pot_g_heal":    {"name":"Potion of Greater Healing", "desc":"Bonus Action: คืน 4d4+4 HP",               "price":150,  "category":"potion",        "stock":-1},
    "pot_s_heal":    {"name":"Potion of Superior Healing","desc":"Bonus Action: คืน 8d4+8 HP",               "price":600,  "category":"potion",        "stock":5},
    "pot_climbing":  {"name":"Potion of Climbing",        "desc":"Climbing Speed = Walking Speed นาน 1 ชม.","price":40,   "category":"potion",        "stock":-1},
    "pot_water_br":  {"name":"Potion of Water Breathing", "desc":"หายใจใต้น้ำได้นาน 1 ชม.",                 "price":180,  "category":"potion",        "stock":-1},
    "pot_invisib":   {"name":"Potion of Invisibility",    "desc":"Invisible 1 ชม. หรือจนกว่าจะโจมตี/ร่ายคาถา","price":400,"category":"potion",        "stock":3},
    "pot_speed":     {"name":"Potion of Speed",           "desc":"ผล Haste 1 นาที",                          "price":400,  "category":"potion",        "stock":3},
    # Alchemical Gear (2024 PHB official prices)
    "acid":          {"name":"Acid (vial)",               "desc":"Attack action: 2d6 Acid dmg, DC 8+DEX+Prof","price":25,  "category":"alch_gear",     "stock":-1},
    "alch_fire":     {"name":"Alchemist's Fire (flask)",  "desc":"Attack action: 1d4 Fire/turn จนดับ DC 8+DEX+Prof","price":50,"category":"alch_gear", "stock":-1},
    "antitoxin":     {"name":"Antitoxin (vial)",          "desc":"Bonus Action: Advantage ต้าน Poisoned 1 ชม.","price":50, "category":"alch_gear",     "stock":-1},
    "holy_water":    {"name":"Holy Water (flask)",        "desc":"Attack action: 2d8 Radiant ต่อ Fiend/Undead","price":25, "category":"alch_gear",     "stock":-1},
    "oil":           {"name":"Oil (flask)",               "desc":"เชื้อเพลิง Lamp/Lantern 6 ชม. | หรือขว้าย +5 fire dmg","price":0.1,"category":"alch_gear","stock":-1},
    "poison_basic":  {"name":"Poison, Basic (vial)",      "desc":"Bonus Action: ทาอาวุธ — +1d4 Poison dmg 1 นาที","price":100,"category":"alch_gear",  "stock":5},
    "healer_kit":    {"name":"Healer's Kit",              "desc":"10 uses | Utilize: Stabilize 0 HP โดยไม่ต้อง roll","price":5,"category":"alch_gear", "stock":-1},
    "component_pouch":{"name":"Component Pouch",         "desc":"เก็บ Material components ทั้งหมดของ spells","price":25,  "category":"alch_gear",     "stock":-1},
    # Arcane/Divine Focuses
    "focus_crystal": {"name":"Arcane Focus — Crystal",   "desc":"Spellcasting Focus สำหรับ Sorcerer/Warlock/Wizard","price":10,"category":"alch_gear","stock":-1},
    "focus_orb":     {"name":"Arcane Focus — Orb",       "desc":"Spellcasting Focus สำหรับ Sorcerer/Warlock/Wizard","price":20,"category":"alch_gear","stock":-1},
    "focus_wand":    {"name":"Arcane Focus — Wand",      "desc":"Spellcasting Focus สำหรับ Sorcerer/Warlock/Wizard","price":10,"category":"alch_gear","stock":-1},
    "focus_staff":   {"name":"Arcane Focus — Staff",     "desc":"Spellcasting Focus (also a Quarterstaff)",  "price":5,   "category":"alch_gear",     "stock":-1},
    "holy_symbol":   {"name":"Holy Symbol (Amulet)",     "desc":"Spellcasting Focus สำหรับ Cleric/Paladin",  "price":5,   "category":"alch_gear",     "stock":-1},
    "druidic_focus": {"name":"Druidic Focus — Yew Wand", "desc":"Spellcasting Focus สำหรับ Druid/Ranger",    "price":10,  "category":"alch_gear",     "stock":-1},
    "spell_scroll0": {"name":"Spell Scroll (Cantrip)",   "desc":"ร่ายคาถา Cantrip ได้ 1 ครั้ง DC 13 / +5",  "price":30,  "category":"alch_gear",     "stock":-1},
    "spell_scroll1": {"name":"Spell Scroll (Level 1)",   "desc":"ร่ายคาถา Level 1 ได้ 1 ครั้ง DC 13 / +5",  "price":50,  "category":"alch_gear",     "stock":-1},
    # ══ GENERAL STORE ════════════════════════════════════════════════
    # Adventuring Gear (2024 PHB official prices)
    "backpack":      {"name":"Backpack",          "desc":"ใส่ของ 30 lb / 1 cubic foot | ใช้เป็น saddlebag ได้",        "price":2,    "category":"gear","stock":-1},
    "ball_bearings": {"name":"Ball Bearings",     "desc":"Utilize: โปรยคลุม 10ft² — DC 10 DEX หรือ Prone",            "price":1,    "category":"gear","stock":-1},
    "bedroll":       {"name":"Bedroll",           "desc":"นอนได้ 1 คน | Auto-succeed ต้าน extreme cold",              "price":1,    "category":"gear","stock":-1},
    "bell":          {"name":"Bell",              "desc":"Utilize: ส่งเสียงได้ยิน 60ft",                               "price":1,    "category":"gear","stock":-1},
    "blanket":       {"name":"Blanket",           "desc":"Advantage ต้าน extreme cold",                                "price":0.5,  "category":"gear","stock":-1},
    "book":          {"name":"Book",              "desc":"+5 bonus INT checks เกี่ยวกับหัวข้อในหนังสือ",               "price":25,   "category":"gear","stock":-1},
    "caltrops":      {"name":"Caltrops",          "desc":"Utilize: โปรย 5ft² — DC 15 DEX หรือ 1 Piercing + Speed 0",  "price":1,    "category":"gear","stock":-1},
    "candle":        {"name":"Candle",            "desc":"Bright 5ft, Dim +5ft นาน 1 ชม.",                             "price":0.01, "category":"gear","stock":-1},
    "chain":         {"name":"Chain",             "desc":"Utilize: มัด Grappled/Incap. creature — DC 18 DEX หรือ Restrained","price":5,"category":"gear","stock":-1},
    "chest":         {"name":"Chest",             "desc":"ใส่ของ 12 cubic feet",                                       "price":5,    "category":"gear","stock":-1},
    "climbers_kit":  {"name":"Climber's Kit",     "desc":"Utilize: Anchor ตัวเอง ไม่ตกเกิน 25ft จาก anchor point",    "price":25,   "category":"gear","stock":-1},
    "crowbar":       {"name":"Crowbar",           "desc":"Advantage บน STR checks ที่ใช้คาน",                          "price":2,    "category":"gear","stock":-1},
    "grappling_hook":{"name":"Grappling Hook",    "desc":"Utilize: ขว้าง 50ft DC 13 DEX (Acrobatics) แล้วปีนเชือก",  "price":2,    "category":"gear","stock":-1},
    "hunting_trap":  {"name":"Hunting Trap",      "desc":"Utilize: วางกับดัก DC 13 DEX หรือ 1d4 Piercing + Speed 0",  "price":5,    "category":"gear","stock":-1},
    "lantern_bull":  {"name":"Lantern, Bullseye", "desc":"Bright 60ft Cone, Dim +60ft | เชื้อเพลิง Oil 6 ชม.",        "price":10,   "category":"gear","stock":-1},
    "lantern_hood":  {"name":"Lantern, Hooded",   "desc":"Bright 30ft, Dim +30ft | Bonus Action: ปิดฝา = Dim 5ft",    "price":5,    "category":"gear","stock":-1},
    "lamp":          {"name":"Lamp",              "desc":"Bright 15ft, Dim +30ft | เชื้อเพลิง Oil 6 ชม.",             "price":0.5,  "category":"gear","stock":-1},
    "lock":          {"name":"Lock",              "desc":"กุญแจล็อค DC 15 Thieves' Tools (มีกุญแจมาด้วย)",            "price":10,   "category":"gear","stock":-1},
    "magnifying_glass":{"name":"Magnifying Glass","desc":"Advantage ประเมินของ | จุดไฟได้ถ้ามีแสงแดด",                "price":100,  "category":"gear","stock":-1},
    "manacles":      {"name":"Manacles",          "desc":"มัด Small/Medium creature | DC 20 DEX หรือ DC 25 STR หลุด", "price":2,    "category":"gear","stock":-1},
    "map":           {"name":"Map",               "desc":"+5 WIS (Survival) checks นำทางในพื้นที่บนแผนที่",           "price":1,    "category":"gear","stock":-1},
    "mirror":        {"name":"Mirror (Steel)",    "desc":"ส่องมุม / ส่งสัญญาณแสง",                                    "price":5,    "category":"gear","stock":-1},
    "net":           {"name":"Net",               "desc":"Attack: DC 8+DEX+Prof หรือ Restrained | AC 10, 5 HP",        "price":1,    "category":"gear","stock":-1},
    "pole":          {"name":"Pole (10ft)",       "desc":"แตะของ 10ft ไกล | Advantage High/Long Jump ถ้า vault",       "price":0.05, "category":"gear","stock":-1},
    "portable_ram":  {"name":"Ram, Portable",     "desc":"+4 STR งัดประตู | ช่วยกัน 2 คน = Advantage",               "price":4,    "category":"gear","stock":-1},
    "rope":          {"name":"Rope (50ft)",       "desc":"DC 10 DEX ผูกเงื่อน | DC 20 STR ขาด | DC 15 DEX หลุด",     "price":1,    "category":"gear","stock":-1},
    "shovel":        {"name":"Shovel",            "desc":"1 ชม.: ขุดหลุม 5ft × 5ft ในดิน",                            "price":2,    "category":"gear","stock":-1},
    "signal_whistle":{"name":"Signal Whistle",    "desc":"Utilize: ส่งเสียงได้ยิน 600ft",                              "price":0.05, "category":"gear","stock":-1},
    "spyglass":      {"name":"Spyglass",          "desc":"ขยายภาพ 2 เท่า",                                            "price":1000, "category":"gear","stock":-1},
    "tent":          {"name":"Tent",              "desc":"นอนได้ 2 คน Small/Medium",                                   "price":2,    "category":"gear","stock":-1},
    "tinderbox":     {"name":"Tinderbox",         "desc":"Bonus Action: จุดเทียน/โคม | 1 นาที: จุดไฟอื่น",           "price":0.5,  "category":"gear","stock":-1},
    "torch":         {"name":"Torch",             "desc":"Bright 20ft, Dim +20ft นาน 1 ชม. | ตี = 1 Fire dmg",        "price":0.01, "category":"gear","stock":-1},
    "waterskin":     {"name":"Waterskin",         "desc":"บรรจุ 4 pints | ไม่ดื่มน้ำเสี่ยง Dehydration",             "price":0.2,  "category":"gear","stock":-1},
    # Packs (สะดวกซื้อรวม)
    "dungeoneers_pack":{"name":"Dungeoneer's Pack","desc":"Backpack, Caltrops, Crowbar, Oil×2, Rations×10, Rope, Tinderbox, Torch×10, Waterskin","price":12,"category":"gear","stock":-1},
    "explorers_pack":{"name":"Explorer's Pack",   "desc":"Backpack, Bedroll, Oil×2, Rations×10, Rope, Tinderbox, Torch×10, Waterskin","price":10,"category":"gear","stock":-1},
    "burglars_pack": {"name":"Burglar's Pack",    "desc":"Backpack, Ball Bearings, Bell, Candle×10, Crowbar, Lantern (Hooded), Oil×7, Rations×5, Rope, Tinderbox, Waterskin","price":16,"category":"gear","stock":-1},
    # Food & Cooking (2024 PHB)
    "rations":       {"name":"Rations (1 day)",   "desc":"อาหารเดินทาง: เนื้อแห้ง ผลไม้แห้ง ถั่ว",                   "price":0.5,  "category":"food","stock":-1},
    "bread_loaf":    {"name":"Bread (loaf)",      "desc":"ขนมปังหนึ่งก้อน",                                           "price":0.02, "category":"food","stock":-1},
    "cheese_hunk":   {"name":"Cheese (hunk)",     "desc":"เนยแข็งชิ้นใหญ่",                                           "price":0.1,  "category":"food","stock":-1},
    "meat_hunk":     {"name":"Meat (hunk)",       "desc":"เนื้อสัตว์ชิ้นใหญ่",                                        "price":0.03, "category":"food","stock":-1},
    "wine_common":   {"name":"Wine, Common (pitcher)","desc":"ไวน์ธรรมดา 1 เหยือก",                                   "price":0.2,  "category":"food","stock":-1},
    "wine_fine":     {"name":"Wine, Fine (bottle)","desc":"ไวน์ชั้นดี 1 ขวด",                                         "price":10,   "category":"food","stock":-1},
    "iron_pot":      {"name":"Iron Pot",          "desc":"หม้อเหล็กใส่ได้ 1 gallon",                                  "price":2,    "category":"food","stock":-1},
    "mess_kit":      {"name":"Mess Kit",          "desc":"กระทะ + ถ้วย + ช้อนส้อมพกพา",                               "price":0.2,  "category":"food","stock":-1},
    "flask":         {"name":"Flask",             "desc":"บรรจุ 1 pint",                                              "price":0.02, "category":"food","stock":-1},
    "jug":           {"name":"Jug",               "desc":"บรรจุ 1 gallon",                                            "price":0.02, "category":"food","stock":-1},
    # Tools & Kits (2024 PHB official prices)
    "thieves_tools": {"name":"Thieves' Tools",    "desc":"DC 15 DEX: ปลดล็อค / ปลดกับดัก",                           "price":25,   "category":"tools","stock":-1},
    "disguise_kit":  {"name":"Disguise Kit",      "desc":"Advantage CHA แปลงตัวเป็นคนอื่น",                           "price":25,   "category":"tools","stock":-1},
    "forgery_kit":   {"name":"Forgery Kit",       "desc":"DC 15 DEX: ปลอมเอกสาร / ตราประทับ",                        "price":15,   "category":"tools","stock":-1},
    "navigator_tools":{"name":"Navigator's Tools","desc":"DC 10 WIS: วางเส้นทาง | DC 15 WIS: หาตำแหน่งจากดาว",       "price":25,   "category":"tools","stock":-1},
    "cook_utensils": {"name":"Cook's Utensils",   "desc":"ชุดอุปกรณ์ทำอาหาร",                                        "price":1,    "category":"tools","stock":-1},
    "carpenter_tools":{"name":"Carpenter's Tools","desc":"เครื่องมือช่างไม้",                                        "price":8,    "category":"tools","stock":-1},
    "smith_tools":   {"name":"Smith's Tools",     "desc":"เครื่องมือช่างเหล็ก ซ่อมอาวุธ/เกราะ",                     "price":20,   "category":"tools","stock":-1},
    "poisoner_kit":  {"name":"Poisoner's Kit",    "desc":"ทำและใช้ยาพิษ INT check",                                   "price":50,   "category":"tools","stock":3},
    "herb_kit":      {"name":"Herbalism Kit",     "desc":"ทำ Antitoxin และยาสมุนไพร WIS check",                       "price":5,    "category":"tools","stock":-1},
    "musical_lute":  {"name":"Lute",              "desc":"เครื่องดนตรี — Lute (CHA)",                                "price":35,   "category":"tools","stock":-1},
    "musical_flute": {"name":"Flute",             "desc":"เครื่องดนตรี — Flute (CHA)",                               "price":2,    "category":"tools","stock":-1},
    "musical_drum":  {"name":"Drum",              "desc":"เครื่องดนตรี — Drum (CHA)",                                "price":6,    "category":"tools","stock":-1},
    # Clothing & Apparel (2024 PHB official prices)
    "clothes_common":{"name":"Clothes, Common",   "desc":"เสื้อผ้าธรรมดา",                                           "price":0.5,  "category":"clothing","stock":-1},
    "clothes_travel":{"name":"Clothes, Traveler's","desc":"เสื้อผ้านักเดินทาง ทนทาน",                                "price":2,    "category":"clothing","stock":-1},
    "clothes_fine":  {"name":"Clothes, Fine",     "desc":"เสื้อผ้าชั้นสูง งานเลี้ยงต้องการ",                         "price":15,   "category":"clothing","stock":-1},
    "costume":       {"name":"Costume",           "desc":"Advantage CHA แปลงตัวเป็นประเภทคนที่ชุดนั้นแทน",          "price":5,    "category":"clothing","stock":-1},
    "robe":          {"name":"Robe",              "desc":"เสื้อคลุมยาว พิธีกรรม/วิชาการ",                            "price":1,    "category":"clothing","stock":-1},
    "perfume":       {"name":"Perfume (vial)",    "desc":"Advantage CHA (Persuasion) ต่อ Indifferent Humanoid 1 ชม.","price":5,    "category":"clothing","stock":-1},
    "ink":           {"name":"Ink (1oz bottle)",  "desc":"หมึกเขียน ใช้ได้ ~500 หน้า",                               "price":10,   "category":"clothing","stock":-1},
    "paper":         {"name":"Paper (sheet)",     "desc":"กระดาษ 1 แผ่น ~250 คำ",                                    "price":0.2,  "category":"clothing","stock":-1},
    "parchment":     {"name":"Parchment (sheet)", "desc":"หนังสัตว์ทำกระดาษ 1 แผ่น ~250 คำ",                        "price":0.1,  "category":"clothing","stock":-1},
}}

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

def load_setup():
    if not SETUP_FILE.exists():
        with open(SETUP_FILE,"w",encoding="utf-8") as f: json.dump({},f)
        return {}
    with open(SETUP_FILE,encoding="utf-8") as f: return json.load(f)
def save_setup(d):
    with open(SETUP_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

def fmt_price(p):
    if p<0.01: return f"{round(p*100)} CP"
    if p<1:    return f"{round(p*10)} SP"
    if p<1000: return f"{p:g} GP"
    return f"{int(p):,} GP"

# ─── Random Roll ──────────────────────────────────────────────────────
def weighted_rarity(rank):
    weights=RANK_TABLES[rank]
    pool=[r for r,w in weights.items() for _ in range(w)]
    return random.choice(pool)
def roll_magic_items(rank,count=5):
    results=[]; attempts=0
    while len(results)<count and attempts<count*20:
        attempts+=1
        rarity=weighted_rarity(rank)
        pool=[iid for iid,item in MAGIC_ITEMS.items() if item["rarity"]==rarity and iid not in results]
        if not pool:
            pool=[iid for iid in MAGIC_ITEMS if iid not in results]
        if not pool: break
        results.append(random.choice(pool))
    return results

# ─── Bot ──────────────────────────────────────────────────────────────
intents=discord.Intents.default(); intents.message_content=True
bot=commands.Bot(command_prefix="!",intents=intents)
def is_admin():
    async def predicate(i:discord.Interaction):
        return i.user.guild_permissions.administrator or any(r.name in("DM","Admin","Game Master") for r in i.user.roles)
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    try:
        bot.tree.clear_commands(guild=None); await bot.tree.sync()
        synced=await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🌿 Synced {len(synced)} command(s) | Global cleared")
    except Exception as e: print(f"❌ {e}")
    # Re-register persistent views so buttons/dropdowns work after restart
    for shop_key in SHOPS:
        bot.add_view(ShopView(shop_key))
    bot.add_view(MarketView())
    print(f"⚔️  {bot.user} พร้อมใช้งานแล้ว!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching,name="🏪 Marketplace | /market"))

# ─── Shared UI ────────────────────────────────────────────────────────
def make_category_embed(shop_key,cat_key):
    items=load_shop()["items"]
    cat_items={k:v for k,v in items.items() if v["category"]==cat_key}
    cat_info=SHOPS[shop_key]["categories"][cat_key]
    emoji,label=cat_info
    color=SHOPS[shop_key]["color"]
    embed=discord.Embed(title=f"{emoji}  {label}",color=color)
    lines=[f"**{v['name']}** `{k}` — **{fmt_price(v['price'])}**\n> {v['desc']}" for k,v in cat_items.items()]
    embed.description="\n\n".join(lines) if lines else "*ไม่มีสินค้า*"
    embed.set_footer(text="ซื้อ: /buy <id> <จำนวน>")
    return embed

def coinpurse_embed(user):
    player=get_player(user.id)
    embed=discord.Embed(title=f"🪙 Coinpurse ของ {user.display_name}",description=f"**{fmt_price(player['gold'])}**",color=0xF1C40F)
    embed.set_thumbnail(url=user.display_avatar.url)
    return embed

def inventory_embed(user):
    player=get_player(user.id); inv=player.get("inventory",{})
    all_items={**load_shop()["items"],**{k:{"name":v["name"]} for k,v in MAGIC_ITEMS.items()}}
    embed=discord.Embed(title=f"🎒 Inventory ของ {user.display_name}",color=0x3498DB)
    embed.add_field(name="🪙 ทอง",value=f"**{fmt_price(player['gold'])}**",inline=False)
    if not inv:
        embed.add_field(name="📦 สิ่งของ",value="*กระเป๋าว่างเปล่า...*",inline=False)
    else:
        lines=[f"**{all_items.get(iid,{}).get('name',iid)}** × {qty}" for iid,qty in inv.items()]
        embed.add_field(name=f"📦 สิ่งของ ({len(inv)} ชนิด)",value="\n".join(lines),inline=False)
    embed.set_thumbnail(url=user.display_avatar.url)
    return embed

class ShopCategorySelect(discord.ui.Select):
    def __init__(self,shop_key):
        self.shop_key=shop_key
        cats=SHOPS[shop_key]["categories"]
        options=[discord.SelectOption(label=label,value=cat_key,emoji=emoji,description=f"ดูสินค้าในหมวด {label}") for cat_key,(emoji,label) in cats.items()]
        super().__init__(placeholder="เลือกหมวดสินค้า...",options=options)
    async def callback(self,i:discord.Interaction):
        embed=make_category_embed(self.shop_key,self.values[0])
        await i.response.send_message(embed=embed,ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self,shop_key):
        super().__init__(timeout=None)
        self.shop_key=shop_key
        self.add_item(ShopCategorySelect(shop_key))
    @discord.ui.button(label="Check Coinpurse",style=discord.ButtonStyle.success,emoji="🪙",custom_id="v5:coinpurse")
    async def cp(self,i:discord.Interaction,b): await i.response.send_message(embed=coinpurse_embed(i.user),ephemeral=True)
    @discord.ui.button(label="List of Items",style=discord.ButtonStyle.primary,emoji="📋",custom_id="v5:inventory")
    async def inv(self,i:discord.Interaction,b): await i.response.send_message(embed=inventory_embed(i.user),ephemeral=True)

def make_shop_embed(shop_key):
    s=SHOPS[shop_key]
    cats=s["categories"]
    cat_list=", ".join(f"{e} {l}" for _,(e,l) in cats.items())
    embed=discord.Embed(title=f"{s['emoji']}  {s['name']}",description=f"*พูดคุยกับ {s['npc']}*\n\n{s['desc']}",color=s["color"])
    embed.add_field(name="📦 หมวดหมู่",value=cat_list,inline=False)
    embed.set_footer(text="เลือกหมวดหมู่จาก dropdown • /buy <id> เพื่อซื้อ")
    return embed

# ─── Market Command ───────────────────────────────────────────────────
class MarketShopSelect(discord.ui.Select):
    def __init__(self):
        options=[
            discord.SelectOption(label="The Iron Bastion",    value="blacksmith",emoji="⚒️",description="Blacksmith — อาวุธและเกราะ"),
            discord.SelectOption(label="The Mystic Vial",     value="alchemist", emoji="🧪",description="Alchemist — ยาและของเวทย์"),
            discord.SelectOption(label="The Wanderer's Pack", value="general",   emoji="🎒",description="General Store — เสบียงและอุปกรณ์"),
        ]
        super().__init__(placeholder="เลือกร้านที่ต้องการเยี่ยมชม...",options=options)
    async def callback(self,i:discord.Interaction):
        shop_key=self.values[0]
        embed=make_shop_embed(shop_key)
        view=ShopView(shop_key)
        await i.response.send_message(embed=embed,view=view,ephemeral=True)

class MarketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(MarketShopSelect())
    @discord.ui.button(label="Check Coinpurse",style=discord.ButtonStyle.success,emoji="🪙",custom_id="market:coinpurse")
    async def cp(self,i:discord.Interaction,b): await i.response.send_message(embed=coinpurse_embed(i.user),ephemeral=True)
    @discord.ui.button(label="List of Items",style=discord.ButtonStyle.primary,emoji="📋",custom_id="market:inventory")
    async def inv(self,i:discord.Interaction,b): await i.response.send_message(embed=inventory_embed(i.user),ephemeral=True)

@bot.tree.command(name="market",description="🏪 เปิดตลาด — เลือกร้านที่ต้องการ",guild=discord.Object(id=GUILD_ID))
async def market(i:discord.Interaction):
    embed=discord.Embed(title="🏪 The Grand Market",color=0xF1C40F,
        description="ยินดีต้อนรับสู่ตลาดกลาง มีร้านค้าหลากหลายให้เลือกชม\nเลือกร้านจาก dropdown ด้านล่าง")
    embed.add_field(name="⚒️ The Iron Bastion",   value="*Duren Ironforge* — อาวุธและเกราะคุณภาพสูง",   inline=False)
    embed.add_field(name="🧪 The Mystic Vial",    value="*Seraphine Duskwhisper* — ยาและของเวทย์",       inline=False)
    embed.add_field(name="🎒 The Wanderer's Pack",value="*Mira Copperkettle* — เสบียงและอุปกรณ์ทั่วไป", inline=False)
    embed.set_footer(text="ใช้ /roll_reward <rank> เพื่อรับรางวัล Magic Items จาก Quest")
    await i.response.send_message(embed=embed,view=MarketView())


# ─── Setup Shop (Forum — ทีละร้าน) ───────────────────────────────────
@bot.tree.command(name="setup_shop",description="[DM] ผูกร้านค้าเข้ากับ Forum Thread ที่มีอยู่แล้ว",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(
    shop="เลือกร้านที่ต้องการผูก",
    thread="Forum Thread ของร้านนั้น",
)
@app_commands.choices(shop=[
    app_commands.Choice(name="⚒️ The Iron Bastion (Blacksmith)",     value="blacksmith"),
    app_commands.Choice(name="🧪 The Mystic Vial (Alchemist)",       value="alchemist"),
    app_commands.Choice(name="🎒 The Wanderer's Pack (General Store)",value="general"),
])
@is_admin()
async def setup_shop(i:discord.Interaction, shop:str, thread:discord.Thread):
    await i.response.defer(ephemeral=True)
    shop_info = SHOPS[shop]
    embed = make_shop_embed(shop)
    embed.set_footer(text="💬 ร้านนี้เปิดตลอด 24/7 | ใช้ /buy <id> เพื่อซื้อ")
    try:
        msg = await thread.send(embed=embed, view=ShopView(shop))
        setup_data = load_setup()
        setup_data[shop] = {"channel_id":thread.parent_id,"thread_id":thread.id,"message_id":msg.id}
        save_setup(setup_data)
        result_embed = discord.Embed(
            title=f"✅ ผูก {shop_info['emoji']} {shop_info['name']} สำเร็จ!",
            description=f"Shop embed โพสต์ลงใน {thread.mention} แล้วผู้เล่นสามารถเข้าไปซื้อของได้เลย",
            color=0x2ECC71
        )
        await i.followup.send(embed=result_embed, ephemeral=True)
    except Exception as e:
        await i.followup.send(f"❌ เกิดข้อผิดพลาด: {e}", ephemeral=True)

@bot.tree.command(name="setup_refresh",description="[DM] รีเฟรช Shop embed ในทุก thread ที่ผูกไว้",guild=discord.Object(id=GUILD_ID))
@is_admin()
async def setup_refresh(i:discord.Interaction):
    await i.response.defer(ephemeral=True)
    setup_data = load_setup()
    if not setup_data:
        await i.followup.send("❌ ยังไม่มีร้านที่ผูกไว้ ใช้ `/setup_shop` ก่อนครับ", ephemeral=True)
        return
    results = []
    for shop_key, data in setup_data.items():
        shop_info = SHOPS.get(shop_key)
        if not shop_info: continue
        try:
            thread = await bot.fetch_channel(data["thread_id"])
            msg = await thread.fetch_message(data["message_id"])
            embed = make_shop_embed(shop_key)
            embed.set_footer(text="💬 ร้านนี้เปิดตลอด 24/7 | ใช้ /buy <id> เพื่อซื้อ")
            await msg.edit(embed=embed, view=ShopView(shop_key))
            results.append(f"✅ {shop_info['emoji']} **{shop_info['name']}** รีเฟรชแล้ว")
        except Exception as e:
            results.append(f"❌ **{shop_key}**: {e}")
    embed_r = discord.Embed(title="🔄 รีเฟรช Shop Embeds", color=0x3498DB, description="\n".join(results))
    await i.followup.send(embed=embed_r, ephemeral=True)


# ─── Buy / Sell ───────────────────────────────────────────────────────
@bot.tree.command(name="buy",description="🛒 ซื้อสินค้า",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า",quantity="จำนวน")
async def buy(i:discord.Interaction,item_id:str,quantity:int=1):
    if quantity<=0: await i.response.send_message("❌ จำนวนต้องมากกว่า 0",ephemeral=True); return
    sd=load_shop(); item=sd["items"].get(item_id)
    if not item: await i.response.send_message(f"❌ ไม่พบ `{item_id}`\nใช้ `/market` เพื่อดู ID",ephemeral=True); return
    if item["stock"]!=-1 and item["stock"]<quantity: await i.response.send_message(f"❌ stock ไม่พอ! เหลือ **{item['stock']} ชิ้น**",ephemeral=True); return
    total=item["price"]*quantity; player=get_player(i.user.id)
    if player["gold"]<total: await i.response.send_message(f"❌ ทองไม่พอ!\nต้องการ **{fmt_price(total)}** | มี **{fmt_price(player['gold'])}**",ephemeral=True); return
    player["gold"]-=total; player["inventory"][item_id]=player["inventory"].get(item_id,0)+quantity; save_player(i.user.id,player)
    if item["stock"]!=-1: sd["items"][item_id]["stock"]-=quantity; save_shop(sd)
    embed=discord.Embed(title="✅ ซื้อสำเร็จ!",color=0x2ECC71)
    embed.add_field(name="🛍️ สินค้า", value=f"**{item['name']}** ×{quantity}",inline=True)
    embed.add_field(name="💸 จ่ายไป", value=f"**{fmt_price(total)}**",         inline=True)
    embed.add_field(name="🪙 คงเหลือ",value=f"**{fmt_price(player['gold'])}**",inline=True)
    await i.response.send_message(embed=embed)

@bot.tree.command(name="sell",description="💱 ขายสินค้า (ได้ 50%)",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า",quantity="จำนวน")
async def sell(i:discord.Interaction,item_id:str,quantity:int=1):
    if quantity<=0: await i.response.send_message("❌ จำนวนต้องมากกว่า 0",ephemeral=True); return
    player=get_player(i.user.id); have=player["inventory"].get(item_id,0)
    if have<quantity: await i.response.send_message(f"❌ มี `{item_id}` แค่ **{have} ชิ้น**",ephemeral=True); return
    item=load_shop()["items"].get(item_id) or MAGIC_ITEMS.get(item_id)
    if not item: await i.response.send_message(f"❌ ไม่พบข้อมูล `{item_id}`",ephemeral=True); return
    earned=item["price"]*quantity/2; player["inventory"][item_id]-=quantity
    if player["inventory"][item_id]<=0: del player["inventory"][item_id]
    player["gold"]+=earned; save_player(i.user.id,player)
    embed=discord.Embed(title="💱 ขายสำเร็จ!",color=0xE67E22)
    embed.add_field(name="🛍️ สินค้า", value=f"**{item['name']}** ×{quantity}",inline=True)
    embed.add_field(name="🪙 ได้รับ",  value=f"**{fmt_price(earned)}**",        inline=True)
    embed.add_field(name="💼 คงเหลือ", value=f"**{fmt_price(player['gold'])}**",inline=True)
    await i.response.send_message(embed=embed)

# ─── Roll Reward ──────────────────────────────────────────────────────
def make_roll_embed(rank,item_ids,quest_name=None):
    embed=discord.Embed(title=f"🎲 Random {len(item_ids)} items from Quest Rank {rank}",color=RANK_COLORS[rank])
    if quest_name: embed.add_field(name="Quest",value=f'*"{quest_name}"*',inline=False)
    for idx,iid in enumerate(item_ids,1):
        item=MAGIC_ITEMS.get(iid)
        if not item: continue
        re=RARITY_EMOJI.get(item["rarity"],"❓"); attune=" *(ต้อง Attune)*" if item.get("attune") else ""
        embed.add_field(name=f"Item {idx} : {item['name']}",
            value=f"**Type :** {item['type']}\n**Rarity :** {re} {item['rarity']}{attune}\n**Price :** {fmt_price(item['price'])}\n> {item['desc']}",inline=False)
    embed.set_footer(text="เลือกซื้อจาก dropdown ด้านล่าง")
    return embed

class BuyRollSelect(discord.ui.Select):
    def __init__(self,item_ids):
        seen=set(); options=[]
        for iid in item_ids:
            if iid in seen: continue
            seen.add(iid); item=MAGIC_ITEMS.get(iid)
            if item:
                options.append(discord.SelectOption(label=item["name"],value=iid,emoji=RARITY_EMOJI.get(item["rarity"],""),description=f"{item['rarity']} | {fmt_price(item['price'])}"))
        super().__init__(placeholder="เลือกซื้อไอเทม...",options=options,min_values=1,max_values=len(options))
    async def callback(self,i:discord.Interaction):
        player=get_player(i.user.id); bought=[]; failed=[]
        for iid in self.values:
            item=MAGIC_ITEMS.get(iid)
            if not item: continue
            if player["gold"]>=item["price"]:
                player["gold"]-=item["price"]; player["inventory"][iid]=player["inventory"].get(iid,0)+1; bought.append(item["name"])
            else: failed.append(f"{item['name']} (ต้องการ {fmt_price(item['price'])})")
        save_player(i.user.id,player)
        embed=discord.Embed(title="🛍️ ผลการซื้อ",color=0x2ECC71 if bought else 0xE74C3C)
        if bought: embed.add_field(name="✅ ซื้อสำเร็จ",value="\n".join(f"• {n}" for n in bought),inline=False)
        if failed: embed.add_field(name="❌ ทองไม่พอ",  value="\n".join(f"• {n}" for n in failed),inline=False)
        embed.add_field(name="🪙 ทองคงเหลือ",value=fmt_price(player["gold"]),inline=False)
        await i.response.send_message(embed=embed,ephemeral=True)

class RollView(discord.ui.View):
    def __init__(self,item_ids): super().__init__(timeout=300); self.add_item(BuyRollSelect(item_ids))

@bot.tree.command(name="roll_reward",description="🎲 สุ่ม Magic Items จาก Quest Rank [DM]",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(rank="Quest Rank",quest_name="ชื่อเควส",count="จำนวนไอเทม (default 5)")
@app_commands.choices(rank=[
    app_commands.Choice(name="🟡 S — Legendary/Very Rare",value="S"),
    app_commands.Choice(name="🟠 A — Very Rare/Rare",     value="A"),
    app_commands.Choice(name="🔴 B — Rare",               value="B"),
    app_commands.Choice(name="🟣 C — Rare/Uncommon",      value="C"),
    app_commands.Choice(name="🔵 D — Uncommon",           value="D"),
    app_commands.Choice(name="🟢 E — Common/Uncommon",    value="E"),
    app_commands.Choice(name="⚪ F — Common",             value="F"),
])
@is_admin()
async def roll_reward(i:discord.Interaction,rank:str,quest_name:str=None,count:int=5):
    count=max(1,min(count,10)); item_ids=roll_magic_items(rank,count)
    await i.response.send_message(embed=make_roll_embed(rank,item_ids,quest_name),view=RollView(item_ids))

# ─── Admin Commands ───────────────────────────────────────────────────
@bot.tree.command(name="admin_gold",description="[DM] ปรับทองผู้เล่น",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น",action="add/remove/set",amount="จำนวน GP")
@app_commands.choices(action=[app_commands.Choice(name="➕ เพิ่ม",value="add"),app_commands.Choice(name="➖ ลด",value="remove"),app_commands.Choice(name="🔧 กำหนด",value="set")])
@is_admin()
async def admin_gold(i:discord.Interaction,member:discord.Member,action:str,amount:float):
    p=get_player(member.id); old=p["gold"]
    if action=="add":    p["gold"]=max(0,p["gold"]+amount); verb=f"+{fmt_price(amount)}"; c=0x2ECC71
    elif action=="remove": p["gold"]=max(0,p["gold"]-amount); verb=f"-{fmt_price(amount)}"; c=0xE74C3C
    else:                p["gold"]=max(0,amount); verb=f"= {fmt_price(amount)}"; c=0x3498DB
    save_player(member.id,p)
    embed=discord.Embed(title="💰 ปรับทองสำเร็จ",color=c)
    embed.add_field(name="👤 ผู้เล่น",     value=member.mention,inline=True)
    embed.add_field(name="🔧 การเปลี่ยน",  value=verb,          inline=True)
    embed.add_field(name="💼 ก่อน→หลัง",   value=f"{fmt_price(old)} → {fmt_price(p['gold'])}",inline=True)
    await i.response.send_message(embed=embed)

@bot.tree.command(name="admin_give_item",description="[DM] มอบไอเทมให้ผู้เล่น",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น",item_id="ID",quantity="จำนวน")
@is_admin()
async def admin_give_item(i:discord.Interaction,member:discord.Member,item_id:str,quantity:int=1):
    item=load_shop()["items"].get(item_id) or MAGIC_ITEMS.get(item_id)
    if not item: await i.response.send_message(f"❌ ไม่พบ `{item_id}`",ephemeral=True); return
    p=get_player(member.id); p["inventory"][item_id]=p["inventory"].get(item_id,0)+quantity; save_player(member.id,p)
    embed=discord.Embed(title="🎁 มอบไอเทมสำเร็จ",color=0x9B59B6)
    embed.add_field(name="👤 ผู้รับ",value=member.mention,inline=True)
    embed.add_field(name="📦 ไอเทม",value=f"**{item['name']}** ×{quantity}",inline=True)
    await i.response.send_message(embed=embed)

@bot.tree.command(name="admin_take_item",description="[DM] เอาไอเทมจากผู้เล่น",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น",item_id="ID",quantity="จำนวน")
@is_admin()
async def admin_take_item(i:discord.Interaction,member:discord.Member,item_id:str,quantity:int=1):
    p=get_player(member.id); have=p["inventory"].get(item_id,0)
    if have<quantity: await i.response.send_message(f"❌ {member.display_name} มี `{item_id}` แค่ {have} ชิ้น",ephemeral=True); return
    p["inventory"][item_id]-=quantity
    if p["inventory"][item_id]<=0: del p["inventory"][item_id]
    save_player(member.id,p)
    await i.response.send_message(f"🗑️ เอา `{item_id}` ×{quantity} จาก {member.mention} ออกแล้ว")

@bot.tree.command(name="admin_add_item",description="[DM] เพิ่มสินค้าใหม่",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID",name="ชื่อ",desc="คำอธิบาย",price="ราคา GP",category="หมวด",stock="stock (-1=∞)")
@app_commands.choices(category=[
    app_commands.Choice(name="⚔️ Simple Melee",   value="simple_melee"),
    app_commands.Choice(name="🏹 Simple Ranged",  value="simple_ranged"),
    app_commands.Choice(name="🗡️ Martial Melee",  value="martial_melee"),
    app_commands.Choice(name="🎯 Martial Ranged", value="martial_ranged"),
    app_commands.Choice(name="🧪 Potion",         value="potion"),
    app_commands.Choice(name="⚗️ Alchemical Gear",value="alch_gear"),
    app_commands.Choice(name="🎒 Adventuring Gear",value="gear"),
    app_commands.Choice(name="🍳 Food & Cooking", value="food"),
    app_commands.Choice(name="🔧 Tools & Kits",   value="tools"),
    app_commands.Choice(name="👕 Clothing",        value="clothing"),
])
@is_admin()
async def admin_add_item(i:discord.Interaction,item_id:str,name:str,desc:str,price:float,category:str,stock:int=-1):
    if " " in item_id: await i.response.send_message("❌ item_id ห้ามมีช่องว่าง",ephemeral=True); return
    sd=load_shop()
    if item_id in sd["items"]: await i.response.send_message(f"❌ มี `{item_id}` อยู่แล้ว",ephemeral=True); return
    sd["items"][item_id]={"name":name,"desc":desc,"price":price,"category":category,"stock":stock}; save_shop(sd)
    await i.response.send_message(f"✅ เพิ่ม **{name}** (`{item_id}`) ราคา {fmt_price(price)} แล้ว!")

@bot.tree.command(name="admin_stock",description="[DM] ปรับ stock",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID",amount="จำนวน (-1=∞)")
@is_admin()
async def admin_stock(i:discord.Interaction,item_id:str,amount:int):
    sd=load_shop()
    if item_id not in sd["items"]: await i.response.send_message(f"❌ ไม่พบ `{item_id}`",ephemeral=True); return
    sd["items"][item_id]["stock"]=amount; save_shop(sd)
    await i.response.send_message(f"✅ ปรับ stock `{item_id}` เป็น **{'∞' if amount==-1 else amount}**")

@bot.tree.command(name="admin_remove_item",description="[DM] ลบสินค้า",guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID")
@is_admin()
async def admin_remove_item(i:discord.Interaction,item_id:str):
    sd=load_shop()
    if item_id not in sd["items"]: await i.response.send_message(f"❌ ไม่พบ `{item_id}`",ephemeral=True); return
    name=sd["items"][item_id]["name"]; del sd["items"][item_id]; save_shop(sd)
    await i.response.send_message(f"🗑️ ลบ **{name}** ออกจากร้านแล้ว")

# ─── Run ──────────────────────────────────────────────────────────────
TOKEN=os.getenv("DISCORD_TOKEN")
if not TOKEN: print("❌ ไม่พบ DISCORD_TOKEN!")
else: bot.run(TOKEN)
