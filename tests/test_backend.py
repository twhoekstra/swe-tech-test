#!/usr/bin/env python3
"""Tests for the FastAPI backend."""

import pytest
import sys
import os
from http import HTTPStatus

from src.backend.app.main import app, DataRequest, get_store, time_to_samples
from fastapi.testclient import TestClient


@pytest.fixture()
def filename() -> str:
    return "mock48_2500hz_1.5h.zarr"


@pytest.fixture()
def client_unset():
    """Test client with no file set."""
    return TestClient(app)


@pytest.fixture()
def client(client_unset, filename):
    """Test client with default file set."""
    # Set the file before running tests
    request_data = {"filename": filename}
    client_unset.post("/set_file", json=request_data)
    return client_unset

def test_set_file(client_unset, filename):
    """Test setting the file to use for data operations."""
    request_data = {"filename": filename}
    
    response = client_unset.post("/set_file", json=request_data)
    assert response.status_code == HTTPStatus.OK
    
    data = response.json()
    assert "message" in data
    assert "file_path" in data
    assert "status" in data
    assert data["status"] == "success"
    assert filename in data["message"]


def test_set_file_nonexistent(client_unset):
    """Test setting a file that doesn't exist."""
    request_data = {"filename": "nonexistent_file.zarr"}
    
    response = client_unset.post("/set_file", json=request_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "does not exist" in response.text


def test_get_metadata(client):
    """Test the metadata endpoint."""

    response = client.get("/metadata")
    assert response.status_code == HTTPStatus.OK
    
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


def test_get_data_valid_request(client):
    """Test data endpoint with valid parameters."""
    request_data = {
        "start_time": 0.0,
        "end_time": 1.0,
        "channel": 0,
        "data_type": "voltage"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == HTTPStatus.OK
    
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


def test_get_data_current(client):
    """Test data endpoint with current data type."""
    request_data = {
        "start_time": 0.0,
        "end_time": 0.1,
        "channel": 0,
        "data_type": "current"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == HTTPStatus.OK
    
    data = response.json()
    assert data["data_type"] == "current"
    assert data["unit"] == "pA"
    assert len(data["data"]) == 250  # 0.1 second at 2500 Hz


def test_get_data_invalid_channel(client):
    """Test data endpoint with invalid channel."""
    request_data = {
        "start_time": 0.0,
        "end_time": 1.0,
        "channel": 48,  # Invalid, max is 47
        "data_type": "voltage"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Channel must be between 0 and 47" in response.text


def test_get_data_invalid_time_range(client):
    """Test data endpoint with invalid time range."""
    request_data = {
        "start_time": 6000.0,  # Beyond duration
        "end_time": 7000.0,
        "channel": 0,
        "data_type": "voltage"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "Time range must be within" in response.text


def test_get_data_invalid_data_type(client):
    """Test data endpoint with invalid data type."""
    request_data = {
        "start_time": 0.0,
        "end_time": 1.0,
        "channel": 0,
        "data_type": "invalid"
    }
    
    response = client.post("/data", json=request_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "data_type must be" in response.text



def test_time_to_samples():
    """Test time to sample conversion."""
    
    start_sample, end_sample = time_to_samples(0.0, 1.0, 2500.0)
    assert start_sample == 0
    assert end_sample == 2500
    
    start_sample, end_sample = time_to_samples(0.5, 1.5, 2500.0)
    assert start_sample == 1250
    assert end_sample == 3750


if __name__ == "__main__":
    pytest.main([__file__, "-v"])