from contextlib import contextmanager
from datetime import datetime

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import User, table_registry
from fastapi_zero.security import get_password_hash
from fastapi_zero.settings import Settings


@pytest.fixture
def client(session):
    """Fixture to provide a TestClient for FastAPI app."""

    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    """Fixture to provide a database session for testing."""
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with AsyncSession(engine) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)

    await engine.dispose()


@contextmanager
def _mock_db_time(*, model, time=datetime.now()):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    """Fixture to mock database time for models."""
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    """Fixture to create user in the database."""
    user = User(
        username='testuser',
        email='user@test.com',
        password_hash=get_password_hash('securepassword'),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user


@pytest.fixture
def token(client, user):
    """Fixture to provide a valid JWT token for authentication."""
    response = client.post(
        '/auth/login',
        data={
            'username': user.username,
            'password': 'securepassword',
        },
    )
    return response.json()['access_token']


@pytest.fixture
def settings():
    return Settings()
