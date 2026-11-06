from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_order() -> None:
    response = TestClient(app).get("/orders/123")
    assert response.status_code == 200
    assert response.json()["id"] == "123"
