import json
from typing import AsyncGenerator

import structlog
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.models import Thread
from ...utils.exceptions import GraphExecutionException, ThreadNotFoundException
from ..models.requests import ChatRequest
from ..models.responses import ChatResponse, ErrorResponse
from ...graph.builder import call_chatbot, stream_chatbot

router = APIRouter(tags=["chat"])
logger = structlog.get_logger()


@router.post(
    "/threads/{thread_id}/chat",
    response_model=ChatResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Thread not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Send a chat message",
    description="Send a message to the AI agent in a specific thread",
)
async def chat(
    thread_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """Send a chat message to the AI agent."""
    try:
        logger.info(
            "Processing chat message",
            thread_id=thread_id,
            message_length=len(request.message),
            reasoning=request.reasoning
        )
        
        # Verify thread exists
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not thread:
            raise ThreadNotFoundException(thread_id)
        
        # Call the chatbot
        response_content = call_chatbot(
            question=request.message,
            thread_id=thread_id,
            reasoning=request.reasoning
        )
        
        logger.info("Chat message processed successfully", thread_id=thread_id)
        
        return ChatResponse(
            response=response_content,
            thread_id=thread_id,
            reasoning=None,  # Add reasoning logic if needed
            metadata={"request_reasoning": request.reasoning}
        )
    
    except ThreadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found"
        )
    except GraphExecutionException as e:
        logger.error("Graph execution failed", error=str(e), thread_id=thread_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=e.message
        )
    except Exception as e:
        logger.error("Chat processing failed", error=str(e), thread_id=thread_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.post(
    "/threads/{thread_id}/chat/stream",
    responses={
        404: {"description": "Thread not found"},
        500: {"description": "Internal server error"},
    },
    summary="Send a chat message with streaming",
    description="Send a message to the AI agent with Server-Sent Events streaming",
)
async def chat_stream(
    thread_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Send a chat message with streaming response."""
    try:
        logger.info(
            "Processing streaming chat message",
            thread_id=thread_id,
            message_length=len(request.message)
        )
        
        # Verify thread exists
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Thread {thread_id} not found"
            )
        
        async def generate_response() -> AsyncGenerator[str, None]:
            """Generate streaming response."""
            try:
                async for chunk in stream_chatbot(
                    question=request.message,
                    thread_id=thread_id,
                    reasoning=request.reasoning
                ):
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps({'content': chunk, 'type': 'content'})}\n\n"
                
                # Send completion signal
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
            
            except Exception as e:
                logger.error("Streaming failed", error=str(e), thread_id=thread_id)
                error_data = {
                    "type": "error",
                    "error": "Streaming failed",
                    "details": str(e)
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            generate_response(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Stream setup failed", error=str(e), thread_id=thread_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup streaming"
        )


@router.websocket("/threads/{thread_id}/chat/ws")
async def chat_websocket(websocket: WebSocket, thread_id: int):
    """WebSocket endpoint for real-time chat."""
    await websocket.accept()
    logger.info("WebSocket connection established", thread_id=thread_id)
    
    try:
        # Verify thread exists (you might want to pass db session differently in websockets)
        # For now, we'll skip the verification or implement it differently
        
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                message = message_data.get("message", "")
                reasoning = message_data.get("reasoning", False)
                
                if not message:
                    await websocket.send_text(json.dumps({
                        "type": "error",
                        "error": "Empty message"
                    }))
                    continue
                
                logger.info("Processing WebSocket message", thread_id=thread_id)
                
                # Stream response back to client
                async for chunk in stream_chatbot(
                    question=message,
                    thread_id=thread_id,
                    reasoning=reasoning
                ):
                    await websocket.send_text(json.dumps({
                        "type": "content",
                        "content": chunk
                    }))
                
                # Send completion signal
                await websocket.send_text(json.dumps({"type": "done"}))
                
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": "Invalid JSON format"
                }))
            except Exception as e:
                logger.error("WebSocket message processing failed", error=str(e))
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "error": str(e)
                }))
    
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed", thread_id=thread_id)
    except Exception as e:
        logger.error("WebSocket error", error=str(e), thread_id=thread_id)
        await websocket.close()