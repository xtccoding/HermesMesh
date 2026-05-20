"""
HermesMesh Command Line Interface
"""

import argparse
import asyncio
import sys
from pathlib import Path

from loguru import logger


def setup_logging(level="INFO", log_file=None):
    """Configure logging."""
    logger.remove()
    logger.add(sys.stderr, level=level)
    if log_file:
        logger.add(log_file, rotation="10 MB", level=level)


async def run_pipeline(args):
    """Run the complete HermesMesh pipeline."""
    from hermesmesh.ingestion import IngestionPipeline
    from hermesmesh.control_plane import MasterControlPlane
    from hermesmesh.feature_workers import WorkerMesh
    from hermesmesh.supervision import SupervisorNetwork
    from hermesmesh.synthesis import ReportingEngine

    logger.info("Starting HermesMesh Pipeline...")

    # Initialize components
    ingestion = IngestionPipeline(config_path=args.ingestion_config)
    control = MasterControlPlane(config_path=args.control_config)
    workers = WorkerMesh(config_path=args.worker_config)
    supervision = SupervisorNetwork(config_path=args.supervisor_config)
    synthesis = ReportingEngine(config_path=args.synthesis_config)

    try:
        # Start all components
        await asyncio.gather(
            ingestion.start(workers=args.ingestion_workers),
            control.start(),
            workers.start(instances=args.worker_instances),
            supervision.start(instances=args.supervisor_instances),
            synthesis.start(),
        )

        logger.info("HermesMesh pipeline is running...")
        logger.info("Press Ctrl+C to stop")

        # Keep running
        while True:
            await asyncio.sleep(60)

    except KeyboardInterrupt:
        logger.info("Shutting down HermesMesh...")
    finally:
        await asyncio.gather(
            ingestion.shutdown(),
            control.shutdown(),
            workers.shutdown(),
            supervision.shutdown(),
            synthesis.shutdown(),
        )
        logger.info("HermesMesh stopped.")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="HermesMesh - AI-Native Distributed Quantitative Analysis Platform"
    )
    parser.add_argument("--version", action="version", version="HermesMesh 0.1.0")

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Run pipeline command
    run_parser = subparsers.add_parser("run", help="Run the complete pipeline")
    run_parser.add_argument(
        "--ingestion-config",
        default="config/ingestion/default.yaml",
        help="Ingestion config path",
    )
    run_parser.add_argument(
        "--control-config",
        default="config/workers/scaling_rules.yaml",
        help="Control plane config path",
    )
    run_parser.add_argument(
        "--worker-config",
        default="config/workers/cluster_a.yaml",
        help="Worker config path",
    )
    run_parser.add_argument(
        "--supervisor-config",
        default="config/supervisor/rules.yaml",
        help="Supervisor config path",
    )
    run_parser.add_argument(
        "--synthesis-config",
        default="config/synthesizer/report_templates.yaml",
        help="Synthesis config path",
    )
    run_parser.add_argument(
        "--ingestion-workers", type=int, default=5, help="Number of ingestion workers"
    )
    run_parser.add_argument(
        "--worker-instances", type=int, default=10, help="Number of worker instances"
    )
    run_parser.add_argument(
        "--supervisor-instances", type=int, default=3, help="Number of supervisor instances"
    )
    run_parser.add_argument("--log-level", default="INFO", help="Logging level")
    run_parser.add_argument("--log-file", help="Log file path")

    args = parser.parse_args()

    if args.command == "run":
        setup_logging(args.log_level, args.log_file)
        asyncio.run(run_pipeline(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
