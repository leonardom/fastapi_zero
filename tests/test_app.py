from http import HTTPStatus

from fastapi.testclient import TestClient

from fastapi_zero.app import app


def test_hello_should_return_200():
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}
