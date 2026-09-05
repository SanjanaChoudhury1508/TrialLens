from langgraph.graph import END, START, StateGraph

from app.agents.state import TrialLensState
from app.agents.router_agent import route_question
from app.agents.retriever_agent import retriever_agent
from app.agents.structured_agent import structured_agent
from app.agents.safety_agent import safety_agent
from app.agents.evidence_agent import aggregate_evidence
from app.agents.synthesis_agent import synthesis_agent
from app.agents.critic_agent import verify_answer


def dispatch_agents(state: TrialLensState):
    """
    Execute every specialist selected by the router.

    This keeps the orchestration explicit:
    Router -> selected specialist agents -> Evidence.
    """

    agents = state.get("agents_to_run", [])

    current_state = dict(state)

    if "retriever" in agents:
        result = retriever_agent.run(current_state)

        current_state.update(result)

    if "structured" in agents:
        result = structured_agent.run(current_state)

        current_state.update(result)

    if "safety" in agents:
        result = safety_agent.run(current_state)

        current_state.update(result)

    # Return only state updates that should be merged by LangGraph.
    return {
        "retrieved_documents": current_state.get(
            "retrieved_documents", []
        ),
        "structured_results": current_state.get(
            "structured_results", []
        ),
        "safety_results": current_state.get(
            "safety_results", []
        ),
        "errors": current_state.get(
            "errors", []
        ),
        "execution_trace": [
            "specialist_dispatch"
        ],
    }


def build_trial_lens_graph():

    graph = StateGraph(TrialLensState)

    graph.add_node("router", route_question)
    graph.add_node("specialists", dispatch_agents)
    graph.add_node("evidence", aggregate_evidence)
    graph.add_node("synthesis", synthesis_agent.run)
    graph.add_node("critic", verify_answer)

    graph.add_edge(START, "router")

    # Router -> all selected specialist agents
    graph.add_edge("router", "specialists")

    # Specialists -> evidence
    graph.add_edge("specialists", "evidence")

    # Evidence -> synthesis
    graph.add_edge("evidence", "synthesis")

    # Synthesis -> critic
    graph.add_edge("synthesis", "critic")

    # Critic -> END
    graph.add_edge("critic", END)

    return graph.compile()


trial_lens_graph = build_trial_lens_graph()