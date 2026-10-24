# Đồ án: Đánh giá hiệu năng NTPv4 / NTPv5

Nhóm: Tùng (P2 — mạng & thực nghiệm), Tuyến (P1 — giao thức & dữ liệu).

## Các file

| File | Dành cho | Nội dung |
|---|---|---|
| `doan.md` | Cả nhóm | **Sổ theo dõi chính**: tổng quan, phân tích draft, kịch bản, tiến độ, nhật ký thí nghiệm, ý tưởng, chuẩn bị bảo vệ |
| `phanbien_nangcap.md` | Cả nhóm | Phản biện phương pháp, kế hoạch A–E, tiêu chí nghiệm thu, câu hỏi trước khi chạy 100 run |
| `phantich.md` | AI | Context để dán cho AI khác đọc |

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
