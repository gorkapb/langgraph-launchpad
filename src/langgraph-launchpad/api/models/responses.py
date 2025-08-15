from datetime import datetime
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field


class CreateThreadResponse(BaseModel):
    """Response model for thread creation."""
    
    thread_id: int = Field(
        ...,
        description="The unique identifier for the thread",
        example=1
    )
    
    user_id: str = Field(
        ...,
        description="User ID for the thread owner",
        example="user123"
    )
    
    created_at: datetime = Field(
        ...,
        description="Thread creation timestamp"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "thread_id": 1,
                "user_id": "user123",
                "created_at": "2024-01-01T12:00:00Z"
            }
        }


class MessageResponse(BaseModel):
    """Response model for individual messages."""
    
    is_user: bool = Field(
        ...,
        description="Whether this message is from a user",
        example=True
    )
    
    content: str = Field(
        ...,
        description="The message content",
        example="Hello, world!"
    )
    
    timestamp: Optional[datetime] = Field(
        None,
        description="Message timestamp"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional message metadata"
    )


class ChatResponse(BaseModel):
    """Response model for chat messages."""
    
    response: str = Field(
        ...,
        description="The AI response",
        example="Hello! How can I help you today?"
    )
    
    thread_id: int = Field(
        ...,
        description="The thread ID",
        example=1
    )
    
    reasoning: Optional[str] = Field(
        None,
        description="Reasoning behind the response (if requested)"
    )
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional response metadata"
    )


class ThreadHistoryResponse(BaseModel):
    """Response model for thread history."""
    
    thread_id: int = Field(
        ...,
        description="The thread ID",
        example=1
    )
    
    user_id: str = Field(
        ...,
        description="The thread owner's user ID",
        example="user123"
    )
    
    messages: List[MessageResponse] = Field(
        ...,
        description="List of messages in the thread"
    )
    
    created_at: datetime = Field(
        ...,
        description="Thread creation timestamp"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Thread last update timestamp"
    )


class ThreadInfo(BaseModel):
    """Response model for thread information."""
    
    thread_id: int = Field(
        ...,
        description="The thread ID",
        example=1
    )
    
    user_id: str = Field(
        ...,
        description="The thread owner's user ID",
        example="user123"
    )
    
    created_at: datetime = Field(
        ...,
        description="Thread creation timestamp"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Thread last update timestamp"
    )
    
    message_count: int = Field(
        default=0,
        description="Number of messages in the thread"
    )


class AllThreadsResponse(BaseModel):
    """Response model for listing all threads."""
    
    threads: List[ThreadInfo] = Field(
        ...,
        description="List of thread information"
    )
    
    total: int = Field(
        ...,
        description="Total number of threads"
    )


class UserThreadsResponse(BaseModel):
    """Response model for user threads."""
    
    user_id: str = Field(
        ...,
        description="The user ID",
        example="user123"
    )
    
    threads: List[ThreadInfo] = Field(
        ...,
        description="List of thread information for the user"
    )
    
    total: int = Field(
        ...,
        description="Total number of threads for the user"
    )


class AllUsersResponse(BaseModel):
    """Response model for listing all users."""
    
    users: List[str] = Field(
        ...,
        description="List of user IDs"
    )
    
    total: int = Field(
        ...,
        description="Total number of users"
    )


class ErrorResponse(BaseModel):
    """Response model for errors."""
    
    error: str = Field(
        ...,
        description="Error message",
        example="Thread not found"
    )
    
    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )
    
    status_code: int = Field(
        ...,
        description="HTTP status code",
        example=404
    )


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(
        ...,
        description="Service status",
        example="healthy"
    )
    
    version: str = Field(
        ...,
        description="Service version",
        example="0.1.0"
    )
    
    timestamp: datetime = Field(
        ...,
        description="Health check timestamp"
    )