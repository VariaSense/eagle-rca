"""Agent running on VM or physical server"""
from connectors.core.base_agent import BaseAgent
from typing import Dict, Any
import platform
import subprocess
import logging

logger = logging.getLogger(__name__)

try:
    import psutil
except ImportError:
    psutil = None


class ServerAgent(BaseAgent):
    """Agent running on VM or physical server"""
    
    @property
    def agent_type(self) -> str:
        return "server"
    
    def get_deployment_command(self) -> str:
        """Generate installation command for server"""
        os_type = platform.system().lower()
        
        if os_type == "linux":
            return self._get_linux_install_command()
        elif os_type == "darwin":
            return self._get_macos_install_command()
        elif os_type == "windows":
            return self._get_windows_install_command()
        else:
            raise ValueError(f"Unsupported OS: {os_type}")
    
    def _get_linux_install_command(self) -> str:
        """Get Linux installation command"""
        return (
            f"curl -fsSL https://install.example.com/agent.sh | bash -s -- \\\n"
            f"  --api-url {self.platform_url} \\\n"
            f"  --token {self.agent_token} \\\n"
            f"  --agent-type server"
        )
    
    def _get_macos_install_command(self) -> str:
        """Get macOS installation command"""
        return (
            f"brew tap incident-rca/agent && "
            f"brew install incident-rca-agent && "
            f"incident-rca-agent init \\\n"
            f"  --api-url {self.platform_url} \\\n"
            f"  --token {self.agent_token}"
        )
    
    def _get_windows_install_command(self) -> str:
        """Get Windows installation command"""
        return (
            f"powershell -Command \"irm https://install.example.com/agent.ps1 | iex\" "
            f"-ApiUrl {self.platform_url} "
            f"-Token {self.agent_token}"
        )
    
    def start(self):
        """Start the agent service"""
        import sys
        
        if sys.platform == "win32":
            subprocess.run("net start incident-rca-agent", shell=True, check=True)
        else:
            subprocess.run("systemctl start incident-rca-agent", shell=True, check=True)
        
        logger.info("Server agent started")
    
    def stop(self):
        """Stop the agent service"""
        import sys
        
        if sys.platform == "win32":
            subprocess.run("net stop incident-rca-agent", shell=True)
        else:
            subprocess.run("systemctl stop incident-rca-agent", shell=True)
        
        logger.info("Server agent stopped")
    
    def _gather_data(self) -> Dict[str, Any]:
        """Gather server/VM system metrics"""
        if not psutil:
            logger.warning("psutil not available, skipping system metrics")
            return {}
        
        return {
            "system_info": self._get_system_info(),
            "cpu_metrics": self._get_cpu_metrics(),
            "memory_metrics": self._get_memory_metrics(),
            "disk_metrics": self._get_disk_metrics(),
            "network_metrics": self._get_network_metrics(),
        }
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "processor": platform.processor(),
            "hostname": platform.node(),
        }
    
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU metrics"""
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_count": psutil.cpu_count(),
            "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
        }
    
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory metrics"""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent,
        }
    
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk metrics"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent,
        }
    
    def _get_network_metrics(self) -> Dict[str, Any]:
        """Get network metrics"""
        net_io = psutil.net_io_counters()
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv,
        }
