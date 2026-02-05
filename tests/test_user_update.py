import pytest
import requests
import time


def test_update_user_first_name_success(base_url, create_test_user):
    """Test updating first name"""
    response, email, password = create_test_user(first_name="Old", last_name="Name")
    assert response.status_code == 201
    
    update_payload = {"first_name": "New"}
    response = requests.put(
        f"{base_url}/v1/user/self",
        json=update_payload,
        auth=(email, password)
    )
    
    assert response.status_code == 204


def test_update_user_password_success(base_url, create_test_user):
    """Test updating password"""
    response, email, old_password = create_test_user()
    assert response.status_code == 201
    
    new_password = "NewSecurePass456!"
    update_payload = {"password": new_password}
    
    response = requests.put(
        f"{base_url}/v1/user/self",
        json=update_payload,
        auth=(email, old_password)
    )
    
    assert response.status_code == 204
    

    response = requests.get(
        f"{base_url}/v1/user/self",
        auth=(email, new_password)
    )
    assert response.status_code == 200


def test_update_with_empty_payload_returns_400(base_url, create_test_user):
    """Test that updating with empty payload returns 400"""
    response, email, password = create_test_user()
    assert response.status_code == 201
    
    response = requests.put(
        f"{base_url}/v1/user/self",
        json={},
        auth=(email, password)
    )
    assert response.status_code == 400
