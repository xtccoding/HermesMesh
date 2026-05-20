#!/usr/bin/env python3
"""
Simple HermesMesh Pipeline Example
"""

import asyncio
from hermesmesh import create_mesh


async def main():
    print("Starting HermesMesh Pipeline Example...")

    # Create mesh components
    mesh = create_mesh(config_path="config/ingestion/default.yaml")

    # Start all components
    await asyncio.gather(
        mesh["ingestion"].start(workers=3),
        mesh["control"].start(),
        mesh["workers"].start(instances=5),
        mesh["supervision"].start(instances=2),
        mesh["synthesis"].start(),
    )

    print("Pipeline is running...")
    print("Press Ctrl+C to stop")

    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await asyncio.gather(
            mesh["ingestion"].shutdown(),
            mesh["control"].shutdown(),
            mesh["workers"].shutdown(),
            mesh["supervision"].shutdown(),
            mesh["synthesis"].shutdown(),
        )


if __name__ == "__main__":
    asyncio.run(main())
