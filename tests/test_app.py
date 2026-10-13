import pytest
from app import create_app

@pytest.fixture()
def app(tmp_path):
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "DATABASE": str(tmp_path / "test.sqlite"),
    })
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()

def add_member(client, name="Taylor Reed", email="taylor@example.com"):
    return client.post("/members/new", data={
        "name": name, "email": email, "phone": "9876543210",
        "goal": "Build Strength", "program": "Strength"
    }, follow_redirects=True)

def test_homepage_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Make every rep" in response.data

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_member_can_be_created_and_listed(client):
    response = add_member(client)
    assert response.status_code == 200
    assert b"Taylor Reed" in response.data
    assert b"taylor@example.com" in client.get("/members").data

def test_member_requires_name_and_email(client):
    response = client.post("/members/new", data={"name": "", "email": ""})
    assert response.status_code == 200
    assert b"Name and email are required" in response.data

def test_duplicate_member_email_is_rejected(client):
    add_member(client)
    response = add_member(client, "Another Person", "taylor@example.com")
    assert b"already registered" in response.data

def test_member_details_and_edit(client):
    add_member(client)
    response = client.get("/members/1")
    assert response.status_code == 200
    response = client.post("/members/1/edit", data={
        "name": "Taylor Updated", "email": "updated@example.com",
        "phone": "", "goal": "Improve Endurance", "program": "Cardio"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Taylor Updated" in response.data

def test_unknown_member_returns_404(client):
    assert client.get("/members/999").status_code == 404

def test_workout_can_be_logged(client):
    add_member(client)
    response = client.post("/workouts", data={
        "member_id": "1", "workout": "Morning run", "duration": "30",
        "calories": "220", "workout_date": "2026-01-20", "notes": "Easy pace"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Morning run" in response.data
    assert b"220" in response.data

def test_calculator_returns_estimate(client):
    response = client.post("/calculator", data={
        "age": "28", "sex": "female", "weight": "65", "height": "165",
        "activity": "1.55"
    })
    assert response.status_code == 200
    assert b"ESTIMATED DAILY MAINTENANCE" in response.data

def test_calculator_rejects_invalid_values(client):
    response = client.post("/calculator", data={
        "age": "5", "sex": "female", "weight": "65", "height": "165",
        "activity": "1.2"
    })
    assert response.status_code == 200
    assert b"Enter valid values" in response.data

def test_member_delete_removes_profile(client):
    add_member(client)
    response = client.post("/members/1/delete", follow_redirects=True)
    assert response.status_code == 200
    assert b"Taylor Reed" not in response.data
