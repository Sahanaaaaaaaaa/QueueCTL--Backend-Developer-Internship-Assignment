import argparse
from queuectl.core.db_manager import init_db
from queuectl.core.job_manager import enqueue_job
from queuectl.core.worker_manager import start_workers
from queuectl.core.dlq_manager import list_dlq, retry_dlq


def main():
    print(">>> CLI started")  # Debug print to confirm CLI runs

    parser = argparse.ArgumentParser(prog="queuectl")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # enqueue
    enq = sub.add_parser("enqueue", help="Add a new job to the queue")
    enq.add_argument("job_json")

    # worker
    worker = sub.add_parser("worker", help="Start worker(s)")
    worker.add_argument("--count", type=int, default=1, help="Number of workers to start")

    # dlq
    dlq = sub.add_parser("dlq", help="Manage Dead Letter Queue")
    dlq_sub = dlq.add_subparsers(dest="dlqcmd", required=True)

    dlq_sub.add_parser("list", help="List all DLQ jobs")

    dlq_retry = dlq_sub.add_parser("retry", help="Retry a DLQ job by ID")
    dlq_retry.add_argument("job_id")

    args = parser.parse_args()
    conn = init_db()

    if args.cmd == "enqueue":
        enqueue_job(conn, args.job_json)

    elif args.cmd == "worker":
        start_workers(args.count)

    elif args.cmd == "dlq":
        print(f"DEBUG: args.cmd={args.cmd}, args.dlqcmd={args.dlqcmd}")  # Debug line
        if args.dlqcmd == "list":
            list_dlq(conn)
        elif args.dlqcmd == "retry":
            retry_dlq(conn, args.job_id)
        else:
            dlq.print_help()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
