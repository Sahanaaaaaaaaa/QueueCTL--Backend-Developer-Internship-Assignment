import subprocess, time, threading
from datetime import datetime
from .db_manager import init_db

def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

stop_event = threading.Event()

def worker_loop(conn, name):
    while not stop_event.is_set():
        job = conn.execute("SELECT id,command FROM jobs WHERE state='pending' LIMIT 1").fetchone()
        if not job:
            time.sleep(1)
            continue
        job_id, command = job
        print(f"[{name}] running {job_id} -> {command}")
        conn.execute("UPDATE jobs SET state='processing' WHERE id=?", (job_id,))
        conn.commit()
        result = subprocess.run(command, shell=True)
        state = "completed" if result.returncode == 0 else "failed"
        conn.execute("UPDATE jobs SET state=?, updated_at=? WHERE id=?", (state, now_iso(), job_id))
        conn.commit()
        print(f"[{name}] finished job {job_id} -> {state}")

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
