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
    "health_potion":         {"name": "🧪 Health Potion",          "desc": "คืน HP 2d4+2",                         "price": 50,  "category": "potion",      "stock": -1},
    "greater_health_potion": {"name": "🫙 Greater Health Potion",   "desc": "คืน HP 4d4+4",                         "price": 150, "category": "potion",      "stock": -1},
    "antitoxin":             {"name": "💊 Antitoxin",               "desc": "+Advantage ต้าน Poison saves 1 ชม.",    "price": 50,  "category": "potion",      "stock": -1},
    "torch":                 {"name": "🔦 Torch",                   "desc": "แสงสว่าง 20ft นาน 1 ชม.",              "price": 1,   "category": "adventuring", "stock": -1},
    "rope_50ft":             {"name": "🪢 Hemp Rope (50ft)",         "desc": "เชือกกัญชา 50 ฟุต",                   "price": 1,   "category": "adventuring", "stock": -1},
    "rations":               {"name": "🍖 Rations (1 day)",          "desc": "อาหารสำหรับ 1 วัน",                   "price": 5,   "category": "adventuring", "stock": -1},
    "shortsword":            {"name": "⚔️ Shortsword",              "desc": "1d6 Piercing | Finesse, Light",         "price": 10,  "category": "weapon",      "stock": 5},
    "longsword":             {"name": "🗡️ Longsword",               "desc": "1d8 Slashing | Versatile",              "price": 15,  "category": "weapon",      "stock": 3},
    "handaxe":               {"name": "🪓 Handaxe",                 "desc": "1d6 Slashing | Light, Thrown (20/60)", "price": 5,   "category": "weapon",      "stock": -1},
    "leather_armor":         {"name": "🛡️ Leather Armor",           "desc": "AC 11 + DEX | Light Armor",            "price": 10,  "category": "armor",       "stock": 3},
    "chain_mail":            {"name": "⛓️ Chain Mail",              "desc": "AC 16 | Heavy | STR 13 required",      "price": 75,  "category": "armor",       "stock": 2},
    "shield":                {"name": "🔰 Shield",                  "desc": "+2 AC",                                 "price": 10,  "category": "armor",       "stock": 5},
    "spellbook":             {"name": "📖 Spellbook (Blank)",        "desc": "สมุดเวทย์เปล่า 100 หน้า",              "price": 50,  "category": "magic",       "stock": 2},
    "scroll_identify":       {"name": "📜 Scroll of Identify",       "desc": "ระบุ properties ของ magic item",       "price": 100, "category": "magic",       "stock": 3},
}}

CATEGORIES = {
    "potion":      ("🧪", "Potions"),
    "weapon":      ("⚔️",  "Weapons"),
    "armor":       ("🛡️",  "Armor & Shields"),
    "adventuring": ("🎒", "Adventuring Gear"),
    "magic":       ("✨",  "Magic Items"),
}
CAT_COLORS = {"potion": 0xE74C3C, "weapon": 0xE67E22, "armor": 0x3498DB, "adventuring": 0x2ECC71, "magic": 0x9B59B6}

def load_shop():
    if not SHOP_FILE.exists():
        save_shop(DEFAULT_SHOP); return DEFAULT_SHOP.copy()
    with open(SHOP_FILE, encoding="utf-8") as f: return json.load(f)
def save_shop(d):
    with open(SHOP_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)
def load_players():
    if not PLAYERS_FILE.exists(): save_players({}); return {}
    with open(PLAYERS_FILE, encoding="utf-8") as f: return json.load(f)
def save_players(d):
    with open(PLAYERS_FILE, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=2)
def get_player(uid):
    players = load_players(); key = str(uid)
    if key not in players:
        players[key] = {"gold": 100, "inventory": {}}; save_players(players)
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
        synced = await bot.tree.sync(guild=discord.Object(id=1460585900504387657)))
        print(f"🌿 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print(f"⚔️  {bot.user} พร้อมใช้งานแล้ว!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="🏪 ร้านค้า DnD | /shop"))

# ─── /shop ────────────────────────────────────────────────────────────
@bot.tree.command(name="shop", description="🏪 ดูรายการสินค้าในร้านทั้งหมด")
@app_commands.describe(category="กรองตามหมวดหมู่")
@app_commands.choices(category=[
    app_commands.Choice(name="🧪 Potions", value="potion"),
    app_commands.Choice(name="⚔️ Weapons", value="weapon"),
    app_commands.Choice(name="🛡️ Armor",   value="armor"),
    app_commands.Choice(name="🎒 Gear",    value="adventuring"),
    app_commands.Choice(name="✨ Magic",   value="magic"),
])
async def shop(interaction: discord.Interaction, category: Optional[str] = None):
    items = load_shop()["items"]
    embed = discord.Embed(title="🏪 ร้านค้า DnD", color=0xF1C40F,
        description="ใช้ `/buy <id> <จำนวน>` เพื่อซื้อ | `/item <id>` ดูรายละเอียด")
    filtered = {k: v for k, v in items.items() if not category or v["category"] == category}
    if category:
        e, n = CATEGORIES.get(category, ("🏪", category))
        embed.title = f"{e} ร้านค้า — {n}"
        embed.color = CAT_COLORS.get(category, 0xF1C40F)
    for cat_key, (ce, cn) in CATEGORIES.items():
        cat_items = {k: v for k, v in filtered.items() if v["category"] == cat_key}
        if not cat_items: continue
        lines = [f"`{iid}` {i['name']} — **{i['price']}gp** (stock: {'∞' if i['stock']==-1 else i['stock']})" for iid, i in cat_items.items()]
        embed.add_field(name=f"{ce} {cn}", value="\n".join(lines), inline=False)
    embed.set_footer(text="💰 /gold | 🎒 /inventory")
    await interaction.response.send_message(embed=embed)

# ─── /item ────────────────────────────────────────────────────────────
@bot.tree.command(name="item", description="🔍 ดูรายละเอียดสินค้า")
@app_commands.describe(item_id="ID ของสินค้า")
async def item_info(interaction: discord.Interaction, item_id: str):
    item = load_shop()["items"].get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบ `{item_id}` — ใช้ `/shop` ดู ID ทั้งหมด", ephemeral=True); return
    ce, cn = CATEGORIES.get(item["category"], ("🏪", item["category"]))
    embed = discord.Embed(title=item["name"], color=CAT_COLORS.get(item["category"], 0xF1C40F))
    embed.add_field(name="📋 คำอธิบาย", value=item["desc"], inline=False)
    embed.add_field(name="💰 ราคา",     value=f"**{item['price']} gp**", inline=True)
    embed.add_field(name="🏷️ หมวด",    value=f"{ce} {cn}",              inline=True)
    embed.add_field(name="📦 คงเหลือ",  value="∞" if item["stock"]==-1 else str(item["stock"]), inline=True)
    embed.set_footer(text=f"ซื้อ: /buy {item_id} 1")
    await interaction.response.send_message(embed=embed)

# ─── /buy ─────────────────────────────────────────────────────────────
@bot.tree.command(name="buy", description="🛒 ซื้อสินค้าจากร้าน")
@app_commands.describe(item_id="ID สินค้า", quantity="จำนวน")
async def buy(interaction: discord.Interaction, item_id: str, quantity: int = 1):
    if quantity <= 0:
        await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True); return
    shop_data = load_shop(); item = shop_data["items"].get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True); return
    if item["stock"] != -1 and item["stock"] < quantity:
        await interaction.response.send_message(f"❌ stock ไม่พอ! เหลือ {item['stock']} ชิ้น", ephemeral=True); return
    total = item["price"] * quantity
    player = get_player(interaction.user.id)
    if player["gold"] < total:
        await interaction.response.send_message(f"❌ ทองไม่พอ! ต้องการ {total} gp มี {player['gold']} gp", ephemeral=True); return
    player["gold"] -= total
    player["inventory"][item_id] = player["inventory"].get(item_id, 0) + quantity
    save_player(interaction.user.id, player)
    if item["stock"] != -1:
        shop_data["items"][item_id]["stock"] -= quantity; save_shop(shop_data)
    embed = discord.Embed(title="✅ ซื้อสำเร็จ!", color=0x2ECC71)
    embed.add_field(name="🛍️ สินค้า",    value=f"{item['name']} ×{quantity}", inline=True)
    embed.add_field(name="💸 จ่ายไป",    value=f"{total} gp",                  inline=True)
    embed.add_field(name="💰 คงเหลือ",   value=f"{player['gold']} gp",          inline=True)
    await interaction.response.send_message(embed=embed)

# ─── /sell ────────────────────────────────────────────────────────────
@bot.tree.command(name="sell", description="💱 ขายสินค้า (ได้ 50%)")
@app_commands.describe(item_id="ID สินค้า", quantity="จำนวน")
async def sell(interaction: discord.Interaction, item_id: str, quantity: int = 1):
    if quantity <= 0:
        await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True); return
    player = get_player(interaction.user.id)
    have = player["inventory"].get(item_id, 0)
    if have < quantity:
        await interaction.response.send_message(f"❌ มี `{item_id}` แค่ {have} ชิ้น", ephemeral=True); return
    item = load_shop()["items"].get(item_id)
    if not item:
        await interaction.response.send_message(f"❌ ไม่พบข้อมูลสินค้า `{item_id}`", ephemeral=True); return
    earned = (item["price"] * quantity) // 2
    player["inventory"][item_id] -= quantity
    if player["inventory"][item_id] <= 0: del player["inventory"][item_id]
    player["gold"] += earned; save_player(interaction.user.id, player)
    embed = discord.Embed(title="💱 ขายสำเร็จ!", color=0xE67E22)
    embed.add_field(name="🛍️ สินค้า",   value=f"{item['name']} ×{quantity}", inline=True)
    embed.add_field(name="💰 ได้รับ",    value=f"{earned} gp",                 inline=True)
    embed.add_field(name="💼 คงเหลือ",  value=f"{player['gold']} gp",           inline=True)
    await interaction.response.send_message(embed=embed)

# ─── /gold ────────────────────────────────────────────────────────────
@bot.tree.command(name="gold", description="💰 ดูจำนวนทองของคุณ")
async def gold(interaction: discord.Interaction):
    player = get_player(interaction.user.id)
    embed = discord.Embed(title=f"💰 กระเป๋าเงินของ {interaction.user.display_name}", color=0xF1C40F)
    embed.add_field(name="ทองคงเหลือ", value=f"**{player['gold']} gp**")
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# ─── /inventory ───────────────────────────────────────────────────────
@bot.tree.command(name="inventory", description="🎒 ดู Inventory ของคุณ")
async def inventory(interaction: discord.Interaction):
    player = get_player(interaction.user.id); inv = player.get("inventory", {})
    shop_data = load_shop()
    embed = discord.Embed(title=f"🎒 Inventory ของ {interaction.user.display_name}", color=0x3498DB)
    embed.add_field(name="💰 ทอง", value=f"**{player['gold']} gp**", inline=False)
    if not inv:
        embed.add_field(name="📦 สิ่งของ", value="*กระเป๋าว่างเปล่า...*", inline=False)
    else:
        lines = []
        for iid, qty in inv.items():
            it = shop_data["items"].get(iid)
            lines.append(f"{it['name'] if it else iid} × **{qty}**" + (f" — {it['price']*qty} gp" if it else ""))
        embed.add_field(name=f"📦 สิ่งของ ({len(inv)} ชนิด)", value="\n".join(lines), inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="ขาย: /sell <id> <จำนวน>")
    await interaction.response.send_message(embed=embed)

# ─── /profile ─────────────────────────────────────────────────────────
@bot.tree.command(name="profile", description="👤 ดูโปรไฟล์นักผจญภัย")
@app_commands.describe(member="ดูโปรไฟล์ของคนอื่น")
async def profile(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    target = member or interaction.user
    player = get_player(target.id); inv = player.get("inventory", {})
    shop_items = load_shop()["items"]
    total_items = sum(inv.values())
    total_value = sum(shop_items.get(iid, {}).get("price", 0) * qty for iid, qty in inv.items())
    embed = discord.Embed(title=f"⚔️ โปรไฟล์ของ {target.display_name}", color=0x9B59B6)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="💰 ทอง",           value=f"{player['gold']} gp",  inline=True)
    embed.add_field(name="🎒 ไอเทม",         value=f"{total_items} ชิ้น",   inline=True)
    embed.add_field(name="💎 มูลค่า Inventory", value=f"{total_value} gp",  inline=True)
    await interaction.response.send_message(embed=embed)

# ─── Admin Commands ───────────────────────────────────────────────────
@bot.tree.command(name="admin_gold", description="[DM] ปรับทองของผู้เล่น")
@app_commands.describe(member="ผู้เล่น", action="add/remove/set", amount="จำนวนทอง")
@app_commands.choices(action=[
    app_commands.Choice(name="➕ เพิ่ม", value="add"),
    app_commands.Choice(name="➖ ลด",   value="remove"),
    app_commands.Choice(name="🔧 กำหนด", value="set"),
])
@is_admin()
async def admin_gold(interaction: discord.Interaction, member: discord.Member, action: str, amount: int):
    player = get_player(member.id); old = player["gold"]
    if action == "add":   player["gold"] = max(0, player["gold"] + amount); verb = f"+{amount} gp"; color = 0x2ECC71
    elif action == "remove": player["gold"] = max(0, player["gold"] - amount); verb = f"-{amount} gp"; color = 0xE74C3C
    else:                 player["gold"] = max(0, amount); verb = f"= {amount} gp"; color = 0x3498DB
    save_player(member.id, player)
    embed = discord.Embed(title="💰 ปรับทองสำเร็จ", color=color)
    embed.add_field(name="👤 ผู้เล่น",     value=member.mention,            inline=True)
    embed.add_field(name="🔧 การเปลี่ยน", value=verb,                       inline=True)
    embed.add_field(name="💼 ก่อน → หลัง", value=f"{old} → {player['gold']} gp", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_give_item", description="[DM] มอบไอเทมให้ผู้เล่น")
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
    embed.add_field(name="👤 ผู้รับ", value=member.mention,                   inline=True)
    embed.add_field(name="📦 ไอเทม", value=f"{item['name']} ×{quantity}",     inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="admin_take_item", description="[DM] เอาไอเทมจากผู้เล่น")
@app_commands.describe(member="ผู้เล่น", item_id="ID ไอเทม", quantity="จำนวน")
@is_admin()
async def admin_take_item(interaction: discord.Interaction, member: discord.Member, item_id: str, quantity: int = 1):
    player = get_player(member.id); have = player["inventory"].get(item_id, 0)
    if have < quantity:
        await interaction.response.send_message(f"❌ {member.display_name} มี `{item_id}` แค่ {have} ชิ้น", ephemeral=True); return
    player["inventory"][item_id] -= quantity
    if player["inventory"][item_id] <= 0: del player["inventory"][item_id]
    save_player(member.id, player)
    await interaction.response.send_message(f"🗑️ เอา `{item_id}` ×{quantity} จาก {member.mention} ออกแล้ว")

@bot.tree.command(name="admin_add_item", description="[DM] เพิ่มสินค้าใหม่")
@app_commands.describe(item_id="ID (ไม่มีช่องว่าง)", name="ชื่อแสดง", desc="คำอธิบาย", price="ราคา gp", category="หมวดหมู่", stock="stock (-1=ไม่จำกัด)")
@app_commands.choices(category=[
    app_commands.Choice(name="🧪 Potion", value="potion"), app_commands.Choice(name="⚔️ Weapon", value="weapon"),
    app_commands.Choice(name="🛡️ Armor",  value="armor"),  app_commands.Choice(name="🎒 Gear",   value="adventuring"),
    app_commands.Choice(name="✨ Magic",  value="magic"),
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

@bot.tree.command(name="admin_stock", description="[DM] ปรับ stock สินค้า")
@app_commands.describe(item_id="ID สินค้า", amount="จำนวน (-1=ไม่จำกัด)")
@is_admin()
async def admin_stock(interaction: discord.Interaction, item_id: str, amount: int):
    shop_data = load_shop()
    if item_id not in shop_data["items"]:
        await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True); return
    shop_data["items"][item_id]["stock"] = amount; save_shop(shop_data)
    await interaction.response.send_message(f"✅ ปรับ stock `{item_id}` เป็น **{'∞' if amount==-1 else amount}** แล้ว")

@bot.tree.command(name="admin_remove_item", description="[DM] ลบสินค้าออกจากร้าน")
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
