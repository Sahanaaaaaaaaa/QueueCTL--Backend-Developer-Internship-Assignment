import sqlite3
import os

DB_PATH = os.path.join("data", "queuectl.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        command TEXT,
        state TEXT,
        attempts INTEGER,
        max_retries INTEGER,
        created_at TEXT,
        updated_at TEXT,
        next_run_at TEXT
    )
    """)
    conn.commit()
    return conn
