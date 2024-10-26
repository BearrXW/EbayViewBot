import os
import requests
import tempfile
import subprocess
import psutil
import concurrent.futures
from random_user_agent.user_agent import UserAgent
from rich.console import Console

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
        os.makedirs(os.path.join(self.temp_dir, "xoloservice"), exist_ok=True)

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

def add_view(link, proxy_rotator):
    """Add a view to the specified eBay link using a rotated proxy and random user agent."""
    try:
        proxy = proxy_rotator.next()
        user_agent = user_agent_rotator.get_random_user_agent()  # Get random user agent
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

def add_views_concurrently(link, proxy_rotator, total_views):
    """Add views concurrently using a thread pool."""
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(add_view, link, proxy_rotator): i for i in range(total_views)}
        for future in concurrent.futures.as_completed(futures):
            future.result()  # Handle any exceptions raised

if __name__ == "__main__":
    total_ips = int(input("Enter the total number of proxies: "))
    total_views = int(input("Enter the total number of views to add: "))
    link = input("Enter the eBay link: ")
    
    service_installer = ServiceInstaller(total_ips)

    # Create user agent rotator instance
    user_agent_rotator = UserAgent()

    add_views_concurrently(link, service_installer.proxy_rotator, total_views)
