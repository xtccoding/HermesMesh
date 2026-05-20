"""
API Key Pool Manager - 核心Key池管理

支持功能：
- 多Provider (OpenAI, Anthropic, OpenRouter, 自定义)
- 多Key轮询
- 优先级权重
- 自动禁用/启用
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from loguru import logger


class KeyStatus(str, Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXCEEDED = "quota_exceeded"
    INVALID = "invalid"
    DISABLED = "disabled"


class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    CUSTOM = "custom"
    LOCAL = "local"


@dataclass
class APIKey:
    """API Key数据模型"""
    id: str
    key: str
    provider: Provider
    name: str = ""
    base_url: str = ""
    status: KeyStatus = KeyStatus.ACTIVE
    priority: int = 1  # 1-10, 越高优先级越高
    weight: float = 1.0  # 负载均衡权重
    
    # 额度信息
    quota_limit: float = 0.0  # 总额度限制 (美元)
    quota_used: float = 0.0  # 已使用额度
    rpm_limit: int = 0  # 每分钟请求数限制
    rpm_current: int = 0  # 当前分钟请求数
    tpm_limit: int = 0  # 每分钟Token限制
    tpm_current: int = 0  # 当前分钟Token数
    
    # 统计信息
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    
    # 时间信息
    created_at: float = field(default_factory=time.time)
    last_used_at: float = 0.0
    last_error_at: float = 0.0
    last_health_check: float = 0.0
    cooldown_until: float = 0.0
    
    # 配置
    models: List[str] = field(default_factory=list)  # 支持的模型列表
    tags: List[str] = field(default_factory=list)  # 标签
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """检查Key是否可用"""
        if self.status in [KeyStatus.DISABLED, KeyStatus.INVALID]:
            return False
        
        # 检查冷却时间
        if self.cooldown_until > time.time():
            return False
        
        # 检查额度
        if self.quota_limit > 0 and self.quota_used >= self.quota_limit:
            self.status = KeyStatus.QUOTA_EXCEEDED
            return False
        
        # 检查RPM限制
        if self.rpm_limit > 0 and self.rpm_current >= self.rpm_limit:
            return False
        
        # 检查TPM限制
        if self.tpm_limit > 0 and self.tpm_current >= self.tpm_limit:
            return False
        
        return self.status == KeyStatus.ACTIVE

    def record_success(self, tokens: int = 0, cost: float = 0.0):
        """记录成功请求"""
        self.total_requests += 1
        self.successful_requests += 1
        self.total_tokens += tokens
        self.total_cost += cost
        self.quota_used += cost
        self.rpm_current += 1
        self.tpm_current += tokens
        self.last_used_at = time.time()
        
        # 成功后重置状态
        if self.status == KeyStatus.RATE_LIMITED:
            self.status = KeyStatus.ACTIVE

    def record_failure(self, error_type: str = "unknown"):
        """记录失败请求"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_error_at = time.time()
        
        if error_type == "rate_limit":
            self.status = KeyStatus.RATE_LIMITED
            self.cooldown_until = time.time() + 60  # 冷却1分钟
        elif error_type == "quota_exceeded":
            self.status = KeyStatus.QUOTA_EXCEEDED
        elif error_type == "invalid_key":
            self.status = KeyStatus.INVALID

    def reset_minute_counters(self):
        """重置每分钟计数器"""
        self.rpm_current = 0
        self.tpm_current = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 隐藏完整key，只显示前8位
        data["key_preview"] = self.key[:8] + "..." if len(self.key) > 8 else self.key
        data["key"] = self.key[:4] + "****" + self.key[-4:] if len(self.key) > 8 else "****"
        return data

    def to_full_dict(self) -> Dict[str, Any]:
        """转换为完整字典（包含key）"""
        return asdict(self)


class KeyPool:
    """API Key池管理器"""

    def __init__(self, config_path: Optional[str] = None):
        self.keys: Dict[str, APIKey] = {}
        self.config_path = config_path or "config/key_pool.json"
        self._lock = asyncio.Lock()
        self._round_robin_index = 0
        
        # 加载配置
        self._load_config()

    def _load_config(self):
        """从配置文件加载Key"""
        config_file = Path(self.config_path)
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for key_data in data.get("keys", []):
                        key = APIKey(**key_data)
                        self.keys[key.id] = key
                logger.info(f"Loaded {len(self.keys)} API keys from config")
            except Exception as e:
                logger.error(f"Failed to load key config: {e}")

    def _save_config(self):
        """保存配置到文件"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "keys": [k.to_full_dict() for k in self.keys.values()],
            "updated_at": time.time()
        }
        
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("Key config saved")
        except Exception as e:
            logger.error(f"Failed to save key config: {e}")

    async def add_key(self, key: APIKey) -> APIKey:
        """添加新的API Key"""
        async with self._lock:
            if not key.id:
                key.id = f"{key.provider}_{int(time.time() * 1000)}"
            
            self.keys[key.id] = key
            self._save_config()
            logger.info(f"Added API key: {key.id} ({key.provider})")
            return key

    async def remove_key(self, key_id: str) -> bool:
        """移除API Key"""
        async with self._lock:
            if key_id in self.keys:
                del self.keys[key_id]
                self._save_config()
                logger.info(f"Removed API key: {key_id}")
                return True
            return False

    async def update_key(self, key_id: str, updates: Dict[str, Any]) -> Optional[APIKey]:
        """更新API Key配置"""
        async with self._lock:
            if key_id not in self.keys:
                return None
            
            key = self.keys[key_id]
            for attr, value in updates.items():
                if hasattr(key, attr):
                    setattr(key, attr, value)
            
            self._save_config()
            logger.info(f"Updated API key: {key_id}")
            return key

    async def get_key(
        self,
        provider: Optional[Provider] = None,
        model: Optional[str] = None,
        strategy: str = "round_robin"
    ) -> Optional[APIKey]:
        """获取一个可用的API Key"""
        async with self._lock:
            # 过滤可用的Key
            available_keys = []
            for key in self.keys.values():
                if not key.is_available():
                    continue
                if provider and key.provider != provider:
                    continue
                if model and key.models and model not in key.models:
                    continue
                available_keys.append(key)
            
            if not available_keys:
                logger.warning("No available API keys!")
                return None
            
            # 选择策略
            if strategy == "round_robin":
                return self._round_robin_select(available_keys)
            elif strategy == "priority":
                return self._priority_select(available_keys)
            elif strategy == "weighted":
                return self._weighted_select(available_keys)
            elif strategy == "least_used":
                return self._least_used_select(available_keys)
            else:
                return available_keys[0]

    def _round_robin_select(self, keys: List[APIKey]) -> APIKey:
        """轮询选择"""
        self._round_robin_index = (self._round_robin_index + 1) % len(keys)
        return keys[self._round_robin_index]

    def _priority_select(self, keys: List[APIKey]) -> APIKey:
        """优先级选择"""
        return max(keys, key=lambda k: k.priority)

    def _weighted_select(self, keys: List[APIKey]) -> APIKey:
        """权重选择"""
        import random
        weights = [k.weight for k in keys]
        return random.choices(keys, weights=weights, k=1)[0]

    def _least_used_select(self, keys: List[APIKey]) -> APIKey:
        """最少使用选择"""
        return min(keys, key=lambda k: k.total_requests)

    async def get_all_keys(self, include_disabled: bool = False) -> List[APIKey]:
        """获取所有Key"""
        if include_disabled:
            return list(self.keys.values())
        return [k for k in self.keys.values() if k.status != KeyStatus.DISABLED]

    async def get_key_by_id(self, key_id: str) -> Optional[APIKey]:
        """根据ID获取Key"""
        return self.keys.get(key_id)

    async def disable_key(self, key_id: str) -> bool:
        """禁用Key"""
        return await self.update_key(key_id, {"status": KeyStatus.DISABLED}) is not None

    async def enable_key(self, key_id: str) -> bool:
        """启用Key"""
        return await self.update_key(key_id, {"status": KeyStatus.ACTIVE}) is not None

    async def get_stats(self) -> Dict[str, Any]:
        """获取Key池统计信息"""
        total = len(self.keys)
        active = sum(1 for k in self.keys.values() if k.status == KeyStatus.ACTIVE)
        rate_limited = sum(1 for k in self.keys.values() if k.status == KeyStatus.RATE_LIMITED)
        quota_exceeded = sum(1 for k in self.keys.values() if k.status == KeyStatus.QUOTA_EXCEEDED)
        disabled = sum(1 for k in self.keys.values() if k.status == KeyStatus.DISABLED)
        
        total_requests = sum(k.total_requests for k in self.keys.values())
        total_tokens = sum(k.total_tokens for k in self.keys.values())
        total_cost = sum(k.total_cost for k in self.keys.values())
        
        # 按Provider分组统计
        by_provider = {}
        for key in self.keys.values():
            provider = key.provider
            if provider not in by_provider:
                by_provider[provider] = {"count": 0, "active": 0, "requests": 0}
            by_provider[provider]["count"] += 1
            if key.status == KeyStatus.ACTIVE:
                by_provider[provider]["active"] += 1
            by_provider[provider]["requests"] += key.total_requests
        
        return {
            "total": total,
            "active": active,
            "rate_limited": rate_limited,
            "quota_exceeded": quota_exceeded,
            "disabled": disabled,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "by_provider": by_provider
        }

    async def reset_minute_counters(self):
        """重置所有Key的每分钟计数器"""
        for key in self.keys.values():
            key.reset_minute_counters()
        logger.debug("Reset all minute counters")

    async def health_check_all(self) -> Dict[str, bool]:
        """对所有Key进行健康检查"""
        results = {}
        for key_id, key in self.keys.items():
            if key.status == KeyStatus.DISABLED:
                results[key_id] = False
                continue
            
            # 这里可以调用实际的API检查
            # 简化版本：检查是否在冷却期
            results[key_id] = key.is_available()
            key.last_health_check = time.time()
        
        return results
