from typing import Any, List, TypedDict

from langchain_core.messages import BaseMessage


class GraphState(TypedDict):
    """State definition for the LangGraph workflow."""
    
    messages: List[BaseMessage]
    user_question: str
    reasoning: bool
    # Add your custom state fields here
    current_step: str
    metadata: dict[str, Any]


# You can extend this state for your specific use case
class ExtendedGraphState(GraphState):
    """Extended state with additional fields for complex workflows."""
    
    agent_outputs: dict[str, Any]
    processing_context: dict[str, Any]
    error_state: bool