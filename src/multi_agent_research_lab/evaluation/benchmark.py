"""Benchmark skeleton for single-agent vs multi-agent."""

from time import perf_counter
from typing import Callable

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState


Runner = Callable[[str], ResearchState]


def run_benchmark(run_name: str, query: str, runner: Runner) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency and return a placeholder metric object."""
    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started
    
    total_cost = sum([r.metadata.get("cost_usd", 0.0) or 0.0 for r in state.agent_results])
    
    quality_score = 5.0
    if state.final_answer and len(state.sources) > 0:
        quality_score += 3.0
    if state.errors:
        quality_score -= 2.0
        
    metrics = BenchmarkMetrics(
        run_name=run_name, 
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=max(0.0, min(10.0, quality_score)),
        notes=f"Sources: {len(state.sources)}, Errors: {len(state.errors)}"
    )
    return state, metrics
