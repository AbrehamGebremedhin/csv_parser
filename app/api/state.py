# Global state for jobs and queue
import asyncio
from typing import Dict, Any
from enum import Enum

jobs: Dict[str, Dict[str, Any]] = {}
job_queue: asyncio.Queue = asyncio.Queue()
# Track all used job IDs to prevent reuse
used_job_ids = set()

class JobStatus(str, Enum):
    WAITING = "WAITING"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"