import pytest
import requests


def test_nonexistent_endpoint_returns_404(base_url):
    """Test that accessing non-existent endpoint returns 404"""
    response = requests.get(f"{base_url}/v1/nonexistent")
    assert response.status_code == 404
