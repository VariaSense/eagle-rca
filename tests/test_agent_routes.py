import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import FastAPI
from connectors.api.agent_routes import router

# Create a test app with the router
app = FastAPI()
app.include_router(router)
client = TestClient(app)


class TestAgentRoutes:
    
    def test_provision_docker_agent(self):
        """Test provisioning docker agent via API"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "docker",
                "environment_name": "prod-cluster-1",
                "config": {"log_level": "debug"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "docker"
        assert data["environment_name"] == "prod-cluster-1"
        assert "docker run" in data["deployment_command"]
        assert "debug" in data["deployment_command"]
        assert "agent_token" in data
    
    def test_provision_kubernetes_agent(self):
        """Test provisioning kubernetes agent via API"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "kubernetes",
                "environment_name": "staging-cluster",
                "config": {"namespace": "monitoring"}
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "kubernetes"
        assert "helm install" in data["deployment_command"]
        assert "agent_token" in data
    
    def test_provision_server_agent(self):
        """Test provisioning server agent via API"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "server",
                "environment_name": "vm-server-1"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "server"
        assert "agent_token" in data
    
    def test_provision_invalid_agent_type(self):
        """Test provisioning with invalid agent type"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "invalid",
                "environment_name": "test"
            }
        )
        
        assert response.status_code == 400
        assert "Unsupported agent type" in response.json()["detail"]
    
    def test_get_supported_agent_types(self):
        """Test retrieving supported agent types"""
        response = client.get("/api/v1/agent/types")
        
        assert response.status_code == 200
        data = response.json()
        assert "docker" in data["types"]
        assert "kubernetes" in data["types"]
        assert "server" in data["types"]
        assert "descriptions" in data
        assert len(data["types"]) == 3
    
    def test_deployment_command_includes_token(self):
        """Test that deployment commands include agent tokens"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "docker",
                "environment_name": "test-env"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        token = data["agent_token"]
        command = data["deployment_command"]
        
        assert token.startswith("agent_test-env_")
        assert token in command
    
    def test_docker_deployment_instructions(self):
        """Test Docker agent includes proper instructions"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "docker",
                "environment_name": "test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        instructions = data["instructions"]
        
        assert "Docker" in instructions
        assert "terminal" in instructions
    
    def test_k8s_deployment_instructions(self):
        """Test Kubernetes agent includes proper instructions"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "kubernetes",
                "environment_name": "test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        instructions = data["instructions"]
        
        assert "Helm" in instructions
        assert "kubeconfig" in instructions
    
    def test_server_deployment_instructions(self):
        """Test Server agent includes proper instructions"""
        response = client.post(
            "/api/v1/agent/provision",
            json={
                "agent_type": "server",
                "environment_name": "test"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        instructions = data["instructions"]
        
        assert "sudo" in instructions
        assert "terminal" in instructions
