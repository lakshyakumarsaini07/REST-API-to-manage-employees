# Employee Management REST API

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A robust REST API built with FastAPI for managing employee data in a company. This project includes full CRUD operations, JWT-based authentication, data validation, filtering, pagination, and comprehensive testing.

##  Features

- **CRUD Operations**: Complete Create, Read, Update, Delete functionality for employees
- **JWT Authentication**: Secure API endpoints with JSON Web Token authentication
- **Data Validation**: Email uniqueness and format validation using Pydantic
- **Filtering & Pagination**: Advanced querying with department/role filters and paginated results
- **Error Handling**: Comprehensive error responses with appropriate HTTP status codes
- **Database Integration**: SQLite database with SQLAlchemy ORM
- **API Documentation**: Interactive Swagger UI and ReDoc documentation
- **Testing**: Full test suite using pytest with coverage reporting

##  Requirements

- Python 3.8 or higher
- SQLite (built-in with Python)

##  Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lakshyakumarsaini07/REST-API-to-manage-employees.git
   cd employee-management-api
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://127.0.0.1:8000`

##  API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

##  Authentication

### 1. Create a User
```bash
curl -X POST "http://127.0.0.1:8000/users/" \
     -H "Content-Type: application/json" \
     -d '\''{"username": "admin", "password": "password"}'\''
```

### 2. Obtain Access Token
```bash
curl -X POST "http://127.0.0.1:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=password"
```

### 3. Use Token in Requests
```bash
curl -X GET "http://127.0.0.1:8000/api/employees/" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/token` | Login and obtain JWT token |
| POST | `/users/` | Create a new user |
| POST | `/api/employees/` | Create a new employee |
| GET | `/api/employees/` | List employees (with filtering & pagination) |
| GET | `/api/employees/{id}/` | Get employee by ID |
| PUT | `/api/employees/{id}/` | Update employee by ID |
| DELETE | `/api/employees/{id}/` | Delete employee by ID |

### Query Parameters for Employee Listing

- `department`: Filter by department (e.g., `?department=Engineering`)
- `role`: Filter by role (e.g., `?role=Manager`)
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)

Example: `GET /api/employees/?department=Engineering&page=1&limit=20`

##  Testing

Run the test suite with pytest:

```bash
pytest
```

For coverage report:
```bash
pytest --cov=app --cov-report=html
```

##  Database

The application uses SQLite (`employees.db`) which is automatically created on first run. The database schema is managed through SQLAlchemy migrations.

##  Project Structure

```
employee-management-api/
 app/
    __init__.py
    main.py          # FastAPI application
    models.py        # SQLAlchemy models
    schemas.py       # Pydantic schemas
    crud.py          # CRUD operations
    database.py      # Database configuration
    auth.py          # Authentication utilities
    config.py        # Application configuration
 tests/
    __init__.py
    test_main.py     # Test cases
 requirements.txt     # Python dependencies
 README.md           # This file
```

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m '\''Add some amazing feature'\'')
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Support

If you have any questions or issues, please open an issue on GitHub or contact the maintainers.

---

Built with  using [FastAPI](https://fastapi.tiangolo.com/)
