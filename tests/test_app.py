import importlib
import os
import sys
from pathlib import Path

import pytest


def load_test_app(tmp_path, monkeypatch):
    monkeypatch.setenv("DB_PATH", str(tmp_path / "tasks.db"))
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    import src.app as app_module

    importlib.reload(app_module)
    return app_module.app.test_client()


def test_index_returns_api_info(tmp_path, monkeypatch):
    client = load_test_app(tmp_path, monkeypatch)
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["name"] == "To-Do API"
    assert "/tasks" in response.json["endpoints"]


def test_create_and_get_task(tmp_path, monkeypatch):
    client = load_test_app(tmp_path, monkeypatch)
    create_response = client.post("/tasks", json={"title": "Test", "description": "Prueba"})

    assert create_response.status_code == 201
    task = create_response.json
    assert task["title"] == "Test"

    get_response = client.get(f"/tasks/{task['id']}")
    assert get_response.status_code == 200
    assert get_response.json["title"] == "Test"


def test_update_task_status(tmp_path, monkeypatch):
    client = load_test_app(tmp_path, monkeypatch)
    create_response = client.post("/tasks", json={"title": "Actualizar tarea"})
    task_id = create_response.json["id"]

    update_response = client.put(f"/tasks/{task_id}", json={"completed": 1})
    assert update_response.status_code == 200
    assert update_response.json["completed"] == 1


def test_delete_task_and_verify_missing(tmp_path, monkeypatch):
    client = load_test_app(tmp_path, monkeypatch)
    create_response = client.post("/tasks", json={"title": "Eliminar tarea"})
    task_id = create_response.json["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json["message"] == "Tarea eliminada"

    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_health_and_metrics_endpoints(tmp_path, monkeypatch):
    client = load_test_app(tmp_path, monkeypatch)
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.json["status"] == "ok"

    metrics_response = client.get("/metrics")
    assert metrics_response.status_code == 200
    assert b"todo_api_requests_total" in metrics_response.data
