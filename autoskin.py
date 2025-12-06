import os
import yaml

def load_phoenixmechasovereign_config(config_path):
    """โหลด config จาก phoenixmechasovereign.yml"""
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_items_ids_cache(base_path):
    """โหลด items_ids_cache.yml สำหรับหา model_id (รองรับ duplicate keys)"""
    cache_path = os.path.join(base_path, 'items_ids_cache.yml')
    if os.path.exists(cache_path):
        # อ่านไฟล์แบบ raw text เพื่อรองรับ duplicate keys ใน YAML
        with open(cache_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

def find_model_id_in_cache(cache_text, namespace, item_name):
    """ค้นหา model_id จาก items_ids_cache.yml (search in raw text)"""
    # สร้าง pattern ที่ต้องการหา เช่น "merry_christmas_2024_set:merry_christmas_2024_axe: 10066"
    import re
    search_pattern = f"{namespace}:{item_name}: (\\d+)"
    match = re.search(search_pattern, cache_text)
    if match:
        return int(match.group(1))
    return 0

def get_item_mapping(config, cache_data=None):
    """ดึงข้อมูล material, model_id, namespace จาก config"""
    namespace = config.get('info', {}).get('namespace', '')
    items = config.get('items', {})
    
    mapping = {}
    for item_name, item_data in items.items():
        resource = item_data.get('resource', {})
        material = resource.get('material', '')
        model_id = resource.get('model_id', 0)
        
        # ถ้า model_id เป็น 0 ให้ค้นหาใน cache
        if model_id == 0 and cache_data:
            model_id = find_model_id_in_cache(cache_data, namespace, item_name)
        
        # สร้าง key จากประเภทอาวุธ (เช่น axe, sword, bow)
        # ลบ namespace prefix ออก
        item_type = item_name.replace(f'{namespace}_', '')
        
        # สร้าง key แบบสั้นด้วย (เช่น axe, sword) สำหรับ matching กับไฟล์ rama
        short_type = item_type
        # ถ้า item_type ยังมี prefix (เช่น merry_christmas_2024_axe)
        if '_' in item_type:
            parts = item_type.split('_')
            short_type = parts[-1]  # เอาส่วนสุดท้าย เช่น axe, sword
        
        mapping[item_type] = {
            'material': material,
            'model_id': model_id,
            'namespace': namespace,
            'short_type': short_type,
            'full_item_name': item_name
        }
        
        # เพิ่ม mapping แบบ short_type ด้วย (สำหรับ match กับ rama_axe.yml)
        if short_type != item_type:
            mapping[short_type] = {
                'material': material,
                'model_id': model_id,
                'namespace': namespace,
                'short_type': short_type,
                'full_type': item_type,
                'full_item_name': item_name
            }
        
        # เพิ่ม mapping พิเศษสำหรับ fishing_rod (รองรับทั้ง fish, rod, fishing_rod)
        if item_type == 'fishing_rod' or short_type == 'rod':
            for alias in ['fish', 'rod', 'fishing_rod']:
                if alias not in mapping:
                    mapping[alias] = {
                        'material': material,
                        'model_id': model_id,
                        'namespace': namespace,
                        'short_type': 'fishing_rod',
                        'full_type': item_type,
                        'full_item_name': item_name
                    }
        
        # เพิ่ม mapping พิเศษสำหรับ rapier_sword (รองรับทั้ง rapier, rapier_sword)
        if item_type == 'rapier_sword' or short_type == 'sword' and 'rapier' in item_name:
            for alias in ['rapier', 'rapier_sword']:
                if alias not in mapping:
                    mapping[alias] = {
                        'material': material,
                        'model_id': model_id,
                        'namespace': namespace,
                        'short_type': 'rapier_sword',
                        'full_type': item_type,
                        'full_item_name': item_name
                    }
        
        # เพิ่ม mapping พิเศษสำหรับ dagger
        if 'dagger' in item_name.lower():
            if 'dagger' not in mapping:
                mapping['dagger'] = {
                    'material': material,
                    'model_id': model_id,
                    'namespace': namespace,
                    'short_type': 'dagger',
                    'full_type': item_type,
                    'full_item_name': item_name
                }
        
        # เพิ่ม mapping พิเศษสำหรับ greatsword (รองรับ gsword)
        if item_type == 'greatsword' or 'greatsword' in item_name.lower():
            for alias in ['gsword', 'greatsword']:
                if alias not in mapping:
                    mapping[alias] = {
                        'material': material,
                        'model_id': model_id,
                        'namespace': namespace,
                        'short_type': 'greatsword',
                        'full_type': item_type,
                        'full_item_name': item_name
                    }
    
    return mapping

def create_skin_file(file_path, item_data, item_type):
    """สร้างไฟล์ skin ใหม่"""
    material = item_data['material']
    model_id = item_data['model_id']
    namespace = item_data['namespace']
    
    # สร้างชื่อ namespace สำหรับ display-name (ใช้ underscore แทน space)
    namespace_display = namespace.capitalize()
    
    # สร้างชื่อ item สำหรับ display-name
    item_display_name = item_type.replace('_', ' ').title()
    
    # สร้าง permission type
    perm_type = item_type
    if item_type == 'rapier_sword':
        perm_type = 'rapier'
    
    content = f'''# The material of the skin
material:
- "{material}"

# The custom model data of the texture
custom-model-data: {model_id}

# The permission to use the skin
permission: "itemskins.{perm_type}.{namespace}"

# List of required data that will be used for
# the preview skin system
#
# Read more about this feature on our wiki!
preview-skin:
  type: RIGHT_ARM
  duration: 5
  eulerAngle:
    x: 261
    y: 278
    z: 0

# This item will be used when player are able to use the skin
# e.g: has permission to use
available-item:
  material: "{material}"
  display-name: "&3&lSkin {namespace_display} {item_display_name} &a(ปลดล็อค)"
  custom-model-data: {model_id}
  glowing: false
  lore:
  - "&7คุณได้ปลดล็อกสกินนี้แล้ว!"
  - ""
  - "&aคลิกซ้าย เพื่อใช้งานสกิน !"
  - "&aคลิกขวา เพื่อดูตัวอย่างสกิน"

# This item will be used when player are not able to use the skin
# e.g: doesn't have permission to use
unavailable-item:
  material: "{material}"
  display-name: "&3&lSkin {namespace_display} {item_display_name} &c(ไม่ปลดล็อค)"
  custom-model-data: {model_id}
  glowing: false
  lore:
  - "&cคุณยังไม่ปลดล็อคสกินนี้"
  - ""
  - "&eสามารถปลดล็อคในร้านของเราหรือเปิดกล่องสุ่ม!"
  - "&3Store: &bhttps://discord.gg/SPYqnfkcQR"
  - ""
  - "&aคลิกขวา เพื่อดูตัวอย่างสกิน"
'''
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return True

def create_main_yml_entry(item_data, item_type):
    """สร้าง entry สำหรับไฟล์ .yml หลัก"""
    material = item_data['material']
    model_id = item_data['model_id']
    namespace = item_data['namespace']
    
    # สร้างชื่อ namespace สำหรับ display-name
    namespace_display = namespace.replace('_', ' ').title()
    
    # สร้างชื่อ item สำหรับ display-name
    item_display_name = item_type.replace('_', ' ').title()
    
    # สร้าง permission type
    perm_type = item_type
    if item_type == 'rapier_sword':
        perm_type = 'rapier'
    
    # สร้าง suffix สำหรับชื่อ item
    type_to_suffix = {
        'axe': 'AXE', 'bow': 'BOW', 'crossbow': 'CROSSBOW',
        'fishing_rod': 'FISH', 'dagger': 'DAGGER', 'hammer': 'HAMMER',
        'hoe': 'HOE', 'pickaxe': 'PICKAXE', 'scythe': 'SCYTHE',
        'shield': 'SHIELD', 'shovel': 'SHOVEL', 'spear': 'SPEAR',
        'staff': 'STAFF', 'sword': 'SWORD', 'trident': 'TRIDENT',
        'rapier_sword': 'RAPIER', 'greatsword': 'GSWORD',
    }
    suffix = type_to_suffix.get(item_type, item_type.upper())
    item_name = f"{namespace.upper()}_{suffix}"
    
    entry = f'''{item_name}:
  base:
    material: {material}
    custom-model-data: {model_id}
    name: '&3&lSkin {namespace_display} {item_display_name}'
    lore:
    - '&fวิธีการใช้งาน'
    - '&7ถือไอเทมแล้วทำการคลิกขวา '
    - ''
    - '&fวิธีเรียกสกิน'
    - '&7พิมพ์คำสั่ง &f/itemskin'
    displayed-type: '&a(ปลดล็อคสกิน)'
    commands:
      cmd0:
        format: lp user %player_name% permission set itemskins.{perm_type}.{namespace} true
        delay: 0.0
        console: true
'''
    return entry

def update_rama_file(rama_file_path, item_data, item_type):
    """อัพเดทไฟล์ rama ด้วยค่า material, custom-model-data และ display-name"""
    with open(rama_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # ตรวจสอบว่ามีข้อมูลที่ต้องการแก้ไขหรือไม่
    has_material = 'material:' in content
    has_custom_model_data = 'custom-model-data:' in content
    
    # ถ้าไม่มีข้อมูลที่ต้องแก้ไขเลย ให้ข้าม
    if not has_material and not has_custom_model_data:
        return False
    
    # แยกบรรทัด
    lines = content.split('\n')
    new_lines = []
    
    material = item_data['material']
    model_id = item_data['model_id']
    namespace = item_data['namespace']
    
    # สร้างชื่อ namespace สำหรับ display-name (ตัวแรกพิมพ์ใหญ่)
    namespace_display = namespace.capitalize()
    
    # สร้างชื่อ item สำหรับ display-name (เช่น Shield, Axe, Sword)
    item_display_name = item_type.replace('_', ' ').title()
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # อัพเดท material (รูปแบบ list) - บรรทัดแรกสุด
        if line.strip() == 'material:' and (i == 0 or not lines[i-1].strip().endswith(':')):
            new_lines.append(line)
            i += 1
            # แทนที่บรรทัดถัดไปที่เป็น - "xxx"
            if i < len(lines) and lines[i].strip().startswith('- "'):
                new_lines.append(f'- "{material}"')
            else:
                new_lines.append(lines[i])
            i += 1
            continue
        
        # อัพเดท custom-model-data
        elif line.strip().startswith('custom-model-data:'):
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + f'custom-model-data: {model_id}')
            i += 1
            continue
        
        # อัพเดท permission (เปลี่ยน rama เป็น namespace)
        elif line.strip().startswith('permission:') and 'itemskins.' in line:
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + f'permission: "itemskins.{item_type}.{namespace}"')
            i += 1
            continue
        
        # อัพเดท material ใน available-item และ unavailable-item (มี indent)
        elif '  material:' in line and line.strip().startswith('material:'):
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + f'material: "{material}"')
            i += 1
            continue
        
        # อัพเดท display-name ใน available-item (ถ้ามี)
        elif 'display-name:' in line and '(ปลดล็อค)' in line:
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + f'display-name: "&3&lSkin {namespace_display} {item_display_name} &a(ปลดล็อค)"')
            i += 1
            continue
        
        # อัพเดท display-name ใน unavailable-item (ถ้ามี)
        elif 'display-name:' in line and '(ไม่ปลดล็อค)' in line:
            indent = len(line) - len(line.lstrip())
            new_lines.append(' ' * indent + f'display-name: "&3&lSkin {namespace_display} {item_display_name} &c(ไม่ปลดล็อค)"')
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    # เขียนไฟล์ใหม่
    with open(rama_file_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    return True

def get_rama_item_type(filename):
    """แปลงชื่อไฟล์ rama เป็น item type"""
    # rama_axe.yml -> axe
    # rama_sword.yml -> sword
    # rama_fish.yml -> fishing_rod
    # merry_christmas_2024_set_axe.yml -> axe
    name = filename.replace('.yml', '').strip()
    
    # ลบ prefix rama_ ถ้ามี
    if name.startswith('rama_'):
        name = name.replace('rama_', '')
    
    # หา item type จากส่วนสุดท้ายของชื่อไฟล์
    # เช่น merry_christmas_2024_set_axe -> axe
    # เช่น phoenixmechasovereign_sword -> sword
    if '_' in name:
        parts = name.split('_')
        # เอาส่วนสุดท้ายเป็น item type
        name = parts[-1]
    
    # mapping พิเศษ
    special_mapping = {
        'fish': 'fishing_rod',
        'rapier': 'rapier_sword',
        'rod': 'fishing_rod',
        'gsword': 'greatsword',
    }
    
    return special_mapping.get(name, name)

def update_rama_yml(rama_yml_path, item_mapping):
    """อัพเดทไฟล์ rama.yml หลัก"""
    with open(rama_yml_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    current_item = None
    current_item_type = None
    
    # mapping ชื่อ item ใน rama.yml กับ item type
    rama_to_type = {
        'AXE': 'axe',
        'BOW': 'bow',
        'CROSSBOW': 'crossbow',
        'FISH': 'fishing_rod',
        'DAGGER': 'dagger',
        'HAMMER': 'hammer',
        'HOE': 'hoe',
        'PICKAXE': 'pickaxe',
        'SCYTHE': 'scythe',
        'SHIELD': 'shield',
        'SHOVEL': 'shovel',
        'SPEAR': 'spear',
        'STAFF': 'staff',
        'SWORD': 'sword',
        'TRIDENT': 'trident',
        'RAPIER': 'rapier_sword',
        'GSWORD': 'greatsword',
    }
    
    # mapping สำหรับ suffix ใหม่ที่ต้องการ (จาก item type)
    type_to_suffix = {
        'axe': 'AXE',
        'bow': 'BOW',
        'crossbow': 'CROSSBOW',
        'fishing_rod': 'FISH',
        'fish': 'FISH',
        'rod': 'FISH',
        'dagger': 'DAGGER',
        'hammer': 'HAMMER',
        'hoe': 'HOE',
        'pickaxe': 'PICKAXE',
        'scythe': 'SCYTHE',
        'shield': 'SHIELD',
        'shovel': 'SHOVEL',
        'spear': 'SPEAR',
        'staff': 'STAFF',
        'sword': 'SWORD',
        'trident': 'TRIDENT',
        'rapier_sword': 'RAPIER',
        'rapier': 'RAPIER',
        'greatsword': 'GSWORD',
    }
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # ตรวจจับ item หลัก (เช่น SUNSEA_AXE:)
        if line and not line.startswith(' ') and line.endswith(':') and '_' in line:
            # เปลี่ยนชื่อ item เป็น namespace ใหม่
            old_item_name = line[:-1]  # ลบ : ออก
            parts = old_item_name.split('_')
            if len(parts) >= 2:
                item_suffix = parts[-1]  # เช่น AXE, BOW
                current_item_type = rama_to_type.get(item_suffix, item_suffix.lower())
                
                if current_item_type in item_mapping:
                    namespace = item_mapping[current_item_type]['namespace']
                    # ใช้ suffix ที่ถูกต้องจาก type_to_suffix
                    new_suffix = type_to_suffix.get(current_item_type, item_suffix)
                    new_item_name = f"{namespace.upper()}_{new_suffix}"
                    new_lines.append(f"{new_item_name}:")
                    current_item = current_item_type
                else:
                    new_lines.append(line)
                    current_item = None
            else:
                new_lines.append(line)
                current_item = None
            i += 1
            continue
        
        # อัพเดท material
        if current_item and 'material:' in line and current_item in item_mapping:
            indent = len(line) - len(line.lstrip())
            material = item_mapping[current_item]['material']
            new_lines.append(' ' * indent + f'material: {material}')
            i += 1
            continue
        
        # อัพเดท custom-model-data
        if current_item and 'custom-model-data:' in line and current_item in item_mapping:
            indent = len(line) - len(line.lstrip())
            model_id = item_mapping[current_item]['model_id']
            new_lines.append(' ' * indent + f'custom-model-data: {model_id}')
            i += 1
            continue
        
        # อัพเดท name
        if current_item and "name: '" in line and current_item in item_mapping:
            indent = len(line) - len(line.lstrip())
            namespace = item_mapping[current_item]['namespace']
            namespace_display = namespace.capitalize()
            item_display = current_item.replace('_', ' ').title()
            new_lines.append(' ' * indent + f"name: '&3&lSkin {namespace_display} {item_display}'")
            i += 1
            continue
        
        # อัพเดท permission ใน format
        if current_item and 'format: lp' in line and 'itemskins.' in line and current_item in item_mapping:
            indent = len(line) - len(line.lstrip())
            namespace = item_mapping[current_item]['namespace']
            # หา item type สำหรับ permission
            perm_type = current_item
            if current_item == 'rapier_sword':
                perm_type = 'rapier'
            elif current_item == 'fishing_rod':
                perm_type = 'fishing_rod'
            new_lines.append(' ' * indent + f'format: lp user %player_name% permission set itemskins.{perm_type}.{namespace} true')
            i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    # ตรวจสอบ items ที่มีใน item_mapping แต่ไม่มีในไฟล์ แล้วเพิ่มเข้าไป
    existing_items = set()
    for line in new_lines:
        if line and not line.startswith(' ') and line.endswith(':') and '_' in line:
            parts = line[:-1].split('_')
            if len(parts) >= 2:
                suffix = parts[-1]
                item_type = rama_to_type.get(suffix, None)
                if item_type:
                    existing_items.add(item_type)
    
    # เพิ่ม entry ที่ไม่มี
    main_item_types = ['axe', 'bow', 'crossbow', 'fishing_rod', 'dagger', 'hammer', 
                      'hoe', 'pickaxe', 'scythe', 'shield', 'shovel', 'spear', 
                      'staff', 'sword', 'trident', 'rapier_sword', 'greatsword']
    
    for item_type in main_item_types:
        if item_type in item_mapping and item_type not in existing_items:
            new_entry = create_main_yml_entry(item_mapping[item_type], item_type)
            new_lines.append('')
            new_lines.append(new_entry)
            print(f"   + เพิ่ม entry ใหม่: {item_type}")
    
    # เขียนไฟล์ใหม่
    with open(rama_yml_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    return True

def find_config_folders(base_path):
    """ค้นหาโฟลเดอร์ที่มี configs/ อยู่ข้างใน"""
    config_folders = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            configs_path = os.path.join(item_path, 'configs')
            if os.path.isdir(configs_path):
                # รวบรวมไฟล์ .yml ทั้งหมดใน configs (ยกเว้น _armor, _category, _cosmetic, _cosmatic)
                config_files = []
                for yml_file in os.listdir(configs_path):
                    if yml_file.endswith('.yml') and not any(yml_file.endswith(suffix) for suffix in ['_armor.yml', '_category.yml', '_cosmetic.yml', '_cosmatic.yml']):
                        config_files.append(os.path.join(configs_path, yml_file))
                
                if config_files:
                    config_folders.append({
                        'name': item,
                        'config_paths': config_files  # เก็บทุกไฟล์ config
                    })
    return config_folders

def load_all_configs(config_paths):
    """โหลดและรวม config จากหลายไฟล์"""
    merged_config = {
        'info': {},
        'items': {}
    }
    
    for config_path in config_paths:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            if config:
                # รวม info (ใช้ตัวแรกที่เจอ)
                if 'info' in config and not merged_config['info']:
                    merged_config['info'] = config['info']
                elif 'info' in config:
                    # ถ้ายังไม่มี namespace ให้ใช้จากไฟล์นี้
                    if 'namespace' not in merged_config['info'] and 'namespace' in config['info']:
                        merged_config['info']['namespace'] = config['info']['namespace']
                
                # รวม items
                if 'items' in config:
                    merged_config['items'].update(config['items'])
    
    return merged_config

def find_skin_folders(base_path, config_folder_names):
    """ค้นหาโฟลเดอร์ที่มีไฟล์ skin .yml อยู่ข้างใน (เช่น rama/)"""
    skin_folders = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        # ข้ามโฟลเดอร์ที่เป็น config folder (มี configs/ ข้างใน)
        if os.path.isdir(item_path) and item not in config_folder_names:
            # ตรวจสอบว่ามีไฟล์ .yml ข้างใน และไม่มีโฟลเดอร์ configs/
            configs_path = os.path.join(item_path, 'configs')
            if not os.path.isdir(configs_path):
                has_yml = any(f.endswith('.yml') for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f)))
                if has_yml:
                    skin_folders.append(item_path)
    return skin_folders

def main():
    # กำหนด path
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    print("=" * 60)
    print("โปรแกรมอัพเดท ItemSkins อัตโนมัติ")
    print("=" * 60)
    
    # ค้นหาโฟลเดอร์ config ทั้งหมด
    config_folders = find_config_folders(base_path)
    
    if not config_folders:
        print("⚠️  ไม่พบโฟลเดอร์ config!")
        return
    
    print(f"\n📂 พบ {len(config_folders)} โฟลเดอร์ config:")
    for cf in config_folders:
        print(f"   - {cf['name']} ({len(cf['config_paths'])} ไฟล์)")
    
    # ให้ผู้ใช้เลือก config
    if len(config_folders) == 1:
        selected_config = config_folders[0]
    else:
        print("\n🔢 กรุณาเลือก config ที่ต้องการใช้:")
        for i, cf in enumerate(config_folders, 1):
            print(f"   {i}. {cf['name']}")
        
        try:
            choice = int(input("\nป้อนหมายเลข: ")) - 1
            if 0 <= choice < len(config_folders):
                selected_config = config_folders[choice]
            else:
                print("❌ หมายเลขไม่ถูกต้อง!")
                return
        except ValueError:
            print("❌ กรุณาป้อนตัวเลข!")
            return
    
    config_paths = selected_config['config_paths']
    
    # รวบรวมชื่อโฟลเดอร์ config ทั้งหมด (เพื่อไม่ให้นับเป็น skin folder)
    config_folder_names = [cf['name'] for cf in config_folders]
    
    # ค้นหาโฟลเดอร์ skin
    skin_folders = find_skin_folders(base_path, config_folder_names)
    
    # หา rama folder หรือโฟลเดอร์ skin อื่นๆ
    rama_folder = None
    if skin_folders:
        rama_folder = skin_folders[0]  # ใช้โฟลเดอร์แรกที่พบ
        print(f"📂 พบ skin folder: {os.path.basename(rama_folder)}")
    else:
        print("⚠️  ไม่พบ skin folder!")
    
    print(f"\n📂 กำลังโหลด config จาก {len(config_paths)} ไฟล์...")
    for cp in config_paths:
        print(f"   - {os.path.basename(cp)}")
    config = load_all_configs(config_paths)
    
    # โหลด items_ids_cache.yml
    print(f"📂 กำลังโหลด items_ids_cache.yml...")
    cache_data = load_items_ids_cache(base_path)
    if cache_data:
        print(f"✅ โหลด items_ids_cache.yml สำเร็จ!")
    else:
        print(f"⚠️  ไม่พบ items_ids_cache.yml (จะใช้ model_id จาก config เท่านั้น)")
    
    # ดึงข้อมูล namespace
    namespace = config.get('info', {}).get('namespace', '')
    print(f"✅ Namespace: {namespace}")
    
    # ดึง mapping ของ items (ส่ง cache_data ไปด้วย)
    item_mapping = get_item_mapping(config, cache_data)
    print(f"✅ พบ {len(item_mapping)} items ใน config")
    
    # แสดงข้อมูลที่พบ
    print("\n📋 รายการ Items ที่พบ:")
    print("-" * 50)
    for item_type, data in item_mapping.items():
        print(f"  {item_type}:")
        print(f"    Material: {data['material']}")
        print(f"    Model ID: {data['model_id']}")
    
    # อัพเดทไฟล์ใน rama folder (ถ้ามี)
    updated_files = []
    skipped_files = []
    renamed_files = []
    
    if rama_folder and os.path.exists(rama_folder):
        print("\n" + "=" * 60)
        print(f"กำลังอัพเดทไฟล์ใน {os.path.basename(rama_folder)} folder...")
        print("=" * 60)
        
        # อัพเดทไฟล์ที่มีอยู่แล้ว
        for filename in os.listdir(rama_folder):
            if filename.endswith('.yml'):
                rama_file_path = os.path.join(rama_folder, filename)
                item_type = get_rama_item_type(filename)
                
                if item_type in item_mapping:
                    item_data = item_mapping[item_type]
                    
                    result = update_rama_file(rama_file_path, item_data, item_type)
                    
                    if result:
                        # เปลี่ยนชื่อไฟล์จาก rama_xxx.yml เป็น namespace_xxx.yml
                        new_filename = f"{item_data['namespace']}_{item_type}.yml"
                        new_file_path = os.path.join(rama_folder, new_filename)
                        
                        # เปลี่ยนชื่อไฟล์ถ้าชื่อไม่เหมือนกัน และไฟล์ใหม่ยังไม่มี
                        if filename != new_filename and not os.path.exists(new_file_path):
                            os.rename(rama_file_path, new_file_path)
                            renamed_files.append((filename, new_filename))
                        
                        print(f"\n📝 อัพเดท: {filename}")
                        print(f"   → Material: {item_data['material']}")
                        print(f"   → Model ID: {item_data['model_id']}")
                        print(f"   → Namespace: {item_data['namespace']}")
                        if filename != new_filename and not os.path.exists(new_file_path):
                            print(f"   → เปลี่ยนชื่อเป็น: {new_filename}")
                        updated_files.append(new_filename if filename == new_filename else filename)
                    else:
                        print(f"\n⏭️  ข้าม: {filename} (ไม่มีข้อมูลที่ต้องแก้ไข)")
                        skipped_files.append(filename)
                else:
                    print(f"\n⚠️  ข้าม: {filename} (ไม่พบ item type '{item_type}' ใน config)")
                    skipped_files.append(filename)
    
    # ถ้าไม่พบ skin folder ให้สร้างขึ้นมาพร้อมไฟล์ skin
    if not rama_folder or not os.path.exists(rama_folder):
        # สร้างโฟลเดอร์ skin ใหม่
        skin_folder_name = f"{namespace}_skins"
        rama_folder = os.path.join(base_path, skin_folder_name)
        os.makedirs(rama_folder, exist_ok=True)
        print(f"\n✨ สร้างโฟลเดอร์ skin ใหม่: {skin_folder_name}")
        
        # สร้างไฟล์ skin ทั้งหมด
        print("\n" + "=" * 60)
        print("กำลังสร้างไฟล์ skin...")
        print("=" * 60)
        
        main_item_types = ['axe', 'bow', 'crossbow', 'fishing_rod', 'dagger', 'hammer', 
                          'hoe', 'pickaxe', 'scythe', 'shield', 'shovel', 'spear', 
                          'staff', 'sword', 'trident', 'rapier_sword', 'greatsword']
        
        created_files = []
        for item_type in main_item_types:
            if item_type in item_mapping:
                item_data = item_mapping[item_type]
                new_filename = f"{item_data['namespace']}_{item_type}.yml"
                new_file_path = os.path.join(rama_folder, new_filename)
                
                create_skin_file(new_file_path, item_data, item_type)
                print(f"\n✨ สร้างไฟล์: {new_filename}")
                print(f"   → Material: {item_data['material']}")
                print(f"   → Model ID: {item_data['model_id']}")
                created_files.append(new_filename)
        
        print(f"\n✅ สร้างไฟล์ skin สำเร็จ: {len(created_files)} ไฟล์")
    
    # สรุปผล
    print("\n" + "=" * 60)
    print("สรุปผลการอัพเดท")
    print("=" * 60)
    print(f"✅ อัพเดทสำเร็จ: {len(updated_files)} ไฟล์")
    print(f"📝 เปลี่ยนชื่อ: {len(renamed_files)} ไฟล์")
    print(f"⚠️  ข้าม: {len(skipped_files)} ไฟล์")
    
    if updated_files:
        print("\nไฟล์ที่อัพเดท:")
        for f in updated_files:
            print(f"  - {f}")
    
    if renamed_files:
        print("\nไฟล์ที่เปลี่ยนชื่อ:")
        for old, new in renamed_files:
            print(f"  - {old} → {new}")
    
    if skipped_files:
        print("\nไฟล์ที่ข้าม:")
        for f in skipped_files:
            print(f"  - {f}")
    
    # อัพเดทไฟล์ .yml หลักทั้งหมดใน base folder
    print("\n" + "=" * 60)
    print("กำลังอัพเดทไฟล์ .yml หลักใน base folder...")
    print("=" * 60)
    
    # หาไฟล์ .yml ทั้งหมดใน base folder (ไม่รวม items_ids_cache.yml)
    yml_files_updated = []
    yml_files_renamed = []
    yml_found = False
    
    for filename in os.listdir(base_path):
        if filename.endswith('.yml') and filename != 'items_ids_cache.yml':
            yml_file_path = os.path.join(base_path, filename)
            
            # ตรวจสอบว่าเป็นไฟล์ไม่ใช่โฟลเดอร์
            if os.path.isfile(yml_file_path):
                yml_found = True
                print(f"\n📄 กำลังอัพเดท: {filename}")
                
                result = update_rama_yml(yml_file_path, item_mapping)
                if result:
                    # เปลี่ยนชื่อไฟล์เป็น namespace.yml
                    new_yml_name = f"{namespace}.yml"
                    new_yml_path = os.path.join(base_path, new_yml_name)
                    
                    if yml_file_path != new_yml_path and not os.path.exists(new_yml_path):
                        os.rename(yml_file_path, new_yml_path)
                        print(f"   ✅ อัพเดทสำเร็จ!")
                        print(f"   → เปลี่ยนชื่อเป็น: {new_yml_name}")
                        yml_files_renamed.append((filename, new_yml_name))
                    else:
                        print(f"   ✅ อัพเดทสำเร็จ!")
                    yml_files_updated.append(filename)
                else:
                    print(f"   ⚠️  ข้าม (ไม่มีข้อมูลที่ต้องแก้ไข)")
    
    # ถ้าไม่พบไฟล์ yml หลัก ให้สร้างใหม่
    if not yml_found:
        print(f"\n✨ สร้างไฟล์ .yml หลักใหม่: {namespace}.yml")
        new_yml_path = os.path.join(base_path, f"{namespace}.yml")
        
        # สร้าง content สำหรับไฟล์ yml หลัก
        main_item_types = ['axe', 'bow', 'crossbow', 'fishing_rod', 'dagger', 'hammer', 
                          'hoe', 'pickaxe', 'scythe', 'shield', 'shovel', 'spear', 
                          'staff', 'sword', 'trident', 'rapier_sword', 'greatsword']
        
        yml_content = ""
        for item_type in main_item_types:
            if item_type in item_mapping:
                entry = create_main_yml_entry(item_mapping[item_type], item_type)
                yml_content += entry + "\n"
        
        with open(new_yml_path, 'w', encoding='utf-8') as f:
            f.write(yml_content)
        
        print(f"   ✅ สร้างสำเร็จ!")
        yml_files_updated.append(f"{namespace}.yml")
    
    if not yml_files_updated:
        print("\n⚠️  ไม่พบไฟล์ .yml ที่ต้องอัพเดทใน base folder")
    else:
        print(f"\n✅ อัพเดทไฟล์ .yml หลักสำเร็จ: {len(yml_files_updated)} ไฟล์")
    
    print("\n✨ เสร็จสิ้น!")

if __name__ == "__main__":
    main()
