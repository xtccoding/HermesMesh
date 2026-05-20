#!/usr/bin/env python3
"""
HermesMesh Web Manager - 启动脚本

启动Web管理界面，包含：
- 可视化Workflow编辑器
- API Key池化管理
- 实时监控仪表盘
- LiteLLM风格API代理
"""

import sys
import argparse
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))


def main():
    parser = argparse.ArgumentParser(description="HermesMesh Web Manager")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--log-level", default="info", help="Log level")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  HermesMesh Web Manager")
    print("=" * 60)
    print()
    print(f"  Dashboard: http://localhost:{args.port}")
    print(f"  API Docs:  http://localhost:{args.port}/docs")
    print()
    print("  Features:")
    print("  - Visual Workflow Editor (ComfyUI-style)")
    print("  - API Key Pool Management (LiteLLM-style)")
    print("  - Real-time Monitoring Dashboard")
    print("  - OpenAI-compatible API Proxy")
    print()
    print("=" * 60)
    
    import uvicorn
    uvicorn.run(
        "web.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()
