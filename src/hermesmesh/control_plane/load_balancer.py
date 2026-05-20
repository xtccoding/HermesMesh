"""
Load Balancer - Intelligent task distribution
"""

import asyncio
import random
from typing import Any, Dict, List, Optional

from loguru import logger


class LoadBalancer:
    """Intelligent load balancer for task distribution."""

    def __init__(self):
        self.workers: Dict[str, Dict[str, Any]] = {}
        self.strategy = "least_loaded"

    def register_worker(self, worker_id: str, metadata: Dict[str, Any] = None):
        """Register a worker with the load balancer."""
        self.workers[worker_id] = {
            "id": worker_id,
            "metadata": metadata or {},
            "current_load": 0,
            "total_processed": 0,
            "health": "healthy",
        }
        logger.info(f"Worker {worker_id} registered")

    def unregister_worker(self, worker_id: str):
        """Unregister a worker."""
        if worker_id in self.workers:
            del self.workers[worker_id]
            logger.info(f"Worker {worker_id} unregistered")

    def select_worker(self, task: Dict[str, Any]) -> str:
        """Select the best worker for a task."""
        if not self.workers:
            raise RuntimeError("No workers available")

        if self.strategy == "least_loaded":
            return self._select_least_loaded()
        elif self.strategy == "round_robin":
            return self._select_round_robin()
        else:
            return self._select_random()

    def _select_least_loaded(self) -> str:
        """Select worker with least load."""
        available = [
            w for w in self.workers.values() if w["health"] == "healthy"
        ]

        if not available:
            raise RuntimeError("No healthy workers available")

        selected = min(available, key=lambda w: w["current_load"])
        return selected["id"]

    def _select_round_robin(self) -> str:
        """Select worker using round-robin."""
        available = [
            w for w in self.workers.values() if w["health"] == "healthy"
        ]

        if not available:
            raise RuntimeError("No healthy workers available")

        # Simple round-robin based on total processed
        selected = min(available, key=lambda w: w["total_processed"])
        return selected["id"]

    def _select_random(self) -> str:
        """Select a random healthy worker."""
        available = [
            w for w in self.workers.values() if w["health"] == "healthy"
        ]

        if not available:
            raise RuntimeError("No healthy workers available")

        return random.choice(available)["id"]

    async def update_load(self, worker_id: str, load_delta: int):
        """Update worker load."""
        if worker_id in self.workers:
            self.workers[worker_id]["current_load"] += load_delta

    async def mark_task_complete(self, worker_id: str):
        """Mark a task as completed for a worker."""
        if worker_id in self.workers:
            self.workers[worker_id]["current_load"] = max(
                0, self.workers[worker_id]["current_load"] - 1
            )
            self.workers[worker_id]["total_processed"] += 1

    async def mark_worker_unhealthy(self, worker_id: str):
        """Mark a worker as unhealthy."""
        if worker_id in self.workers:
            self.workers[worker_id]["health"] = "unhealthy"
            logger.warning(f"Worker {worker_id} marked as unhealthy")

    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics."""
        healthy_count = sum(
            1 for w in self.workers.values() if w["health"] == "healthy"
        )

        return {
            "total_workers": len(self.workers),
            "healthy_workers": healthy_count,
            "strategy": self.strategy,
        }
