from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from fastapi_zero.models import TodoState


class Pagination(BaseModel):
    skip: int = Field(ge=0, default=0)
    limit: int = Field(gt=0, default=10)


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(from_attributes=True)


class ListUserResponse(BaseModel):
    users: list[UserResponse]


class UpdateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class CreateTodoRequest(BaseModel):
    title: str
    description: Optional[str] = None
    state: TodoState = TodoState.NEW


class UpdateTodoRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    state: Optional[TodoState] = None


class TodoResponse(CreateTodoRequest):
    id: int


class ListTodoResponse(BaseModel):
    todos: list[TodoResponse]


class TodoFilter(Pagination):
    title: str | None = Field(None, min_length=3, max_length=20)
    description: str | None = Field(None, min_length=3, max_length=20)
    state: TodoState | None = None
