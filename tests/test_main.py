import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app, get_db
from app.database import Base
from app import models, auth

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    
    # Create a test user
    db = TestingSessionLocal()
    try:
        test_user = models.User(
            username="testuser",
            email="test@example.com",
            hashed_password=auth.get_password_hash("Test123!"),
            full_name="Test User",
            is_active=True,
            is_superuser=False
        )
        db.add(test_user)
        
        # Create an admin user
        admin_user = models.User(
            username="admin",
            email="admin@example.com",
            hashed_password=auth.get_password_hash("Admin123!"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True
        )
        db.add(admin_user)
        db.commit()
    finally:
        db.close()
    
    yield
    
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)

def get_auth_headers(username="testuser", password="Test123!"):
    """Helper function to get authentication headers"""
    response = client.post(
        "/api/auth/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def get_admin_headers():
    """Helper function to get admin authentication headers"""
    return get_auth_headers("admin", "Admin123!")

# Health Check Tests
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# Authentication Tests
def test_register_user():
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewUser123!",
        "full_name": "New User"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data  # Password should not be returned

def test_register_duplicate_username():
    user_data = {
        "username": "testuser",  # Already exists
        "email": "another@example.com",
        "password": "Test123!",
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_register_duplicate_email():
    user_data = {
        "username": "anotheruser",
        "email": "test@example.com",  # Already exists
        "password": "Test123!",
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_register_weak_password():
    user_data = {
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "weak",  # Too weak
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error

def test_login_success():
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "Test123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data

def test_login_wrong_password():
    response = client.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

def test_login_nonexistent_user():
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent", "password": "Test123!"}
    )
    assert response.status_code == 401

def test_get_current_user():
    headers = get_auth_headers()
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

# Employee Tests
def test_create_employee():
    headers = get_auth_headers()
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
    headers = get_auth_headers()
    
    # Create first employee
    employee_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "department": "HR",
        "role": "Manager"
    }
    client.post("/api/employees/", json=employee_data, headers=headers)
    
    # Try to create with same email
    duplicate_data = {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "department": "Marketing",
        "role": "Coordinator"
    }
    response = client.post("/api/employees/", json=duplicate_data, headers=headers)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_create_employee_invalid_email():
    headers = get_auth_headers()
    employee_data = {
        "name": "Invalid Email",
        "email": "not-an-email",
        "department": "IT",
        "role": "Support"
    }
    response = client.post("/api/employees/", json=employee_data, headers=headers)
    assert response.status_code == 422  # Validation error

def test_list_employees():
    headers = get_auth_headers()
    
    # Create some employees
    for i in range(3):
        employee_data = {
            "name": f"Employee {i}",
            "email": f"employee{i}@example.com",
            "department": "Engineering",
            "role": "Developer"
        }
        client.post("/api/employees/", json=employee_data, headers=headers)
    
    response = client.get("/api/employees/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    assert "total" in data
    assert "page" in data
    assert data["total"] >= 3

def test_list_employees_with_filter():
    headers = get_auth_headers()
    
    # Create employees in different departments
    client.post("/api/employees/", json={
        "name": "HR Person",
        "email": "hr@example.com",
        "department": "HR",
        "role": "Manager"
    }, headers=headers)
    
    client.post("/api/employees/", json={
        "name": "Tech Person",
        "email": "tech@example.com",
        "department": "Engineering",
        "role": "Developer"
    }, headers=headers)
    
    # Filter by department
    response = client.get("/api/employees/?department=HR", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) >= 1
    for emp in data["employees"]:
        assert "HR" in emp["department"]

def test_list_employees_with_search():
    headers = get_auth_headers()
    
    client.post("/api/employees/", json={
        "name": "Alice Smith",
        "email": "alice@example.com",
        "department": "Sales",
        "role": "Representative"
    }, headers=headers)
    
    response = client.get("/api/employees/?search=Alice", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

def test_get_employee():
    headers = get_auth_headers()
    
    # Create employee
    create_response = client.post("/api/employees/", json={
        "name": "Get Test",
        "email": "gettest@example.com",
        "department": "Testing",
        "role": "Tester"
    }, headers=headers)
    employee_id = create_response.json()["id"]
    
    # Get employee
    response = client.get(f"/api/employees/{employee_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == employee_id
    assert data["name"] == "Get Test"

def test_get_employee_not_found():
    headers = get_auth_headers()
    response = client.get("/api/employees/99999", headers=headers)
    assert response.status_code == 404

def test_update_employee():
    headers = get_auth_headers()
    
    # Create employee
    create_response = client.post("/api/employees/", json={
        "name": "Update Test",
        "email": "updatetest@example.com",
        "department": "Old Dept",
        "role": "Old Role"
    }, headers=headers)
    employee_id = create_response.json()["id"]
    
    # Update employee
    update_data = {
        "name": "Updated Name",
        "department": "New Dept"
    }
    response = client.put(f"/api/employees/{employee_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["department"] == "New Dept"
    assert data["email"] == "updatetest@example.com"  # Should not change

def test_update_employee_not_found():
    headers = get_auth_headers()
    update_data = {"name": "New Name"}
    response = client.put("/api/employees/99999", json=update_data, headers=headers)
    assert response.status_code == 404

def test_delete_employee():
    headers = get_auth_headers()
    
    # Create employee
    create_response = client.post("/api/employees/", json={
        "name": "Delete Test",
        "email": "deletetest@example.com",
        "department": "Temp",
        "role": "Temp"
    }, headers=headers)
    employee_id = create_response.json()["id"]
    
    # Delete employee
    response = client.delete(f"/api/employees/{employee_id}", headers=headers)
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(f"/api/employees/{employee_id}", headers=headers)
    assert get_response.status_code == 404

def test_delete_employee_not_found():
    headers = get_auth_headers()
    response = client.delete("/api/employees/99999", headers=headers)
    assert response.status_code == 404

# Authorization Tests
def test_unauthorized_access():
    response = client.get("/api/employees/")
    assert response.status_code == 401

def test_invalid_token():
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get("/api/employees/", headers=headers)
    assert response.status_code == 401

# Admin Tests
def test_list_users_as_admin():
    headers = get_admin_headers()
    response = client.get("/api/users/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2  # At least testuser and admin

def test_list_users_as_regular_user():
    headers = get_auth_headers()
    response = client.get("/api/users/", headers=headers)
    assert response.status_code == 403  # Not enough permissions

def test_get_user_as_admin():
    headers = get_admin_headers()
    response = client.get("/api/users/1", headers=headers)
    assert response.status_code == 200

def test_pagination():
    headers = get_auth_headers()
    
    # Create multiple employees
    for i in range(15):
        client.post("/api/employees/", json={
            "name": f"Pagination Test {i}",
            "email": f"page{i}@example.com",
            "department": "Testing",
            "role": "Tester"
        }, headers=headers)
    
    # Test pagination
    response = client.get("/api/employees/?page=1&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 10
    assert data["page"] == 1
    assert data["limit"] == 10
    
    # Get second page
    response = client.get("/api/employees/?page=2&limit=10", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2