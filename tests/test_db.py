from dataclasses import asdict

from sqlalchemy import select

from fastapi_zero.models import User


def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as mock_time:
        user = User(
            username='testuser',
            email='user@test.com',
            password_hash='hashedpassword123',
        )
        session.add(user)
        session.commit()
        user = session.scalar(select(User).where(User.username == 'testuser'))
        assert asdict(user) == {
            'id': 1,
            'username': 'testuser',
            'email': 'user@test.com',
            'password_hash': 'hashedpassword123',
            'created_at': mock_time,
            'updated_at': mock_time,
        }
