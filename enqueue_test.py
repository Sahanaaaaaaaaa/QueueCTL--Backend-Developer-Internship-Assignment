from queuectl.core.db_manager import init_db
from queuectl.core.job_manager import enqueue_job

conn = init_db()
enqueue_job(conn, '{"id":"fail1","command":"exit 1","max_retries":2}')
