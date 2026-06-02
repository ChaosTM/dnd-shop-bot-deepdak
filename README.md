# ⚔️ Merchant Boy — DnD 5e Shop Bot

> Discord Bot สำหรับจัดการตลาดค้าขายและระบบเลเวลใน Campaign DnD 5e (2024 PHB)

---

## 🏪 ร้านค้าทั้งหมด

| ร้าน | NPC | สินค้า |
|------|-----|--------|
| ⚒️ **Blacksmith** | แนะนำให้เข้าไปตั้งเอง | Simple/Martial Weapons + Ammo |
| 🧪 **Alchemists** | แนะนำให้เข้าไปตั้งเอง | Potions + Alchemical Gear + Focuses + Scrolls |
| 🎒 **General store** | แนะนำให้เข้าไปตั้งเอง | Gear + Food + Tools + Clothing |

**สินค้ารวม 131 รายการ** อิงราคาจาก 2024 PHB Official ทุกชิ้น

---

## 📋 คำสั่งทั้งหมด

### 👥 ผู้เล่นทั่วไป

| คำสั่ง | คำอธิบาย |
|--------|---------|
| `/market` | เปิดตลาด — เลือกร้านจาก dropdown |
| `/buy <id> [จำนวน]` | ซื้อสินค้า |
| `/sell <id> [จำนวน]` | ขายสินค้า (ได้คืน 50%) |
| `/gold` | ดูทอง + เลเวล + inventory |
| `/level [@member]` | ดูเลเวลและความคืบหน้าของตัวเองหรือคนอื่น |

> 💡 กดปุ่ม **Check Coinpurse** และ **List of Items** ใน embed ได้เลย

---

### 🎲 Quest Reward (DM เท่านั้น)

| คำสั่ง | คำอธิบาย |
|--------|---------|
| `/roll_reward <rank> [quest_name] [count]` | สุ่ม Magic Items ตาม Quest Rank |

**ตาราง Quest Rank:**

| Rank | Common | Uncommon | Rare | Very Rare | Legendary |
|------|--------|----------|------|-----------|-----------|
| ⚪ F | 90% | 10% | — | — | — |
| 🟢 E | 65% | 30% | 5% | — | — |
| 🔵 D | 30% | 55% | 15% | — | — |
| 🟣 C | 10% | 45% | 40% | 5% | — |
| 🔴 B | 5% | 20% | 50% | 25% | — |
| 🟠 A | — | 10% | 35% | 45% | 10% |
| 🟡 S | — | 5% | 20% | 45% | 30% |

---

### ⭐ ระบบเลเวล (DM เท่านั้น)

| คำสั่ง | คำอธิบาย |
|--------|---------|
| `/admin_quest <@A @B @C> [amount] [quest_name]` | เพิ่มเควสให้ผู้เล่นหลายคนพร้อมกัน |

**กติกา:**
- เริ่มต้นที่ **Level 3**
- ทุก **4 เควส** = Level Up 1 ระดับ
- ไม่มี Level สูงสุด — DM กำหนดตามเนื้อเรื่อง
- ถ้า Level Up จะ announce ให้ทุกคนในแชทเห็น 🎉

---

### 🛡️ Admin Commands (DM / Admin / Game Master เท่านั้น)

| คำสั่ง | คำอธิบาย |
|--------|---------|
| `/setup_shop <shop> <thread>` | ผูกร้านค้าเข้ากับ Forum Thread (ทำทีละร้าน) |
| `/setup_refresh` | รีเฟรช embed ทุกร้านพร้อมกัน |
| `/admin_gold <member> <add/remove/set> <amount>` | ปรับทองผู้เล่น |
| `/admin_give_item <member> <id> [จำนวน]` | มอบไอเทมให้ผู้เล่น |
| `/admin_take_item <member> <id> [จำนวน]` | เอาไอเทมจากผู้เล่น |
| `/admin_add_item <id> <name> <desc> <price> <category> [stock]` | เพิ่มสินค้าใหม่ |
| `/admin_stock <id> <amount>` | ปรับ stock (-1 = ไม่จำกัด) |
| `/admin_remove_item <id>` | ลบสินค้าออกจากร้าน |
| `/magic_ids [rarity]` | ดู ID ของ Magic Items ทั้งหมด |

> 💡 `/admin_give_item` และ `/sell` รองรับ **autocomplete** — พิมพ์ชื่อไอเทมแล้วเลือกจากรายการได้เลย

---

## 🚀 วิธีติดตั้ง

### 1. สร้าง Discord Bot

1. ไปที่ [discord.com/developers/applications](https://discord.com/developers/applications)
2. **New Application** → ตั้งชื่อ → **Create**
3. ไปที่ **Bot** tab → เปิด **Privileged Gateway Intents** ทั้ง 3 ตัว ✅
4. คัดลอก **Token**
5. **OAuth2 → URL Generator** → Scopes: `bot` + `applications.commands`
   Permissions: `Send Messages`, `Embed Links`, `Use Slash Commands`, `Create Public Threads`
6. เชิญ bot เข้า server

### 2. ติดตั้ง

```bash
pip install -r requirements.txt
```

### 3. ตั้งค่า Token

```bash
cp .env.example .env
# แก้ไข .env ใส่ token
DISCORD_TOKEN=your_token_here
```

### 4. รัน

```bash
python bot.py
```

หรือ deploy บน **Railway.app** โดยใส่ `DISCORD_TOKEN` ใน Variables และสร้าง `Procfile`:
```
worker: python bot.py
```

---

## 📌 วิธีตั้ง Forum Shop

1. สร้าง **Forum Channel** ใน server (เช่น `#marketplace`)
2. สร้าง thread แยกสำหรับแต่ละร้าน (3 threads)
3. DM พิมพ์ `/setup_shop` → เลือกร้าน → เลือก thread ที่ต้องการ
4. ทำซ้ำกับทุกร้าน
5. ผู้เล่นเข้าไปกด dropdown ซื้อของได้เลยโดยไม่ต้องพิมพ์คำสั่ง

> ✅ หลัง bot restart ปุ่มและ dropdown ยังทำงานได้ เพราะ views ถูก re-register อัตโนมัติ

---

## 📁 โครงสร้างไฟล์

```
├── bot.py              # ไฟล์เดียว — ทุกอย่างอยู่ที่นี่
├── requirements.txt
├── Procfile
├── .env.example
└── data/               # สร้างอัตโนมัติเมื่อรัน
    ├── shop.json       # สินค้าและ stock
    ├── players.json    # ทอง, inventory, เลเวล, เควส
    └── setup.json      # ตำแหน่ง Forum threads
```

---

## 💰 ระบบเศรษฐกิจ

ออกแบบสำหรับ Campaign ที่ได้รับ **100–150 GP ต่อเควสต่อหัว**

| Rarity | ราคา | เก็บกี่เควส |
|--------|------|------------|
| ⚪ Common | 30–80 GP | น้อยกว่า 1 เควส |
| 🟢 Uncommon | 150–550 GP | 1–4 เควส |
| 🔵 Rare | 600–2,500 GP | 5–20 เควส |
| 🟣 Very Rare | 1,500–6,000 GP | 12–48 เควส |
| 🟡 Legendary | 10,000–25,000 GP | 80–200 เควส |

---

## ⚙️ สิทธิ์ Admin

ต้องการอย่างใดอย่างหนึ่ง:
- สิทธิ์ `Administrator` บน server
- Role ชื่อ `DM`, `Admin`, หรือ `Game Master`

---

## 🔧 การปรับแต่ง

แก้ค่าตัวแปรด้านบนของไฟล์ `bot.py`:

```python
GUILD_ID       = 1460585900504387657  # Server ID ของคุณ
START_LEVEL    = 3                    # เริ่มต้นที่ Level เท่าไหร่
QUESTS_PER_LVL = 4                   # กี่เควสถึง Level Up
```

---

*Merchant Boy — Built for ChaosTM's DnD 5e Campaign | 2024 PHB*
