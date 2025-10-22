from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class MessageResponse(BaseModel):
    message: str


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
