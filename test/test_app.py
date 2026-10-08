import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Welcome to ACEest Fitness & Gym"


def test_get_members(client):
    response = client.get("/members")

    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_existing_member(client):
    response = client.get("/members/1")

    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_non_existing_member(client):
    response = client.get("/members/999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Member not found"


def test_add_member(client):
    response = client.post(
        "/members",
        json={
            "name": "Alex",
            "age": 28,
            "membership": "Premium"
        }
    )

    assert response.status_code == 201
    assert response.get_json()["name"] == "Alex"


def test_add_member_without_required_data(client):
    response = client.post(
        "/members",
        json={
            "name": "Alex"
        }
    )

    assert response.status_code == 400


def test_delete_existing_member(client):
    response = client.delete("/members/2")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Member deleted successfully"


def test_delete_non_existing_member(client):
    response = client.delete("/members/999")

    assert response.status_code == 404


def test_health_check(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"