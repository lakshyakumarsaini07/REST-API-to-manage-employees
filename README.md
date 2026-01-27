# Employee Management REST API

A production-ready REST API for employee management built with FastAPI, featuring JWT authentication, comprehensive validation, and robust error handling.

## 🚀 Features

- **JWT Authentication**: Secure token-based authentication with bcrypt password hashing
- **User Management**: Role-based access control (regular users and superusers)
- **Employee CRUD Operations**: Complete employee management with validation
- **Advanced Filtering**: Search and filter employees by department, role, or name
- **Pagination**: Efficient data retrieval with configurable page sizes
- **Input Validation**: Comprehensive data validation using Pydantic
- **Error Handling**: Detailed error messages and proper HTTP status codes
- **Database**: SQLAlchemy ORM with support for SQLite, PostgreSQL, and MySQL
- **Testing**: Comprehensive test suite with pytest
- **Logging**: Structured logging for debugging and monitoring
- **API Documentation**: Auto-generated interactive documentation (Swagger UI & ReDoc)

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## 🔧 Installation

1. **Clone the repository**

<<<<<<< HEAD

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lakshyakumarsaini07/REST-API-to-manage-employees.git
   ```

=======

> > > > > > > ce39420 (changes in AUTH)

2. **Create and activate virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and update the SECRET_KEY
# Generate a secure key with: openssl rand -hex 32
```

5. **Initialize the database and create admin user**

```bash
python -m app.init_admin
```

This creates a default admin user:

- Username: `admin`
- Password: `Admin123!`
- Email: admin@example.com
- **⚠️ Change this password immediately after first login!**

## 🏃 Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## 🔐 Authentication Flow

### 1. Register a New User

```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

### 2. Login

```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=johndoe&password=SecurePass123!
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 3. Use the Token

Include the token in the Authorization header for all subsequent requests:

```bash
Authorization: Bearer <your_token>
```

## 👥 API Endpoints

### Authentication

| Method | Endpoint             | Description           | Auth Required |
| ------ | -------------------- | --------------------- | ------------- |
| POST   | `/api/auth/register` | Register new user     | No            |
| POST   | `/api/auth/login`    | Login and get token   | No            |
| GET    | `/api/auth/me`       | Get current user info | Yes           |

### Employees

| Method | Endpoint              | Description                   | Auth Required |
| ------ | --------------------- | ----------------------------- | ------------- |
| POST   | `/api/employees/`     | Create employee               | Yes           |
| GET    | `/api/employees/`     | List employees (with filters) | Yes           |
| GET    | `/api/employees/{id}` | Get employee by ID            | Yes           |
| PUT    | `/api/employees/{id}` | Update employee               | Yes           |
| DELETE | `/api/employees/{id}` | Delete employee               | Yes           |

### Users (Admin Only)

| Method | Endpoint          | Description    | Auth Required |
| ------ | ----------------- | -------------- | ------------- |
| GET    | `/api/users/`     | List all users | Admin         |
| GET    | `/api/users/{id}` | Get user by ID | Admin         |
| PUT    | `/api/users/{id}` | Update user    | Admin         |

## 📝 Example Requests

### Create Employee

```bash
curl -X POST "http://localhost:8000/api/employees/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith",
    "email": "jane@example.com",
    "department": "Engineering",
    "role": "Senior Developer"
  }'
```

### List Employees with Filters

```bash
curl -X GET "http://localhost:8000/api/employees/?page=1&limit=10&department=Engineering&search=Jane" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Query Parameters:

- `page`: Page number (default: 1)
- `limit`: Items per page (default: 10, max: 100)
- `department`: Filter by department
- `role`: Filter by role
- `search`: Search in name and email

### Update Employee

```bash
curl -X PUT "http://localhost:8000/api/employees/1" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Smith-Johnson",
    "role": "Lead Developer"
  }'
```

### Delete Employee

```bash
curl -X DELETE "http://localhost:8000/api/employees/1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_main.py::test_create_employee -v
```

View coverage report:

```bash
# Open htmlcov/index.html in your browser
```

## 📁 Project Structure

```
REST API PROJECT/
│
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI app & routes
│   ├── auth.py              # JWT authentication logic
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   └── init_admin.py        # Admin creation script
│
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Comprehensive API tests
│
├── .env.example             # Environment template
├── .gitignore              # Git ignore rules
├── alembic.ini             # Database migrations config
├── requirements.txt         # Python dependencies
├── README.md               # Documentation
└── render.yml              # Deployment config
```

## 🔒 Security Features

- **Password Hashing**: Bcrypt with automatic salt generation
- **JWT Tokens**: Cryptographically signed tokens with expiration
- **Password Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
- **Email Validation**: RFC-compliant email validation
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy ORM
- **CORS Configuration**: Configurable CORS middleware
- **Input Sanitization**: Automatic via Pydantic validation
- **Role-Based Access**: Admin and regular user roles

## 🌍 Environment Variables

Create a `.env` file based on `.env.example`:

| Variable                      | Description                                 | Default                     |
| ----------------------------- | ------------------------------------------- | --------------------------- |
| `SECRET_KEY`                  | JWT signing key (**Change in production!**) | `your-super-secret-key-...` |
| `DATABASE_URL`                | Database connection string                  | `sqlite:///./employees.db`  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token lifetime                          | `30`                        |
| `REFRESH_TOKEN_EXPIRE_DAYS`   | Refresh token lifetime                      | `7`                         |
| `PASSWORD_MIN_LENGTH`         | Minimum password length                     | `8`                         |

### Database URL Examples:

```bash
# SQLite (Development)
DATABASE_URL=sqlite:///./employees.db

# PostgreSQL (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# MySQL
DATABASE_URL=mysql://user:password@localhost:3306/dbname
```

## 🚀 Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t employee-api .
docker run -d -p 8000:8000 --env-file .env employee-api
```

### Using Render

1. Push code to GitHub
2. Connect repository to Render
3. Configure environment variables
4. Deploy (configured via `render.yml`)

### Using Heroku

```bash
heroku create your-app-name
heroku config:set SECRET_KEY=your-secret-key
heroku addons:create heroku-postgresql:mini
git push heroku main
```

## 📊 Database Migrations with Alembic

```bash
# Create a migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## 🐛 Troubleshooting

### Issue: ModuleNotFoundError

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Token Expired

Tokens expire after 30 minutes. Request a new token via `/api/auth/login`.

### Issue: Database Locked (SQLite)

Use PostgreSQL for production environments.

### Issue: CORS Errors

Update CORS settings in [app/main.py](app/main.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📈 Performance Tips

1. **Use PostgreSQL** for production (better concurrency than SQLite)
2. **Enable connection pooling** in database.py
3. **Add database indexes** on frequently queried columns
4. **Implement caching** for read-heavy endpoints
5. **Use async database drivers** for better performance
6. **Set up rate limiting** to prevent abuse

## 🔍 Monitoring & Logging

Logs are configured in [app/main.py](app/main.py). View logs:

```bash
# View uvicorn logs
uvicorn app.main:app --log-level debug

# Save logs to file
uvicorn app.main:app --log-config logging.conf
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add some AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - SQL toolkit and ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [python-jose](https://github.com/mpdavis/python-jose) - JWT implementation
- [Passlib](https://passlib.readthedocs.io/) - Password hashing
