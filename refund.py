# -*- coding: utf-8 -*-
"""
此腳本為自動退款機器人的核心部分，專門用於執行退款操作。

主要功能：
1.  初始化 Selenium WebDriver。
2.  讀取儲存的 Cookies 檔案，自動登入目標網站。
3.  讀取標記好的訂單編號檔案 (`marked_order_id.txt`)。
4.  遍歷所有需要退款的訂單，並在網頁上自動執行點擊「退款」和「確認」的動作。
5.  詳細記錄所有操作過程、成功與失敗的日誌，並將日誌同時輸出到檔案 (`refund_log.txt`) 和控制台。

使用方式：
-   此腳本通常由主應用程式 (app.py) 調用。
-   也可以獨立執行，此時日誌和狀態更新會直接打印到控制台。
"""

import time
import pickle
import logging
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

# 全局日誌記錄器
logger = logging.getLogger(__name__)

def setup_logging():
    """
    設定日誌記錄器，使其能夠同時將日誌輸出到檔案和控制台。
    檔案日誌會以覆寫模式寫入 `refund_log.txt`。
    """
    # 防止重複添加 handler
    if logger.hasHandlers():
        return

    logger.setLevel(logging.INFO)

    # 檔案日誌處理器：記錄所有 INFO 等級以上的日誌
    # 使用 'w' 模式，每次執行都會建立新的日誌檔案
    file_handler = logging.FileHandler('refund_log.txt', 'w', 'utf-8')
    file_handler.setLevel(logging.INFO)

    # 控制台日誌處理器：同樣記錄 INFO 等級以上的日誌
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # 定義日誌輸出的格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 將處理器加入 logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

def create_driver():
    """
    建立並返回一個設定好的 Chrome WebDriver 實例。

    Returns:
        webdriver.Chrome: 設定好的 WebDriver 實例。
    """
    logger.info("正在初始化 Chrome 瀏覽器...")
    options = Options()
    options.add_argument("--start-maximized")  # 瀏覽器視窗最大化
    # options.add_argument('--headless')  # 如果需要在背景執行，可以取消註解此行
    try:
        driver = webdriver.Chrome(options=options)
        return driver
    except WebDriverException as e:
        logger.error(f"初始化 Chrome Driver 失敗，請確認 chromedriver.exe 是否存在且版本相容: {e}")
        return None

def login_with_cookies(driver):
    """
    使用儲存的 cookies.pkl 檔案自動登入網站。

    Args:
        driver (webdriver.Chrome): WebDriver 實例。

    Returns:
        bool: 如果成功登入返回 True，否則返回 False。
    """
    try:
        logger.info("正在開啟目標網站並載入 Cookies...")
        driver.get("https://maplestoryworlds.nexon.com")
        time.sleep(2)  # 等待頁面基本載入

        with open("cookies.pkl", "rb") as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            # 移除 Selenium 不支援的 'sameSite' 屬性
            if "sameSite" in cookie:
                del cookie["sameSite"]
            driver.add_cookie(cookie)

        driver.refresh()  # 刷新頁面以套用 Cookie
        time.sleep(3)  # 等待登入狀態生效
        logger.info("Cookies 已成功載入，模擬登入完成！")
        return True
    except FileNotFoundError:
        logger.error("找不到 cookies.pkl 檔案！請先執行第一步以產生 Cookie 檔案。")
        return False
    except Exception as e:
        logger.error(f"載入 Cookies 或登入時發生未預期的錯誤: {e}", exc_info=True)
        return False

def get_order_ids_from_file(file_path='marked_order_id.txt'):
    """
    從指定的檔案中讀取並解析需要退款的訂單 ID。
    僅選取未以 '※' 或 '--' 開頭的行（表示要退款的訂單）。
    """
    logger.info(f"正在從 {file_path} 讀取待退款的訂單編號...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            order_ids = [
                line.strip()
                for line in f
                if line.strip() and not line.strip().startswith('※') and not line.strip().startswith('--')
            ]
        return order_ids
    except FileNotFoundError:
        logger.error(f"找不到訂單檔案: {file_path}！")
        return None

def process_single_order(driver, order_id, status_callback, index, total):
    """
    處理單一訂單的退款流程。

    Args:
        driver (webdriver.Chrome): WebDriver 實例。
        order_id (str): 要處理的訂單 ID。
        status_callback (function): 用於更新 UI 狀態的回調函式。
        index (int): 目前處理的訂單序號。
        total (int): 總訂單數。
    """
    base_url = "https://maplestoryworlds.nexon.com/zh-tw/coin/history?type=earning&page=1&startDate=2025-06-04&endDate=2025-07-16&searchCategory=O&searchKeyword="
    search_url = base_url + order_id

    log_msg = f"[{index}/{total}] 正在處理訂單 {order_id}... "
    logger.info(log_msg)
    status_callback(log_msg)
    driver.get(search_url)

    try:
        # 1. 點擊「詳情」按鈕
        detail_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "btn_detail"))
        )
        detail_button.click()
        WebDriverWait(driver, 10).until(EC.url_contains("/coin/history/detail"))
        logger.info(f"  - 成功進入訂單 {order_id} 的詳情頁面。")
        status_callback(f"  ✅ 成功進入訂單 {order_id} 的詳情頁面")
        time.sleep(1)  # 等待頁面穩定

        # 2. 點擊「退款」按鈕
        refund_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "button_status"))
        )
        refund_button.click()
        logger.info(f"  - 已點擊訂單 {order_id} 的『退款』按鈕。")
        status_callback("    ✅ 已點擊『退款』按鈕")

        # 檢查是否出現錯誤彈窗（例如『失敗』）
        try:
            error_modal = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "modal-header"))
            )
            if error_modal.text.strip() == "失敗":
                error_msg = f"    ⚠️ 訂單 {order_id} 無法退款（彈出『失敗』視窗）"
                logger.warning(error_msg)
                status_callback(error_msg)
                return  # 不再進行確認按鈕流程
        except TimeoutException:
            pass  # 沒出現視窗就繼續往下執行

        # 3. 在彈出視窗中點擊「確認」按鈕
        confirm_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((
                By.XPATH, '//button[contains(@class, "fill--bk") and .//span[contains(text(), "確認")]]'
            ))
        )
        confirm_button.click()
        logger.info(f"  - 已點擊『確認』按鈕，訂單 {order_id} 退款成功！")
        status_callback("    ✅ 已點擊『確認』按鈕，退款成功！")
        time.sleep(1)  # 等待操作完成

    except TimeoutException:
        error_msg = f"  - 處理訂單 {order_id} 時發生超時錯誤，可能是頁面元素未在預期時間內出現。"
        logger.error(error_msg)
        status_callback(f"  ❌ 處理訂單 {order_id} 時發生超時錯誤")
    except NoSuchElementException:
        error_msg = f"  - 處理訂單 {order_id} 時找不到頁面元素，可能是頁面結構已改變。"
        logger.error(error_msg)
        status_callback(f"  ❌ 處理訂單 {order_id} 時找不到頁面元素")
    except Exception as e:
        error_msg = f"  - 處理訂單 {order_id} 時發生未預期錯誤: {e}"
        logger.error(error_msg, exc_info=True)
        status_callback(f"  ❌ 處理訂單 {order_id} 時發生錯誤: {e}")

def process_refunds(status_callback):
    """
    執行完整的退款流程，包括登入、讀取訂單和處理退款。

    Args:
        status_callback (function): 一個函式，用於將狀態更新傳遞到呼叫者 (例如 GUI)。
                                      它接受一個字串參數。
    """
    setup_logging()  # 確保日誌已設定
    driver = None
    try:
        # --- 步驟 1: 初始化瀏覽器並登入 ---
        status_callback("正在初始化瀏覽器...")
        driver = create_driver()
        if not driver:
            status_callback("❌ 錯誤：瀏覽器初始化失敗，請檢查日誌。")
            return

        status_callback("正在使用 Cookie 進行登入...")
        if not login_with_cookies(driver):
            status_callback("❌ 錯誤：使用 Cookie 登入失敗，請檢查日誌。")
            return
        status_callback("✅ 登入成功！")

        # --- 步驟 2: 讀取待退款的訂單 ID ---
        status_callback("正在讀取待退款訂單列表...")
        order_ids = get_order_ids_from_file()

        if order_ids is None:
            status_callback("❌ 錯誤：找不到 marked_order_id.txt 檔案！")
            return

        if not order_ids:
            logger.warning("在 marked_order_id.txt 中沒有找到需要退款的訂單 (沒有以 '※' 標記的訂單)。")
            status_callback("⚠️ 沒有找到需要退款的訂單。")
            return

        # --- 步驟 3: 執行退款流程 ---
        total_orders = len(order_ids)
        logger.info(f"找到 {total_orders} 筆需要退款的訂單，開始處理...")
        status_callback(f"找到 {total_orders} 筆訂單，開始退款流程...")

        for i, order_id in enumerate(order_ids, start=1):
            process_single_order(driver, order_id, status_callback, i, total_orders)

    except Exception as e:
        logger.error(f"在主流程中發生未預期的嚴重錯誤: {e}", exc_info=True)
        status_callback(f"❌ 發生未預期的嚴重錯誤: {e}")
    finally:
        if driver:
            driver.quit()
        logger.info("所有退款任務處理完畢，瀏覽器已關閉。")
        status_callback("✅ 所有退款任務完成！")


if __name__ == '__main__':
    """
    當此腳本被直接執行時的進入點。
    主要用於開發和測試，可以直接在終端機中看到執行過程。
    """
    # 定義一個簡單的回調函式，直接將狀態訊息打印到控制台
    def console_status_callback(message):
        print(message)

    print("腳本以獨立模式啟動...")
    process_refunds(console_status_callback)
    print("腳本執行完畢。")