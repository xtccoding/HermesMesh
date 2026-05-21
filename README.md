<div align="center">

# 🏛️ HermesMesh

### The AI-Native Data Engine

**用 Python异步并发 + Hermes LLM 替代 K8s，实现轻量级分布式智能处理**

[![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Hermes Powered](https://img.shields.io/badge/LLM-Hermes--3-orange)](https://github.com/NousResearch/Hermes-3)

[Quick Start](#-quick-start) • [Why HermesMesh](#-why-hermesmesh) • [Architecture](#-architecture) • [CLI Commands](#-cli-commands) • [Web Dashboard](#-web-dashboard)

</div>

---

## 💡 Why HermesMesh?

### 传统方案 vs HermesMesh

| | K8s + 传统微服务 | HermesMesh |
|---|---|---|
| **部署复杂度** | YAML地狱，Helm Charts | `python web_start.py` 一行启动 |
| **扩缩容** | Pod调度，HPA配置 | asyncio任务动态创建/销毁 |
| **IO开销** | 容器网络，Service Mesh | 进程内异步通信，接近零开销 |
| **1000并发** | 需要大量Pod和网络资源 | 纯代码级协程，内存占用极小 |
| **智能调度** | 规则引擎，人工配置 | Hermes LLM 自动决策 |
| **故障恢复** | 健康检查+重启策略 | LLM推理+自动降级 |

### 核心优势

```
┌─────────────────────────────────────────────────────────────────┐
│                    传统 K8s 方案                                 │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                      │
│  │Pod 1│ │Pod 2│ │Pod 3│ │ ... │ │Pod N│  ← 每个Pod都有开销    │
│  └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                      │
│     └──────┴──────┴──────┴──────┴────┘                         │
│              Service Mesh / Kube-proxy                          │
│                    IO开销：大 ❌                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    HermesMesh 方案                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              单进程 asyncio 事件循环                        │  │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐                      │  │
│  │  │协程│ │协程│ │协程│ │协程│ │协程│  ← 轻量级任务         │  │
│  │  └────┘ └────┘ └────┘ └────┘ └────┘                      │  │
│  │         Hermes LLM 统一调度决策                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                    IO开销：极小 ✅                               │
└─────────────────────────────────────────────────────────────────┘
```

**即使1000个并发任务，IO开销也比一个完整的K8s集群小太多！**

---

## 🖼️ System Architecture

<div align="center">
  <img src="docs/arch.png" alt="HermesMesh Architecture" width="100%">
  <p><em>全链路 AI-Native 纯 Hermes 驱动型分布式智能量化分析平台</em></p>
</div>

### 数据流

```
原始数据 → [Ingestion Pods] → [消息队列] → [Master Hermes调度]
                                                    │
                        ┌───────────────────────────┼───────────────────────────┐
                        ▼                           ▼                           ▼
              [Worker Cluster A]          [Worker Cluster B]          [Worker Cluster C]
              (数据提取处理)              (因子计算分析)              (异常检测)
                        │                           │                           │
                        └───────────────────────────┼───────────────────────────┘
                                                    ▼
                                          [Supervisor Mesh]
                                          (交叉验证+抗幻觉)
                                                    │
                                                    ▼
                                          [Synthesizer Hermes]
                                          (报告生成+信号输出)
```

---

## 🚀 Quick Start

### 1. 安装

```bash
git clone https://github.com/xtccoding/HermesMesh.git
cd HermesMesh
pip install -r requirements.txt
pip install -r web/requirements.txt
```

### 2. 配置

```bash
cp .env.example .env
# 编辑 .env 添加你的 API Key
```

### 3. 启动

```bash
# 方式1: Web管理界面 (推荐)
python web_start.py

# 方式2: CLI命令行模式
python -m hermesmesh.cli run

# 方式3: 模拟演示
python demo_simulation.py
```

---

## 🖥️ CLI Commands

HermesMesh 提供强大的命令行工具：

```bash
# 启动完整管道
hermesmesh run --workers 10 --strategy round_robin

# 只启动数据摄入
hermesmesh ingest --source data.csv --batch-size 100

# 只启动Worker集群
hermesmesh workers --cluster A --instances 20

# 运行监督验证
hermesmesh supervise --debate-rounds 3

# 生成报告
hermesmesh synthesize --output report.md

# Key管理
hermesmesh keys add --provider openai --key sk-xxx
hermesmesh keys list
hermesmesh keys health-check

# 系统状态
hermesmesh status
hermesmesh metrics
```

### 命令示例

```bash
# 完整的端到端处理流程
$ hermesmesh run --config production.yaml

🏛️ HermesMesh v1.0.0 - AI-Native Data Engine
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[14:23:01] ✅ Ingestion Pods started (5 workers)
[14:23:02] ✅ Master Hermes initialized
[14:23:03] ✅ Worker Cluster A: 10 instances
[14:23:03] ✅ Worker Cluster B: 10 instances  
[14:23:04] ✅ Supervisor Mesh: 3 supervisors
[14:23:05] ✅ Synthesizer ready

📊 Processing Pipeline Active
   ├── Ingested: 1,234 documents
   ├── Processed: 1,156 factors
   ├── Validated: 1,150 (99.5%)
   └── Reports: 12 generated

Press Ctrl+C to stop
```

---

## 🌐 Web Dashboard

访问 http://localhost:8000 打开可视化管理界面：

### 功能模块

| 模块 | 功能 |
|------|------|
| **🔄 Workflow Editor** | 拖拽式可视化工作流编辑 |
| **🔑 Key Management** | API Key池化管理，多Key轮询 |
| **📊 Monitoring** | 实时监控：请求数、Token、费用、延迟 |
| **🌐 API Proxy** | OpenAI兼容的代理接口 |
| **⚙️ Settings** | 系统配置管理 |

### Key管理特性

```python
# 多Key自动轮询，避免单Key限额
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="any"  # HermesMesh自动管理Key
)

# 1000个并发请求，自动分配到不同Key
for i in range(1000):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"Task {i}"}]
    )
    # HermesMesh自动选择最优Key，不会触发限额
```

---

## 📁 Project Structure

```
HermesMesh/
├── 📄 README.md
├── 📄 web_start.py           # Web管理界面启动
├── 📄 quick_start.py         # 快速启动
├── 📄 demo_simulation.py     # 模拟演示
│
├── 📂 src/hermesmesh/        # 核心模块
│   ├── 📂 ingestion/         # 数据摄入
│   ├── 📂 control_plane/     # 调度中心
│   ├── 📂 feature_workers/   # 处理集群
│   ├── 📂 supervision/       # 监督验证
│   └── 📂 synthesis/         # 报告生成
│
├── 📂 key_manager/           # Key池管理
├── 📂 web/                   # Web界面
└── 📂 config/                # 配置文件
```

---

## 🔧 Core Concepts

### 1. 代码级弹性伸缩 (Zero-K8s Scaling)

```python
# 传统K8s: 需要配置HPA
# apiVersion: autoscaling/v2
# kind: HorizontalPodAutoscaler
# spec:
#   minReplicas: 5
#   maxReplicas: 100

# HermesMesh: 纯代码控制
async def scale_workers(queue_size: int):
    if queue_size > 1000:
        # 动态创建更多协程任务
        for _ in range(10):
            asyncio.create_task(worker())
    elif queue_size < 10:
        # 自动缩减
        cancel_idle_workers()
```

### 2. Hermes LLM 智能调度

```python
# Master Hermes 通过 Tool Calling 决策
async def schedule_task(task: Task):
    # Hermes分析任务语义，决定最优处理方式
    decision = await hermes.chat(
        messages=[{"role": "user", "content": f"调度任务: {task}"}],
        tools=[{
            "name": "assign_to_cluster",
            "parameters": {
                "cluster": "A or B",
                "priority": "1-10",
                "strategy": "round_robin|priority|weighted"
            }
        }]
    )
    return execute_decision(decision)
```

### 3. 抗幻觉监督机制

```python
# Supervisor交叉验证
async def validate_output(worker_output, source_data):
    # 多个Supervisor独立验证
    results = await asyncio.gather(
        supervisor_1.verify(worker_output, source_data),
        supervisor_2.verify(worker_output, source_data),
        supervisor_3.verify(worker_output, source_data)
    )
    
    # 共识投票
    if consensus(results):
        return worker_output
    else:
        # 触发辩论机制
        return await cross_debate(results)
```

---

## 📊 Performance

### IO开销对比

| 场景 | K8s方案 | HermesMesh |
|------|---------|------------|
| 10并发 | ~100ms 网络延迟 | ~1ms 协程切换 |
| 100并发 | ~500ms + 负载均衡开销 | ~5ms |
| 1000并发 | 需要大量Pod，延迟显著 | ~50ms，几乎无额外开销 |

### 资源占用

| 指标 | K8s (100 Pods) | HermesMesh (1000 协程) |
|------|----------------|------------------------|
| CPU | 高 (容器开销) | 低 (纯Python) |
| 内存 | ~10GB | ~500MB |
| 网络IO | 大 (Service Mesh) | 极小 (进程内通信) |
| 启动时间 | 分钟级 | 毫秒级 |

---

## 📚 Documentation

- [Architecture Guide](docs/architecture.md)
- [Configuration Guide](docs/configuration.md)
- [CLI Reference](docs/cli.md)
- [API Reference](http://localhost:8000/docs)

---

## 🤝 Contributing

```bash
# 开发环境
pip install -r requirements.txt
pip install pytest ruff mypy

# 运行测试
pytest tests/

# 代码检查
ruff check src/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

<div align="center">

**用代码的力量替代基础设施的复杂性**

[⬆ Back to Top](#-hermesmesh)

</div>
