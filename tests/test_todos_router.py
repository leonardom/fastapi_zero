from http import HTTPStatus

import factory.fuzzy
import pytest

from fastapi_zero.models import Todo, TodoState


class TodoFactory(factory.Factory):
    class Meta:
        model = Todo

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TodoState)
    user_id = 1


@pytest.mark.asyncio
async def test_create_todo_should_return_201(client, token):
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'New Todo',
            'description': 'This is a new todo item',
            'state': 'NEW',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'title': 'New Todo',
        'description': 'This is a new todo item',
        'state': 'NEW',
    }


@pytest.mark.asyncio
async def test_create_todo_with_invalid_status_should_return_422(
    client, token
):
    response = client.post(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'New Todo',
            'description': 'This is a new todo item',
            'state': 'INVALID_STATE',
        },
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_list_todos_should_return_5_todos(session, client, user, token):
    expected_todos = 5
    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_title_should_return_5_records(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(5, user_id=user.id, title='Test todo 1')
    )
    await session.commit()

    response = client.get(
        '/todos?title=Test todo 1',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_description_should_return_5_records(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5, user_id=user.id, description='This is a test'
        )
    )
    await session.commit()

    response = client.get(
        '/todos?description=test',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_state_should_return_3_records(
    session, user, client, token
):
    expected_todos = 3
    session.add_all(
        TodoFactory.create_batch(2, user_id=user.id, state=TodoState.DONE)
    )
    session.add_all(
        TodoFactory.create_batch(3, user_id=user.id, state=TodoState.PENDING)
    )
    await session.commit()

    response = client.get(
        '/todos?state=PENDING',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_list_todos_filter_combined_should_return_5_todos(
    session, user, client, token
):
    expected_todos = 5
    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.DONE,
        )
    )
    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.PENDING,
        )
    )
    await session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=DONE',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


@pytest.mark.asyncio
async def test_find_todo_should_return_200(client, session, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.get(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['id'] == todo.id
    assert response.json()['title'] == todo.title
    assert response.json()['description'] == todo.description
    assert response.json()['state'] == todo.state.name


@pytest.mark.asyncio
async def test_find_todo_not_found_should_return_404(client, token):
    response = client.get(
        '/todos/999',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


@pytest.mark.asyncio
async def test_find_todo_not_owned_should_return_403(
    client, session, other_user, token
):
    todo = TodoFactory(user_id=other_user.id)
    session.add(todo)
    await session.commit()

    response = client.get(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not authorized to access this todo'}


@pytest.mark.asyncio
async def test_update_todo_should_return_200(client, session, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    input = {
        'title': 'Updated Todo',
    }
    response = client.put(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json=input,
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'Updated Todo'


@pytest.mark.asyncio
async def test_update_todo_not_found_should_return_404(client, token):
    input = {
        'title': 'Updated Todo',
        'description': 'This is an updated todo item',
        'state': 'PENDING',
    }
    response = client.put(
        '/todos/999',
        headers={'Authorization': f'Bearer {token}'},
        json=input,
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


@pytest.mark.asyncio
async def test_update_todo_not_owned_should_return_403(
    client, session, other_user, token
):
    todo = TodoFactory(user_id=other_user.id)
    session.add(todo)
    await session.commit()

    input = {
        'title': 'Updated Todo',
        'description': 'This is an updated todo item',
        'state': 'PENDING',
    }
    response = client.put(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json=input,
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not authorized to update this todo'}


@pytest.mark.asyncio
async def test_update_todo_with_invalid_state_should_return_422(
    client, session, user, token
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    input = {
        'state': 'INVALID_STATE',
    }
    response = client.put(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json=input,
    )
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_todo_should_return_204(client, session, user, token):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_delete_todo_not_found_should_return_404(client, token):
    response = client.delete(
        '/todos/999',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}


@pytest.mark.asyncio
async def test_delete_todo_not_owned_should_return_403(
    client, session, other_user, token
):
    todo = TodoFactory(user_id=other_user.id)
    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert response.json() == {'detail': 'Not authorized to delete this todo'}
