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
    
    # 網頁內的動態類型識別
    current_type = default_type

    for table in tables:
        # 將表格內的所有 td, th 轉成純文字陣列
        items = [td.get_text().strip() for td in table.find_all(["td", "th"]) if td.get_text().strip()]
        
        # 檢查是否為標準裝備方塊表格
        if "等級" not in items or "名稱" not in items or "所需材料" not in items:
            continue
            
        try:
            # 定位關鍵標題位置
            idx_mat_title = items.index("所需材料")
            
            # 提取名稱與等級
            name = items[idx_mat_title + 2] 
            level_str = items[idx_mat_title + 1]
            level_match = re.search(r"\d+", level_str)
            if not level_match or not name or name == "-" or name == "名稱" or "售店" in name:
                continue
                
            level = int(level_match.group())
            
            # 聰明的動態分類：如果在這個裝備表格前看見大標題，就更新當前裝備種類
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
                # 遇到結尾區塊（屬性字眼或價格）就停下來
                if any(k in part for k in ["防禦", "抗魔", "售店", "攻擊", "命中", "閃躲", "性能", "配方"]) or part.endswith("G") or "+" in part or "~" in part:
                    break
                
                # 分流名字與數量
                if part.isdigit():
                    mat_qtys.append(int(part))
                elif len(part) > 1 and not part.isdigit():
                    mat_names.append(part)
            
            # 一對一精準疊加配對
            materials_dict = {}
            for i in range(min(len(mat_names), len(mat_qtys))):
                m_name = mat_names[i].strip()
                if m_name and m_name not in ["x", "X", "個", "R", "-", "—"]:
                    materials_dict[m_name] = mat_qtys[i]
            
            # 封裝成品
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
            continue # 個別異常表格直接跳過
            
    print(f"  ✅ 成功解碼 {len(page_equipments)} 件裝備！")
    return page_equipments

def main():
    # 所有的目標網址大集合
    targets = [
        # 防具類 (Gamerch 453316 網頁包山包海，所以 default 設防具，程式內會自動細分)
        {"url": "https://gamerch.com/blue-cg/453316", "category": "防具", "type": "盾牌"},
        {"url": "https://gamerch.com/blue-cg/453317", "category": "防具", "type": "衣服"},
        {"url": "https://gamerch.com/blue-cg/453318", "category": "防具", "type": "帽子"},
        {"url": "https://gamerch.com/blue-cg/453319", "category": "防具", "type": "頭盔"},
        {"url": "https://gamerch.com/blue-cg/453320", "category": "防具", "type": "鎧甲"},
        {"url": "https://gamerch.com/blue-cg/453321", "category": "防具", "type": "長袍"},
        {"url": "https://gamerch.com/blue-cg/453322", "category": "防具", "type": "鞋子"},
        {"url": "https://gamerch.com/blue-cg/453323", "category": "防具", "type": "靴子"},
        # 武器類
        {"url": "https://gamerch.com/blue-cg/453302", "category": "武器", "type": "劍"},
        {"url": "https://gamerch.com/blue-cg/453303", "category": "武器", "type": "斧"},
        {"url": "https://gamerch.com/blue-cg/453304", "category": "武器", "type": "矛"},
        {"url": "https://gamerch.com/blue-cg/453305", "category": "武器", "type": "杖"},
        {"url": "https://gamerch.com/blue-cg/453306", "category": "武器", "type": "弓"},
        {"url": "https://gamerch.com/blue-cg/453307", "category": "武器", "type": "投擲武器"},
        {"url": "https://gamerch.com/blue-cg/453308", "category": "武器", "type": "小刀"},
    ]

    all_equipments = []
    item_id = 1
    
    for t in targets:
        items = parse_gamerch_bizarre_page(t["url"], t["category"], t["type"])
        for item in items:
            item["id"] = item_id
            all_equipments.append(item)
            item_id += 1
        time.sleep(1.5) # 溫柔爬取，避免被網站封鎖

    # 輸出成 data.js 供前端網頁直接使用
    equipments_json = json.dumps(all_equipments, ensure_ascii=False, indent=2)
    js_content = f"const equipments = {equipments_json};"
    
    with open("data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"\n🎉 ===========================================")
    print(f"   【全自動裝備資料庫更新完成】")
    print(f"   🚀 總共成功解碼 {len(all_equipments)} 件裝備配方！")
    print(f"   💾 資料已完美覆寫到 data.js，快去重整網頁看看吧！")
    print(f"==============================================")

if __name__ == "__main__":
    main()