import os
import re
import json
import time
import requests
from bs4 import BeautifulSoup

def parse_gamerch_bizarre_page(url, category, default_type):
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
    
    # 這裡固定使用我們在 targets 裡指定好的精確種類，不再依賴網頁隨機的標題
    current_type = default_type

    for table in tables:
        items = [td.get_text().strip() for td in table.find_all(["td", "th"]) if td.get_text().strip()]
        
        if "等級" not in items or "名稱" not in items or "所需材料" not in items:
            continue
            
        try:
            idx_mat_title = items.index("所需材料")
            
            # 提取名稱與等級
            name = items[idx_mat_title + 2] 
            level_str = items[idx_mat_title + 1]
            level_match = re.search(r"\d+", level_str)
            if not level_match or not name or name == "-" or name == "名稱" or "售店" in name:
                continue
                
            level = int(level_match.group())
            
            # 【特別防呆】如果是原本防具大合集的網頁 (453316)，內部再做一次細分
            if "453316" in url:
                prev_element = table.find_previous(["h2", "h3", "h4", "p"])
                if prev_element:
                    prev_text = prev_element.get_text().strip()
                    for t in ["劍", "斧", "矛", "杖", "弓", "投擲武器", "小刀", "迴力鏢", "盾牌", "衣服", "帽子", "頭盔", "鎧甲", "長袍", "鞋子", "靴子"]:
                        if t in prev_text:
                            current_type = t
                            break

            # 從「所需材料」後面切出資料區塊進行解碼
            search_zone = items[idx_mat_title + 3:]
            mat_names = []
            mat_qtys = []
            
            for part in search_zone:
                if any(k in part for k in ["防禦", "抗魔", "售店", "攻擊", "命中", "閃躲", "性能", "配方", "效果", "說明"]) or part.endswith("G") or "+" in part or "~" in part:
                    break
                
                if part.isdigit():
                    mat_qtys.append(int(part))
                elif len(part) > 1 and not part.isdigit():
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
            
    print(f"  ✅ 成功解碼 {len(page_equipments)} 件項目！")
    return page_equipments

def main():
    targets = [
        # === 原有的防具類 ===
        {"url": "https://gamerch.com/blue-cg/453316", "category": "防具", "type": "盾牌"}, # 這頁會自適應細分
        {"url": "https://gamerch.com/blue-cg/453317", "category": "防具", "type": "衣服"},
        {"url": "https://gamerch.com/blue-cg/453318", "category": "防具", "type": "帽子"},
        {"url": "https://gamerch.com/blue-cg/453319", "category": "防具", "type": "頭盔"},
        {"url": "https://gamerch.com/blue-cg/453320", "category": "防具", "type": "鎧甲"},
        {"url": "https://gamerch.com/blue-cg/453321", "category": "防具", "type": "長袍"},
        {"url": "https://gamerch.com/blue-cg/453322", "category": "防具", "type": "鞋子"},
        {"url": "https://gamerch.com/blue-cg/453323", "category": "防具", "type": "靴子"},
        
        # === 原有的武器類 ===
        {"url": "https://gamerch.com/blue-cg/453302", "category": "武器", "type": "劍"},
        {"url": "https://gamerch.com/blue-cg/453303", "category": "武器", "type": "斧"},
        {"url": "https://gamerch.com/blue-cg/453304", "category": "武器", "type": "矛"},
        {"url": "https://gamerch.com/blue-cg/453305", "category": "武器", "type": "杖"},
        {"url": "https://gamerch.com/blue-cg/453306", "category": "武器", "type": "弓"},
        {"url": "https://gamerch.com/blue-cg/453307", "category": "武器", "type": "投擲武器"},
        {"url": "https://gamerch.com/blue-cg/453308", "category": "武器", "type": "小刀"},
        
        # === 寵物裝備系列：依網址精準鎖定種類 ===
        {"url": "https://guide.bluecg.net/blue-cg/453587", "category": "寵物裝備", "type": "寵物晶石"},
        {"url": "https://guide.bluecg.net/blue-cg/453588", "category": "寵物裝備", "type": "寵物飾品"},
        {"url": "https://guide.bluecg.net/blue-cg/453589", "category": "寵物裝備", "type": "寵物項圈"},
        {"url": "https://guide.bluecg.net/blue-cg/453590", "category": "寵物裝備", "type": "寵物重裝"},
        {"url": "https://guide.bluecg.net/blue-cg/453591", "category": "寵物裝備", "type": "寵物輕裝"},
        
        # === 其他道具系列：依網址精準鎖定種類 ===
        {"url": "https://guide.bluecg.net/blue-cg/453290", "category": "其他", "type": "料理"},
        {"url": "https://guide.bluecg.net/blue-cg/453291", "category": "其他", "type": "藥水"},
        {"url": "https://guide.bluecg.net/blue-cg/453267", "category": "其他", "type": "飾品"},
        {"url": "https://guide.bluecg.net/blue-cg/453256", "category": "其他", "type": "外傷藥"},
        {"url": "https://guide.bluecg.net/blue-cg/453262", "category": "其他", "type": "療傷藥"},
        {"url": "https://guide.bluecg.net/blue-cg/453257", "category": "其他", "type": "炸彈"},
        {"url": "https://guide.bluecg.net/blue-cg/452830", "category": "其他", "type": "變身卡"}
    ]

    all_equipments = []
    item_id = 1
    
    for t in targets:
        items = parse_gamerch_bizarre_page(t["url"], t["category"], t["type"])
        for item in items:
            item["id"] = item_id
            all_equipments.append(item)
            item_id += 1
        time.sleep(1.5)

    equipments_json = json.dumps(all_equipments, ensure_ascii=False, indent=2)
    js_content = f"const equipments = {equipments_json};"
    
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"\n🎉 完美對齊！共解碼 {len(all_equipments)} 件項目，資料已匯入 data.js！")

if __name__ == "__main__":
    main()
