from http import HTTPStatus

from fastapi_zero.schemas import UserResponse
from fastapi_zero.security import create_access_token


def test_create_user_should_return_201(client):
    input = {
        'username': 'testuser',
        'email': 'user@test.com',
        'password': 'securepassword',
    }
    response = client.post('/users/', json=input)
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'testuser',
        'email': 'user@test.com',
    }


def test_create_user_username_conflict_should_return_409(client, user):
    input = {
        'username': 'testuser',
        'email': 'newuser@test.com',
        'password': 'securepassword',
    }
    response = client.post('/users/', json=input)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username already registered'}


def test_create_user_email_conflict_should_return_409(client, user):
    input = {
        'username': 'newtestuser',
        'email': 'user@test.com',
        'password': 'securepassword',
    }
    response = client.post('/users/', json=input)
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Email already registered'}


def test_find_user_should_return_200(client, user):
    expected_user = UserResponse.model_validate(user).model_dump()
    response = client.get(f'/users/{user.id}')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == expected_user


def test_find_nonexistent_user_should_return_404(client):
    response = client.get('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_list_users_should_return_200(client, user):
    expected_user = UserResponse.model_validate(user).model_dump()
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [expected_user]}


def test_update_user_should_return_200(client, user, token):
    input = {
        'username': 'updated-testuser',
        'email': 'user@test.com',
        'password': 'newsecurepassword',
    }
    response = client.put(
        f'/users/{user.id}',
        json=input,
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': user.id,
        'username': 'updated-testuser',
        'email': 'user@test.com',
    }


def test_update_integrity_error_user_should_return_409(client, user, token):
    client.post(
        '/users/',
        json={
            'username': 'johndoe',
            'email': 'johndoe@test.com',
            'password': 'securepassword',
        },
    )
    input = {
        'username': 'johndoe',
        'email': 'user@test.com',
    }
    response = client.put(
        '/users/1',
        json=input,
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {'detail': 'Username or email already exists'}


def test_update_user_different_user_id_should_return_403(client, user, token):
    input = {
        'username': 'johndoe',
        'email': 'user@test.com',
    }
    response = client.put(
        '/users/99',
        json=input,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not authorized to update this user'}


def test_delete_user_should_return_204(client, user, token):
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_user_missing_token_email_should_return_401(client, user):
    token = create_access_token({'username': 'testuser'})
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_user_does_not_exist_should_return_401(client, user):
    token = create_access_token({'sub': 'tester@test.com'})
    response = client.delete(
        f'/users/{user.id}', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_delete_user_different_user_id_should_return_403(client, user, token):
    response = client.delete(
        '/users/99', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not authorized to delete this user'}
