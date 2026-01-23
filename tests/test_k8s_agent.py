"""Tests for K8sAgent class"""
import pytest
from unittest.mock import patch, MagicMock
from connectors.kubernetes.k8s_agent import K8sAgent


class TestK8sAgent:
    
    @pytest.fixture
    def k8s_agent(self):
        return K8sAgent(
            platform_url="http://localhost:8000",
            agent_token="test-token-k8s",
            config={
                "namespace": "monitoring",
                "release_name": "incident-rca",
                "replicas": "2"
            }
        )
    
    def test_agent_type(self, k8s_agent):
        """Test K8s agent type"""
        assert k8s_agent.agent_type == "kubernetes"
    
    def test_namespace_from_config(self, k8s_agent):
        """Test namespace is set from config"""
        assert k8s_agent.namespace == "monitoring"
        assert k8s_agent.release_name == "incident-rca"
    
    def test_deployment_command_format(self, k8s_agent):
        """Test K8s deployment command format"""
        command = k8s_agent.get_deployment_command()
        
        assert "helm repo add" in command
        assert "helm install" in command
        assert "incident-rca" in command
        assert "monitoring" in command
    
    def test_deployment_command_includes_auth(self, k8s_agent):
        """Test deployment command includes authentication"""
        command = k8s_agent.get_deployment_command()
        
        assert "test-token-k8s" in command
        assert "http://localhost:8000" in command
    
    def test_deployment_command_includes_config(self, k8s_agent):
        """Test deployment command includes custom config"""
        command = k8s_agent.get_deployment_command()
        
        assert "replicas=2" in command
    
    @patch('subprocess.run')
    def test_start_k8s_agent(self, mock_run, k8s_agent):
        """Test deploying K8s agent"""
        k8s_agent.start()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "helm install" in call_args[0][0]
    
    @patch('subprocess.run')
    def test_stop_k8s_agent(self, mock_run, k8s_agent):
        """Test removing K8s agent"""
        k8s_agent.stop()
        
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "helm uninstall" in call_args[0][0]
        assert "incident-rca" in call_args[0][0]
    
    @patch('kubernetes.config.load_incluster_config')
    @patch('kubernetes.client.CoreV1Api')
    def test_gather_data_structure(self, mock_api_class, mock_load_config, k8s_agent):
        """Test gather_data returns expected structure"""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        with patch.object(k8s_agent, '_get_pod_info', return_value={"pods": []}):
            with patch.object(k8s_agent, '_get_node_info', return_value={"nodes": []}):
                with patch.object(k8s_agent, '_get_namespace_quota', return_value={}):
                    data = k8s_agent._gather_data()
        
        assert "pod_info" in data
        assert "node_info" in data
        assert "namespace_quota" in data
    
    @patch('kubernetes.client.CoreV1Api')
    def test_get_pod_info(self, mock_api_class, k8s_agent):
        """Test retrieving pod info"""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        mock_pod1 = MagicMock()
        mock_pod1.metadata.name = "agent-pod-1"
        mock_pod2 = MagicMock()
        mock_pod2.metadata.name = "agent-pod-2"
        
        mock_pods = MagicMock()
        mock_pods.items = [mock_pod1, mock_pod2]
        mock_api.list_namespaced_pod.return_value = mock_pods
        
        with patch('kubernetes.config.load_incluster_config', side_effect=Exception):
            with patch('kubernetes.config.load_kube_config'):
                pod_info = k8s_agent._get_pod_info(mock_api)
        
        assert pod_info["total_pods"] == 2
        assert "agent-pod-1" in pod_info["pods"]
    
    @patch('kubernetes.client.CoreV1Api')
    def test_get_node_info(self, mock_api_class, k8s_agent):
        """Test retrieving node info"""
        mock_api = MagicMock()
        mock_api_class.return_value = mock_api
        
        mock_node = MagicMock()
        mock_node.metadata.name = "worker-node-1"
        
        mock_nodes = MagicMock()
        mock_nodes.items = [mock_node]
        mock_api.list_node.return_value = mock_nodes
        
        node_info = k8s_agent._get_node_info(mock_api)
        
        assert node_info["total_nodes"] == 1
        assert "worker-node-1" in node_info["nodes"]
