from http import HTTPStatus

from freezegun import freeze_time


def test_login_should_return_200(client, user):
    input = {
        'username': user.username,
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
        'username': user.username,
        'password': 'wrongpassword',
    }
    response = client.post(
        '/auth/login',
        data=input,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password'}


def test_token_inexistent_user_should_return_401(client):
    input = {
        'username': 'no_user@no_domain.com',
        'password': 'wrongpassword',
    }
    response = client.post(
        '/auth/login',
        data=input,
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Invalid username or password'}


def test_token_expired_after_time_should_return_401(client, user):
    with freeze_time('2025-10-23 12:00:00'):
        response = client.post(
            '/auth/login',
            data={'username': user.email, 'password': 'securepassword'},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2025-10-23 12:31:00'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'wrongwrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token_should_return_200(client, user, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )
    data = response.json()

    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh_should_return_401(client, user):
    with freeze_time('2023-07-14 12:00:00'):
        response = client.post(
            '/auth/login',
            data={'username': user.email, 'password': 'securepassword'},
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()['access_token']

    with freeze_time('2023-07-14 12:31:00'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
