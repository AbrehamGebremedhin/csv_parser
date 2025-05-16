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
   git clone <your-repo-url>
   cd csv_parser
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

### Running the Server

Start the API server with:

```sh
python main.py
```

The API will be available at `http://localhost:8000`.

### Interactive API Docs

Once the server is running, access the interactive documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

> **Note:** The following is a general overview. For detailed, interactive documentation, visit `/docs` when the server is running.

- **Upload CSV**: `POST /upload`
- **Parse CSV**: `POST /parse`
- **Get State**: `GET /state`
- **Other endpoints**: See `/docs` for the full list.

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

## Testing

- Tests are located in the `tests/` directory.
- Run tests with:
  ```sh
  pytest
  ```
