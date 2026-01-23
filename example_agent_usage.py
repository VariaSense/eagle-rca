"""Quick example of using the agent factory"""
from connectors.agent_factory import AgentFactory

def main():
    print("=" * 60)
    print("Agent Connector System - Usage Examples")
    print("=" * 60)
    
    # Example 1: Create Docker Agent
    print("\n1. Docker Agent:")
    docker_agent = AgentFactory.create_agent(
        agent_type="docker",
        platform_url="https://api.example.com",
        agent_token="docker-token-xyz",
        config={"log_level": "info", "max_batch_size": "500"}
    )
    print(f"   Type: {docker_agent.agent_type}")
    print(f"   Deployment Command:\n{docker_agent.get_deployment_command()}\n")
    
    # Example 2: Create Kubernetes Agent
    print("2. Kubernetes Agent:")
    k8s_agent = AgentFactory.create_agent(
        agent_type="kubernetes",
        platform_url="https://api.example.com",
        agent_token="k8s-token-abc",
        config={
            "namespace": "monitoring",
            "release_name": "incident-rca",
            "replicas": "3"
        }
    )
    print(f"   Type: {k8s_agent.agent_type}")
    print(f"   Namespace: {k8s_agent.namespace}")
    print(f"   Deployment Command:\n{k8s_agent.get_deployment_command()}\n")
    
    # Example 3: Create Server Agent
    print("3. Server Agent:")
    server_agent = AgentFactory.create_agent(
        agent_type="server",
        platform_url="https://api.example.com",
        agent_token="server-token-def"
    )
    print(f"   Type: {server_agent.agent_type}")
    print(f"   Deployment Command:\n{server_agent.get_deployment_command()}\n")
    
    # Example 4: List supported types
    print("4. Supported Agent Types:")
    types = AgentFactory.list_supported_types()
    for agent_type in types:
        print(f"   - {agent_type}")
    
    # Example 5: Collect metrics
    print("\n5. Collecting Metrics (Server Agent):")
    metrics = server_agent.collect_metrics()
    print(f"   Agent Type: {metrics['agent_type']}")
    print(f"   Timestamp: {metrics['timestamp']}")
    print(f"   Data Keys: {list(metrics['data'].keys())}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
