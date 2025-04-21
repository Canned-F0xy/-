import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import threading
import time
import json
import os
import webbrowser



CONFIG_FILE = "config.json"

DOWNLOAD_FOLDER = "downloads"



class testv1:

    def __init__(self, root):

        self.root = root
        self.root.title("testv_1.0")
        self.setup_styles()
        self.setup_ui()
        self.load_settings()



    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Accent.TButton", foreground="white", background="#0078D7")
        style.map("Accent.TButton", background=[("active", "#005A9E")])



    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.setup_api_section(main_frame)
        self.setup_tag_input(main_frame)
        self.setup_buttons(main_frame)
        self.setup_log_output(main_frame)



    def setup_api_section(self, parent):
        self.proxy_placeholder = "필요시 입력 예) https://127.0.0.1:0000"
        api_frame = ttk.LabelFrame(parent, text="API 설정", padding="10")
        api_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(api_frame, text="Username:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(api_frame)
        self.username_entry.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(api_frame, text="API Key:").pack(anchor=tk.W)
        self.api_key_entry = ttk.Entry(api_frame, show="*")
        self.api_key_entry.pack(fill=tk.X, pady=(0, 5))



        ttk.Label(api_frame, text="프록시 주소:").pack(anchor=tk.W)
        self.proxy_entry = tk.Entry(api_frame, font=("Segoe UI", 9), fg='grey')
        self.proxy_entry.insert(0, self.proxy_placeholder)
        self.proxy_entry.pack(fill=tk.X, pady=(0, 10))



        def clear_placeholder(event):
            if self.proxy_entry.get() == self.proxy_placeholder:
                self.proxy_entry.delete(0, tk.END)
                self.proxy_entry.config(fg='black')



        def add_placeholder(event):
            if not self.proxy_entry.get():
                self.proxy_entry.insert(0, self.proxy_placeholder)
                self.proxy_entry.config(fg='grey')

        self.proxy_entry.bind("<FocusIn>", clear_placeholder)
        self.proxy_entry.bind("<FocusOut>", add_placeholder)

        ttk.Button(api_frame, text="브라우저 인증 시도", command=self.browser_login, style="Accent.TButton").pack(fill=tk.X)



    def setup_tag_input(self, parent):
        tag_frame = ttk.LabelFrame(parent, text="태그 검색", padding="10")
        tag_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        ttk.Label(tag_frame, text="검색 태그 입력 (예시: female kemono -male)").pack(anchor=tk.W)
    
        self.tags_entry = ttk.Entry(tag_frame)
        self.tags_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(tag_frame, text="여러 줄 태그 입력:").pack(anchor=tk.W)

        self.tag_entry = tk.Text(tag_frame, height=4, wrap=tk.WORD, font=('Segoe UI', 9))
        self.tag_entry.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(tag_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="태그 목록", command=lambda: webbrowser.open("https://e621.net/tags")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="e621.net 홈페이지", command=lambda: webbrowser.open("https://e621.net")).pack(side=tk.LEFT)



    def setup_buttons(self, parent):
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="설정 저장", command=self.save_settings, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="설정 불러오기", command=self.load_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="다운로드 시작", command=self.start_download, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)



    def setup_log_output(self, parent):
        log_frame = ttk.LabelFrame(parent, text="로그 출력", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

  
    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

  
    def save_settings(self):
        settings = {
            "username": self.username_entry.get(),
            "api_key": self.api_key_entry.get(),
            "proxy": self.proxy_entry.get(),
            "tags": self.tags_entry.get()

        }

        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        self.log("설정 저장 완료.")



    def load_settings(self):
        if not os.path.exists(CONFIG_FILE):

            return

        try:

            with open(CONFIG_FILE, "r", encoding="utf-8") as f:

                settings = json.load(f)

            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, settings.get("username", ""))
            self.api_key_entry.delete(0, tk.END)
            self.api_key_entry.insert(0, settings.get("api_key", ""))
            self.proxy_entry.delete(0, tk.END)
            self.proxy_entry.insert(0, settings.get("proxy", self.proxy_placeholder))
            self.tags_entry.delete(0, tk.END)
            self.tags_entry.insert(0, settings.get("tags", ""))
            self.log("설정 불러오기 완료.")

        except Exception as e:

            self.log(f"설정 불러오기 오류: {e}")



    def browser_login(self):

        self.log("브라우저 인증 시도 중...")



        def run_browser():

            try:

                from playwright.sync_api import sync_playwright

                with sync_playwright() as p:

                    browser = p.chromium.launch(headless=False)

                    context = browser.new_context()

                    page = context.new_page()

                    page.goto("https://e621.net")

                    self.log("브라우저가 열렸습니다. 로그인 후 쿠키가 자동 추출됩니다.")

                    page.wait_for_timeout(60000)

                    cookies = context.cookies()

                    session = [c for c in cookies if c['name'] == '_danbooru_session']

                    if session:

                        cookie_val = session[0]['value']

                        self.log(f"쿠키 추출 완료: _danbooru_session={cookie_val}")

                    else:

                        self.log("쿠키를 찾을 수 없습니다.")

                    browser.close()

            except Exception as e:

                self.log(f"브라우저 인증 중 오류: {e}")



        threading.Thread(target=run_browser).start()



    def start_download(self):

        tags = self.tags_entry.get()

        if not tags.strip():

            self.log("태그를 입력하세요.")

            return



        threading.Thread(target=self.download_posts, args=(tags.strip(),)).start()



    def download_posts(self, tags):

        self.log("다운로드 시작...")

        headers = {

            "User-Agent": "E621Downloader/6.0",

        }



        auth = (self.username_entry.get(), self.api_key_entry.get())

        proxies = {}

        proxy_input = self.proxy_entry.get().strip()

        if proxy_input and proxy_input != self.proxy_placeholder:

            proxies["http"] = proxy_input

            proxies["https"] = proxy_input



        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)



        try:

            page = 1

            downloaded = 0

            while True:

                url = f"https://e621.net/posts.json?tags={tags}&limit=10&page={page}"

                r = requests.get(url, headers=headers, auth=auth, proxies=proxies)

                if r.status_code != 200:

                    self.log(f"요청 실패: {r.status_code}")

                    break

                data = r.json()

                posts = data.get("posts", [])

                if not posts:

                    self.log("더 이상 게시물이 없습니다.")

                    break

                for post in posts:

                    file_url = post.get("file", {}).get("url")

                    if not file_url:

                        continue

                    file_name = os.path.join(DOWNLOAD_FOLDER, file_url.split("/")[-1])

                    if not os.path.exists(file_name):

                        self.log(f"다운로드 중: {file_url}")

                        with open(file_name, "wb") as f:

                            f.write(requests.get(file_url).content)

                        downloaded += 1

                page += 1

            self.log(f"다운로드 완료. 총 {downloaded}개 파일 저장됨.")

        except Exception as e:

            self.log(f"오류 발생: {e}")



if __name__ == "__main__":

    root = tk.Tk()

    app = testv1(root)

    root.mainloop()



