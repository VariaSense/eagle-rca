"""Agent running in Kubernetes cluster"""
from connectors.core.base_agent import BaseAgent
from typing import Dict, Any
import subprocess
import logging

logger = logging.getLogger(__name__)


class K8sAgent(BaseAgent):
    """Agent running in Kubernetes cluster"""
    
    def __init__(self, platform_url: str, agent_token: str, config: Dict[str, Any] = None):
        super().__init__(platform_url, agent_token, config)
        self.namespace = self.config.get("namespace", "default")
        self.release_name = self.config.get("release_name", "incident-rca-agent")
    
    @property
    def agent_type(self) -> str:
        return "kubernetes"
    
    def get_deployment_command(self) -> str:
        """Generate kubectl/helm command for K8s deployment"""
        # Using Helm for K8s is more idiomatic
        return (
            f"helm repo add incident-rca https://charts.example.com && "
            f"helm repo update && "
            f"helm install {self.release_name} incident-rca/agent \\\n"
            f"  --namespace {self.namespace} \\\n"
            f"  --set platformUrl={self.platform_url} \\\n"
            f"  --set agentToken={self.agent_token} \\\n"
            f"  --set {self._build_helm_values()}"
        )
    
    def _build_helm_values(self) -> str:
        """Build Helm values from config"""
        values = [f"{k}={v}" for k, v in self.config.items() 
                 if k not in ["namespace", "release_name"]]
        return " --set ".join(values) if values else "version=latest"
    
    def start(self):
        """Deploy agent to K8s cluster"""
        cmd = self.get_deployment_command()
        subprocess.run(cmd, shell=True, check=True)
        logger.info("K8s agent deployed")
    
    def stop(self):
        """Remove agent from K8s cluster"""
        subprocess.run(
            f"helm uninstall {self.release_name} -n {self.namespace}",
            shell=True
        )
        logger.info("K8s agent removed")
    
    def _gather_data(self) -> Dict[str, Any]:
        """Gather K8s cluster metrics"""
        try:
            from kubernetes import client, config as k8s_config
            
            try:
                k8s_config.load_incluster_config()
            except:
                k8s_config.load_kube_config()
            
            v1 = client.CoreV1Api()
            
            return {
                "pod_info": self._get_pod_info(v1),
                "node_info": self._get_node_info(v1),
                "namespace_quota": self._get_namespace_quota(v1),
            }
        except Exception as e:
            logger.error(f"Failed to gather K8s data: {e}")
            return {}
    
    def _get_pod_info(self, v1) -> Dict[str, Any]:
        """Get pod information"""
        try:
            pods = v1.list_namespaced_pod(self.namespace)
            return {
                "total_pods": len(pods.items),
                "pods": [p.metadata.name for p in pods.items]
            }
        except Exception as e:
            logger.error(f"Failed to get pod info: {e}")
            return {}
    
    def _get_node_info(self, v1) -> Dict[str, Any]:
        """Get node information"""
        try:
            nodes = v1.list_node()
            return {
                "total_nodes": len(nodes.items),
                "nodes": [n.metadata.name for n in nodes.items]
            }
        except Exception as e:
            logger.error(f"Failed to get node info: {e}")
            return {}
    
    def _get_namespace_quota(self, v1) -> Dict[str, Any]:
        """Get namespace quota information"""
        try:
            quotas = v1.list_namespaced_resource_quota(self.namespace)
            return {f"quota_{q.metadata.name}": q.status.used for q in quotas.items}
        except Exception as e:
            logger.error(f"Failed to get quota info: {e}")
            return {}
