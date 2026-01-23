"""Agent provisioning and management API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from connectors.agent_factory import AgentFactory
import logging
import secrets

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/agent", tags=["agent"])


class AgentDeploymentRequest(BaseModel):
    """Request to generate agent deployment command"""
    agent_type: str  # "docker", "kubernetes", "server"
    environment_name: str
    config: Optional[Dict[str, Any]] = None


class AgentDeploymentResponse(BaseModel):
    """Response with deployment command"""
    environment_name: str
    agent_type: str
    deployment_command: str
    instructions: str
    agent_token: str


class SupportedAgentTypesResponse(BaseModel):
    """Response with supported agent types"""
    types: List[str]
    descriptions: Dict[str, str]


@router.post("/provision", response_model=AgentDeploymentResponse)
async def provision_agent(request: AgentDeploymentRequest):
    """Generate provisioning command for agent"""
    try:
        # Validate agent type
        if request.agent_type not in AgentFactory.list_supported_types():
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported agent type: {request.agent_type}"
            )
        
        # Generate token for this environment
        agent_token = f"agent_{request.environment_name}_{generate_token()}"
        
        # Create agent instance
        agent = AgentFactory.create_agent(
            agent_type=request.agent_type,
            platform_url="http://your-platform.com",  # from config
            agent_token=agent_token,
            config=request.config or {}
        )
        
        # Get deployment command
        deployment_command = agent.get_deployment_command()
        
        # Store token in database for later validation
        # await store_agent_token(request.environment_name, agent_token)
        
        # Return deployment info
        return AgentDeploymentResponse(
            environment_name=request.environment_name,
            agent_type=request.agent_type,
            deployment_command=deployment_command,
            instructions=get_deployment_instructions(request.agent_type),
            agent_token=agent_token
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to provision agent: {e}")
        raise HTTPException(status_code=500, detail="Failed to provision agent")


@router.get("/types", response_model=SupportedAgentTypesResponse)
async def get_supported_agent_types():
    """Get list of supported agent types"""
    return SupportedAgentTypesResponse(
        types=AgentFactory.list_supported_types(),
        descriptions={
            "docker": "Deploy as Docker container",
            "kubernetes": "Deploy to Kubernetes cluster using Helm",
            "server": "Install on Linux, macOS, or Windows server"
        }
    )


def generate_token() -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(32)


def get_deployment_instructions(agent_type: str) -> str:
    """Get deployment instructions for agent type"""
    instructions = {
        "docker": (
            "1. Ensure Docker is installed and running\n"
            "2. Copy the command below\n"
            "3. Run it in your terminal\n"
            "4. Agent will appear as 'pending' once it connects"
        ),
        "kubernetes": (
            "1. Ensure Helm 3+ is installed\n"
            "2. Have kubeconfig configured for your cluster\n"
            "3. Copy the command below\n"
            "4. Run it in your terminal\n"
            "5. Agent will appear as 'pending' once it connects"
        ),
        "server": (
            "1. Run as root or with sudo\n"
            "2. Copy the command below\n"
            "3. Execute in your terminal\n"
            "4. Agent will register after installation"
        )
    }
    return instructions.get(agent_type, "Follow the command output")
