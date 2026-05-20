"""
Metrics Collector - System metrics collection and monitoring
"""

import asyncio
from typing import Any, Dict, List
from datetime import datetime

from loguru import logger


class MetricsCollector:
    """Collect and aggregate system metrics."""

    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}
        self.collection_interval = 60  # seconds

    async def collect(self, component: str, metrics: Dict[str, Any]):
        """Collect metrics from a component."""
        if component not in self.metrics:
            self.metrics[component] = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            **metrics,
        }

        self.metrics[component].append(entry)

        # Keep only last 1000 entries per component
        if len(self.metrics[component]) > 1000:
            self.metrics[component] = self.metrics[component][-1000:]

    async def get_metrics(self, component: str = None) -> Dict[str, Any]:
        """Get collected metrics."""
        if component:
            return {component: self.metrics.get(component, [])}
        return self.metrics

    async def get_latest(self, component: str) -> Dict[str, Any]:
        """Get latest metrics for a component."""
        if component not in self.metrics or not self.metrics[component]:
            return {}

        return self.metrics[component][-1]

    async def clear(self):
        """Clear all collected metrics."""
        self.metrics.clear()
        logger.info("Metrics cleared")
