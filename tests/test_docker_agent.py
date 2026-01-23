"""Tests for DockerAgent class"""
import pytest
from unittest.mock import patch, MagicMock
from connectors.docker.docker_agent import DockerAgent


class TestDockerAgent:
    
    @pytest.fixture
    def docker_agent(self):
        return DockerAgent(
            platform_url="http://localhost:8000",
            agent_token="test-token-docker",
            config={"log_level": "debug", "max_batch_size": "1000"}
        )
    
    def test_agent_type(self, docker_agent):
        """Test docker agent type"""
        assert docker_agent.agent_type == "docker"
    
    def test_deployment_command_format(self, docker_agent):
        """Test docker deployment command format"""
        command = docker_agent.get_deployment_command()
        
        assert "docker run" in command
        assert "-d" in command
        assert "--name incident-rca-agent" in command
        assert "incident-rca/agent:latest" in command
    
    def test_deployment_command_includes_auth(self, docker_agent):
        """Test deployment command includes authentication"""
        command = docker_agent.get_deployment_command()
        
        assert "test-token-docker" in command
        assert "http://localhost:8000" in command
    
    def test_deployment_command_includes_config(self, docker_agent):
        """Test deployment command includes custom config"""
        command = docker_agent.get_deployment_command()
        
        assert "LOG_LEVEL=debug" in command
        assert "MAX_BATCH_SIZE=1000" in command
    
    @patch('subprocess.run')
    def test_start_docker_agent(self, mock_run, docker_agent):
        """Test starting docker agent"""
        docker_agent.start()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "docker run" in call_args[0][0]
        assert call_args[1]["shell"] is True
        assert call_args[1]["check"] is True
    
    @patch('subprocess.run')
    def test_stop_docker_agent(self, mock_run, docker_agent):
        """Test stopping docker agent"""
        docker_agent.stop()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "docker stop incident-rca-agent" in call_args[0][0]
    
    @patch('subprocess.run')
    def test_get_container_info(self, mock_run, docker_agent):
        """Test retrieving container info"""
        mock_run.return_value = MagicMock(
            stdout='[{"Id": "abc123", "State": {"Running": true}}]'
        )
        
        info = docker_agent._get_container_info()
        
        assert info["Id"] == "abc123"
        assert info["State"]["Running"] is True
    
    @patch('subprocess.run')
    def test_get_docker_stats(self, mock_run, docker_agent):
        """Test retrieving docker stats"""
        mock_run.return_value = MagicMock(
            stdout='{"MemUsage": "256MB", "CPUPercent": "5%"}'
        )
        
        stats = docker_agent._get_docker_stats()
        
        assert stats["MemUsage"] == "256MB"
        assert stats["CPUPercent"] == "5%"
    
    def test_gather_data_structure(self, docker_agent):
        """Test gather_data returns expected structure"""
        with patch.object(docker_agent, '_get_container_info', return_value={"id": "abc"}):
            with patch.object(docker_agent, '_get_docker_stats', return_value={"cpu": "5%"}):
                data = docker_agent._gather_data()
        
        assert "container_info" in data
        assert "docker_stats" in data
