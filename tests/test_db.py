from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import User


@pytest.mark.asyncio
async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as mock_time:
        user = User(
            username='testuser',
            email='user@test.com',
            password_hash='hashedpassword123',
        )
        session.add(user)
        await session.commit()
        user = await session.scalar(
            select(User).where(User.username == 'testuser')
        )
        assert asdict(user) == {
            'id': 1,
            'username': 'testuser',
            'email': 'user@test.com',
            'password_hash': 'hashedpassword123',
            'created_at': mock_time,
            'updated_at': mock_time,
        }
