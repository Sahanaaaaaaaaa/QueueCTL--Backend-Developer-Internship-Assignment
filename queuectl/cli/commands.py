import argparse
from queuectl.core.db_manager import init_db
from queuectl.core.job_manager import enqueue_job
from queuectl.core.worker_manager import start_workers
from queuectl.core.dlq_manager import list_dlq, retry_dlq

def main():
    parser = argparse.ArgumentParser(
        prog="queuectl",
        description=(
            "QueueCTL — Lightweight Background Job Queue System\n\n"
            "Commands:\n"
            "  enqueue   Add a new job to the queue\n"
            "  worker    Start worker(s) to process jobs\n"
            "  dlq       View or retry jobs in the Dead Letter Queue\n\n"
            "Use 'queuectl <command> --help' for more information on a specific command.\n\n"
            "Examples:\n"
            "  queuectl enqueue \"{\"id\":\"job1\",\"command\":\"echo 'Hello'\"}\"\n"
            "  queuectl worker --count 2\n"
            "  queuectl dlq list\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    sub = parser.add_subparsers(dest="cmd", help="Available commands")

    # enqueue
    enq = sub.add_parser(
        "enqueue",
        help="Add a new job to the queue",
        description="Add a job by providing JSON with 'id' and 'command'.",
    )
    enq.add_argument("job_json", help="Job JSON string (e.g. '{\"id\":\"job1\",\"command\":\"echo Hello\"}')")

    # worker
    worker = sub.add_parser(
        "worker",
        help="Start worker(s)",
        description="Start one or more workers to execute pending jobs.",
    )
    worker.add_argument("--count", type=int, default=1, help="Number of workers to start (default: 1)")

    # DLQ
    dlq = sub.add_parser(
        "dlq",
        help="Manage Dead Letter Queue",
        description="List or retry jobs in the Dead Letter Queue.",
    )
    dlq_sub = dlq.add_subparsers(dest="dlqcmd", help="DLQ operations")

    dlq_sub.add_parser("list", help="List all jobs in the Dead Letter Queue")
    dlq_retry = dlq_sub.add_parser("retry", help="Retry a DLQ job")
    dlq_retry.add_argument("job_id", help="ID of the DLQ job to retry")

    args = parser.parse_args()
    conn = init_db()

    if args.cmd == "enqueue":
        enqueue_job(conn, args.job_json)
    elif args.cmd == "worker":
        start_workers(args.count)
    elif args.cmd == "dlq":
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
