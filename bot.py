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
    # Simple Weapons
    "club":         {"name": "Club",         "desc": "1d4 Bludgeoning | Light",                      "price": 1,   "category": "simple_weapon",  "stock": -1},
    "dagger":       {"name": "Dagger",       "desc": "1d4 Piercing | Finesse, Light, Thrown 20/60",  "price": 2,   "category": "simple_weapon",  "stock": -1},
    "handaxe":      {"name": "Handaxe",      "desc": "1d6 Slashing | Light, Thrown 20/60",           "price": 5,   "category": "simple_weapon",  "stock": -1},
    "javelin":      {"name": "Javelin",       "desc": "1d6 Piercing | Thrown 30/120",                 "price": 5,   "category": "simple_weapon",  "stock": -1},
    "spear":        {"name": "Spear",        "desc": "1d6 Piercing | Thrown 20/60, Versatile 1d8",   "price": 1,   "category": "simple_weapon",  "stock": -1},
    "shortbow":     {"name": "Shortbow",     "desc": "1d6 Piercing | Ammunition, Range 80/320",      "price": 25,  "category": "simple_weapon",  "stock": -1},
    "light_xbow":   {"name": "Light Crossbow","desc": "1d8 Piercing | Ammunition, Range 80/320",     "price": 25,  "category": "simple_weapon",  "stock": -1},
    # Martial Weapons
    "shortsword":   {"name": "Shortsword",   "desc": "1d6 Piercing | Finesse, Light",                "price": 10,  "category": "martial_weapon", "stock": -1},
    "longsword":    {"name": "Longsword",    "desc": "1d8 Slashing | Versatile 1d10",                "price": 15,  "category": "martial_weapon", "stock": -1},
    "battleaxe":    {"name": "Battleaxe",    "desc": "1d8 Slashing | Versatile 1d10",                "price": 10,  "category": "martial_weapon", "stock": -1},
    "warhammer":    {"name": "Warhammer",    "desc": "1d8 Bludgeoning | Versatile 1d10",             "price": 15,  "category": "martial_weapon", "stock": -1},
    "rapier":       {"name": "Rapier",       "desc": "1d8 Piercing | Finesse",                       "price": 25,  "category": "martial_weapon", "stock": -1},
    "greataxe":     {"name": "Greataxe",     "desc": "1d12 Slashing | Heavy, Two-Handed",            "price": 30,  "category": "martial_weapon", "stock": 3},
    "greatsword":   {"name": "Greatsword",   "desc": "2d6 Slashing | Heavy, Two-Handed",             "price": 50,  "category": "martial_weapon", "stock": 2},
    "longbow":      {"name": "Longbow",      "desc": "1d8 Piercing | Ammunition, Range 150/600",     "price": 50,  "category": "martial_weapon", "stock": -1},
    # Armor
    "padded":       {"name": "Padded Armor", "desc": "AC 11 + DEX | เกราะผ้า น้ำหนักเบา",           "price": 5,   "category": "armor",          "stock": -1},
    "leather":      {"name": "Leather Armor","desc": "AC 11 + DEX | เกราะหนัง น้ำหนักเบา",          "price": 10,  "category": "armor",          "stock": -1},
    "studded":      {"name": "Studded Leather","desc": "AC 12 + DEX | เกราะหนังเสริมหมุด",          "price": 45,  "category": "armor",          "stock": -1},
    "hide":         {"name": "Hide Armor",   "desc": "AC 12 + DEX (max 2) | เกราะหนังสัตว์",        "price": 10,  "category": "armor",          "stock": -1},
    "chain_shirt":  {"name": "Chain Shirt",  "desc": "AC 13 + DEX (max 2) | เกราะโซ่เบา",           "price": 50,  "category": "armor",          "stock": -1},
    "scale_mail":   {"name": "Scale Mail",   "desc": "AC 14 + DEX (max 2) | เกราะเกล็ด",            "price": 50,  "category": "armor",          "stock": -1},
    "breastplate":  {"name": "Breastplate",  "desc": "AC 14 + DEX (max 2) | เกราะอกเหล็ก",          "price": 400, "category": "armor",          "stock": 1},
    "chain_mail":   {"name": "Chain Mail",   "desc": "AC 16 | Heavy, STR 13 req.",                   "price": 75,  "category": "armor",          "stock": -1},
    "splint":       {"name": "Splint Armor", "desc": "AC 17 | Heavy, STR 15 req.",                   "price": 200, "category": "armor",          "stock": 2},
    "plate":        {"name": "Plate Armor",  "desc": "AC 18 | Heavy, STR 15 req. | เกราะเต็มตัว",   "price": 1500,"category": "armor",          "stock": 1},
    "shield":       {"name": "Shield",       "desc": "+2 AC | โล่ไม้หรือเหล็ก",                     "price": 10,  "category": "armor",          "stock": -1},
}}

CATEGORIES = {
    "simple_weapon":  ("✂️", "Simple Weapon",  0xE67E22),
    "martial_weapon": ("⚔️", "Martial Weapon", 0xE74C3C),
    "armor":          ("🛡️", "Armor",          0x3498DB),
}

SHOP_NAME = "The Iron Bastion"
SHOP_DESC = (
    "ยินดีต้อนรับสู่ร้านของช่างตีเหล็กผู้เชี่ยวชาญ "
    "ที่นี่มีอาวุธและเกราะคุณภาพสูงพร้อมจำหน่าย "
    "ไม่ว่าจะเป็นนักรบมือใหม่หรือทหารผ่านศึก ร้านนี้มีทุกสิ่งที่คุณต้องการ"
)
SHOP_COLOR = 0xB7410E  # สีสนิมเหล็ก

GUILD_ID = 1460585900504387657

# ─── DB Helpers ──────────────────────────────────────────────────────
def load_shop():
    if not SHOP_FILE.exists():
        with open(SHOP_FILE, "w", encoding="utf-8") as f: json.dump(DEFAULT_SHOP, f, ensure_ascii=False, indent=2)
        return DEFAULT_SHOP.copy()
    with open(SHOP_FILE, encoding="utf-8") as f: return json.load(f)

def save_shop(d):
    with open(SHOP_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def load_players():
    if not PLAYERS_FILE.exists():
        with open(PLAYERS_FILE, "w", encoding="utf-8") as f: json.dump({}, f)
        return {}
    with open(PLAYERS_FILE, encoding="utf-8") as f: return json.load(f)

def save_players(d):
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)

def get_player(uid):
    players = load_players(); key = str(uid)
    if key not in players:
        players[key] = {"gold": 100, "inventory": {}}
        save_players(players)
    return players[key]

def save_player(uid, data):
    players = load_players(); players[str(uid)] = data; save_players(players)

# ─── Bot ─────────────────────────────────────────────────────────────
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

# ─── UI Components ───────────────────────────────────────────────────

def make_shop_embed():
    embed = discord.Embed(
        title=f"⚒️  {SHOP_NAME}",
        description=SHOP_DESC,
        color=SHOP_COLOR
    )
    embed.set_footer(text="เลือกหมวดหมู่จาก dropdown ด้านล่าง • ใช้ /buy <id> เพื่อซื้อ")
    return embed

def make_category_embed(cat_key: str, items: dict):
    emoji, label, color = CATEGORIES[cat_key]
    embed = discord.Embed(title=f"{emoji}  {label}", color=color)
    lines = []
    for iid, item in items.items():
        stock = "∞" if item["stock"] == -1 else str(item["stock"])
        lines.append(
            f"**{item['name']}** `{iid}` — **{item['price']} gp** | {item['desc']} | stock: {stock}"
        )
    embed.description = "\n".join(lines) if lines else "*ไม่มีสินค้า*"
    embed.set_footer(text=f"ซื้อ: /buy <id> <จำนวน>  •  ดูทั้งหมด: /shop")
    return embed

class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Simple Weapon",  value="simple_weapon",  emoji="✂️",  description="ดาบ หอก ธนู ราคาเข้าถึงง่าย"),
            discord.SelectOption(label="Martial Weapon", value="martial_weapon", emoji="⚔️",  description="อาวุธหนักสำหรับนักรบมืออาชีพ"),
            discord.SelectOption(label="Armor",          value="armor",          emoji="🛡️",  description="เกราะทุกประเภท ตั้งแต่หนังจนถึง Plate"),
        ]
        super().__init__(placeholder="เลือกหมวดหมู่สินค้า...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        cat_key = self.values[0]
        items = {k: v for k, v in load_shop()["items"].items() if v["category"] == cat_key}
        embed = make_category_embed(cat_key, items)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ShopButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CategorySelect())

    @discord.ui.button(label="Check Coinpurse", style=discord.ButtonStyle.success, emoji="🪙", custom_id="shop:coinpurse")
    async def coinpurse(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = get_player(interaction.user.id)
        embed = discord.Embed(
            title=f"🪙 กระเป๋าเงินของ {interaction.user.display_name}",
            description=f"**{player['gold']} gp**",
            color=0xF1C40F
        )
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="List of Items", style=discord.ButtonStyle.primary, emoji="📋", custom_id="shop:inventory")
    async def inventory(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = get_player(interaction.user.id)
        inv = player.get("inventory", {})
        shop_data = load_shop()
        embed = discord.Embed(
            title=f"🎒 Inventory ของ {interaction.user.display_name}",
            color=0x3498DB
        )
        embed.add_field(name="💰 ทอง", value=f"**{player['gold']} gp**", inline=False)
        if not inv:
            embed.add_field(name="📦 สิ่งของ", value="*กระเป๋าว่างเปล่า...*", inline=False)
        else:
            lines = []
            for iid, qty in inv.items():
                it = shop_data["items"].get(iid)
                name = it["name"] if it else iid
                lines.append(f"**{name}** × {qty}")
            embed.add_field(name=f"📦 สิ่งของ ({len(inv)} ชนิด)", value="\n".join(lines), inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ─── /shop ────────────────────────────────────────────────────────────
@bot.tree.command(name="shop", description="🏪 เปิดร้านค้า The Iron Bastion", guild=discord.Object(id=GUILD_ID))
async def shop(interaction: discord.Interaction):
    embed = make_shop_embed()
    view = ShopButtons()
    await interaction.response.send_message(embed=embed, view=view)

# ─── /buy ─────────────────────────────────────────────────────────────
@bot.tree.command(name="buy", description="🛒 ซื้อสินค้า", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(item_id="ID สินค้า (เช่น longsword)", quantity="จำนวน")
async def buy(interaction: discord.Interaction, item_id: str, quantity: int = 1):
    if quantity <= 0:
        await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True); return
    shop_data = load_shop()
    item = shop_data["items"].get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบสินค้า `{item_id}`\nใช้ `/shop` เพื่อดู ID สินค้า", ephemeral=True); return
    if item["stock"] != -1 and item["stock"] < quantity:
        await interaction.response.send_message(f"❌ stock ไม่พอ! เหลือเพียง **{item['stock']} ชิ้น**", ephemeral=True); return
    total = item["price"] * quantity
    player = get_player(interaction.user.id)
    if player["gold"] < total:
        await interaction.response.send_message(
            f"❌ ทองไม่พอ!\nต้องการ **{total} gp** | มี **{player['gold']} gp**", ephemeral=True); return
    player["gold"] -= total
    player["inventory"][item_id] = player["inventory"].get(item_id, 0) + quantity
    save_player(interaction.user.id, player)
    if item["stock"] != -1:
        shop_data["items"][item_id]["stock"] -= quantity; save_shop(shop_data)
    embed = discord.Embed(title="✅ ซื้อสำเร็จ!", color=0x2ECC71)
    embed.add_field(name="🛍️ สินค้า",    value=f"**{item['name']}** × {quantity}", inline=True)
    embed.add_field(name="💸 จ่ายไป",    value=f"**{total} gp**",                   inline=True)
    embed.add_field(name="💰 คงเหลือ",   value=f"**{player['gold']} gp**",           inline=True)
    await interaction.response.send_message(embed=embed)

# ─── /sell ────────────────────────────────────────────────────────────
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
    earned = (item["price"] * quantity) // 2
    player["inventory"][item_id] -= quantity
    if player["inventory"][item_id] <= 0: del player["inventory"][item_id]
    player["gold"] += earned
    save_player(interaction.user.id, player)
    embed = discord.Embed(title="💱 ขายสำเร็จ!", color=0xE67E22)
    embed.add_field(name="🛍️ สินค้า", value=f"**{item['name']}** × {quantity}", inline=True)
    embed.add_field(name="💰 ได้รับ",  value=f"**{earned} gp**",                  inline=True)
    embed.add_field(name="💼 คงเหลือ", value=f"**{player['gold']} gp**",           inline=True)
    await interaction.response.send_message(embed=embed)

# ─── Admin Commands ───────────────────────────────────────────────────
@bot.tree.command(name="admin_gold", description="[DM] ปรับทองของผู้เล่น", guild=discord.Object(id=GUILD_ID))
@app_commands.describe(member="ผู้เล่น", action="add/remove/set", amount="จำนวนทอง")
@app_commands.choices(action=[
    app_commands.Choice(name="➕ เพิ่ม", value="add"),
    app_commands.Choice(name="➖ ลด",   value="remove"),
    app_commands.Choice(name="🔧 กำหนด", value="set"),
])
@is_admin()
async def admin_gold(interaction: discord.Interaction, member: discord.Member, action: str, amount: int):
    player = get_player(member.id); old = player["gold"]
    if action == "add":    player["gold"] = max(0, player["gold"] + amount); verb = f"+{amount} gp"; color = 0x2ECC71
    elif action == "remove": player["gold"] = max(0, player["gold"] - amount); verb = f"-{amount} gp"; color = 0xE74C3C
    else:                  player["gold"] = max(0, amount); verb = f"= {amount} gp"; color = 0x3498DB
    save_player(member.id, player)
    embed = discord.Embed(title="💰 ปรับทองสำเร็จ", color=color)
    embed.add_field(name="👤 ผู้เล่น",      value=member.mention,                 inline=True)
    embed.add_field(name="🔧 การเปลี่ยน",  value=verb,                            inline=True)
    embed.add_field(name="💼 ก่อน → หลัง", value=f"{old} → {player['gold']} gp", inline=True)
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
@app_commands.describe(item_id="ID (ไม่มีช่องว่าง)", name="ชื่อแสดง", desc="คำอธิบาย", price="ราคา gp", category="หมวดหมู่", stock="stock (-1=ไม่จำกัด)")
@app_commands.choices(category=[
    app_commands.Choice(name="✂️ Simple Weapon",  value="simple_weapon"),
    app_commands.Choice(name="⚔️ Martial Weapon", value="martial_weapon"),
    app_commands.Choice(name="🛡️ Armor",          value="armor"),
])
@is_admin()
async def admin_add_item(interaction: discord.Interaction, item_id: str, name: str, desc: str, price: int, category: str, stock: int = -1):
    if " " in item_id:
        await interaction.response.send_message("❌ item_id ต้องไม่มีช่องว่าง", ephemeral=True); return
    shop_data = load_shop()
    if item_id in shop_data["items"]:
        await interaction.response.send_message(f"❌ มี `{item_id}` อยู่แล้ว", ephemeral=True); return
    shop_data["items"][item_id] = {"name": name, "desc": desc, "price": price, "category": category, "stock": stock}
    save_shop(shop_data)
    await interaction.response.send_message(f"✅ เพิ่ม **{name}** (`{item_id}`) ราคา {price} gp แล้ว!")

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
