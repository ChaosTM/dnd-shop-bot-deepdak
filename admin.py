import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import database as db

# ─── Permission Check ─────────────────────────────────────────────────
def is_admin():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.guild_permissions.administrator or \
               any(r.name in ("DM", "Admin", "Game Master") for r in interaction.user.roles)
    return app_commands.check(predicate)


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── /admin_gold ────────────────────────────────────────────────────
    @app_commands.command(name="admin_gold", description="[DM] ปรับทองของผู้เล่น")
    @app_commands.describe(
        member="ผู้เล่นที่ต้องการปรับทอง",
        action="add=เพิ่ม | remove=ลด | set=กำหนดค่า",
        amount="จำนวนทอง"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="➕ เพิ่ม",    value="add"),
        app_commands.Choice(name="➖ ลด",       value="remove"),
        app_commands.Choice(name="🔧 กำหนดค่า", value="set"),
    ])
    @is_admin()
    async def admin_gold(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        action: str,
        amount: int
    ):
        if amount < 0:
            await interaction.response.send_message("❌ จำนวนต้องเป็นบวก", ephemeral=True)
            return

        player = db.get_player(member.id)
        old_gold = player["gold"]

        if action == "add":
            new_gold = db.add_gold(member.id, amount)
            verb = f"เพิ่ม +{amount} gp"
            color = 0x2ECC71
        elif action == "remove":
            new_gold = db.add_gold(member.id, -amount)
            verb = f"ลด -{amount} gp"
            color = 0xE74C3C
        else:  # set
            new_gold = db.set_gold(member.id, amount)
            verb = f"กำหนดเป็น {amount} gp"
            color = 0x3498DB

        embed = discord.Embed(title="💰 ปรับทองสำเร็จ", color=color)
        embed.add_field(name="👤 ผู้เล่น",  value=member.mention,  inline=True)
        embed.add_field(name="🔧 การเปลี่ยน", value=verb,           inline=True)
        embed.add_field(name="💼 ก่อน → หลัง", value=f"{old_gold} → {new_gold} gp", inline=True)
        embed.set_footer(text=f"ดำเนินการโดย {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    # ── /admin_give_item ───────────────────────────────────────────────
    @app_commands.command(name="admin_give_item", description="[DM] มอบไอเทมให้ผู้เล่น")
    @app_commands.describe(member="ผู้เล่น", item_id="ID ไอเทม", quantity="จำนวน")
    @is_admin()
    async def admin_give_item(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        item_id: str,
        quantity: int = 1
    ):
        shop_data = db.load_shop()
        item = shop_data["items"].get(item_id)
        if not item:
            await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True)
            return

        player = db.get_player(member.id)
        player["inventory"][item_id] = player["inventory"].get(item_id, 0) + quantity
        db.save_player(member.id, player)

        embed = discord.Embed(title="🎁 มอบไอเทมสำเร็จ", color=0x9B59B6)
        embed.add_field(name="👤 ผู้รับ",  value=member.mention,              inline=True)
        embed.add_field(name="📦 ไอเทม",  value=f"{item['name']} × {quantity}", inline=True)
        embed.set_footer(text=f"ดำเนินการโดย {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    # ── /admin_take_item ───────────────────────────────────────────────
    @app_commands.command(name="admin_take_item", description="[DM] เอาไอเทมจากผู้เล่น")
    @app_commands.describe(member="ผู้เล่น", item_id="ID ไอเทม", quantity="จำนวน")
    @is_admin()
    async def admin_take_item(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        item_id: str,
        quantity: int = 1
    ):
        player = db.get_player(member.id)
        have = player["inventory"].get(item_id, 0)
        if have < quantity:
            await interaction.response.send_message(
                f"❌ {member.display_name} มี `{item_id}` แค่ {have} ชิ้น",
                ephemeral=True
            )
            return

        player["inventory"][item_id] -= quantity
        if player["inventory"][item_id] <= 0:
            del player["inventory"][item_id]
        db.save_player(member.id, player)

        embed = discord.Embed(title="🗑️ เอาไอเทมออกแล้ว", color=0xE74C3C)
        embed.add_field(name="👤 จาก",   value=member.mention,    inline=True)
        embed.add_field(name="📦 ไอเทม", value=f"`{item_id}` × {quantity}", inline=True)
        embed.set_footer(text=f"ดำเนินการโดย {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

    # ── /admin_add_item ────────────────────────────────────────────────
    @app_commands.command(name="admin_add_item", description="[DM] เพิ่มสินค้าใหม่เข้าร้าน")
    @app_commands.describe(
        item_id="ID ไอเทม (ภาษาอังกฤษ ไม่มีช่องว่าง เช่น magic_sword)",
        name="ชื่อแสดง (เช่น ⚡ Magic Sword)",
        desc="คำอธิบาย",
        price="ราคา (gp)",
        category="หมวดหมู่",
        stock="จำนวน stock (-1 = ไม่จำกัด)"
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="🧪 Potion",         value="potion"),
        app_commands.Choice(name="⚔️ Weapon",          value="weapon"),
        app_commands.Choice(name="🛡️ Armor",           value="armor"),
        app_commands.Choice(name="🎒 Adventuring Gear",value="adventuring"),
        app_commands.Choice(name="✨ Magic",            value="magic"),
    ])
    @is_admin()
    async def admin_add_item(
        self,
        interaction: discord.Interaction,
        item_id: str,
        name: str,
        desc: str,
        price: int,
        category: str,
        stock: int = -1
    ):
        # Validate ID
        if " " in item_id:
            await interaction.response.send_message("❌ item_id ต้องไม่มีช่องว่าง", ephemeral=True)
            return

        shop_data = db.load_shop()
        if item_id in shop_data["items"]:
            await interaction.response.send_message(
                f"❌ มีสินค้า `{item_id}` อยู่แล้ว ใช้ /admin_edit_item เพื่อแก้ไข",
                ephemeral=True
            )
            return

        shop_data["items"][item_id] = {
            "name": name,
            "desc": desc,
            "price": price,
            "category": category,
            "stock": stock
        }
        db.save_shop(shop_data)

        stock_txt = "∞ ไม่จำกัด" if stock == -1 else str(stock)
        embed = discord.Embed(title="✅ เพิ่มสินค้าสำเร็จ!", color=0x2ECC71)
        embed.add_field(name="🆔 ID",      value=f"`{item_id}`", inline=True)
        embed.add_field(name="📛 ชื่อ",    value=name,           inline=True)
        embed.add_field(name="💰 ราคา",    value=f"{price} gp",  inline=True)
        embed.add_field(name="📋 คำอธิบาย",value=desc,           inline=False)
        embed.add_field(name="📦 Stock",   value=stock_txt,       inline=True)
        await interaction.response.send_message(embed=embed)

    # ── /admin_stock ───────────────────────────────────────────────────
    @app_commands.command(name="admin_stock", description="[DM] ปรับ stock สินค้า")
    @app_commands.describe(item_id="ID สินค้า", amount="จำนวน (-1 = ไม่จำกัด)")
    @is_admin()
    async def admin_stock(
        self,
        interaction: discord.Interaction,
        item_id: str,
        amount: int
    ):
        shop_data = db.load_shop()
        if item_id not in shop_data["items"]:
            await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True)
            return

        shop_data["items"][item_id]["stock"] = amount
        db.save_shop(shop_data)

        stock_txt = "∞ ไม่จำกัด" if amount == -1 else str(amount)
        await interaction.response.send_message(
            f"✅ ปรับ stock `{item_id}` เป็น **{stock_txt}** แล้ว"
        )

    # ── /admin_remove_item ─────────────────────────────────────────────
    @app_commands.command(name="admin_remove_item", description="[DM] ลบสินค้าออกจากร้าน")
    @app_commands.describe(item_id="ID สินค้าที่ต้องการลบ")
    @is_admin()
    async def admin_remove_item(self, interaction: discord.Interaction, item_id: str):
        shop_data = db.load_shop()
        if item_id not in shop_data["items"]:
            await interaction.response.send_message(f"❌ ไม่พบ `{item_id}`", ephemeral=True)
            return

        item_name = shop_data["items"][item_id]["name"]
        del shop_data["items"][item_id]
        db.save_shop(shop_data)

        await interaction.response.send_message(
            f"🗑️ ลบ **{item_name}** (`{item_id}`) ออกจากร้านแล้ว"
        )

    # ── Error Handler ──────────────────────────────────────────────────
    async def cog_app_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้! ต้องมีสิทธิ์ Administrator หรือ role: DM / Admin / Game Master",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot):
    await bot.add_cog(AdminCog(bot))
