import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_conversation_streams(client: AsyncClient):
    """Test that creating a conversation returns SSE stream"""
    async with client.stream(
        "POST",
        "/api/chat/",
        json={"initial_message": "Find AI conferences"},
        headers={"Authorization": "Bearer test"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Read some events
        conversation_id = None
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                import json
                data = json.loads(line[6:])
                if "conversation_id" in data:
                    conversation_id = data["conversation_id"]
                    break
        
        assert conversation_id is not None


# Removed test_realtime_token as Ably is no longer used


@pytest.mark.asyncio
async def test_answer_questions_streams(client: AsyncClient):
    """Test that answering questions returns SSE stream"""
    # First create a conversation via stream
    conversation_id = None
    async with client.stream(
        "POST",
        "/api/chat/",
        json={"initial_message": "Find remote ML jobs"},
        headers={"Authorization": "Bearer test"},
    ) as response:
        async for line in response.aiter_lines():
            if line.startswith("data:"):
                import json
                data = json.loads(line[6:])
                if "conversation_id" in data:
                    conversation_id = data["conversation_id"]
                    break
    
    assert conversation_id is not None

    # Answer clarifying questions (free-form)
    payload = {
        "answers": [{"question": "clarification", "answer": "I prefer remote roles in Europe"}]
    }
    
    async with client.stream(
        "POST",
        f"/api/chat/{conversation_id}/answer-questions",
        json=payload,
        headers={"Authorization": "Bearer test"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        # Check that we receive at least one event
        event_received = False
        async for line in response.aiter_lines():
            if line.startswith("event:") or line.startswith("data:"):
                event_received = True
                break
        
        assert event_received


