"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.search_client import SearchClient
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        search_client = SearchClient()
        sources = search_client.search(state.request.query, max_results=state.request.max_sources)
        state.sources.extend(sources)
        
        sources_text = "\n\n".join([f"Source: {s.title}\nURL: {s.url}\nContent: {s.snippet}" for s in sources])
        
        llm = LLMClient()
        prompt = f"Extract the most relevant research notes for the query: '{state.request.query}'.\n\nSources:\n{sources_text}"
        response = llm.complete(
            system_prompt="You are an expert researcher. Synthesize factual notes with citations.",
            user_prompt=prompt
        )
        
        state.research_notes = response.content
        state.agent_results.append(
            AgentResult(
                agent=AgentName.RESEARCHER,
                content=response.content,
                metadata={"cost_usd": response.cost_usd}
            )
        )
        return state
