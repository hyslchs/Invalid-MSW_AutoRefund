import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import datetime

# 修正後的導入
from take_cookie import CookieManager
from main import mark_orders
from refund import process_refunds

class RefundApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MSW Auto Refund")
        self.geometry("700x1000")

        # 初始化 Cookie 管理器
        self.cookie_manager = CookieManager(self.update_status)

        # --- 樣式設定 ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.style.configure('TButton', font=('Helvetica', 12), padding=10)
        self.style.configure('TLabel', font=('Helvetica', 12), padding=5)
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Accent.TButton', foreground='white', background='#0078D7')

        # --- 主框架 ---
        main_frame = ttk.Frame(self, padding="20 20 20 20")
        main_frame.pack(expand=True, fill=tk.BOTH)

        # --- 標題 ---
        header_label = ttk.Label(main_frame, text="MSW Auto Refund", style='Header.TLabel')
        header_label.pack(pady=(0, 20))

        # --- 功能區塊 ---
        self.create_step1_frame(main_frame)
        self.create_step2_frame(main_frame)
        self.create_step3_frame(main_frame)

        # --- 狀態顯示區 ---
        status_frame = ttk.LabelFrame(main_frame, text="執行狀態", padding="10 10 10 10")
        status_frame.pack(expand=True, fill=tk.BOTH, pady=(20, 0))

        self.status_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD, font=("Consolas", 10), height=15)
        self.status_text.pack(expand=True, fill=tk.BOTH)
        self.status_text.configure(state='disabled')

    def create_step1_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="第一步：取得並儲存 Cookie", padding="15 15 15 15")
        frame.pack(fill=tk.X, pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack()

        self.login_btn = ttk.Button(button_frame, text="1. 開啟瀏覽器登入", command=self.start_login_thread)
        self.login_btn.grid(row=0, column=0, padx=5)

        self.save_cookie_btn = ttk.Button(button_frame, text="2. 儲存Cookie並關閉", command=self.save_cookie_thread, state=tk.DISABLED)
        self.save_cookie_btn.grid(row=0, column=1, padx=5)

    def create_step2_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="第二步：抓取並標記訂單", padding="15 15 15 15")
        frame.pack(fill=tk.X, pady=10)

        controls_frame = ttk.Frame(frame)
        controls_frame.pack()

        ttk.Label(controls_frame, text="起始頁數:").grid(row=0, column=0, sticky='w', pady=2)
        self.start_page_entry = ttk.Entry(controls_frame, width=8)
        self.start_page_entry.grid(row=0, column=1, padx=5, pady=2)
        self.start_page_entry.insert(0, "1")

        ttk.Label(controls_frame, text="結束頁數:").grid(row=0, column=2, sticky='w', pady=2)
        self.end_page_entry = ttk.Entry(controls_frame, width=8)
        self.end_page_entry.grid(row=0, column=3, padx=5, pady=2)
        self.end_page_entry.insert(0, "2")

        today = datetime.date.today()
        one_month_ago = today - datetime.timedelta(days=30)

        ttk.Label(controls_frame, text="開始日期:").grid(row=1, column=0, sticky='w', pady=2)
        self.start_date_entry = ttk.Entry(controls_frame, width=12)
        self.start_date_entry.grid(row=1, column=1, padx=5, pady=2)
        self.start_date_entry.insert(0, one_month_ago.strftime("%Y-%m-%d"))

        ttk.Label(controls_frame, text="結束日期:").grid(row=1, column=2, sticky='w', pady=2)
        self.end_date_entry = ttk.Entry(controls_frame, width=12)
        self.end_date_entry.grid(row=1, column=3, padx=5, pady=2)
        self.end_date_entry.insert(0, today.strftime("%Y-%m-%d"))

        btn = ttk.Button(frame, text="開始抓取與標記", command=self.run_mark_orders, style='Accent.TButton')
        btn.pack(pady=(15, 0), anchor='center')

    def create_step3_frame(self, parent):
        frame = ttk.LabelFrame(parent, text="第三步：執行自動退款", padding="15 15 15 15")
        frame.pack(fill=tk.X, pady=10)

        btn = ttk.Button(frame, text="開始退款", command=lambda: self.run_task(process_refunds, self.update_status))
        btn.pack(anchor='center')

    def update_status(self, message):
        def _update():
            self.status_text.configure(state='normal')
            self.status_text.insert(tk.END, message + '\n')
            self.status_text.see(tk.END)
            self.status_text.configure(state='disabled')
        self.after(0, _update)

    def run_task(self, task_func, *args):
        self.update_status(f">>> 開始執行任務：{task_func.__name__}...")
        thread = threading.Thread(target=task_func, args=args)
        thread.daemon = True
        thread.start()

    def start_login_thread(self):
        self.login_btn.config(state=tk.DISABLED)
        self.save_cookie_btn.config(state=tk.NORMAL)
        self.run_task(self.cookie_manager.start_login)

    def save_cookie_thread(self):
        self.save_cookie_btn.config(state=tk.DISABLED)
        self.run_task(self.cookie_manager.save_cookies_and_quit)
        self.login_btn.config(state=tk.NORMAL)

    def run_mark_orders(self):
        try:
            start_page = int(self.start_page_entry.get())
            end_page = int(self.end_page_entry.get())
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()

            datetime.datetime.strptime(start_date, '%Y-%m-%d')
            datetime.datetime.strptime(end_date, '%Y-%m-%d')

            if start_page > end_page:
                self.update_status("❌ 錯誤：起始頁數不能大於結束頁數。")
                return
            
            self.run_task(mark_orders, start_page, end_page, start_date, end_date, self.update_status)

        except ValueError:
            self.update_status("❌ 錯誤：頁數必須是有效的數字，日期格式必須是 YYYY-MM-DD。")

if __name__ == "__main__":
    app = RefundApp()
    app.mainloop()
