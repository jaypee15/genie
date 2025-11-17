import pytest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.agents.coordinator import CoordinatorAgent


@pytest.mark.asyncio
async def test_search_internal_first_skips_scrape(monkeypatch):
    coord = CoordinatorAgent()

    # Mock _count_internal_opportunities to return high number
    monkeypatch.setattr(coord, "_count_internal_opportunities", AsyncMock(return_value=999))
    # Mock executor to ensure it's not called
    coord.executor = SimpleNamespace(execute_search=AsyncMock())

    # Mock Ably publish to be no-op
    from app.services import ably_service
    monkeypatch.setattr(ably_service.ably_service.client.channels, "get", lambda k: SimpleNamespace(publish=AsyncMock()))

    # Use a dummy db (not used due to mocks)
    db = None  # type: ignore
    goal_data = {"goal_type": "job", "original_description": "test"}
    results = await coord._search_with_updates(db, goal_data, conversation_id="conv-1")

    # Should not scrape, results remain empty list
    assert results == []
    coord.executor.execute_search.assert_not_called()


