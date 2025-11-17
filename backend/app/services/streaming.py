"""
SSE (Server-Sent Events) streaming utilities for FastAPI.
"""
import json
import logging
from typing import Dict, Any, AsyncGenerator, Tuple, Literal

logger = logging.getLogger(__name__)

# Type alias for structured events
EventType = Literal["stream_token", "stream_end", "status", "complete", "message", "error"]
StructuredEvent = Tuple[EventType, Dict[str, Any]]


def format_sse(event: str, data: Dict[str, Any]) -> str:
    """
    Format data as an SSE event.
    
    Args:
        event: Event type (e.g., 'stream_token', 'status', 'stream_end')
        data: Event data as a dictionary
    
    Returns:
        Formatted SSE string with event type and JSON data
    """
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def stream_llm_tokens(
    token_generator: AsyncGenerator[str, None],
    message_id: str
) -> AsyncGenerator[str, None]:
    """
    Convert LLM token generator to SSE stream_token events.
    
    Args:
        token_generator: Async generator yielding tokens
        message_id: ID of the message being streamed
    
    Yields:
        SSE-formatted stream_token events
    """
    try:
        async for token in token_generator:
            yield format_sse("stream_token", {
                "message_id": message_id,
                "token": token
            })
    except Exception as e:
        logger.error(f"Error streaming tokens: {e}")
        yield format_sse("error", {
            "message": "An error occurred while streaming the response"
        })


def status_event(status: str, message: str, metadata: Dict[str, Any] = None) -> str:
    """
    Create an SSE status event.
    
    Args:
        status: Status type (e.g., 'searching', 'processing', 'complete')
        message: Human-readable status message
        metadata: Optional additional metadata
    
    Returns:
        SSE-formatted status event
    """
    return format_sse("status", {
        "status": status,
        "message": message,
        "metadata": metadata or {}
    })


def stream_end_event(message_id: str, content: str, created_at: str) -> str:
    """
    Create an SSE stream_end event.
    
    Args:
        message_id: ID of the completed message
        content: Full message content
        created_at: ISO timestamp of message creation
    
    Returns:
        SSE-formatted stream_end event
    """
    return format_sse("stream_end", {
        "message_id": message_id,
        "content": content,
        "created_at": created_at
    })


def complete_event(goal_id: str, opportunities_count: int) -> str:
    """
    Create an SSE complete event.
    
    Args:
        goal_id: ID of the completed goal
        opportunities_count: Number of opportunities found
    
    Returns:
        SSE-formatted complete event
    """
    return format_sse("complete", {
        "goal_id": goal_id,
        "opportunities_count": opportunities_count
    })


def message_event(message_data: Dict[str, Any]) -> str:
    """
    Create an SSE message event.
    
    Args:
        message_data: Complete message object
    
    Returns:
        SSE-formatted message event
    """
    return format_sse("message", {
        "message": message_data
    })


def error_event(message: str) -> str:
    """
    Create an SSE error event.
    
    Args:
        message: Error message to display to user
    
    Returns:
        SSE-formatted error event
    """
    return format_sse("error", {
        "message": message
    })


def emit_event(event_type: EventType, data: Dict[str, Any]) -> str:
    """
    Generic event emitter that routes to the appropriate formatter.
    
    Args:
        event_type: Type of event to emit
        data: Event data
    
    Returns:
        SSE-formatted event string
    """
    return format_sse(event_type, data)
