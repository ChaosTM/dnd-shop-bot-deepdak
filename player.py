import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db

class PlayerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /gold ──────────────────────────────────────────────────────────
    @app_commands.command(name="gold", description="💰 ดูจำนวนทองของคุณ")
    async def gold(self, interaction: discord.Interaction):
        player = db.get_player(interaction.user.id)
        embed = discord.Embed(
            title=f"💰 กระเป๋าเงินของ {interaction.user.display_name}",
            color=0xF1C40F
        )
        embed.add_field(name="ทองคงเหลือ", value=f"**{player['gold']} gp**", inline=False)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    # ── /inventory ─────────────────────────────────────────────────────
    @app_commands.command(name="inventory", description="🎒 ดู Inventory ของคุณ")
    async def inventory(self, interaction: discord.Interaction):
        player = db.get_player(interaction.user.id)
        inv = player.get("inventory", {})
        shop_data = db.load_shop()

        embed = discord.Embed(
            title=f"🎒 Inventory ของ {interaction.user.display_name}",
            color=0x3498DB
        )
        embed.add_field(name="💰 ทอง", value=f"**{player['gold']} gp**", inline=False)

        if not inv:
            embed.add_field(name="📦 สิ่งของ", value="*กระเป๋าว่างเปล่า...*", inline=False)
        else:
            lines = []
            total_value = 0
            for item_id, qty in inv.items():
                item = shop_data["items"].get(item_id)
                if item:
                    value = item["price"] * qty
                    total_value += value
                    lines.append(f"{item['name']} × **{qty}** — {value} gp")
                else:
                    lines.append(f"`{item_id}` × **{qty}** — (ไม่ทราบราคา)")
            
            embed.add_field(
                name=f"📦 สิ่งของ ({len(inv)} ชนิด)",
                value="\n".join(lines),
                inline=False
            )
            embed.add_field(
                name="💎 มูลค่ารวม",
                value=f"{total_value} gp",
                inline=False
            )

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="ขายสินค้า: /sell <id> <จำนวน>")
        await interaction.response.send_message(embed=embed)

    # ── /sell ──────────────────────────────────────────────────────────
    @app_commands.command(name="sell", description="💱 ขายสินค้าจาก inventory (ได้ 50% ราคา)")
    @app_commands.describe(item_id="ID สินค้าที่ต้องการขาย", quantity="จำนวนที่ขาย")
    async def sell(self, interaction: discord.Interaction, item_id: str, quantity: int = 1):
        if quantity <= 0:
            await interaction.response.send_message("❌ จำนวนต้องมากกว่า 0", ephemeral=True)
            return

        player = db.get_player(interaction.user.id)
        inv = player.get("inventory", {})

        if item_id not in inv or inv[item_id] < quantity:
            have = inv.get(item_id, 0)
            await interaction.response.send_message(
                f"❌ คุณมี `{item_id}` เพียง **{have} ชิ้น** เท่านั้น",
                ephemeral=True
            )
            return

        shop_data = db.load_shop()
        item = shop_data["items"].get(item_id)
        if not item:
            await interaction.response.send_message(
                f"❌ ไม่พบข้อมูลสินค้า `{item_id}`",
                ephemeral=True
            )
            return

        sell_price = (item["price"] * quantity) // 2  # 50% ราคา
        player["inventory"][item_id] -= quantity
        if player["inventory"][item_id] <= 0:
            del player["inventory"][item_id]
        player["gold"] += sell_price
        db.save_player(interaction.user.id, player)

        embed = discord.Embed(title="💱 ขายสำเร็จ!", color=0xE67E22)
        embed.add_field(name="🛍️ สินค้า",    value=f"{item['name']} × {quantity}", inline=True)
        embed.add_field(name="💰 ได้รับ",     value=f"**{sell_price} gp**",         inline=True)
        embed.add_field(name="💼 ทองคงเหลือ", value=f"{player['gold']} gp",          inline=True)
        embed.set_footer(text="ขายได้ 50% ของราคาซื้อ")
        await interaction.response.send_message(embed=embed)

    # ── /profile ───────────────────────────────────────────────────────
    @app_commands.command(name="profile", description="👤 ดูโปรไฟล์และสถิตินักผจญภัย")
    @app_commands.describe(member="ดูโปรไฟล์ของสมาชิกคนอื่น (ไม่ระบุ = ของตัวเอง)")
    async def profile(self, interaction: discord.Interaction, member: Optional[discord.Member] = None):
        target = member or interaction.user
        player = db.get_player(target.id)
        inv = player.get("inventory", {})

        total_items = sum(inv.values())
        shop_data = db.load_shop()
        total_value = sum(
            shop_data["items"].get(iid, {}).get("price", 0) * qty
            for iid, qty in inv.items()
        )

        embed = discord.Embed(
            title=f"⚔️ โปรไฟล์ของ {target.display_name}",
            color=0x9B59B6
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="💰 ทองคงเหลือ",   value=f"{player['gold']} gp",     inline=True)
        embed.add_field(name="🎒 จำนวนไอเทม",   value=f"{total_items} ชิ้น",      inline=True)
        embed.add_field(name="💎 มูลค่า Inventory", value=f"{total_value} gp",    inline=True)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(PlayerCog(bot))
