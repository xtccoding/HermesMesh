"""
Key Rotator - 智能Key轮询与分发

支持多种轮询策略：
- Round Robin: 轮询
- Priority: 优先级
- Weighted: 权重
- Least Used: 最少使用
- Failover: 故障转移
"""

import asyncio
import time
from typing import Optional, Dict, Any, List
from enum import Enum
from loguru import logger

from .key_pool import KeyPool, APIKey, Provider, KeyStatus


class RotationStrategy(str, Enum):
    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    WEIGHTED = "weighted"
    LEAST_USED = "least_used"
    FAILOVER = "failover"
    RANDOM = "random"


class KeyRotator:
    """Key轮询器 - 核心分发引擎"""

    def __init__(self, key_pool: KeyPool):
        self.key_pool = key_pool
        self.strategy = RotationStrategy.ROUND_ROBIN
        self._current_index = 0
        self._failover_order: List[str] = []
        self._request_history: List[Dict[str, Any]] = []
        self._max_history = 1000

    async def get_key(
        self,
        provider: Optional[Provider] = None,
        model: Optional[str] = None,
        exclude_keys: Optional[List[str]] = None
    ) -> Optional[APIKey]:
        """获取一个可用的Key"""
        exclude_keys = exclude_keys or []
        
        # 获取所有可用Key
        available_keys = []
        for key in await self.key_pool.get_all_keys():
            if key.id in exclude_keys:
                continue
            if not key.is_available():
                continue
            if provider and key.provider != provider:
                continue
            if model and key.models and model not in key.models:
                continue
            available_keys.append(key)
        
        if not available_keys:
            logger.warning("No available keys found!")
            return None
        
        # 根据策略选择
        selected = await self._select_key(available_keys)
        
        # 记录选择
        self._record_selection(selected)
        
        return selected

    async def _select_key(self, keys: List[APIKey]) -> APIKey:
        """根据策略选择Key"""
        if self.strategy == RotationStrategy.ROUND_ROBIN:
            return self._round_robin(keys)
        elif self.strategy == RotationStrategy.PRIORITY:
            return self._priority(keys)
        elif self.strategy == RotationStrategy.WEIGHTED:
            return self._weighted(keys)
        elif self.strategy == RotationStrategy.LEAST_USED:
            return self._least_used(keys)
        elif self.strategy == RotationStrategy.FAILOVER:
            return self._failover(keys)
        elif self.strategy == RotationStrategy.RANDOM:
            return self._random(keys)
        else:
            return keys[0]

    def _round_robin(self, keys: List[APIKey]) -> APIKey:
        """轮询选择"""
        self._current_index = (self._current_index + 1) % len(keys)
        return keys[self._current_index]

    def _priority(self, keys: List[APIKey]) -> APIKey:
        """优先级选择"""
        return max(keys, key=lambda k: k.priority)

    def _weighted(self, keys: List[APIKey]) -> APIKey:
        """权重选择"""
        import random
        weights = [k.weight for k in keys]
        total = sum(weights)
        if total == 0:
            return keys[0]
        
        r = random.uniform(0, total)
        cumulative = 0
        for key, weight in zip(keys, weights):
            cumulative += weight
            if r <= cumulative:
                return key
        return keys[-1]

    def _least_used(self, keys: List[APIKey]) -> APIKey:
        """最少使用选择"""
        return min(keys, key=lambda k: k.total_requests)

    def _failover(self, keys: List[APIKey]) -> APIKey:
        """故障转移选择 - 按优先级顺序，失败后切换到下一个"""
        # 按优先级排序
        sorted_keys = sorted(keys, key=lambda k: k.priority, reverse=True)
        
        # 查找第一个未在故障转移列表中的Key
        for key in sorted_keys:
            if key.id not in self._failover_order:
                return key
        
        # 如果所有Key都在故障转移列表中，重置并返回第一个
        self._failover_order.clear()
        return sorted_keys[0]

    def _random(self, keys: List[APIKey]) -> APIKey:
        """随机选择"""
        import random
        return random.choice(keys)

    def _record_selection(self, key: APIKey):
        """记录Key选择"""
        self._request_history.append({
            "key_id": key.id,
            "provider": key.provider,
            "timestamp": time.time()
        })
        
        # 限制历史记录大小
        if len(self._request_history) > self._max_history:
            self._request_history = self._request_history[-self._max_history:]

    async def report_success(self, key_id: str, tokens: int = 0, cost: float = 0.0):
        """报告成功请求"""
        key = await self.key_pool.get_key_by_id(key_id)
        if key:
            key.record_success(tokens, cost)
            logger.debug(f"Key {key_id} success: tokens={tokens}, cost={cost}")

    async def report_failure(self, key_id: str, error_type: str = "unknown"):
        """报告失败请求"""
        key = await self.key_pool.get_key_by_id(key_id)
        if key:
            key.record_failure(error_type)
            
            # 如果是故障转移策略，将此Key加入故障列表
            if self.strategy == RotationStrategy.FAILOVER:
                self._failover_order.append(key_id)
            
            logger.warning(f"Key {key_id} failure: {error_type}")

    async def mark_key_unavailable(self, key_id: str, duration: float = 60):
        """临时标记Key不可用"""
        key = await self.key_pool.get_key_by_id(key_id)
        if key:
            key.cooldown_until = time.time() + duration
            logger.info(f"Key {key_id} marked unavailable for {duration}s")

    def set_strategy(self, strategy: RotationStrategy):
        """设置轮询策略"""
        self.strategy = strategy
        logger.info(f"Rotation strategy set to: {strategy}")

    def get_strategy(self) -> RotationStrategy:
        """获取当前策略"""
        return self.strategy

    def get_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取请求历史"""
        return self._request_history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """获取轮询统计"""
        if not self._request_history:
            return {"total_requests": 0, "by_key": {}, "by_provider": {}}
        
        by_key = {}
        by_provider = {}
        
        for record in self._request_history:
            key_id = record["key_id"]
            provider = record["provider"]
            
            by_key[key_id] = by_key.get(key_id, 0) + 1
            by_provider[provider] = by_provider.get(provider, 0) + 1
        
        return {
            "total_requests": len(self._request_history),
            "strategy": self.strategy,
            "by_key": by_key,
            "by_provider": by_provider,
            "failover_order": self._failover_order
        }
