# Agent Connector System

A flexible, extensible system for deploying agents across different infrastructure types.

## Architecture

```
connectors/
├── core/
│   ├── __init__.py
│   └── base_agent.py          # Abstract base class with shared logic
├── docker/
│   ├── __init__.py
│   └── docker_agent.py        # Docker container deployment
├── kubernetes/
│   ├── __init__.py
│   └── k8s_agent.py           # Kubernetes cluster deployment
├── server/
│   ├── __init__.py
│   └── server_agent.py        # Linux, macOS, Windows server deployment
├── __init__.py
└── agent_factory.py           # Factory pattern for agent creation
```

## Key Features

### 1. **Unified Interface**
All agents inherit from `BaseAgent` and implement a common interface:
- `get_deployment_command()` - Get deployment instructions
- `start()` / `stop()` - Lifecycle management
- `collect_metrics()` - Gather environment data
- `send_data()` - Send data to platform
- `heartbeat()` - Health check

### 2. **Shared Core Logic**
`BaseAgent` provides:
- **Authentication**: Secure token-based API sessions
- **Network Communication**: `send_data()` and `heartbeat()` methods
- **Metrics Collection**: Abstract framework for gathering metrics
- **Error Handling**: Consistent exception handling

### 3. **Infrastructure-Specific Implementations**

#### Docker Agent
```python
agent = AgentFactory.create_agent(
    agent_type="docker",
    platform_url="https://api.example.com",
    agent_token="docker-token",
    config={"log_level": "debug"}
)

print(agent.get_deployment_command())
# Output:
# docker run -d --name incident-rca-agent \
#   -e PLATFORM_API_URL=https://api.example.com \
#   -e AGENT_TOKEN=docker-token \
#   -e AGENT_TYPE=docker \
#   -e LOG_LEVEL=debug \
#   incident-rca/agent:latest
```

#### Kubernetes Agent
```python
agent = AgentFactory.create_agent(
    agent_type="kubernetes",
    platform_url="https://api.example.com",
    agent_token="k8s-token",
    config={
        "namespace": "monitoring",
        "release_name": "incident-rca",
        "replicas": "2"
    }
)

print(agent.get_deployment_command())
# Output:
# helm repo add incident-rca https://charts.example.com && \
# helm install incident-rca incident-rca/agent \
#   --namespace monitoring \
#   --set platformUrl=https://api.example.com \
#   --set agentToken=k8s-token \
#   --set replicas=2
```

#### Server Agent
```python
agent = AgentFactory.create_agent(
    agent_type="server",
    platform_url="https://api.example.com",
    agent_token="server-token"
)

print(agent.get_deployment_command())
# Output (auto-detects OS):
# Linux:   curl -fsSL https://install.example.com/agent.sh | bash -s -- ...
# macOS:   brew tap incident-rca/agent && brew install ...
# Windows: powershell -Command "irm https://install.example.com/agent.ps1 | iex" ...
```

### 4. **Factory Pattern**
Simple, consistent agent creation:
```python
from connectors.agent_factory import AgentFactory

# Create any agent type with same interface
agent = AgentFactory.create_agent(
    agent_type="docker",  # or "kubernetes", "server"
    platform_url="https://api.example.com",
    agent_token="your-token",
    config={}  # optional
)

# List supported types
types = AgentFactory.list_supported_types()
# ['docker', 'kubernetes', 'server']
```

## Shared Core Functionality

### Authentication
All agents automatically authenticate with the platform:
```python
# Session headers are automatically set with Bearer token
headers = {
    "Authorization": "Bearer {agent_token}",
    "Content-Type": "application/json"
}
```

### Sending Data to Platform
```python
data = {
    "metrics": {...},
    "timestamp": "2026-01-23T...",
    "agent_type": "docker"
}

success = agent.send_data(data)
# Automatically handles errors and retries
```

### Health Checks
```python
is_healthy = agent.heartbeat()
# Sends periodic status to platform
```

### Metrics Collection
```python
metrics = agent.collect_metrics()
# Returns:
# {
#     "agent_type": "docker",
#     "timestamp": "2026-01-23T...",
#     "data": {...}  # environment-specific data
# }
```

## Backend Integration

### API Routes
The system includes FastAPI routes in `app/api/agent_routes.py`:

```python
# POST /api/v1/agent/provision
# Generate deployment command for customer
{
    "agent_type": "docker",
    "environment_name": "prod-cluster-1",
    "config": {"log_level": "debug"}
}

# Response:
{
    "agent_type": "docker",
    "environment_name": "prod-cluster-1",
    "agent_token": "agent_prod-cluster-1_...",
    "deployment_command": "docker run -d ...",
    "instructions": "1. Ensure Docker is installed..."
}
```

```python
# GET /api/v1/agent/types
# List supported agent types
{
    "types": ["docker", "kubernetes", "server"],
    "descriptions": {
        "docker": "Deploy as Docker container",
        "kubernetes": "Deploy to Kubernetes cluster using Helm",
        "server": "Install on Linux, macOS, or Windows server"
    }
}
```

## Testing

### Run All Tests
```bash
pytest tests/
```

### Run Specific Test File
```bash
pytest tests/test_docker_agent.py -v
```

### Run with Coverage
```bash
pytest tests/ --cov=connectors --cov=app
```

### Test Coverage
- **48 tests** covering all agent types
- **56% code coverage** with focus on core functionality
- Tests for:
  - Agent creation and initialization
  - Deployment command generation
  - Authentication and API communication
  - Metrics collection
  - Error handling
  - Factory pattern

## Adding New Agent Types

To add a new infrastructure type (e.g., AWS Lambda):

1. **Create new file** in `connectors/lambda/lambda_agent.py`
```python
from connectors.core.base_agent import BaseAgent

class LambdaAgent(BaseAgent):
    @property
    def agent_type(self) -> str:
        return "lambda"
    
    def get_deployment_command(self) -> str:
        # Return CloudFormation/SAM command
        pass
    
    def _gather_data(self) -> Dict[str, Any]:
        # Gather Lambda-specific metrics
        pass
    
    # Implement start(), stop()
```

2. **Register in factory** `connectors/agent_factory.py`:
```python
from connectors.lambda.lambda_agent import LambdaAgent

class AgentFactory:
    _agents = {
        "docker": DockerAgent,
        "kubernetes": K8sAgent,
        "server": ServerAgent,
        "lambda": LambdaAgent,  # Add new type
    }
```

3. **Add tests** in `tests/test_lambda_agent.py`

4. **No changes needed to base classes** - inheritance handles the rest!

## Environment-Specific Metrics

Each agent gathers relevant metrics:

### Docker Agent
- Container info (ID, state, config)
- Docker stats (CPU, memory, network)

### Kubernetes Agent
- Pod information
- Node information
- Namespace quotas

### Server Agent
- System information (OS, hostname)
- CPU metrics (usage, core count)
- Memory metrics (total, used, available)
- Disk metrics (usage, available space)
- Network metrics (bytes/packets sent/received)

## Security Considerations

1. **Token Generation**: Tokens are randomly generated per environment
2. **Bearer Authentication**: All API calls use Bearer tokens
3. **HTTPS**: Use HTTPS URLs in production
4. **Token Storage**: Tokens should be securely stored in database
5. **Rotation**: Implement token rotation policies

## Example Usage

See `example_agent_usage.py` for a complete working example:

```bash
python example_agent_usage.py
```

Output shows:
- Deployment commands for each agent type
- Metrics collection example
- Supported agent types

## Dependencies

### Core
- `requests` - HTTP client for API calls
- `datetime` - Timestamp generation

### Docker Agent
- `subprocess` - Docker command execution
- `json` - Docker output parsing

### Kubernetes Agent
- `kubernetes` - K8s Python client

### Server Agent
- `psutil` - System metrics
- `platform` - OS detection
- `subprocess` - Service management

### Testing
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities

Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

## Configuration

Agents accept custom configuration through the `config` parameter:

```python
agent = AgentFactory.create_agent(
    agent_type="docker",
    platform_url="https://api.example.com",
    agent_token="token",
    config={
        "log_level": "debug",
        "max_batch_size": "1000",
        "retry_count": "3"
    }
)
```

Config values are:
- Passed to deployment commands as environment variables
- Stored in agent instance for runtime use
- Infrastructure-specific or shared as needed

## License

Part of the Incident RCA platform.
