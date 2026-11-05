import csv
from pathlib import Path

ROOT = Path("runs/pilot")
KPI_DIR = Path("results/pilot_kpi")
OUTPUT = Path("results/pilot_qa.csv")

def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

original = {
    r["run_id"]: r
    for r in read_csv(ROOT / "metadata.csv")
}

files = sorted(KPI_DIR.glob("pilot-b1-*.csv"))
expected = {
    (s, m)
    for s in ("S0", "S4")
    for m in ("M1", "M2", "M3", "M4")
}

if len(files) != 8:
    raise SystemExit(f"ERROR: Expected 8 KPI files, got {len(files)}")

reports = []
seen = set()

for file in files:
    row = read_csv(file)[0]
    run = file.stem
    scenario = row["scenario"]
    mode = row["mode_id"]
    seen.add((scenario, mode))

    errors = []

    req = int(row["measure_requests"])
    resp = int(row["measure_responses"])
    valid = int(row["measure_valid"])
    matched = int(row["matched_samples"])
    il = int(row["interleaved_samples"])

    if not (0 <= matched <= valid <= resp <= req):
        errors.append("INVALID_COUNTS")

    if req != 119:
        errors.append("UNEXPECTED_PILOT_REQUESTS")

    if run not in original:
        errors.append("MISSING_RUN_METADATA")
    else:
        meta = original[run]

        if meta["status"] != "ok":
            errors.append("RUN_NOT_OK")

        if (meta["scenario"], meta["mode"]) != (scenario, mode):
            errors.append("METADATA_MISMATCH")

        if int(meta["requests_sent"]) < req:
            errors.append("REQUEST_COUNT_MISMATCH")

        if int(meta["responses_received"]) < resp:
            errors.append("RESPONSE_COUNT_MISMATCH")

    folder = ROOT / run

    for name in ("client.log", "server.log",
                 "tc_before.txt", "tc_after.txt",
                 "capture.pcap"):
        if not (folder / name).is_file():
            errors.append("MISSING_" + name)

    parsed = folder / "parsed" / f"{run}_timed_samples.csv"

    if not parsed.is_file():
        errors.append("MISSING_PARSED_CSV")
    else:
        samples = read_csv(parsed)
        measured = sum(
            r["in_warmup"].lower() == "false"
            for r in samples
        )
        if measured != valid:
            errors.append("SAMPLE_COUNT_MISMATCH")

    if req:
        ratio = valid / req
        if abs(ratio - float(row["valid_ratio"])) > 0.000001:
            errors.append("VALID_RATIO_MISMATCH")

    status = "PASS" if not errors else "FAIL"

    reports.append({
        "run_id": run,
        "scenario": scenario,
        "mode": mode,
        "requests": req,
        "responses": resp,
        "valid": valid,
        "matched": matched,
        "interleaved": il,
        "qa_status": status,
        "issues": ";".join(errors)
    })

if seen != expected:
    raise SystemExit("ERROR: Missing or duplicate scenario/mode")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=reports[0].keys())
    writer.writeheader()
    writer.writerows(reports)

print("\n========== NTP PILOT QA ==========")

for r in reports:
    print(
        f"{r['scenario']} {r['mode']} "
        f"req={r['requests']} "
        f"resp={r['responses']} "
        f"valid={r['valid']} "
        f"QA={r['qa_status']} "
        f"{r['issues']}"
    )

passed = sum(r["qa_status"] == "PASS" for r in reports)

print(f"\nQA passed: {passed}/{len(reports)}")
print("Saved:", OUTPUT)
print("NOTE: This QA does not verify packet pairing.")
print("NOTE: Official runs still require 120 measure requests.")
