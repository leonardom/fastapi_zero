from typing import Optional

from pydantic import BaseModel, EmailStr


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


class UpdateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: Optional[str] = None


class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
