#!/usr/bin/env python3
"""Integration tests for the backend and frontend."""

import pytest
import sys
import os
import time
import subprocess
import requests
import signal

from backend.app.main import app, DataRequest, get_store, time_to_samples
from fastapi.testclient import TestClient

client = TestClient(app)


class TestIntegration:
    """Integration tests that test the full data flow."""
    
    @pytest.fixture(scope="class")
    def backend_server(self):
        """Start the FastAPI server as a subprocess."""
        # Start the server
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            cwd="/repo/src/backend",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        yield process
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
    
    def test_backend_endpoints(self):
        """Test that backend endpoints are working."""
        # Test metadata endpoint
        response = client.get("/metadata")
        assert response.status_code == 200
        metadata = response.json()
        assert metadata["number_of_channels"] == 48
        
        # Test data endpoint
        data_request = {
            "start_time": 0.0,
            "end_time": 1.0,
            "channel": 0,
            "data_type": "voltage"
        }
        response = client.post("/data", json=data_request)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 2500  # 1 second at 2500 Hz
    
    def test_data_consistency(self):
        """Test that data is consistent across multiple requests."""
        request_data = {
            "start_time": 0.0,
            "end_time": 0.1,
            "channel": 0,
            "data_type": "voltage"
        }
        
        # Make multiple requests
        response1 = client.post("/data", json=request_data)
        response2 = client.post("/data", json=request_data)
        
        data1 = response1.json()["data"]
        data2 = response2.json()["data"]
        
        # Data should be identical
        assert data1 == data2
    
    def test_large_time_range(self):
        """Test fetching data over a larger time range."""
        request_data = {
            "start_time": 0.0,
            "end_time": 60.0,  # 1 minute
            "channel": 0,
            "data_type": "voltage"
        }
        
        response = client.post("/data", json=request_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should get 60 seconds * 2500 Hz = 150,000 samples
        assert len(data["data"]) == 150000
    
    def test_multiple_channels(self):
        """Test fetching data from different channels."""
        channels_to_test = [0, 1, 47]  # First, second, and last channel
        
        for channel in channels_to_test:
            request_data = {
                "start_time": 0.0,
                "end_time": 0.1,
                "channel": channel,
                "data_type": "voltage"
            }
            
            response = client.post("/data", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["channel"] == channel
            assert len(data["data"]) == 250  # 0.1 second at 2500 Hz
    
    def test_data_types(self):
        """Test both voltage and current data types."""
        for data_type in ["voltage", "current"]:
            request_data = {
                "start_time": 0.0,
                "end_time": 0.1,
                "channel": 0,
                "data_type": data_type
            }
            
            response = client.post("/data", json=request_data)
            assert response.status_code == 200
            data = response.json()
            assert data["data_type"] == data_type
            assert data["unit"] == ("mV" if data_type == "voltage" else "pA")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])