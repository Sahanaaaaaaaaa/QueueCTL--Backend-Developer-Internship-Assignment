import subprocess, time, threading
from datetime import datetime, timedelta
from .db_manager import init_db

def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

stop_event = threading.Event()

def handle_failure(conn, job_id, attempts, max_retries, base=2):
    attempts += 1
    if attempts > max_retries:
        conn.execute("UPDATE jobs SET state='dead', updated_at=? WHERE id=?", (now_iso(), job_id))
        print(f"Job {job_id} moved to DLQ")
    else:
        delay = base ** attempts
        next_time = (datetime.utcnow() + timedelta(seconds=delay)).isoformat() + "Z"
        conn.execute(
            "UPDATE jobs SET state='failed', next_run_at=?, attempts=?, updated_at=? WHERE id=?",
            (next_time, attempts, now_iso(), job_id)
        )
        print(f"Retrying job {job_id} after {delay}s")
    conn.commit()

def worker_loop(conn, name):
    while not stop_event.is_set():
        # Select any job that’s pending or ready to retry (next_run_at <= now)
        job = conn.execute(
            """
            SELECT id, command, attempts, max_retries 
            FROM jobs 
            WHERE state IN ('pending', 'failed') 
            AND (next_run_at IS NULL OR next_run_at <= ?)
            LIMIT 1
            """,
            (now_iso(),)
        ).fetchone()

        if not job:
            time.sleep(1)
            continue

        job_id, command, attempts, max_retries = job
        print(f"[{name}] running {job_id} -> {command}")

        # Mark as processing
        conn.execute("UPDATE jobs SET state='processing' WHERE id=?", (job_id,))
        conn.commit()

        # Run the actual shell command
        result = subprocess.run(command, shell=True)

        if result.returncode == 0:
            # Success
            conn.execute("UPDATE jobs SET state='completed', updated_at=? WHERE id=?", (now_iso(), job_id))
            conn.commit()
            print(f"Job {job_id} completed successfully")
        else:
            # Failure: trigger retry or DLQ
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
        print("Worker stopped.")

if __name__ == "__main__":
    print("Worker manager started...")
    start_workers()

