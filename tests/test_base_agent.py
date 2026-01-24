"""Tests for BaseAgent class"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import requests
from sdk.core.base_agent import BaseAgent


class ConcreteAgent(BaseAgent):
    """Concrete implementation for testing abstract class"""
    
    @property
    def agent_type(self) -> str:
        return "test"
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def get_deployment_command(self) -> str:
        return "test command"
    
    def _gather_data(self):
        return {"test": "data"}


class TestBaseAgent:
    
    @pytest.fixture
    def agent(self):
        return ConcreteAgent(
            platform_url="http://localhost:8000",
            agent_token="test-token-123",
            config={"key": "value"}
        )
    
    def test_agent_initialization(self, agent):
        """Test agent is initialized correctly"""
        assert agent.platform_url == "http://localhost:8000"
        assert agent.agent_token == "test-token-123"
        assert agent.config["key"] == "value"
        assert agent.session is not None
    
    def test_session_has_auth_header(self, agent):
        """Test session includes authorization header"""
        assert "Authorization" in agent.session.headers
        assert agent.session.headers["Authorization"] == "Bearer test-token-123"
        assert agent.session.headers["Content-Type"] == "application/json"
    
    @patch('requests.Session.post')
    def test_send_data_success(self, mock_post, agent):
        """Test successful data transmission"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        data = {"metric": "cpu", "value": 75}
        result = agent.send_data(data)
        
        assert result is True
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert "metrics" in call_args[0][0]
        assert call_args[1]["json"] == data
    
    @patch('requests.Session.post')
    def test_send_data_failure(self, mock_post, agent):
        """Test data transmission failure"""
        mock_post.side_effect = requests.RequestException("Connection failed")
        
        data = {"metric": "cpu", "value": 75}
        result = agent.send_data(data)
        
        assert result is False
    
    @patch('requests.Session.post')
    def test_send_data_http_error(self, mock_post, agent):
        """Test data transmission with HTTP error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Server error")
        mock_post.return_value = mock_response
        
        data = {"metric": "cpu", "value": 75}
        result = agent.send_data(data)
        
        assert result is False
    
    @patch('requests.Session.post')
    def test_heartbeat_success(self, mock_post, agent):
        """Test successful heartbeat"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        result = agent.heartbeat()
        
        assert result is True
        call_args = mock_post.call_args
        assert "heartbeat" in call_args[0][0]
    
    @patch('requests.Session.post')
    def test_heartbeat_failure(self, mock_post, agent):
        """Test failed heartbeat"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        result = agent.heartbeat()
        
        assert result is False
    
    @patch('requests.Session.post')
    def test_heartbeat_connection_error(self, mock_post, agent):
        """Test heartbeat with connection error"""
        mock_post.side_effect = requests.RequestException("Connection timeout")
        
        result = agent.heartbeat()
        
        assert result is False
    
    def test_collect_metrics(self, agent):
        """Test metrics collection"""
        metrics = agent.collect_metrics()
        
        assert metrics["agent_type"] == "test"
        assert "timestamp" in metrics
        assert "data" in metrics
        assert metrics["data"] == {"test": "data"}
    
    def test_agent_type_property(self, agent):
        """Test agent type property"""
        assert agent.agent_type == "test"
    
    def test_get_timestamp_format(self, agent):
        """Test timestamp is ISO format"""
        timestamp = agent._get_timestamp()
        # Should not raise exception
        from datetime import datetime
        datetime.fromisoformat(timestamp)
