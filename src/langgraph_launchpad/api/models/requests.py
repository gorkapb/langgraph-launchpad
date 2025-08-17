from typing import Optional

from pydantic import BaseModel, Field


class CreateThreadRequest(BaseModel):
    """Request model for creating a new thread."""
    
    user_id: str = Field(
        ...,
        description="User ID for the thread owner",
        min_length=1,
        max_length=255,
        example="user123"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user123"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat messages."""
    
    message: str = Field(
        ...,
        description="The message content",
        min_length=1,
        max_length=10000,
        example="Hello, how can you help me?"
    )
    
    reasoning: bool = Field(
        default=False,
        description="Whether to include reasoning in the response"
    )
    
    stream: bool = Field(
        default=False,
        description="Whether to stream the response"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Hello, how can you help me?",
                "reasoning": False,
                "stream": False
            }
        }


class UpdateThreadRequest(BaseModel):
    """Request model for updating a thread."""
    
    user_id: Optional[str] = Field(
        None,
        description="New user ID for the thread",
        min_length=1,
        max_length=255
    )