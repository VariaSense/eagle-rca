"""Abstract base class for all agent types"""
from abc import ABC, abstractmethod
from typing import Dict, Any
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agent types"""
    
    def __init__(self, platform_url: str, agent_token: str, config: Dict[str, Any] = None):
        self.platform_url = platform_url
        self.agent_token = agent_token
        self.config = config or {}
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create authenticated session"""
        session = requests.Session()
        session.headers.update({
            "Authorization": f"Bearer {self.agent_token}",
            "Content-Type": "application/json"
        })
        return session
    
    @abstractmethod
    def start(self):
        """Start the agent - implementation specific"""
        pass
    
    @abstractmethod
    def stop(self):
        """Stop the agent - implementation specific"""
        pass
    
    @abstractmethod
    def get_deployment_command(self) -> str:
        """Get the deployment/install command for this agent type"""
        pass
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect metrics from the environment"""
        logger.info("Collecting metrics...")
        metrics = {
            "agent_type": self.agent_type,
            "timestamp": self._get_timestamp(),
            "data": self._gather_data()
        }
        return metrics
    
    def send_data(self, data: Dict[str, Any], data_type: str = "metrics", metadata: Dict[str, Any] | None = None) -> bool:
        """Send collected data to platform."""
        payload = {
            "data_type": data_type,
            "payload": data,
            "metadata": metadata or {},
        }
        try:
            response = self.session.post(
                f"{self.platform_url}/api/v1/agent/data",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            logger.info("Data sent successfully")
            return True
        except requests.RequestException as e:
            logger.error(f"Failed to send data: {e}")
            return False
    
    def heartbeat(self) -> bool:
        """Send periodic heartbeat to platform"""
        try:
            response = self.session.post(
                f"{self.platform_url}/api/v1/agent/heartbeat",
                json={"status": "active"},
                timeout=5
            )
            return response.status_code == 200
        except requests.RequestException as e:
            logger.error(f"Heartbeat failed: {e}")
            return False
    
    @abstractmethod
    def _gather_data(self) -> Dict[str, Any]:
        """Gather environment-specific data"""
        pass
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import timezone
        return datetime.now(timezone.utc).isoformat()
    
    @property
    @abstractmethod
    def agent_type(self) -> str:
        """Return agent type identifier"""
        pass
