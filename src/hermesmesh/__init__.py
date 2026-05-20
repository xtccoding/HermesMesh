"""
HermesMesh - AI-Native Distributed Intelligent Quantitative Analysis Platform
"""

__version__ = "0.1.0"
__author__ = "HermesMesh Team"

from .ingestion import IngestionPipeline
from .control_plane import MasterControlPlane
from .feature_workers import WorkerMesh
from .supervision import SupervisorNetwork
from .synthesis import ReportingEngine


def create_mesh(config_path=None):
    """Create and initialize the HermesMesh pipeline."""
    return {
        "ingestion": IngestionPipeline(config_path),
        "control": MasterControlPlane(),
        "workers": WorkerMesh(),
        "supervision": SupervisorNetwork(),
        "synthesis": ReportingEngine(),
    }
