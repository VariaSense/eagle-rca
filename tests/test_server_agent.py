"""Tests for ServerAgent class"""
import pytest
from unittest.mock import patch, MagicMock
import platform
from connectors.server.server_agent import ServerAgent


class TestServerAgent:
    
    @pytest.fixture
    def server_agent(self):
        return ServerAgent(
            platform_url="http://localhost:8000",
            agent_token="test-token-server",
            config={"environment": "production"}
        )
    
    def test_agent_type(self, server_agent):
        """Test server agent type"""
        assert server_agent.agent_type == "server"
    
    @patch('platform.system', return_value='Linux')
    def test_deployment_command_linux(self, mock_platform, server_agent):
        """Test Linux deployment command"""
        command = server_agent.get_deployment_command()
        
        assert "curl" in command
        assert "bash" in command
        assert "test-token-server" in command
    
    @patch('platform.system', return_value='Darwin')
    def test_deployment_command_macos(self, mock_platform, server_agent):
        """Test macOS deployment command"""
        command = server_agent.get_deployment_command()
        
        assert "brew" in command
        assert "test-token-server" in command
    
    @patch('platform.system', return_value='Windows')
    def test_deployment_command_windows(self, mock_platform, server_agent):
        """Test Windows deployment command"""
        command = server_agent.get_deployment_command()
        
        assert "powershell" in command
        assert "test-token-server" in command
    
    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run')
    def test_start_linux(self, mock_run, mock_platform, server_agent):
        """Test starting agent on Linux"""
        server_agent.start()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "systemctl start" in call_args[0][0]
    
    @patch('platform.system', return_value='Windows')
    @patch('sys.platform', 'win32')
    @patch('subprocess.run')
    def test_start_windows(self, mock_run, mock_platform, server_agent):
        """Test starting agent on Windows"""
        # Force the platform check to use Windows
        with patch('sys.platform', 'win32'):
            with patch('platform.system', return_value='Windows'):
                import sys
                original_platform = sys.platform
                try:
                    sys.platform = 'win32'
                    server_agent.start()
                finally:
                    sys.platform = original_platform
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "net start" in call_args[0][0]
    
    @patch('platform.system', return_value='Linux')
    @patch('subprocess.run')
    def test_stop_linux(self, mock_run, mock_platform, server_agent):
        """Test stopping agent on Linux"""
        server_agent.stop()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "systemctl stop" in call_args[0][0]
    
    @patch('psutil.cpu_percent')
    @patch('psutil.cpu_count')
    def test_get_cpu_metrics(self, mock_cpu_count, mock_cpu_percent, server_agent):
        """Test CPU metrics collection"""
        mock_cpu_percent.return_value = 45.5
        mock_cpu_count.return_value = 4
        
        metrics = server_agent._get_cpu_metrics()
        
        assert metrics["cpu_percent"] == 45.5
        assert metrics["cpu_count"] == 4
    
    @patch('psutil.virtual_memory')
    def test_get_memory_metrics(self, mock_memory, server_agent):
        """Test memory metrics collection"""
        mock_memory.return_value = MagicMock(
            total=16000000000,
            available=8000000000,
            used=8000000000,
            percent=50.0
        )
        
        metrics = server_agent._get_memory_metrics()
        
        assert metrics["total"] == 16000000000
        assert metrics["used"] == 8000000000
        assert metrics["percent"] == 50.0
    
    @patch('psutil.disk_usage')
    def test_get_disk_metrics(self, mock_disk, server_agent):
        """Test disk metrics collection"""
        mock_disk.return_value = MagicMock(
            total=1000000000000,
            used=500000000000,
            free=500000000000,
            percent=50.0
        )
        
        metrics = server_agent._get_disk_metrics()
        
        assert metrics["total"] == 1000000000000
        assert metrics["percent"] == 50.0
    
    @patch('psutil.net_io_counters')
    def test_get_network_metrics(self, mock_net, server_agent):
        """Test network metrics collection"""
        mock_net.return_value = MagicMock(
            bytes_sent=1000000,
            bytes_recv=2000000,
            packets_sent=500,
            packets_recv=1000
        )
        
        metrics = server_agent._get_network_metrics()
        
        assert metrics["bytes_sent"] == 1000000
        assert metrics["bytes_recv"] == 2000000
    
    @patch('psutil.cpu_percent', return_value=30)
    @patch('psutil.cpu_count', return_value=8)
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    @patch('psutil.net_io_counters')
    @patch('platform.system', return_value='Linux')
    def test_gather_data_complete(self, mock_platform, mock_net, mock_disk, 
                                   mock_memory, mock_cpu_count, mock_cpu_percent, 
                                   server_agent):
        """Test complete data gathering"""
        mock_memory.return_value = MagicMock(
            total=16000000000,
            available=8000000000,
            used=8000000000,
            percent=50.0
        )
        mock_disk.return_value = MagicMock(
            total=1000000000000,
            used=500000000000,
            free=500000000000,
            percent=50.0
        )
        mock_net.return_value = MagicMock(
            bytes_sent=1000000,
            bytes_recv=2000000,
            packets_sent=500,
            packets_recv=1000
        )
        
        data = server_agent._gather_data()
        
        assert "system_info" in data
        assert "cpu_metrics" in data
        assert "memory_metrics" in data
        assert "disk_metrics" in data
        assert "network_metrics" in data
