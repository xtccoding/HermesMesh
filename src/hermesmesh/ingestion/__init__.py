"""
Ingestion Module - Data ingestion and parsing from multiple sources
"""

from .pods import IngestionPodManager
from .parsers import DocumentParser
from .cleaners import DataCleaner


class IngestionPipeline:
    """Main ingestion pipeline orchestrator."""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.parser = DocumentParser()
        self.cleaner = DataCleaner()
        self.pod_manager = None

    async def start(self, workers=5, batch_size=100):
        """Start the ingestion pipeline."""
        self.pod_manager = IngestionPodManager(self.config_path)
        await self.pod_manager.start(workers=workers, batch_size=batch_size)

    async def ingest(self, source_data):
        """Ingest data from a source."""
        parsed = await self.parser.parse(source_data)
        cleaned = await self.cleaner.clean(parsed)
        return cleaned

    async def shutdown(self):
        """Shutdown the ingestion pipeline."""
        if self.pod_manager:
            await self.pod_manager.shutdown()
