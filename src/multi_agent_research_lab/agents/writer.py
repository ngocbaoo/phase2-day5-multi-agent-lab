"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        llm = LLMClient()
        prompt = f"Query: {state.request.query}\nAudience: {state.request.audience}\n\nResearch:\n{state.research_notes}\n\nAnalysis:\n{state.analysis_notes}\n\nWrite the final comprehensive answer with proper citations."
        
        response = llm.complete(
            system_prompt="You are a professional tech writer. Write clear, well-structured articles with citations.",
            user_prompt=prompt
        )
        
        state.final_answer = response.content
        state.agent_results.append(
            AgentResult(
                agent=AgentName.WRITER,
                content=response.content,
                metadata={"cost_usd": response.cost_usd}
            )
        )
        return state
