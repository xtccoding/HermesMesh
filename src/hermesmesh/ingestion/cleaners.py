"""
Data Cleaner - Stream cleaning and filtering
"""

import asyncio
from typing import Any, Dict, List

from loguru import logger


class DataCleaner:
    """Clean and filter ingested data."""

    def __init__(self, threshold: float = 0.8):
        self.threshold = threshold
        self.stats = {"total": 0, "cleaned": 0, "filtered": 0}

    async def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate data."""
        self.stats["total"] += 1

        # Check relevance score
        relevance = await self._calculate_relevance(data)

        if relevance < self.threshold:
            self.stats["filtered"] += 1
            logger.debug(f"Data filtered out (relevance: {relevance:.2f})")
            return None

        self.stats["cleaned"] += 1

        return {
            "cleaned": True,
            "relevance_score": relevance,
            "data": data,
            "metadata": {
                "original_length": len(str(data)),
                "cleaned_length": len(str(data)),
            },
        }

    async def _calculate_relevance(self, data: Dict[str, Any]) -> float:
        """Calculate data relevance score."""
        # Simulate relevance calculation
        await asyncio.sleep(0.01)
        
        content = data.get("raw_content", "")
        if not content:
            return 0.0

        # Simple heuristic: longer content = more relevant
        return min(1.0, len(content) / 1000)

    async def clean_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean a batch of data items."""
        tasks = [self.clean(item) for item in batch]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]

    def get_stats(self) -> Dict[str, int]:
        """Get cleaning statistics."""
        return self.stats.copy()
