"""
Quick integration guide for adding agent routes to FastAPI app.

Add this to your app/main.py or wherever your FastAPI app is initialized:
"""

# In your main.py or app initialization file:

from fastapi import FastAPI
from app.api import agent_routes  # Import the agent routes module

app = FastAPI(
    title="Incident RCA Platform",
    description="Platform for incident root cause analysis"
)

# Include agent provisioning routes
app.include_router(agent_routes.router)

# Your other routes...
# app.include_router(other_routes.router)

# This adds:
# - POST   /api/v1/agent/provision       - Generate deployment command
# - GET    /api/v1/agent/types           - List supported agent types

# Now your customers can:
# 1. Call GET /api/v1/agent/types to see available options
# 2. Call POST /api/v1/agent/provision with their environment details
# 3. Receive a deployment command tailored to their infrastructure
# 4. Run the command to deploy the agent
# 5. Agent connects back to the platform and starts sending data

# Example flow:
# 
# Frontend: User selects "Docker" from infrastructure dropdown
# API Call: POST /api/v1/agent/provision
# {
#     "agent_type": "docker",
#     "environment_name": "production",
#     "config": {"log_level": "info"}
# }
# 
# Response:
# {
#     "agent_type": "docker",
#     "environment_name": "production",
#     "agent_token": "agent_production_...",
#     "deployment_command": "docker run -d --name incident-rca-agent ...",
#     "instructions": "1. Ensure Docker is installed..."
# }
# 
# Frontend: Display command to user with copy button
# User: Runs: docker run -d --name incident-rca-agent ...
# Agent: Connects back to platform and registers
# Platform: Shows agent as "active" in dashboard

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
