import os
import sys
import time
import importlib.util

def get_spider_info_safely(file_path):
    """安全且精準地直接載入爬蟲檔內的 CONFIG，杜絕正則表達式失敗的問題"""
    try:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "CONFIG"):
            cfg = module.CONFIG
            return f"[{cfg.get('category', '未知')} - {cfg.get('type', '未知')}]"
        return "[無CONFIG設定]"
    except Exception:
        return "[讀取模組失敗]"

def load_and_run_spider(file_path):
    """動態載入並執行爬蟲模組"""
    module_name = os.path.splitext(os.path.basename(file_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main()

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    spider_dir = "spiders"
    data_dir = "data"

    if not os.path.exists(spider_dir):
        print(f"❌ 找不到 '{spider_dir}' 資料夾，請先執行 generate_spiders.py！")
        return

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    files = [f for f in os.listdir(spider_dir) if f.startswith("spy_") and f.endswith(".py")]
    files.sort()

    if not files:
        print(f"ℹ️ '{spider_dir}' 資料夾內沒有任何 spy_ 開頭的爬蟲檔案。")
        return

    print("====================================")
    print("      魔力寶貝 爬蟲自動化主控台      ")
    print("====================================")
    print(" 1. 執行所有爬蟲 (全部重新抓取並分流到 data/)")
    print(" 2. 執行單一爬蟲 (適合微調測試)")
    print(" 3. 離開程式")
    print("------------------------------------")
    
    choice = input("👉 請選擇功能編號: ").strip()

    if choice == "1":
        print(f"\n🚀 準備開始執行全部共 {len(files)} 個爬蟲任務...")
        start_time = time.time()
        
        for idx, file in enumerate(files, 1):
            file_path = os.path.join(spider_dir, file)
            info = get_spider_info_safely(file_path)
            print(f"\n 🎬 [{idx}/{len(files)}] 正在啟動 {file} {info}")
            
            try:
                load_and_run_spider(file_path)
            except Exception as e:
                print(f" 💥 錯誤：執行 {file} 時發生崩潰: {e}")
                
            time.sleep(1.5)
            
        end_time = time.time()
        print(f"\n🎉 任務全數完成！總耗時: {end_time - start_time:.2f} 秒。資料已全部儲存於 {data_dir}/ 目錄。")

    elif choice == "2":
        print("\n🔍 正在讀取爬蟲設定，請選擇要微調的項目：")
        print("------------------------------------")
        
        menu_items = []
        for idx, file in enumerate(files, 1):
            file_path = os.path.join(spider_dir, file)
            info = get_spider_info_safely(file_path)
            menu_items.append((file_path, file, info))
            print(f" [{idx:02d}] {info:<15} -> {file}")
            
        print("------------------------------------")
        try:
            sel = input("👉 請輸入要執行的編號 (或按 Enter 取消): ").strip()
            if not sel:
                print("👋 已取消操作。")
                return
                
            sel_idx = int(sel) - 1
            if 0 <= sel_idx < len(menu_items):
                target_path, target_file, target_info = menu_items[sel_idx]
                print(f"\n🚀 單獨啟動：{target_file} {target_info}")
                
                load_and_run_spider(target_path)
                print("🏁 單一爬蟲測試完畢！")
            else:
                print("❌ 錯誤：輸入的編號超出範圍！")
        except ValueError:
            print("❌ 錯誤：請輸入正確的數字編號！")
            
    elif choice == "3":
        print("👋 感謝使用，再見！")
        return
    else:
        print("❌ 無效的選擇，請重新執行程式。")

if __name__ == "__main__":
    main()