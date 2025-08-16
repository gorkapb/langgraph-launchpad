import structlog
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI

from config.settings import get_settings
from graph.state import GraphState

logger = structlog.get_logger()
settings = get_settings()


def example_agent(state: GraphState) -> dict:
    """
    Example agent node that processes user messages.
    
    Replace this with your own agent implementation.
    """
    try:
        logger.info("Example agent processing message")
        
        messages = state["messages"]
        user_question = state["user_question"]
        reasoning = state.get("reasoning", False)
        
        # Initialize the language model
        if settings.openai_api_key:
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                api_key=settings.openai_api_key,
                temperature=0.7
            )
            
            # Create a system prompt
            system_prompt = "You are a helpful AI assistant."
            if reasoning:
                system_prompt += " Please provide detailed reasoning for your responses."
            
            # Prepare messages for the LLM
            llm_messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    llm_messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    llm_messages.append({"role": "assistant", "content": msg.content})
            
            # Get response from LLM
            response = llm.invoke(llm_messages)
            response_content = response.content
            
        else:
            # Fallback response when no API key is provided
            response_content = f"Echo: {user_question} (No OpenAI API key configured)"
        
        logger.info("Example agent completed processing")
        
        return {
            "messages": messages + [AIMessage(content=response_content)],
            "current_step": "example_agent_completed",
        }
    
    except Exception as e:
        logger.error("Example agent failed", error=str(e))
        error_response = f"I encountered an error while processing your request: {str(e)}"
        
        return {
            "messages": messages + [AIMessage(content=error_response)],
            "current_step": "example_agent_error",
        }


def reasoning_agent(state: GraphState) -> dict:
    """
    Example reasoning agent that provides detailed explanations.
    """
    try:
        logger.info("Reasoning agent processing")
        
        messages = state["messages"]
        last_message = messages[-1] if messages else None
        
        if not last_message or not isinstance(last_message, AIMessage):
            return {
                "messages": messages,
                "current_step": "reasoning_skipped",
            }
        
        reasoning_prompt = f"""
        Please provide reasoning for this response: "{last_message.content}"
        
        Explain your thought process and why you chose this particular response.
        """
        
        reasoning_response = "Here's my reasoning: I provided a helpful response based on the user's question, taking into account the context and trying to be as accurate and useful as possible."
        
        logger.info("Reasoning agent completed")
        
        return {
            "messages": messages + [AIMessage(content=f"Reasoning: {reasoning_response}")],
            "current_step": "reasoning_completed",
        }
    
    except Exception as e:
        logger.error("Reasoning agent failed", error=str(e))
        return {
            "messages": messages,
            "current_step": "reasoning_error",
        }