"""Tests for the FastAPI wrapper."""

import numpy as np
import pytest

# Skip all tests in this module if fastapi is not installed
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from solar_and_storage.api.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_successful_optimization():
    """Test successful optimization with valid data."""
    # Use test data from test_optimization.py
    hours_per_day = 24

    prices = np.zeros(hours_per_day) + 30
    prices[6:19] = 40
    prices[9] = 50
    prices[12:14] = 30
    prices[16:18] = 50
    prices[17] = 60

    solar = np.zeros(hours_per_day)
    solar[8:16] = 2.0
    solar[10:14] = 4.0

    request_data = {
        "prices": prices.tolist(),
        "solar_generation": solar.tolist(),
    }

    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "optimal"
    assert data["message"] == "Optimization successful"
    assert data["total_profit"] is not None
    assert data["total_profit"] > 0
    assert data["schedule"] is not None
    assert len(data["schedule"]) == 24

    # Check schedule structure
    first_item = data["schedule"][0]
    assert "hour" in first_item
    assert "power" in first_item
    assert "battery_soc" in first_item
    assert "solar_power_to_grid" in first_item
    assert "profit" in first_item


def test_validation_error_wrong_list_length():
    """Test validation error for wrong list lengths."""
    request_data = {
        "prices": [30],  # Only 1 item instead of 24
        "solar_generation": [0],  # Only 1 item instead of 24
    }

    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 422
    assert "detail" in response.json()


def test_validation_error_invalid_soc_range():
    """Test validation error for invalid SOC values."""
    prices = [30] * 24
    solar = [0] * 24

    request_data = {
        "prices": prices,
        "solar_generation": solar,
        "battery_soc_min": -0.5,  # Invalid: should be >= 0
    }

    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 422


def test_validation_error_invalid_capacity():
    """Test validation error for invalid capacity values."""
    prices = [30] * 24
    solar = [0] * 24

    request_data = {
        "prices": prices,
        "solar_generation": solar,
        "battery_capacity": 0,  # Invalid: should be > 0
    }

    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 422


def test_infeasible_scenario():
    """Test handling of infeasible optimization scenario."""
    # Create an infeasible scenario: impossible constraints
    prices = [50] * 24
    solar = [0] * 24

    request_data = {
        "prices": prices,
        "solar_generation": solar,
        "battery_soc_min": 0.8,  # Minimum SOC of 80%
        "battery_soc_max": 0.2,  # Maximum SOC of 20% (impossible!)
        "battery_capacity": 1,
        "power_rating": 1,
        "current_soc": 0.5,
    }

    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 200  # Not a client error

    data = response.json()
    assert data["status"] == "infeasible"
    assert data["total_profit"] is None
    assert data["schedule"] is None


def test_with_default_parameters():
    """Test optimization using all default parameters."""
    # Minimal request with only required fields
    request_data = {
        "prices": [
            30, 30, 30, 30, 30, 30, 40, 40, 40, 50, 40, 40,
            30, 30, 40, 40, 50, 60, 40, 30, 30, 30, 30, 30,
        ],
        "solar_generation": [
            0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 4, 4,
            4, 4, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0,
        ],
    }

    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "optimal"
    assert data["total_profit"] is not None


def test_with_custom_parameters():
    """Test optimization with custom battery parameters."""
    request_data = {
        "prices": [
            30, 30, 30, 30, 30, 30, 40, 40, 40, 50, 40, 40,
            30, 30, 40, 40, 50, 60, 40, 30, 30, 30, 30, 30,
        ],
        "solar_generation": [
            0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 4, 4,
            4, 4, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0,
        ],
        "battery_capacity": 2.0,
        "power_rating": 1.5,
        "battery_eta_charge": 0.9,
        "battery_eta_discharge": 0.9,
        "current_soc": 0.5,
    }

    response = client.post("/api/v1/optimize", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "optimal"
    assert data["total_profit"] is not None
