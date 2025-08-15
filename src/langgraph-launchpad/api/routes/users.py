import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.models import Thread
from ...utils.exceptions import UserNotFoundException
from ..models.responses import (
    AllUsersResponse,
    UserThreadsResponse,
    ThreadInfo,
    ErrorResponse,
)
from ...graph.builder import get_thread_messages

router = APIRouter(prefix="/users", tags=["users"])
logger = structlog.get_logger()


@router.get(
    "",
    response_model=AllUsersResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="List all users",
    description="Retrieve a list of all users who have threads",
)
async def get_all_users(db: Session = Depends(get_db)) -> AllUsersResponse:
    """Get all users."""
    try:
        logger.info("Retrieving all users")
        
        results = db.query(Thread.user_id).distinct().all()
        users = [user[0] for user in results]
        
        return AllUsersResponse(users=users, total=len(users))
    
    except Exception as e:
        logger.error("Failed to retrieve users", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )


@router.get(
    "/{user_id}/threads",
    response_model=UserThreadsResponse,
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    summary="Get user threads",
    description="Retrieve all conversation threads for a specific user",
)
async def get_user_threads(
    user_id: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> UserThreadsResponse:
    """Get all threads for a specific user."""
    try:
        logger.info("Retrieving user threads", user_id=user_id, skip=skip, limit=limit)
        
        threads = (
            db.query(Thread)
            .filter(Thread.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        if not threads:
            # Check if user exists at all
            user_exists = db.query(Thread).filter(Thread.user_id == user_id).first()
            if not user_exists:
                raise UserNotFoundException(user_id)
        
        total = db.query(Thread).filter(Thread.user_id == user_id).count()
        
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
        
        return UserThreadsResponse(
            user_id=user_id,
            threads=thread_infos,
            total=total
        )
    
    except UserNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{user_id}' not found"
        )
    except Exception as e:
        logger.error("Failed to retrieve user threads", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user threads"
        )