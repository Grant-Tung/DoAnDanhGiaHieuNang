# Sổ theo dõi Đồ án: Đánh giá hiệu năng NTPv5

> **Người dùng chung:** Tùng (P2) và Tuyến (P1).
> **Cập nhật lần cuối:** 24/10/2026 (Tùng).
> File `phantich.md` (cùng thư mục) là bản context viết cho AI. File này là bản cho **người đọc** — dùng để theo dõi công việc, ghi kết quả test và làm nguồn viết báo cáo.

## Mục lục
1. [Cách dùng file này](#1-cách-dùng-file-này)
2. [Tổng quan đồ án](#2-tổng-quan-đồ-án)
3. [Tài liệu nghiên cứu: loại tài liệu, trạng thái, tác giả, trích dẫn](#3-tài-liệu-nghiên-cứu)
4. [Kiến thức nền](#4-kiến-thức-nền)
5. [Phân tích draft-ietf-ntp-ntpv5-09](#5-phân-tích-draft-ietf-ntp-ntpv5-09)
6. [Công cụ thực nghiệm ntp5-exp: những gì đã kiểm tra](#6-công-cụ-thực-nghiệm-ntp5-exp)
7. [Môi trường lab & topology](#7-môi-trường-lab--topology)
8. [Kịch bản thử nghiệm](#8-kịch-bản-thử-nghiệm)
9. [Dự đoán kết quả](#9-dự-đoán-kết-quả)
10. [Quy ước dữ liệu, KPI, biểu đồ](#10-quy-ước-dữ-liệu-kpi-biểu-đồ)
11. [Theo dõi tiến độ](#11-theo-dõi-tiến-độ)
12. [Nhật ký thí nghiệm](#12-nhật-ký-thí-nghiệm)
13. [Kho ý tưởng](#13-kho-ý-tưởng)
14. [Chuẩn bị bảo vệ: câu hỏi hội đồng](#14-chuẩn-bị-bảo-vệ)
15. [Giới hạn của đồ án](#15-giới-hạn-của-đồ-án)
16. [Câu hỏi mở cần kiểm chứng](#16-câu-hỏi-mở-cần-kiểm-chứng)
17. [Ghi chú viết báo cáo](#17-ghi-chú-viết-báo-cáo)
18. [Cheat sheet lệnh](#18-cheat-sheet-lệnh)
19. [Lịch sử thay đổi file](#19-lịch-sử-thay-đổi-file)

---

## 1. Cách dùng file này

- **Ký hiệu trạng thái:** ✅ xong · 🔄 đang làm · ⏭️ làm tiếp theo · ⬜ chưa làm · ❓ chưa rõ / cần kiểm tra · ❌ bỏ
- Làm xong việc gì → sửa trạng thái ở **mục 11**, ghi tên + ngày.
- Chạy một lần thử nghiệm → thêm một dòng vào **mục 12**.
- Nghĩ ra ý tưởng → thêm vào **mục 13** (đừng xoá ý tưởng bị bỏ, đổi trạng thái thành ❌ và ghi lý do).
- Sửa file → thêm một dòng ở **mục 19**.
- Mọi điều đã kết luận phải có **nguồn** (draft, code, lệnh đã chạy). Điều chưa chắc ghi ❓.

---

## 2. Tổng quan đồ án

### 2.1 Đề tài
**Đánh giá hiệu năng giao thức đồng bộ thời gian NTPv5.**
Đề xuất chỉnh tên (nếu còn sửa được): *"Đánh giá hiệu năng và giới hạn của giao thức NTPv5 (draft-09) trong môi trường mạng giả lập"* — chữ "và giới hạn" báo trước rằng đồ án chỉ ra cả điểm yếu, khớp với kết quả dự kiến.

### 2.2 Đồ án trả lời câu hỏi gì
> Khi mạng xấu (chậm, giật, mất gói, đi–về không đều), NTPv5 có chỉnh giờ chính xác hơn NTPv4 không? Vì sao?

So sánh 3 chế độ:

| Chế độ | Ý nghĩa |
|---|---|
| NTPv4 Basic | Bản cũ (RFC 5905, 2010), cách hỏi giờ thông thường |
| NTPv5 Basic | Bản mới, cùng cách hỏi giờ thông thường |
| NTPv5 Interleaved | Bản mới, server báo giờ gửi chính xác của lần trước |

### 2.3 Câu hỏi nghiên cứu (RQ)

| RQ | Câu hỏi | Kết quả dự kiến | Kịch bản |
|---|---|---|---|
| RQ1 | NTPv5 có chính xác hơn NTPv4 dưới mạng xấu? | Gần như bằng nhau | S0–S4 |
| RQ2 | Bất đối xứng ảnh hưởng thế nào? | Cả 3 lệch đúng (d↓−d↑)/2, khớp lý thuyết | S4, S5a |
| RQ3 | Interleaved giúp bao nhiêu khi không có phần cứng? | Chỉ vài chục µs | S0, S5b |
| RQ4 | Mất gói ảnh hưởng Interleaved thế nào? | Mất mẫu nhiều hơn, tự rơi về Basic | S3, S5a |
| RQ5 | Mất gói có ép client từ v5 về v4? | Có thể có (điểm yếu ít tài liệu nói tới) | S5c |
| RQ6 | Chi phí của NTPv5? | Gói 180 B vs 48 B (×3,75); thời gian khởi động lâu hơn | Tất cả |

### 2.4 Kết luận dự kiến (một câu)
NTPv5 là bước tiến về **thiết kế và bảo mật**, không phải về **độ chính xác**: thiếu timestamp phần cứng thì không vượt NTPv4, và bất đối xứng vẫn là "điểm mù" chung của mọi phiên bản.

> Kết quả "NTPv5 không thắng" **không phải kết quả xấu**. Đánh giá hiệu năng = đo đúng + giải thích được + khớp lý thuyết, không phải chứng minh cái mới tốt hơn.

### 2.5 Phân công

| Người | Vai trò | Chương báo cáo |
|---|---|---|
| P1 – Tuyến | Giao thức & dữ liệu: lý thuyết, schema CSV, lọc dữ liệu, MAE/P95, biểu đồ, phân tích kết quả | Ch.2 (lý thuyết), Ch.4 (kết quả) |
| P2 – Tùng | Mạng & thực nghiệm: Ubuntu, namespace, NetEm, runner, chạy ma trận | Ch.3 (phương pháp) |

---

## 3. Tài liệu nghiên cứu

### 3.1 Loại tài liệu: Internet-Draft, KHÔNG phải bài báo khoa học

| | Bài báo khoa học | Internet-Draft (tài liệu ta dùng) |
|---|---|---|
| Mục đích | Công bố phát hiện nghiên cứu | Đặc tả giao thức để phần mềm cài đặt theo |
| Ai duyệt | Vài người phản biện ẩn danh | Công khai trên mailing list nhóm làm việc IETF |
| Có thay đổi không | Đăng xong cố định | **Còn sửa** (đã ~18 phiên bản từ 2020) |
| Trích dẫn | Bình thường | IETF quy định chỉ ghi là **"work in progress"** |

### 3.2 Trạng thái (theo IETF Datatracker, kiểm tra 24/10/2026)

| Mục | Giá trị | Nghĩa |
|---|---|---|
| Tên | draft-ietf-ntp-ntpv5-09 | `ietf-ntp` = tài liệu của nhóm làm việc NTP |
| Loại | Active Internet-Draft (ntp WG) | Đang hoạt động |
| Thay thế | draft-mlichvar-ntp-ntpv5 | Bắt đầu là bản nháp cá nhân (11/2020), sau được nhóm nhận |
| WG state | **WG Document** | Nhóm NTP đã chấp nhận làm tài liệu chung |
| IESG state | **I-D Exists** | Chưa gửi lên ban duyệt cuối → còn xa mới thành RFC |
| Intended RFC status | (None) trên Datatracker; header draft ghi Standards Track | Chưa chốt |
| Shepherd / Consensus | None / Unknown | Chưa tới giai đoạn chốt |
| Bản mới nhất | -09, 01/07/2026, hết hạn 02/01/2027 | Vẫn làm tích cực (03/2026 và 07/2026) |
| Đã thành RFC? | **Chưa** | |

→ NTPv5 **chưa là chuẩn**, nhưng **đang trên đường chính thức**. Chi tiết còn thay đổi → đồ án **chốt phạm vi ở bản -09 / công cụ 09+**.

### 3.3 Tác giả
- **Miroslav Lichvar (Red Hat):** phát triển chính và duy trì **chrony** (phần mềm đồng bộ giờ mặc định trên RHEL, Fedora, nhiều bản Linux). Đồng tác giả **RFC 9769 "NTP Interleaved Modes"** (với A. Malhotra, 2025, Proposed Standard — chuẩn hoá Interleaved cho NTPv4). Tác giả công cụ `ntp5-exp` mà nhóm dùng.
- **Tal Mizrahi (Huawei):** đồng tác giả nhiều RFC về timestamp và bảo mật đồng bộ giờ, ví dụ RFC 7384, RFC 7822, RFC 8877 ❓ *(theo hiểu biết, chưa tra lại — kiểm tra trên rfc-editor.org trước khi đưa vào báo cáo)*. Nền PTP → giải thích vì sao NTPv5 có Correction field.

### 3.4 Cách trích dẫn
> M. Lichvar, T. Mizrahi, "Network Time Protocol Version 5", Internet-Draft draft-ietf-ntp-ntpv5-09, IETF, July 2026, work in progress.

### 3.5 Tài liệu tham khảo nên dùng

| Tài liệu | Loại | Dùng cho |
|---|---|---|
| draft-ietf-ntp-ntpv5-09 | Internet-Draft | Đối tượng đánh giá |
| RFC 5905 (NTPv4) | Chuẩn | So sánh, công thức offset/delay |
| RFC 8915 (Network Time Security) | Chuẩn | Bảo mật NTP |
| RFC 7384 (Security Requirements of Time Protocols) | Chuẩn (thông tin) | Delay attack, bất đối xứng |
| RFC 7822 (NTPv4 Extension Fields) | Chuẩn | Nguồn gốc thiết kế EF của NTPv5 |
| Malhotra et al., "Attacking the Network Time Protocol", NDSS 2016 | Bài báo hội nghị (phản biện) | Lỗ hổng NTPv4 → động lực cho NTPv5 |
| D. L. Mills, *Computer Network Time Synchronization* | Sách | Nền tảng lý thuyết NTP |
| tc-netem (man page Linux) | Tài liệu công cụ | Phương pháp giả lập |
| https://github.com/mlichvar/ntp5-exp | Mã nguồn | Công cụ thực nghiệm |

Nguyên tắc: **tài liệu đã kiểm chứng** cho phần nền tảng + **bản nháp mới nhất** cho đối tượng đánh giá.

---

## 4. Kiến thức nền

### 4.1 NTP là gì
Đồng hồ máy tính nào cũng chạy lệch dần. NTP = máy (client) hỏi giờ một máy chuẩn (server) qua mạng để chỉnh lại. Vấn đề: câu hỏi và câu trả lời đi qua mạng mất thời gian → phải trừ phần đó đi.

### 4.2 Bốn mốc thời gian

| Ký hiệu | Sự kiện | Đồng hồ |
|---|---|---|
| T1 | client gửi request | client |
| T2 | server nhận request | server |
| T3 | server gửi response | server |
| T4 | client nhận response | client |

```
offset θ = [(T2 − T1) + (T3 − T4)] / 2      # đồng hồ client lệch bao nhiêu
delay  δ = (T4 − T1) − (T3 − T2)            # thời gian khứ hồi trên mạng
```

### 4.3 Giả định ngầm và điểm mù
NTP giả định **thời gian đi = thời gian về**. Nếu không bằng (d↑ ≠ d↓):
```
sai số offset = (d↑ − d↓) / 2
```
**Không giao thức hỏi–đáp hai chiều nào phát hiện được sai số này** — kể cả NTPv5.
Ví dụ: gọi điện hỏi giờ, tiếng đi mất 1 s, tiếng về mất 3 s → bạn chỉnh sai 1 s mà không biết.

### 4.4 Basic vs Interleaved (ví dụ đời thường)
- **Basic:** ghi giờ gửi lên phong bì *trước khi* dán → thư còn nằm chờ trên bàn → giờ ghi sớm hơn thật.
- **Interleaved:** gửi xong mới ghi giờ chính xác, rồi báo giờ đó trong **lá thư sau**. Chính xác hơn nhưng thông tin đến **chậm một lượt**.

---

## 5. Phân tích draft-ietf-ntp-ntpv5-09

### 5.1 Thay đổi cốt lõi so với NTPv4

**Header vẫn 48 byte** (bằng NTPv4). Phần mở rộng (Extension Field, EF) nối phía sau, độ dài tuỳ ý, làm tròn bội số 4.

| Trường | NTPv4 | NTPv5-09 | Ý nghĩa |
|---|---|---|---|
| Word 1 | LI, VN, Mode, Stratum, Poll, Precision | Giữ bố cục, VN cùng vị trí | Phân biệt phiên bản |
| Root Delay / Dispersion | 32 bit, ~15 µs | 32 bit, ~3,7 ns, tối đa 16 s | Khai báo sai số mịn hơn |
| Reference ID | 32 bit | Bỏ khỏi header → ID 120 bit trong Bloom filter 4096 bit (qua EF) | Phát hiện vòng lặp thời gian |
| Reference Timestamp | 64 bit | Bỏ khỏi header (EF tuỳ chọn) | |
| Origin Timestamp | 64 bit, kiêm chống giả mạo | Bỏ → **Client Cookie** 64 bit ngẫu nhiên | Client không lộ giờ của mình |
| — | — | **Server Cookie** 64 bit | Nền tảng của Interleaved |
| — | — | Timescale 8 bit (UTC, TAI, UT1, UTC smeared) | Hỗ trợ nhiều loại giờ |
| — | — | Era 8 bit (~136 năm → ~35.000 năm) | Xử lý mốc tràn 2036 |
| — | — | Flags 16 bit: Synchronized, Interleaved, Auth-NAK | Cờ tường minh |
| MAC | Nối trần cuối gói | Bọc trong EF | Parse rõ ràng |
| Chế độ | client/server, symmetric, broadcast, mode 6, mode 7 | **Chỉ client/server** | Bỏ nguồn tấn công khuếch đại |

Khác về cơ chế:
- Draft **chỉ quy định phần trên dây**. Lọc mẫu, chọn nguồn, điều khiển đồng hồ nằm ngoài phạm vi → kết quả phụ thuộc phần mềm cài đặt.
- Response **không được dài hơn** request.
- **Không tương thích** trên dây với NTPv4 → phải thương lượng: client gửi gói v4 có Reference Timestamp = giá trị đặc biệt "NTP5NTP5" (bản draft dùng "NTP5DRFT"); server v5 echo lại → chuyển v5. Quy tắc hạ cấp trong văn bản draft ("mất 2 → về v4, chờ 256 request") ❓ chưa đối chiếu nguyên văn. **Công cụ ntp5-exp làm khác:** hạ về v4 khi > 8 lượt mất liên tiếp, nâng lại v5 ngay khi server echo (xem `phanbien_nangcap.md` mục 3).

### 5.2 Extension Fields

| Mã | Tên | Kích thước | Ghi chú |
|---|---|---|---|
| 0xF501 | Padding | tuỳ | Giữ request = response |
| 0xF502 | MAC | 4 B + MAC | Toàn vẹn dữ liệu |
| 0xF503/0xF504 | Reference IDs Req/Resp | chunk của filter 512 B | Server bắt buộc hỗ trợ |
| 0xF505 | Server Information | 8 B | Bitmask phiên bản 1–16 |
| 0xF506 | Correction | 28 B | Giống PTP; không xác thực |
| 0xF507 | Reference Timestamp | 12 B | Draft tự nghi ngờ có cần |
| 0xF508 | Monotonic Receive Timestamp | 16 B | Frequency transfer |
| 0xF509 | Secondary Receive Timestamp | 16 B | Timestamp theo timescale khác |
| 0xF5FF | Draft Identification | tuỳ | Sẽ xoá khi lên RFC |

### 5.3 Basic vs Interleaved — chi tiết kỹ thuật
- **Basic:** T3 nằm trong chính response → server ghi T3 trước khi gói rời máy → sai số ε = thời gian gói còn nằm trong máy. Hệ quả: θ_basic ≈ θ_thật − ε/2, δ_basic ≈ δ_thật + ε.
- **Interleaved:** response k mang Server Cookie C_k → request k+1 bật cờ Interleaved, gửi lại C_k → server trả **T3 thật của response k**. Mẫu luôn trễ ≥ 1 lượt; lượt đầu là Basic; server không tra được cookie → trả Basic.
- So với NTPv4 Interleaved (**RFC 9769**, Proposed Standard): v4 nhận biết ngầm qua origin timestamp (không đổi header); v5 có cờ tường minh + cookie riêng.

**Interleaved sửa được gì:**

| Nguồn sai số | Basic | Interleaved | Correction field |
|---|---|---|---|
| Hàng đợi/xử lý trong máy server | ❌ | ✅ | — |
| Hàng đợi tại switch/router | ❌ | ❌ | ✅ nếu thiết bị hỗ trợ |
| Bất đối xứng đường truyền | ❌ | ❌ | chỉ một phần |

> ⚠️ **Không được viết** "Interleaved triệt tiêu trễ hàng đợi". Viết đúng: "Interleaved giảm sai số do xử lý/hàng đợi **phía máy server**".

### 5.4 Cải tiến đáng giá
1. **Interleaved chính thức hoá** + timestamp phần cứng → loại sai số phía server.
2. **Correction field** → cơ chế duy nhất xử lý hàng đợi trong mạng (nhưng cần switch hỗ trợ — chưa có).
3. **Bảo mật:** bỏ mode 6/7 (nguồn tấn công khuếch đại kiểu `monlist`); response ≤ request (khuếch đại ≤ 1); client cookie chống giả mạo; MAC trong EF; dùng được NTS; cơ chế bảo mật do cấu hình nên không bị hạ cấp.

### 5.5 Điểm yếu (phản biện)

| # | Điểm yếu | Giải thích | Mức |
|---|---|---|---|
| 1 | Correction field không xác thực | Kẻ đứng giữa đường sửa giá trị → lệch offset tới ~δ/2 mà **không cần làm chậm gói** (khó phát hiện) | Cao |
| 2 | Bất đối xứng / delay attack | Draft thừa nhận không giải quyết; NTS cũng không giúp | Cao (giới hạn chung) |
| 3 | Đầu độc Bloom filter | Máy phía trên gửi filter toàn bit 1 → máy phía dưới tưởng có vòng lặp → bỏ nguồn tốt | Trung bình |
| 4 | Dương tính giả Bloom | ~1e-12 với 26 ID; ~1e-6 với 118 ID | Thấp ở LAN |
| 5 | Bị ép về NTPv4 khi mất gói | Theo draft (❓ chưa đối chiếu nguyên văn): mất 2 phản hồi → về v4, kẹt 256 lượt. **Công cụ:** > 8 lượt mất liên tiếp → v4, nâng lại ngay → khó đo, không đưa vào RQ lõi | Lý thuyết |
| 6 | Phản xạ (reflection) | Không khuếch đại nhưng vẫn phản xạ 1:1 được | Thấp |
| 7 | Server phải nhớ T3 cho Interleaved | Server lớn phải xoá bớt → rơi về Basic khó đoán | Trung bình |

**Mất gói phá Interleaved thế nào:**
- Server nhớ T3 theo cookie → mất gói chỉ làm mẫu đến muộn; tỷ lệ mẫu ≈ (1−p).
- Server chỉ nhớ T3 mới nhất → tỷ lệ mẫu ≈ (1−p)²; ví dụ p = 30%: Basic 70%, Interleaved ≈ 49%.
- Mất theo cụm → cookie hết hạn → về Basic.
- Hệ quả đo được: phân bố offset có **hai đỉnh** (mẫu Basic và Interleaved trộn lẫn), cách nhau ε/2.

### 5.6 Phần thừa / thiết kế quá mức (trong ngữ cảnh LAN)

| Thành phần | Nhận xét |
|---|---|
| Correction field | Cần switch hiểu NTPv5 — chưa có trên thị trường |
| Bloom filter 512 B + chia chunk | Thừa với mạng 1–4 nguồn, nhưng server bắt buộc hỗ trợ |
| UT1, Secondary Receive Timestamp | Ứng dụng hẹp (thiên văn) |
| Monotonic Receive Timestamp | Ngách |
| Reference Timestamp EF | Chính draft nghi ngờ |
| Bitmask phiên bản 1–16 | Dư |
| Era 8 bit | Hợp lý dài hạn nhưng dư |

Công bằng: Era, TAI, độ phân giải ns **không thừa** nếu nhìn dài hạn.

---

## 6. Công cụ thực nghiệm ntp5-exp

- Nguồn: https://github.com/mlichvar/ntp5-exp — clone tại `~/Desktop/ntp5-exp`.
- File chính: `ntpnode.py` (Python, vừa làm client vừa làm server).

### 6.1 Đã kiểm tra (bằng grep/sed, 24/10/2026)

| # | Điều kiểm tra | Kết quả | Hệ quả |
|---|---|---|---|
| 1 | Ghi giờ ở đâu | Chỉ bằng `time.time()` của Python (hàm `read_clock`, dòng 88–90); **không** dùng timestamp của kernel | NetEm không làm sai phép đo → **không cần router** (xem 7.3) |
| 2 | Client có chỉnh đồng hồ hệ thống không | **Không** | An toàn khi 2 namespace dùng chung đồng hồ |
| 3 | Nhiễu cố ý | `read_clock` XOR bit ngẫu nhiên (~1 µs với precision −20) | Chênh lệch < 1 µs là nhiễu, không diễn giải |
| 4 | T3 của Basic | Lấy **trước** khi soạn response | |
| 5 | T3 của Interleaved | Lấy **sau** khi soạn response, nhưng **trước** `encode()` và `sendto()` | Interleaved chỉ hơn Basic đúng bằng thời gian Python soạn gói (cỡ chục µs) → **proof-of-concept** |
| 6 | Tự rơi về Basic | Client chỉ gửi Interleaved khi `missed_responses <= 4` và response trước cùng phiên bản | Có fallback khi mất gói |
| 7 | Thương lượng phiên bản | Mặc định khởi động v4 + giá trị "NTP5DRFT", nâng v5 khi server echo; hạ v4 khi > 8 lượt mất liên tiếp; không có cơ chế 256 | S5c yếu → bỏ khỏi hướng nâng cao |
| 7b | Server lưu T3 cho Interleaved | Một dictionary chung, tối đa 1000 mục, khoá = receive timestamp. **v4: xoá mục sau khi dùng; v5: giữ lại** | Mất response: M2 (v4) rơi về Basic, M4 (v5) vẫn Interleaved → giả thuyết H2b |
| 7c | Công thức & dấu | `offset = ½[(T2−T1)+(T3−T4)]` = server − client; `delay = abs(...)`; **không lọc mẫu**, mỗi response hợp lệ 1 dòng log | S4 kỳ vọng **−15 ms** |
| 7d | Server cookie | = receive timestamp của server (không ngẫu nhiên) | Chi tiết cài đặt |
| 7e | NTPv4 Interleaved | `-v 4 -x` có hỗ trợ (cách nhận biết theo RFC 9769) | Thêm mode M2 |
| 8 | Poll mặc định | `-i 2` → hỏi 4 s/lần; 10 phút ≈ 150 mẫu | |
| 9 | Khởi động | "waiting for complete refids" đến khi nhận đủ `-f` fragment (~16 s mặc định) | Bỏ 60 s đầu mỗi run |
| 10 | Mẫu S0 đầu tiên (v5 Basic) | offset = +57 µs, delay = 493 µs | Overhead Python lớn hơn ping (~50 µs) |

### 6.2 Kích thước gói: 180 byte là gì

Đo thực tế: mặc định (`-f 4`) → **180 B**; `-f 8` → **148 B**. Phân rã khớp cả hai:

| Thành phần | Byte |
|---|---|
| Header NTPv5 | 48 |
| EF Draft Identification (`draft-ietf-ntp-ntpv5-09+`) | 28 |
| EF Server Information | 8 |
| EF Reference Timestamp | 12 |
| EF Secondary Receive Timestamp | 16 |
| EF Reference IDs (`-f 4` / `-f 8`) | 68 / 36 |
| **Tổng** | **180 / 148** |

> ⚠️ **Không được viết** "header NTPv5 là 180 byte". Header là 48 byte; 180 là tổng payload UDP. Cookie nằm trong header, không phải EF. (❓ xác nhận lần cuối bằng `tcpdump -X`)

### 6.3 Công cụ là bản "09+", khác văn bản draft-09

| Điểm | Văn bản draft-09 | ntp5-exp (09+) |
|---|---|---|
| Reference IDs | Bloom filter 4096 bit, ID 120 bit | Danh sách 32 ID × 64 bit (8 bit "share" + 56 bit ID) |
| Cờ 0x0001 | **Synchronized** (1 = đã đồng bộ) | **UNSYNCHRONIZED** (1 = chưa đồng bộ) |

→ Báo cáo ghi: *"công cụ thực nghiệm là cài đặt tham chiếu draft-09+ của tác giả, khác văn bản -09 ở …"*. Phân tích Bloom filter (5.5 #3, #4) là **lý thuyết**, lab không kiểm thử.

### 6.4 Tuỳ chọn dòng lệnh

| Cờ | Ý nghĩa | Mặc định |
|---|---|---|
| `-p PORT` | Cổng server | 10123 |
| `-v VERSION` | Ép phiên bản (4 hoặc 5) | tự thương lượng |
| `-i POLL` | Chu kỳ hỏi, log2 giây | 2 (4 s) |
| `-f NUMBER` | Số fragment Reference IDs | 4 |
| `-r RATE` | Dispersion rate | 15e-6 |
| `-m DIST` | Root distance tối đa chấp nhận | 1.0 |
| `-l` | Server dùng đồng hồ local làm chuẩn (bắt buộc cho server) | tắt |
| `-x` | Yêu cầu Interleaved | tắt |
| `-n` | Tắt kiểm tra vòng lặp refid NTPv4 | tắt |
| `-d` | Tăng mức debug | tắt |

---

## 7. Môi trường lab & topology

### 7.1 Thành phần

| Thứ thật | Giả lập bằng | Cách hiểu |
|---|---|---|
| 2 máy tính | 2 network namespace `ntp-c`, `ntp-s` | 2 "căn phòng" kín trong 1 ngôi nhà |
| Cáp mạng | Cặp veth `veth-c` ↔ `veth-s` | Ống nối thẳng 2 phòng |
| Mạng xấu | NetEm | "Phòng chờ" ở cửa ra: giữ gói (trễ), vứt gói (mất) |
| Phần mềm NTP | `ntpnode.py` | Client + server |
| Hệ điều hành | Ubuntu 22.04.5 LTS trên VMware | |

### 7.2 Topology (đang dùng)

```
┌──────────── Máy ảo Ubuntu (1 đồng hồ chung) ────────────┐
│  [ntp-c] CLIENT 10.10.0.1          [ntp-s] SERVER 10.10.0.2 │
│      veth-c ═══════════ ống nối ═══════════ veth-s        │
│      ▲ NetEm cửa ra (chiều C→S)      ▲ NetEm cửa ra (S→C) │
└──────────────────────────────────────────────────────────┘
```
- NetEm chỉ tác động gói **đi ra** → muốn chậm chiều nào thì gắn ở cửa ra của bên gửi.
- **Lợi thế:** 2 phòng chung đồng hồ → offset thật = 0 → **offset đo được = sai số**.
- **Hạn chế:** không đánh giá được 2 đồng hồ vật lý trôi lệch nhau.

### 7.3 Vì sao từng tính thêm router, rồi bỏ (nên kể trong Ch.3)

**Câu hỏi then chốt:** server ghi "giờ gửi" **trước hay sau** khi gói ngồi ở phòng chờ NetEm?
- **Trước** (chương trình tự ghi giờ rồi mới gửi): trễ NetEm được tính là trễ mạng → **đúng**.
- **Sau** (nhờ kernel ghi giờ lúc gói thật sự ra khỏi máy): trễ NetEm bị coi là "nằm trong máy server" → Interleaved xoá mất trễ → **sai, thiên vị**.

Lúc đầu chưa biết `ntpnode.py` thuộc loại nào → đề xuất **router ở giữa** (namespace thứ 3, NetEm đặt ở router) cho an toàn cả hai trường hợp.
Kiểm tra code (6.1 #1, #5): chỉ dùng `time.time()`, ghi giờ **trước** `sendto()` → trường hợp "trước" → **không cần router**.

> Câu cho báo cáo: *"Nhóm đã kiểm tra vị trí lấy timestamp trong mã nguồn để đảm bảo NetEm không làm sai lệch phép đo."*

---

## 8. Kịch bản thử nghiệm

### 8.1 Kịch bản chính S0–S4 (lab ảo)

| KB | C→S (`veth-c`) | S→C (`veth-s`) | Mục đích |
|---|---|---|---|
| S0 | không | không | Mốc chuẩn |
| S1 | delay 10ms | delay 10ms | Trễ ổn định có gây sai? |
| S2 | delay 20ms 10ms | delay 20ms 10ms | Giật thì sao? |
| S3 | delay 20ms 5ms loss 5% | delay 20ms 5ms loss 5% | Mất gói, đặc biệt với Interleaved |
| S4 | delay 10ms | delay 40ms | Bất đối xứng |

Ma trận chính (T18): 5 kịch bản × 3 chế độ × 5 lần lặp = **75 run**.
❓ Phân phối jitter khi không khai `distribution`: man page tc-netem **không nói** → phải đo (1000 ping, vẽ histogram) và ghi phân phối quan sát được vào Ch.3.

> 🔄 **Đề xuất sửa ma trận (chưa chốt)** — xem `phanbien_nangcap.md` mục 2: 4 mode (thêm M2 = NTPv4 Interleaved `-v 4 -x`), mọi kịch bản trễ trung bình 25 ms/chiều (S1 25/25; S2 25±10; S3 = S2 + loss 5%; S4 10/40), 100 run.

Script `config_scenario.sh`:
```bash
#!/usr/bin/env bash
set -e
C="sudo ip netns exec ntp-c"; S="sudo ip netns exec ntp-s"
reset() { $C tc qdisc del dev veth-c root 2>/dev/null || true; $S tc qdisc del dev veth-s root 2>/dev/null || true; }
apply() { $C tc qdisc add dev veth-c root netem $1; $S tc qdisc add dev veth-s root netem $2; }   # $1 = C→S, $2 = S→C
reset
case "$1" in
  S0)    ;;
  S1)    apply "delay 10ms"               "delay 10ms" ;;
  S2)    apply "delay 20ms 10ms"          "delay 20ms 10ms" ;;
  S3)    apply "delay 20ms 5ms loss 5%"   "delay 20ms 5ms loss 5%" ;;
  S4)    apply "delay 10ms"               "delay 40ms" ;;
  reset) ;;
  *) echo "usage: $0 S0|S1|S2|S3|S4|reset"; exit 1 ;;
esac
$C tc -s qdisc show dev veth-c; $S tc -s qdisc show dev veth-s
```

Kiểm chứng (T11): `sudo ./config_scenario.sh Sx` → `sudo ip netns exec ntp-c ping -c 20 10.10.0.2`

| KB | RTT trung bình kỳ vọng | Loss kỳ vọng |
|---|---|---|
| S0 | < 0,1 ms | 0% |
| S1 | ~20 ms | 0% |
| S2 | ~40 ms, dao động mạnh | 0% |
| S3 | ~40 ms | ~10% (20 gói mất 1–3 là bình thường) |
| S4 | ~50 ms | 0% |

### 8.2 Kịch bản nâng cao S5 (lab ảo, T21)

**S5a — Bất đối xứng + mất gói theo cụm**
```bash
sudo ip netns exec ntp-c tc qdisc add dev veth-c root netem delay 2ms 0.2ms distribution normal
sudo ip netns exec ntp-s tc qdisc add dev veth-s root netem delay 22ms 2ms distribution pareto loss gemodel 5% 30% 70% 0.1%
```
- Quét chênh lệch d↓ − d↑ ∈ {0, 5, 10, 20, 50} ms → sai số offset là đường thẳng hệ số 0,5, trùng nhau cho 3 chế độ.
- Interleaved: histogram offset (tìm hai đỉnh), tỷ lệ rơi về Basic theo mức loss.

**S5b — Nghẽn một chiều + server quá tải** (kịch bản Interleaved có thể thắng rõ nhất)
```bash
sudo ip netns exec ntp-s tc qdisc add dev veth-s root netem delay 5ms 10ms 25% rate 10mbit limit 1000
sudo ip netns exec ntp-s iperf3 -s &
sudo ip netns exec ntp-c iperf3 -c 10.10.0.2 -u -b 9M -t 120 -R      # bật/tắt theo chu kỳ
sudo ip netns exec ntp-s stress-ng --cpu 2 --io 2                     # cần cài stress-ng
```

**S5c — Bị ép về NTPv4 khi mất gói** (RQ5)
- Client chạy **không có `-v`** (tự thương lượng); tăng loss dần 5 → 30% (dùng `gemodel`).
- Ghi phiên bản thực tế theo thời gian → bắt thời điểm rơi về v4.
- ❌ **Đã hạ ưu tiên:** công cụ chỉ hạ v4 khi > 8 lượt mất liên tiếp và nâng lại ngay → kết quả nói về công cụ, không về giao thức. Hướng nâng cao được chọn: **chèn trễ xử lý phía server** (`phanbien_nangcap.md` mục 6).
- Cần thêm cột `version_actual` vào CSV.

### 8.3 Kịch bản bắt buộc dùng máy thật (tuỳ chọn, sau T18)

| Mã | Kịch bản | Vì sao không giả lập được | Cần gì | Ưu tiên |
|---|---|---|---|---|
| P1 | **Wi-Fi thật** | Tranh kênh, gửi lại ở tầng sóng, ngủ tiết kiệm pin, upload/download không đều → bất đối xứng thật thay đổi liên tục | 1 laptop có Wi-Fi + LAN, 1 router Wi-Fi | **1** |
| P2 | **Timestamp phần cứng** (chrony + NTPv4) | Chip trên card mạng ghi giờ lúc gói ra dây; VM và Python không có | Card mạng có HW timestamp (Intel i210/i350/X710) — mượn lab trường | **2** |
| P3 | **Hai đồng hồ vật lý** | Thạch anh thật trôi theo nhiệt, tải — mô hình toán không bắt chước sát | 2 máy + nguồn giờ chuẩn (PTP/GPS) | 3 |

**P1 — giữ được "giờ chuẩn":** 1 laptop, client namespace dùng card Wi-Fi, server namespace dùng cổng LAN, cùng nối 1 router → vẫn chung đồng hồ, gói đi qua Wi-Fi thật. ❓ Chuyển card Wi-Fi vào namespace phải chuyển theo `phy` (`iw phy phy0 set netns name ntp-c`) và chạy kết nối Wi-Fi trong namespace — cần thử.

**P2 — ma trận 4 cấu hình** (chrony, NTPv4):

| | Timestamp phần mềm | Timestamp phần cứng |
|---|---|---|
| Basic | ① | ② |
| Interleaved | ③ | ④ |

Kỳ vọng ④ tốt hơn hẳn (cỡ dưới µs). Cấu hình: server `hwtimestamp *`; client `server <IP> xleave`. Nếu client và server cùng máy (chung đồng hồ) → chạy client với `chronyd -x` (không chỉnh đồng hồ hệ thống). Kiểm tra card: `ethtool -T <card>` phải có `hardware-transmit`. ❓ Kiểm tra chrony trên máy lab đã hỗ trợ NTPv5 chưa.

**Phương án mượn lab (1 máy, 2 card mạng, đi qua switch/router thật):**
```bash
sudo ip link set enp1s0 netns ntp-c     # tên card xem bằng: ip link
sudo ip link set enp2s0 netns ntp-s
```
Vẫn chung đồng hồ; gói đi qua cáp và thiết bị thật. Nghẽn thật: `iperf3` qua switch. Bất đối xứng thật: 2 router, chiều đi/về khác đường.

Danh sách mượn: 1 PC có 2 cổng mạng (card USB-LAN thường không có HW timestamp), 1 switch (tốt nhất managed) hoặc 2 router, 2–3 cáp, thêm 1 máy chạy `iperf3`.
Hỏi lab: được cài/boot Ubuntu không? Card mạng loại gì? Được cấu hình router/switch không? Mượn bao lâu?
Câu xin mượn: *"em cần máy có card mạng hỗ trợ hardware timestamping"*.

### 8.4 Không test được (kể cả máy thật) — ghi vào giới hạn

| Tính năng | Lý do |
|---|---|
| Correction field | Chưa có switch hiểu NTPv5 |
| Timestamp phần cứng với ntp5-exp | Công cụ Python, không đọc được HW timestamp |
| Bloom filter của draft-09 | Công cụ 09+ dùng cơ chế khác (6.3) |

---

## 9. Dự đoán kết quả

> Dự đoán **lý thuyết**, dùng để đối chiếu. Giả định: KPI tính trên **từng mẫu thô** trong log, chưa qua bộ lọc. Offset thật = 0 → offset đo = sai số.

| KB | Delay | Sai số offset (MAE / P95) | v4 Basic vs v5 Basic | v5 Interleaved |
|---|---|---|---|---|
| S0 | ~0,3–0,5 ms | vài chục µs | Bằng nhau | **Tốt hơn chút** (delay nhỏ hơn vài chục µs) |
| S1 | ~20,5 ms | vài chục µs | Bằng nhau | Bằng nhau |
| S2 | 20–60 ms | **~3,3 ms / ~7,8 ms** | Bằng nhau | Bằng nhau |
| S3 | 30–50 ms | **~1,7 ms / ~3,9 ms**; ~90% lượt hỏi thành công (~135/150 mẫu) | Bằng nhau | Sai số tương đương, **ít mẫu hơn**, có lúc về Basic |
| S4 | ~50 ms | **~15 ms / ~15 ms** (lệch cố định) | Bằng nhau | **Bằng nhau, cùng lệch 15 ms** |

Cách tính:
- **S2:** mỗi chiều giật đều ±10 ms → offset = (giật chiều đi − giật chiều về)/2 → phân phối tam giác trên [−10, 10] ms → MAE = 10/3 ≈ 3,3 ms; P95 = 10·(1 − √0,05) ≈ 7,8 ms.
- **S3:** tương tự với ±5 ms → MAE ≈ 1,7 ms; P95 ≈ 3,9 ms. Lượt hỏi thành công ≈ 0,95 × 0,95 ≈ 90%.
- **S4:** offset = server − client (đã xác minh trong mã) → (d↑ − d↓)/2 = (10 − 40)/2 = **−15 ms**.
- ❓ Các giá trị MAE/P95 của S2/S3 giả định jitter phân phối đều — chưa kiểm chứng; chỉ là tham chiếu, **không đưa vào phần kết quả**.

**Nếu kết quả khác dự đoán:**

| Thấy | Có thể do |
|---|---|
| S1 sai số lớn hơn nhiều S0 | NetEm 2 chiều cấu hình không bằng nhau |
| S4 lệch +15 thay vì −15 | Quy ước dấu, không phải lỗi |
| S4 lệch khác xa 15 ms | NetEm gắn nhầm chiều/cửa |
| S2/S3 sai số nhỏ hơn nhiều | Script có lọc mẫu → tốt, nhưng phải ghi rõ |
| v4 và v5 Basic khác rõ | Gói 180 B vs 48 B → Python xử lý lâu hơn? Đáng điều tra |

---

## 10. Quy ước dữ liệu, KPI, biểu đồ

### 10.1 Cột dữ liệu (schema CSV — Tuyến chốt)

| Cột | Nguồn |
|---|---|
| `run_id`, `scenario`, `rep`, `timestamp` | Runner |
| `mode_requested` | Cờ dòng lệnh: `-v 4` → v4 Basic; `-v 5` → v5 Basic; `-v 5 -x` → v5 Interleaved |
| `mode_actual` | Log có chuỗi `Interleaved mode` → Interleaved; không có → Basic |
| `version_actual` | Phiên bản thực tế (cho S5c) |
| `offset`, `delay`, `rdist`, `stratum` | Log dạng `Basic mode offset=+0.000057 delay=0.000493 rdist=0.000247 stratum=1` (đơn vị **giây**) |

Quy tắc: **bỏ 60 s đầu** mỗi run (chờ đủ refids + lượt Interleaved đầu).

### 10.2 KPI
- MAE và P95 của |offset|
- Trung bình, độ lệch chuẩn của delay
- Tỷ lệ mẫu hữu dụng = số mẫu / số request
- Tỷ lệ fallback = mẫu `mode_actual = Basic` khi `mode_requested = Interleaved`
- Chi phí: kích thước gói, băng thông/giờ, thời gian tới khi đồng bộ

### 10.3 Biểu đồ nên có
1. Offset theo thời gian, S4, 3 chế độ + đường lý thuyết −15 ms
2. Boxplot |offset| theo chế độ × kịch bản
3. Histogram offset của Interleaved ở S3 (tìm hai đỉnh)
4. Sai số offset theo mức bất đối xứng (S5a) — đường hệ số 0,5
5. Tỷ lệ fallback theo mức loss
6. Phiên bản thực tế theo thời gian (S5c)

---

## 11. Theo dõi tiến độ

| Task | Nội dung | Người | Trạng thái | Ghi chú |
|---|---|---|---|---|
| T01–T03 | Chuẩn bị lý thuyết/dữ liệu | Tuyến | ❓ | Tuyến cập nhật |
| T04 | Ubuntu 22.04.5 + công cụ + clone ntp5-exp | Tùng | ✅ | |
| T05 | 2 namespace + veth, ping OK | Tùng | ✅ | |
| T06 | Duyệt kịch bản | Cả hai | ⬜ | Duyệt mục 8 |
| T07–T08 | Schema CSV, `export_logs.py` | Tuyến | ❓ | Xem mục 10.1 |
| T09 | Chạy được 3 chế độ | Tùng | ✅ | Server cần `-l` |
| — | Kiểm tra mã `ntpnode.py` | Tùng | ✅ 24/10 | Mục 6 |
| T10 | `config_scenario.sh` | Tùng | ⏭️ | Mục 8.1 |
| T11 | Kiểm chứng qdisc + ping S1–S4 | Tùng | ⬜ | Bảng ở mục 8.1 |
| T12–T14 | Pipeline phân tích | Tuyến | ⬜ | |
| T15–T17 | Runner + pilot (S0, S4) | Tùng | ⬜ | |
| T18 | Ma trận chính 75 run | Tùng | ⬜ | |
| T19–T20 | QA dữ liệu + PCAP | Tuyến | ⬜ | Xác nhận 180 B bằng PCAP |
| T21 | S5 nâng cao (S5a, S5b, S5c) | Tùng | ⬜ | |
| T22–T24 | KPI, biểu đồ, Ch.2 & Ch.4 | Tuyến | ⬜ | |
| T25–T26 | Ch.3, chạy lại run lỗi | Tùng | ⬜ | |
| T27–T30 | Báo cáo, slide, demo, đóng gói mã | Cả hai | ⬜ | |
| (tuỳ chọn) | Máy thật P1 Wi-Fi | Tùng | ⬜ | Sau T18 |
| (tuỳ chọn) | Máy thật P2 HW timestamp | Tùng | ⬜ | Cần mượn lab |

---

## 12. Nhật ký thí nghiệm

> Mỗi lần chạy thêm một dòng. Run lỗi vẫn ghi (ghi lý do), không xoá.

| Ngày | Run ID | KB | Chế độ | Thời lượng | Người | Kết quả chính | Ghi chú |
|---|---|---|---|---|---|---|---|
| 24/10/2026 | thử-01 | S0 | v5 Basic | vài lượt | Tùng | offset +57 µs, delay 493 µs | Mẫu đầu tiên, chưa chạy runner |
| 24/10/2026 | thử-02 | S0 | v5 Basic `-f 8` | vài lượt | Tùng | gói 148 B | Kiểm chứng phân rã 180 B |
| | | | | | | | |

---

## 13. Kho ý tưởng

| # | Ý tưởng | Giá trị | Trạng thái |
|---|---|---|---|
| I1 | Router ở giữa (namespace thứ 3) | An toàn nếu script dùng timestamp kernel | ❌ Không cần — script dùng `time.time()` (mục 7.3) |
| I2 | S5c: đo bị ép về v4 khi mất gói | Phát hiện ít tài liệu nói tới (RQ5) | ⬜ |
| I3 | S5b: server quá tải CPU | Kịch bản Interleaved có thể thắng rõ | ⬜ |
| I4 | Đo chi phí (byte, băng thông, thời gian khởi động) | Đúng tinh thần "hiệu năng mạng" | ⬜ |
| I5 | So sánh `-f 4` vs `-f 8` vs nhiều hơn | Ảnh hưởng tới kích thước gói và thời gian khởi động | ⬜ |
| I6 | P1 Wi-Fi thật (1 laptop) | Kiểm chứng ngoài thực tế, rẻ | ⬜ |
| I7 | P2 HW timestamp với chrony | Chứng minh "Interleaved cần phần cứng" | ⬜ cần mượn lab |
| I8 | Mô phỏng đồng hồ trôi bằng cách sửa `read_clock()` | Đo ảnh hưởng độ trễ 1 lượt của Interleaved | ⬜ |
| I9 | Đổi tên đề tài thêm "và giới hạn" | Khớp kết quả dự kiến | ⬜ hỏi GVHD |
| I10 | Tạo trang ngắn xin mượn thiết bị gửi GV lab | | ⬜ |

---

## 14. Chuẩn bị bảo vệ

| Hội đồng có thể hỏi | Trả lời |
|---|---|
| Sao đánh giá cái chưa phải chuẩn? | Đã được nhóm NTP của IETF nhận (WG Document), hướng tới Standards Track; đánh giá giai đoạn nháp giúp góp ý thiết kế (QUIC cũng từng được đo nhiều khi còn nháp); dùng cài đặt tham chiếu của chính tác giả |
| Kết quả không có gì mới? | Định lượng được: Interleaved chỉ hiệu quả khi có phần cứng; bất đối xứng là giới hạn chung, khớp lý thuyết; mất gói làm Interleaved suy giảm và có thể ép về v4 |
| Lab ảo có thực tế không? | Có giới hạn (chung đồng hồ, không HW timestamp) nhưng có tham chiếu tuyệt đối và điều kiện lặp lại được; (nếu làm) đã kiểm chứng trên Wi-Fi/phần cứng thật |
| Draft ra bản mới thì sao? | Đánh giá ghi rõ bản -09/09+; kết luận về bất đối xứng và Interleaved dựa trên nguyên lý, không phụ thuộc chi tiết gói |
| Gói 180 byte gồm gì? | Bảng mục 6.2 — header 48 B + 5 EF |
| Sao NetEm không làm sai Interleaved? | Đã kiểm tra mã: timestamp lấy trước `sendto()`, NetEm nằm sau (mục 7.3) |
| Tác giả là ai, có đáng tin? | Lichvar (chrony, Red Hat) + Mizrahi (Huawei, nhiều RFC về timestamp) |

---

## 15. Giới hạn của đồ án

1. Hai namespace **chung đồng hồ** → không đánh giá được đồng hồ vật lý trôi lệch, vòng điều khiển đồng hồ.
2. **Không có timestamp phần cứng** (veth ảo, công cụ Python) → Interleaved chỉ thể hiện được một phần lợi ích.
3. Công cụ là **draft-09+**, khác văn bản -09 (Reference IDs, ngữ nghĩa cờ 0x0001).
4. NTPv5 **còn là bản nháp** → chi tiết có thể đổi ở bản sau.
5. Mạng xấu là **giả lập** (NetEm), phân phối jitter là mô hình (đều/chuẩn/pareto), không phải mạng thật.
6. **Không kiểm thử được** Correction field, Bloom filter, bảo mật NTS/MAC.
7. Chạy trên **máy ảo VMware** → có nhiễu do hypervisor ở mức µs.

---

## 16. Câu hỏi mở cần kiểm chứng

| # | Câu hỏi | Cách kiểm tra | Ai | Trạng thái |
|---|---|---|---|---|
| Q1 | Server lưu T3 cho Interleaved thế nào? | Đọc mã `master` | AI | ✅ dictionary 1000 mục; v4 xoá, v5 giữ (mục 6.1 #7b) — xác nhận lại trên đúng commit |
| Q2 | Quy ước dấu offset? | Đọc mã | AI | ✅ server − client → S4 = −15 ms |
| Q3 | Script có lọc mẫu không? | Đọc mã | AI | ✅ không lọc |
| Q9 | Hash commit ntp5-exp nhóm dùng? | `git -C ~/Desktop/ntp5-exp rev-parse HEAD` | Tùng | ⬜ |
| Q10 | Khi mất response, mẫu Interleaved ghép đúng T1/T4? | Đọc chỗ gán `prev_transmit_ts`, `prev_receive_ts` | Tuyến | ⬜ |
| Q11 | Đã tắt VMware timesync + timesyncd? | `vmware-toolbox-cmd timesync status`; `timedatectl` | Tùng | ⬜ |
| Q12 | NetEm trên Ubuntu 22.04 có hỗ trợ `seed`? | Thử lệnh | Tùng | ⬜ |
| Q4 | 180 B đúng gồm 5 EF như bảng 6.2? | `tcpdump -X` | Tuyến (T19) | ⬜ |
| Q5 | `-m 1.0` có loại mẫu ở kịch bản delay lớn không? | Xem log "Not selected" | Tùng | ⬜ |
| Q6 | Danh sách RFC của Mizrahi | rfc-editor.org | Tuyến | ⬜ |
| Q7 | Chuyển card Wi-Fi vào namespace được không? | Thử `iw phy ... set netns` | Tùng | ⬜ |
| Q8 | Chrony trên máy lab có hỗ trợ NTPv5? | Tài liệu chrony | Tùng | ⬜ |

---

## 17. Ghi chú viết báo cáo

### 17.1 Chương nào dùng phần nào

| Chương | Nội dung | Lấy từ mục |
|---|---|---|
| Ch.1 Mở đầu | Bối cảnh, câu hỏi nghiên cứu, phạm vi | 2, 3.2 |
| Ch.2 Lý thuyết (Tuyến) | NTP, công thức, NTPv4 vs NTPv5, Interleaved, bảo mật, điểm yếu | 4, 5 |
| Ch.3 Phương pháp (Tùng) | Lab, topology, kiểm tra công cụ, lý do không cần router, kịch bản, dự đoán | 6, 7, 8, 9 |
| Ch.4 Kết quả (Tuyến) | KPI, biểu đồ, đối chiếu dự đoán | 9, 10, 12 |
| Ch.5 Kết luận | Trả lời RQ1–RQ6, giới hạn, hướng phát triển | 2.3, 15, 8.3 |

### 17.2 KHÔNG được viết

| ❌ Sai | ✅ Đúng |
|---|---|
| Header NTPv5 180 byte | Header 48 byte; payload UDP của công cụ là 180 byte (gồm 5 EF) |
| Interleaved triệt tiêu trễ hàng đợi | Interleaved giảm sai số xử lý/hàng đợi **phía máy server** |
| NTPv5 là chuẩn | NTPv5 là Internet-Draft (work in progress), WG Document |
| Bài báo NTPv5 | Bản nháp tiêu chuẩn (Internet-Draft) |
| Cookie là Extension Field | Cookie nằm trong header |
| Interleaved đọc nhãn thời gian phần cứng (trong lab) | Lab dùng timestamp phần mềm Python |
| Kiểm thử Bloom filter | Công cụ 09+ dùng danh sách ID, không phải Bloom filter |

---

## 18. Cheat sheet lệnh

```bash
cd ~/Desktop/ntp5-exp

# Server (Terminal 1)
sudo ip netns exec ntp-s python3 ntpnode.py -l -p 10123

# Client (Terminal 2)
sudo ip netns exec ntp-c python3 ntpnode.py -d -v 4    10.10.0.2:10123   # NTPv4 Basic
sudo ip netns exec ntp-c python3 ntpnode.py -d -v 5    10.10.0.2:10123   # NTPv5 Basic
sudo ip netns exec ntp-c python3 ntpnode.py -d -v 5 -x 10.10.0.2:10123   # NTPv5 Interleaved
sudo ip netns exec ntp-c python3 ntpnode.py -d         10.10.0.2:10123   # Tự thương lượng (S5c)

# Kịch bản mạng
sudo ./config_scenario.sh S3
sudo ./config_scenario.sh reset

# Kiểm tra
sudo ip netns exec ntp-c ping -c 20 10.10.0.2
sudo ip netns exec ntp-c tc -s qdisc show dev veth-c
sudo ip netns exec ntp-s tc -s qdisc show dev veth-s

# Bắt gói (T19–T20)
sudo ip netns exec ntp-s tcpdump -i veth-s -w run.pcap udp port 10123
sudo ip netns exec ntp-s tcpdump -i veth-s -X udp port 10123            # xem nội dung gói

# Máy thật: kiểm tra card có HW timestamp
ethtool -T <tên_card>
```

Lỗi thường gặp:

| Lỗi | Cách xử lý |
|---|---|
| `Unsynchronized response` / `Not selected (missing sample)` | Server thiếu `-l` |
| `Not selected (waiting for complete refids)` | Bình thường lúc khởi động, chờ ~16 s |
| `[Errno 98] Address already in use` | Còn tiến trình cũ: `sudo pkill -f ntpnode.py` |
| `[Errno 111] Connection refused` | Server chưa chạy hoặc sai IP/cổng |

---

## 19. Lịch sử thay đổi file

| Ngày | Người | Thay đổi |
|---|---|---|
| 24/10/2026 | Tùng (+AI) | Tạo file: tổng hợp phân tích draft-09, kiểm tra ntp5-exp, topology, kịch bản S0–S5, máy thật P1–P3, dự đoán, tiến độ, ý tưởng, chuẩn bị bảo vệ |
| 24/10/2026 | Tùng (+AI) | Phản biện theo tài liệu góp ý của nhóm → tạo `phanbien_nangcap.md`. Đính chính: RFC 9769 (NTPv4 Interleaved), hành vi thương lượng của công cụ (> 8 lượt mất, không có 256), jitter mặc định chưa kiểm chứng, dấu S4 = −15 ms, cách server lưu T3 (v4 xoá / v5 giữ). Hạ ưu tiên S5c; hướng nâng cao chọn: chèn trễ xử lý phía server |
