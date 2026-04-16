#!/usr/bin/env python3
"""FastAPI backend for serving time-series data from Zarr files."""

import zarr
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

app = FastAPI(title="Time-Series Data API")

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATA_FILE = "./recordings/mock48_2500hz_1.5h.zarr"

class DataRequest(BaseModel):
    start_time: float  # in seconds
    end_time: float  # in seconds
    channel: int = 0  # channel index (0-47)
    data_type: str = "voltage"  # 'voltage' or 'current'

class MetadataResponse(BaseModel):
    device_id: str
    number_of_channels: int
    sample_rate_hz: float
    duration_sec: float
    current_units: str
    current_range: float
    current_scale: float
    current_offset: int
    voltage_scale: float
    voltage_offset: int

def get_zarr_store():
    """Open the Zarr store."""
    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")
    return zarr.open(DATA_FILE, mode="r")

def time_to_samples(start_time: float, end_time: float, sample_rate: float) -> tuple:
    """Convert time range to sample indices."""
    start_sample = int(start_time * sample_rate)
    end_sample = int(end_time * sample_rate)
    return start_sample, end_sample

@app.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    """Get metadata about the recording."""
    try:
        store = get_zarr_store()
        
        return MetadataResponse(
            device_id=store.attrs.get("device_id", "unknown"),
            number_of_channels=store.attrs.get("number_of_channels", 0),
            sample_rate_hz=store.attrs.get("sample_rate_hz", 0.0),
            duration_sec=store.attrs.get("duration_sec", 0.0),
            current_units=store.attrs.get("current_units", ""),
            current_range=store.attrs.get("current_range", 0.0),
            current_scale=store.attrs.get("current_scale", 0.0),
            current_offset=store.attrs.get("current_offset", 0),
            voltage_scale=store.attrs.get("voltage_scale", 0.0),
            voltage_offset=store.attrs.get("voltage_offset", 0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data")
async def get_data(request: DataRequest):
    """Get time-series data for a specific time range and channel."""
    try:
        store = get_zarr_store()
    except IOError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Validate channel
    num_channels = store.attrs.get("number_of_channels", 48)
    if request.channel < 0 or request.channel >= num_channels:
        raise HTTPException(status_code=400, detail=f"Channel must be between 0 and {num_channels-1}")

    # Validate time range
    duration = store.attrs.get("duration_sec", 5400.0)
    if request.start_time < 0 or request.end_time > duration:
        raise HTTPException(status_code=400, detail=f"Time range must be within [0, {duration}] seconds")
    if request.start_time >= request.end_time:
        raise HTTPException(status_code=400, detail="start_time must be less than end_time")

    # Convert time to samples
    sample_rate = store.attrs.get("sample_rate_hz", 2500.0)
    start_sample, end_sample = time_to_samples(request.start_time, request.end_time, sample_rate)

    # Read data
    if request.data_type == "voltage":
        data = store["voltage_data"][request.channel, start_sample:end_sample]
        scale = store.attrs.get("voltage_scale", 0.0625)
    elif request.data_type == "current":
        data = store["current_data"][request.channel, start_sample:end_sample]
        scale = store.attrs.get("current_scale", 0.06103515625)
    else:
        raise HTTPException(status_code=400, detail="data_type must be 'voltage' or 'current'")

    # Convert to physical units
    data_physical = data.astype("float32") * scale

    return {
        "channel": request.channel,
        "start_time": request.start_time,
        "end_time": request.end_time,
        "sample_rate": sample_rate,
        "data": data_physical.tolist(),
        "data_type": request.data_type,
        "unit": "mV" if request.data_type == "voltage" else "pA"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)