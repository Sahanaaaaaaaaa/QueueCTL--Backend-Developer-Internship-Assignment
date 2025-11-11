import json
from datetime import datetime

def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def enqueue_job(conn, job_json):
    job = json.loads(job_json)
    job_id = job.get("id")
    command = job.get("command")
    created = now_iso()
    conn.execute(
        "INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?)",
        (job_id, command, "pending", 0, job.get("max_retries", 3),
         created, created, created)
    )
    conn.commit()
    print(f"Job {job_id} enqueued")
