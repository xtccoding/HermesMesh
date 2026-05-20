"""
Worker Cluster A - Data extraction and processing
"""

import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger


class ClusterAWorker:
    """Cluster A worker for data extraction and processing."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.workers: List[asyncio.Task] = []
        self.is_running = False
        self.processed_count = 0

    async def start(self, instances: int = 5):
        """Start worker instances."""
        self.is_running = True

        for i in range(instances):
            task = asyncio.create_task(self._worker_loop(i))
            self.workers.append(task)

        logger.info(f"Cluster A started with {instances} instances")

    async def _worker_loop(self, worker_id: int):
        """Main worker loop."""
        logger.debug(f"Cluster A Worker {worker_id} started")

        while self.is_running:
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break

        logger.debug(f"Cluster A Worker {worker_id} stopped")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through Cluster A."""
        self.processed_count += 1

        # Extract entities, metrics, timestamps
        extracted = await self._extract_data(data)

        return {
            "cluster": "A",
            "processed_id": self.processed_count,
            "extracted": extracted,
            "original": data,
        }

    async def _extract_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured data from input."""
        await asyncio.sleep(0.02)

        return {
            "entities": [],
            "metrics": {},
            "timestamps": [],
            "sentiment": 0.0,
        }

    async def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        return {
            "cluster": "A",
            "is_running": self.is_running,
            "active_workers": len(self.workers),
            "processed_count": self.processed_count,
        }

    async def shutdown(self):
        """Shutdown all workers."""
        self.is_running = False

        for task in self.workers:
            task.cancel()

        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()

        logger.info("Cluster A shutdown complete")
