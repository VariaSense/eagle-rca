"""Agent running as Docker container"""
from connectors.core.base_agent import BaseAgent
from typing import Dict, Any
import json
import subprocess
import logging

logger = logging.getLogger(__name__)


class DockerAgent(BaseAgent):
    """Agent running as Docker container"""
    
    @property
    def agent_type(self) -> str:
        return "docker"
    
    def get_deployment_command(self) -> str:
        """Generate docker run command"""
        env_vars = self._build_env_vars()
        return (
            f"docker run -d --name incident-rca-agent \\\n"
            f"  {env_vars} \\\n"
            f"  incident-rca/agent:latest"
        )
    
    def _build_env_vars(self) -> str:
        """Build environment variables for docker"""
        vars_list = [
            f"-e PLATFORM_API_URL={self.platform_url}",
            f"-e AGENT_TOKEN={self.agent_token}",
            f"-e AGENT_TYPE=docker",
        ]
        # Add custom config vars
        for key, value in self.config.items():
            vars_list.append(f"-e {key.upper()}={value}")
        return " \\\n  ".join(vars_list)
    
    def start(self):
        """Start docker container"""
        cmd = self.get_deployment_command()
        subprocess.run(cmd, shell=True, check=True)
        logger.info("Docker agent started")
    
    def stop(self):
        """Stop docker container"""
        subprocess.run("docker stop incident-rca-agent", shell=True)
        logger.info("Docker agent stopped")
    
    def _gather_data(self) -> Dict[str, Any]:
        """Gather docker environment metrics"""
        data = {
            "container_info": self._get_container_info(),
            "docker_stats": self._get_docker_stats(),
        }
        return data
    
    def _get_container_info(self) -> Dict[str, Any]:
        """Get container inspection data"""
        try:
            result = subprocess.run(
                "docker inspect incident-rca-agent",
                shell=True,
                capture_output=True,
                text=True
            )
            return json.loads(result.stdout)[0] if result.stdout else {}
        except Exception as e:
            logger.error(f"Failed to get container info: {e}")
            return {}
    
    def _get_docker_stats(self) -> Dict[str, Any]:
        """Get docker container statistics"""
        try:
            result = subprocess.run(
                "docker stats --no-stream --format json incident-rca-agent",
                shell=True,
                capture_output=True,
                text=True
            )
            return json.loads(result.stdout) if result.stdout else {}
        except Exception as e:
            logger.error(f"Failed to get docker stats: {e}")
            return {}
