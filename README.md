# ⚔️ DnD 5.5e Shop Bot

Discord Bot สำหรับจัดการร้านค้าใน campaign DnD ของคุณ

---

## 📋 ฟีเจอร์

| คำสั่ง | คำอธิบาย | ใครใช้ได้ |
|--------|---------|-----------|
| `/shop` | ดูสินค้าทั้งหมด (กรองตาม category ได้) | ทุกคน |
| `/item <id>` | ดูรายละเอียดสินค้า | ทุกคน |
| `/buy <id> <จำนวน>` | ซื้อสินค้า | ทุกคน |
| `/sell <id> <จำนวน>` | ขายสินค้า (ได้ 50%) | ทุกคน |
| `/gold` | ดูทองของตัวเอง | ทุกคน |
| `/inventory` | ดู inventory | ทุกคน |
| `/profile [@user]` | ดูโปรไฟล์ | ทุกคน |
| `/admin_gold` | เพิ่ม/ลด/กำหนดทองผู้เล่น | DM/Admin |
| `/admin_give_item` | มอบไอเทมให้ผู้เล่น | DM/Admin |
| `/admin_take_item` | เอาไอเทมจากผู้เล่น | DM/Admin |
| `/admin_add_item` | เพิ่มสินค้าใหม่ในร้าน | DM/Admin |
| `/admin_stock` | ปรับ stock สินค้า | DM/Admin |
| `/admin_remove_item` | ลบสินค้าออกจากร้าน | DM/Admin |

---

## 🚀 วิธีติดตั้ง

### 1. สร้าง Discord Bot

1. ไปที่ [Discord Developer Portal](https://discord.com/developers/applications)
2. กด **New Application** → ตั้งชื่อ bot
3. ไปที่ **Bot** tab → กด **Add Bot**
4. เปิด **Privileged Gateway Intents**:
   - ✅ Server Members Intent
   - ✅ Message Content Intent
5. คัดลอก **Token** ไว้ใช้ในขั้นตอนถัดไป
6. ไปที่ **OAuth2 → URL Generator**:
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Embed Links`, `Use Slash Commands`
7. คัดลอก URL และเชิญ bot เข้า server

### 2. ติดตั้ง Dependencies

```bash
# ต้องการ Python 3.10+
pip install -r requirements.txt
```

### 3. ตั้งค่า Token

```bash
# คัดลอก .env.example เป็น .env
cp .env.example .env

# แก้ไข .env แล้วใส่ token ของคุณ
DISCORD_TOKEN=ใส่_token_ที่นี่
```

### 4. รัน Bot

```bash
python bot.py
```

---

## ⚙️ สิทธิ์ Admin

คำสั่ง `/admin_*` ต้องการ **อย่างใดอย่างหนึ่ง**:
- สิทธิ์ Administrator บน server
- Role ที่ชื่อว่า `DM`, `Admin`, หรือ `Game Master`

---

## 📁 โครงสร้างไฟล์

```
dnd_shop_bot/
├── bot.py              # ไฟล์หลัก
├── database.py         # จัดการ data (JSON)
├── requirements.txt
├── .env.example
├── cogs/
│   ├── shop.py         # คำสั่งร้านค้า
│   ├── player.py       # คำสั่งผู้เล่น
│   └── admin.py        # คำสั่ง DM/Admin
└── data/               # สร้างอัตโนมัติเมื่อรัน
    ├── shop.json       # ข้อมูลสินค้า
    └── players.json    # ข้อมูลผู้เล่น
```

---

## 🎒 สินค้าเริ่มต้น

มีสินค้า default มาให้ 14 รายการ แบ่งเป็น:
- 🧪 **Potions**: Health Potion, Greater Health Potion, Antitoxin
- ⚔️ **Weapons**: Shortsword, Longsword, Handaxe
- 🛡️ **Armor**: Leather Armor, Chain Mail, Shield
- 🎒 **Adventuring**: Torch, Hemp Rope, Rations
- ✨ **Magic**: Spellbook, Scroll of Identify

DM สามารถเพิ่ม/ลบ/แก้ไขสินค้าได้ตลอดเวลาผ่าน slash commands

---

## 💡 Tips

- ผู้เล่นใหม่จะได้รับ **100 gp** เริ่มต้น (ปรับได้ใน `database.py`)
- ข้อมูลทั้งหมดบันทึกใน `data/` เป็น JSON → backup ง่าย
- ต้องการ database จริง (PostgreSQL/SQLite) ติดต่อได้เลย!
