"""Append-only experiment log (JSON lines) plus a console echo."""
import json
import time
from pathlib import Path


def log_experiment(record, path="reports/experiment_log.jsonl"):
    record = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), **record}
    line = json.dumps(record, sort_keys=True)
    print("EXPERIMENT " + line)
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass
    return record
