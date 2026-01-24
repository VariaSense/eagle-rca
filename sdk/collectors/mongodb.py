"""MongoDB collector for runtime agents."""
from __future__ import annotations

from typing import Any, Dict

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from sdk.core.collector import BaseCollector, register_collector


@register_collector("mongodb")
class MongoDBCollector(BaseCollector):
    """Collect basic MongoDB health and stats."""

    def collect(self) -> Dict[str, Any]:
        uri = self.config.get("uri")
        if not uri:
            return {"metrics": {"mongodb.configured": 0}, "payload": {"error": "missing_uri"}}

        metrics: Dict[str, Any] = {"mongodb.configured": 1}
        payload: Dict[str, Any] = {}
        database = self.config.get("database")
        collection = self.config.get("collection")

        try:
            with MongoClient(uri, serverSelectionTimeoutMS=3000) as client:
                client.admin.command("ping")
                metrics["mongodb.ping"] = 1

                try:
                    status = client.admin.command("serverStatus")
                    connections = status.get("connections", {})
                    opcounters = status.get("opcounters", {})
                    metrics.update(
                        {
                            "mongodb.connections_current": connections.get("current", 0),
                            "mongodb.connections_available": connections.get("available", 0),
                            "mongodb.opcounters_insert": opcounters.get("insert", 0),
                            "mongodb.opcounters_update": opcounters.get("update", 0),
                            "mongodb.opcounters_delete": opcounters.get("delete", 0),
                            "mongodb.opcounters_query": opcounters.get("query", 0),
                        }
                    )
                except PyMongoError:
                    payload["server_status"] = "unavailable"

                if database and collection:
                    try:
                        coll = client[database][collection]
                        payload["collection_stats"] = {
                            "database": database,
                            "collection": collection,
                            "document_count": coll.estimated_document_count(),
                        }
                    except PyMongoError as exc:
                        payload["collection_stats_error"] = str(exc)

        except PyMongoError as exc:
            metrics["mongodb.ping"] = 0
            payload["error"] = str(exc)

        return {"metrics": metrics, "payload": payload}
