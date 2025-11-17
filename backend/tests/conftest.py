import os
import asyncio
import uuid
import json
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def _ensure_test_db_url():
    test_db = os.environ.get("TEST_DATABASE_URL")
    if not test_db:
        pytest.skip("TEST_DATABASE_URL not set; skipping backend DB tests")
    # Point the app to the test DB
    os.environ["DATABASE_URL"] = test_db
    # Provide minimal other envs to satisfy settings
    os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
    os.environ.setdefault("ALLOWED_ORIGINS", "*")


@pytest.fixture(scope="session")
def app() -> FastAPI:
    # Import after env set so settings pick it up
    from app.main import app as fastapi_app
    return fastapi_app


@pytest.fixture(scope="session")
async def _init_db(app: FastAPI):
    # Trigger lifespan init_db once for the session using a lightweight client
    async with AsyncClient(app=app, base_url="http://test") as _:
        pass


@pytest.fixture
async def client(app: FastAPI, _init_db) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def override_auth_dependencies(app: FastAPI, monkeypatch: pytest.MonkeyPatch):
    # Force authenticated user and stable email to avoid Supabase in tests
    from app.auth import get_current_user, get_user_email_from_token
    test_user_id = uuid.uuid4()

    async def _fake_current_user():
        return test_user_id

    def _fake_email_from_token(_token: str) -> str:
        return "test@example.com"

    app.dependency_overrides[get_current_user] = _fake_current_user
    monkeypatch.setattr("app.api.chat.get_user_email_from_token", _fake_email_from_token, raising=True)
    yield
    app.dependency_overrides.pop(get_current_user, None)


