"""Optional critic agent skeleton for bonus work."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.core.schemas import AgentName, AgentResult


class CriticAgent(BaseAgent):
    """Optional fact-checking and safety-review agent."""

    name = "critic"

    def run(self, state: ResearchState) -> ResearchState:
        """Validate final answer and append findings."""
        if not state.final_answer:
            return state
            
        llm = LLMClient()
        sources_text = "\n".join([s.title for s in state.sources])
        prompt = f"Query: {state.request.query}\n\nFinal Answer:\n{state.final_answer}\n\nSources:\n{sources_text}\n\nPerform a strict fact-check. Check for hallucination and citation coverage. Suggest improvements or output 'PASS' if it is perfect."
        
        response = llm.complete(
            system_prompt="You are a strict editor and fact-checker.",
            user_prompt=prompt
        )
        
        if "PASS" not in response.content.upper():
            state.errors.append("Critic raised concerns: " + response.content[:200])
        
        state.agent_results.append(
            AgentResult(
                agent=AgentName.CRITIC,
                content=response.content,
                metadata={"cost_usd": response.cost_usd}
            )
        )
        return state
