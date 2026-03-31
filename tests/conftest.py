import pytest
import requests
import time
import uuid
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

@pytest.fixture(scope="session", autouse=True)
def wait_for_app():
    """Wait for application to be ready before running tests"""
    max_retries = 30
    
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/healthz", timeout=2)
            if response.status_code in [200, 503]:
                print(f"\n✓ Application is responding after {i+1} attempts")
                return
        except (requests.ConnectionError, requests.Timeout):
            if i < max_retries - 1:
                time.sleep(1)
    
    pytest.fail("Application failed to start within 30 seconds")

@pytest.fixture
def base_url():
    """Provide base URL for tests"""
    return BASE_URL

@pytest.fixture
def unique_email():
    """Generate unique email for testing"""
    return f"test_{uuid.uuid4()}@example.com"

@pytest.fixture
def create_test_user(base_url):
    """Factory fixture to create test users"""
    def _create_user(email=None, password="TestPass123!", first_name="Test", last_name="User"):
        if email is None:
            email = f"test_{uuid.uuid4()}@example.com"
        
        payload = {
            "username": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name
        }
        
        response = requests.post(f"{base_url}/v1/user", json=payload)

        # Auto-verify the user in DB so tests can use authenticated endpoints
        if response.status_code == 201:
            try:
                from app.database import get_db
                from app.models import User
                db = next(get_db())
                user = db.query(User).filter(User.email == email).first()
                if user:
                    user.verified = True
                    user.verification_token = None
                    user.token_expiry = None
                    db.commit()
                db.close()
            except Exception as e:
                print(f"Warning: could not auto-verify user: {e}")

        return response, email, password
    
    return _create_user