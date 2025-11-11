from queuectl.core.db_manager import init_db

def clear_jobs():
    conn = init_db()
    deleted = conn.execute("DELETE FROM jobs").rowcount
    conn.commit()
    print(f"Cleared {deleted} jobs from the queue database!")

if __name__ == "__main__":
    clear_jobs()