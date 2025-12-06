# AutoSkin Generator

🎮 เครื่องมือสร้างไฟล์ skin อัตโนมัติสำหรับ ItemSkins Plugin (Minecraft Server)

## 📋 คุณสมบัติ

- สร้างไฟล์ skin จาก config ของ PhoenixMechaSovereign
- รองรับการอ่าน `items_ids_cache.yml` สำหรับหา `model_id`
- สร้างไฟล์ `.yml` พร้อม permission, preview-skin, และ display items
- รองรับอาวุธหลายประเภท (axe, sword, bow, fishing_rod, dagger, greatsword, rapier และอื่นๆ)

## 🔧 ความต้องการ

- Python 3.7+
- PyYAML

## 📦 การติดตั้ง

```bash
# Clone repository
git clone https://github.com/chayangkunx/autoskin.git
cd autoskin

# ติดตั้ง dependencies
pip install -r requirements.txt
```

## 🚀 วิธีใช้งาน

```bash
python autoskin.py
```

### ตัวอย่างการใช้งาน

1. เตรียมไฟล์ config ของ PhoenixMechaSovereign (`phoenixmechasovereign.yml`)
2. (ถ้ามี) เตรียมไฟล์ `items_ids_cache.yml` สำหรับ model_id
3. รันสคริปต์
4. ไฟล์ skin จะถูกสร้างในโฟลเดอร์ที่กำหนด

## 📁 โครงสร้างไฟล์ที่สร้าง

```
skins/
├── axe/
│   └── namespace_axe.yml
├── sword/
│   └── namespace_sword.yml
└── bow/
    └── namespace_bow.yml
```

## ⚙️ การตั้งค่า

ไฟล์ skin ที่สร้างจะมีรูปแบบดังนี้:

```yaml
material:
- "DIAMOND_AXE"

custom-model-data: 10001

permission: "itemskins.axe.namespace"

preview-skin:
  type: RIGHT_ARM
  duration: 5
  eulerAngle:
    x: 261
    y: 278
    z: 0

available-item:
  material: "DIAMOND_AXE"
  display-name: "&3&lSkin Namespace Axe &a(ปลดล็อค)"
  # ...

unavailable-item:
  material: "DIAMOND_AXE"
  display-name: "&3&lSkin Namespace Axe &c(ไม่ปลดล็อค)"
  # ...
```

## 🤝 การมีส่วนร่วม

ยินดีรับ Pull Requests! สำหรับการเปลี่ยนแปลงครั้งใหญ่ กรุณาเปิด Issue ก่อนเพื่อหารือ

## 📄 License

[MIT](LICENSE)

## 👤 ผู้พัฒนา

- GitHub: [chayangkunx](https://github.com/chayangkunx)
