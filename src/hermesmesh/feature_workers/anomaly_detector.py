"""
Anomaly Detector - Statistical anomaly detection
"""

import asyncio
from typing import Any, Dict, List

from loguru import logger


class AnomalyDetector:
    """Detect anomalies in quantitative data."""

    def __init__(self, threshold: float = 3.0):
        self.threshold = threshold
        self.history: List[Dict[str, Any]] = []

    async def detect(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect anomalies in the data."""
        anomalies = []

        # Check each numeric value
        for key, value in data.items():
            if isinstance(value, (int, float)):
                anomaly = await self._check_value(key, value)
                if anomaly:
                    anomalies.append(anomaly)

        # Store in history
        self.history.append({"data": data, "anomalies": anomalies})

        # Keep only last 1000 entries
        if len(self.history) > 1000:
            self.history = self.history[-1000:]

        return anomalies

    async def _check_value(
        self, name: str, value: float
    ) -> Dict[str, Any]:
        """Check if a value is anomalous."""
        # Simple threshold-based detection
        if abs(value) > self.threshold:
            return {
                "factor": name,
                "value": value,
                "threshold": self.threshold,
                "type": "extreme_value",
                "severity": "high" if abs(value) > self.threshold * 2 else "medium",
            }

        return None

    async def detect_batch(
        self, batch: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """Detect anomalies in a batch of data."""
        tasks = [self.detect(item) for item in batch]
        return await asyncio.gather(*tasks)

    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        total_anomalies = sum(
            len(entry["anomalies"]) for entry in self.history
        )

        return {
            "total_checks": len(self.history),
            "total_anomalies": total_anomalies,
            "anomaly_rate": total_anomalies / max(1, len(self.history)),
        }
