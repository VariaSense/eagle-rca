"""Factory to create appropriate agent based on infrastructure type"""
from typing import Dict, Any
from connectors.docker.docker_agent import DockerAgent
from connectors.kubernetes.k8s_agent import K8sAgent
from connectors.server.server_agent import ServerAgent


class AgentFactory:
    """Factory to create appropriate agent based on infrastructure type"""
    
    _agents = {
        "docker": DockerAgent,
        "kubernetes": K8sAgent,
        "server": ServerAgent,
    }
    
    @classmethod
    def create_agent(
        cls,
        agent_type: str,
        platform_url: str,
        agent_token: str,
        config: Dict[str, Any] = None
    ):
        """Create and return appropriate agent instance"""
        if agent_type not in cls._agents:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agents[agent_type]
        return agent_class(platform_url, agent_token, config or {})
    
    @classmethod
    def list_supported_types(cls):
        """List all supported agent types"""
        return list(cls._agents.keys())
