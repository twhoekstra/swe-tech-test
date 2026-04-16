#!/usr/bin/env python3
"""FastAPI backend for serving time-series data from Zarr files."""
import pathlib

import zarr

from zarr.core.group import Group

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
from http import HTTPStatus
from contextlib import asynccontextmanager

# Configuration
RECORDINGS_FOLDER_PATH = pathlib.Path("./recordings") # Bit hacky for now but fine

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application state on startup and cleanup on shutdown."""
    app.state.store = None
    
    yield

    del app.state.store

app = FastAPI(title="Time-Series Data API", lifespan=lifespan)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FileRequest(BaseModel):
    filename: str  # name of the zarr file to open

class DataRequest(BaseModel):
    start_time: float  # in seconds
    end_time: float  # in seconds
    channel: int = 0  # channel index (0-47)
    data_type: str = "current"  # 'voltage' or 'current'

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


def get_store(app_state) -> Group:
    """Get the current Zarr store, opening default if none is set."""
    return app_state.store

def time_to_samples(start_time: float, end_time: float, sample_rate: float) -> tuple:
    """Convert time range to sample indices."""
    start_sample = int(start_time * sample_rate)
    end_sample = int(end_time * sample_rate)
    return start_sample, end_sample

@app.post("/set_file")
async def set_file(request: FileRequest):
    """Set the file to use for data operations."""
    file_path = request.filename
    path = RECORDINGS_FOLDER_PATH / file_path
    
    if not path.exists():
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"File {path} does not exist")

    try:
        z = zarr.open_group(str(path), mode="r")
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    app.state.store = z

    return {
        "message": f"File set to {path}",
        "file_path": str(path),
        "status": "success"
    }


@app.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    """Get metadata about the recording."""
    try:
        store = get_store(app.state)
    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
        
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


@app.post("/data")
async def get_data(request: DataRequest):
    """Get time-series data for a specific time range and channel."""
    try:
        store = get_store(app.state)
    except IOError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))

    # Validate channel
    num_channels = store.attrs.get("number_of_channels", 48)
    if request.channel < 0 or request.channel >= num_channels:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Channel must be between 0 and {num_channels-1}")

    # Validate time range
    duration = store.attrs.get("duration_sec", 5400.0)
    if request.start_time < 0 or request.end_time > duration:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=f"Time range must be within [0, {duration}] seconds")
    if request.start_time >= request.end_time:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="start_time must be less than end_time")

    # Convert time to samples
    sample_rate = store.attrs.get("sample_rate_hz", 2500.0)
    start_sample, end_sample = time_to_samples(request.start_time, request.end_time, sample_rate)

    # Read data



    if request.data_type == "voltage":
        data_range = 1 / store.attrs["voltage_scale"]# Voltage doesn't have a range in the data file for some reason
    elif request.data_type == "current":
        data_range = store.attrs["current_range"]
    else:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="data_type must be 'voltage' or 'current'")

    data = store[f"{request.data_type}_data"][request.channel, start_sample:end_sample]
    data_offset = store.attrs[f"{request.data_type}_offset"]


    return {
        "channel": request.channel,
        "start_time": request.start_time,
        "end_time": request.end_time,
        "sample_rate": sample_rate,
        "data": data,
        "data_type": request.data_type,
        "data_range": data_range,
        "data_offset": data_offset,
        "unit": "mV" if request.data_type == "voltage" else "pA"
    }


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()