import pytest
import requests


def test_create_user_success(base_url, unique_email):
    """Test successful user creation with valid data"""
    payload = {
        "username": unique_email,
        "password": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe"
    }
    
    response = requests.post(f"{base_url}/v1/user", json=payload)
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data.get("username", data.get("email")) == unique_email
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "account_created" in data
    assert "account_updated" in data
    assert "password" not in data


def test_create_user_ignores_readonly_fields(base_url, unique_email):
    """Test that account_created and account_updated cannot be set by user"""
    payload = {
        "username": unique_email,
        "password": "SecurePass123!",
        "first_name": "Jane",
        "last_name": "Smith",
        "account_created": "2020-01-01T00:00:00Z",
        "account_updated": "2020-01-01T00:00:00Z"
    }
    
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["account_created"] != "2020-01-01T00:00:00Z"
    assert data["account_updated"] != "2020-01-01T00:00:00Z"


def test_create_user_duplicate_email_returns_400(base_url, create_test_user):
    """Test that creating user with duplicate email returns 400"""
    response1, email, password = create_test_user()
    assert response1.status_code == 201
    
    payload = {
        "username": email,
        "password": "AnotherPass123!",
        "first_name": "Duplicate",
        "last_name": "User"
    }
    
    response2 = requests.post(f"{base_url}/v1/user", json=payload)
    assert response2.status_code == 400


def test_create_user_missing_password_returns_400(base_url, unique_email):
    """Test that missing required field returns 400"""
    payload = {
        "username": unique_email,
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 400


def test_create_user_invalid_email_format_returns_400(base_url):
    """Test that invalid email format returns 400"""
    payload = {
        "username": "not-an-email",
        "password": "SecurePass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 400


def test_create_user_short_password_returns_400(base_url, unique_email):
    """Test that password shorter than 8 characters returns 400"""
    payload = {
        "username": unique_email,
        "password": "short",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 400
