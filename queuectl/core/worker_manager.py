import subprocess
import time
import threading
from datetime import datetime, timedelta
from .db_manager import init_db

stop_event = threading.Event()

def now_iso():
    return datetime.now().replace(microsecond=0).isoformat() + "Z"

def claim_one_job(conn):
    cur = conn.cursor()
    try:
        cur.execute("BEGIN IMMEDIATE")
        row = cur.execute(
            """
            SELECT id, command, attempts, max_retries
            FROM jobs
            WHERE state='pending'
              AND (next_run_at IS NULL OR next_run_at <= ?)
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (now_iso(),),
        ).fetchone()

        if not row:
            conn.rollback()
            return None

        job_id, command, attempts, max_retries = row
        cur.execute(
            "UPDATE jobs SET state='processing', updated_at=? WHERE id=?",
            (now_iso(), job_id),
        )
        conn.commit()
        return {"id": job_id, "command": command, "attempts": attempts, "max_retries": max_retries}

    except Exception as e:
        conn.rollback()
        print(f"claim_one_job error: {e}")
        return None

def handle_failure(conn, job_id, attempts, max_retries, base=2):
    attempts += 1
    if attempts > max_retries:
        conn.execute(
            "UPDATE jobs SET state='dead', updated_at=? WHERE id=?",
            (now_iso(), job_id),
        )
        conn.commit()
        print(f"Job {job_id} moved to DLQ")
        return

    delay = base ** attempts
    next_run = (datetime.utcnow() + timedelta(seconds=delay)).isoformat() + "Z"
    conn.execute(
        "UPDATE jobs SET state='pending', next_run_at=?, attempts=?, updated_at=? WHERE id=?",
        (next_run, attempts, now_iso(), job_id),
    )
    conn.commit()
    print(f"Retrying job {job_id} in {delay}s (attempt {attempts})")

def worker_loop(conn, name):
    while not stop_event.is_set():
        job = claim_one_job(conn)
        if not job:
            time.sleep(1)
            continue

        job_id = job["id"]
        command = job["command"]
        attempts = job["attempts"]
        max_retries = job["max_retries"]

        print(f"[{name}] running {job_id} -> {command}")
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            conn.execute(
                "UPDATE jobs SET state='completed', updated_at=? WHERE id=?",
                (now_iso(), job_id),
            )
            conn.commit()
            print(f"[{name}] completed job {job_id}")
        else:
            print(f"[{name}] failed job {job_id}")
            handle_failure(conn, job_id, attempts, max_retries)

def start_workers(count=1):
    conn = init_db()
    threads = []
    for i in range(count):
        t = threading.Thread(target=worker_loop, args=(conn, f"worker-{i+1}"), daemon=True)
        threads.append(t)
        t.start()

    print(f"Started {count} workers. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_event.set()
        print("Stopping workers gracefully...")

if __name__ == "__main__":
    start_workers()
