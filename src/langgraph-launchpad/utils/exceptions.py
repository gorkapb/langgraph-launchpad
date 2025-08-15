from typing import Any, Dict, Optional


class LangGraphLaunchpadException(Exception):
    """Base exception class for LangGraph Launchpad."""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500,
    ):
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ThreadNotFoundException(LangGraphLaunchpadException):
    """Exception raised when thread is not found."""
    
    def __init__(self, thread_id: int):
        super().__init__(
            message=f"Thread with ID {thread_id} not found",
            details={"thread_id": thread_id},
            status_code=404,
        )


class UserNotFoundException(LangGraphLaunchpadException):
    """Exception raised when user is not found."""
    
    def __init__(self, user_id: str):
        super().__init__(
            message=f"User with ID '{user_id}' not found",
            details={"user_id": user_id},
            status_code=404,
        )


class GraphExecutionException(LangGraphLaunchpadException):
    """Exception raised during graph execution."""
    
    def __init__(self, message: str, original_error: Exception = None):
        details = {}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__
        
        super().__init__(
            message=f"Graph execution failed: {message}",
            details=details,
            status_code=500,
        )