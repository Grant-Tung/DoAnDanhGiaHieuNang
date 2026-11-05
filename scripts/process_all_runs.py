import argparse
import csv
import shutil
import subprocess
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--phase", choices=["pilot", "main"], required=True)
parser.add_argument("--warmup", type=float, default=60)
args = parser.parse_args()

source = Path("runs") / args.phase
output = Path("results/batch") / args.phase
output.mkdir(parents=True, exist_ok=True)

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def execute(*command):
    result = subprocess.run(
        [sys.executable, *map(str, command)],
        text=True, capture_output=True
    )
    if result.returncode:
        raise RuntimeError(
            (result.stderr or result.stdout).strip()[-600:]
        )

metadata_path = source / "metadata.csv"
if not metadata_path.is_file():
    raise SystemExit(f"Missing {metadata_path}")

metadata = read_csv(metadata_path)
kpi_rows = []
qa_rows = []

for item in metadata:
    run = item["run_id"]
    mode = item["mode"]
    scenario = item["scenario"]
    rep = item["rep"]

    work = output / "work" / run
    work.mkdir(parents=True, exist_ok=True)

    problems = []
    kpi = None

    try:
        original = source / run

        for filename in (
            "client.log", "server.log",
            "tc_before.txt", "tc_after.txt", "capture.pcap"
        ):
            if not (original / filename).is_file():
                problems.append("MISSING_" + filename)

        if "MISSING_client.log" in problems:
            raise RuntimeError("client.log missing")

        shutil.copy2(original / "client.log", work / "client.log")

        execute(
            "scripts/convert_runner_log.py",
            "--log", work / "client.log",
            "--warmup", args.warmup
        )

        timed = work / f"{run}_timed.log"

        execute(
            "scripts/parse_timed_v2.py",
            "--log", timed,
            "--mode", mode,
            "--scenario", scenario,
            "--rep", rep
        )

        parsed = work / "parsed"
        samples = parsed / f"{run}_timed_samples.csv"
        meta = parsed / f"{run}_timed_metadata.csv"
        kpi_file = output / "kpis" / f"{run}.csv"
        kpi_file.parent.mkdir(parents=True, exist_ok=True)

        execute(
            "scripts/analyze_runs.py",
            "--samples", samples,
            "--metadata", meta,
            "--out", kpi_file
        )

        kpi = read_csv(kpi_file)[0]

        req = int(kpi["measure_requests"])
        resp = int(kpi["measure_responses"])
        valid = int(kpi["measure_valid"])
        matched = int(kpi["matched_samples"])

        if not (0 <= matched <= valid <= resp <= req):
            problems.append("INVALID_COUNTS")

        if args.phase == "main" and req != 120:
            problems.append("MEASURE_REQUESTS_NOT_120")

        if matched < valid:
            problems.append("MODE_FALLBACK_OR_MISMATCH")

        original_sent = int(item["requests_sent"])
        if original_sent != req + int(read_csv(meta)[0]["warmup_requests"]):
            problems.append("REQUEST_TOTAL_MISMATCH")

        if item["status"] != "ok":
            problems.append("RUNNER_NOT_OK")

        kpi_rows.append({
            "source_run_id": run,
            **kpi
        })

    except Exception as e:
        problems.append("PROCESS_ERROR: " + str(e))

    status = (
        "ERROR" if any(p.startswith("PROCESS_ERROR") for p in problems)
        else "WARN" if problems else "CHECKED"
    )

    qa_rows.append({
        "run_id": run,
        "scenario": scenario,
        "mode": mode,
        "rep": rep,
        "status": status,
        "issues": "; ".join(problems)
    })

    print(f"{run}: {status}")
    if problems:
        print("  ", "; ".join(problems))

write_csv(output / "kpi_summary.csv", kpi_rows)
write_csv(output / "qa_summary.csv", qa_rows)

print("\n===== BATCH ANALYSIS =====")
print("Metadata runs:", len(metadata))
print("KPI generated:", len(kpi_rows))
print("Warnings/errors:", sum(
    r["status"] != "CHECKED" for r in qa_rows
))
print("Saved:", output)
print("NOTE: Request-response pairing and timestamps")
print("still require independent validation.")
