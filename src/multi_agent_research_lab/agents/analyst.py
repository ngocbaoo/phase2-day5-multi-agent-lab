"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        if not state.research_notes:
            state.analysis_notes = "No research notes to analyze."
            return state
            
        llm = LLMClient()
        prompt = f"Query: {state.request.query}\n\nResearch Notes:\n{state.research_notes}\n\nExtract key claims, compare viewpoints, and flag weak evidence."
        response = llm.complete(
            system_prompt="You are a critical data analyst. Provide structured insights and critique the evidence.",
            user_prompt=prompt
        )
        
        state.analysis_notes = response.content
        state.agent_results.append(
            AgentResult(
                agent=AgentName.ANALYST,
                content=response.content,
                metadata={"cost_usd": response.cost_usd}
            )
        )
        return state
