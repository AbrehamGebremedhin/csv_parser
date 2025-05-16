import os
import io
import shutil
import tempfile
import pytest
from fastapi.testclient import TestClient
from app.api.api import app
from app.api.state import jobs, used_job_ids

client = TestClient(app)

def setup_function():
    jobs.clear()
    used_job_ids.clear()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_and_job_status():
    # Create a temp CSV file
    csv_content = b"col1,col2\n1,2\n3,4\n"
    job_id = "testjob1"
    files = {"csv_file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    response = client.post(f"/process?job_id={job_id}", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert data["status"] == "WAITING"

    # Check job status
    response = client.get(f"/job_status/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "WAITING"
    # The job_status endpoint does not return job_id in the response
    assert "processing_time" in data
    assert data["download_url"] is None
    assert data["direct_download_url"] is None


def test_process_duplicate_job_id():
    job_id = "dupjob"
    csv_content = b"a,b\n1,2\n"
    files = {"csv_file": ("dup.csv", io.BytesIO(csv_content), "text/csv")}
    # First submission
    response = client.post(f"/process?job_id={job_id}", files=files)
    assert response.status_code == 200
    # Second submission with same job_id
    response = client.post(f"/process?job_id={job_id}", files=files)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"] or "has been used before" in response.json()["detail"]


def test_job_status_not_found():
    response = client.get("/job_status/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found."


def test_download_file_by_id_not_found():
    response = client.get("/download/nonexistent")
    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found."


def test_download_file_by_id_not_finished():
    job_id = "unfinished"
    jobs[job_id] = {"status": "waiting", "result": None, "error": None, "processing_time": {"start": None, "end": None}}
    response = client.get(f"/download/{job_id}")
    assert response.status_code == 400
    assert "not finished" in response.json()["detail"]


def test_download_file_by_id_file_missing(tmp_path):
    job_id = "finished_missing"
    fake_path = tmp_path / "missing.csv"
    jobs[job_id] = {"status": "FINISHED", "result": str(fake_path), "error": None, "processing_time": {"start": None, "end": None}}
    response = client.get(f"/download/{job_id}")
    assert response.status_code == 404
    assert "Result file not found" in response.json()["detail"]


def test_download_file_by_id_success(tmp_path):
    job_id = "finished_success"
    file_path = tmp_path / "result.csv"
    file_path.write_text("a,b\n1,2\n")
    jobs[job_id] = {"status": "FINISHED", "result": str(file_path), "error": None, "processing_time": {"start": None, "end": None}}
    response = client.get(f"/download/{job_id}")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert response.content.startswith(b"a,b")
