# QueueCTL

A **CLI-based background job queue system** built in Python, using **SQLite** for persistent storage.  
QueueCTL lets you enqueue background jobs, run multiple workers concurrently, automatically retry failed jobs with exponential backoff, and manage a Dead Letter Queue (DLQ) — all through an installable command-line interface.

---

## 📦 Tech Stack
- **Language:** Python 3.12  
- **Database:** SQLite  
- **Libraries:** `argparse`, `threading`, `subprocess`, `sqlite3`, `datetime`  

---

## 🧠 Architecture Overview

| Module | Description |
|---------|--------------|
| `queuectl/core/db_manager.py` | Initializes and manages the SQLite database. |
| `queuectl/core/job_manager.py` | Handles job creation, insertion, and validation. |
| `queuectl/core/worker_manager.py` | Executes jobs, handles retries, and manages DLQ logic. |
| `queuectl/core/dlq_manager.py` | Lists and retries Dead Letter Queue jobs. |
| `queuectl/cli/commands.py` | CLI entrypoint that defines and routes all commands. |
| `pyproject.toml` | Defines CLI packaging configuration and the `queuectl` command entrypoint. |

---

## 🔄 Job Lifecycle

| State | Description |
|--------|-------------|
| `pending` | Waiting to be picked up by a worker |
| `processing` | Currently being executed |
| `completed` | Successfully executed |
| `failed` | Failed, will retry with backoff |
| `dead` | Permanently failed, moved to DLQ |

**Job structure:**
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
- Enqueue and execute background jobs through CLI  
- Multiple worker threads for parallel execution  
- Atomic job claiming (no duplicate processing)  
- Exponential retry backoff (`delay = base^attempts`)  
- Dead Letter Queue (DLQ) for permanently failed jobs  
- Persistent storage using SQLite  
- Graceful worker shutdown (`Ctrl+C`)  
- Global CLI installation via pip  

---

## 🚀 Installation (via pip)

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-username>/queuectl.git
cd queuectl
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # macOS / Linux
```

### 3️⃣ Install QueueCTL as a global CLI
```bash
pip install -e .
```

This makes the `queuectl` command globally available inside your environment.

### 4️⃣ Verify installation
```bash
queuectl --help
```

Expected output:
```
usage: queuectl [-h] {enqueue,worker,dlq} ...

QueueCTL — Lightweight Background Job Queue System

Commands:
  enqueue   Add a new job to the queue
  worker    Start worker(s) to process jobs
  dlq       View or retry jobs in the Dead Letter Queue
```

---

## 💻 CLI Usage

### Enqueue a Job
```bash
queuectl enqueue "{\"id\":\"job1\",\"command\":\"echo 'Hello QueueCTL'\"}"
```

### Start Workers
```bash
queuectl worker --count 2
```

### List Dead Letter Queue Jobs
```bash
queuectl dlq list
```

### Retry a DLQ Job
```bash
queuectl dlq retry job1
```

---

## 🧪 Testing Locally

### Reset and Test Workflow
```bash
python clear_jobs.py
python enqueue_test.py
queuectl worker --count 2
```

Run a second worker in another terminal:
```bash
queuectl worker --count 2
```

You’ll see output similar to:
```
Started 2 workers. Press Ctrl+C to stop.
[worker-1] running job1 -> echo 'Hello QueueCTL'
[worker-1] completed job job1
[worker-2] running fail1 -> exit 1
Retrying job fail1 in 2s (attempt 1)
Retrying job fail1 in 4s (attempt 2)
Job fail1 moved to DLQ
```

---

## 📊 Example Output

```
usage: queuectl [-h] {enqueue,worker,dlq} ...

QueueCTL — Lightweight Background Job Queue System

Commands:
  enqueue   Add a new job to the queue
  worker    Start worker(s) to process jobs
  dlq       View or retry jobs in the Dead Letter Queue

Use 'queuectl <command> --help' for more details.

Examples:
  queuectl enqueue "{\"id\":\"job1\",\"command\":\"echo 'Hello'\"}"
  queuectl worker --count 2
  queuectl dlq list
```

---

## 🧾 Design Notes
- SQLite chosen for simplicity and persistence across restarts  
- Each worker thread opens its own DB connection  
- Atomic transactions (`BEGIN IMMEDIATE`) prevent double-processing  
- Graceful shutdown ensures no half-completed jobs  
- CLI built using `argparse` for clarity and extensibility  
- Installable via `pyproject.toml` for modern pip compatibility  

---

## 🌟 Future Enhancements
- `status` command for job state counts  
- `list --state` filtering for specific jobs  
- Configurable retry base and max retries (`config set/get`)  
- Worker daemonization (`start` / `stop`)  
- Job timeout and priority queueing  
- Scheduled jobs with `run_at` field  
- Web dashboard for monitoring job stats  

---

## 🧑‍💻 Author
**Sahana B**  
Backend Developer Internship Assignment – QueueCTL  
PES University · 2025
