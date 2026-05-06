"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route."""
        history = state.route_history
        
        if len(history) >= 6:
            state.record_route("done")
            return state
            
        if not history:
            state.record_route("researcher")
        elif history[-1] == "researcher":
            state.record_route("analyst")
        elif history[-1] == "analyst":
            state.record_route("writer")
        elif history[-1] == "writer":
            state.record_route("critic")
        else:
            state.record_route("done")
            
        return state
