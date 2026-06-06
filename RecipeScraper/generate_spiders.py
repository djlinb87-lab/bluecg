import os

# 1. 定義所有的目標網頁與設定
targets = [
    # === 原有的防具類 ===
    {"url": "https://gamerch.com/blue-cg/453316", "category": "防具", "type": "鎧甲", "suffix": "armor"},
    {"url": "https://gamerch.com/blue-cg/453317", "category": "防具", "type": "衣服", "suffix": "cloth"},
    {"url": "https://gamerch.com/blue-cg/453318", "category": "防具", "type": "長袍", "suffix": "robe"},
    {"url": "https://gamerch.com/blue-cg/453319", "category": "防具", "type": "靴子", "suffix": "boots"},
    {"url": "https://gamerch.com/blue-cg/453320", "category": "防具", "type": "頭盔", "suffix": "helm"},
    {"url": "https://gamerch.com/blue-cg/453321", "category": "防具", "type": "帽子", "suffix": "hat"},
    {"url": "https://gamerch.com/blue-cg/453322", "category": "防具", "type": "盾牌", "suffix": "shield"},
    {"url": "https://gamerch.com/blue-cg/453323", "category": "防具", "type": "鞋子", "suffix": "shoes"},
    
    # === 原有的武器類 ===
    {"url": "https://gamerch.com/blue-cg/453302", "category": "武器", "type": "劍", "suffix": "sword"},
    {"url": "https://gamerch.com/blue-cg/453303", "category": "武器", "type": "斧", "suffix": "axe"},
    {"url": "https://gamerch.com/blue-cg/453304", "category": "武器", "type": "槍", "suffix": "spear"},
    {"url": "https://gamerch.com/blue-cg/453305", "category": "武器", "type": "弓", "suffix": "bow"},
    {"url": "https://gamerch.com/blue-cg/453306", "category": "武器", "type": "杖", "suffix": "staff"},
    {"url": "https://gamerch.com/blue-cg/453307", "category": "武器", "type": "投擲武器", "suffix": "throw"},
    {"url": "https://gamerch.com/blue-cg/453308", "category": "武器", "type": "小刀", "suffix": "knife"},
    
    # === 寵物裝備系列 ===
    {"url": "https://gamerch.com/blue-cg/453587", "category": "寵物裝備", "type": "寵物晶石", "suffix": "pet_crystal"},
    {"url": "https://gamerch.com/blue-cg/453588", "category": "寵物裝備", "type": "寵物項圈", "suffix": "pet_collar"},
    {"url": "https://gamerch.com/blue-cg/453589", "category": "寵物裝備", "type": "寵物重裝", "suffix": "pet_heavy"},
    {"url": "https://gamerch.com/blue-cg/453590", "category": "寵物裝備", "type": "寵物飾品", "suffix": "pet_accessory"},
    {"url": "https://gamerch.com/blue-cg/453591", "category": "寵物裝備", "type": "寵物輕裝", "suffix": "pet_light"},
    
    # === 其他道具系列 ===
    {"url": "https://gamerch.com/blue-cg/453290", "category": "其他", "type": "飾品", "suffix": "accessory"},
    {"url": "https://gamerch.com/blue-cg/453291", "category": "其他", "type": "炸彈", "suffix": "bomb"},
    {"url": "https://gamerch.com/blue-cg/453267", "category": "其他", "type": "料理", "suffix": "food"},
    {"url": "https://gamerch.com/blue-cg/453256", "category": "其他", "type": "藥水", "suffix": "potion"},
    {"url": "https://gamerch.com/blue-cg/453262", "category": "其他", "type": "外傷藥", "suffix": "injury_med"},
    {"url": "https://gamerch.com/blue-cg/453257", "category": "其他", "type": "療傷藥", "suffix": "heal_med"},
    {"url": "https://gamerch.com/blue-cg/452830", "category": "其他", "type": "變身卡", "suffix": "card"}
]

# 2. 乾淨的模版（已將正則表達式改為完全不需要反斜線的 [0-9]+）
SPIDER_TEMPLATE = """import os
import re
import json
import requests
from bs4 import BeautifulSoup

# ==================== 每個檔案獨有的設定區 ====================
CONFIG = {
    "url": "__TARGET_URL__",
    "category": "__TARGET_CATEGORY__",
    "type": "__TARGET_TYPE__",
    "output_js": "__TARGET_OUTPUT_JS__"
}
# ============================================================

def parse_page():
    url = CONFIG["url"]
    category = CONFIG["category"]
    default_type = CONFIG["type"]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://gamerch.com/"
    }
    
    print(f"🔄 正在解碼：[{category} - {default_type}] -> {url}")
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f" ❌ 失敗，狀態碼: {response.status_code}")
            return []
    except Exception as e:
        print(f" ❌ 連線異常: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    page_equipments = []
    current_type = default_type

    for table in tables:
        items = [td.get_text().strip() for td in table.find_all(["td", "th"]) if td.get_text().strip()]
        
        if "等級" not in items or "名稱" not in items or "所需材料" not in items:
            continue
            
        try:
            idx_mat_title = items.index("所需材料")
            name = items[idx_mat_title + 2] 
            level_str = items[idx_mat_title + 1]
            level_match = re.search("[0-9]+", level_str)  # 🌟 改用無反斜線的純粹數字匹配法
            
            if not level_match or not name or name == "-" or name == "名稱" or "售店" in name:
                continue
                
            level = int(level_match.group())
            
            if "453316" in url:
                prev_element = table.find_previous(["h2", "h3", "h4", "p"])
                if prev_element:
                    prev_text = prev_element.get_text().strip()
                    for t in ["劍", "斧", "槍", "杖", "弓", "投擲武器", "小刀", "迴力鏢", "盾牌", "衣服", "帽子", "頭盔", "鎧甲", "長袍", "鞋子", "靴子"]:
                        if t in prev_text:
                            current_type = t
                            break

            search_zone = items[idx_mat_title + 3:]
            mat_names = []
            mat_qtys = []
            
            for part in search_zone:
                if any(k in part for k in ["防禦", "抗魔", "售店", "攻擊", "命中", "閃躲", "性能", "配方", "效果", "說明", "負重"]) or part.endswith("G") or "+" in part or "~" in part:
                    continue
                if part.isdigit():
                    mat_qtys.append(int(part))
                elif len(part) >= 1 and not part.isdigit():
                    mat_names.append(part)
            
            materials_dict = {}
            for i in range(min(len(mat_names), len(mat_qtys))):
                m_name = mat_names[i].strip()
                if m_name and m_name not in ["x", "X", "個", "R", "-", "—"]:
                    materials_dict[m_name] = mat_qtys[i]
            
            if materials_dict:
                page_equipments.append({
                    "category": category,
                    "type": current_type,
                    "level": level,
                    "name": name,
                    "materials": materials_dict,
                    "note": f"R{level} {current_type}"
                })
                
        except Exception:
            continue
            
    print(f" ✅ 成功解碼 {len(page_equipments)} 件項目！")
    return page_equipments

def main():
    items = parse_page()
    for idx, item in enumerate(items, 1):
        item["id"] = idx
        
    equipments_json = json.dumps(items, ensure_ascii=False, indent=2)
    js_content = f"window.equipments = {equipments_json};"
    
    output_path = CONFIG["output_js"]
    
    dir_name = os.path.dirname(output_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name)
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"💾 資料已寫入 {output_path}\\n")

if __name__ == "__main__":
    main()
"""

def generate():
    output_dir = "spiders"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 已建立資料夾: {output_dir}")

    print("🛠️ 開始產生獨立爬蟲檔案...")
    
    for t in targets:
        page_id = t["url"].split("/")[-1]
        file_name = f"spy_{page_id}_{t['suffix']}.py"
        file_path = os.path.join(output_dir, file_name)
        
        output_js = f"data/data_{t['suffix']}.js"
        
        file_content = (SPIDER_TEMPLATE
                        .replace("__TARGET_URL__", t["url"])
                        .replace("__TARGET_CATEGORY__", t["category"])
                        .replace("__TARGET_TYPE__", t["type"])
                        .replace("__TARGET_OUTPUT_JS__", output_js))
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(file_content)
            
        print(f"  ✅ 已生成: {file_path} -> 預設對應 {output_js}")

    print(f"\n🎉 大功告成！總共建立了 {len(targets)} 個獨立爬蟲。")

if __name__ == "__main__":
    generate()