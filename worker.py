import os
import sys
import logging
from rq import Connection
from rq.worker import SimpleWorker
from redis import Redis
import time
import traceback

# Add project root to path so imports work correctly
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

from config.config import config_properties

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("worker.log")
    ]
)

logger = logging.getLogger(__name__)

# Windows-compatible worker class that doesn't use fork() or SIGALRM
class WindowsWorker(SimpleWorker):
    def execute_job(self, job, queue):
        """Execute job in same thread/process, no forking."""
        self.prepare_job_execution(job)
        
        job_started = time.time()
        timeout = job.timeout or self.default_worker_ttl
        
        try:
            job.perform()
            registry = self.get_started_job_registry(queue.name)
            self.handle_job_success(job=job, queue=queue, started_job_registry=registry)
        except Exception as e:
            exc_string = self.get_safe_exception_string(e)
            self.handle_job_failure(job=job, exc_string=exc_string)
            self.handle_exception(job, *sys.exc_info())
            
        # Periodic check for timeout
        if time.time() - job_started > timeout:
            self.handle_job_failure(job=job, exc_string="Job exceeded timeout")
            
        self.handle_job_after_run(job=job, queue=queue)
    
    def get_safe_exception_string(self, exception):
        """Convert exception to a safe string representation."""
        try:
            return "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        except Exception:
            return str(exception)

# Redis connection parameters
redis_params = {
    'host': config_properties.REDIS_HOST,
    'port': config_properties.REDIS_PORT,
    'db': config_properties.REDIS_DB,
}

# Only add password if it's set
if config_properties.REDIS_PASSWORD:
    redis_params['password'] = config_properties.REDIS_PASSWORD

# Create Redis connection
redis_conn = Redis(**redis_params)

def main():
    """Start the worker to process jobs from the queue."""
    try:
        logger.info(f"Starting worker for queue: {config_properties.REDIS_QUEUE_NAME}")
        
        with Connection(redis_conn):
            # Use WindowsWorker which is compatible with Windows instead of SimpleWorker
            worker = WindowsWorker([config_properties.REDIS_QUEUE_NAME])
            worker.work(with_scheduler=True)
    
    except Exception as e:
        logger.error(f"Worker error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 