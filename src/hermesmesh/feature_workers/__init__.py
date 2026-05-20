"""
Feature Workers Module - Data processing and factor extraction
"""

from .cluster_a import ClusterAWorker
from .cluster_b import ClusterBWorker
from .factor_calculator import FactorCalculator
from .anomaly_detector import AnomalyDetector


class WorkerMesh:
    """Worker mesh orchestrator."""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.cluster_a = ClusterAWorker(config_path)
        self.cluster_b = ClusterBWorker(config_path)
        self.factor_calculator = FactorCalculator()
        self.anomaly_detector = AnomalyDetector()

    async def start(self, instances=10):
        """Start worker clusters."""
        await self.cluster_a.start(instances=instances // 2)
        await self.cluster_b.start(instances=instances // 2)

    async def process(self, data):
        """Process data through worker mesh."""
        # Cluster A: Data extraction and cleaning
        extracted = await self.cluster_a.process(data)
        
        # Cluster B: Factor calculation
        factors = await self.cluster_b.process(extracted)
        
        # Calculate additional factors
        computed_factors = await self.factor_calculator.calculate(factors)
        
        # Detect anomalies
        anomalies = await self.anomaly_detector.detect(computed_factors)
        
        return {
            "factors": computed_factors,
            "anomalies": anomalies,
            "metadata": extracted.get("metadata", {}),
        }

    async def shutdown(self):
        """Shutdown all workers."""
        await self.cluster_a.shutdown()
        await self.cluster_b.shutdown()
