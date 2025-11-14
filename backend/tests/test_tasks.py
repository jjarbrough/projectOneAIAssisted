from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, email: str) -> dict[str, str]:
    response = client.post(
        "/api/register",
        json={
            "email": email,
            "password": "secret-password",
            "full_name": "Task User",
        },
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_requires_authentication_for_task_list_creation(client: TestClient):
    response = client.post("/api/lists", json={"name": "Unauth List"})
    assert response.status_code == 401


def test_task_lifecycle(client: TestClient):
    headers = _register_and_login(client, "tasker@example.com")

    create_list_response = client.post(
        "/api/lists",
        json={"name": "Math Homework"},
        headers=headers,
    )
    assert create_list_response.status_code == 201
    task_list = create_list_response.json()
    list_id = task_list["id"]

    get_lists_response = client.get("/api/lists", headers=headers)
    assert get_lists_response.status_code == 200
    lists = get_lists_response.json()
    assert len(lists) == 1
    assert lists[0]["name"] == "Math Homework"

    create_task_response = client.post(
        f"/api/lists/{list_id}/tasks",
        json={
            "title": "Finish worksheet",
            "description": "Complete problems 1-10",
            "due_date": "2025-11-20",
            "status": "pending",
            "priority": "high",
            "tags": ["algebra", "urgent"],
        },
        headers=headers,
    )
    assert create_task_response.status_code == 201
    task = create_task_response.json()
    task_id = task["id"]
    assert task["status"] == "pending"
    assert task["priority"] == "high"
    assert task["tags"] == ["algebra", "urgent"]

    tasks_response = client.get(f"/api/lists/{list_id}/tasks", headers=headers)
    assert tasks_response.status_code == 200
    tasks = tasks_response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Finish worksheet"
    assert tasks[0]["priority"] == "high"
    assert tasks[0]["tags"] == ["algebra", "urgent"]

    update_task_response = client.put(
        f"/api/tasks/{task_id}",
        json={
            "title": "Finish worksheet",
            "description": "Complete problems 1-10 and review answers",
            "due_date": "2025-11-21",
            "status": "completed",
            "priority": "medium",
            "tags": ["algebra", "reviewed"],
        },
        headers=headers,
    )
    assert update_task_response.status_code == 200
    updated_task = update_task_response.json()
    assert updated_task["status"] == "completed"
    assert updated_task["description"].endswith("review answers")
    assert updated_task["priority"] == "medium"
    assert updated_task["tags"] == ["algebra", "reviewed"]

    delete_response = client.delete(f"/api/tasks/{task_id}", headers=headers)
    assert delete_response.status_code == 204

    empty_tasks_response = client.get(f"/api/lists/{list_id}/tasks", headers=headers)
    assert empty_tasks_response.status_code == 200
    assert empty_tasks_response.json() == []


def test_reorder_tasks(client: TestClient):
    headers = _register_and_login(client, "organizer@example.com")

    list_response = client.post("/api/lists", json={"name": "Project"}, headers=headers)
    assert list_response.status_code == 201
    list_id = list_response.json()["id"]

    task_payloads = [
        {
            "title": "First task",
            "description": "",
            "status": "pending",
            "priority": "low",
            "tags": [],
        },
        {
            "title": "Second task",
            "description": "",
            "status": "pending",
            "priority": "medium",
            "tags": ["planning"],
        },
        {
            "title": "Third task",
            "description": "",
            "status": "pending",
            "priority": "high",
            "tags": ["planning", "urgent"],
        },
    ]

    created_tasks = []
    for payload in task_payloads:
        response = client.post(
            f"/api/lists/{list_id}/tasks",
            json=payload,
            headers=headers,
        )
        assert response.status_code == 201
        created_tasks.append(response.json())

    original_order = [task["id"] for task in created_tasks]
    reversed_order = list(reversed(original_order))

    reorder_response = client.put(
        f"/api/lists/{list_id}/tasks/reorder",
        json={"task_ids": reversed_order},
        headers=headers,
    )
    assert reorder_response.status_code == 200
    reordered_tasks = reorder_response.json()
    assert [task["id"] for task in reordered_tasks] == reversed_order

    fetch_response = client.get(f"/api/lists/{list_id}/tasks", headers=headers)
    assert fetch_response.status_code == 200
    fetched_tasks = fetch_response.json()
    assert [task["id"] for task in fetched_tasks] == reversed_order

