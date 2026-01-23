# Docker Agent

Build the agent image:

```sh
docker build -t incident-rca/agent:latest .
```

Run the agent with your token:

```sh
docker run -d --name incident-rca-agent \
  -e PLATFORM_API_URL=http://localhost:8000/api/v1 \
  -e AGENT_TOKEN=YOUR_AGENT_TOKEN \
  incident-rca/agent:latest
```

Optional environment variables:
- `HEARTBEAT_INTERVAL` (seconds, default: 30)
- `SSL_VERIFY` (`true`/`false`, default: true)
- `COLLECT_SYSTEM_STATS` (`true`/`false`, default: true)
- `COMMAND_TIMEOUT` (seconds, default: 60)
- `MAX_OUTPUT_CHARS` (default: 20000)
