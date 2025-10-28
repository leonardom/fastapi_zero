from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import Todo, User


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
            'todos': [],
        }


@pytest.mark.asyncio
async def test_create_todo(session, user, mock_db_time):
    with mock_db_time(model=Todo) as mock_time:
        todo = Todo(
            title='Test Todo',
            description='This is a test todo item.',
            state='NEW',
            user_id=user.id,
        )
        session.add(todo)
        await session.commit()

        todo = await session.scalar(select(Todo))
        assert asdict(todo) == {
            'id': 1,
            'title': 'Test Todo',
            'description': 'This is a test todo item.',
            'state': 'NEW',
            'user_id': user.id,
            'created_at': mock_time,
            'updated_at': mock_time,
        }


@pytest.mark.asyncio
async def test_user_todo_relationship(session, user):
    todo = Todo(
        title='Test Todo',
        description='This is a test todo item.',
        state='NEW',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(user)

    user = await session.scalar(select(User).where(User.id == user.id))

    assert user.todos == [todo]
