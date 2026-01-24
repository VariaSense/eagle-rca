"""Docker container log collector."""
from __future__ import annotations

from typing import Any, Dict, List
import time

import docker
from docker.errors import DockerException

from sdk.core.collector import BaseCollector, register_collector


@register_collector("docker_logs")
class DockerLogsCollector(BaseCollector):
    """Collect recent logs from Docker containers."""

    def collect(self) -> Dict[str, Any]:
        tail_lines = int(self.config.get("tail_lines", 200))
        since_seconds = int(self.config.get("since_seconds", 300))
        max_bytes = int(self.config.get("max_bytes", 50000))
        include_names = set(self.config.get("include_names", []))
        exclude_names = set(self.config.get("exclude_names", []))

        payload: Dict[str, Any] = {"containers": []}
        metrics: Dict[str, Any] = {}
        since_ts = int(time.time()) - since_seconds

        try:
            client = docker.from_env()
            containers = client.containers.list(all=False)
            metrics["docker_logs.containers_seen"] = len(containers)
            for container in containers:
                name = container.name or ""
                if include_names and name not in include_names:
                    continue
                if exclude_names and name in exclude_names:
                    continue
                logs = container.logs(
                    tail=tail_lines,
                    since=since_ts,
                    stdout=True,
                    stderr=True,
                )
                if isinstance(logs, bytes):
                    logs_text = logs.decode(errors="replace")
                else:
                    logs_text = str(logs)
                if max_bytes > 0:
                    logs_text = logs_text[-max_bytes:]
                payload["containers"].append(
                    {
                        "id": container.id,
                        "name": name,
                        "image": container.image.tags[0] if container.image.tags else "",
                        "logs": logs_text,
                    }
                )
        except DockerException as exc:
            payload["error"] = str(exc)

        return {"metrics": metrics, "payload": payload}
