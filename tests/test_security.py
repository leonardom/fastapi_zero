from http import HTTPStatus

from jwt import decode

from fastapi_zero.security import create_access_token
from fastapi_zero.settings import Settings


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)
    settings = Settings()
    decoded = decode(
        token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
    )

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token_should_return_401(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer token-invalido'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
