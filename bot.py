import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import json, os
from pathlib import Path

# ─── Database ────────────────────────────────────────────────────────
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)
SHOP_FILE    = DATA_DIR / "shop.json"
PLAYERS_FILE = DATA_DIR / "players.json"

DEFAULT_SHOP = {"items": {
    # ── Simple Melee ──────────────────────────────────────────────────
    "club":          {"name": "Club",          "desc": "1d4 Bludgeoning | Light | Mastery: Slow",                        "price": 0.1,  "category": "simple_melee",   "stock": -1},
    "dagger":        {"name": "Dagger",        "desc": "1d4 Piercing | Finesse, Light, Thrown 20/60 | Mastery: Nick",   "price": 2,    "category": "simple_melee",   "stock": -1},
    "greatclub":     {"name": "Greatclub",     "desc": "1d8 Bludgeoning | Two-Handed | Mastery: Push",                  "price": 0.2,  "category": "simple_melee",   "stock": -1},
    "handaxe":       {"name": "Handaxe",       "desc": "1d6 Slashing | Light, Thrown 20/60 | Mastery: Vex",             "price": 5,    "category": "simple_melee",   "stock": -1},
    "javelin":       {"name": "Javelin",       "desc": "1d6 Piercing | Thrown 30/120 | Mastery: Slow",                  "price": 0.5,  "category": "simple_melee",   "stock": -1},
    "light_hammer":  {"name": "Light Hammer",  "desc": "1d4 Bludgeoning | Light, Thrown 20/60 | Mastery: Nick",         "price": 2,    "category": "simple_melee",   "stock": -1},
    "mace":          {"name": "Mace",          "desc": "1d6 Bludgeoning | Mastery: Sap",                                "price": 5,    "category": "simple_melee",   "stock": -1},
    "quarterstaff":  {"name": "Quarterstaff",  "desc": "1d6 Bludgeoning | Versatile (1d8) | Mastery: Topple",           "price": 0.2,  "category": "simple_melee",   "stock": -1},
    "sickle":        {"name": "Sickle",        "desc": "1d4 Slashing | Light | Mastery: Nick",                          "price": 1,    "category": "simple_melee",   "stock": -1},
    "spear":         {"name": "Spear",         "desc": "1d6 Piercing | Thrown 20/60, Versatile (1d8) | Mastery: Sap",   "price": 1,    "category": "simple_melee",   "stock": -1},
    # ── Simple Ranged ─────────────────────────────────────────────────
    "dart":          {"name": "Dart",          "desc": "1d4 Piercing | Finesse, Thrown 20/60 | Mastery: Vex",           "price": 0.05, "category": "simple_ranged",  "stock": -1},
    "light_crossbow":{"name": "Light Crossbow","desc": "1d8 Piercing | Ammo (Bolt) 80/320, Loading, Two-Handed | Mastery: Slow", "price": 25, "category": "simple_ranged", "stock": -1},
    "shortbow":      {"name": "Shortbow",      "desc": "1d6 Piercing | Ammo (Arrow) 80/320, Two-Handed | Mastery: Vex","price": 25,   "category": "simple_ranged",  "stock": -1},
    "sling":         {"name": "Sling",         "desc": "1d4 Bludgeoning | Ammo (Bullet) 30/120 | Mastery: Slow",        "price": 0.1,  "category": "simple_ranged",  "stock": -1},
    # ── Martial Melee ─────────────────────────────────────────────────
    "battleaxe":     {"name": "Battleaxe",     "desc": "1d8 Slashing | Versatile (1d10) | Mastery: Topple",             "price": 10,   "category": "martial_melee",  "stock": -1},
    "flail":         {"name": "Flail",         "desc": "1d8 Bludgeoning | Mastery: Sap",                                "price": 10,   "category": "martial_melee",  "stock": -1},
    "glaive":        {"name": "Glaive",        "desc": "1d10 Slashing | Heavy, Reach, Two-Handed | Mastery: Graze",     "price": 20,   "category": "martial_melee",  "stock": -1},
    "greataxe":      {"name": "Greataxe",      "desc": "1d12 Slashing | Heavy, Two-Handed | Mastery: Cleave",           "price": 30,   "category": "martial_melee",  "stock": -1},
    "greatsword":    {"name": "Greatsword",    "desc": "2d6 Slashing | Heavy, Two-Handed | Mastery: Graze",             "price": 50,   "category": "martial_melee",  "stock": -1},
    "halberd":       {"name": "Halberd",       "desc": "1d10 Slashing | Heavy, Reach, Two-Handed | Mastery: Cleave",    "price": 20,   "category": "martial_melee",  "stock": -1},
    "lance":         {"name": "Lance",         "desc": "1d10 Piercing | Heavy, Reach, Two-Handed* | Mastery: Topple",   "price": 10,   "category": "martial_melee",  "stock": -1},
    "longsword":     {"name": "Longsword",     "desc": "1d8 Slashing | Versatile (1d10) | Mastery: Sap",                "price": 15,   "category": "martial_melee",  "stock": -1},
    "maul":          {"name": "Maul",          "desc": "2d6 Bludgeoning | Heavy, Two-Handed | Mastery: Topple",         "price": 10,   "category": "martial_melee",  "stock": -1},
    "morningstar":   {"name": "Morningstar",   "desc": "1d8 Piercing | Mastery: Sap",                                   "price": 15,   "category": "martial_melee",  "stock": -1},
    "pike":          {"name": "Pike",          "desc": "1d10 Piercing | Heavy, Reach, Two-Handed | Mastery: Push",      "price": 5,    "category": "martial_melee",  "stock": -1},
    "rapier":        {"name": "Rapier",        "desc": "1d8 Piercing | Finesse | Mastery: Vex",                         "price": 25,   "category": "martial_melee",  "stock": -1},
    "scimitar":      {"name": "Scimitar",      "desc": "1d6 Slashing | Finesse, Light | Mastery: Nick",                 "price": 25,   "category": "martial_melee",  "stock": -1},
    "shortsword":    {"name": "Shortsword",    "desc": "1d6 Piercing | Finesse, Light | Mastery: Vex",                  "price": 10,   "category": "martial_melee",  "stock": -1},
    "trident":       {"name": "Trident",       "desc": "1d8 Piercing | Thrown 20/60, Versatile (1d10) | Mastery: Topple","price": 5,   "category": "martial_melee",  "stock": -1},
    "warhammer":     {"name": "Warhammer",     "desc": "1d8 Bludgeoning | Versatile (1d10) | Mastery: Push",            "price": 15,   "category": "martial_melee",  "stock": -1},
    "war_pick":      {"name": "War Pick",      "desc": "1d8 Piercing | Versatile (1d10) | Mastery: Sap",                "price": 5,    "category": "martial_melee",  "stock": -1},
    "whip":          {"name": "Whip",          "desc": "1d4 Slashing | Finesse, Reach | Mastery: Slow",                 "price": 2,    "category": "martial_melee",  "stock": -1},
    # ── Martial Ranged ────────────────────────────────────────────────
    "blowgun":       {"name": "Blowgun",       "desc": "1 Piercing | Ammo (Needle) 25/100, Loading | Mastery: Vex",     "price": 10,   "category": "martial_ranged", "stock": -1},
    "hand_crossbow": {"name": "Hand Crossbow", "desc": "1d6 Piercing | Ammo (Bolt) 30/120, Light, Loading | Mastery: Vex","price": 75, "category": "martial_ranged", "stock": -1},
    "heavy_crossbow":{"name": "Heavy Crossbow","desc": "1d10 Piercing | Ammo (Bolt) 100/400, Heavy, Loading, Two-Handed | Mastery: Push","price": 50,"category": "martial_ranged","stock": -1},
    "longbow":       {"name": "Longbow",       "desc": "1d8 Piercing | Ammo (Arrow) 150/600, Heavy, Two-Handed | Mastery: Slow","price": 50,"category": "martial_ranged","stock": -1},
}}

CATEGORIES = {
    "simple_melee":   ("⚔️",  "Simple Melee Weapons",   0xE67E22),
    "simple_ranged":  ("🏹",  "Simple Ranged Weapons",  0xE67E22),
    "martial_melee":  ("🗡️",  "Martial Melee Weapons",  0xE74C3C),
    "martial_ranged": ("🎯",  "Martial Ranged Weapons", 0xE74C3C),
}

SHOP_NAME  = "The Iron Bastion"
SHOP_DESC  = (
    "ยินดีต้อนรับสู่ร้านของช่างตีเหล็กผู้เชี่ยวชาญ "
    "ที่นี่มีอาวุธคุณภาพสูงพร้อมจำหน่ายทุกชนิด "
    "ไม่ว่าจะเป็นนักรบมือใหม่หรือทหารผ่านศึก ร้านนี้มีทุกสิ่งที่คุณต้องการ"
)
SHOP_COLOR = 0xB7410E
GUILD_ID   = 1460585900504387657

# ─── DB Helpers ──────────────────────────────────────────────────────
def load_shop():
    if not SHOP_FILE.exists():
        with open(SHOP_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SHOP, f, ensure_ascii=False, indent=2)
        return DEFAULT_SHOP.copy()
    with open(SHOP_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_shop(d):
    with open(SHOP_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def load_players():
    if not PLAYERS_FILE.exists():
        with open(PLAYERS_FILE, "w", encoding="utf-8") as f: json.dump({}, f)
        return {}
    with open(PLAYERS_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_players(d):
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

def get_player(uid):
    players = load_players(); key = str(uid)
    if key not in players:
        players[key] = {"gold": 100, "inventory": {}}
        save_players(players)
    return players[key]

def save_player(uid, data):
    players = load_players(); players[str(uid)] = data; save_players(players)

# ─── Bot Setup ────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator or \
               any(r.name in ("DM", "Admin", "Game Master") for r in interaction.user.roles)
    return app_commands.check(predicate)

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"🌿 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print(f"⚔️  {bot.user} พร้อมใช้งานแล้ว!")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching, name=f"🏪 {SHOP_NAME} | /shop"))

# ─── UI Helpers ──────────────────────────────────────────────────────
def fmt_price(p):
    if p < 1:
        sp = round(p * 10)
        if sp < 10: return f"{round(p*100)} CP"
        return f"{sp} SP"
    return f"{int(p)} GP"

def make_shop_embed():
    embed = discord.Embed(title=f"⚒️  {SHOP_NAME}", description=SHOP_DESC, color=SHOP_COLOR)
    embed.set_footer(text="เลือกหมวดหมู่จาก dropdown • ใช้ /buy <id> เพื่อซื้อ")
    return embed

def make_category_embed(cat_key: str):
    items = load_shop()["items"]
    cat_items = {k: v for k, v in items.items() if v["category"] == cat_key}
    emoji, label, color = CATEGORIES[cat_key]
    embed = discord.Embed(title=f"{emoji}  {label}", color=color)
    lines = []
    for iid, item in cat_items.items():
        stock = "∞" if item["stock"] == -1 else str(item["stock"])
        lines.append(f"**{item['name']}** `{iid}` — **{fmt_price(item['price'])}**\n> {item['desc']}")
    embed.description = "\n\n".join(lines) if lines else "*ไม่มีสินค้าในหมวดนี้*"
    embed.set_footer(text="ซื้อ: /buy <id> <จำนวน>")
    return embed

# ─── UI Components ────────────────────────────────────────────────────
class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Simple Melee Weapons",   value="simple_melee",   emoji="⚔️",  description="Club, Dagger, Handaxe, Spear..."),
            discord.SelectOption(label="Simple Ranged Weapons",  value="simple_ranged",  emoji="🏹",  description="Shortbow, Crossbow, Sling, Dart..."),
            discord.SelectOption(label="Martial Melee Weapons",  value="martial_melee",  emoji="🗡️",  description="Longsword, Greatsword, Rapier..."),
            discord.SelectOption(label="Martial Ranged Weapons", value="martial_ranged", emoji="🎯",  description="Longbow, Hand Crossbow, Blowgun..."),
        ]
        super().__init__(placeholder="เลือกหมวดหมู่สินค้า...", options=options)

    async def callback(self, interaction: discord.Interaction):
        embed = make_category_embed(self.values[0])
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategorySelect())

    @discord.ui.button(label="Check Coinpurse", style=discord.ButtonStyle.success, emoji="🪙", custom_id="shop:coinpurse")
    async def coinpurse(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = get_player(interaction.user.id)
        embed = discord.Embed(
            title=f"🪙 Coinpurse ของ {interaction.user.display_name}",
            description=f"**{fmt_price(player['gold'])}**",
            color=0xF1C40F
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="List of Items", style=discord.ButtonStyle.primary, emoji="📋", custom_id="shop:inventory")
    async def inventory_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = get_player(interaction.user.id)
        inv = player.get("inventory", {})
        shop_items = load_shop()["items"]
        embed = discord.Embed(
            title=f"🎒 Inventory ของ {interaction.user.display_name}",
            color=0x3498DB
        )
        embed.add_field(name="🪙 ทอง", value=f"**{fmt_price(player['gold'])}**", inline=False)
        if not inv:
            embed.add_field(name="📦 สิ่งของ", value="*กระเป๋าว่างเปล่า...*", inline=False)
        else:
            lines = []
            for iid, qty in inv.items():
                it = shop_items.get(iid)
                name = it["name"] if it else iid
                lines.append(f"**{name}** × {qty}")
            embed.add_field(name=f"📦 สิ่งของ ({len(inv)} ชนิด)", value="\n".join(lines), inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ─── Commands ─────────────────────────────────────────────────────────
@bot.tree.command(name="shop", description="🏪 เปิดร้านค้า The Iron Bastion", guild=discord.Object(id=GUILD_ID))
async def shop(interaction: discord.Interaction):
    await interaction.response.send_message(embed=make_shop_embed(), view=ShopView())

@bot.tree.command(name="buy", description="🛒 ซื้อสินค้า", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า (เช่น longsword)", quantity="จำนวน")
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
    item = load_shop()["items"].get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบข้อมูลสินค้า `{item_id}`", ephemeral=True); return
    earned = item["price"] * quantity / 2
    player["inventory"][item_id] -= quantity
    if player["inventory"][item_id] <= 0: del player["inventory"][item_id]
    player["gold"] += earned
    save_player(interaction.user.id, player)
    embed = discord.Embed(title="💱 ขายสำเร็จ!", color=0xE67E22)
    embed.add_field(name="🛍️ สินค้า",  value=f"**{item['name']}** × {quantity}", inline=True)
    embed.add_field(name="🪙 ได้รับ",   value=f"**{fmt_price(earned)}**",          inline=True)
    embed.add_field(name="💼 คงเหลือ",  value=f"**{fmt_price(player['gold'])}**",  inline=True)
    await interaction.response.send_message(embed=embed)

# ─── Admin ────────────────────────────────────────────────────────────
@bot.tree.command(name="admin_gold", description="[DM] ปรับทองของผู้เล่น", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น", action="add/remove/set", amount="จำนวน GP")
@app_commands.choices(action=[
    app_commands.Choice(name="➕ เพิ่ม", value="add"),
    app_commands.Choice(name="➖ ลด",   value="remove"),
    app_commands.Choice(name="🔧 กำหนด", value="set"),
])
@is_admin()
async def admin_gold(interaction: discord.Interaction, member: discord.Member, action: str, amount: float):
    player = get_player(member.id); old = player["gold"]
    if action == "add":    player["gold"] = max(0, player["gold"] + amount); verb = f"+{fmt_price(amount)}"; color = 0x2ECC71
    elif action == "remove": player["gold"] = max(0, player["gold"] - amount); verb = f"-{fmt_price(amount)}"; color = 0xE74C3C
    else:                  player["gold"] = max(0, amount); verb = f"= {fmt_price(amount)}"; color = 0x3498DB
    save_player(member.id, player)
    embed = discord.Embed(title="💰 ปรับทองสำเร็จ", color=color)
    embed.add_field(name="👤 ผู้เล่น",     value=member.mention,                              inline=True)
    embed.add_field(name="🔧 การเปลี่ยน", value=verb,                                         inline=True)
    embed.add_field(name="💼 ก่อน→หลัง",  value=f"{fmt_price(old)} → {fmt_price(player['gold'])}", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_give_item", description="[DM] มอบไอเทมให้ผู้เล่น", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น", item_id="ID ไอเทม", quantity="จำนวน")
@is_admin()
async def admin_give_item(interaction: discord.Interaction, member: discord.Member, item_id: str, quantity: int = 1):
    item = load_shop()["items"].get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True); return
    player = get_player(member.id)
    player["inventory"][item_id] = player["inventory"].get(item_id, 0) + quantity
    save_player(member.id, player)
    embed = discord.Embed(title="🎁 มอบไอเทมสำเร็จ", color=0x9B59B6)
    embed.add_field(name="👤 ผู้รับ", value=member.mention,                     inline=True)
    embed.add_field(name="📦 ไอเทม", value=f"**{item['name']}** × {quantity}", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_take_item", description="[DM] เอาไอเทมจากผู้เล่น", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น", item_id="ID ไอเทม", quantity="จำนวน")
@is_admin()
async def admin_take_item(interaction: discord.Interaction, member: discord.Member, item_id: str, quantity: int = 1):
    player = get_player(member.id)
    have = player["inventory"].get(item_id, 0)
    if have < quantity:
        await interaction.response.send_message(f"❌ {member.display_name} มี `{item_id}` แค่ {have} ชิ้น", ephemeral=True); return
    player["inventory"][item_id] -= quantity
    if player["inventory"][item_id] <= 0: del player["inventory"][item_id]
    save_player(member.id, player)
    await interaction.response.send_message(f"🗑️ เอา `{item_id}` × {quantity} จาก {member.mention} ออกแล้ว")

@bot.tree.command(name="admin_add_item", description="[DM] เพิ่มสินค้าใหม่", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID (ไม่มีช่องว่าง)", name="ชื่อแสดง", desc="คำอธิบาย", price="ราคา (GP)", category="หมวดหมู่", stock="stock (-1=ไม่จำกัด)")
@app_commands.choices(category=[
    app_commands.Choice(name="⚔️ Simple Melee",   value="simple_melee"),
    app_commands.Choice(name="🏹 Simple Ranged",  value="simple_ranged"),
    app_commands.Choice(name="🗡️ Martial Melee",  value="martial_melee"),
    app_commands.Choice(name="🎯 Martial Ranged", value="martial_ranged"),
])
@is_admin()
async def admin_add_item(interaction: discord.Interaction, item_id: str, name: str, desc: str, price: float, category: str, stock: int = -1):
    if " " in item_id:
        await interaction.response.send_message("❌ item_id ต้องไม่มีช่องว่าง", ephemeral=True); return
    shop_data = load_shop()
    if item_id in shop_data["items"]:
        await interaction.response.send_message(f"❌ มี `{item_id}` อยู่แล้ว", ephemeral=True); return
    shop_data["items"][item_id] = {"name": name, "desc": desc, "price": price, "category": category, "stock": stock}
    save_shop(shop_data)
    await interaction.response.send_message(f"✅ เพิ่ม **{name}** (`{item_id}`) ราคา {fmt_price(price)} แล้ว!")

@bot.tree.command(name="admin_stock", description="[DM] ปรับ stock สินค้า", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า", amount="จำนวน (-1=ไม่จำกัด)")
@is_admin()
async def admin_stock(interaction: discord.Interaction, item_id: str, amount: int):
    shop_data = load_shop()
    if item_id not in shop_data["items"]:
        await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True); return
    shop_data["items"][item_id]["stock"] = amount; save_shop(shop_data)
    await interaction.response.send_message(f"✅ ปรับ stock `{item_id}` เป็น **{'∞' if amount==-1 else amount}** แล้ว")

@bot.tree.command(name="admin_remove_item", description="[DM] ลบสินค้าออกจากร้าน", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า")
@is_admin()
async def admin_remove_item(interaction: discord.Interaction, item_id: str):
    shop_data = load_shop()
    if item_id not in shop_data["items"]:
        await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True); return
    name = shop_data["items"][item_id]["name"]; del shop_data["items"][item_id]; save_shop(shop_data)
    await interaction.response.send_message(f"🗑️ ลบ **{name}** ออกจากร้านแล้ว")

# ─── Run ──────────────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    print("❌ ไม่พบ DISCORD_TOKEN!")
else:
    bot.run(TOKEN)
