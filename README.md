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

## Tiến độ gần nhất (26/10/2026)

- **Đã xác nhận:** Tùng có NetEm S0–S4 và pilot S0/S4 **8/8 run đạt** (24/10; xem `doan.md` mục 12). Tuyến kiểm thử localhost đủ M1–M4, 268 mẫu, tạo parser/metadata/KPI bản thử.
- **GitHub:** Sáu script Python P1 đã được gộp vào `main` qua [PR #5](https://github.com/Grant-Tung/DoAnDanhGiaHieuNang/pull/5); shell runner/NetEm P2 cũng trên `main`.
- **Chưa hoàn tất:** chuyển và phân tích log pilot NetEm thực tế bằng parser P1, kiểm chứng request/response khi mất gói, đúng 120 request sau warm-up, QA kết quả 100 run và báo cáo cuối.
- **Tiếp theo:** Tùng bàn giao log S0/M4 từ pilot; Tuyến xác minh CSV/KPI, rồi kiểm tra S4/S3 trước khi xử lý ma trận chính.

**Phạm vi đánh giá không đổi:** 4 mode (M1–M4), 5 kịch bản (S0–S4), 5 lần lặp = 100 run. Localhost và log giả lập chỉ dùng thử công cụ, không phải số liệu kết luận.

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
