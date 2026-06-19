import json
import re

import json
import re

def load_js_array(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 修改重點：匹配 window.equipments = [...]
    match = re.search(r"window\.equipments\s*=\s*(\[.*\])\s*;", content, re.DOTALL)

    if not match:
        raise Exception(f"找不到陣列資料，請檢查檔案格式: {file_path}")

    return json.loads(match.group(1))

def save_js_array(file_path, data):
    # 修改重點：存檔時補上 window.equipments = 
    content = (
        "window.equipments = "
        + json.dumps(data, ensure_ascii=False, indent=2)
        + ";\n"
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# run_batch_hacks 的邏輯保持不變即可

def run_batch_hacks(config_file):
    # 讀取你的設定 JSON
    with open(config_file, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    # 為了避免重複讀寫同一個檔案，我們可以先把要修改的分類存好
    # 這裡簡化流程：直接遍歷執行
    for task in tasks:
        file = task.pop("file") # 取出目標檔案路徑
        print(f"\n正在處理檔案: {file}")
        
        # 讀取 JS 資料
        data = load_js_array(file)
        
        # 區分條件與要修改的內容
        patch_fields = {"materials", "note", "level", "id"}
        condition = {k: v for k, v in task.items() if k not in patch_fields}
        patch = {k: v for k, v in task.items() if k in patch_fields}
        
        found = False
        for item in data:
            if all(item.get(k) == v for k, v in condition.items()):
                item.update(patch)
                found = True
                print(f"  -> 已修改: {item.get('name', 'Unknown')}")
        
        if found:
            save_js_array(file, data)
        else:
            print("  -> 找不到符合條件的資料")

if __name__ == "__main__":
    # 一口氣執行所有定義在 JSON 裡的修改
    run_batch_hacks("patch_config.json")
