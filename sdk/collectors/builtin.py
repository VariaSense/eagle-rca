"""Built-in collectors for the docker agent."""
from __future__ import annotations

import os
import psutil
from typing import Any, Dict

from sdk.core.collector import BaseCollector, register_collector


@register_collector("system_stats")
class SystemStatsCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        metrics = {
            "cpu_percent": psutil.cpu_percent(interval=0.2),
            "cpu_count": psutil.cpu_count(logical=True) or 0,
            "load_avg_1m": os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0,
            "mem_total_bytes": psutil.virtual_memory().total,
            "mem_used_bytes": psutil.virtual_memory().used,
            "mem_used_percent": psutil.virtual_memory().percent,
            "disk_total_bytes": psutil.disk_usage("/").total,
            "disk_used_bytes": psutil.disk_usage("/").used,
            "disk_used_percent": psutil.disk_usage("/").percent,
        }
        return {"metrics": metrics, "payload": {}}


@register_collector("process_stats")
class ProcessStatsCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        processes = list(psutil.process_iter(attrs=["cpu_percent"]))
        cpu_total = sum(p.info.get("cpu_percent") or 0.0 for p in processes)
        metrics = {
            "process_count": len(processes),
            "process_cpu_total_percent": cpu_total,
        }
        return {"metrics": metrics, "payload": {}}


@register_collector("static")
class StaticCollector(BaseCollector):
    def collect(self) -> Dict[str, Any]:
        metrics = self.config.get("metrics", {})
        payload = self.config.get("payload", {})
        return {"metrics": metrics, "payload": payload}
