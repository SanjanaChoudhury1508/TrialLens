from typing import Annotated, Any, Dict, List, Optional, TypedDict
import operator

class TrialLensState(TypedDict, total=False):
    """
    Shared state passed between TrialLens LangGraph agents.

    Each agent reads information from this state and adds its
    own evidence/results without destroying information produced
    by previous agents.
    """

    # User interaction
    question: str
    conversation_context: Optional[str]

    # Routing
    intent: str
    agents_to_run: List[str]

    # Evidence collected by different agents
    retrieved_documents: List[Dict[str, Any]]
    structured_results: List[Dict[str, Any]]
    safety_results: List[Dict[str, Any]]
    table_results: List[Dict[str, Any]]
    visual_results: List[Dict[str, Any]]

    # Combined evidence
    evidence: List[Dict[str, Any]]

    # Answer generation
    draft_answer: str
    final_answer: str

    # Verification
    verification_passed: bool
    verification_issues: List[str]

    # Sources/citations
    sources: List[Dict[str, Any]]

    # Basic execution metadata
    errors: List[str]
    execution_trace: Annotated[List[str], operator.add]