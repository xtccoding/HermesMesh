<div align="center">

# 🏛️ HermesMesh

### The AI-Native Data Engine

**A Distributed, Self-Scaling & Convolutional Multi-Agent Mesh Powered Entirely by Hermes**

[![License MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Hermes Powered](https://img.shields.io/badge/LLM-Hermes--3-orange)](https://github.com/NousResearch/Hermes-3)

[Quick Start](#-quick-start) • [Features](#-features) • [Architecture](#-architecture) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 📖 Overview

**HermesMesh** is a fully AI-native distributed intelligent quantitative analysis platform powered entirely by Hermes-3 LLM. It eliminates traditional ETL scripts and crawler rules by leveraging pure semantic understanding for data ingestion, processing, and report generation.

### Why HermesMesh?

| Traditional Approach | HermesMesh |
|---------------------|------------|
| ❌ Hard-coded regex parsers | ✅ Pure semantic understanding |
| ❌ Manual K8s scaling | ✅ Code-level auto-scaling |
| ❌ LLM hallucination risk | ✅ Convolutional supervision |
| ❌ Single API key limits | ✅ Multi-key pool rotation |
| ❌ Complex YAML configs | ✅ Zero-config deployment |

---

## 🖼️ System Architecture

<div align="center">
  <img src="docs/arch.png" alt="HermesMesh Architecture" width="100%">
  <p><em>HermesMesh System Architecture - Full Pipeline Visualization</em></p>
</div>

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           📥 INGESTION MESH                                 │
│  HTML • PDF • API • CSV │ Semantic Parsing │ Edge Cleaning                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         🧠 CONTROL PLANE                                    │
│  Master Hermes │ Load Balancer │ Task Scheduler │ Auto-Scaling              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
┌───────────────────────────────┐     ┌───────────────────────────────┐
│     ⚙️ WORKER CLUSTER A       │     │     📈 WORKER CLUSTER B       │
│  Data Extraction • Cleaning   │     │  Factor Calc • Anomaly Det    │
└───────────────────────────────┘     └───────────────────────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        🔍 SUPERVISION MESH                                  │
│  Cross-Debate │ Alignment Tools │ Consensus Voting │ Anti-Hallucination     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         📊 SYNTHESIS LAYER                                  │
│  Report Builder │ Signal Generator │ Commercial-Grade Output                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Features

### 🔄 Visual Workflow Editor
- **ComfyUI-style** drag-and-drop interface
- Real-time node connection and data flow visualization
- Custom node configuration and presets

### 🔑 API Key Pool Management
- **LiteLLM-style** multi-key rotation
- Support for OpenAI, Anthropic, OpenRouter, and custom providers
- Smart strategies: Round Robin, Priority, Weighted, Least Used, Failover
- Real-time quota tracking and automatic failover

### 📊 Monitoring Dashboard
- Real-time metrics: requests, tokens, costs, latency
- Health check with auto-disable/recovery
- Activity logging and alert system

### 🌐 OpenAI-Compatible API Proxy
- Drop-in replacement for OpenAI API
- Automatic key selection and load balancing
- Works with any OpenAI-compatible SDK

### 🛡️ Anti-Hallucination System
- Cross-debate mechanism between supervisors
- Hard verification with Python/Pandas
- Consensus voting for result validation

### ⚡ Zero-K8s Elastic Scaling
- Pure code-level auto-scaling
- No YAML configurations needed
- AsyncIO-based high-performance processing

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Redis (optional, for caching)
- Kafka/NATS (optional, for message queue)

### Installation

```bash
# Clone the repository
git clone https://github.com/xtccoding/HermesMesh.git
cd HermesMesh

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r web/requirements.txt
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# - OPENAI_API_KEY or other provider keys
# - Database connections (optional)
# - Message queue settings (optional)
```

### Launch

```bash
# Option 1: Start Web Management Dashboard
python web_start.py

# Option 2: Start Pipeline Only
python quick_start.py

# Option 3: CLI Mode
python -m hermesmesh.cli run --worker-instances 10
```

### Access

| Service | URL |
|---------|-----|
| 🖥️ Web Dashboard | http://localhost:8000 |
| 📚 API Documentation | http://localhost:8000/docs |
| 🔌 API Proxy Endpoint | http://localhost:8000/v1/chat/completions |

---

## 📁 Project Structure

```
HermesMesh/
├── 📄 README.md                    # This file
├── 📄 LICENSE                      # MIT License
├── 📄 pyproject.toml               # Python project config
├── 📄 requirements.txt             # Core dependencies
├── 📄 quick_start.py               # Quick start script
├── 📄 web_start.py                 # Web dashboard launcher
│
├── 📂 src/hermesmesh/              # Core pipeline modules
│   ├── 📂 ingestion/               # Data ingestion mesh
│   │   ├── pods.py                 # Ingestion pod manager
│   │   ├── parsers.py              # Semantic document parsers
│   │   └── cleaners.py             # Data cleaning filters
│   │
│   ├── 📂 control_plane/           # Orchestration center
│   │   ├── master_hermes.py        # Master scheduler
│   │   ├── scheduler.py            # Task scheduler
│   │   └── load_balancer.py        # Load balancing
│   │
│   ├── 📂 feature_workers/         # Processing clusters
│   │   ├── cluster_a.py            # Data extraction workers
│   │   ├── cluster_b.py            # Factor calculation workers
│   │   ├── factor_calculator.py    # Quantitative factors
│   │   └── anomaly_detector.py     # Anomaly detection
│   │
│   ├── 📂 supervision/             # Anti-hallucination mesh
│   │   ├── supervisor_hermes.py    # Supervisor network
│   │   ├── cross_debate.py         # Debate engine
│   │   ├── alignment_tools.py      # Verification tools
│   │   └── consensus_voting.py     # Voting mechanism
│   │
│   └── 📂 synthesis/               # Report generation
│       ├── synthesizer_hermes.py   # Synthesizer agent
│       ├── report_builder.py       # Report construction
│       └── signal_generator.py     # Trading signals
│
├── 📂 key_manager/                 # API Key pool management
│   ├── key_pool.py                 # Key pool manager
│   ├── key_rotator.py              # Smart rotation strategies
│   ├── health_checker.py           # Health monitoring
│   └── quota_tracker.py            # Quota tracking
│
├── 📂 web/                         # Web management dashboard
│   ├── app.py                      # FastAPI backend
│   ├── requirements.txt            # Web dependencies
│   └── templates/
│       └── index.html              # Dashboard UI
│
├── 📂 config/                      # Configuration files
│   ├── ingestion/                  # Ingestion configs
│   ├── workers/                    # Worker configs
│   ├── supervisor/                 # Supervision rules
│   └── synthesizer/                # Report templates
│
├── 📂 docs/                        # Documentation
│   ├── arch.png                    # Architecture diagram
│   ├── index.html                  # Interactive demo
│   ├── architecture.md             # Architecture details
│   ├── configuration.md            # Configuration guide
│   └── troubleshooting.md          # Troubleshooting guide
│
└── 📂 examples/                    # Usage examples
    ├── simple_pipeline.py          # Basic pipeline
    └── advanced_configuration.py   # Advanced setup
```

---

## 🔑 API Key Management

HermesMesh includes a powerful API key pool manager similar to LiteLLM:

### Adding Keys via Web UI

1. Open the Dashboard at http://localhost:8000
2. Navigate to "Key Management"
3. Click "+ Add Key"
4. Enter your API key details

### Adding Keys via API

```bash
curl -X POST http://localhost:8000/api/keys \
  -H "Content-Type: application/json" \
  -d '{
    "key": "sk-your-api-key",
    "provider": "openai",
    "name": "My OpenAI Key",
    "priority": 5,
    "quota_limit": 100.0,
    "rpm_limit": 60
  }'
```

### Using the Proxy

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="any-key"  # Managed by HermesMesh
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Rotation Strategies

| Strategy | Description |
|----------|-------------|
| `round_robin` | Rotate through keys sequentially |
| `priority` | Use highest priority key first |
| `weighted` | Distribute based on weight |
| `least_used` | Select least frequently used |
| `failover` | Switch on failure |
| `random` | Random selection |

---

## 📊 Monitoring

### Real-time Metrics

- **Active Keys**: Number of available API keys
- **Request Count**: Total requests processed
- **Token Usage**: Total tokens consumed
- **Cost Tracking**: Estimated API costs
- **Latency**: Average response time

### Health Checks

- Automatic health monitoring every 60 seconds
- Auto-disable keys after 3 consecutive failures
- Auto-recovery after cooldown period

---

## 🛠️ Configuration

### Environment Variables

```env
# LLM Configuration
OPENAI_API_KEY=sk-your-key
HERMES_MODEL=hermes-3-llama-3.1-8b

# Message Queue (optional)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
NATS_URL=nats://localhost:4222

# Database (optional)
REDIS_HOST=localhost
DATABASE_URL=postgresql://user:pass@localhost/hermesmesh

# Logging
LOG_LEVEL=INFO
```

### Worker Configuration

```yaml
# config/workers/cluster_a.yaml
cluster_a:
  max_instances: 50
  min_instances: 5
  scaling_factor: 1.5
  max_queue_size: 1000
```

---

## 📚 Documentation

- [Architecture Guide](docs/architecture.md) - System design and components
- [Configuration Guide](docs/configuration.md) - Detailed configuration options
- [Troubleshooting Guide](docs/troubleshooting.md) - Common issues and solutions
- [API Reference](http://localhost:8000/docs) - Interactive API documentation

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone and setup
git clone https://github.com/xtccoding/HermesMesh.git
cd HermesMesh
python -m venv venv
source venv/bin/activate

# Install dev dependencies
pip install -r requirements.txt
pip install pytest ruff mypy

# Run tests
pytest tests/

# Run linter
ruff check src/

# Start development server
python web_start.py --reload --log-level debug
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Hermes-3](https://github.com/NousResearch/Hermes-3) by NousResearch
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [LiteLLM](https://github.com/BerriAI/litellm) for inspiration on key management

---

<div align="center">

**Built with ❤️ by the HermesMesh Team**

[⬆ Back to Top](#-hermesmesh)

</div>
