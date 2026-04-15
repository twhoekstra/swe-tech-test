# AGENTS.md

## Overview
- We are building a browser-based trace viewer designed for scientists working with electrophysiology recordings from nanopore experiments. 
- The primary goal: intuitive, real-time web browser interface for visualizing and navigating large datasets 
- Datasets have tens of millions of data points across 48 channels

## Structure
- A `.zarr` file with a test recording is found in `recordings/mock48_2500hz_1.5h.zarr`

## Dev environment tips
- Before running any code activate the virtual environment in `.venv`
- Use the Google Style Guide
- Only add inline comments for exceptional cases, generally use Google-style docstrings instead
- Use `uv add` to add packages
- Do not add fallback values or `try-except` blocks unless the operation is critical and the fallback is part of the intended design.
- Build the code such that when an error occurs, an explicit error is raised rather that it silently continues
- Always assume inputs in functions are valid unless specified otherwise
- Avoid default arguments unless they are part of the intended API

