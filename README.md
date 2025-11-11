# QueueCTL

A CLI-based background job queue system built in **Python** using **SQLite** for persistent storage.

---

## 📦 Tech Stack
- Python 3.12  
- SQLite  
- Argparse  
- Threading  
- Subprocess  
- Datetime  

---

## 🧠 Architecture

| Module | Description |
|---------|--------------|
| `queuectl/core/db_manager.py` | Initializes and manages the SQLite database. |
| `queuectl/core/job_manager.py` | Handles job creation and enqueue logic. |
| `queuectl/core/worker_manager.py` | Executes jobs, handles retries, and manages the DLQ. |
| `queuectl/core/dlq_manager.py` | Lists and retries DLQ jobs. |
| `queuectl/cli/commands.py` | Command-line interface for managing the queue. |
| `main.py` | CLI entry point. |

---

## Job Lifecycle

| State | Description |
|--------|-------------|
| `pending` | Waiting to be picked up by a worker |
| `processing` | Currently being executed |
| `completed` | Finished successfully |
| `failed` | Failed but retryable |
| `dead` | Permanently failed, moved to DLQ |

```json
{
  "id": "unique-job-id",
  "command": "echo 'Hello World'",
  "state": "pending",
  "attempts": 0,
  "max_retries": 3,
  "created_at": "2025-11-11T10:30:00Z",
  "updated_at": "2025-11-11T10:30:00Z"
}
```

---

## ⚙️ Features
- Enqueue and execute background jobs  
- Multiple worker threads  
- Atomic job claiming with transaction locks  
- Exponential retry backoff (`delay = base^attempts`)  
- Dead Letter Queue (DLQ) for failed jobs  
- Persistent storage with SQLite  
- Graceful shutdown  

---

## 🚀 Setup

```bash
git clone https://github.com/<your-username>/queuectl.git
cd queuectl
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Initialize the database:
```bash
python
>>> from queuectl.core.db_manager import init_db
>>> init_db()
>>> exit()
```

---

## 💻 CLI Commands

### Enqueue a job
```bash
python main.py enqueue "{\"id\":\"job1\",\"command\":\"echo 'Hello World'\"}"
```

### Start worker(s)
```bash
python main.py worker --count 2
```

### List DLQ jobs
```bash
python main.py dlq list
```

### Retry DLQ job
```bash
python main.py dlq retry job1
```

---

## 🧪 Testing

```bash
python clear_jobs.py
python enqueue_test.py
python enqueue_test.py
python -u -m queuectl.core.worker_manager
```

Run a second worker in another terminal:
```bash
python -u -m queuectl.core.worker_manager
```

---

## 📊 Sample Output

```
Started 2 workers. Press Ctrl+C to stop.
[worker-1] running job1 -> echo 'Hello World'
[worker-1] completed job job1
[worker-2] running fail1 -> exit 1
Retrying job fail1 in 2s (attempt 1)
Job fail1 moved to DLQ
```

---

## 🧾 Design Notes
- SQLite ensures persistence and simplicity  
- Each worker opens its own DB connection  
- Atomic `BEGIN IMMEDIATE` transactions prevent duplicate claims  
- Graceful shutdown via `Ctrl+C`  

---

## 🌟 Future Enhancements
- `status` command for job state counts  
- `list --state` for job filtering  
- Configurable retry base and max retries (`config set/get`)  
- Worker daemonization (`start` / `stop`)  
- Scheduled and delayed jobs  
- Job priority queueing  
- Web dashboard for monitoring  

---

## 🧑‍💻 Author
**Sahana B**  
Backend Developer Internship Assignment – QueueCTL  
PES University · 2025
