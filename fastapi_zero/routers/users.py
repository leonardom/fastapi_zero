from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import (
    CreateUserRequest,
    ListUserResponse,
    Pagination,
    UpdateUserRequest,
    UserResponse,
)
from fastapi_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])
T_Session = Annotated[Session, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Pagination = Annotated[Pagination, Query()]


@router.post(
    '/',
    status_code=HTTPStatus.CREATED,
    response_model=UserResponse,
)
def create(input: CreateUserRequest, session: T_Session):
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
    hashed_password = get_password_hash(input.password)
    user = User(
        username=input.username,
        email=input.email,
        password_hash=hashed_password,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get(
    '/',
    status_code=HTTPStatus.OK,
    response_model=ListUserResponse,
)
def find_all(session: T_Session, pagination: T_Pagination):
    users = session.scalars(
        select(User).offset(pagination.skip).limit(pagination.limit)
    ).all()
    return {'users': users}


@router.get(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
def find(user_id: int, session: T_Session):
    user = session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail='User not found')

    return user


@router.put(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
def update(
    user_id: int,
    input: UpdateUserRequest,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not authorized to update this user',
        )

    try:
        current_user.username = input.username
        current_user.email = input.email
        if input.password:
            hashed_password = get_password_hash(input.password)
            current_user.password_hash = hashed_password
        session.commit()
        session.refresh(current_user)
        return current_user
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or email already exists',
        )


@router.delete('/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not authorized to delete this user',
        )

    session.delete(current_user)
    session.commit()
