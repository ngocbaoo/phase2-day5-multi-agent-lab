"""Benchmark report rendering."""

from multi_agent_research_lab.core.schemas import BenchmarkMetrics


def render_markdown_report(metrics: list[BenchmarkMetrics]) -> str:
    """Render benchmark metrics to markdown."""
    lines = [
        "# Benchmark Report", 
        "", 
        "## Summary",
        "A comparison between Single-Agent Baseline and Multi-Agent Workflow.",
        "",
        "| Run | Latency (s) | Cost (USD) | Quality (0-10) | Notes |", 
        "|---|---:|---:|---:|---|"
    ]
    for item in metrics:
        cost = "" if item.estimated_cost_usd is None else f"${item.estimated_cost_usd:.4f}"
        quality = "" if item.quality_score is None else f"{item.quality_score:.1f}/10"
        lines.append(f"| **{item.run_name}** | {item.latency_seconds:.2f}s | {cost} | {quality} | {item.notes} |")
        
    lines.append("")
    lines.append("## Analysis")
    lines.append("Multi-agent workflows typically have higher latency and cost but produce better quality answers with more robust citation checking.")
    return "\n".join(lines) + "\n"
