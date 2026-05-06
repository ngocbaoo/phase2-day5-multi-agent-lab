"""LangGraph workflow skeleton."""

from langgraph.graph import StateGraph, END
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.agents.critic import CriticAgent

class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""
    
    def __init__(self):
        self.graph = self.build()

    def build(self) -> object:
        """Create a LangGraph graph."""
        workflow = StateGraph(ResearchState)
        
        supervisor = SupervisorAgent()
        researcher = ResearcherAgent()
        analyst = AnalystAgent()
        writer = WriterAgent()
        critic = CriticAgent()
        
        workflow.add_node("supervisor", supervisor.run)
        workflow.add_node("researcher", researcher.run)
        workflow.add_node("analyst", analyst.run)
        workflow.add_node("writer", writer.run)
        workflow.add_node("critic", critic.run)
        
        workflow.set_entry_point("supervisor")
        
        def router(state: ResearchState):
            if not state.route_history:
                return "END"
            last_route = state.route_history[-1]
            if last_route == "done":
                return "END"
            return last_route
            
        workflow.add_conditional_edges(
            "supervisor",
            router,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "critic": "critic",
                "END": END
            }
        )
        
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")
        workflow.add_edge("critic", "supervisor")
        
        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        final_state = self.graph.invoke(state)
        if isinstance(final_state, ResearchState):
            return final_state
        if isinstance(final_state, dict):
            # In langgraph 0.2+, the output is usually a dict
            return ResearchState(**final_state)
        return state
