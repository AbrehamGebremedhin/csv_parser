from app.api.state import jobs, job_queue, JobStatus
from app.service.reader_service import AsyncCSVReaderService
import os
from app.utils.logger import Logger
import time
import polars as pl

async def worker(logger=None):
    logger = logger or Logger()
    while True:
        job = await job_queue.get()
        job_id = job["job_id"]
        file_path = job["file_path"]
        try:
            logger.info(f"Worker started job {job_id} for file {file_path}")
            # Validate CSV columns before processing
            required_columns = {"Department Name", "Date", "Number of Sales"}
            try:
                df = pl.read_csv(file_path, n_rows=0)
                csv_columns = set(df.columns)
                missing = required_columns - csv_columns
                if missing:
                    raise ValueError(f"Missing required columns: {', '.join(missing)}")
            except Exception as e:
                logger.error(f"Validation failed for job {job_id}: {e}")
                jobs[job_id]["status"] = JobStatus.FAILED
                jobs[job_id]["error"] = f"CSV validation error: {e}"
                continue
            jobs[job_id]["status"] = JobStatus.STARTED
            jobs[job_id]["processing_time"] = {"start": time.time(), "end": None}
            service = AsyncCSVReaderService(logger=logger)
            result_path = await service.aggregate_sales_by_department(file_path, os.path.dirname(file_path))
            jobs[job_id]["status"] = JobStatus.FINISHED
            jobs[job_id]["result"] = result_path
            jobs[job_id]["processing_time"]["end"] = time.time()
            logger.info(f"Worker finished job {job_id}, result at {result_path}")
        except Exception as e:
            jobs[job_id]["status"] = JobStatus.FAILED
            jobs[job_id]["error"] = str(e)
            if "processing_time" in jobs[job_id] and jobs[job_id]["processing_time"]["end"] is None:
                jobs[job_id]["processing_time"]["end"] = time.time()
            logger.error(f"Worker failed job {job_id}: {e}")
        finally:
            job_queue.task_done()
            logger.debug(f"Worker marked job {job_id} as done in queue.")