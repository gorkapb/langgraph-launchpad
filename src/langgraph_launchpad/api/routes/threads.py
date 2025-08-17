from typing import List

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from langgraph_launchpad.core.database import get_db
from langgraph_launchpad.core.models import Thread
from langgraph_launchpad.utils.exceptions import ThreadNotFoundException
from langgraph_launchpad.api.models.requests import CreateThreadRequest, UpdateThreadRequest
from langgraph_launchpad.api.models.responses import (
    AllThreadsResponse,
    CreateThreadResponse,
    ThreadHistoryResponse,
    ThreadInfo,
    ErrorResponse,
)
from langgraph_launchpad.graph.builder import get_thread_messages

router = APIRouter(prefix="/threads", tags=["threads"])
logger = structlog.get_logger()


@router.post(
    "",
    response_model=CreateThreadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Create a new thread",
    description="Create a new conversation thread for a user",
)
async def create_thread(
    request: CreateThreadRequest,
    db: Session = Depends(get_db)
) -> CreateThreadResponse:
    """Create a new conversation thread."""
    try:
        logger.info("Creating new thread", user_id=request.user_id)
        
        thread = Thread(user_id=request.user_id)
        db.add(thread)
        db.commit()
        db.refresh(thread)
        
        logger.info("Thread created successfully", thread_id=thread.thread_id)
        
        return CreateThreadResponse(
            thread_id=thread.thread_id,
            user_id=thread.user_id,
            created_at=thread.created_at,
        )
    
    except Exception as e:
        logger.error("Failed to create thread", error=str(e), user_id=request.user_id)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create thread"
        )


@router.get(
    "/{thread_id}",
    response_model=ThreadHistoryResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Thread not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get thread history",
    description="Retrieve the conversation history for a specific thread",
)
async def get_thread_history(
    thread_id: int,
    db: Session = Depends(get_db)
) -> ThreadHistoryResponse:
    """Get thread conversation history."""
    try:
        logger.info("Retrieving thread history", thread_id=thread_id)
        
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not thread:
            raise ThreadNotFoundException(thread_id)
        
        messages = get_thread_messages(thread_id)
        
        # Convert messages to response format
        from ..models.responses import MessageResponse
        message_responses = []
        for msg in messages:
            message_responses.append(
                MessageResponse(
                    is_user=getattr(msg, "name", "") == "user",
                    content=getattr(msg, "content", ""),
                    metadata=getattr(msg, "additional_kwargs", {}),
                )
            )
        
        return ThreadHistoryResponse(
            thread_id=thread.thread_id,
            user_id=thread.user_id,
            messages=message_responses,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
        )
    
    except ThreadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found"
        )
    except Exception as e:
        logger.error("Failed to retrieve thread history", error=str(e), thread_id=thread_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve thread history"
        )


@router.get(
    "",
    response_model=AllThreadsResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="List all threads",
    description="Retrieve a list of all conversation threads",
)
async def get_all_threads(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> AllThreadsResponse:
    """Get all threads with pagination."""
    try:
        logger.info("Retrieving all threads", skip=skip, limit=limit)
        
        threads = db.query(Thread).offset(skip).limit(limit).all()
        total = db.query(Thread).count()
        
        thread_infos = []
        for thread in threads:
            # Get message count for each thread
            try:
                messages = get_thread_messages(thread.thread_id)
                message_count = len(messages)
            except Exception:
                message_count = 0
            
            thread_infos.append(
                ThreadInfo(
                    thread_id=thread.thread_id,
                    user_id=thread.user_id,
                    created_at=thread.created_at,
                    updated_at=thread.updated_at,
                    message_count=message_count,
                )
            )
        
        return AllThreadsResponse(threads=thread_infos, total=total)
    
    except Exception as e:
        logger.error("Failed to retrieve threads", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve threads"
        )


@router.delete(
    "/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Thread not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Delete a thread",
    description="Delete a conversation thread and its history",
)
async def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db)
) -> None:
    """Delete a conversation thread."""
    try:
        logger.info("Deleting thread", thread_id=thread_id)
        
        thread = db.query(Thread).filter(Thread.thread_id == thread_id).first()
        if not thread:
            raise ThreadNotFoundException(thread_id)
        
        db.delete(thread)
        db.commit()
        
        logger.info("Thread deleted successfully", thread_id=thread_id)
        
    except ThreadNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Thread {thread_id} not found"
        )
    except Exception as e:
        logger.error("Failed to delete thread", error=str(e), thread_id=thread_id)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete thread"
        )