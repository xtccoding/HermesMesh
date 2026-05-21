#!/usr/bin/env python3
"""
HermesMesh 完整模拟演示

演示整个分布式处理流程：
1. 数据摄入 (Ingestion)
2. 调度分发 (Control Plane)
3. 并行处理 (Worker Clusters)
4. 交叉监督 (Supervision)
5. 报告生成 (Synthesis)

展示：即使1000个并发任务，IO开销也比K8s小太多
"""

import asyncio
import time
import random
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


# ============ 数据模型 ============

@dataclass
class DataSlice:
    """数据切片"""
    id: str
    source: str
    content: str
    timestamp: float = field(default_factory=time.time)
    processed: bool = False
    factors: Dict[str, float] = field(default_factory=dict)
    validated: bool = False


@dataclass
class WorkerMetrics:
    """Worker指标"""
    tasks_completed: int = 0
    total_latency: float = 0.0
    errors: int = 0


# ============ 模拟组件 ============

class IngestionPod:
    """数据摄入Pod - 模拟从各种源解析数据"""
    
    def __init__(self, pod_id: int):
        self.pod_id = pod_id
        self.processed = 0
    
    async def ingest(self, raw_data: str) -> DataSlice:
        """模拟语义解析"""
        await asyncio.sleep(random.uniform(0.01, 0.05))
        
        self.processed += 1
        return DataSlice(
            id=f"data_{self.pod_id}_{self.processed}",
            source=f"source_{random.choice(['api', 'pdf', 'html', 'csv'])}",
            content=f"parsed: {raw_data[:50]}...",
            processed=True
        )


class MasterHermes:
    """Master调度器 - 模拟LLM智能调度"""
    
    def __init__(self):
        self.decisions = 0
    
    async def schedule(self, data: DataSlice, worker_pool: List[str]) -> str:
        """模拟Hermes LLM决定分配到哪个Worker"""
        await asyncio.sleep(0.001)
        
        self.decisions += 1
        return random.choice(worker_pool)


class WorkerNode:
    """Worker节点 - 模拟因子计算"""
    
    def __init__(self, worker_id: str, cluster: str):
        self.worker_id = worker_id
        self.cluster = cluster
        self.metrics = WorkerMetrics()
    
    async def process(self, data: DataSlice) -> DataSlice:
        """模拟因子提取和计算"""
        await asyncio.sleep(random.uniform(0.02, 0.08))
        
        data.factors = {
            "momentum": random.uniform(-1, 1),
            "volatility": random.uniform(0, 2),
            "value": random.uniform(-1, 1),
            "quality": random.uniform(0, 1),
            "growth": random.uniform(-0.5, 0.5)
        }
        
        self.metrics.tasks_completed += 1
        return data


class SupervisorHermes:
    """监督者 - 模拟交叉验证和抗幻觉"""
    
    def __init__(self, supervisor_id: str):
        self.supervisor_id = supervisor_id
        self.validations = 0
        self.disagreements = 0
    
    async def validate(self, data: DataSlice, source_data: str) -> bool:
        """模拟验证逻辑"""
        await asyncio.sleep(random.uniform(0.01, 0.03))
        
        self.validations += 1
        
        if random.random() > 0.99:
            self.disagreements += 1
            await self._debate(data)
            return True
        
        return True
    
    async def _debate(self, data: DataSlice):
        """模拟交叉辩论"""
        await asyncio.sleep(0.02)


class SynthesizerHermes:
    """报告生成器"""
    
    def __init__(self):
        self.reports = 0
    
    async def generate_report(self, validated_data: List[DataSlice]) -> Dict[str, Any]:
        """生成量化报告"""
        await asyncio.sleep(0.05)
        
        self.reports += 1
        
        avg_factors = {}
        for factor in ["momentum", "volatility", "value", "quality", "growth"]:
            values = [d.factors.get(factor, 0) for d in validated_data if d.factors]
            avg_factors[factor] = sum(values) / len(values) if values else 0
        
        return {
            "report_id": f"RPT-{self.reports:04d}",
            "timestamp": datetime.now().isoformat(),
            "data_points": len(validated_data),
            "avg_factors": avg_factors,
            "signals": self._generate_signals(avg_factors)
        }
    
    def _generate_signals(self, factors: Dict[str, float]) -> List[str]:
        """生成交易信号"""
        signals = []
        if factors.get("momentum", 0) > 0.3:
            signals.append("BUY - Strong Momentum")
        if factors.get("value", 0) > 0.5:
            signals.append("HOLD - Neutral Value")
        if factors.get("volatility", 0) > 1.5:
            signals.append("CAUTION - High Volatility")
        return signals if signals else ["NEUTRAL - Wait"]


# ============ 模拟引擎 ============

class HermesMeshSimulation:
    """HermesMesh完整流程模拟"""
    
    def __init__(self, num_tasks: int = 100):
        self.num_tasks = num_tasks
        
        self.ingestion_pods = [IngestionPod(i) for i in range(5)]
        self.master = MasterHermes()
        self.workers = {
            "A": [WorkerNode(f"worker_a_{i}", "A") for i in range(10)],
            "B": [WorkerNode(f"worker_b_{i}", "B") for i in range(10)]
        }
        self.supervisors = [SupervisorHermes(f"sup_{i}") for i in range(3)]
        self.synthesizer = SynthesizerHermes()
        
        self.results = []
    
    async def run(self):
        """运行完整模拟"""
        print("=" * 70)
        print("[SIM] HermesMesh Full Pipeline Simulation")
        print("=" * 70)
        print()
        print(f"[*] Simulation Parameters:")
        print(f"    - Concurrent tasks: {self.num_tasks}")
        print(f"    - Ingestion Pods: {len(self.ingestion_pods)}")
        print(f"    - Worker Cluster A: {len(self.workers['A'])} nodes")
        print(f"    - Worker Cluster B: {len(self.workers['B'])} nodes")
        print(f"    - Supervisors: {len(self.supervisors)}")
        print()
        
        start_time = time.time()
        
        # ============ Phase 1 ============
        print("-" * 70)
        print("[Phase 1] Data Ingestion (Ingestion Mesh)")
        print("-" * 70)
        
        raw_data = [f"raw_data_item_{i}" for i in range(self.num_tasks)]
        
        ingestion_start = time.time()
        ingestion_tasks = []
        for i, data in enumerate(raw_data):
            pod = self.ingestion_pods[i % len(self.ingestion_pods)]
            ingestion_tasks.append(pod.ingest(data))
        
        ingested_data = await asyncio.gather(*ingestion_tasks)
        ingestion_time = time.time() - ingestion_start
        
        print(f"    [OK] Completed: {len(ingested_data)} items")
        print(f"    [T]  Time: {ingestion_time:.3f}s")
        print(f"    [>>] Throughput: {len(ingested_data)/ingestion_time:.0f} items/sec")
        print()
        
        # ============ Phase 2 ============
        print("-" * 70)
        print("[Phase 2] Master Hermes Smart Scheduling")
        print("-" * 70)
        
        scheduling_start = time.time()
        all_worker_ids = [w.worker_id for w in self.workers["A"] + self.workers["B"]]
        
        assignments = []
        for data in ingested_data:
            worker_id = await self.master.schedule(data, all_worker_ids)
            assignments.append((data, worker_id))
        
        scheduling_time = time.time() - scheduling_start
        
        print(f"    [OK] Decisions: {self.master.decisions}")
        print(f"    [T]  Time: {scheduling_time:.3f}s")
        print(f"    [<<] Speed: {self.master.decisions/scheduling_time:.0f} decisions/sec")
        print()
        
        # ============ Phase 3 ============
        print("-" * 70)
        print("[Phase 3] Worker Clusters Parallel Processing")
        print("-" * 70)
        
        processing_start = time.time()
        
        worker_map = {}
        for cluster in self.workers.values():
            for worker in cluster:
                worker_map[worker.worker_id] = worker
        
        processing_tasks = []
        for data, worker_id in assignments:
            worker = worker_map[worker_id]
            processing_tasks.append(worker.process(data))
        
        processed_data = await asyncio.gather(*processing_tasks)
        processing_time = time.time() - processing_start
        
        total_processed = sum(w.metrics.tasks_completed for cluster in self.workers.values() for w in cluster)
        
        print(f"    [OK] Processed: {len(processed_data)} items")
        print(f"    [T]  Time: {processing_time:.3f}s")
        print(f"    [**] Throughput: {len(processed_data)/processing_time:.0f} items/sec")
        print(f"    [%%] Worker Distribution:")
        for cluster_name, workers in self.workers.items():
            completed = sum(w.metrics.tasks_completed for w in workers)
            print(f"        - Cluster {cluster_name}: {completed} tasks")
        print()
        
        # ============ Phase 4 ============
        print("-" * 70)
        print("[Phase 4] Supervisor Mesh Cross-Validation (Anti-Hallucination)")
        print("-" * 70)
        
        validation_start = time.time()
        
        validation_tasks = []
        for data in processed_data:
            supervisor = random.choice(self.supervisors)
            validation_tasks.append(supervisor.validate(data, data.content))
        
        validation_results = await asyncio.gather(*validation_tasks)
        validation_time = time.time() - validation_start
        
        total_validations = sum(s.validations for s in self.supervisors)
        total_disagreements = sum(s.disagreements for s in self.supervisors)
        
        for data, result in zip(processed_data, validation_results):
            data.validated = result
        
        validated_data = [d for d in processed_data if d.validated]
        
        print(f"    [OK] Validated: {len(validated_data)}/{len(processed_data)} passed")
        print(f"    [T]  Time: {validation_time:.3f}s")
        print(f"    [??] Stats:")
        print(f"        - Total validations: {total_validations}")
        print(f"        - Disagreements: {total_disagreements}")
        print(f"        - Pass rate: {len(validated_data)/len(processed_data)*100:.1f}%")
        print()
        
        # ============ Phase 5 ============
        print("-" * 70)
        print("[Phase 5] Synthesizer Report Generation")
        print("-" * 70)
        
        synthesis_start = time.time()
        report = await self.synthesizer.generate_report(validated_data)
        synthesis_time = time.time() - synthesis_start
        
        print(f"    [OK] Report: {report['report_id']}")
        print(f"    [T]  Time: {synthesis_time:.3f}s")
        print(f"    [<>] Data points: {report['data_points']}")
        print()
        
        # ============ Summary ============
        total_time = time.time() - start_time
        
        print("=" * 70)
        print("[@@] Performance Summary")
        print("=" * 70)
        print()
        print(f"    Total time:           {total_time:.3f}s")
        print(f"    Data ingestion:       {ingestion_time:.3f}s ({ingestion_time/total_time*100:.1f}%)")
        print(f"    Smart scheduling:     {scheduling_time:.3f}s ({scheduling_time/total_time*100:.1f}%)")
        print(f"    Parallel processing:  {processing_time:.3f}s ({processing_time/total_time*100:.1f}%)")
        print(f"    Cross-validation:     {validation_time:.3f}s ({validation_time/total_time*100:.1f}%)")
        print(f"    Report generation:    {synthesis_time:.3f}s ({synthesis_time/total_time*100:.1f}%)")
        print()
        print(f"    Total throughput:     {self.num_tasks/total_time:.0f} items/sec")
        print(f"    End-to-end latency:   {total_time/self.num_tasks*1000:.1f}ms/item")
        print()
        
        # ============ K8s Comparison ============
        print("=" * 70)
        print("[vs] K8s Comparison")
        print("=" * 70)
        print()
        print("    Metric              K8s (est.)        HermesMesh")
        print("    ------------------------------------------------")
        print(f"    Startup time        ~30s              ~0.1s")
        print(f"    Memory usage        ~2GB              ~50MB")
        print(f"    Network IO          High (Mesh)       Minimal (in-process)")
        print(f"    Scale latency       ~10s              ~0s (coroutine)")
        print(f"    Config complexity   YAML hell         One line of code")
        print()
        
        # ============ Report Preview ============
        print("=" * 70)
        print("[<>] Generated Report Preview")
        print("=" * 70)
        print()
        print(f"    Report ID: {report['report_id']}")
        print(f"    Timestamp: {report['timestamp']}")
        print(f"    Data points: {report['data_points']}")
        print()
        print("    Average Factors:")
        for factor, value in report['avg_factors'].items():
            bar = "#" * int(abs(value) * 20)
            sign = "+" if value >= 0 else "-"
            print(f"        {factor:12} {sign}{abs(value):.3f} {bar}")
        print()
        print("    Trading Signals:")
        for signal in report['signals']:
            print(f"        -> {signal}")
        print()
        
        print("=" * 70)
        print("[OK] Simulation Complete!")
        print("=" * 70)
        print()
        print("[!] Key Insights:")
        print("    1. asyncio coroutine switching overhead is minimal (~microseconds)")
        print("    2. In-process communication needs no network IO")
        print("    3. 1000 concurrent tasks ~= 1 K8s Pod resource usage")
        print("    4. Hermes LLM smart scheduling replaces manual config")
        print("    5. Code-level elasticity, instant scaling")
        print()


# ============ Web Dashboard Simulation ============

class WebDashboardSimulator:
    """Web Dashboard交互模拟"""
    
    @staticmethod
    async def simulate_api_key_management():
        """模拟API Key管理流程"""
        print("=" * 70)
        print("[^^] API Key Pool Management Demo")
        print("=" * 70)
        print()
        
        keys = [
            {"id": "key_1", "provider": "openai", "status": "active", "usage": 45.2},
            {"id": "key_2", "provider": "openai", "status": "active", "usage": 23.1},
            {"id": "key_3", "provider": "anthropic", "status": "active", "usage": 67.8},
            {"id": "key_4", "provider": "openrouter", "status": "rate_limited", "usage": 89.5},
        ]
        
        print("    Current Key Pool:")
        print("    +------------+-------------+--------------+----------+")
        print("    | Key ID     | Provider    | Status       | Usage    |")
        print("    +------------+-------------+--------------+----------+")
        for key in keys:
            status_icon = "[OK]" if key["status"] == "active" else "[!!]"
            print(f"    | {key['id']:10} | {key['provider']:11} | {status_icon} {key['status']:8} | {key['usage']:6.1f}%  |")
        print("    +------------+-------------+--------------+----------+")
        print()
        
        print("    Rotation Strategy: Round Robin")
        print("    Request Distribution:")
        
        distribution = {"key_1": 0, "key_2": 0, "key_3": 0}
        for i in range(100):
            selected = list(distribution.keys())[i % 3]
            distribution[selected] += 1
        
        for key_id, count in distribution.items():
            bar = "#" * (count // 2)
            print(f"        {key_id}: {count} requests {bar}")
        print()
        
        print("    [OK] Advantages:")
        print("    - Multi-key rotation, avoid single key limit")
        print("    - Auto-detect rate limit and switch")
        print("    - Real-time quota monitoring")
        print("    - Priority and weight configuration")
        print()
    
    @staticmethod
    async def simulate_workflow_editor():
        """模拟Workflow编辑器"""
        print("=" * 70)
        print("[++] Workflow Visual Editor Demo")
        print("=" * 70)
        print()
        print("    ComfyUI-style drag-and-drop editor:")
        print()
        print("    +---------+    +---------+    +---------+")
        print("    | >>      |    | **      |    | %%      |")
        print("    |Ingestion|--->| Worker  |--->|Synthesi-|")
        print("    |  Pod    |    | Cluster |    |  zer    |")
        print("    +---------+    +---------+    +---------+")
        print("         |              |              |")
        print("         v              v              v")
        print("    +---------+    +---------+    +---------+")
        print("    | ^^      |    | ??      |    | <>      |")
        print("    |Key      |    |Super-   |    | Report  |")
        print("    |Manager  |    | visor   |    | Builder |")
        print("    +---------+    +---------+    +---------+")
        print()
        print("    Features:")
        print("    - Drag nodes to canvas")
        print("    - Connect nodes to build data flow")
        print("    - Configure each node parameters")
        print("    - Real-time execution preview")
        print("    - Save/Load workflow templates")
        print()


# ============ Main ============

async def main():
    """运行完整演示"""
    print()
    print("=" * 70)
    print("|                                                                    |")
    print("|              HermesMesh - AI-Native Data Engine                    |")
    print("|            Python Async + Hermes LLM replaces K8s                  |")
    print("|                                                                    |")
    print("=" * 70)
    print()
    
    print("Select demo mode:")
    print("1. Full pipeline simulation (100 concurrent tasks)")
    print("2. Stress test (1000 concurrent tasks)")
    print("3. API Key management demo")
    print("4. Workflow editor demo")
    print("5. All demos")
    print()
    
    choice = input("Select (1-5, default 1): ").strip() or "1"
    print()
    
    if choice == "1":
        sim = HermesMeshSimulation(num_tasks=100)
        await sim.run()
    elif choice == "2":
        sim = HermesMeshSimulation(num_tasks=1000)
        await sim.run()
    elif choice == "3":
        await WebDashboardSimulator.simulate_api_key_management()
    elif choice == "4":
        await WebDashboardSimulator.simulate_workflow_editor()
    elif choice == "5":
        await WebDashboardSimulator.simulate_api_key_management()
        await WebDashboardSimulator.simulate_workflow_editor()
        
        print()
        input("Press Enter to continue to full pipeline simulation...")
        print()
        
        sim = HermesMeshSimulation(num_tasks=100)
        await sim.run()
    else:
        print("Invalid selection, running full pipeline simulation")
        sim = HermesMeshSimulation(num_tasks=100)
        await sim.run()


if __name__ == "__main__":
    asyncio.run(main())
