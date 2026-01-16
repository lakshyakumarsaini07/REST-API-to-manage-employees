import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, engine
from app import models

@pytest.fixture(scope="module")
def db():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    models.Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_create_employee():
    # First, get token
    response = client.post("/token", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    employee_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "department": "Engineering",
        "role": "Developer"
    }
    response = client.post("/api/employees/", json=employee_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data
    assert "date_joined" in data

def test_create_employee_duplicate_email():
    response = client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    employee_data = {
        "name": "Jane Doe",
        "email": "john@example.com",  # duplicate
        "department": "HR",
        "role": "Manager"
    }
    response = client.post("/api/employees/", json=employee_data, headers=headers)
    assert response.status_code == 400
    assert "Email already exists" in response.json()["detail"]

def test_create_employee_empty_name():
    response = client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    employee_data = {
        "name": "",
        "email": "jane@example.com",
        "department": "HR",
        "role": "Manager"
    }
    response = client.post("/api/employees/", json=employee_data, headers=headers)
    assert response.status_code == 400
    assert "Name cannot be empty" in response.json()["detail"]

def test_read_employees():
    response = client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/employees/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_read_employee():
    response = client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Assuming employee with id 1 exists from previous test
    response = client.get("/api/employees/1/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1

def test_read_employee_not_found():
    response = client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/employees/999/", headers=headers)
    assert response.status_code == 404

def test_update_employee():
    response = client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {
        "name": "John Smith"
    }
    response = client.put("/api/employees/1/", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Smith"

def test_delete_employee():
    response = client.post("/token", data={"username": "admin", "password": "password"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.delete("/api/employees/1/", headers=headers)
    assert response.status_code == 204

    # Check if deleted
    response = client.get("/api/employees/1/", headers=headers)
    assert response.status_code == 404

def test_unauthorized_access():
    response = client.get("/api/employees/")
    assert response.status_code == 401