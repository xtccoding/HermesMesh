#!/usr/bin/env python3
"""
Advanced Configuration Example
"""

import asyncio
from pathlib import Path

from hermesmesh.ingestion import IngestionPipeline
from hermesmesh.control_plane import MasterControlPlane
from hermesmesh.feature_workers import WorkerMesh
from hermesmesh.supervision import SupervisorNetwork
from hermesmesh.synthesis import ReportingEngine


async def main():
    print("HermesMesh Advanced Configuration Example")
    print("=" * 50)

    # Custom configuration
    config = {
        "ingestion": {
            "workers": 10,
            "batch_size": 200,
            "sources": ["html", "pdf", "api"],
        },
        "workers": {
            "instances": 20,
            "clusters": ["A", "B"],
        },
        "supervision": {
            "instances": 5,
            "debate_rounds": 5,
        },
    }

    # Initialize components with custom config
    ingestion = IngestionPipeline(config_path="config/ingestion/default.yaml")
    control = MasterControlPlane(config_path="config/workers/scaling_rules.yaml")
    workers = WorkerMesh(config_path="config/workers/cluster_a.yaml")
    supervision = SupervisorNetwork(config_path="config/supervisor/rules.yaml")
    synthesis = ReportingEngine(config_path="config/synthesizer/report_templates.yaml")

    print(f"Starting with config: {config}")
    print()

    # Start components
    await asyncio.gather(
        ingestion.start(
            workers=config["ingestion"]["workers"],
            batch_size=config["ingestion"]["batch_size"],
        ),
        control.start(),
        workers.start(instances=config["workers"]["instances"]),
        supervision.start(instances=config["supervision"]["instances"]),
        synthesis.start(),
    )

    print("All components started successfully!")
    print("Running pipeline...")

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await asyncio.gather(
            ingestion.shutdown(),
            control.shutdown(),
            workers.shutdown(),
            supervision.shutdown(),
            synthesis.shutdown(),
        )
        print("Shutdown complete.")


if __name__ == "__main__":
    asyncio.run(main())
