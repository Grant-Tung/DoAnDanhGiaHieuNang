"""Thống kê bền vững tại một kịch bản (mặc định S3): MAE gốc, Median |offset|,
MAE sau khi loại outlier |offset| > ngưỡng, số outlier. Bỏ mẫu warm-up.

Dùng: python scripts/s3_robust_stats.py [runs_dir] [scenario] [threshold_ms]
"""
import csv, glob, os, statistics as st, sys

runs = sys.argv[1] if len(sys.argv) > 1 else "runs/main"
sc = sys.argv[2] if len(sys.argv) > 2 else "S3"
thr = float(sys.argv[3]) if len(sys.argv) > 3 else 100.0

print("mode,n,mae_ms,median_abs_ms,mae_wo_outlier_ms,n_outlier")
for m in ["M1", "M2", "M3", "M4"]:
    v = []
    for f in glob.glob(os.path.join(runs, f"*_{sc}_{m}", "parsed", "*_samples.csv")):
        with open(f, newline="") as fh:
            v += [abs(float(r["offset_ms"])) for r in csv.DictReader(fh) if r["in_warmup"] == "False"]
    if not v:
        print(f"{m},0,,,,"); continue
    keep = [x for x in v if x <= thr]
    assert len(keep) <= len(v)
    print(f"{m},{len(v)},{st.mean(v):.3f},{st.median(v):.3f},{st.mean(keep):.3f},{len(v) - len(keep)}")
