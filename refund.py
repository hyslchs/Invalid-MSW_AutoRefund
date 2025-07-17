import time
import pickle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def process_refunds(status_callback):
    """
    Logs in and processes refunds for orders listed in 'marked_order_id.txt'.
    """
    driver = None
    try:
        # --- 1. 初始化瀏覽器並載入 Cookies ---
        status_callback("正在初始化瀏覽器...")
        options = Options()
        options.add_argument("--start-maximized")
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        status_callback("正在開啟目標網站並載入 Cookies...")
        driver.get("https://maplestoryworlds.nexon.com")
        time.sleep(2)

        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            if "sameSite" in cookie:
                del cookie["sameSite"]
            if "expiry" in cookie:
                cookie["expires"] = cookie["expiry"]
            driver.add_cookie(cookie)

        driver.refresh()
        time.sleep(3)
        status_callback("✅ Cookies 已載入，登入成功！")

        # --- 2. 讀取待退款的訂單ID ---
        status_callback("正在讀取 marked_order_id.txt...")
        try:
            with open('marked_order_id.txt', 'r', encoding='utf-8') as f:
                # 只讀取包含 '※' 的行，並去除 '※ ' 前綴
                ids = [line.strip().replace('※ ', '') for line in f if line.strip().startswith('※')]
        except FileNotFoundError:
            status_callback("❌ 錯誤：找不到 marked_order_id.txt 檔案！")
            return

        if not ids:
            status_callback("⚠️ 在 marked_order_id.txt 中沒有找到需要退款的訂單 (沒有以 '※' 標記的訂單)。")
            return

        # --- 3. 執行退款流程 ---
        status_callback(f"找到 {len(ids)} 筆需要退款的訂單，開始處理...")
        base_url = "https://maplestoryworlds.nexon.com/zh-tw/coin/history?type=earning&page=1&startDate=2025-06-04&endDate=2025-07-16&searchCategory=O&searchKeyword="

        for i, order_id in enumerate(ids, start=1):
            url = base_url + order_id
            status_callback(f"[{i}/{len(ids)}] 正在處理訂單 {order_id}...")
            driver.get(url)

            try:
                # 點擊詳情
                detail_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "btn_detail"))
                )
                detail_button.click()
                WebDriverWait(driver, 10).until(EC.url_contains("/coin/history/detail"))
                status_callback(f"  ✅ 成功進入訂單 {order_id} 的詳情頁面")
                time.sleep(1)

                # 點擊退款
                refund_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "button_status"))
                )
                refund_button.click()
                status_callback("    ✅ 已點擊『退款』按鈕")

                # 點擊確認
                confirm_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((
                        By.XPATH, '//button[contains(@class, "fill--bk") and .//span[contains(text(), "確認")]]'
                    ))
                )
                confirm_button.click()
                status_callback("    ✅ 已點擊『確認』按鈕，退款成功！")
                time.sleep(1)

            except Exception as e:
                status_callback(f"  ❌ 處理訂單 {order_id} 時發生錯誤: {e}")

    except FileNotFoundError:
        status_callback("❌ 錯誤：找不到 cookies.pkl 檔案！請先執行第一步取得 Cookie。")
    except Exception as e:
        status_callback(f"❌ 發生未預期的錯誤: {e}")
    finally:
        if driver:
            driver.quit()
        status_callback("✅ 所有退款任務完成，瀏覽器已關閉。")

if __name__ == '__main__':
    def print_status(message):
        print(message)
    process_refunds(print_status)