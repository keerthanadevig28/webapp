import pytest
import requests


def test_get_user_without_auth_returns_401(base_url):
    """Test that accessing protected endpoint without auth returns 401"""
    response = requests.get(f"{base_url}/v1/user/self")
    assert response.status_code == 401


def test_get_user_with_invalid_credentials_returns_401(base_url):
    """Test that invalid credentials return 401"""
    response = requests.get(
        f"{base_url}/v1/user/self",
        auth=("invalid@example.com", "wrongpassword")
    )
    assert response.status_code == 401


def test_get_user_self_with_valid_auth(base_url, create_test_user):
    """Test retrieving own user information"""
    response, email, password = create_test_user()
    assert response.status_code == 201
    
    response = requests.get(
        f"{base_url}/v1/user/self",
        auth=(email, password)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data.get("username", data.get("email")) == email
    assert "password" not in data


def test_update_user_without_auth_returns_401(base_url):
    """Test updating without auth returns 401"""
    payload = {"first_name": "New"}
    response = requests.put(f"{base_url}/v1/user/self", json=payload)
    assert response.status_code == 401
