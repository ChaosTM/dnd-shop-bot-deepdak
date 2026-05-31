# ⚔️ DnD 5e Shop Bot — Merchant Boy

> Discord Bot สำหรับจัดการตลาดค้าขายใน Campaign DnD 5e (2024 PHB)  
> มีร้านค้า 3 ร้าน • สินค้า 131 รายการ • ระบบสุ่ม Magic Items ตาม Quest Rank

---

## 🏪 ร้านค้าทั้งหมด

| ร้าน | NPC | สินค้า |
|------|-----|--------|
| ⚒️ **The Iron Bastion** | Duren Ironforge | Simple/Martial Weapons + Ammo (40 รายการ) |
| 🧪 **The Mystic Vial** | Seraphine Duskwhisper | Potions + Alchemical Gear + Focuses + Scrolls (23 รายการ) |
| 🎒 **The Wanderer's Pack** | Mira Copperkettle | Gear + Food + Tools + Clothing (68 รายการ) |

---

## 📋 คำสั่งทั้งหมด

### 👥 ผู้เล่นทั่วไป

| คำสั่ง | คำอธิบาย |
|--------|---------|
| `/market` | เปิดตลาด เลือกร้านจาก dropdown |
| `/buy <id> [จำนวน]` | ซื้อสินค้า (ดู ID จากร้าน) |
| `/sell <id> [จำนวน]` | ขายสินค้า (ได้คืน 50%) |

> 💡 ใช้ปุ่ม **Check Coinpurse** และ **List of Items** ใน embed ได้เลยโดยไม่ต้องพิมพ์คำสั่ง

---

### 🎲 ระบบ Quest Reward (DM เท่านั้น)

| คำสั่ง | คำอธิบาย |
|--------|---------|
| `/roll_reward <rank> [quest_name] [count]` | สุ่ม Magic Items ตาม Quest Rank |

**Quest Rank และโอกาสได้รับ:**

| Rank | Common | Uncommon | Rare | Very Rare | Legendary |
|------|--------|----------|------|-----------|-----------|
| ⚪ F | 90% | 10% | — | — | — |
| 🟢 E | 65% | 30% | 5% | — | — |
| 🔵 D | 30% | 55% | 15% | — | — |
| 🟣 C | 10% | 45% | 40% | 5% | — |
| 🔴 B | 5% | 20% | 50% | 25% | — |
| 🟠 A | — | 10% | 35% | 45% | 10% |
| 🟡 S | — | 5% | 20% | 45% | 30% |

> ผู้เล่นเลือกซื้อจาก dropdown ที่ปรากฏหลังสุ่มได้ทันที

---

### 🛡️ Admin Commands (DM / Admin / Game Master เท่านั้น)

| คำสั่ง | คำอธิบาย |
|--------|---------|
| `/setup_market <forum_channel>` | ติดตั้งร้านค้าลง Forum Channel (ทำครั้งเดียว) |
| `/admin_gold <member> <add/remove/set> <amount>` | ปรับทองผู้เล่น |
| `/admin_give_item <member> <id> [จำนวน]` | มอบไอเทมให้ผู้เล่น |
| `/admin_take_item <member> <id> [จำนวน]` | เอาไอเทมจากผู้เล่น |
| `/admin_add_item <id> <name> <desc> <price> <category> [stock]` | เพิ่มสินค้าใหม่ |
| `/admin_stock <id> <amount>` | ปรับ stock (-1 = ไม่จำกัด) |
| `/admin_remove_item <id>` | ลบสินค้าออกจากร้าน |

---

## 🚀 วิธีติดตั้ง

### 1. สร้าง Discord Bot

1. ไปที่ [discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application** → ตั้งชื่อ → **Create**
3. ไปที่ **Bot** tab
4. เปิด **Privileged Gateway Intents** ทั้ง 3 ตัว ✅
5. คัดลอก **Token**
6. **OAuth2 → URL Generator** → Scopes: `bot` + `applications.commands`
   Permissions: `Send Messages`, `Embed Links`, `Use Slash Commands`, `Create Public Threads`
7. คัดลอก URL → เชิญ bot เข้า server

### 2. ติดตั้ง Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า Token

```bash
cp .env.example .env
# แก้ไข .env แล้วใส่ token
DISCORD_TOKEN=your_token_here
```

### 4. รัน Bot

```bash
python bot.py
```

หรือ deploy บน **Railway.app** โดยใส่ `DISCORD_TOKEN` ใน Variables

---

## 📌 วิธีตั้ง Forum Shop (แนะนำ)

แทนที่จะให้ผู้เล่นพิมพ์ `/market` ทุกครั้ง ตั้งให้ร้านค้าแสดงอยู่ใน **Forum Channel** ได้ถาวร

1. สร้าง **Forum Channel** ใน server (เช่น `#marketplace`)
2. DM พิมพ์: `/setup_market #marketplace`
3. Bot สร้าง thread ให้แต่ละร้านอัตโนมัติ ผู้เล่นกดเข้าไปดูและซื้อได้เลย

> ✅ หลัง bot restart ร้านค้ายังใช้งานได้เหมือนเดิม เพราะ views ถูก re-register อัตโนมัติ

---

## 📁 โครงสร้างไฟล์

```
├── bot.py              # ไฟล์หลัก
├── requirements.txt
├── Procfile            # Railway: worker: python bot.py
├── .env.example
└── data/               # สร้างอัตโนมัติ
    ├── shop.json       # สินค้าและ stock
    ├── players.json    # ทองและ inventory ของผู้เล่น
    └── setup.json      # ตำแหน่ง Forum threads
```

---

## 💰 ระบบเศรษฐกิจ

เซ็ตมาให้เหมาะกับ Campaign ที่ได้รับ **100–150 GP ต่อเควสต่อหัว**

| Rarity | ราคา | เก็บกี่เควส |
|--------|------|------------|
| ⚪ Common | 30–80 GP | น้อยกว่า 1 เควส |
| 🟢 Uncommon | 150–550 GP | 1–4 เควส |
| 🔵 Rare | 600–2,500 GP | 5–20 เควส |
| 🟣 Very Rare | 1,500–6,000 GP | 12–48 เควส |
| 🟡 Legendary | 10,000–25,000 GP | 80–200 เควส |

---

## ⚙️ สิทธิ์ Admin

ต้องการอย่างใดอย่างหนึ่ง: สิทธิ์ `Administrator` บน server หรือ Role ชื่อ `DM`, `Admin`, หรือ `Game Master`

---

## 🔧 การปรับแต่ง

```python
# บน bot.py บรรทัดแรกๆ
GUILD_ID = 1460585900504387657   # เปลี่ยนเป็น Server ID ของคุณ
```

เปลี่ยนชื่อร้าน/NPC ได้ในส่วน `SHOPS = { ... }`

*สร้างสำหรับ campaign DnD 5e 2024 PHB*
