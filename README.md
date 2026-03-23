A FastAPI-based RESTful web application with user management and health monitoring capabilities.

## Prerequisites

### System Requirements
- **Operating System**: Ubuntu 24.04 LTS (production) or macOS (development)
- **Python**: 3.9 or higher
- **Database**: PostgreSQL 14+
- **Package Manager**: pip

### Development Tools
- Git (configured with SSH)
- Virtual environment (venv)
- curl or Postman for API testing

## Framework and Library Dependencies

### Application Dependencies
- **FastAPI** 0.104.1 - Modern web framework for building APIs
- **Uvicorn** 0.24.0 - ASGI web server
- **SQLAlchemy** 2.0.23 - SQL ORM toolkit
- **psycopg2-binary** 2.9.9 - PostgreSQL database adapter
- **python-dotenv** 1.0.0 - Environment variable management
- **passlib[bcrypt]** 1.7.4 - Password hashing library
- **pydantic[email]** 2.5.0 - Data validation using Python type hints
- **pydantic-settings** 2.1.0 - Settings management
- **python-multipart** 0.0.6 - Multipart form data parsing

### Testing Dependencies
- **pytest** 7.4.3 - Testing framework
- **requests** 2.31.0 - HTTP library for API testing
- **pytest-html** 4.1.1 - HTML test report generation
- **pytest-cov** 4.1.0 - Test coverage reporting

## Installation

### 1. Clone the Repository
```bash
# Clone using SSH (required)
git clone git@github.com:YOUR-USERNAME/webapp.git
cd webapp
```

### 2. Set Up PostgreSQL Database

#### On macOS:
```bash
brew install postgresql@14
brew services start postgresql@14
```

#### Create Database:
```bash
createdb webapp_db
```

### 3. Configure Environment Variables
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

Required environment variables:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=webapp_db
DB_USER=postgres
DB_PASSWORD=your_password
APP_HOST=0.0.0.0
APP_PORT=8080
```

### 4. Set Up Python Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
.\venv\Scripts\activate  # On Windows
```

### 5. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install application dependencies
pip install -r requirements.txt

# Install development/testing dependencies
pip install -r requirements-dev.txt
```

## Build and Deploy Instructions

### Running the Application

From the project root directory:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

The application will start on `http://localhost:8080`

### Verify Deployment
```bash
# Test health check endpoint
curl http://localhost:8080/healthz

# Expected: HTTP 200 with empty body
```

## API Endpoints

### Public Endpoints (No Authentication)

#### Health Check
```
GET /healthz
```
Returns application and database connectivity status.

#### Create User Account
```
POST /v1/user
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "SecurePassword123!",
  "first_name": "John",
  "last_name": "Doe"
}
```
Returns: 201 Created with user details (excluding password)

### Protected Endpoints (Basic Authentication Required)

#### Get User Information
```
GET /v1/user/self
Authorization: Basic <base64-encoded-credentials>
```
Returns: 200 OK with user information

#### Update User Information
```
PUT /v1/user/self
Authorization: Basic <base64-encoded-credentials>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "NewPassword456!"
}
```
Returns: 204 No Content

## Testing

### Prerequisites for Testing
1. PostgreSQL database running and accessible
2. Application running on http://localhost:8080
3. Test dependencies installed from requirements-dev.txt

### Running Tests

#### Run All Tests
```bash
pytest tests/ -v
```

#### Run Specific Test File
```bash
pytest tests/test_health.py -v
```

#### Run Specific Test
```bash
pytest tests/test_health.py::test_health_check_get_returns_200 -v
```

#### Run Tests with Detailed Output
```bash
pytest tests/ -vv
```


### Test Coverage

The test suite includes 21 comprehensive integration tests:

- **Health Check Tests (7)**: Validates endpoint availability and HTTP methods
- **User Creation Tests (6)**: Tests valid/invalid user registration scenarios
- **Authentication Tests (4)**: Verifies authentication and authorization
- **User Update Tests (3)**: Tests user information modification
- **Negative Cases (1)**: Tests error handling

## Continuous Integration

### GitHub Actions Workflow

This project uses GitHub Actions for automated testing on every pull request.

#### Workflow Triggers
- Pull requests to the `main` branch
- Automatic on code push to PR branches

#### Workflow Steps
1. Checkout code from repository
2. Set up Python 3.9 environment
3. Install application and test dependencies
4. Start PostgreSQL service container
5. Start FastAPI application
6. Run all integration tests
7. Upload test results as artifacts

#### Viewing CI Results

1. Navigate to the repository on GitHub
2. Go to the "Pull requests" tab
3. Select your pull request
4. Click the "Checks" tab to view test results

### Branch Protection Rules

The `main` branch is protected with:
- ✅ Require pull request before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators in restrictions
- ❌ No force pushes allowed
- ❌ No deletions allowed

## Project Structure
```
webapp/
├── app/                          # Application code
│   ├── routes/                   # API route handlers
│   │   ├── __init__.py
│   │   ├── health.py            # Health check endpoint
│   │   └── user.py              # User management endpoints
│   ├── __init__.py
│   ├── auth.py                  # Authentication logic
│   ├── config.py                # Configuration management
│   ├── database.py              # Database connection and initialization
│   ├── main.py                  # Application entry point
│   ├── models.py                # SQLAlchemy database models
│   └── schemas.py               # Pydantic request/response schemas
├── tests/                        # Integration tests
│   ├── __init__.py
│   ├── conftest.py              # Test fixtures and configuration
│   ├── test_health.py           # Health endpoint tests
│   ├── test_user_creation.py   # User creation tests
│   ├── test_authentication.py  # Authentication tests
│   ├── test_user_update.py     # User update tests
│   └── test_negative_cases.py  # Error and edge case tests
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD pipeline
├── .gitignore                   # Git ignore patterns
├── .env.example                 # Example environment variables
├── requirements.txt             # Application dependencies
├── requirements-dev.txt         # Development dependencies
└── README.md                    # This file
```

## Configuration

### Environment Variables

All sensitive configuration is managed through environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |
| `DB_NAME` | Database name | `webapp_db` |
| `DB_USER` | Database username | `postgres` |
| `DB_PASSWORD` | Database password | `your_password` |
| `APP_HOST` | Application host | `0.0.0.0` |
| `APP_PORT` | Application port | `8080` |

### Database Schema

The application automatically creates the following tables:

#### `users` table
- `id` (UUID): Primary key
- `email` (String): Unique user email/username
- `password` (String): BCrypt hashed password
- `first_name` (String): User's first name
- `last_name` (String): User's last name
- `account_created` (DateTime): Account creation timestamp
- `account_updated` (DateTime): Last update timestamp

#### `health_checks` table
- `check_id` (BigInt): Primary key
- `check_datetime` (DateTime): Health check timestamp
