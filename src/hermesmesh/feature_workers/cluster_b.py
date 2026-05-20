"""
Worker Cluster B - Factor calculation and anomaly detection
"""

import asyncio
from typing import Any, Dict, List, Optional

from loguru import logger


class ClusterBWorker:
    """Cluster B worker for factor calculation and analysis."""

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

        logger.info(f"Cluster B started with {instances} instances")

    async def _worker_loop(self, worker_id: int):
        """Main worker loop."""
        logger.debug(f"Cluster B Worker {worker_id} started")

        while self.is_running:
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break

        logger.debug(f"Cluster B Worker {worker_id} stopped")

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through Cluster B."""
        self.processed_count += 1

        # Calculate factors
        factors = await self._calculate_factors(data)

        # Detect anomalies
        anomalies = await self._detect_anomalies(factors)

        return {
            "cluster": "B",
            "processed_id": self.processed_count,
            "factors": factors,
            "anomalies": anomalies,
            "original": data,
        }

    async def _calculate_factors(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate quantitative factors."""
        await asyncio.sleep(0.03)

        return {
            "momentum": 0.0,
            "volatility": 0.0,
            "value": 0.0,
            "quality": 0.0,
            "growth": 0.0,
        }

    async def _detect_anomalies(self, factors: Dict[str, float]) -> List[Dict[str, Any]]:
        """Detect anomalies in factors."""
        await asyncio.sleep(0.01)

        anomalies = []
        for name, value in factors.items():
            if abs(value) > 3.0:  # Simple threshold
                anomalies.append({
                    "factor": name,
                    "value": value,
                    "type": "extreme_value",
                })

        return anomalies

    async def get_stats(self) -> Dict[str, Any]:
        """Get worker statistics."""
        return {
            "cluster": "B",
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

        logger.info("Cluster B shutdown complete")
