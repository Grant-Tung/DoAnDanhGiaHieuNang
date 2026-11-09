# Đánh giá hiệu năng NTPv4 / NTPv5

Đồ án môn Đánh giá hiệu năng hệ thống – Nhóm 14 (Nguyễn Ngọc Tuyến, Nguyễn Công Tùng), UIT.

Đo sai số ước lượng offset của NTPv4 và NTPv5 (`ntp5-exp`) ở 4 chế độ (Basic/Interleaved) và 5 kịch bản mạng giả lập bằng NetEm. Tổng cộng 100 run. Ghi chú chi tiết xem [doan.md](doan.md).

## Cấu trúc

```
doan.md            ghi chú đồ án: phạm vi, kết quả, tiến độ
scripts/           script lab, chạy thực nghiệm và xử lý dữ liệu
runs/pilot/        8 run thử (S0, S4)
runs/main/         100 run chính, KPI tổng hợp và biểu đồ
ntp5-exp           công cụ NTPv5 (submodule, commit fe19210)
ntp5-exp.zip       log và PCAP thô của 100 run
```

## Scripts

| Script | Chức năng |
|---|---|
| `setup_lab.sh` | Tạo 2 namespace và veth |
| `config_scenario.sh` | Cấu hình NetEm S0–S4 |
| `run_matrix.sh` | Chạy ma trận thí nghiệm (`test`, `pilot`, `main`) |
| `convert_runner_log.py` | Chuyển log của runner sang dạng timed (WARMUP/MEASURE) |
| `parse_timed_v2.py` | Tách mẫu offset/delay ra CSV |
| `analyze_runs.py` | Tính KPI cho 1 run |
| `batch_process.py` | Chạy toàn bộ pipeline cho mọi run và gộp KPI |
| `plot_kpi.py` | Vẽ biểu đồ |
| `qa_runs.py` | Đối chiếu KPI của các run pilot |
| `s3_robust_stats.py` | Median và MAE sau khi loại outlier tại S3 |
| `capture_timed.py` | Chạy thử client trên localhost |

## Chạy lại phân tích

```bash
python scripts/batch_process.py --phase main      # ra runs/main/kpi_summary.csv, kpi_by_mode_scenario.csv
python scripts/plot_kpi.py --phase main           # ra runs/main/charts/*.png (cần matplotlib)
python scripts/s3_robust_stats.py runs/main S3 100
```

## Ghi chú về dữ liệu

- Runner: `run_matrix.sh`, công cụ `ntp5-exp` commit `fe19210790b2a1cbd951e3e5066dca094dd62a52`.
- Run `main-b3-08_S3_M1` bị dừng sớm (Ctrl+C) nên chỉ có 96 request MEASURE; run này vẫn được giữ lại và có ghi chú.
- Ba run có đủ log và PCAP để đối chiếu: `main-b3-08_S3_M1`, `main-b1-02_S3_M2`, `main-b1-13_S3_M4`.

## Làm việc với Git

- `main` là bản thống nhất, không sửa trực tiếp.
- Mỗi người làm trên nhánh riêng (`Tung`, `Tuyen`) rồi mở Pull Request vào `main`.

```bash
git checkout Tung
git pull origin main
# sửa file
git add . && git commit -m "Mô tả ngắn"
git push origin Tung
```
