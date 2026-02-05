import pytest
import requests


def test_creation_with_all_fields_missing(base_url):
    """Negative: All required fields missing"""
    payload = {}
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 400


def test_creation_with_null_values(base_url, unique_email):
    """Negative: Null values in required fields"""
    payload = {
        "username": unique_email,
        "password": None,
        "first_name": "Test",
        "last_name": "User"
    }
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 400


def test_update_with_readonly_field_returns_400(base_url, create_test_user):
    """Negative: Attempt to update readonly field"""
    response, email, password = create_test_user()
    assert response.status_code == 201
    
    payload = {"username": "newemail@example.com"}
    response = requests.put(
        f"{base_url}/v1/user/self",
        json=payload,
        auth=(email, password)
    )
    assert response.status_code == 400


def test_update_with_invalid_field_type(base_url, create_test_user):
    """Negative: Invalid data type in update"""
    response, email, password = create_test_user()
    assert response.status_code == 201
    
    payload = {"first_name": 12345}
    response = requests.put(
        f"{base_url}/v1/user/self",
        json=payload,
        auth=(email, password)
    )
    assert response.status_code in [400, 422]
