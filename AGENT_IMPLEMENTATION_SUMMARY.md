# Connector Runtime Agent Summary

The connectors package now only ships the runtime agent. The SDK is in `sdk/`.
provisioning API, agent factory, and deployment helpers were removed.

## Current Components

- `connectors/docker/agent.py`: runtime agent (auth, heartbeat, data upload)
- `sdk/core/base_agent.py`: shared HTTP client and send_data helpers
- `sdk/core/collector.py`: collector SDK + registry
- `sdk/collectors/builtin.py`: built-in collectors

## Platform Endpoints Used

- `POST /api/v1/agent/authenticate`
- `POST /api/v1/agent/heartbeat`
- `POST /api/v1/agent/data`
