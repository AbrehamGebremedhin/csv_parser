from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict
import os
import shutil
import uuid
import asyncio
import time
from app.api.state import jobs, job_queue, JobStatus
from app.api.worker import worker
from app.utils.logger import Logger

FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../FILE_DIR'))

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
    logger.info(f"Status for job {job_id} queried: {job}")
    return {**job, "processing_time": processing_time}
