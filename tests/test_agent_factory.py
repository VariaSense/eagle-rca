"""Tests for AgentFactory class"""
import pytest
from connectors.agent_factory import AgentFactory
from connectors.docker.docker_agent import DockerAgent
from connectors.kubernetes.k8s_agent import K8sAgent
from connectors.server.server_agent import ServerAgent


class TestAgentFactory:
    
    def test_create_docker_agent(self):
        """Test creating docker agent through factory"""
        agent = AgentFactory.create_agent(
            agent_type="docker",
            platform_url="http://localhost:8000",
            agent_token="token-123",
            config={"key": "value"}
        )
        
        assert isinstance(agent, DockerAgent)
        assert agent.agent_type == "docker"
    
    def test_create_kubernetes_agent(self):
        """Test creating kubernetes agent through factory"""
        agent = AgentFactory.create_agent(
            agent_type="kubernetes",
            platform_url="http://localhost:8000",
            agent_token="token-123",
            config={"namespace": "default"}
        )
        
        assert isinstance(agent, K8sAgent)
        assert agent.agent_type == "kubernetes"
    
    def test_create_server_agent(self):
        """Test creating server agent through factory"""
        agent = AgentFactory.create_agent(
            agent_type="server",
            platform_url="http://localhost:8000",
            agent_token="token-123"
        )
        
        assert isinstance(agent, ServerAgent)
        assert agent.agent_type == "server"
    
    def test_create_agent_with_default_config(self):
        """Test creating agent with no config"""
        agent = AgentFactory.create_agent(
            agent_type="docker",
            platform_url="http://localhost:8000",
            agent_token="token-123"
        )
        
        assert agent.config == {}
    
    def test_create_agent_invalid_type(self):
        """Test creating agent with invalid type raises error"""
        with pytest.raises(ValueError) as exc_info:
            AgentFactory.create_agent(
                agent_type="invalid",
                platform_url="http://localhost:8000",
                agent_token="token-123"
            )
        
        assert "Unknown agent type" in str(exc_info.value)
    
    def test_list_supported_types(self):
        """Test listing supported agent types"""
        types = AgentFactory.list_supported_types()
        
        assert "docker" in types
        assert "kubernetes" in types
        assert "server" in types
        assert len(types) == 3
