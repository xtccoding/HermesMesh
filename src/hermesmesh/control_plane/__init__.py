"""
Control Plane Module - Master scheduling and orchestration
"""

from .master_hermes import MasterHermes
from .scheduler import TaskScheduler
from .load_balancer import LoadBalancer


class MasterControlPlane:
    """Central control plane for the mesh."""

    def __init__(self, config_path=None):
        self.config_path = config_path
        self.master = MasterHermes(config_path)
        self.scheduler = TaskScheduler()
        self.load_balancer = LoadBalancer()

    async def start(self):
        """Start the control plane."""
        await self.master.start()
        await self.scheduler.start()

    async def schedule_task(self, task):
        """Schedule a task for execution."""
        target_worker = self.load_balancer.select_worker(task)
        return await self.scheduler.assign(task, target_worker)

    async def get_metrics(self):
        """Get current system metrics."""
        return await self.master.get_metrics()

    async def shutdown(self):
        """Shutdown the control plane."""
        await self.master.shutdown()
        await self.scheduler.shutdown()
