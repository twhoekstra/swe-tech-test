# Real-Time Data Visualization System

A system for visualizing large time-series datasets with pan/zoom capabilities using FastAPI backend and React + Deck.gl frontend.

## System Overview

- **Backend**: FastAPI server serving downsampled data chunks from Zarr files
- **Frontend**: React application with Deck.gl for interactive visualization
- **Data**: 48-channel time-series data at 2.5kHz sampling rate (~657MB)

## Directory Structure

```
src/
├── backend/               # FastAPI server
│   ├── app/               # API routes and data processing
│   └── requirements.txt   # Python dependencies
│
├── frontend/              # React + Deck.gl client
│   ├── public/            # Static files
│   ├── src/               # React components
│   └── package.json       # Node dependencies
│
└── tests/                 # Pytest tests
    ├── test_backend.py     # Backend unit tests
    └── test_integration.py  # Integration tests
```

## Setup Instructions

### Prerequisites

- uv package manger
- Node.js 24+

### Backend Setup

1. **Install Python dependencies:**

```bash
uv venv
source .venv/bin/activate
uv sync
soruce 
```

2. **Start the FastAPI server:**

```bash
cd 
uvicorn src/backend/app.main:app --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node dependencies:**

```bash
cd src/frontend
npm install
```

2. **Start the React development server:**

```bash
npm start # Assuming still in frontend dir
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### GET `/metadata`

Returns metadata about the recording:

```json
{
  "device_id": "mock-48ch-001",
  "number_of_channels": 48,
  "sample_rate_hz": 2500.0,
  "duration_sec": 5400.0,
  "current_units": "pA",
  "current_range": 2.0,
  "current_scale": 0.06103515625,
  "current_offset": 0,
  "voltage_scale": 0.0625,
  "voltage_offset": 0
}
```

### POST `/data`

Fetch time-series data for a specific range:

**Request:**
```json
{
  "start_time": 0.0,
  "end_time": 1.0,
  "channel": 0,
  "data_type": "voltage"
}
```

**Response:**
```json
{
  "channel": 0,
  "start_time": 0.0,
  "end_time": 1.0,
  "sample_rate": 2500.0,
  "data": [0.123, 0.456, ...],
  "data_type": "voltage",
  "unit": "mV"
}
```

## Running Tests

### Backend Tests

```bash
cd /repo
python -m pytest tests/test_backend.py -v
```

### Integration Tests

```bash
cd /repo
python -m pytest tests/test_integration.py -v
```

### Run All Tests

```bash
cd /repo
python -m pytest tests/ -v
```

## Data Format

The system uses Zarr format for efficient storage and access of large time-series data:

- **File**: `recordings/mock48_2500hz_1.5h.zarr`
- **Size**: ~657MB
- **Structure**: 48 channels × 13.5M samples each
- **Sampling Rate**: 2.5kHz
- **Duration**: 1.5 hours

## Frontend Features

- **Interactive Visualization**: Deck.gl LineLayer for rendering traces
- **Real-time Updates**: requestAnimationFrame for smooth pan/zoom simulation
- **Data Fetching**: Axios for API communication
- **Viewport Management**: Simulated pan/zoom with continuous data fetching

## Development Notes

### Backend Performance

- Uses Zarr for efficient chunked reading of large datasets
- Converts raw ADC counts to physical units (mV/pA)
- Validates all input parameters
- Returns appropriate HTTP status codes

### Frontend Performance

- Deck.gl provides GPU-accelerated rendering
- Data is fetched in chunks based on viewport position
- requestAnimationFrame ensures smooth 60fps updates
- Loading states provide user feedback

## Troubleshooting

### Backend Issues

- **Module not found**: Run `pip install -r requirements.txt`
- **Data file not found**: Ensure `recordings/mock48_2500hz_1.5h.zarr` exists
- **Port conflict**: Change the port in the uvicorn command

### Frontend Issues

- **Dependency errors**: Run `npm install`
- **CORS issues**: Backend has CORS enabled for all origins
- **Connection refused**: Ensure backend is running on port 8000

## Future Improvements

- Add downsampling for overview visualization
- Implement caching for frequently accessed data ranges
- Add multi-channel display
- Implement proper authentication
- Add data export functionality
- Improve error handling and user feedback

## License

This project is for demonstration purposes only. The data is randomly generated mock data simulating real electrophysiology recordings.