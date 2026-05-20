"""
Task Scheduler - Task assignment and execution coordination
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime

from loguru import logger


class TaskScheduler:
    """Task scheduler for distributing work across the mesh."""

    def __init__(self):
        self.is_running = False
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_counter = 0

    async def start(self):
        """Start the task scheduler."""
        self.is_running = True
        logger.info("TaskScheduler started")

    async def submit(self, task: Dict[str, Any]) -> str:
        """Submit a task for execution."""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"

        task_entry = {
            "id": task_id,
            "data": task,
            "status": "pending",
            "submitted_at": datetime.now().isoformat(),
        }

        await self.task_queue.put(task_entry)
        self.active_tasks[task_id] = task_entry

        logger.debug(f"Task {task_id} submitted")
        return task_id

    async def assign(self, task: Dict[str, Any], worker_id: str) -> Dict[str, Any]:
        """Assign a task to a specific worker."""
        task_id = await self.submit(task)

        self.active_tasks[task_id]["status"] = "assigned"
        self.active_tasks[task_id]["worker_id"] = worker_id
        self.active_tasks[task_id]["assigned_at"] = datetime.now().isoformat()

        return self.active_tasks[task_id]

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        return self.active_tasks.get(task_id)

    async def complete_task(self, task_id: str, result: Any = None):
        """Mark a task as completed."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "completed"
            self.active_tasks[task_id]["completed_at"] = datetime.now().isoformat()
            self.active_tasks[task_id]["result"] = result
            logger.debug(f"Task {task_id} completed")

    async def fail_task(self, task_id: str, error: str):
        """Mark a task as failed."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "failed"
            self.active_tasks[task_id]["error"] = error
            self.active_tasks[task_id]["failed_at"] = datetime.now().isoformat()
            logger.warning(f"Task {task_id} failed: {error}")

    async def get_stats(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        statuses = {}
        for task in self.active_tasks.values():
            status = task["status"]
            statuses[status] = statuses.get(status, 0) + 1

        return {
            "total_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "statuses": statuses,
        }

    async def shutdown(self):
        """Shutdown the task scheduler."""
        self.is_running = False
        logger.info("TaskScheduler shutdown complete")
