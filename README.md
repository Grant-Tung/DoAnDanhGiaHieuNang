# Đồ án: Đánh giá hiệu năng NTPv4 / NTPv5

Nhóm: Tùng (P2 — mạng & thực nghiệm), Tuyến (P1 — giao thức & dữ liệu).

## Các file

| File | Vai trò | Ai đọc | Khi nào sửa |
|---|---|---|---|
| `doan.md` | **Sổ theo dõi chính**. Phần A: đọc nhanh, dễ hiểu. Phần B: chi tiết chính xác để làm thí nghiệm và viết báo cáo | Tùng, Tuyến | Mỗi khi xong việc, chạy thí nghiệm, hoặc **chốt** một quyết định |
| `phanbien_nangcap.md` | **Hộp góp ý**: ý tưởng, sửa phương pháp **chưa chốt** | Tùng, Tuyến, AI | Khi có góp ý mới; khi một đề xuất được chấp nhận/bác bỏ |
| `phantich.md` | **Bàn giao cho AI**: đọc khối "BÀN GIAO" ở đầu file là AI mới làm tiếp được | AI | Khi trạng thái đồ án thay đổi đáng kể |
| `hoc_doan.md` | **Học đồ án**: bản đồ 12 bài + prompt cho AI gia sư | Tùng, Tuyến | Khi phạm vi/kết quả đồ án thay đổi |
| `scripts/` | NetEm/runner (Tùng) và các script Python parser/KPI (Tuyến); một converter ở nhánh `Tuyen-integration` | Cả hai | Khi thay đổi công cụ, kiểm tra chạy và ghi rõ trạng thái nghiệm thu |

## Scripts

| Script | Vai trò | Trạng thái |
|---|---|---|
| `scripts/run_matrix.sh` | Runner chạy ma trận thí nghiệm | ✅ Dùng chính |
| `scripts/config_scenario.sh` | Cấu hình NetEm S0–S4 | ✅ Dùng chính |
| `scripts/convert_runner_log.py` | Chuyển `client.log` (epoch) → timed log (elapsed + WARMUP/MEASURE) | ✅ Dùng chính |
| `scripts/parse_timed_v2.py` | Parser v2: đọc timed log → samples + metadata CSV | ✅ Dùng chính |
| `scripts/analyze_runs.py` | Tính KPI cho 1 run từ samples + metadata | ✅ Dùng chính |
| `scripts/batch_process.py` | **MỚI** — chạy pipeline cho tất cả run (đọc plan.csv, gộp kết quả) | ✅ Dùng chính |
| `scripts/plot_kpi.py` | **MỚI** — vẽ 5 biểu đồ theo mục 10.3 doan.md | ✅ Dùng chính |
| `scripts/capture_timed.py` | Chạy client localhost (dùng thử) | 🟡 Thử nghiệm |
| `scripts/parse_timed.py` | ⚠️ **CŨ** — parser v1 (thư mục output cứng `~/ntpv5-project/results/parsed`). Dùng `parse_timed_v2.py` thay thế | ❌ Không dùng |
| `scripts/parse_log.py` | ⚠️ **CŨ** — parser localhost cứng đường dẫn. Dùng `batch_process.py` thay thế | ❌ Không dùng |
| `scripts/parse_runs.py` | ⚠️ **CŨ** — parser localhost v2, vẫn cứng `~/ntpv5-project/results/`. Dùng `batch_process.py` thay thế | ❌ Không dùng |

## Tiến độ gần nhất (06/11/2026)

- **Đã xác nhận:** Tùng có NetEm S0–S4 và pilot S0/S4 **8/8 run đạt** (24/10; xem `doan.md` mục 12). Tuyến kiểm thử localhost đủ M1–M4, 268 mẫu, tạo parser/metadata/KPI bản thử.
- **GitHub:** Sáu script Python P1 đã được gộp vào `main` qua [PR #5](https://github.com/Grant-Tung/DoAnDanhGiaHieuNang/pull/5); shell runner/NetEm P2 cũng trên `main`.
- **Mới thêm (06/11):** `batch_process.py` (pipeline tự động cho 100 run), `plot_kpi.py` (5 biểu đồ), sửa `analyze_runs.py` (MAE tính trên tất cả mẫu, bao gồm fallback).
- **Tiếp theo:** Tùng chạy 100 run main, Tuyến chạy `batch_process.py --phase main` để xử lý và `plot_kpi.py --phase main` để vẽ biểu đồ.

**Phạm vi đánh giá không đổi:** 4 mode (M1–M4), 5 kịch bản (S0–S4), 5 lần lặp = 100 run. Localhost và log giả lập chỉ dùng thử công cụ, không phải số liệu kết luận.

## Chạy nhanh (sau khi có dữ liệu)

```bash
# 1. Xử lý tất cả run (convert → parse → analyze → gộp KPI)
python scripts/batch_process.py --phase pilot   # hoặc main
# → Output: runs/pilot/kpi_summary.csv, kpi_by_mode_scenario.csv

# 2. Vẽ biểu đồ
pip install matplotlib   # chỉ cần lần đầu
python scripts/plot_kpi.py --phase pilot
# → Output: runs/pilot/charts/chart1_*.png ... chart5_*.png
```

## Vòng đời của một ý tưởng

```
Góp ý mới ──► phanbien_nangcap.md  (ghi: ⏳ chờ duyệt)
                  │
        Cả hai bàn, quyết định
           │                 │
     ✅ Chấp nhận        ❌ Bác bỏ
           │                 │
  Chuyển vào doan.md    Giữ trong phanbien, ghi lý do
  (Phần B + Phần A nếu cần, ghi mục 19)
           │
  Cập nhật khối "Trạng thái hiện tại" trong phantich.md
```

## Khi dùng AI
- Mở cuộc trò chuyện mới → dán (hoặc đính kèm) `phantich.md` + `doan.md` → nói: *"Đọc khối BÀN GIAO trong phantich.md rồi tiếp tục việc tiếp theo."*
- Xong buổi làm việc → nhắc AI: *"Cập nhật doan.md (tiến độ, lịch sử) và khối Trạng thái hiện tại trong phantich.md."* → commit + push.

## Cách làm việc với 2 nhánh

| Nhánh | Ai sửa |
|---|---|
| `main` | Bản đã thống nhất — **không sửa trực tiếp** |
| `Tung` | Tùng |
| `Tuyen` | Tuyến |

### Mỗi lần làm việc
```bash
git checkout Tung              # Tuyến dùng: git checkout Tuyen
git pull origin main           # lấy bản thống nhất mới nhất về nhánh mình
# ... sửa file ...
git add .
git commit -m "Mô tả ngắn việc đã làm"
git push origin Tung
```

### So sánh và gộp
- Xem khác nhau giữa 2 nhánh: trên GitHub mở `Compare` → chọn `Tung` ... `Tuyen`
  hoặc trên máy: `git diff origin/Tung origin/Tuyen -- doan.md`
- Bên nào hợp lý → tạo **Pull Request** từ nhánh đó vào `main` → cả hai xem → **Merge**.
- Sau khi merge, người còn lại chạy `git pull origin main` trên nhánh mình để cập nhật.
- Nếu GitHub báo **conflict** (hai người sửa cùng một dòng): mở file, giữ đoạn đúng, xoá các dòng `<<<<<<<`, `=======`, `>>>>>>>`, rồi commit.

### Quy ước
- Mỗi commit nhỏ, một việc; message ghi rõ (ví dụ: `T10: thêm config_scenario.sh`).
- Thêm dòng vào mục "Lịch sử thay đổi file" trong `doan.md` khi sửa nội dung quan trọng.
- Script và dữ liệu sau này: `scripts/`, `results/`, `logs/` (log/PCAP lớn không đưa lên Git — lưu Drive và ghi đường dẫn trong metadata).
