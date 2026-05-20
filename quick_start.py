#!/usr/bin/env python3
"""
HermesMesh Quick Start Script
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from hermesmesh.ingestion import IngestionPipeline
from hermesmesh.control_plane import MasterControlPlane
from hermesmesh.feature_workers import WorkerMesh
from hermesmesh.supervision import SupervisorNetwork
from hermesmesh.synthesis import ReportingEngine


async def quick_start():
    """Quick start the HermesMesh pipeline."""
    print("=" * 60)
    print("  HermesMesh - AI-Native Quantitative Analysis Platform")
    print("=" * 60)
    print()

    # Initialize components
    print("Initializing components...")
    ingestion = IngestionPipeline()
    control = MasterControlPlane()
    workers = WorkerMesh()
    supervision = SupervisorNetwork()
    synthesis = ReportingEngine()

    print("Starting pipeline...")
    print()

    # Start all components
    await asyncio.gather(
        ingestion.start(workers=3),
        control.start(),
        workers.start(instances=6),
        supervision.start(instances=2),
        synthesis.start(),
    )

    print("✓ All components started successfully!")
    print()
    print("Pipeline is running. Press Ctrl+C to stop.")
    print()

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print()
        print("Shutting down...")
    finally:
        await asyncio.gather(
            ingestion.shutdown(),
            control.shutdown(),
            workers.shutdown(),
            supervision.shutdown(),
            synthesis.shutdown(),
        )
        print("✓ Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(quick_start())
