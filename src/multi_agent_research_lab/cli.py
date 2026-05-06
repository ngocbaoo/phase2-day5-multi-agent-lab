"""Command-line entrypoint for the lab starter."""

from dotenv import load_dotenv
load_dotenv()

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()
from pathlib import Path
from datetime import datetime

def save_response(run_type: str, content: str) -> None:
    output_dir = Path("model_response")
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = output_dir / f"{run_type}_{timestamp}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    console.print(f"\n[bold green]Response saved to {filepath}[/bold green]")


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a minimal single-agent baseline placeholder."""

    _init()
    request = ResearchQuery(query=query)
    state = ResearchState(request=request)
    
    from multi_agent_research_lab.services.llm_client import LLMClient
    from multi_agent_research_lab.core.schemas import AgentName, AgentResult
    
    llm = LLMClient()
    response = llm.complete(
        system_prompt="You are a helpful research assistant. Provide a concise, well-researched answer with references.",
        user_prompt=query
    )
    
    state.final_answer = response.content
    state.agent_results.append(
        AgentResult(
            agent=AgentName.WRITER,
            content=response.content,
            metadata={"cost_usd": response.cost_usd, "input_tokens": response.input_tokens, "output_tokens": response.output_tokens}
        )
    )
    
    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline"))
    console.print(f"Estimated Cost: ${response.cost_usd:.4f}" if response.cost_usd else "Cost: Unknown")
    if state.final_answer:
        save_response("single", state.final_answer)


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow skeleton."""

    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))
    if result.final_answer:
        save_response("multi", result.final_answer)


if __name__ == "__main__":
    app()
