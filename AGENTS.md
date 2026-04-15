# AGENTS.md

## Overview
- PoreFlow is a fast, simple, and flexible set of tools for analysing raw nanopore sequencing data.
- Features a Python API based on pandas.DataFrame for storing measurement, event, and step data.
- Has a fast step detection algorithm written in C++
- Support for .fast5 (HDF) files, along with .dat files from the UTube device which are converted
- Use of fast .fast5 I/O to reduce memory usage and allow persistence

## Dev environment tips
- Before running any code activate the virtual environment in `.venv`
- Run tests using `pytest`. If checking the whole repo, just run pytest without any arguments.
- Use the Google Style Guide
- Only add inline comments for exceptional cases, generally use Google-style docstrings instead
- Use `uv add` to add packages
- Check `src/poreflow/__init__.py` for often-used imports
- When writing scripts, use `import poreflow as pf`
- Add or update tests for the code you change, even if nobody asked
- Find the CI plan in .gitlab-ci.yml
- Lint using `ruff check --fix`
- Format using `ruff format`
- Do not add fallback values or `try-except` blocks unless the operation is critical and the fallback is part of the intended design.
- Build the code such that when an error occurs, an explicit error is raised rather that it silently continues
- Always assume inputs in functions are valid unless specified otherwise
- Avoid default arguments unless they are part of the intended API

## Plotly Dashboard tips
- The dashboard is created using plotly Dash 
- After creating a new callback, check if there are any duplicate outputs.


## About nanopore sequencing
- Nanopore sequencing involves threading DNA through a nanometre-scale pore embedded in a lipid bilayer separating two conductive wells 
- A positive voltage bias is applied over membrane, which drives an ionic current through the nanopore
- When unblocked, the pore has a so-called open-state current (IOS)
- The voltage electrophoretically draws negatively charged molecules, like DNA, into the pore
- As the DNA is drawn through the nanopore, the ionic current is partially bottlenecked by the passing DNA
- Each base in the DNA has a different contribution to the blockade, thus modulating the ionic current
- As the DNA translocates through the pore, it leads to an ionic current trace characteristic or "squiggle" for its sequence
- A base-calling algorithm uses the ionic current to predict the DNA sequence that caused it
- A motor enzyme, like the Hel308 DNA helicase is commonly used to control the translocation of the DNA
- We can also create a peptide-DNA conjugate which allows for peptide measurements.