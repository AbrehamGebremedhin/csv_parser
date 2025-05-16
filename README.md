# CSV Parser API Documentation

Welcome to the CSV Parser API! This project provides a FastAPI-based backend for parsing, processing, and managing CSV files. Below you'll find details on how to use, run, and extend the API.

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Development](#development)
- [Testing](#testing)
- [License](#license)

---

## Overview

This project is a backend service for parsing and processing CSV files. It is built using FastAPI and Uvicorn, and is organized for easy extension and testing.

## Getting Started

### Prerequisites

- Python 3.12+
- pip (Python package manager)

### Installation

1. Clone the repository:
   ```sh
   https://github.com/AbrehamGebremedhin/csv_parser
   cd csv_parser
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Server

Start the API server with:

```sh
uvicorn app.api.api:app --reload
```

The API will be available at `http://localhost:8000`.

### Interactive API Docs

Once the server is running, access the interactive documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

**For a full list of endpoints, request/response schemas, and try-it-out features, see the [Swagger UI](http://localhost:8000/docs) when the server is running.**

## Project Structure

```
main.py                # Entry point for the API server
app/
  api/                 # API routes and logic
  service/             # Business logic and services
  utils/               # Utility modules (CSV generation, logging, etc.)
FILE_DIR/              # Input files
OUTPUT_DIR/            # Output files
sales_data/            # Example CSV files
```

## Development

- Use `uvicorn` for local development with auto-reload:
  ```sh
  uvicorn app.api.api:app --reload
  ```
- Update or add endpoints in `app/api/api.py`.
- Add business logic in `app/service/`.

## Running and Testing the Solution on Windows

### Running the Server

1. Install dependencies:
   ```pwsh
   pip install -r requirements.txt
   ```
2. Start the API server:
   ```pwsh
   uvicorn app.api.api:app --reload
   ```
   The API will be available at [http://localhost:8000](http://localhost:8000).

### Running Tests

1. Make sure you are in the project root directory.
2. Run all tests:
   ```pwsh
   pytest
   ```
   This will execute all tests in the `tests/` directory and verify the CSV parsing and aggregation logic.

## Testing

- Tests are located in the `tests/` directory.
- Run tests with:
  ```sh
  pytest
  ```

## Test Coverage

Test coverage is provided for the core API endpoints, CSV parsing and aggregation logic, and utility modules. The tests are located in the `tests/` directory and include:

- **API Endpoints:**
  - Health check (`/health`)
  - CSV processing and job submission (`/process`)
  - Duplicate job ID handling
  - Job status retrieval (`/job_status/{job_id}`), including not-found cases
  - Downloading results (`/download/{job_id}`), including not-found, not-finished, and file-missing scenarios
- **CSV Aggregation:**
  - Verifies correct aggregation by department, including handling of empty and malformed values
  - Ensures output files are created and contain the expected columns and results
- **Utility Modules:**
  - Tests for CSV generation and logging utilities

To check test coverage, you can use the `pytest-cov` plugin:

1. Install the plugin (if not already installed):
   ```pwsh
   pip install pytest-cov
   ```
2. Run tests with coverage:
   ```pwsh
   pytest --cov=app --cov-report=term-missing
   ```
   This will display a coverage report in the terminal, showing which lines of code are covered by tests and which are missing coverage.

---

## Algorithm Explanation and Memory Efficiency

The core CSV parsing and aggregation logic is implemented in `app/service/reader_service.py` using the Polars library. The algorithm works as follows:

- Reads the CSV file in a streaming (lazy) fashion, processing one row at a time.
- Cleans and converts the 'Number of Sales' column to integers, handling empty or malformed values.
- Groups the data by 'Department Name' and sums the sales for each department.
- Writes the aggregated results to a new CSV file in the `OUTPUT_DIR`.

**Memory Efficiency:**

- The use of Polars' lazy evaluation and streaming ensures that only a small portion of the file is loaded into memory at any time.
- This allows the application to efficiently process large CSV files without high memory usage.

---

## Computational Complexity

- **Time Complexity:** O(n), where n is the number of rows in the CSV file. Each row is read, cleaned, and aggregated once.
- **Space Complexity:** O(k), where k is the number of unique departments (groups). Only the aggregation results and a small buffer are kept in memory.
