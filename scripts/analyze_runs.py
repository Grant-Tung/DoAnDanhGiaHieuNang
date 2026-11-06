import argparse
import csv
import math
import statistics
from pathlib import Path


def percentile(values, percentage):
    values = sorted(values)
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]

    pos = (len(values) - 1) * percentage / 100
    low = math.floor(pos)
    high = math.ceil(pos)

    return values[low] + (
        values[high] - values[low]
    ) * (pos - low)


parser = argparse.ArgumentParser()
parser.add_argument("--samples", required=True)
parser.add_argument("--metadata", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

with open(args.samples, newline="", encoding="utf-8") as f:
    samples = list(csv.DictReader(f))

with open(args.metadata, newline="", encoding="utf-8") as f:
    metadata = list(csv.DictReader(f))

if not samples or len(metadata) != 1:
    raise SystemExit("ERROR: Invalid samples or metadata")

meta = metadata[0]

# Only use measurements after warm-up
measured = [
    row for row in samples
    if row["in_warmup"].strip().lower() == "false"
]

if not measured:
    raise SystemExit("ERROR: No measurement samples after warm-up")

# ── KPI trên TẤT CẢ mẫu (bao gồm fallback Basic khi yêu cầu Interleaved) ──
all_offsets = [float(r["offset_ms"]) for r in measured]
all_delays = [float(r["delay_ms"]) for r in measured]
all_absolute = [abs(v) for v in all_offsets]

# ── KPI chỉ trên mẫu matched (mode_actual == mode_requested) ──
matched = [
    row for row in measured
    if row["mode_actual"] == meta["mode_requested"]
    and row["protocol_actual"] == meta["protocol_requested"]
]

# Dùng ALL mẫu cho KPI chính (bao gồm fallback) — tránh tô hồng Interleaved
offsets = all_offsets
delays = all_delays
absolute = all_absolute

result = {
    "run_id": meta["run_id"],
    "scenario": meta["scenario"],
    "rep": meta["rep"],
    "mode_id": meta["mode_id"],
    "measure_requests": meta["measure_requests"],
    "measure_responses": meta["measure_responses"],
    "measure_valid": len(measured),
    "matched_samples": len(matched),
    "fallback_samples": len(measured) - len(matched),
    "interleaved_samples": sum(
        r["mode_actual"] == "Interleaved"
        for r in measured
    ),
    # KPI trên TẤT CẢ mẫu (bao gồm fallback)
    "bias_ms": statistics.mean(offsets),
    "mae_ms": statistics.mean(absolute),
    "p95_abs_offset_ms": percentile(absolute, 95),
    "std_offset_ms": (
        statistics.stdev(offsets)
        if len(offsets) > 1 else 0.0
    ),
    "mean_delay_ms": statistics.mean(delays),
    "p95_delay_ms": percentile(delays, 95),
    # KPI chỉ trên matched (để so sánh — nếu muốn báo cả hai con số)
    "mae_matched_ms": (
        statistics.mean([abs(float(r["offset_ms"])) for r in matched])
        if matched else float("nan")
    ),
    "p95_matched_ms": (
        percentile([abs(float(r["offset_ms"])) for r in matched], 95)
        if matched else float("nan")
    ),
    "valid_ratio": meta["valid_ratio"],
    "interleaved_ratio": meta["interleaved_ratio"],
}

output = Path(args.out)
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=result.keys())
    writer.writeheader()
    writer.writerow(result)

print("\n===== NTP KPI ANALYSIS =====")
for key, value in result.items():
    if isinstance(value, float):
        print(f"{key}: {value:.6f}")
    else:
        print(f"{key}: {value}")

print("\nSaved:", output)
print("NOTE: mae_ms = all samples (incl. fallback);")
print("      mae_matched_ms = only mode_actual == mode_requested.")
