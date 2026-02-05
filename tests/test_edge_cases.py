import pytest
import requests
import threading
import time


# Boundary Value Tests
def test_minimum_valid_password_length(base_url, unique_email):
    """Edge: Exactly 8 character password (minimum)"""
    payload = {
        "username": unique_email,
        "password": "Pass123!",  # Exactly 8 chars
        "first_name": "Test",
        "last_name": "User"
    }
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 201


def test_below_minimum_password_length(base_url, unique_email):
    """Edge: 7 character password (below minimum)"""
    payload = {
        "username": unique_email,
        "password": "Pass12!",  # 7 chars
        "first_name": "Test",
        "last_name": "User"
    }
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code == 400


def test_special_characters_in_names(base_url, unique_email):
    """Edge: Special characters in name fields"""
    payload = {
        "username": unique_email,
        "password": "Pass123!",
        "first_name": "John-Paul",
        "last_name": "O'Brien"
    }
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code in [201, 400]


def test_very_long_names(base_url, unique_email):
    """Edge: Very long name strings"""
    long_name = "A" * 100
    payload = {
        "username": unique_email,
        "password": "Pass123!",
        "first_name": long_name,
        "last_name": long_name
    }
    response = requests.post(f"{base_url}/v1/user", json=payload)
    assert response.status_code in [201, 400]


# Performance Tests (Basic)
def test_health_check_response_time(base_url):
    """Performance: Health check responds quickly"""
    start = time.time()
    response = requests.get(f"{base_url}/healthz")
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 1.0, f"Response took {elapsed}s"


def test_concurrent_health_checks(base_url):
    """Performance: Handle concurrent requests"""
    results = []
    
    def make_request():
        response = requests.get(f"{base_url}/healthz")
        results.append(response.status_code)
    
    threads = [threading.Thread(target=make_request) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    
    assert all(code == 200 for code in results)
    assert len(results) == 5


# Data Integrity Tests
def test_data_persists_correctly(base_url, create_test_user):
    """Data Integrity: Created data persists"""
    response, email, password = create_test_user(
        first_name="Persist",
        last_name="Test"
    )
    assert response.status_code == 201
    created_data = response.json()
    
    # Retrieve and verify
    response2 = requests.get(
        f"{base_url}/v1/user/self",
        auth=(email, password)
    )
    retrieved_data = response2.json()
    
    assert created_data["id"] == retrieved_data["id"]
    assert created_data["first_name"] == retrieved_data["first_name"]


def test_updates_dont_affect_other_fields(base_url, create_test_user):
    """Data Integrity: Updates don't modify unrelated fields"""
    response, email, password = create_test_user(
        first_name="Original",
        last_name="Name"
    )
    original = response.json()
    
    # Update only first_name
    requests.put(
        f"{base_url}/v1/user/self",
        json={"first_name": "Modified"},
        auth=(email, password)
    )
    
    # Verify other fields unchanged
    response = requests.get(
        f"{base_url}/v1/user/self",
        auth=(email, password)
    )
    updated = response.json()
    
    assert updated["last_name"] == original["last_name"]
    assert updated["id"] == original["id"]
    assert updated["account_created"] == original["account_created"]
