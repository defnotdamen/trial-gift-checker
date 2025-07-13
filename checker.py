import requests
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from random import choice
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

tokens = [line.rstrip("\n") for line in open("data/tokens.txt", "r")]
proxies = [line.rstrip("\n") for line in open("data/proxies.txt", "r")]

lock = Lock()

def now():
    return datetime.now().strftime("%H:%M:%S")

def save_str(location: str, item: str):
    with lock:
        with open(location, "a") as file:
            file.write(item + "\n")

class GIFT_CHECKER:
    def __init__(self, token, x):
        self.full_token: str = token
        self.token = token
        if ":" in self.full_token:
            self.token = self.full_token.split(":")[2]
        self.thread = x
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": self.token,
            "cache-control": "no-cache",
            "origin": "https://discord.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            "referer": "https://discord.com/shop",
            "sec-ch-ua": "\"Google Chrome\";v=\"135\", \"Not-A.Brand\";v=\"8\", \"Chromium\";v=\"135\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "Asia/Bahrain",
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoi..."
        }

    def check_nitro_gift(self, retries=3):
        try:
            proxy = "http://" + choice(proxies)
            req = requests.get("https://discord.com/api/v9/users/@me/referrals/eligibility", headers=self.headers, proxies={
                "http": proxy,
                "https": proxy
            })
            if req.status_code == 200:
                return True, req.json()["referrals_remaining"]
            elif req.status_code in [401, 403, 404]:
                return None, req.status_code
            return False, False
        except:
            if retries > 0:
                return self.check_nitro_gift(retries - 1)
            return False, False

    def run(self):
        try:
            check, result = self.check_nitro_gift()
            short_token = self.token[:30] + "..."
            if check:
                with lock:
                    print(f"\033[1;90m{now()} » \033[1;92mVALID \033[1;97m• {result} gifts found ➔ \033[1;92m[{short_token}]\033[0m")
                save_str(f"output/{result}_gifts.txt", self.full_token)
            elif check is None:
                if result == 401:
                    with lock:
                        print(f"\033[1;90m{now()} » \033[1;91mINVALID \033[1;97m• Unauthorized ➔ \033[1;91m[{short_token}]\033[0m")
                    save_str("output/invalids.txt", self.full_token)
                elif result == 403:
                    with lock:
                        print(f"\033[1;90m{now()} » \033[1;93mLOCKED \033[1;97m• Access denied ➔ \033[1;93m[{short_token}]\033[0m")
                    save_str("output/locked.txt", self.full_token)
                elif result == 404:
                    with lock:
                        print(f"\033[1;90m{now()} » \033[1;94mNO GIFTS \033[1;97m• Not eligible ➔ \033[1;94m[{short_token}]\033[0m")
                    save_str("output/no_gifts.txt", self.full_token)
            else:
                with lock:
                    print(f"\033[1;90m{now()} » \033[1;91mERROR \033[1;97m• Request failed ➔ \033[1;91m[{short_token}]\033[0m")
                save_str("output/failed.txt", self.full_token)
        except Exception as e:
            short_token = self.token[:30] + "..."
            with lock:
                print(f"\033[1;90m{now()} » \033[1;91mERROR \033[1;97m• Exception ➔ \033[1;91m[{short_token}] ➔ {e}\033[0m")
            save_str("output/failed.txt", self.full_token)

def loop(token, x):
    checker = GIFT_CHECKER(token, x)
    checker.run()

if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=100)
    x = 0
    for token in tokens:
        with lock:
            x += 1
        executor.submit(loop, token, x)
    executor.shutdown(wait=True)
    input("PRESS ENTER TO EXIT")
