# Quy tắc sử dụng Model & Tối ưu hóa Token (Memory & System Rule)

## 1. Phân định vai trò Model
- **Claude / GPT (Bộ não chiến lược - High-level Brain):**
  - Đóng vai trò hoạch định kế hoạch, phân tích logic kiến trúc, suy nghĩ giải pháp phức tạp và đưa ra quyết định cốt lõi.
  - **TUYỆT ĐỐI KHÔNG** tự ý dùng Claude hoặc GPT cho các tác vụ tiêu tốn nhiều token (đọc khối lượng lớn tài liệu, quét file dài, tạo ảnh, sinh báo cáo đồ sộ) khi chưa có sự xác nhận của người dùng.

- **Gemini (Thực thi & Tác vụ tốn Token - Token-Heavy Execution):**
  - Chuyên trách các công việc xử lý dữ liệu lớn, quét mã nguồn diện rộng, đọc tài liệu dài, sinh hình ảnh hoặc xuất báo cáo văn bản chi tiết nhằm tiết kiệm token.

## 2. Quy tắc bắt buộc trước khi hành động
- **Luôn luôn hỏi ý kiến người dùng** trước khi chuyển sang hoặc sử dụng Claude / GPT cho bất kỳ tác vụ nào có tính chất tiêu tốn lượng token lớn.
- Nếu người dùng đang chọn model Claude/GPT mà có tác vụ nặng (như đọc hàng loạt tài liệu hoặc tổng hợp báo cáo dài), trợ lý phải chủ động thông báo/hỏi người dùng hoặc đề xuất thực hiện qua Gemini để tối ưu chi phí.
