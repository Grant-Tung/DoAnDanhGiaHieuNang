#!/usr/bin/env python3
"""batch_process.py — Chạy pipeline cho tất cả run trong plan.csv.

Pipeline mỗi run:
  1) convert_runner_log.py  → tạo <run_id>_timed.log
  2) parse_timed_v2.py      → tạo parsed/<run_id>_timed_samples.csv + _metadata.csv
  3) analyze_runs.py        → tạo parsed/<run_id>_timed_kpi.csv

Cuối cùng gộp tất cả KPI thành bảng tổng hợp kpi_summary.csv
và bảng trung bình theo mode × scenario: kpi_by_mode_scenario.csv

Dùng:
  python batch_process.py --phase pilot        # xử lý runs/pilot/
  python batch_process.py --phase main         # xử lý runs/main/
  python batch_process.py --phase pilot --dry  # chỉ liệt kê, không chạy
"""

import argparse
import csv
import math
import statistics
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent


def percentile(values, pct):
    """Tính percentile (linear interpolation) — copy từ analyze_runs.py."""
    values = sorted(values)
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    pos = (len(values) - 1) * pct / 100
    low = math.floor(pos)
    high = math.ceil(pos)
    return values[low] + (values[high] - values[low]) * (pos - low)


def run_cmd(args, label=""):
    """Chạy một lệnh Python, in stdout/stderr, trả exit code."""
    print(f"  -> {label}: {' '.join(str(a) for a in args)}")
    result = subprocess.run(
        [sys.executable] + [str(a) for a in args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    if stdout.strip():
        for line in stdout.strip().split("\n"):
            print(f"    {line}")
    if result.returncode != 0:
        print(f"    ! STDERR: {stderr.strip()}")
    return result.returncode


def process_one_run(run_id, scenario, mode, rep, run_dir):
    """Chạy pipeline convert → parse → analyze cho một run.

    Trả (success: bool, kpi_path: Path | None).
    """
    client_log = run_dir / "client.log"
    if not client_log.is_file():
        print(f"  [!] Bo qua {run_id}: khong tim thay client.log")
        return False, None

    # 1) convert_runner_log.py
    timed_log = run_dir / f"{run_id}_timed.log"
    rc = run_cmd(
        [SCRIPT_DIR / "convert_runner_log.py",
         "--log", str(client_log),
         "--warmup", "60"],
        label="convert"
    )
    if rc != 0:
        return False, None

    # convert output: <parent_name>_timed.log ở cùng thư mục với client.log
    # Tên file output = run_dir.name + "_timed.log"
    expected_timed = run_dir / f"{run_dir.name}_timed.log"
    if not expected_timed.is_file():
        print(f"  [!] convert khong tao duoc {expected_timed.name}")
        return False, None

    # 2) parse_timed_v2.py
    rc = run_cmd(
        [SCRIPT_DIR / "parse_timed_v2.py",
         "--log", str(expected_timed),
         "--mode", mode,
         "--scenario", scenario,
         "--rep", str(rep)],
        label="parse_v2"
    )
    if rc != 0:
        return False, None

    parsed_dir = run_dir / "parsed"
    samples_csv = parsed_dir / f"{expected_timed.stem}_samples.csv"
    metadata_csv = parsed_dir / f"{expected_timed.stem}_metadata.csv"

    if not metadata_csv.is_file():
        print(f"  [!] parse_v2 khong tao duoc metadata CSV")
        return False, None

    # 3) analyze_runs.py
    kpi_csv = parsed_dir / f"{expected_timed.stem}_kpi.csv"
    rc = run_cmd(
        [SCRIPT_DIR / "analyze_runs.py",
         "--samples", str(samples_csv),
         "--metadata", str(metadata_csv),
         "--out", str(kpi_csv)],
        label="analyze"
    )
    if rc != 0:
        return False, None

    if not kpi_csv.is_file():
        print(f"  [!] analyze khong tao duoc KPI CSV")
        return False, None

    return True, kpi_csv


def merge_kpi(kpi_files, output_dir):
    """Gộp tất cả KPI file thành bảng tổng hợp."""
    all_rows = []
    for kpi_path in kpi_files:
        with kpi_path.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                all_rows.append(row)

    if not all_rows:
        print("[!] Khong co ket qua KPI nao de gop")
        return

    # Lưu bảng tổng hợp
    summary_path = output_dir / "kpi_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(all_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\n[OK] Bang tong hop: {summary_path}")
    print(f"     Tong so run: {len(all_rows)}")

    # Bảng trung bình theo mode × scenario
    groups = {}
    for row in all_rows:
        key = (row.get("mode_id", ""), row.get("scenario", ""))
        groups.setdefault(key, []).append(row)

    FLOAT_COLS = [
        "bias_ms", "mae_ms", "p95_abs_offset_ms",
        "std_offset_ms", "mean_delay_ms", "p95_delay_ms",
    ]

    agg_rows = []
    for (mode_id, scenario), rows in sorted(groups.items()):
        agg = {
            "mode_id": mode_id,
            "scenario": scenario,
            "n_runs": len(rows),
        }
        for col in FLOAT_COLS:
            vals = []
            for r in rows:
                try:
                    vals.append(float(r[col]))
                except (ValueError, KeyError):
                    pass
            if vals:
                agg[f"{col}_mean"] = statistics.mean(vals)
                agg[f"{col}_std"] = (
                    statistics.stdev(vals) if len(vals) > 1 else 0.0
                )
            else:
                agg[f"{col}_mean"] = ""
                agg[f"{col}_std"] = ""

        # Trung bình valid_ratio
        vr_vals = []
        for r in rows:
            try:
                vr_vals.append(float(r.get("valid_ratio", "")))
            except ValueError:
                pass
        agg["valid_ratio_mean"] = (
            statistics.mean(vr_vals) if vr_vals else ""
        )

        agg_rows.append(agg)

    if agg_rows:
        agg_path = output_dir / "kpi_by_mode_scenario.csv"
        with agg_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f, fieldnames=list(agg_rows[0].keys())
            )
            writer.writeheader()
            writer.writerows(agg_rows)
        print(f"[OK] KPI theo mode x scenario: {agg_path}")

        # In bảng ra console
        print(f"\n{'mode':>6} {'scen':>6} {'n':>3} "
              f"{'MAE_ms':>10} {'P95_ms':>10} {'bias_ms':>10} "
              f"{'delay_ms':>10} {'valid%':>8}")
        print("-" * 72)
        for a in agg_rows:
            def fmt(v):
                try:
                    return f"{float(v):.4f}"
                except (ValueError, TypeError):
                    return "N/A"
            print(
                f"{a['mode_id']:>6} {a['scenario']:>6} "
                f"{a['n_runs']:>3} "
                f"{fmt(a.get('mae_ms_mean', '')):>10} "
                f"{fmt(a.get('p95_abs_offset_ms_mean', '')):>10} "
                f"{fmt(a.get('bias_ms_mean', '')):>10} "
                f"{fmt(a.get('mean_delay_ms_mean', '')):>10} "
                f"{fmt(a.get('valid_ratio_mean', '')):>8}"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Batch pipeline: convert → parse → analyze cho tất cả run"
    )
    parser.add_argument(
        "--phase", required=True, choices=["pilot", "main"],
        help="Chạy pilot (8 run) hoặc main (100 run)"
    )
    parser.add_argument(
        "--dry", action="store_true",
        help="Chỉ liệt kê run, không chạy"
    )
    args = parser.parse_args()

    phase_dir = ROOT / "runs" / args.phase
    plan_csv = phase_dir / "plan.csv"

    if not plan_csv.is_file():
        print(f"[ERROR] Khong tim thay {plan_csv}")
        sys.exit(1)

    with plan_csv.open(newline="", encoding="utf-8") as f:
        plan = list(csv.DictReader(f))

    print(f"[PLAN] {plan_csv}")
    print(f"       Tong so run: {len(plan)}")
    print()

    if args.dry:
        for row in plan:
            print(f"  {row['run_id']:30s}  {row['scenario']:4s}  "
                  f"{row['mode']:3s}  rep={row['rep']}")
        print("\n(Dry run - khong chay gi)")
        return

    kpi_files = []
    ok = 0
    fail = 0

    for i, row in enumerate(plan, 1):
        run_id = row["run_id"]
        scenario = row["scenario"]
        mode = row["mode"]
        rep = row["rep"]
        run_dir = phase_dir / run_id

        print(f"[{i}/{len(plan)}] {run_id} ({scenario}, {mode}, rep={rep})")

        if not run_dir.is_dir():
            print(f"  [!] Thu muc khong ton tai: {run_dir}")
            fail += 1
            continue

        success, kpi_path = process_one_run(
            run_id, scenario, mode, rep, run_dir
        )
        if success and kpi_path:
            kpi_files.append(kpi_path)
            ok += 1
        else:
            fail += 1

        print()

    print(f"\n{'='*60}")
    print(f"Hoàn tất: {ok} OK, {fail} lỗi / bỏ qua")

    if kpi_files:
        merge_kpi(kpi_files, phase_dir)


if __name__ == "__main__":
    main()
