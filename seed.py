import requests
import time
from colorama import init, Fore, Style
import sys
import os
import threading
import random  # Thêm thư viện random để tạo thời gian chờ ngẫu nhiên

init(autoreset=True)

class Seed:
    def __init__(self):
        self.line = Fore.WHITE + "~" * 50

        # Banner with logo
        self.banner = f"""
{Fore.BLUE} █████   █████                               
{Fore.BLUE}░░███   ░░███                                
 {Fore.BLUE}░███    ░███   ██████   ████████    ██████  
 {Fore.BLUE}░███████████  ░░░░░███ ░░███░░███  ░░░░░███ 
 {Fore.BLUE}░███░░░░░███   ███████  ░███ ░███   ███████ 
 {Fore.BLUE}░███    ░███  ███░░███  ░███ ░███  ███░░███ 
 {Fore.BLUE} █████   █████░░████████ ████ █████░░████████
{Fore.BLUE}░░░░░   ░░░░░  ░░░░░░░░ ░░░░ ░░░░░  ░░░░░░░░ 

{Fore.WHITE}Tú Bà Hana iu thưn bạn
{Fore.WHITE}t.me/hana2495
"""

    def display_banner(self):
        print(self.banner)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

# URLs and headers for API requests
url_claim = 'https://elb.seeddao.org/api/v1/seed/claim'
url_balance = 'https://elb.seeddao.org/api/v1/profile/balance'
url_checkin = 'https://elb.seeddao.org/api/v1/login-bonuses'
url_get_profile = 'https://elb.seeddao.org/api/v1/profile'
url_tasks = 'https://elb.seeddao.org/api/v1/tasks/progresses'
url_complete_task = 'https://elb.seeddao.org/api/v1/tasks/'

headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-ID,en-US;q=0.9,en;q=0.8,id;q=0.7',
    'content-length': '0',
    'dnt': '1',
    'origin': 'https://cf.seeddao.org',
    'referer': 'https://cf.seeddao.org/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'telegram-data': 'tokens',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
}

# Function to load tokens from a file
def load_credentials():
    try:
        with open('tokens.txt', 'r') as file:
            tokens = file.read().strip().split('\n')
        return tokens
    except FileNotFoundError:
        print(Fore.RED + "[ERROR]: tokens.txt file not found.")
        return []
    except Exception as e:
        print(Fore.RED + f"[ERROR]: An error occurred while loading tokens: {str(e)}")
        return []

# Function to load proxies from a file
def load_proxies():
    try:
        with open('proxy.txt', 'r') as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    except FileNotFoundError:
        print(Fore.RED + "[ERROR]: proxy.txt file not found.")
        return []
    except Exception as e:
        print(Fore.RED + f"[ERROR]: An error occurred while loading proxies: {str(e)}")
        return []

access_token = None
expires_in = 0

# Dummy refresh token function (update according to your actual flow)
def refresh_token():
    global access_token, expires_in
    access_token = 'YOUR_ACTUAL_TOKEN_HERE'
    expires_in = time.time() + 3600

# Ensure token is valid
def ensure_token():
    global access_token, expires_in
    if access_token is None or time.time() >= expires_in:
        refresh_token()

# Function to get profile data and display account name with proxy
def get_profile(proxy=None, proxy_ip=None, account_number=None):
    ensure_token()
    headers['Authorization'] = f'Bearer {access_token}'
    
    try:
        response = requests.get(url_get_profile, headers=headers, proxies=proxy)
        if response.status_code == 200:
            profile_data = response.json()
            name = profile_data['data']['name']
            # Display the account name with proxy and account number
            print(f"{Fore.CYAN + Style.BRIGHT}[{account_number}] Account: {name} | Proxy IP: {proxy_ip}")
        else:
            print(f"{Fore.RED + '[ Profile ]: Failed to fetch profile data, status code: {response.status_code}'}")
    except requests.RequestException as e:
        print(Fore.RED + f"[ERROR]: Proxy error: {e}")
        return False
    return True

# Function to get and complete tasks with retry mechanism for 429 status code
def get_tasks(proxy=None):
    ensure_token()
    headers['Authorization'] = f'Bearer {access_token}'
    try:
        response = requests.get(url_tasks, headers=headers, proxies=proxy)
        if response.status_code == 200:
            tasks = response.json()['data']
            for task in tasks:
                if task['task_user'] is None or not task['task_user']['completed']:
                    complete_task(task['id'], task['name'], proxy)
                    # Thêm thời gian chờ giữa các tác vụ để tránh lỗi 429
                    time.sleep(5)  # Chờ 5 giây giữa các yêu cầu hoàn thành nhiệm vụ
        else:
            print(f"{Fore.RED + '[ Tasks ]: Failed to fetch tasks, status code: {response.status_code}'}")
    except requests.RequestException as e:
        print(Fore.RED + f"[ERROR]: Proxy error: {e}")

# Function to complete a task with retry on status code 429
def complete_task(task_id, task_name, proxy=None, max_retries=3):
    headers['Authorization'] = f'Bearer {access_token}'
    retries = 0
    success = False
    
    while retries < max_retries and not success:
        try:
            response = requests.post(f'{url_complete_task}{task_id}', headers=headers, proxies=proxy)
            if response.status_code == 200:
                print(f"{Fore.GREEN + Style.BRIGHT}[ Tasks ]: Task {task_name} completed.")
                success = True
            elif response.status_code == 429:  # Rate-limiting error
                retry_delay = random.uniform(3, 5)  # Thời gian chờ ngẫu nhiên từ 3 đến 5 giây
                print(f"{Fore.RED + Style.BRIGHT}[ Tasks ]: Failed to complete task {task_name}, status code: 429 (Too Many Requests). Retrying in {retry_delay:.2f} seconds...")
                time.sleep(retry_delay)  # Tăng thời gian chờ ngẫu nhiên trước khi thử lại
                retries += 1
            else:
                print(f"{Fore.RED + Style.BRIGHT}[ Tasks ]: Failed to complete task {task_name}, status code: {response.status_code}")
                break
        except requests.RequestException as e:
            print(Fore.RED + f"[ERROR]: Proxy error: {e}")
            break

# Function to handle each thread
def handle_thread(token, proxy, proxy_ip, account_number):
    try:
        headers['telegram-data'] = token
        if get_profile(proxy, proxy_ip, account_number):
            get_tasks(proxy)
        # Thêm thời gian chờ ngẫu nhiên giữa các hành động của mỗi tài khoản
        time.sleep(random.uniform(3, 5))  # Thời gian chờ ngẫu nhiên giữa các tài khoản
    except Exception as e:
        print(Fore.RED + f"[ERROR]: Error occurred in thread: {e}")

def run_cycle(tokens, proxies):
    proxy_index = 0
    threads = []
    for index, token in enumerate(tokens):
        # Use proxies in a round-robin fashion
        proxy_data = proxies[index % len(proxies)].split(':')
        proxy = {
            'http': f'http://{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}',  # Force HTTP proxy for both HTTP and HTTPS
            'https': f'http://{proxy_data[2]}:{proxy_data[3]}@{proxy_data[0]}:{proxy_data[1]}'  # Using HTTP proxy for HTTPS
        }
        proxy_ip = proxy_data[0]  # Only show the IP address, exclude the port
        account_number = index + 1  # Display the account number

        # Create and start a thread for each token
        thread = threading.Thread(target=handle_thread, args=(token, proxy, proxy_ip, account_number))
        threads.append(thread)
        thread.start()

        # Tăng thời gian chờ giữa các luồng để tránh việc khởi tạo quá nhiều yêu cầu cùng lúc
        time.sleep(2)  # Tăng thời gian chờ lên 2 giây giữa các luồng

        # Limit to 100 concurrent threads
        if len(threads) >= 100:
            for t in threads:
                t.join()  # Wait for all threads to finish
            threads = []  # Clear thread list to start the next batch

    # Ensure all remaining threads are completed
    for t in threads:
        t.join()

def main():
    # Display banner
    bot = Seed()
    bot.display_banner()

    tokens = load_credentials()
    proxies = load_proxies()
    
    if not proxies:
        print(Fore.RED + "[ERROR]: No proxies found. Exiting.")
        return

    while True:
        # Run the full cycle of all tokens
        run_cycle(tokens, proxies)

        # Wait for 30 seconds before the next cycle
        for i in range(30, 0, -1):
            sys.stdout.write(f"\r{Fore.CYAN + Style.BRIGHT}============ Waiting {i} seconds before next cycle... ============")
            sys.stdout.flush()
            time.sleep(1)
        print()  # New line after the countdown

if __name__ == "__main__":
    main()
