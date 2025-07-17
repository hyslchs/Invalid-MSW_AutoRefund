import time
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class CookieManager:
    def __init__(self, status_callback):
        """
        Initializes the CookieManager.
        Args:
            status_callback: A function to call to update the GUI status.
        """
        self.driver = None
        self.status_callback = status_callback

    def start_login(self):
        """
        Opens a browser for the user to log in.
        """
        try:
            if self.driver:
                self.status_callback("⚠️ 瀏覽器已經開啟。")
                return

            self.status_callback("正在初始化瀏覽器...")
            options = Options()
            self.driver = webdriver.Chrome(options=options)
            self.status_callback("正在開啟登入頁面...")
            self.driver.get("https://maplestoryworlds.nexon.com")
            self.status_callback("✅ 瀏覽器已開啟。請手動登入。")
            self.status_callback("   登入完成後，請點擊主程式的「儲存Cookie並關閉」按鈕。")
        except Exception as e:
            self.status_callback(f"❌ 開啟瀏覽器時發生錯誤: {e}")
            if self.driver:
                self.driver.quit()
                self.driver = None

    def save_cookies_and_quit(self):
        """
        Saves cookies from the currently open browser and then closes it.
        """
        if not self.driver:
            self.status_callback("❌ 錯誤：瀏覽器尚未開啟。請先點擊「開啟瀏覽器登入」。")
            return

        try:
            self.status_callback("正在儲存 Cookies...")
            cookies = self.driver.get_cookies()
            with open("cookies.pkl", "wb") as f:
                pickle.dump(cookies, f)
            self.status_callback("✅ Cookies 已成功儲存至 cookies.pkl！")
        except Exception as e:
            self.status_callback(f"❌ 儲存 Cookies 時發生錯誤: {e}")
        finally:
            if self.driver:
                self.status_callback("正在關閉瀏覽器...")
                self.driver.quit()
                self.driver = None # Reset driver
            self.status_callback("✅ 第一步操作完成。")
