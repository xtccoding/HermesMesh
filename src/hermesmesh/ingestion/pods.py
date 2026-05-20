"""
Ingestion Pods - Edge data ingestion nodes
"""

import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger


class IngestionPod:
    """Single ingestion pod instance."""

    def __init__(self, pod_id: int, config: Dict[str, Any] = None):
        self.pod_id = pod_id
        self.config = config or {}
        self.is_running = False
        self.queue = asyncio.Queue()
        self.processed_count = 0

    async def start(self):
        """Start the ingestion pod."""
        self.is_running = True
        logger.info(f"Ingestion Pod {self.pod_id} started")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming data."""
        if not self.is_running:
            raise RuntimeError(f"Pod {self.pod_id} is not running")

        # Simulate processing
        await asyncio.sleep(0.01)
        self.processed_count += 1

        return {
            "pod_id": self.pod_id,
            "original": data,
            "processed": True,
            "count": self.processed_count,
        }

    async def stop(self):
        """Stop the ingestion pod."""
        self.is_running = False
        logger.info(f"Ingestion Pod {self.pod_id} stopped")


class IngestionPodManager:
    """Manages multiple ingestion pods."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.pods: List[IngestionPod] = []
        self.is_running = False

    async def start(self, workers: int = 5, batch_size: int = 100):
        """Start the pod manager with specified number of workers."""
        self.is_running = True
        self.pods = [IngestionPod(i) for i in range(workers)]

        for pod in self.pods:
            await pod.start()

        logger.info(f"IngestionPodManager started with {workers} workers")

    async def ingest_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Ingest a batch of data items."""
        if not self.is_running:
            raise RuntimeError("PodManager is not running")

        tasks = []
        for i, item in enumerate(batch):
            pod = self.pods[i % len(self.pods)]
            tasks.append(pod.process(item))

        return await asyncio.gather(*tasks)

    async def shutdown(self):
        """Shutdown all pods."""
        self.is_running = False
        for pod in self.pods:
            await pod.stop()

        logger.info("IngestionPodManager shutdown complete")
