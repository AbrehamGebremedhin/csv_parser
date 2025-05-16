# Global state for jobs and queue
import asyncio
from typing import Dict, Any
from enum import Enum

jobs: Dict[str, Dict[str, Any]] = {}
job_queue: asyncio.Queue = asyncio.Queue()

class JobStatus(str, Enum):
    WAITING = "WAITING"
    STARTED = "STARTED"
    FINISHED = "FINISHED"
    FAILED = "FAILED"