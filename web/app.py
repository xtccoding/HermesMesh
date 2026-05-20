"""
HermesMesh Web Manager - FastAPI后端服务

功能：
- Key池管理API
- Workflow管理API
- 实时监控WebSocket
- 静态文件服务
"""

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from loguru import logger

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from key_manager import KeyPool, APIKey, KeyRotator, HealthChecker, QuotaTracker
from key_manager.key_pool import Provider, KeyStatus
from key_manager.key_rotator import RotationStrategy


# ============ Pydantic Models ============

class KeyCreateRequest(BaseModel):
    """创建Key请求"""
    key: str
    provider: str
    name: str = ""
    base_url: str = ""
    priority: int = 1
    weight: float = 1.0
    quota_limit: float = 0.0
    rpm_limit: int = 0
    tpm_limit: int = 0
    models: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

class KeyUpdateRequest(BaseModel):
    """更新Key请求"""
    name: Optional[str] = None
    base_url: Optional[str] = None
    priority: Optional[int] = None
    weight: Optional[float] = None
    quota_limit: Optional[float] = None
    rpm_limit: Optional[int] = None
    tpm_limit: Optional[int] = None
    models: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

class WorkflowNode(BaseModel):
    """工作流节点"""
    id: str
    type: str
    label: str
    x: float = 0
    y: float = 0
    config: Dict[str, Any] = Field(default_factory=dict)
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)

class WorkflowEdge(BaseModel):
    """工作流边"""
    id: str
    source: str
    target: str
    sourceHandle: str = ""
    targetHandle: str = ""

class Workflow(BaseModel):
    """工作流"""
    id: Optional[str] = None
    name: str
    description: str = ""
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ProxyRequest(BaseModel):
    """代理请求"""
    model: str
    messages: List[Dict[str, str]]
    provider: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 1000
    stream: bool = False


# ============ Global State ============

class AppState:
    """应用状态"""
    def __init__(self):
        self.key_pool = KeyPool()
        self.rotator = KeyRotator(self.key_pool)
        self.health_checker = HealthChecker(self.key_pool)
        self.quota_tracker = QuotaTracker(self.key_pool)
        self.workflows: Dict[str, Workflow] = {}
        self.websocket_clients: List[WebSocket] = []
        self._initialized = False

    async def initialize(self):
        """初始化"""
        if self._initialized:
            return
        
        # 启动健康检查
        await self.health_checker.start()
        
        # 加载示例Key（如果有的话）
        await self._load_demo_keys()
        
        self._initialized = True
        logger.info("App state initialized")

    async def _load_demo_keys(self):
        """加载演示Key"""
        # 检查是否有现有Key
        keys = await self.key_pool.get_all_keys(include_disabled=True)
        if len(keys) > 0:
            return
        
        # 添加演示Key
        demo_keys = [
            APIKey(
                id="demo_openai_1",
                key="sk-demo1************************************************",
                provider=Provider.OPENAI,
                name="OpenAI Demo Key 1",
                base_url="https://api.openai.com/v1",
                priority=5,
                weight=1.0,
                quota_limit=100.0,
                models=["gpt-4", "gpt-3.5-turbo"]
            ),
            APIKey(
                id="demo_openai_2",
                key="sk-demo2************************************************",
                provider=Provider.OPENAI,
                name="OpenAI Demo Key 2",
                base_url="https://api.openai.com/v1",
                priority=3,
                weight=0.8,
                quota_limit=50.0,
                models=["gpt-4", "gpt-3.5-turbo"]
            ),
            APIKey(
                id="demo_openrouter_1",
                key="sk-or-demo1**********************************************",
                provider=Provider.OPENROUTER,
                name="OpenRouter Demo Key",
                base_url="https://openrouter.ai/api/v1",
                priority=4,
                weight=1.0,
                quota_limit=200.0,
                models=["anthropic/claude-3", "google/gemini-pro"]
            ),
        ]
        
        for key in demo_keys:
            await self.key_pool.add_key(key)
        
        logger.info(f"Loaded {len(demo_keys)} demo keys")

    async def shutdown(self):
        """关闭"""
        await self.health_checker.stop()
        logger.info("App state shutdown")


# ============ App Instance ============

state = AppState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期"""
    await state.initialize()
    yield
    await state.shutdown()


# ============ FastAPI App ============

app = FastAPI(
    title="HermesMesh Manager",
    description="HermesMesh Workflow & Key Management Dashboard",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# ============ Dashboard Routes ============

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """主仪表盘"""
    template_path = Path(__file__).parent / "templates" / "index.html"
    if template_path.exists():
        return template_path.read_text(encoding="utf-8")
    return "<h1>HermesMesh Manager</h1><p>Template not found</p>"


# ============ Key Management API ============

@app.get("/api/keys")
async def get_keys(include_disabled: bool = False):
    """获取所有Key"""
    keys = await state.key_pool.get_all_keys(include_disabled=include_disabled)
    return {"keys": [k.to_dict() for k in keys]}

@app.post("/api/keys")
async def create_key(request: KeyCreateRequest):
    """创建新Key"""
    try:
        provider = Provider(request.provider)
    except ValueError:
        raise HTTPException(400, f"Invalid provider: {request.provider}")
    
    key = APIKey(
        id="",
        key=request.key,
        provider=provider,
        name=request.name,
        base_url=request.base_url,
        priority=request.priority,
        weight=request.weight,
        quota_limit=request.quota_limit,
        rpm_limit=request.rpm_limit,
        tpm_limit=request.tpm_limit,
        models=request.models,
        tags=request.tags
    )
    
    created = await state.key_pool.add_key(key)
    return {"key": created.to_dict()}

@app.get("/api/keys/{key_id}")
async def get_key(key_id: str):
    """获取单个Key"""
    key = await state.key_pool.get_key_by_id(key_id)
    if not key:
        raise HTTPException(404, "Key not found")
    return {"key": key.to_dict()}

@app.put("/api/keys/{key_id}")
async def update_key(key_id: str, request: KeyUpdateRequest):
    """更新Key"""
    updates = {k: v for k, v in request.dict().items() if v is not None}
    
    if "status" in updates:
        updates["status"] = KeyStatus(updates["status"])
    
    key = await state.key_pool.update_key(key_id, updates)
    if not key:
        raise HTTPException(404, "Key not found")
    return {"key": key.to_dict()}

@app.delete("/api/keys/{key_id}")
async def delete_key(key_id: str):
    """删除Key"""
    success = await state.key_pool.remove_key(key_id)
    if not success:
        raise HTTPException(404, "Key not found")
    return {"success": True}

@app.post("/api/keys/{key_id}/enable")
async def enable_key(key_id: str):
    """启用Key"""
    success = await state.key_pool.enable_key(key_id)
    if not success:
        raise HTTPException(404, "Key not found")
    return {"success": True}

@app.post("/api/keys/{key_id}/disable")
async def disable_key(key_id: str):
    """禁用Key"""
    success = await state.key_pool.disable_key(key_id)
    if not success:
        raise HTTPException(404, "Key not found")
    return {"success": True}

@app.post("/api/keys/{key_id}/health-check")
async def health_check_key(key_id: str):
    """健康检查单个Key"""
    result = await state.health_checker.force_check(key_id)
    if not result:
        raise HTTPException(404, "Key not found")
    return {"result": {
        "key_id": result.key_id,
        "is_healthy": result.is_healthy,
        "latency_ms": result.latency_ms,
        "error": result.error
    }}


# ============ Key Stats API ============

@app.get("/api/keys/stats")
async def get_keys_stats():
    """获取Key池统计"""
    pool_stats = await state.key_pool.get_stats()
    rotator_stats = state.rotator.get_stats()
    health_stats = state.health_checker.get_stats()
    quota_stats = state.quota_tracker.get_stats()
    
    return {
        "pool": pool_stats,
        "rotator": rotator_stats,
        "health": health_stats,
        "quota": quota_stats
    }

@app.get("/api/keys/usage")
async def get_keys_usage(key_id: Optional[str] = None):
    """获取额度使用情况"""
    usage = await state.quota_tracker.get_usage(key_id)
    return {"usage": [
        {
            "key_id": u.key_id,
            "provider": u.provider,
            "quota_limit": u.quota_limit,
            "quota_used": u.quota_used,
            "quota_remaining": u.quota_remaining,
            "quota_percentage": u.quota_percentage,
            "rpm_limit": u.rpm_limit,
            "rpm_current": u.rpm_current,
            "tpm_limit": u.tpm_limit,
            "tpm_current": u.tpm_current,
            "alert_level": u.alert_level
        }
        for u in usage
    ]}

@app.get("/api/keys/alerts")
async def get_keys_alerts(limit: int = 50):
    """获取告警历史"""
    alerts = await state.quota_tracker.get_alerts(limit)
    return {"alerts": alerts}

@app.get("/api/keys/daily-stats")
async def get_daily_stats():
    """获取每日统计"""
    stats = await state.quota_tracker.get_daily_stats()
    return stats

@app.get("/api/keys/monthly-stats")
async def get_monthly_stats():
    """获取每月统计"""
    stats = await state.quota_tracker.get_monthly_stats()
    return stats


# ============ Rotation Strategy API ============

@app.get("/api/rotator/strategy")
async def get_rotation_strategy():
    """获取当前轮询策略"""
    return {"strategy": state.rotator.get_strategy()}

@app.put("/api/rotator/strategy")
async def set_rotation_strategy(strategy: str):
    """设置轮询策略"""
    try:
        rot_strategy = RotationStrategy(strategy)
        state.rotator.set_strategy(rot_strategy)
        return {"strategy": rot_strategy}
    except ValueError:
        raise HTTPException(400, f"Invalid strategy: {strategy}")

@app.get("/api/rotator/stats")
async def get_rotator_stats():
    """获取轮询统计"""
    return state.rotator.get_stats()

@app.get("/api/rotator/history")
async def get_rotator_history(limit: int = 100):
    """获取轮询历史"""
    history = state.rotator.get_history(limit)
    return {"history": history}


# ============ Workflow API ============

@app.get("/api/workflows")
async def get_workflows():
    """获取所有工作流"""
    return {"workflows": [
        {
            "id": wf.id,
            "name": wf.name,
            "description": wf.description,
            "nodes_count": len(wf.nodes),
            "edges_count": len(wf.edges),
            "metadata": wf.metadata
        }
        for wf in state.workflows.values()
    ]}

@app.post("/api/workflows")
async def create_workflow(workflow: Workflow):
    """创建工作流"""
    if not workflow.id:
        workflow.id = f"wf_{int(time.time() * 1000)}"
    
    state.workflows[workflow.id] = workflow
    logger.info(f"Created workflow: {workflow.id}")
    return {"workflow": workflow}

@app.get("/api/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """获取单个工作流"""
    if workflow_id not in state.workflows:
        raise HTTPException(404, "Workflow not found")
    return {"workflow": state.workflows[workflow_id]}

@app.put("/api/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, workflow: Workflow):
    """更新工作流"""
    if workflow_id not in state.workflows:
        raise HTTPException(404, "Workflow not found")
    
    workflow.id = workflow_id
    state.workflows[workflow_id] = workflow
    logger.info(f"Updated workflow: {workflow_id}")
    return {"workflow": workflow}

@app.delete("/api/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """删除工作流"""
    if workflow_id not in state.workflows:
        raise HTTPException(404, "Workflow not found")
    
    del state.workflows[workflow_id]
    logger.info(f"Deleted workflow: {workflow_id}")
    return {"success": True}


# ============ Proxy API (LiteLLM风格) ============

@app.post("/v1/chat/completions")
async def proxy_chat_completions(request: ProxyRequest):
    """代理Chat Completions请求 - 类似LiteLLM"""
    # 获取可用Key
    provider = Provider(request.provider) if request.provider else None
    key = await state.rotator.get_key(provider=provider, model=request.model)
    
    if not key:
        raise HTTPException(503, "No available API keys")
    
    try:
        # 这里应该实际调用API
        # 简化版本：返回模拟响应
        logger.info(f"Proxying request to {key.provider} using key {key.id}")
        
        # 记录使用
        await state.rotator.report_success(key.id, tokens=100, cost=0.001)
        await state.quota_tracker.record_usage(key.id, tokens=100, cost=0.001)
        
        return {
            "id": f"chatcmpl-{int(time.time() * 1000)}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": request.model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a simulated response from HermesMesh proxy."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 50,
                "completion_tokens": 50,
                "total_tokens": 100
            },
            "key_id": key.id,
            "provider": key.provider
        }
    except Exception as e:
        await state.rotator.report_failure(key.id, "unknown")
        raise HTTPException(500, str(e))


# ============ WebSocket ============

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket连接 - 实时更新"""
    await websocket.accept()
    state.websocket_clients.append(websocket)
    logger.info(f"WebSocket client connected. Total: {len(state.websocket_clients)}")
    
    try:
        # 发送初始状态
        stats = await state.key_pool.get_stats()
        await websocket.send_json({"type": "stats", "data": stats})
        
        # 保持连接
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30)
                # 处理客户端消息
                await handle_websocket_message(websocket, data)
            except asyncio.TimeoutError:
                # 发送心跳
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        state.websocket_clients.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(state.websocket_clients)}")

async def handle_websocket_message(websocket: WebSocket, message: str):
    """处理WebSocket消息"""
    try:
        data = json.loads(message)
        msg_type = data.get("type")
        
        if msg_type == "get_stats":
            stats = await state.key_pool.get_stats()
            await websocket.send_json({"type": "stats", "data": stats})
        elif msg_type == "get_keys":
            keys = await state.key_pool.get_all_keys()
            await websocket.send_json({"type": "keys", "data": [k.to_dict() for k in keys]})
    except Exception as e:
        logger.error(f"WebSocket message error: {e}")

async def broadcast_update(message: Dict[str, Any]):
    """广播更新到所有WebSocket客户端"""
    disconnected = []
    for client in state.websocket_clients:
        try:
            await client.send_json(message)
        except:
            disconnected.append(client)
    
    for client in disconnected:
        state.websocket_clients.remove(client)


# ============ System API ============

@app.get("/api/system/status")
async def get_system_status():
    """获取系统状态"""
    pool_stats = await state.key_pool.get_stats()
    health_stats = state.health_checker.get_stats()
    
    return {
        "status": "running",
        "uptime": time.time(),
        "keys": pool_stats,
        "health": health_stats,
        "workflows": len(state.workflows),
        "websocket_clients": len(state.websocket_clients)
    }

@app.get("/api/system/config")
async def get_system_config():
    """获取系统配置"""
    return {
        "rotation_strategy": state.rotator.get_strategy(),
        "health_check_interval": state.health_checker.check_interval,
        "warning_threshold": state.quota_tracker.warning_threshold,
        "critical_threshold": state.quota_tracker.critical_threshold
    }


# ============ Run ============

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
