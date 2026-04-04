# Web Application - CSYE 6225

A FastAPI-based RESTful web application with user management, email verification, file upload, and health monitoring.

## Prerequisites

### System Requirements
- **OS**: Ubuntu 24.04 LTS (production) / macOS (development)
- **Python**: 3.9+
- **Database**: PostgreSQL 14+

### Development Tools
- Git (configured with SSH)
- Python virtual environment (venv)
- curl or Postman for API testing

## Framework and Library Dependencies

### Application Dependencies
- **FastAPI** 0.104.1 — web framework
- **Uvicorn** 0.24.0 — ASGI server
- **SQLAlchemy** 2.0.23 — ORM
- **psycopg2-binary** 2.9.9 — PostgreSQL adapter
- **python-dotenv** 1.0.0 — environment variable management
- **passlib[bcrypt]** 1.7.4 — password hashing
- **pydantic[email]** 2.5.0 — data validation
- **boto3** — AWS SDK (S3, SNS, Secrets Manager, CloudWatch)
- **python-multipart** 0.0.6 — file upload support

### Testing Dependencies
- **pytest** 7.4.3
- **requests** 2.31.0
- **pytest-html** 4.1.1
- **pytest-cov** 4.1.0

---

## Installation

### 1. Clone the Repository
```bash
git clone git@github.com:KeerthanaDeviGovindaraj/webapp-fork.git
cd webapp-fork
```

### 2. Set Up PostgreSQL
```bash
# macOS
brew install postgresql@14
brew services start postgresql@14
createdb webapp_db
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
nano .env
```

Required variables:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=webapp_db
DB_USER=postgres
DB_PASSWORD=your_password
APP_HOST=0.0.0.0
APP_PORT=8080
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:...
APP_DOMAIN=dev.keerthana.click
```

### 4. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 5. Run the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

---

## API Endpoints

### Public Endpoints

#### Health Check
```
GET /healthz
```
Returns 200 OK if app and database are healthy.

#### Create User
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
Returns 201 Created. Triggers SNS → Lambda → SES email verification.

#### Verify Email
```
GET /v1/user/verify?token=<uuid>&email=<email>
```
Verifies the user's email address. Token expires after 2 minutes.

### Protected Endpoints (Basic Auth)

#### Get User
```
GET /v1/user/self
Authorization: Basic <base64-credentials>
```

#### Update User
```
PUT /v1/user/self
Authorization: Basic <base64-credentials>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith",
  "password": "NewPassword456!"
}
```

#### Upload Profile Picture
```
POST /v1/user/self/pic
Authorization: Basic <base64-credentials>
Content-Type: multipart/form-data
```
Stores image in S3. Only one image per user (replaces existing).

#### Delete Profile Picture
```
DELETE /v1/user/self/pic
Authorization: Basic <base64-credentials>
```

---

## Email Verification Flow

1. User registers via `POST /v1/user`
2. App publishes message to SNS topic with `{ email, firstName, token }`
3. SNS triggers Lambda function
4. Lambda sends verification email via SES
5. User clicks link: `https://<domain>/v1/user/verify?token=<token>&email=<email>`
6. Token expires after 2 minutes — unverified users cannot log in

---

## CI/CD Pipeline

### Pull Request Workflow (`.github/workflows/ci.yml`)

Triggers on pull requests to `main`. Steps:
1. Checkout code
2. Set up Python 3.9
3. Install dependencies
4. Start PostgreSQL service
5. Run integration tests
6. Upload test results as artifacts

### PR Merged Workflow (`.github/workflows/packer-build.yml`)

Triggers on merge to `main`. Steps:
1. Build application artifact
2. Run Packer to bake new AMI (DEV account)
3. Share AMI with DEMO account
4. Switch to DEMO AWS credentials
5. Create new Launch Template version with new AMI
6. Trigger ASG instance refresh
7. Wait for refresh to complete (health check)

### Branch Protection Rules

- Require pull request before merging
- Require status checks to pass
- Require branches to be up to date
- No force pushes
- No deletions

---

## Project Structure

```
webapp/
├── app/
│   ├── routes/
│   │   ├── health.py         # Health check endpoint
│   │   ├── user.py           # User CRUD endpoints
│   │   └── picture.py        # Profile picture endpoints
│   ├── auth.py               # Basic auth logic
│   ├── config.py             # Configuration management
│   ├── database.py           # DB connection
│   ├── main.py               # App entry point
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   └── sns.py                # SNS publish logic
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_user_creation.py
│   ├── test_authentication.py
│   ├── test_user_update.py
│   └── test_negative_cases.py
├── .github/
│   └── workflows/
│       ├── ci.yml                  # PR integration tests
│       └── packer-build.yml        # AMI build + DEMO deploy
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## Database Schema

### `users` table
| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `email` | String | Unique username/email |
| `password` | String | BCrypt hashed |
| `first_name` | String | First name |
| `last_name` | String | Last name |
| `is_verified` | Boolean | Email verified flag |
| `account_created` | DateTime | Creation timestamp |
| `account_updated` | DateTime | Last update timestamp |

### `email_verification_tokens` table
| Column | Type | Description |
|--------|------|-------------|
| `token` | UUID | Primary key |
| `email` | String | Associated email |
| `expires_at` | DateTime | Token expiry (2 min TTL) |

---

## Security Considerations

- Passwords are BCrypt hashed — never stored in plaintext
- No AWS credentials hardcoded — IAM role attached to EC2
- DB password retrieved from Secrets Manager at boot
- S3 bucket is private — no public access
- HTTPS enforced via ALB (port 443)
- EC2 instances not directly reachable — only via ALB
- Unverified users cannot authenticate

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_health.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

The test suite includes 21 integration tests covering health checks, user creation, authentication, user updates, and negative cases.
