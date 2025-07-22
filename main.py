import time
import pickle
import math
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import urllib.parse

def mark_orders(start_page, end_page, start_date, end_date, status_callback):
    """
    Logs in, fetches order details, and marks specific orders.
    """
    driver = None
    try:
        # --- 1. 初始化瀏覽器並載入 Cookies ---
        status_callback("--- 開始執行第二步：抓取與標記訂單 ---")
        status_callback("正在初始化瀏覽器...")
        options = Options()
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        status_callback("正在開啟目標網站並載入 Cookies...")
        driver.get("https://maplestoryworlds.nexon.com")
        time.sleep(2)

        try:
            with open("cookies.pkl", "rb") as f:
                cookies = pickle.load(f)
        except FileNotFoundError:
            status_callback("❌ 錯誤：找不到 cookies.pkl 檔案！請先執行第一步取得 Cookie。")
            return

        for cookie in cookies:
            if "sameSite" in cookie:
                del cookie["sameSite"]
            if "expiry" in cookie:
                cookie["expires"] = cookie["expiry"]
            driver.add_cookie(cookie)

        driver.refresh()
        time.sleep(3)
        status_callback("✅ Cookies 已載入，登入成功！")

        # --- 2. 根據 buyer.txt 抓取特定買家的訂單編號 ---
        status_callback("\n--- 正在抓取特定買家訂單 ---")
        try:
            with open("buyer.txt", "r", encoding="utf-8") as f:
                buyer_ids = [line.strip() for line in f if line.strip()]
            status_callback(f"在 buyer.txt 中找到 {len(buyer_ids)} 位買家。")
        except FileNotFoundError:
            status_callback("❌ 錯誤：找不到 buyer.txt 檔案！請在程式目錄下建立此檔案。")
            return

        order_numbers = []
        base_url = "https://maplestoryworlds.nexon.com/zh-tw/coin/history"
        query_template = f"?type=earning&page=1&startDate={start_date}&endDate={end_date}&searchCategory=B&searchKeyword="

        for i, buyer_id in enumerate(buyer_ids, 1):
            encoded_id = urllib.parse.quote(buyer_id)
            full_url = base_url + query_template + encoded_id
            status_callback(f"({i}/{len(buyer_ids)}) 正在搜尋買家: {buyer_id}")
            driver.get(full_url)
            time.sleep(3) # 等待頁面載入

            try:
                elements = driver.find_elements(By.CLASS_NAME, "txt_order_number")
                if not elements:
                    status_callback(f"  -> ⚠️ {buyer_id} 在指定日期範圍內查無訂單。")
                else:
                    for el in elements:
                        order_num = el.text.strip()
                        order_numbers.append(order_num)
                        status_callback(f"  -> ✅ 成功抓取訂單: {order_num}")
            except Exception as e:
                status_callback(f"  -> ❌ 抓取時發生錯誤: {e}")

        with open("buyer's_order_id.txt", "w", encoding="utf-8") as f:
            for num in order_numbers:
                f.write(num + "\n")
        status_callback(f"✅ 特定買家訂單已全部寫入 buyer's_order_id.txt (共 {len(order_numbers)} 筆)")

        # --- 3. 抓取指定頁數範圍內的所有訂單編號 ---
        status_callback(f"\n--- 正在抓取第 {start_page} 到 {end_page} 頁的所有訂單 ---")
        driver.get(f"https://maplestoryworlds.nexon.com/zh-tw/coin/history?type=earning&page=1&startDate={start_date}&endDate={end_date}")
        wait = WebDriverWait(driver, 10)

        with open("all_order_id.txt", "w", encoding="utf-8") as output_file:
            # ... (click_page 和 click_next_arrow 函數維持不變) ...
            def click_page(page_num):
                try:
                    xpath = f'//ul[contains(@class, "list_page")]//a[text()="{page_num}"]'
                    page_btn = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                    page_btn.click()
                    status_callback(f"  成功點擊分頁 {page_num}")
                    time.sleep(2)
                    
                    order_elems = driver.find_elements(By.CLASS_NAME, "txt_order_number")
                    page_orders = [elem.text.strip() for elem in order_elems if elem.text.strip()]
                    
                    output_file.write(f"-- 第 {page_num} 頁 --\n")
                    for num in page_orders:
                        output_file.write(num + "\n")
                    status_callback(f"    -> 📦 第 {page_num} 頁抓到 {len(page_orders)} 筆訂單")
                    return True
                except Exception as e:
                    status_callback(f"  -> ❌ 點擊分頁 {page_num} 失敗: {e}")
                    return False

            def click_next_arrow():
                try:
                    next_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn__paging.btn_next")))
                    next_btn.click()
                    status_callback("  ➡️ 正在翻頁...")
                    time.sleep(2)
                    return True
                except:
                    status_callback("  ⛔ 無法再往下翻頁。")
                    return False

            target_group = math.ceil(start_page / 5)
            if start_page > 5:
              status_callback(f"正在跳轉至目標頁碼 {start_page} 附近...")
              for _ in range(1, target_group):
                  if not click_next_arrow():
                      raise Exception("無法移動到目標分頁群組")

            for i in range(start_page, end_page + 1):
                if not click_page(i):
                    break
                if i % 5 == 0 and i < end_page:
                    if not click_next_arrow():
                        break
        
        status_callback(f"✅ 已完成第 {start_page} ~ {end_page} 頁的資料擷取")

        # --- 4. 比對並標記訂單 ---
        status_callback("\n--- 正在進行訂單比對與標記 ---")
        with open("buyer's_order_id.txt", "r", encoding="utf-8") as f:
            target_ids = set(line.strip() for line in f if line.strip())

        marked_count = 0
        output_lines = []
        with open("all_order_id.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("-- 第"):
                    output_lines.append(line)
                elif line and line in target_ids:
                    output_lines.append(f"※ {line}")
                    marked_count += 1
                else:
                    output_lines.append(line)
        
        with open("marked_order_id.txt", "w", encoding="utf-8") as f:
            for line in output_lines:
                f.write(line + "\n")
        
        status_callback(f"✅ 已完成比對，共標記了 {marked_count} 筆訂單。")
        status_callback("   結果已輸出至 marked_order_id.txt")

    except Exception as e:
        status_callback(f"❌ 發生未預期的錯誤: {e}")
    finally:
        if driver:
            driver.quit()
        status_callback("\n✅ 第二步任務完成，瀏覽器已關閉。")

if __name__ == '__main__':
    def print_status(message):
        print(message)
    
    START_PAGE = 1
    END_PAGE = 2 
    START_DATE = "2025-06-04"
    END_DATE = "2025-07-16"
    mark_orders(START_PAGE, END_PAGE, START_DATE, END_DATE, print_status)