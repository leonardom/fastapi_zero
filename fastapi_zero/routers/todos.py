from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import Todo, User
from fastapi_zero.schemas import (
    CreateTodoRequest,
    ListTodoResponse,
    TodoFilter,
    TodoResponse,
    UpdateTodoRequest,
)
from fastapi_zero.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_Filter = Annotated[TodoFilter, Query()]


@router.post('/', response_model=TodoResponse, status_code=201)
async def create_todo(
    todo: CreateTodoRequest,
    user: T_CurrentUser,
    session: T_Session,
):
    todo = Todo(
        title=todo.title,
        description=todo.description,
        state=todo.state,
        user_id=user.id,
    )
    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return todo


@router.get('/', response_model=ListTodoResponse)
async def find_all(user: T_CurrentUser, session: T_Session, filter: T_Filter):
    query = select(Todo).where(Todo.user_id == user.id)

    if filter.title:
        query = query.filter(Todo.title.contains(filter.title))

    if filter.description:
        query = query.filter(Todo.description.contains(filter.description))

    if filter.state:
        query = query.filter(Todo.state == filter.state)

    todos = await session.scalars(
        query.offset(filter.skip).limit(filter.limit)
    )
    return {'todos': todos.all()}


@router.get('/{todo_id}', response_model=TodoResponse)
async def find(
    todo_id: int,
    session: T_Session,
    user: T_CurrentUser,
):
    todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not authorized to access this todo',
        )

    return todo


@router.put('/{todo_id}', response_model=TodoResponse)
async def update(
    todo_id: int,
    session: T_Session,
    user: T_CurrentUser,
    input: UpdateTodoRequest,
):
    todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not authorized to update this todo',
        )

    todo.update_fields(input)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return todo


@router.delete('/{todo_id}', status_code=HTTPStatus.NO_CONTENT)
async def delete(
    todo_id: int,
    session: T_Session,
    user: T_CurrentUser,
):
    todo = await session.scalar(select(Todo).where(Todo.id == todo_id))

    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Todo not found'
        )

    if todo.user_id != user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Not authorized to delete this todo',
        )

    await session.delete(todo)
    await session.commit()
