"""
Quota Tracker - 额度追踪与限制管理

功能：
- 实时额度追踪
- 多维度限制（RPM/TPM/费用）
- 自动告警
- 历史统计
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger

from .key_pool import KeyPool, APIKey, KeyStatus


class QuotaAlert(str, Enum):
    NONE = "none"
    WARNING = "warning"  # 80%
    CRITICAL = "critical"  # 95%
    EXCEEDED = "exceeded"  # 100%


@dataclass
class QuotaUsage:
    """额度使用情况"""
    key_id: str
    provider: str
    
    # 费用额度
    quota_limit: float = 0.0
    quota_used: float = 0.0
    quota_remaining: float = 0.0
    quota_percentage: float = 0.0
    
    # RPM限制
    rpm_limit: int = 0
    rpm_current: int = 0
    rpm_remaining: int = 0
    
    # TPM限制
    tpm_limit: int = 0
    tpm_current: int = 0
    tpm_remaining: int = 0
    
    # 告警级别
    alert_level: QuotaAlert = QuotaAlert.NONE
    
    # 时间戳
    updated_at: float = field(default_factory=time.time)


class QuotaTracker:
    """额度追踪器"""

    def __init__(
        self,
        key_pool: KeyPool,
        warning_threshold: float = 0.8,  # 80%告警
        critical_threshold: float = 0.95,  # 95%严重告警
    ):
        self.key_pool = key_pool
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        
        self._usage_history: List[Dict[str, Any]] = []
        self._alerts: List[Dict[str, Any]] = []
        self._max_history = 1000
        self._max_alerts = 500

    async def get_usage(self, key_id: Optional[str] = None) -> List[QuotaUsage]:
        """获取额度使用情况"""
        usages = []
        
        if key_id:
            key = await self.key_pool.get_key_by_id(key_id)
            if key:
                usage = self._calculate_usage(key)
                usages.append(usage)
        else:
            keys = await self.key_pool.get_all_keys()
            for key in keys:
                usage = self._calculate_usage(key)
                usages.append(usage)
        
        return usages

    def _calculate_usage(self, key: APIKey) -> QuotaUsage:
        """计算单个Key的额度使用情况"""
        # 计算剩余额度
        quota_remaining = max(0, key.quota_limit - key.quota_used) if key.quota_limit > 0 else float('inf')
        quota_percentage = (key.quota_used / key.quota_limit * 100) if key.quota_limit > 0 else 0
        
        rpm_remaining = max(0, key.rpm_limit - key.rpm_current) if key.rpm_limit > 0 else float('inf')
        tpm_remaining = max(0, key.tpm_limit - key.tpm_current) if key.tpm_limit > 0 else float('inf')
        
        # 确定告警级别
        alert_level = QuotaAlert.NONE
        if key.quota_limit > 0:
            if quota_percentage >= 100:
                alert_level = QuotaAlert.EXCEEDED
            elif quota_percentage >= self.critical_threshold * 100:
                alert_level = QuotaAlert.CRITICAL
            elif quota_percentage >= self.warning_threshold * 100:
                alert_level = QuotaAlert.WARNING
        
        return QuotaUsage(
            key_id=key.id,
            provider=key.provider,
            quota_limit=key.quota_limit,
            quota_used=key.quota_used,
            quota_remaining=quota_remaining,
            quota_percentage=round(quota_percentage, 2),
            rpm_limit=key.rpm_limit,
            rpm_current=key.rpm_current,
            rpm_remaining=rpm_remaining,
            tpm_limit=key.tpm_limit,
            tpm_current=key.tpm_current,
            tpm_remaining=tpm_remaining,
            alert_level=alert_level,
            updated_at=time.time()
        )

    async def check_and_alert(self) -> List[Dict[str, Any]]:
        """检查额度并生成告警"""
        alerts = []
        usages = await self.get_usage()
        
        for usage in usages:
            if usage.alert_level in [QuotaAlert.WARNING, QuotaAlert.CRITICAL, QuotaAlert.EXCEEDED]:
                alert = {
                    "key_id": usage.key_id,
                    "provider": usage.provider,
                    "level": usage.alert_level,
                    "quota_percentage": usage.quota_percentage,
                    "quota_remaining": usage.quota_remaining,
                    "timestamp": time.time(),
                    "message": self._generate_alert_message(usage)
                }
                alerts.append(alert)
                self._alerts.append(alert)
                
                # 限制告警历史大小
                if len(self._alerts) > self._max_alerts:
                    self._alerts = self._alerts[-self._max_alerts:]
                
                logger.warning(f"Quota alert: {alert['message']}")
        
        return alerts

    def _generate_alert_message(self, usage: QuotaUsage) -> str:
        """生成告警消息"""
        if usage.alert_level == QuotaAlert.EXCEEDED:
            return f"Key {usage.key_id} ({usage.provider}) 额度已用尽! 已用: ${usage.quota_used:.4f}"
        elif usage.alert_level == QuotaAlert.CRITICAL:
            return f"Key {usage.key_id} ({usage.provider}) 额度即将用尽! 使用率: {usage.quota_percentage}%"
        elif usage.alert_level == QuotaAlert.WARNING:
            return f"Key {usage.key_id} ({usage.provider}) 额度使用较高: {usage.quota_percentage}%"
        return ""

    async def record_usage(
        self,
        key_id: str,
        tokens: int = 0,
        cost: float = 0.0
    ):
        """记录使用量"""
        key = await self.key_pool.get_key_by_id(key_id)
        if key:
            key.record_success(tokens, cost)
            
            # 记录历史
            self._usage_history.append({
                "key_id": key_id,
                "tokens": tokens,
                "cost": cost,
                "timestamp": time.time()
            })
            
            if len(self._usage_history) > self._max_history:
                self._usage_history = self._usage_history[-self._max_history:]

    async def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取告警历史"""
        return self._alerts[-limit:]

    async def get_usage_history(
        self,
        key_id: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """获取使用历史"""
        cutoff = time.time() - (hours * 3600)
        
        history = [
            h for h in self._usage_history
            if h["timestamp"] >= cutoff
        ]
        
        if key_id:
            history = [h for h in history if h["key_id"] == key_id]
        
        return history

    async def get_daily_stats(self) -> Dict[str, Any]:
        """获取每日统计"""
        now = time.time()
        day_start = now - (now % 86400)  # 今天开始时间
        
        daily_usage = [
            h for h in self._usage_history
            if h["timestamp"] >= day_start
        ]
        
        total_tokens = sum(h["tokens"] for h in daily_usage)
        total_cost = sum(h["cost"] for h in daily_usage)
        total_requests = len(daily_usage)
        
        # 按Key分组
        by_key = {}
        for h in daily_usage:
            key_id = h["key_id"]
            if key_id not in by_key:
                by_key[key_id] = {"tokens": 0, "cost": 0, "requests": 0}
            by_key[key_id]["tokens"] += h["tokens"]
            by_key[key_id]["cost"] += h["cost"]
            by_key[key_id]["requests"] += 1
        
        return {
            "date": time.strftime("%Y-%m-%d", time.localtime(day_start)),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "total_requests": total_requests,
            "by_key": by_key
        }

    async def get_monthly_stats(self) -> Dict[str, Any]:
        """获取每月统计"""
        now = time.time()
        month_start = now - (now % 2592000)  # 大约30天
        
        monthly_usage = [
            h for h in self._usage_history
            if h["timestamp"] >= month_start
        ]
        
        total_tokens = sum(h["tokens"] for h in monthly_usage)
        total_cost = sum(h["cost"] for h in monthly_usage)
        total_requests = len(monthly_usage)
        
        return {
            "month": time.strftime("%Y-%m", time.localtime(month_start)),
            "total_tokens": total_tokens,
            "total_cost": round(total_cost, 4),
            "total_requests": total_requests
        }

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_usage_records": len(self._usage_history),
            "total_alerts": len(self._alerts),
            "warning_threshold": self.warning_threshold,
            "critical_threshold": self.critical_threshold
        }
