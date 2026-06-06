import os
import re
import json
import requests
from bs4 import BeautifulSoup

# ==================== 每個檔案獨有的設定區 ====================
CONFIG = {
    "url": "https://gamerch.com/blue-cg/453323",
    "category": "防具",
    "type": "鞋子",
    "output_js": "data/data_shoes.js"
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
    print(f"💾 資料已寫入 {output_path}\n")

if __name__ == "__main__":
    main()
