import asyncio
from app.api.state import jobs, job_queue
from app.api.worker import worker

async def run_workers(num_workers: int = 4):
    for _ in range(num_workers):
        asyncio.create_task(worker())
    await job_queue.join()  # Wait for all jobs to be processed

# Optional: CLI entry point for running workers directly
if __name__ == "__main__":
    asyncio.run(run_workers())