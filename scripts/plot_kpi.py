#!/usr/bin/env python3
"""plot_kpi.py — Ve bieu do theo muc 10.3 doan.md.

Yeu cau: pip install matplotlib

Dung:
  python plot_kpi.py --phase pilot
  python plot_kpi.py --phase main
  python plot_kpi.py --phase main --only 1 2   # chi ve bieu do 1 va 2

Bieu do (theo muc 10.3):
  1. Offset theo thoi gian, S4, cac che do + duong ly thuyet -15 ms
  2. Boxplot |offset| theo che do x kich ban
  3. Histogram offset cua Interleaved o S3 (tim hai dinh)
  4. Sai so offset theo muc bat doi xung — duong he so 0.5
  5. Ty le fallback theo muc loss
"""

import argparse
import csv
import math
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent

MODE_LABELS = {
    "M1": "NTPv4 Basic",
    "M2": "NTPv4 Interleaved",
    "M3": "NTPv5 Basic",
    "M4": "NTPv5 Interleaved",
}

MODE_COLORS = {
    "M1": "#1f77b4",
    "M2": "#ff7f0e",
    "M3": "#2ca02c",
    "M4": "#d62728",
}

SCENARIO_LABELS = {
    "S0": "S0 (no delay)",
    "S1": "S1 (25/25 ms)",
    "S2": "S2 (25+-10 ms)",
    "S3": "S3 (25+-10 + 5% loss)",
    "S4": "S4 (10/40 ms asym.)",
}


def load_all_samples(phase_dir):
    """Tai tat ca *_samples.csv tu thu muc parsed cua moi run."""
    samples = []
    for samples_csv in phase_dir.rglob("*_samples.csv"):
        if "parsed" not in str(samples_csv):
            continue
        with samples_csv.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                if row.get("in_warmup", "").strip().lower() == "true":
                    continue
                try:
                    row["offset_ms"] = float(row["offset_ms"])
                    row["delay_ms"] = float(row["delay_ms"])
                    row["elapsed_s"] = float(row.get("elapsed_s", 0))
                except (ValueError, KeyError):
                    continue
                samples.append(row)
    return samples


def load_kpi_summary(phase_dir):
    """Tai kpi_summary.csv."""
    kpi_path = phase_dir / "kpi_summary.csv"
    if not kpi_path.is_file():
        return []
    with kpi_path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def plot1_offset_timeseries_s4(samples, out_dir):
    """Bieu do 1: Offset theo thoi gian cho S4, cac mode."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 5))

    s4 = [s for s in samples if s.get("scenario") == "S4"]
    if not s4:
        print("  [!] Khong co mau S4 - bo qua bieu do 1")
        plt.close(fig)
        return

    for mode in ["M1", "M2", "M3", "M4"]:
        data = [s for s in s4 if s.get("mode_id") == mode]
        if not data:
            continue
        data.sort(key=lambda s: s["elapsed_s"])
        xs = [s["elapsed_s"] for s in data]
        ys = [s["offset_ms"] for s in data]
        ax.scatter(xs, ys, s=8, alpha=0.5, label=MODE_LABELS[mode],
                   color=MODE_COLORS[mode])

    ax.axhline(-15, color="black", linestyle="--", linewidth=1,
               label="Ly thuyet -15 ms")
    ax.set_xlabel("Thoi gian (s) trong run")
    ax.set_ylabel("Offset (ms)")
    ax.set_title("S4 (bat doi xung 10/40 ms): Offset theo thoi gian")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    path = out_dir / "chart1_offset_timeseries_S4.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def plot2_boxplot_offset(samples, out_dir):
    """Bieu do 2: Boxplot |offset| theo mode x scenario."""
    import matplotlib.pyplot as plt

    scenarios = sorted(set(s.get("scenario", "") for s in samples))
    modes = ["M1", "M2", "M3", "M4"]

    fig, axes = plt.subplots(1, len(scenarios), figsize=(4 * len(scenarios), 5),
                             sharey=True)
    if len(scenarios) == 1:
        axes = [axes]

    for ax, scen in zip(axes, scenarios):
        data_by_mode = []
        labels = []
        for mode in modes:
            vals = [abs(s["offset_ms"]) for s in samples
                    if s.get("scenario") == scen and s.get("mode_id") == mode]
            if vals:
                data_by_mode.append(vals)
                labels.append(mode)

        if data_by_mode:
            bp = ax.boxplot(data_by_mode, labels=labels, patch_artist=True,
                            showfliers=False)
            for patch, mode in zip(bp["boxes"], labels):
                patch.set_facecolor(MODE_COLORS.get(mode, "gray"))
                patch.set_alpha(0.6)

        ax.set_title(SCENARIO_LABELS.get(scen, scen))
        ax.set_xlabel("Mode")
        ax.grid(True, alpha=0.3, axis="y")

    axes[0].set_ylabel("|Offset| (ms)")
    fig.suptitle("Boxplot |Offset| theo Mode x Kich ban", fontsize=13)
    fig.tight_layout()

    path = out_dir / "chart2_boxplot_offset.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def plot3_histogram_interleaved_s3(samples, out_dir):
    """Bieu do 3: Histogram offset Interleaved o S3 (tim hai dinh)."""
    import matplotlib.pyplot as plt

    data = [s["offset_ms"] for s in samples
            if s.get("scenario") == "S3"
            and s.get("mode_actual") == "Interleaved"]

    if not data:
        # Thu voi mode_id M2/M4 tai S3
        data = [s["offset_ms"] for s in samples
                if s.get("scenario") == "S3"
                and s.get("mode_id") in ("M2", "M4")]

    if not data:
        print("  [!] Khong co mau Interleaved S3 - bo qua bieu do 3")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(data, bins=50, edgecolor="black", alpha=0.7,
            color="#ff7f0e")
    ax.set_xlabel("Offset (ms)")
    ax.set_ylabel("So mau")
    ax.set_title("S3: Histogram offset Interleaved (tim 2 dinh: fallback vs that)")
    ax.axvline(0, color="red", linestyle="--", linewidth=0.8)
    ax.grid(True, alpha=0.3)

    path = out_dir / "chart3_histogram_interleaved_S3.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def plot4_offset_vs_asymmetry(kpi_rows, out_dir):
    """Bieu do 4: MAE offset theo muc bat doi xung — duong 0.5*Delta."""
    import matplotlib.pyplot as plt

    # Bat doi xung: S0=0, S1=0, S2=0, S3=0, S4=30ms (40-10)
    ASYMMETRY = {"S0": 0, "S1": 0, "S2": 0, "S3": 0, "S4": 30}

    fig, ax = plt.subplots(figsize=(8, 5))

    for mode in ["M1", "M2", "M3", "M4"]:
        xs = []
        ys = []
        for row in kpi_rows:
            if row.get("mode_id") != mode:
                continue
            scen = row.get("scenario", "")
            asym = ASYMMETRY.get(scen, None)
            if asym is None:
                continue
            try:
                bias = abs(float(row.get("bias_ms", 0)))
            except ValueError:
                continue
            xs.append(asym)
            ys.append(bias)

        if xs:
            ax.scatter(xs, ys, s=20, alpha=0.6, label=MODE_LABELS[mode],
                       color=MODE_COLORS[mode])

    # Duong ly thuyet: bias = 0.5 x Delta
    x_theory = list(range(0, 35, 1))
    y_theory = [0.5 * x for x in x_theory]
    ax.plot(x_theory, y_theory, "k--", linewidth=1.5,
            label="Ly thuyet: bias = 0.5*Delta")

    ax.set_xlabel("Bat doi xung Delta (ms) = delay_s2c - delay_c2s")
    ax.set_ylabel("|Bias| trung binh (ms)")
    ax.set_title("Sai so offset theo muc bat doi xung")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    path = out_dir / "chart4_offset_vs_asymmetry.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def plot5_fallback_vs_loss(kpi_rows, out_dir):
    """Bieu do 5: Ty le fallback theo muc loss."""
    import matplotlib.pyplot as plt

    # S3 la kich ban co loss 5%
    LOSS_PCT = {"S0": 0, "S1": 0, "S2": 0, "S3": 5, "S4": 0}

    fig, ax = plt.subplots(figsize=(8, 5))

    for mode in ["M2", "M4"]:  # chi Interleaved moi co fallback
        xs = []
        ys = []
        for row in kpi_rows:
            if row.get("mode_id") != mode:
                continue
            scen = row.get("scenario", "")
            loss = LOSS_PCT.get(scen, None)
            if loss is None:
                continue
            try:
                matched = int(row.get("matched_samples", 0))
                total = int(row.get("measure_valid", 0))
            except ValueError:
                continue
            if total > 0:
                fallback_ratio = 1.0 - (matched / total)
            else:
                fallback_ratio = 0
            xs.append(loss)
            ys.append(fallback_ratio * 100)

        if xs:
            ax.scatter(xs, ys, s=30, alpha=0.6, label=MODE_LABELS[mode],
                       color=MODE_COLORS[mode])

    ax.set_xlabel("Ty le mat goi (%)")
    ax.set_ylabel("Ty le fallback ve Basic (%)")
    ax.set_title("Ty le fallback (Interleaved -> Basic) theo muc mat goi")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    path = out_dir / "chart5_fallback_vs_loss.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.name}")


def main():
    parser = argparse.ArgumentParser(
        description="Ve bieu do KPI theo muc 10.3 doan.md"
    )
    parser.add_argument(
        "--phase", required=True, choices=["pilot", "main"],
    )
    parser.add_argument(
        "--only", nargs="+", type=int, default=[],
        help="Chi ve bieu do duoc chi dinh (1-5)"
    )
    args = parser.parse_args()

    try:
        import matplotlib
        matplotlib.use("Agg")
    except ImportError:
        print("[ERROR] Can cai matplotlib: pip install matplotlib")
        sys.exit(1)

    phase_dir = ROOT / "runs" / args.phase
    out_dir = phase_dir / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[PLOT] Ve bieu do cho {args.phase}")
    print(f"       Output: {out_dir}\n")

    samples = load_all_samples(phase_dir)
    kpi_rows = load_kpi_summary(phase_dir)

    print(f"       Tong mau (sau warm-up): {len(samples)}")
    print(f"       Tong KPI rows: {len(kpi_rows)}\n")

    plots = args.only or [1, 2, 3, 4, 5]

    if 1 in plots:
        print("Bieu do 1: Offset timeseries S4")
        plot1_offset_timeseries_s4(samples, out_dir)

    if 2 in plots:
        print("Bieu do 2: Boxplot |offset|")
        plot2_boxplot_offset(samples, out_dir)

    if 3 in plots:
        print("Bieu do 3: Histogram Interleaved S3")
        plot3_histogram_interleaved_s3(samples, out_dir)

    if 4 in plots:
        print("Bieu do 4: Offset vs asymmetry")
        plot4_offset_vs_asymmetry(kpi_rows, out_dir)

    if 5 in plots:
        print("Bieu do 5: Fallback vs loss")
        plot5_fallback_vs_loss(kpi_rows, out_dir)

    print(f"\n[OK] Xong. Bieu do o {out_dir}")


if __name__ == "__main__":
    main()
