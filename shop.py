import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db

CATEGORIES = {
    "potion":      ("🧪", "Potions & Consumables"),
    "weapon":      ("⚔️",  "Weapons"),
    "armor":       ("🛡️",  "Armor & Shields"),
    "adventuring": ("🎒", "Adventuring Gear"),
    "magic":       ("✨",  "Magic Items"),
}

CATEGORY_COLORS = {
    "potion":      0xE74C3C,
    "weapon":      0xE67E22,
    "armor":       0x3498DB,
    "adventuring": 0x2ECC71,
    "magic":       0x9B59B6,
}

class ShopCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /shop ──────────────────────────────────────────────────────────
    @app_commands.command(name="shop", description="🏪 ดูรายการสินค้าในร้านทั้งหมด")
    @app_commands.describe(category="กรองตามหมวดหมู่ (ไม่ระบุ = แสดงทั้งหมด)")
    @app_commands.choices(category=[
        app_commands.Choice(name="🧪 Potions",        value="potion"),
        app_commands.Choice(name="⚔️ Weapons",         value="weapon"),
        app_commands.Choice(name="🛡️ Armor",           value="armor"),
        app_commands.Choice(name="🎒 Adventuring Gear",value="adventuring"),
        app_commands.Choice(name="✨ Magic Items",      value="magic"),
    ])
    async def shop(self, interaction: discord.Interaction, category: Optional[str] = None):
        shop_data = db.load_shop()
        items = shop_data["items"]

        if category:
            filtered = {k: v for k, v in items.items() if v["category"] == category}
            cat_emoji, cat_name = CATEGORIES.get(category, ("🏪", category))
            color = CATEGORY_COLORS.get(category, 0xF1C40F)
            embed = discord.Embed(
                title=f"{cat_emoji} ร้านค้า — {cat_name}",
                color=color,
                description="ใช้ `/buy <ชื่อสินค้า> <จำนวน>` เพื่อซื้อ\n"
                            "ใช้ `/item <ชื่อสินค้า>` เพื่อดูรายละเอียด"
            )
            self._add_item_fields(embed, filtered)
        else:
            embed = discord.Embed(
                title="🏪 ร้านค้า DnD",
                color=0xF1C40F,
                description="ยินดีต้อนรับ นักผจญภัย! 🗺️\n"
                            "ใช้ `/buy <id> <จำนวน>` เพื่อซื้อ | `/item <id>` ดูรายละเอียด"
            )
            for cat_key, (cat_emoji, cat_name) in CATEGORIES.items():
                cat_items = {k: v for k, v in items.items() if v["category"] == cat_key}
                if not cat_items:
                    continue
                lines = []
                for item_id, item in cat_items.items():
                    stock_txt = "∞" if item["stock"] == -1 else str(item["stock"])
                    lines.append(f"`{item_id}` {item['name']} — **{item['price']}gp** (stock: {stock_txt})")
                embed.add_field(
                    name=f"{cat_emoji} {cat_name}",
                    value="\n".join(lines),
                    inline=False
                )

        embed.set_footer(text="💰 ดูทองของคุณ: /gold | 🎒 ดู inventory: /inventory")
        await interaction.response.send_message(embed=embed)

    def _add_item_fields(self, embed, items):
        for item_id, item in items.items():
            stock_txt = "∞ ไม่จำกัด" if item["stock"] == -1 else f"{item['stock']} ชิ้น"
            embed.add_field(
                name=f"{item['name']} — {item['price']} gp",
                value=f"📋 {item['desc']}\n🆔 ID: `{item_id}` | 📦 คงเหลือ: {stock_txt}",
                inline=False
            )

    # ── /item ──────────────────────────────────────────────────────────
    @app_commands.command(name="item", description="🔍 ดูรายละเอียดสินค้าเพิ่มเติม")
    @app_commands.describe(item_id="ID ของสินค้า (เช่น health_potion)")
    async def item_info(self, interaction: discord.Interaction, item_id: str):
        shop_data = db.load_shop()
        item = shop_data["items"].get(item_id)

        if not item:
            await interaction.response.send_message(
                f"❌ ไม่พบสินค้า `{item_id}` ลองใช้ `/shop` เพื่อดู ID สินค้าทั้งหมด",
                ephemeral=True
            )
            return

        cat_key = item["category"]
        cat_emoji, cat_name = CATEGORIES.get(cat_key, ("🏪", cat_key))
        color = CATEGORY_COLORS.get(cat_key, 0xF1C40F)
        stock_txt = "∞ ไม่จำกัด" if item["stock"] == -1 else f"{item['stock']} ชิ้น"

        embed = discord.Embed(title=item["name"], color=color)
        embed.add_field(name="📋 คำอธิบาย", value=item["desc"], inline=False)
        embed.add_field(name="💰 ราคา",     value=f"**{item['price']} gp**", inline=True)
        embed.add_field(name="🏷️ หมวดหมู่", value=f"{cat_emoji} {cat_name}",  inline=True)
        embed.add_field(name="📦 คงเหลือ",  value=stock_txt,                  inline=True)
        embed.set_footer(text=f"ซื้อ: /buy {item_id} 1")
        await interaction.response.send_message(embed=embed)

    # ── /buy ───────────────────────────────────────────────────────────
    @app_commands.command(name="buy", description="🛒 ซื้อสินค้าจากร้าน")
    @app_commands.describe(item_id="ID สินค้า", quantity="จำนวนที่ต้องการซื้อ")
    async def buy(self, interaction: discord.Interaction, item_id: str, quantity: int = 1):
        if quantity <= 0:
            await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True)
            return

        shop_data = db.load_shop()
        item = shop_data["items"].get(item_id)
        if not item:
            await interaction.response.send_message(
                f"❌ ไม่พบสินค้า `{item_id}`\nใช้ `/shop` เพื่อดูรายการสินค้า",
                ephemeral=True
            )
            return

        # เช็ค stock
        if item["stock"] != -1 and item["stock"] < quantity:
            await interaction.response.send_message(
                f"❌ สินค้าไม่พอ! {item['name']} คงเหลือ **{item['stock']} ชิ้น** เท่านั้น",
                ephemeral=True
            )
            return

        total_cost = item["price"] * quantity
        player = db.get_player(interaction.user.id)

        if player["gold"] < total_cost:
            await interaction.response.send_message(
                f"❌ ทองไม่พอ!\n"
                f"ราคา: **{total_cost} gp** | ทองของคุณ: **{player['gold']} gp**",
                ephemeral=True
            )
            return

        # ทำการซื้อ
        player["gold"] -= total_cost
        inv = player["inventory"]
        inv[item_id] = inv.get(item_id, 0) + quantity
        db.save_player(interaction.user.id, player)

        # ลด stock ถ้าจำกัด
        if item["stock"] != -1:
            shop_data["items"][item_id]["stock"] -= quantity
            db.save_shop(shop_data)

        embed = discord.Embed(
            title="✅ ซื้อสำเร็จ!",
            color=0x2ECC71
        )
        embed.add_field(name="🛍️ สินค้า",    value=f"{item['name']} x{quantity}", inline=True)
        embed.add_field(name="💸 ค่าใช้จ่าย", value=f"{total_cost} gp",            inline=True)
        embed.add_field(name="💰 ทองคงเหลือ", value=f"{player['gold']} gp",         inline=True)
        embed.set_footer(text="ดู inventory: /inventory")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(ShopCog(bot))
