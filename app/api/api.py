from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict
import os
import shutil
import uuid
import asyncio
import time
from app.api.state import jobs, job_queue, JobStatus, used_job_ids
from app.api.worker import worker
from app.utils.logger import Logger

FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../FILE_DIR'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../OUTPUT_DIR'))

app = FastAPI()

class CSVFileRequest(BaseModel):
    job_id: str
    # csv_file will be handled as UploadFile, not in the model

@app.on_event("startup")
async def startup_event():
    logger = Logger()
    logger.info("Starting up FastAPI app and launching workers...")
    for _ in range(4):  # Number of workers
        asyncio.create_task(worker(logger=logger))
    logger.info("All workers launched.")

@app.post("/process")
async def process_csv_endpoint(job_id: str, csv_file: UploadFile = File(...)):
    logger = Logger()
    file_path = os.path.join(FILE_DIR, csv_file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(csv_file.file, buffer)
    logger.info(f"Received file {csv_file.filename} for job {job_id}, saved to {file_path}")
    if not os.path.exists(file_path):
        logger.error(f"CSV file {file_path} not found after upload for job {job_id}")
        raise HTTPException(status_code=400, detail="CSV file not found after upload.")
    # Enforce job_id uniqueness even after completion
    if job_id in used_job_ids:
        logger.error(f"Job ID {job_id} has been used before.")
        raise HTTPException(status_code=400, detail="Job ID has been used before and cannot be reused.")
    used_job_ids.add(job_id)
    if job_id in jobs:
        logger.error(f"Job ID {job_id} already exists.")
        raise HTTPException(status_code=400, detail="Job ID already exists.")
    jobs[job_id] = {"status": JobStatus.WAITING, "result": None, "error": None, "processing_time": {"start": None, "end": None}}
    await job_queue.put({"job_id": job_id, "file_path": file_path})
    logger.info(f"Job {job_id} queued for processing.")
    return {"job_id": job_id, "status": JobStatus.WAITING}

@app.get("/job_status/{job_id}")
async def job_status(job_id: str):
    logger = Logger()
    job = jobs.get(job_id)
    if not job:
        logger.error(f"Job {job_id} not found in status query.")
        raise HTTPException(status_code=404, detail="Job not found.")
    # Calculate processing_time in seconds if possible
    processing_time = None
    pt = job.get("processing_time")
    if pt and pt["start"]:
        end = pt["end"] if pt["end"] else time.time()
        processing_time = end - pt["start"]
    # Add download links for finished jobs with result files
    download_url = None
    direct_download_url = None
    if job.get("status") == JobStatus.FINISHED and job.get("result"):
        file_path = job.get("result")
        file_name = os.path.basename(file_path)
        download_url = f"/download/{job_id}/{file_name}"
        direct_download_url = f"/download/{job_id}"
    logger.info(f"Status for job {job_id} queried: {job}")
    return {**job, "processing_time": processing_time, "download_url": download_url, "direct_download_url": direct_download_url}

@app.get("/download/{job_id}")
async def download_file_by_id(job_id: str):
    logger = Logger()
    job = jobs.get(job_id)
    if not job:
        logger.error(f"Job {job_id} not found in download request.")
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.get("status") != JobStatus.FINISHED or not job.get("result"):
        logger.error(f"Job {job_id} is not finished or has no result for download.")
        raise HTTPException(status_code=400, detail="Job not finished or has no result file.")
    file_path = job.get("result")
    if not os.path.exists(file_path):
        logger.error(f"Result file {file_path} not found for job {job_id}.")
        raise HTTPException(status_code=404, detail="Result file not found.")
    file_name = os.path.basename(file_path)
    logger.info(f"Serving download for job {job_id}, file: {file_path}")
    return FileResponse(path=file_path, filename=file_name, media_type="text/csv")
