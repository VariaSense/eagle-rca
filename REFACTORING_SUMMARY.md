# Refactoring Summary: Connector Runtime Cleanup

Removed provisioning helpers and factory code from `connectors/` so it only
contains the runtime agent. The SDK lives in `sdk/`.

## Removed
- `connectors/api/agent_routes.py`
- `connectors/agent_factory.py`
- `connectors/docker/docker_agent.py`
- `connectors/kubernetes/k8s_agent.py`
- `connectors/server/server_agent.py`
- Associated tests and example usage

## Remaining
- `connectors/docker/agent.py` (runtime agent)
- `sdk/core/base_agent.py`
- `sdk/core/collector.py`
- `sdk/collectors/builtin.py`
