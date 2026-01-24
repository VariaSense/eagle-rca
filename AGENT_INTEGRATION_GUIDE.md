# Connector Agent Integration Guide

The runtime agent does not expose any HTTP API. It only talks to the platform
backend using these endpoints:

- `POST /api/v1/agent/authenticate`
- `POST /api/v1/agent/heartbeat`
- `POST /api/v1/agent/data`

If you need provisioning workflows, implement them in the platform backend
and store agent tokens in your database.
