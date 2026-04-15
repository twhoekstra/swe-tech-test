#!/usr/bin/env python3
"""Tests for the FastAPI backend."""

import pytest
import sys
import os

# Add the backend to the path
sys.path.insert(0, "/repo/src/backend")

from app.main import app, DataRequest, get_zarr_store
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_metadata():
    """Test the metadata endpoint."""
    response = client.get("/metadata")
    assert response.status_code == 200
    
    data = response.json()
    assert "device_id" in data
    assert "number_of_channels" in data
    assert "sample_rate_hz" in data
    assert "duration_sec" in data
    
    # Check expected values
    assert data["device_id"] == "mock-48ch-001"
    assert data["number_of_channels"] == 48
    assert data["sample_rate_hz"] == 2500.0
    assert data["duration_sec"] == 5400.0


def test_get_data_valid_request():
    """Test data endpoint with valid parameters."""
    request_data = {
        "start_time": 0.0,
        "end_time": 1.0,
        "channel": 0,
        "data_type": "voltage"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "channel" in data
    assert "start_time" in data
    assert "end_time" in data
    assert "sample_rate" in data
    assert "data" in data
    assert "data_type" in data
    assert "unit" in data
    
    # Check data properties
    assert data["channel"] == 0
    assert data["data_type"] == "voltage"
    assert data["unit"] == "mV"
    assert len(data["data"]) == 2500  # 1 second at 2500 Hz


def test_get_data_current():
    """Test data endpoint with current data type."""
    request_data = {
        "start_time": 0.0,
        "end_time": 0.1,
        "channel": 0,
        "data_type": "current"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["data_type"] == "current"
    assert data["unit"] == "pA"
    assert len(data["data"]) == 250  # 0.1 second at 2500 Hz


def test_get_data_invalid_channel():
    """Test data endpoint with invalid channel."""
    request_data = {
        "start_time": 0.0,
        "end_time": 1.0,
        "channel": 48,  # Invalid, max is 47
        "data_type": "voltage"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == 400
    assert "Channel must be between 0 and 47" in response.text


def test_get_data_invalid_time_range():
    """Test data endpoint with invalid time range."""
    request_data = {
        "start_time": 6000.0,  # Beyond duration
        "end_time": 7000.0,
        "channel": 0,
        "data_type": "voltage"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == 400
    assert "Time range must be within" in response.text


def test_get_data_invalid_data_type():
    """Test data endpoint with invalid data type."""
    request_data = {
        "start_time": 0.0,
        "end_time": 1.0,
        "channel": 0,
        "data_type": "invalid"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == 400
    assert "data_type must be" in response.text


def test_zarr_store_access():
    """Test that we can access the Zarr store."""
    store = get_zarr_store()
    assert store is not None
    assert "voltage_data" in store
    assert "current_data" in store
    assert store.attrs["number_of_channels"] == 48


def test_time_to_samples():
    """Test time to sample conversion."""
    from app.main import time_to_samples
    
    start_sample, end_sample = time_to_samples(0.0, 1.0, 2500.0)
    assert start_sample == 0
    assert end_sample == 2500
    
    start_sample, end_sample = time_to_samples(0.5, 1.5, 2500.0)
    assert start_sample == 1250
    assert end_sample == 3750


if __name__ == "__main__":
    pytest.main([__file__, "-v"])