from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    CreateUserRequest,
    ListUserResponse,
    MessageResponse,
    UpdateUserRequest,
    UserResponse,
)

app = FastAPI()


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageResponse)
def hello():
    return {'message': 'Hello, World!'}


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserResponse,
)
def create_user(
    input: CreateUserRequest, session: Session = Depends(get_session)
):
    user = session.scalar(
        select(User).where(
            (User.email == input.email) | (User.username == input.username)
        )
    )
    if user:
        if user.username == input.username:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username already registered',
            )
        elif user.email == input.email:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Email already registered',
            )

    user = User(
        username=input.username,
        email=input.email,
        password_hash=input.password,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@app.get(
    '/users/',
    status_code=HTTPStatus.OK,
    response_model=ListUserResponse,
)
def list_users(
    skip: int = 0, limit: int = 10, session: Session = Depends(get_session)
):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
def find_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return user


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
def update_user(
    user_id: int,
    input: UpdateUserRequest,
    session: Session = Depends(get_session),
):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    try:
        user.username = input.username
        user.email = input.email
        if input.password:
            user.password_hash = input.password
        session.commit()
        session.refresh(user)
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    session.delete(user)
    session.commit()
