from typing import AsyncGenerator, List

import structlog
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

from core.checkpoint import checkpointer
from utils.exceptions import GraphExecutionException
from graph.nodes.example_agent import example_agent, reasoning_agent
from graph.state import GraphState

logger = structlog.get_logger()


def create_graph() -> StateGraph:
    """Create and configure the LangGraph workflow."""
    builder = StateGraph(GraphState)
    
    # Add nodes
    builder.add_node("example_agent", example_agent)
    builder.add_node("reasoning_agent", reasoning_agent)
    
    # Add edges
    builder.add_edge(START, "example_agent")
    
    # Conditional edge: only add reasoning if requested
    def should_add_reasoning(state: GraphState) -> str:
        if state.get("reasoning", False):
            return "reasoning_agent"
        return END
    
    builder.add_conditional_edges(
        "example_agent",
        should_add_reasoning,
        {
            "reasoning_agent": "reasoning_agent",
            END: END
        }
    )
    
    builder.add_edge("reasoning_agent", END)
    
    return builder.compile(checkpointer=checkpointer)


# Create the global graph instance
graph = create_graph()


def call_chatbot(question: str, thread_id: int, reasoning: bool = False) -> str:
    """
    Synchronous function to call the chatbot and get a response.
    
    Args:
        question: The user's question
        thread_id: The thread ID for conversation context
        reasoning: Whether to include reasoning in the response
    
    Returns:
        The AI response content
    """
    try:
        logger.info("Calling chatbot", thread_id=thread_id, reasoning=reasoning)
        
        config = {"configurable": {"thread_id": str(thread_id)}}
        
        response = graph.invoke(
            {
                "messages": [HumanMessage(content=question, name="user")],
                "user_question": question,
                "reasoning": reasoning,
                "current_step": "start",
                "metadata": {},
            },
            config=config,
        )
        
        # Extract the last AI message
        messages = response.get("messages", [])
        if messages:
            last_message = messages[-1]
            return getattr(last_message, "content", "No response generated")
        
        return "No response generated"
    
    except Exception as e:
        logger.error("Chatbot call failed", error=str(e), thread_id=thread_id)
        raise GraphExecutionException(
            message=f"Failed to stream message in thread {thread_id}",
            original_error=e
        )


def get_thread_messages(thread_id: int) -> List[BaseMessage]:
    """
    Get all messages from a thread's conversation history.
    
    Args:
        thread_id: The thread ID
    
    Returns:
        List of messages in the thread
    """
    try:
        config = {"configurable": {"thread_id": str(thread_id)}}
        state = graph.get_state(config=config)
        
        if state and state.values:
            return state.values.get("messages", [])
        
        return []
    
    except Exception as e:
        logger.error("Failed to get thread messages", error=str(e), thread_id=thread_id)
        return []


def clear_thread_history(thread_id: int) -> bool:
    """
    Clear the conversation history for a thread.
    
    Args:
        thread_id: The thread ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        config = {"configurable": {"thread_id": str(thread_id)}}
        
        # Reset the thread state
        graph.update_state(
            config,
            {
                "messages": [],
                "user_question": "",
                "reasoning": False,
                "current_step": "cleared",
                "metadata": {},
            }
        )
        
        logger.info("Thread history cleared", thread_id=thread_id)
        return True
    
    except Exception as e:
        logger.error("Failed to clear thread history", error=str(e), thread_id=thread_id)
        return FalseExecutionException(
            message=f"Failed to process message in thread {thread_id}",
            original_error=e
        )


async def stream_chatbot(
    question: str, 
    thread_id: int, 
    reasoning: bool = False
) -> AsyncGenerator[str, None]:
    """
    Asynchronous function to stream chatbot responses.
    
    Args:
        question: The user's question
        thread_id: The thread ID for conversation context
        reasoning: Whether to include reasoning in the response
    
    Yields:
        Chunks of the AI response
    """
    try:
        logger.info("Starting chatbot streaming", thread_id=thread_id, reasoning=reasoning)
        
        config = {"configurable": {"thread_id": str(thread_id)}}
        
        # Stream the graph execution
        async for chunk in graph.astream(
            {
                "messages": [HumanMessage(content=question, name="user")],
                "user_question": question,
                "reasoning": reasoning,
                "current_step": "start",
                "metadata": {},
            },
            config=config,
        ):
            # Extract content from the chunk
            if "messages" in chunk:
                messages = chunk["messages"]
                if messages:
                    last_message = messages[-1]
                    content = getattr(last_message, "content", "")
                    if content:
                        # For streaming, we might want to yield the content in smaller chunks
                        # This is a simple implementation - you can make it more sophisticated
                        yield content
    
    except Exception as e:
        logger.error("Chatbot streaming failed", error=str(e), thread_id=thread_id)
        raise Graph