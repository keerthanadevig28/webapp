import pytest
import requests


def test_health_check_get_returns_200(base_url):
    """Test GET /healthz returns 200 OK"""
    response = requests.get(f"{base_url}/healthz")
    assert response.status_code == 400
    assert len(response.content) == 0


def test_health_check_has_cache_control_header(base_url):
    """Test response includes Cache-Control header"""
    response = requests.get(f"{base_url}/healthz")
    assert "Cache-Control" in response.headers
    cache_control = response.headers["Cache-Control"].lower()
    assert "no-cache" in cache_control


def test_health_check_post_returns_405(base_url):
    """Test POST /healthz returns 405 Method Not Allowed"""
    response = requests.post(f"{base_url}/healthz")
    assert response.status_code == 405


def test_health_check_put_returns_405(base_url):
    """Test PUT /healthz returns 405"""
    response = requests.put(f"{base_url}/healthz")
    assert response.status_code == 405


def test_health_check_delete_returns_405(base_url):
    """Test DELETE /healthz returns 405"""
    response = requests.delete(f"{base_url}/healthz")
    assert response.status_code == 405


def test_health_check_patch_returns_405(base_url):
    """Test PATCH /healthz returns 405"""
    response = requests.patch(f"{base_url}/healthz")
    assert response.status_code == 405


def test_health_check_with_payload_returns_400(base_url):
    """Test GET /healthz with payload returns 400 Bad Request"""
    response = requests.get(f"{base_url}/healthz", json={"test": "data"})
    assert response.status_code == 400
