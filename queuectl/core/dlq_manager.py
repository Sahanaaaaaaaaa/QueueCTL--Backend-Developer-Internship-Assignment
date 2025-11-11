from .db_manager import init_db

def list_dlq(conn):
    print("DEBUG: list_dlq() called")          # <-- temporary debug line
    rows = conn.execute(
        "SELECT id, command, attempts, max_retries, updated_at FROM jobs WHERE state='dead'"
    ).fetchall()
    if not rows:
        print("DLQ is empty!")
        return
    print("Dead Letter Queue Jobs:")
    for r in rows:
        print(f"  ID: {r[0]}, Attempts: {r[2]}, Max: {r[3]}, Last Updated: {r[4]}")

def retry_dlq(conn, job_id):
    row = conn.execute("SELECT id FROM jobs WHERE id=? AND state='dead'", (job_id,)).fetchone()
    if not row:
        print(f"No DLQ job found with ID '{job_id}'")
        return
    conn.execute(
        "UPDATE jobs SET state='pending', attempts=0, next_run_at=datetime('now') WHERE id=?",
        (job_id,),
    )
    conn.commit()
    print(f"Moved DLQ job '{job_id}' back to pending")
