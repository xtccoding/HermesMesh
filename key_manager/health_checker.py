"""
Health Checker - Key健康检查与自动恢复

功能：
- 定期健康检查
- 自动禁用不健康Key
- 自动恢复冷却中的Key
- 延迟监控
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from loguru import logger

from .key_pool import KeyPool, APIKey, KeyStatus


@dataclass
class HealthCheckResult:
    """健康检查结果"""
    key_id: str
    is_healthy: bool
    latency_ms: float = 0.0
    error: Optional[str] = None
    checked_at: float = 0.0


class HealthChecker:
    """Key健康检查器"""

    def __init__(
        self,
        key_pool: KeyPool,
        check_interval: float = 60.0,  # 检查间隔（秒）
        max_failures: int = 3,  # 最大失败次数后禁用
        recovery_time: float = 300.0,  # 恢复时间（秒）
    ):
        self.key_pool = key_pool
        self.check_interval = check_interval
        self.max_failures = max_failures
        self.recovery_time = recovery_time
        
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._check_history: List[HealthCheckResult] = []
        self._failure_counts: Dict[str, int] = {}
        self._custom_checker: Optional[Callable] = None

    def set_custom_checker(self, checker: Callable):
        """设置自定义健康检查函数"""
        self._custom_checker = checker

    async def start(self):
        """启动健康检查"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._check_loop())
        logger.info(f"Health checker started (interval: {self.check_interval}s)")

    async def stop(self):
        """停止健康检查"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Health checker stopped")

    async def _check_loop(self):
        """健康检查循环"""
        while self._running:
            try:
                await self.check_all_keys()
                await self._recover_keys()
            except Exception as e:
                logger.error(f"Health check error: {e}")
            
            await asyncio.sleep(self.check_interval)

    async def check_all_keys(self) -> List[HealthCheckResult]:
        """检查所有Key的健康状态"""
        results = []
        keys = await self.key_pool.get_all_keys(include_disabled=False)
        
        for key in keys:
            result = await self.check_key(key)
            results.append(result)
            
            # 记录失败次数
            if not result.is_healthy:
                self._failure_counts[key.id] = self._failure_counts.get(key.id, 0) + 1
                
                # 如果失败次数超过阈值，禁用Key
                if self._failure_counts[key.id] >= self.max_failures:
                    await self.key_pool.update_key(key.id, {
                        "status": KeyStatus.INVALID
                    })
                    logger.warning(f"Key {key.id} disabled due to {self.max_failures} consecutive failures")
            else:
                # 重置失败计数
                self._failure_counts[key.id] = 0
            
            # 记录历史
            self._check_history.append(result)
            if len(self._check_history) > 1000:
                self._check_history = self._check_history[-1000:]
        
        healthy_count = sum(1 for r in results if r.is_healthy)
        logger.debug(f"Health check complete: {healthy_count}/{len(results)} healthy")
        
        return results

    async def check_key(self, key: APIKey) -> HealthCheckResult:
        """检查单个Key的健康状态"""
        start_time = time.time()
        
        try:
            if self._custom_checker:
                is_healthy = await self._custom_checker(key)
            else:
                # 默认检查：检查是否在冷却期、是否可用
                is_healthy = key.is_available()
            
            latency = (time.time() - start_time) * 1000
            
            return HealthCheckResult(
                key_id=key.id,
                is_healthy=is_healthy,
                latency_ms=round(latency, 2),
                checked_at=time.time()
            )
        except Exception as e:
            return HealthCheckResult(
                key_id=key.id,
                is_healthy=False,
                error=str(e),
                checked_at=time.time()
            )

    async def _recover_keys(self):
        """恢复冷却中的Key"""
        current_time = time.time()
        keys = await self.key_pool.get_all_keys(include_disabled=True)
        
        for key in keys:
            # 检查冷却期是否结束
            if key.status == KeyStatus.RATE_LIMITED and key.cooldown_until <= current_time:
                await self.key_pool.update_key(key.id, {
                    "status": KeyStatus.ACTIVE,
                    "cooldown_until": 0
                })
                logger.info(f"Key {key.id} recovered from rate limit")
            
            # 检查是否可以重新启用被禁用的Key
            elif key.status == KeyStatus.INVALID:
                last_error = key.last_error_at
                if last_error and (current_time - last_error) > self.recovery_time:
                    await self.key_pool.update_key(key.id, {
                        "status": KeyStatus.ACTIVE
                    })
                    logger.info(f"Key {key.id} re-enabled after recovery period")

    async def force_check(self, key_id: str) -> Optional[HealthCheckResult]:
        """强制检查指定Key"""
        key = await self.key_pool.get_key_by_id(key_id)
        if not key:
            return None
        
        result = await self.check_key(key)
        self._check_history.append(result)
        
        return result

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取检查历史"""
        history = self._check_history[-limit:]
        return [
            {
                "key_id": r.key_id,
                "is_healthy": r.is_healthy,
                "latency_ms": r.latency_ms,
                "error": r.error,
                "checked_at": r.checked_at
            }
            for r in history
        ]

    def get_failure_counts(self) -> Dict[str, int]:
        """获取失败计数"""
        return self._failure_counts.copy()

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_checks = len(self._check_history)
        healthy_checks = sum(1 for r in self._check_history if r.is_healthy)
        
        avg_latency = 0.0
        if self._check_history:
            latencies = [r.latency_ms for r in self._check_history if r.latency_ms > 0]
            if latencies:
                avg_latency = sum(latencies) / len(latencies)
        
        return {
            "total_checks": total_checks,
            "healthy_checks": healthy_checks,
            "unhealthy_checks": total_checks - healthy_checks,
            "health_rate": healthy_checks / total_checks if total_checks > 0 else 0,
            "avg_latency_ms": round(avg_latency, 2),
            "failure_counts": self._failure_counts,
            "is_running": self._running,
            "check_interval": self.check_interval
        }
