import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = str(Path(__file__).parent.parent)
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.hotels import get_hotels

client = TestClient(app)


def test_get_hotels_no_prompt():
    """Test that the endpoint returns all hotels when no prompt is provided"""
    response = client.get("/hotels")
    print(response)
    print("Hello@###################")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


def test_get_hotels_with_prompt():
    """Test that the endpoint returns filtered hotels when a prompt is provided"""
    response = client.get("/hotels?prompt=test")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_hotels_empty_result():
    """Test that the endpoint returns empty list when no hotels match the prompt"""
    response = client.get("/hotels?prompt=nonexistenthotel123")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_hotel_schema():
    """Test that returned hotels have the correct schema"""
    response = client.get("/hotels")
    assert response.status_code == 200
    data = response.json()

    # Check that each hotel has required fields
    for hotel in data:
        assert "name" in hotel
        assert "amenities" in hotel
        assert isinstance(hotel["amenities"], list)
