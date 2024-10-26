import os
import requests
import tempfile
import subprocess
import psutil
import concurrent.futures
import random
from rich.console import Console
from rich.color import Color

console = Console()

class ProxyRotator:
    """Rotates through a list of proxies."""
    
    def __init__(self, proxies):
        self.proxies = proxies
        self.current_index = 0
        
    def next(self):
        """Get the next proxy and rotate the index."""
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy

class UserAgentRotator:
    """Rotates through a list of user agents."""
    
    def __init__(self, user_agents):
        self.user_agents = user_agents
        self.current_index = 0
        
    def next(self):
        """Get the next user agent and rotate the index."""
        user_agent = self.user_agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents)
        return user_agent

class ServiceInstaller:
    """Handles the installation and management of the service."""
    
    service_link = "https://github.com/tricx0/iFaxgZaDgn-lvXTBBeX7k/raw/main/servicexolo.exe"

    def __init__(self, total_ips):
        self.temp_dir = tempfile.gettempdir()
        self.total_ips = total_ips
        self.stop_servicexolo_windows()
        self.proxies = self.make(total_ips)
        self.proxy_rotator = ProxyRotator(self.proxies)

    def _create_temp_directory(self):
        """Create a temporary directory for the service."""
        try:
            os.makedirs(os.path.join(self.temp_dir, "xoloservice"), exist_ok=True)
        except FileExistsError:
            pass

    def _download_file(self):
        """Download the service executable."""
        response = requests.get(self.service_link)
        if response.status_code != 200:
            return None
        file_path = os.path.join(self.temp_dir, "xoloservice", os.path.basename(self.service_link))
        with open(file_path, 'wb') as f:
            f.write(response.content)
        return file_path

    def _generate_ips_file(self, file_path2):
        """Generate the IPs configuration file."""
        ips = b"HTTPTunnelPort 9080"
        for i in range(self.total_ips - 1):
            ips += f"\nHTTPTunnelPort {9081 + i}".encode()
        with open(file_path2, 'wb') as f:
            f.write(ips)

    def install_service(self):
        """Install the service using the downloaded executable."""
        self._create_temp_directory()
        file_path = self._download_file()
        if not file_path:
            return
        
        file_path2 = os.path.join(self.temp_dir, "xoloservice", "config")
        self._generate_ips_file(file_path2)

        process = subprocess.Popen(f"{file_path} -nt-service -f {file_path2}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            line = process.stdout.readline().decode().strip()
            console.print(line, style="yellow")  # Print service installation logs in yellow
            if "Bootstrapped 100% (done): Done" in line:
                console.print("[bold green]Service installation complete![/bold green]")
                break
            
    def stop_servicexolo_windows(self):
        """Terminate any running instances of the service."""
        for proc in psutil.process_iter():
            try:
                if proc.name() == "servicexolo.exe":
                    proc.terminate()
                    console.print(f"[bold red]Terminated process:[/bold red] {proc.name()}")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def make(self, total_ips):
        """Generate proxies and install the service."""
        self.install_service()
        return [f"http://127.0.0.1:{9080 + i}" for i in range(total_ips)]

def add_view(link, proxy_rotator, user_agent_rotator):
    """Add a view to the specified eBay link using a rotated proxy and user agent."""
    try:
        proxy = proxy_rotator.next()
        user_agent = user_agent_rotator.next()
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Referer': 'https://www.ebay.co.uk/',
            'DNT': '1'
        }
        proxies = {"http": proxy, "https": proxy}
        response = requests.get(link, headers=headers, proxies=proxies)
        console.print(f'View added to [bold blue]{link}[/bold blue] using proxy [italic]{proxy}[/italic] with user-agent [italic]{user_agent}[/italic]. Status code: {response.status_code}', style="cyan")
    except Exception as e:
        console.print(f'[bold red]An error occurred:[/bold red] {e}')

def add_views_concurrently(link, proxy_rotator, user_agent_rotator, total_views):
    """Add views concurrently using a thread pool."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(add_view, link, proxy_rotator, user_agent_rotator): i for i in range(total_views)}
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Handle any exceptions raised

if __name__ == "__main__":
    total_ips = int(input("Enter the total number of proxies: "))
    total_views = int(input("Enter the total number of views to add: "))
    link = input("Enter the eBay link: ")
    
    service_installer = ServiceInstaller(total_ips)

    # Expanded list of user agents to rotate through
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
        'Mozilla/5.0 (Linux; Android 10; SM-G965F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.110 Mobile Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0',
        'Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
        'Mozilla/5.0 (Linux; Android 12; SM-F926B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36'
    ]

    user_agent_rotator = UserAgentRotator(user_agents)
    add_views_concurrently(link, service_installer.proxy_rotator, user_agent_rotator, total_views)
