# Agent Connector System Architecture

## Project Structure

```
connectors/
├── __init__.py
├── agent_factory.py          # Factory for creating agents
├── README.md
│
├── core/
│   ├── __init__.py
│   ├── base_agent.py         # Abstract base class for all agents
│   └── agent_config.py       # Shared configuration (optional)
│
├── api/
│   ├── __init__.py
│   └── agent_routes.py       # FastAPI routes for agent provisioning
│
├── docker/
│   ├── __init__.py
│   ├── docker_agent.py       # Docker-specific agent implementation
│   └── agent.py              # Legacy support
│
├── kubernetes/
│   ├── __init__.py
│   └── k8s_agent.py          # Kubernetes-specific agent implementation
│
└── server/
    ├── __init__.py
    └── server_agent.py       # VM/Server-specific agent implementation
```

## Architecture Overview

### Core Design Patterns

1. **Inheritance Hierarchy**
   ```
   BaseAgent (abstract)
   ├── DockerAgent
   ├── K8sAgent
   └── ServerAgent
   ```

2. **Factory Pattern**
   - `AgentFactory` creates appropriate agent instances based on type
   - Centralizes agent creation logic
   - Easy to register new agent types

3. **Separation of Concerns**
   - **`core/`**: Shared functionality (authentication, metrics collection, heartbeat)
   - **`docker/`**: Docker-specific deployment and monitoring
   - **`kubernetes/`**: Kubernetes-specific deployment and monitoring
   - **`server/`**: OS-specific deployment and system metrics
   - **`api/`**: HTTP API for agent provisioning

## Backend Integration

### Import Paths

**Option 1: Direct from connectors.api**
```python
from connectors.api import router

app = FastAPI()
app.include_router(router)
```

**Option 2: Via app/api for backward compatibility**
```python
from app.api.agent_routes import router

app = FastAPI()
app.include_router(router)
```

Both work because `app/api/agent_routes.py` re-exports from `connectors/api/agent_routes.py`.

### API Endpoints

All endpoints are prefixed with `/api/v1/agent`:

1. **POST `/provision`** - Generate agent deployment command
   - Request: `agent_type`, `environment_name`, `config` (optional)
   - Response: `deployment_command`, `agent_token`, `instructions`

2. **GET `/types`** - List supported agent types
   - Response: List of available agent types with descriptions

## Usage Examples

### Creating Agents Programmatically

```python
from connectors.agent_factory import AgentFactory

# Create Docker agent
docker_agent = AgentFactory.create_agent(
    agent_type="docker",
    platform_url="http://localhost:8000",
    agent_token="token-123",
    config={"log_level": "debug"}
)

# Get deployment command
command = docker_agent.get_deployment_command()
print(command)
# Output: docker run -d --name incident-rca-agent \
#         -e PLATFORM_API_URL=http://localhost:8000 \
#         -e AGENT_TOKEN=token-123 \
#         -e LOG_LEVEL=debug \
#         incident-rca/agent:latest
```

### Via HTTP API

```bash
# Request deployment command for Kubernetes
curl -X POST http://localhost:8000/api/v1/agent/provision \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "kubernetes",
    "environment_name": "prod-cluster",
    "config": {
      "namespace": "monitoring",
      "replicas": 2
    }
  }'

# Response
{
  "agent_type": "kubernetes",
  "environment_name": "prod-cluster",
  "deployment_command": "helm repo add incident-rca ... helm install incident-rca ...",
  "instructions": "1. Ensure Helm 3+ is installed...",
  "agent_token": "agent_prod-cluster_xyz..."
}
```

## Implementation Details

### BaseAgent Class

Provides shared functionality for all agents:
- **Authentication**: Session management with bearer tokens
- **Data Collection**: `collect_metrics()` method
- **Data Transmission**: `send_data()` to platform
- **Heartbeat**: Regular `heartbeat()` calls to platform
- **Abstract Methods**: Each subclass must implement:
  - `start()` - Start the agent
  - `stop()` - Stop the agent
  - `get_deployment_command()` - Return deployment command
  - `_gather_data()` - Collect environment-specific metrics

### DockerAgent

- **Deployment**: `docker run` command with environment variables
- **Metrics**: Container info, Docker stats
- **Control**: `docker start/stop`

### K8sAgent

- **Deployment**: Helm chart installation
- **Metrics**: Pod info, node info, namespace quotas
- **Control**: `helm install/uninstall`
- **Configuration**: Namespace, release name

### ServerAgent

- **Deployment**: Platform-specific install commands
  - Linux: curl + bash script
  - macOS: Homebrew
  - Windows: PowerShell
- **Metrics**: CPU, memory, disk, network, system info
- **Control**: systemctl (Linux/macOS), net (Windows)

## Testing

### Test Coverage: 59%
- **57 passing tests**
- Unit tests for each agent type
- Factory pattern tests
- API integration tests

### Run Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_docker_agent.py

# With coverage report
pytest tests/ --cov

# Watch mode
pytest-watch tests/
```

## Key Features

✅ **Abstraction**: Common logic in `BaseAgent`, infrastructure-specific in subclasses  
✅ **Extensibility**: Add new agent types by extending `BaseAgent`  
✅ **Type Safety**: Factory pattern prevents runtime errors  
✅ **API Integration**: FastAPI endpoints for provisioning  
✅ **Cross-Platform**: Support for Docker, Kubernetes, Linux, macOS, Windows  
✅ **Security**: Token-based authentication  
✅ **Monitoring**: Built-in heartbeat and metrics collection  

## Future Enhancements

- [ ] Agent health monitoring dashboard
- [ ] Automatic agent updates
- [ ] Agent version management
- [ ] Custom metrics collection per agent
- [ ] Agent clustering/grouping
- [ ] Webhook notifications on agent status changes
