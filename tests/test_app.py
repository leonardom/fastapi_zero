from http import HTTPStatus


def test_hello_should_return_200(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


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


def test_list_users_should_return_200(client):
    response = client.get('/users/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [
        {'id': 1, 'username': 'testuser', 'email': 'user@test.com'}
    ]


def test_update_user_should_return_200(client):
    input = {
        'username': 'updated-testuser',
        'email': 'user@test.com',
        'password': 'newsecurepassword',
    }
    response = client.put('/users/1', json=input)
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'updated-testuser',
        'email': 'user@test.com',
    }


def test_update_nonexistent_user_should_return_404(client):
    input = {
        'username': 'updated-testuser',
        'email': 'user@test.com',
    }
    response = client.put('/users/999', json=input)
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_user_should_return_204(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_nonexistent_user_should_return_404(client):
    response = client.delete('/users/999')
    assert response.status_code == HTTPStatus.NOT_FOUND
