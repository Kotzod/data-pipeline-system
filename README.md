# Data Pipeline Final Project

This repository contains the final data pipeline project in:

- `Final_project_Oliver_Chandler/`

## What This Project Does

The pipeline fetches football match data from external APIs, stores and processes
it with Pandas and SQLite, and generates match outcome predictions.

## Tech Stack

- Python
- Pandas
- NumPy
- scikit-learn
- SciPy
- SQLite
- Requests

## Quick Start

1. Go to the project folder:
   - `cd Final_project_Oliver_Chandler`
2. Create and activate a virtual environment (recommended).
3. Install dependencies:
   - `pip install pandas numpy scikit-learn scipy requests`
4. Create a `.env` file and define API keys used by `main.py`:
   - `FOOTBALL_DATA_KEY=...`
   - `API_FOOTBALL_KEY=...`
5. Run the pipeline:
   - `python main.py`

## Optional Viewer Scripts

- `python results_viewer.py`
- `python predictions_viewer.py`
