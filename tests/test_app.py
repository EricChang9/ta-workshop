import pytest

from app import DEFAULT_PRIORITY, app, tasks


@pytest.fixture
def client():
    """Provide a Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def reset_tasks():
    """Reset the in-memory task list before each test."""
    tasks.clear()
    tasks.extend([
        {"id": 1, "title": "Project-1 Report"},
        {"id": 2, "title": "Project-2 MMFs"}
    ])


def test_index(client):
    """Render the task tracker page."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Task Tracker" in response.data


def test_get_tasks(client):
    """Return all tasks with normalized default priorities."""
    response = client.get('/api/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert all(task['priority'] == DEFAULT_PRIORITY for task in data)


def test_add_task_success(client):
    """Create a task with the requested valid priority."""
    response = client.post(
        '/api/tasks',
        json={"title": "Test new task", "priority": "high"}
    )
    assert response.status_code == 201
    assert response.get_json() == {
        "id": 3,
        "title": "Test new task",
        "priority": "high"
    }

    get_response = client.get('/api/tasks')
    assert len(get_response.get_json()) == 3


def test_add_task_defaults_to_medium_priority(client):
    """Assign medium priority when a new task omits priority."""
    response = client.post('/api/tasks', json={"title": "Default task"})

    assert response.status_code == 201
    assert response.get_json()['priority'] == DEFAULT_PRIORITY


def test_add_task_accepts_all_valid_priorities(client):
    """Accept low, medium, and high priorities on task creation."""
    for priority in ('low', 'medium', 'high'):
        response = client.post(
            '/api/tasks',
            json={"title": f"{priority} task", "priority": priority}
        )
        assert response.status_code == 201
        assert response.get_json()['priority'] == priority


def test_add_task_rejects_invalid_priority(client):
    """Reject priorities outside the supported set."""
    response = client.post(
        '/api/tasks',
        json={"title": "Invalid task", "priority": "urgent"}
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid priority"


def test_add_task_missing_title(client):
    """Reject task creation when the title is missing."""
    response = client.post('/api/tasks', json={"wrong_key": "value"})
    assert response.status_code == 400
    assert "error" in response.get_json()

    response2 = client.post('/api/tasks', json={})
    assert response2.status_code == 400


def test_update_task_priority(client):
    """Update an existing task to a valid priority."""
    response = client.patch('/api/tasks/1', json={"priority": "low"})

    assert response.status_code == 200
    assert response.get_json()['id'] == 1
    assert response.get_json()['priority'] == "low"

    tasks_response = client.get('/api/tasks')
    updated_task = tasks_response.get_json()[0]
    assert updated_task['priority'] == "low"


def test_update_task_rejects_invalid_priority(client):
    """Reject invalid priorities when updating a task."""
    response = client.patch(
        '/api/tasks/1',
        json={"priority": "urgent"}
    )

    assert response.status_code == 400
    assert response.get_json()['error'] == "Invalid priority"


def test_update_missing_task(client):
    """Return not found when updating a missing task."""
    response = client.patch(
        '/api/tasks/999',
        json={"priority": "high"}
    )

    assert response.status_code == 404
    assert response.get_json()['error'] == "Task not found"


def test_legacy_task_priority_is_normalized(client):
    """Normalize legacy tasks without a priority to medium."""
    response = client.get('/api/tasks')

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['priority'] == DEFAULT_PRIORITY
    assert data[1]['priority'] == DEFAULT_PRIORITY
    assert tasks[0]['priority'] == DEFAULT_PRIORITY
    assert tasks[1]['priority'] == DEFAULT_PRIORITY


def test_delete_task(client):
    """Delete an existing task."""
    response = client.delete('/api/tasks/1')
    assert response.status_code == 200

    get_response = client.get('/api/tasks')
    data = get_response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == 2
