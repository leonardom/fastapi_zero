from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.database import get_session
from fastapi_zero.models import User
from fastapi_zero.schemas import TokenResponse
from fastapi_zero.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])
T_OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
T_Session = Annotated[AsyncSession, Depends(get_session)]


@router.post('/login', status_code=HTTPStatus.OK, response_model=TokenResponse)
async def login(
    input: T_OAuth2Form,
    session: T_Session,
):
    user = await session.scalar(
        select(User).where(User.username == input.username)
    )

    if not user or not verify_password(input.password, user.password_hash):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Invalid username or password',
        )

    access_token = create_access_token(data={'sub': user.email})

    return TokenResponse(access_token=access_token, token_type='bearer')
