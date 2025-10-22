from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fastapi_zero.schemas import (
    CreateUserRequest,
    MessageResponse,
    UpdateUserRequest,
    User,
    UserResponse,
)

app = FastAPI()

in_memory_users_db = []


@app.get('/', status_code=HTTPStatus.OK, response_model=MessageResponse)
def hello():
    return {'message': 'Hello, World!'}


@app.post(
    '/users/',
    status_code=HTTPStatus.CREATED,
    response_model=UserResponse,
)
def create_user(user: CreateUserRequest):
    new_user = User(**user.model_dump(), id=len(in_memory_users_db) + 1)
    in_memory_users_db.append(new_user)
    return new_user


@app.get(
    '/users/',
    status_code=HTTPStatus.OK,
    response_model=list[UserResponse],
)
def list_users():
    return in_memory_users_db


@app.put(
    '/users/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=UserResponse,
)
def update_user(user_id: int, user: UpdateUserRequest):
    for idx, existing_user in enumerate(in_memory_users_db):
        if existing_user.id == user_id:
            updated_user = existing_user.model_copy(
                update=user.model_dump(exclude_unset=True)
            )
            in_memory_users_db[idx] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail='User not found')


@app.delete('/users/{user_id}', status_code=HTTPStatus.NO_CONTENT)
def delete_user(user_id: int):
    for idx, existing_user in enumerate(in_memory_users_db):
        if existing_user.id == user_id:
            del in_memory_users_db[idx]
            return
    raise HTTPException(status_code=404, detail='User not found')
