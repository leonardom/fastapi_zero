from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
