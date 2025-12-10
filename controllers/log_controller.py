# aws/log_controller.py

import os
import time
import boto3
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# NEW: import our embedding + Chroma storage helper
from controllers.vector_controller import embed_and_store

load_dotenv()

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LOG_GROUP = os.getenv("CLOUDWATCH_LOG_GROUP", "/ec2/logs/RAG")
DEFAULT_LOOKBACK_MIN = int(os.getenv("DEFAULT_LOOKBACK_MIN", "10"))

AWS_DIR = "./aws_logs"
LOG_FILE = os.path.join(AWS_DIR, "log.txt")
LAST_TS_FILE = os.path.join(AWS_DIR, "last_ts.txt")

os.makedirs(AWS_DIR, exist_ok=True)

logs_client = boto3.client("logs", region_name=AWS_REGION)


# -------------------------------
# Timestamp helpers
# -------------------------------
def read_last_ts():
    if not os.path.exists(LAST_TS_FILE):
        return None
    try:
        return int(open(LAST_TS_FILE).read().strip())
    except:
        return None


def write_last_ts(ts_ms: int):
    with open(LAST_TS_FILE, "w") as f:
        f.write(str(ts_ms))


# -------------------------------
# CloudWatch Pull Logic
# -------------------------------
def pull_cloudwatch_events(start_time_ms=None):
    events = []
    params = dict(logGroupName=LOG_GROUP, limit=10000)
    if start_time_ms:
        params["startTime"] = int(start_time_ms)

    next_token = None

    while True:
        if next_token:
            params["nextToken"] = next_token

        resp = logs_client.filter_log_events(**params)
        events.extend(resp.get("events", []))

        next_token = resp.get("nextToken")
        if not next_token:
            break

        time.sleep(0.1)  # prevent throttling
    return events


# -------------------------------
# Main Pull + Save + Embed
# -------------------------------
def pull_and_save_logs():
    """Pull latest logs from CloudWatch, save them, embed them, store in ChromaDB."""
    last_ts = read_last_ts()

    if last_ts is None:
        dt = datetime.now(timezone.utc) - timedelta(minutes=DEFAULT_LOOKBACK_MIN)
        start_ms = int(dt.timestamp() * 1000)
    else:
        start_ms = last_ts + 1

    events = pull_cloudwatch_events(start_ms)
    ingested_count = 0
    max_ts = start_ms

    to_write = []

    for e in events:
        message = e.get("message", "")
        ts = e.get("timestamp", 0)

        iso = datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()
        log_stream = e.get("logStreamName", "-")

        # Final cleaned log line
        line = f"{iso} | {log_stream} | {message}"

        to_write.append(line)
        ingested_count += 1

        if ts > max_ts:
            max_ts = ts

    # -------------------------------------------
    # SAVE + EMBED
    # -------------------------------------------
    if to_write:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            for line in to_write:
                f.write(line + "\n")

                # Metadata for Chroma vector DB
                metadata = {
                    "timestamp": line.split(" | ")[0],
                    "log_stream": line.split(" | ")[1],
                }

                # 🔥 Embed + Store in ChromaDB
                embed_and_store(line, metadata)

        write_last_ts(max_ts)

    return ingested_count, start_ms, max_ts if max_ts != start_ms else None
