# Real-Time Data Visualization System

Prototype for visualizing large time-series datasets with pan/zoom capabilities using FastAPI backend and React + D3.js frontend.

## System Overview

- **Backend**: FastAPI server serving downsampled data chunks from Zarr files
- **Frontend**: Next.js application with D3.js for interactive visualization
- **Data**: 48-channel time-series data at 2.5kHz sampling rate (~657MB)

## Directory Structure

```
src/
├── backend/               # FastAPI server
│   └── app/               # API routes and data processing
│  
├── frontend/              # React + Deck.gl client
│   ├── public/            # Static files
│   ├── src/               # React components
│   └── package.json       # Node dependencies
│
└── tests/                 # Pytest tests
    └── test_backend.py     # Backend unit tests
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
```

2. **Start the FastAPI server:**

```bash
serve
```
The server will be available at `http://localhost:8000`

### Frontend Setup

1. **Install Node dependencies:**

```bash
cd src/frontend
npm install
```

2. **Start the Next.js development server:**

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Running Tests

### Backend Tests

```bash
pytest
```

## Features


### Backend
- **Data serving API**: FastAPI for selecting file and retrieving data + metadata

Not implemented yet:
- **Downscaling**: No pre-calculation of downscaled versions of data
- **Optimization**: No optimization of voltage data (identical per channel, stored in multiple.)


### Frontend

- **Next.js App Router**: Modern Next.js structure with app router
- **Interactive Visualization**: D3.js for rendering traces
- **Data Fetching**: Axios for API communication

Not implemented yet:
- **Viewport Management**: Simulated pan/zoom with continuous data fetching

## Development Notes

### Backend

- ADC counts are served when data is requested. Metadata contains scaling to conver to physical units (mV/pA) on client side

### Frontend

- **Dynamic Components**: D3.js component is dynamic to avoid server-side pre-rendering issues

## Future Improvements

- Add downsampling for overview visualization
- Dynamic data fetching when panning/zooming
- Implement caching for frequently accessed data ranges
- Add multi-channel display
- Add data export functionality
- Improve error handling and user feedback

## License

**MIT License** - This project is for prototyping/demonstration purposes only.

Copyright (c) 2026 - All rights reserved.