import requests
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from random import choice
from colorama import Fore, init
init()

tokens = [line.rstrip("\n") for line in open("data/tokens.txt", "r")]
proxies = [line.rstrip("\n") for line in open("data/proxies.txt", "r")]

lock = Lock()
def save_str(location : str, item : str):
    lock.acquire()
    file = open(location, "a")
    file.write(item+"\n")
    file.close()
    lock.release()

class GIFT_CHECKER:
    def __init__(self, token, x):
        self.full_token : str = token
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
            "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiQ2hyb21lIiwiZGV2aWNlIjoiIiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiaGFzX2NsaWVudF9tb2RzIjpmYWxzZSwiYnJvd3Nlcl91c2VyX2FnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzEzNS4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiYnJvd3Nlcl92ZXJzaW9uIjoiMTM1LjAuMC4wIiwib3NfdmVyc2lvbiI6IjEwIiwicmVmZXJyZXIiOiIiLCJyZWZlcnJpbmdfZG9tYWluIjoiIiwicmVmZXJyZXJfY3VycmVudCI6IiIsInJlZmVycmluZ19kb21haW5fY3VycmVudCI6ImRpc2NvcmQuY29tIiwicmVsZWFzZV9jaGFubmVsIjoic3RhYmxlIiwiY2xpZW50X2J1aWxkX251bWJlciI6Mzg5MDA0LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ=="
        }


    def check_nitro_gift(self, retries=3):
        try:
            proxy = "http://" + choice(proxies)
            req = requests.get("https://discord.com/api/v9/users/@me/referrals/eligibility", headers=self.headers, proxies = {
                "http": proxy,
                "https": proxy
            })
            print(req.text)
            
            if req.status_code == 200:
                return True, req.json()["referrals_remaining"]
            elif req.status_code in [401, 403, 404]:
                return None, req.status_code
            return False, False
        except:
            retries -= 1
            self.check_nitro_gift(retries)
            return False, False

    def run(self):
        try:
            check, result = self.check_nitro_gift()
            if check:
                print(f"[{self.thread}] {result} {Fore.GREEN}Gifts Found{Fore.RESET} - {self.token}")
                save_str(f"output/{result}_gifts.txt", self.full_token)
            elif check == None:
                if result == 401:
                    print(f"[{self.thread}] Invalid Token - {self.token}")
                    save_str(f"output/invalids.txt", self.full_token)
                elif result == 401:
                    print(f"[{self.thread}] Locked Token - {self.token}")
                    save_str(f"output/locked.txt", self.full_token)
                elif result == 404:
                    print(f"[{self.thread}] Not Found - {self.token}")
                    save_str(f"output/no_gifts.txt", self.full_token)
            else:
                print(f"[{self.thread}] Failed Token - {self.token}")
                save_str(f"output/failed.txt", self.full_token)
        except Exception as e:
            print(f"[{self.thread}] Failed Token - {e}")
            save_str(f"output/failed.txt", self.full_token)

def loop(token, x):
    class_function = GIFT_CHECKER(token, x)
    class_function.run()

if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=100)
    x = 0
    for i in tokens:
        with lock:
            x += 1
        executor.submit(loop, i, x)
    executor.shutdown(wait=True)
    input("PRESS ENTER TO EXIT")
    
