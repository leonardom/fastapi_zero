from http import HTTPStatus


def test_login_should_return_200(client, user):
    input = {
        'username': 'testuser',
        'password': 'securepassword',
    }
    response = client.post(
        '/auth/login',
        data=input,
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert token['token_type'] == 'bearer'


def test_login_invalid_credentials_should_return_401(client, user):
    input = {
        'username': 'testuser',
        'password': 'wrongpassword',
    }
    response = client.post(
        '/auth/login',
        data=input,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password'}
