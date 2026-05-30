import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# ─── ตั้งค่า Bot ───────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ─── โหลด Cogs ─────────────────────────────────────────────────
async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"✅ โหลด Cog: {filename}")

@bot.event
async def on_ready():
    await load_extensions()
    try:
        synced = await bot.tree.sync()
        print(f"🌿 Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"❌ Sync error: {e}")
    print(f"⚔️  {bot.user} พร้อมใช้งานแล้ว!")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🏪 ร้านค้า DnD | /shop"
        )
    )

# ─── รัน Bot ───────────────────────────────────────────────────
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ไม่พบ DISCORD_TOKEN ใน environment variable!")
        print("   ใส่ token ใน .env หรือ set ตัวแปร DISCORD_TOKEN ก่อนรัน")
    else:
        bot.run(TOKEN)
