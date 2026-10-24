# Context tổng hợp — Đồ án "Đánh giá hiệu năng NTPv5"

## ★ BÀN GIAO CHO AI MỚI — đọc phần này trước tiên

**Bạn là AI tiếp nhận hỗ trợ đồ án này.** Làm theo thứ tự:

1. **Đọc theo thứ tự:** (1) khối này → (2) `doan.md` Phần A, rồi mục 11 (tiến độ), 16 (câu hỏi mở), 19 (lịch sử) → (3) `phanbien_nangcap.md` mục 0 và 7 → (4) phần còn lại của file này khi cần chi tiết.
2. **Thứ tự ưu tiên khi các file mâu thuẫn:** `doan.md` Phần B (mới nhất, đã đính chính) > khối đính chính bên dưới > `phanbien_nangcap.md` > phần thân file này (viết sớm hơn, có chỗ đã lỗi thời).
3. **Người dùng:** Tùng (P2, mạng & thực nghiệm) và Tuyến (P1, giao thức & dữ liệu). **Chưa có nền mạng/đồng bộ thời gian** → tiếng Việt, đơn giản, ví dụ đời thường; lệnh phải copy-paste chạy được (Ubuntu 22.04 trong VMware, namespace `ntp-c`/`ntp-s`, server `10.10.0.2:10123`).
4. **Quy tắc làm việc:**
   - Không khẳng định hành vi `ntpnode.py` khi chưa xem mã trên **đúng commit** nhóm dùng; không khẳng định nội dung draft/RFC khi chưa đọc nguyên văn.
   - Gắn nhãn độ tin cậy: [QS] đã quan sát · [MÃ] có trong mã · [TL] có trong tài liệu · [GT] giả thuyết · [CKC] chưa kiểm chứng.
   - Không đưa số dự đoán vào phần kết quả.
   - Mọi thay đổi: cập nhật `doan.md` (tiến độ mục 11, câu hỏi mục 16, lịch sử mục 19; sửa Phần A nếu ảnh hưởng). Ý tưởng/sửa phương pháp chưa được nhóm đồng ý → ghi vào `phanbien_nangcap.md`, **không** ghi vào `doan.md` như đã chốt.
   - Nếu có kiến thức mới quan trọng cho AI sau → cập nhật khối bàn giao này.
5. **Repo:** https://github.com/Grant-Tung/DoAnDanhGiaHieuNang (private). Nhánh `main` = bản thống nhất; `Tung`, `Tuyen` = nhánh cá nhân; gộp qua Pull Request.

### Trạng thái hiện tại (cập nhật 24/10/2026)
- ✅ Lab 2 namespace chạy được 3 mode; đã đọc mã `ntpnode.py`. Commit nhóm dùng: **`fe19210790b2a1cbd951e3e5066dca094dd62a52`** = bản mới nhất nhánh `main` trên GitHub (đã so bằng GitHub API 24/10). Khi có mâu thuẫn giữa bản tóm tắt mã và output `sed` trên máy nhóm, **tin output trên máy** (ví dụ: `transmit_ts` được đọc trước `encode()`).
- ✅ Tuyến (P1) đã chạy 3 mode trên localhost, có `parse_log.py` → 241 mẫu (smoke test, không dùng để kết luận).
- 🔒 **PHẠM VI ĐÃ ĐÓNG BĂNG (24/10/2026)** — xem `doan.md` mục A0. Tóm tắt: 4 mode (M1 v4 Basic, M2 v4 Interleaved, M3 v5 Basic, M4 v5 Interleaved); S0 không trễ, S1 25/25, S2 25±10, S3 = S2 + loss 5%, S4 10/40 ms; 100 run; `-i 1`, bỏ 60 s, 120 request/run; 4 RQ; thống kê đơn giản (run là đơn vị, trung bình + khoảng dao động). Tuỳ chọn duy nhất: chèn trễ xử lý phía server, sau khi xong 100 run.
- ⛔ **AI KHÔNG được đề xuất mở rộng phạm vi** (máy thật, S5, kiểm định nâng cao, kịch bản mới, rà soát thêm). Nếu người dùng tự nêu ý tưởng mới → ghi vào `phanbien_nangcap.md` nhãn "sau đồ án". Chỉ đề xuất đổi bảng A0 khi số liệu pilot chứng minh không chạy được.
- ⏳ Còn chờ duy nhất: tên đề tài (hỏi GVHD).
- ✅ (24/10) Bước 1–3 trong `doan.md` A6 xong: NetEm kiểm chứng bằng ping (jitter phân phối đều), 4 mode chạy được, runner `scripts/run_matrix.sh` + pilot 8/8 ok, S4 lệch −15,0 ms đúng lý thuyết.
- ⏭️ Việc kế tiếp: Tùng chạy `sudo ./run_matrix.sh main` (100 run, ~8 giờ 40); Tuyến viết `parse_log.py` theo định dạng ở `doan.md` B-10.1 (thử trên dữ liệu `runs/pilot`). Vai trò của AI giờ là **hỗ trợ thực thi** (viết script, đọc log, gỡ lỗi), không thiết kế lại.
- ⚠️ Máy Tùng dùng locale dấu phẩy thập phân → mọi lệnh `awk`/`printf` trong shell phải có `LC_ALL=C`.

### Việc dở dang khi đóng phiên 24/10/2026 (hỏi người dùng tình trạng trước khi làm tiếp)
1. **Chạy 100 run** `sudo ./run_matrix.sh main` trên máy ảo — chưa xác nhận đã bắt đầu/xong. Kiểm tra: `grep -c ',ok$' runs/main/metadata.csv` phải = 100; rồi chạy lệnh "Kiểm tra nhanh" ở `doan.md` mục 18.
2. **Gửi `runs_pilot.tgz` cho Tuyến** — file đã nằm ở `~/Desktop/runs_pilot.tgz` trên máy ảo. VMware Shared Folders **chưa chạy được** (`/mnt/hgfs` trống sau `vmhgfs-fuse`; chưa thử `vmware-hgfsclient` / kiểm tra VM → Settings → Options → Shared Folders → Always enabled + tick Enabled). Cách thay thế: kéo thả file ra Windows, hoặc tải lên Google Drive bằng Firefox trong máy ảo.
3. **Tuyến** viết `parse_log.py` theo định dạng runner (`doan.md` B-10.1), thử trên `runs/pilot`.
4. **Mời Tuyến vào repo** (repo private) — cần tên tài khoản GitHub của Tuyến.
5. **D1 tên đề tài** — hỏi GVHD.
6. Tùng có thể bắt đầu viết Ch.3 và học theo `hoc_doan.md` trong lúc máy chạy.

### Ghi chú kỹ thuật cho AI chạy trên máy Windows của Tùng (Claude Code)
- Repo trên máy: `C:\Users\Administrator\Downloads\DoAnDanhGiaHieuNang` (làm việc trên nhánh `Tung`, gộp vào `main` qua Pull Request do Tùng bấm merge).
- `git push` thường bị lỗi vì chưa chạy `gh auth setup-git`; đẩy bằng: `git -c credential.helper= -c "credential.helper=!gh auth git-credential" push origin Tung` (tài khoản GitHub `Grant-Tung`).
- Trước khi sửa, `fetch` + `merge --ff-only origin/main` vì Tùng hay merge PR trên GitHub.
- Các file `doan.md`, `phanbien_nangcap.md`, `phantich.md` nằm trực tiếp trong `Downloads\` (và `Downloads\thanhtruc\phantich.md`) là **bản cũ, lỗi thời** — chỉ dùng bản trong repo.
- Thư mục `Downloads\thanhtruc` là repo thiệp 20/10, **không liên quan** đồ án.

### Khối đính chính (ưu tiên hơn phần thân bên dưới)
> - Công cụ ntp5-exp hạ về v4 khi **> 8 lượt mất liên tiếp** và nâng lại v5 ngay; **không có** cơ chế "chờ 256 request". Quy tắc "mất 2 → v4, chờ 256" của draft chưa đối chiếu nguyên văn.
> - Man page tc-netem **không nói** jitter mặc định là phân phối đều → chưa kiểm chứng, phải đo.
> - Dấu offset = server − client (mã nguồn) → S4 (10/40 ms) kỳ vọng **−15 ms**.
> - NTPv4 Interleaved là **RFC 9769** (Lichvar & Malhotra, 2025, Proposed Standard); công cụ hỗ trợ `-v 4 -x`.
> - Server lưu T3 trong 1 dictionary ≤ 1000 mục; **v4 xoá mục sau khi dùng, v5 giữ lại**. Công cụ **không lọc mẫu**.
> - ✅ Đã chốt (24/10): 4 mode; mọi kịch bản trễ trung bình 25 ms/chiều; 100 run. Các kịch bản S0–S4 và lệnh trong phần thân file này là **bản cũ** (10/10, 20±10, 3 mode, 75 run) → dùng bản trong `doan.md` mục 8.1 và 18.

> File này là nguồn context duy nhất cho AI hỗ trợ đồ án. Gộp từ: (a) `ntpv5_project_context-v7.md` (tiến độ, môi trường, kế hoạch), (b) phân tích draft-ietf-ntp-ntpv5-09 (đọc trực tiếp tại https://www.ietf.org/archive/id/draft-ietf-ntp-ntpv5-09.txt). Các chỗ (a) và (b) mâu thuẫn đã được đính chính ở mục 3.

## 0. Hướng dẫn cho AI đọc file

- **Người đang làm việc với bạn:** Tùng (P2) — phụ trách mạng NetEm & thực nghiệm. **Chưa có nền tảng về mạng/đồng bộ thời gian** → giải thích đơn giản, ví dụ đời thường, tiếng Việt; lệnh đưa ra phải chạy được ngay (copy-paste).
- **Đừng lặp lại các hiểu lầm đã đính chính ở mục 3.**
- **Trước khi khẳng định hành vi của `ntpnode.py`**, kiểm tra mã nguồn (mục 11 liệt kê những điểm chưa xác minh).
- Mọi số liệu dự đoán ở mục 9 là **giả thuyết lý thuyết** để đối chiếu với kết quả đo, không phải kết quả.

---

## 1. Tổng quan đồ án

- **Đề tài:** Đánh giá hiệu năng giao thức đồng bộ thời gian NTPv5.
- **Mục tiêu:** So sánh 3 chế độ `NTPv4 Basic`, `NTPv5 Basic`, `NTPv5 Interleaved` dưới điều kiện mạng giả lập S0–S4 (+ S5 nâng cao).
- **Trạng thái giao thức:** NTPv5 là Internet-Draft (draft-ietf-ntp-ntpv5-09), chưa phải RFC.
- **Công cụ:** `ntpnode.py` từ repo thực nghiệm của Miroslav Lichvar (tác giả draft, maintainer chrony): https://github.com/mlichvar/ntp5-exp, clone tại `~/Desktop/ntp5-exp`.

### Phân công
| Người | Vai trò |
|---|---|
| P1 – Tuyến | Giao thức & dữ liệu: schema CSV, lọc dữ liệu, MAE/P95, lý thuyết (Ch.2), phân tích kết quả (Ch.4) |
| P2 – Tùng | Mạng & thực nghiệm: Ubuntu, namespace, veth, script NetEm, runner chạy ma trận, phương pháp thực nghiệm (Ch.3) |

---

## 2. Môi trường & tiến độ

### Đã xong
- **T04:** Ubuntu 22.04.5 LTS trên VMware; cài `git python3 iproute2 tcpdump iperf3`; `open-vm-tools-desktop` (copy-paste `Ctrl+Shift+V`); clone `ntp5-exp`.
- **T05:** 2 namespace nối trực tiếp bằng 1 cặp veth:
  - `ntp-c` (client) — `veth-c` 10.10.0.1/24
  - `ntp-s` (server) — `veth-s` 10.10.0.2/24
  - ping 2 chiều 0% loss, RTT ~0,05 ms.
- **T09:** chạy được cả 3 chế độ trên UDP port 10123:
  - Server cần cờ `-l` (`--local`, local reference clock, stratum 1) — nếu thiếu sẽ lỗi `Unsynchronized response` / `Not selected (missing sample)`.
  - Đã xử lý `[Errno 98] Address already in use` và `[Errno 111] Connection refused`.
  - `-v 4`: gói 48 B. `-v 5`: gói 180 B. `-v 5 -x`: gói 180 B, `flags=2`, log `Interleaved mode offset=...` từ nhịp thứ 2.

### Tiếp theo
- **T10:** script `config_scenario.sh` cấu hình/reset NetEm cho S0–S4 (xem khuyến nghị topology ở mục 8 — **quan trọng**).
- **T11:** kiểm chứng qdisc (`tc -s qdisc show dev ...`) + ping trước khi chạy runner.

### Lộ trình
| Giai đoạn | Task |
|---|---|
| 1 Cài đặt | T01–T03 (P1), T04–T05 (P2, xong), T06 duyệt kịch bản |
| 2 Kết nối & đo | T07–T08 (P1), T09 (P2, xong), T10–T11 (P2, tiếp theo) |
| 3 Pilot & tự động hoá | T12–T14 (P1), T15–T17 (P2 runner & pilot) |
| 4 Ma trận chính | T18 (P2, ≥75 runs S0–S4 = 5 kịch bản × 3 chế độ × 5 lần lặp), T19–T20 (P1 QA & PCAP), T21 (S5) |
| 5 Phân tích & báo cáo | T22–T24 (P1 KPI, biểu đồ, Ch.2 & 4), T25–T26 (P2 Ch.3, chạy lại run lỗi) |
| 6 Bảo vệ | T27–T30 (báo cáo, slide, demo, đóng gói mã) |

---

## 3. Giới hạn học thuật & đính chính (đọc kỹ)

1. **"180 bytes" KHÔNG phải header.** Header NTPv5 cố định **48 octet** (= NTPv4, RFC 5905). 180 B là **tổng payload UDP**. Cookie nằm trong header, không phải EF (context v7 ghi nhầm). Đã đo: `-f 4` (mặc định) → **180 B**, `-f 8` → **148 B**. Phân rã khớp cả hai số đo (vẫn nên xác nhận bằng `tcpdump -X`):

   | Thành phần | Byte |
   |---|---|
   | Header NTPv5 | 48 |
   | EF Draft Identification (4 + chuỗi `draft-ietf-ntp-ntpv5-09+` 24 ký tự) | 28 |
   | EF Server Information | 8 |
   | EF Reference Timestamp | 12 |
   | EF Secondary Receive Timestamp | 16 |
   | EF Reference IDs (4 + 32/f mục × 8 B) | 68 (f=4) / 36 (f=8) |
   | **Tổng** | **180 / 148** |

   Response luôn được pad bằng đúng độ dài request (`encode(target_len=request_len)`; server từ chối gửi nếu dài hơn). Không bao giờ viết "header NTPv5 180 bytes" trong báo cáo/slide.
6. **`ntpnode.py` cài đặt bản "draft-09+" (thử nghiệm của tác giả), KHÁC văn bản draft-09 ở hai điểm:**
   - Reference IDs: script dùng **danh sách 32 ID, mỗi mục 64 bit (8 bit "share" + 56 bit ID)**, chia thành `-f` fragment; draft-09 dùng **Bloom filter 4096 bit với ID 120 bit**. → Các phân tích về Bloom filter (mục 7.2 #3, #4) là phân tích **văn bản draft**, lab **không** kiểm thử được.
   - Flag 0x0001: script đặt tên `UNSYNCHRONIZED` (1 = chưa đồng bộ; client gửi flags=1, server đồng bộ trả flags=0); draft-09 đặt tên **Synchronized** (1 = đã đồng bộ) — ngữ nghĩa ngược nhau.
   → Trong báo cáo ghi rõ: "công cụ thực nghiệm là cài đặt tham chiếu draft-09+ của tác giả draft, có khác biệt so với văn bản -09 ở …".
2. **Interleaved KHÔNG "triệt tiêu queueing delay" nói chung.** Nó chỉ loại sai số **bên trong máy server** (khoảng thời gian từ lúc server ghi T3 đến lúc gói thực sự rời máy). Nó **không** loại hàng đợi tại switch/router và **không** sửa bất đối xứng. Context v7 cũ viết "triệt tiêu sai số trễ hàng đợi" — phải sửa thành "sai số hàng đợi/xử lý phía host server".
3. **Lab không có hardware timestamp.** veth là thiết bị ảo, không có HW timestamping. Interleaved trong lab chỉ dùng được timestamp phần mềm (userspace hoặc kernel) → lợi thế của Interleaved ở lab nhỏ (cỡ µs) so với NetEm (cỡ ms). Đây là kết quả hợp lệ, cần nói rõ, không phải lỗi.
4. **Đồng hồ dùng chung.** Hai namespace chung một kernel clock → offset thật = 0 → **offset đo được chính là sai số**. Thuận lợi: có sẵn tham chiếu tuyệt đối. Hạn chế: không đánh giá được trôi tần số (drift) giữa 2 đồng hồ vật lý, không đánh giá được vòng điều khiển đồng hồ.
5. **Cờ `-x` chỉ là yêu cầu.** Có thể fallback về Basic (nhịp đầu tiên, mất gói, server không còn T3 cũ). Phải phân biệt `mode_requested` và `mode_actual` (mục 10).

---

## 4. Kiến thức nền tối thiểu

Bốn mốc thời gian của một lần hỏi–đáp:

| Ký hiệu | Sự kiện | Đồng hồ |
|---|---|---|
| T1 | client gửi request | client |
| T2 | server nhận request | server |
| T3 | server gửi response | server |
| T4 | client nhận response | client |

```
offset θ = [(T2 − T1) + (T3 − T4)] / 2      # đồng hồ client lệch bao nhiêu so với server
delay  δ = (T4 − T1) − (T3 − T2)            # thời gian khứ hồi trên mạng
```

Giả định ngầm: trễ chiều đi d↑ = trễ chiều về d↓. Nếu khác: **sai số offset = (d↑ − d↓)/2** (dấu tuỳ quy ước của script), và **không giao thức two-way nào phát hiện được** — kể cả NTPv5.

Ví dụ dễ hiểu cho người dùng: gọi điện hỏi giờ; nếu tiếng đi mất 1 s mà tiếng về mất 3 s, bạn sẽ chỉnh sai 1 s mà không biết.

---

## 5. NTPv5 khác NTPv4 thế nào

### Header 48 octet
| Trường | NTPv4 | NTPv5-09 |
|---|---|---|
| Word 1 | LI(2) VN(3) Mode(3) Stratum(8) Poll(8) Precision(8) | Giữ bố cục, VN cùng vị trí |
| Root Delay / Dispersion | 32 bit, 16.16, ~15 µs | 32 bit time32 (4.28), ~3,7 ns, max 16 s |
| Reference ID | 32 bit | Bỏ khỏi header → ID 120 bit trong Bloom filter 4096 bit (qua EF) |
| Reference Timestamp | 64 bit | Bỏ khỏi header (EF tuỳ chọn 0xF507) |
| Origin Timestamp | 64 bit (kiêm chống giả mạo) | Bỏ → **Client Cookie** 64 bit ngẫu nhiên |
| — | — | Timescale(8): 0=UTC, 1=TAI, 2=UT1, 3=UTC smeared |
| — | — | Era(8): dải ~136 năm → ~35.000 năm |
| — | — | Flags(16): 0x0001 Synchronized, 0x0002 Interleaved, 0x0004 Auth-NAK |
| — | — | **Server Cookie** 64 bit |
| Receive / Transmit Timestamp | 64 bit | 64 bit |
| MAC | nối trần cuối gói | bọc trong EF 0xF502 |
| Mode | client/server, symmetric, broadcast, mode 6, mode 7 | **chỉ client/server** |

Khác biệt cơ chế:
- Draft chỉ quy định **on-wire protocol**. Lọc mẫu, chọn nguồn, điều khiển đồng hồ nằm ngoài phạm vi → kết quả phụ thuộc implementation.
- Tách timestamp khỏi định danh gói (cookie). Client không gửi T1/thông tin đồng hồ (riêng tư).
- Response không được dài hơn request.

### Extension Fields (mã tạm)
| Mã | Tên | Kích thước | Ghi chú |
|---|---|---|---|
| 0xF501 | Padding | biến đổi | giữ request = response về độ dài |
| 0xF502 | MAC | 4 B Key ID + MAC (AES-CMAC) | phải đứng cuối |
| 0xF503/0xF504 | Reference IDs Req/Resp | chunk của filter 512 B | server **bắt buộc** hỗ trợ |
| 0xF505 | Server Information | 8 B | bitmask phiên bản 1–16 |
| 0xF506 | Correction | 28 B | kiểu transparent clock của PTP; không xác thực |
| 0xF507 | Reference Timestamp | 12 B | draft tự nghi ngờ có cần |
| 0xF508 | Monotonic Receive Timestamp | 16 B | Epoch ID 32 bit; cho frequency transfer |
| 0xF509 | Secondary Receive Timestamp | 16 B | timestamp theo timescale khác |
| 0xF5FF | Draft Identification | — | sẽ xoá khi lên RFC |

Phải xác minh bằng `tcpdump -X` / PCAP (T19–T20) xem 180 B của `ntpnode.py` gồm chính xác những EF nào → đưa vào báo cáo.

### Thương lượng phiên bản
NTPv5 **không tương thích trên dây** với NTPv4. Client gửi gói v4 có Reference Timestamp = `0x4E5450354E545035` ("NTP5NTP5"; bản draft dùng "NTP5DRFT"); server v5 echo lại → chuyển v5. Mất 2 phản hồi → quay về v4, chờ 256 request mới thử lại. **Đã xác minh: `ntpnode.py` mặc định là "negotiation"** (`-v` chỉ để ép phiên bản). Khi chạy `-v 4`/`-v 5` cố định thì cơ chế này không kích hoạt; muốn đo điểm yếu hạ phiên bản (mục 7.2 #5) thì chạy client **không có `-v`** (kịch bản S5c).

---

## 6. Basic vs Interleaved

- **Basic:** T3 nằm trong chính response → server ghi T3 *trước khi* gói rời máy. Sai số ε = thời gian gói còn nằm trong phần mềm/stack/driver. Hệ quả: θ_basic ≈ θ_true − ε/2, δ_basic ≈ δ_true + ε.
- **Interleaved:** response k mang Server Cookie C_k; request k+1 bật cờ 0x0002 và echo C_k; server trả **T3 thật của response k** (ghi sau khi đã gửi). Client ghép (T1ₖ, T2ₖ, T4ₖ) đã lưu với T3ₖ.
  - Mẫu luôn **trễ ≥ 1 nhịp poll**; nhịp đầu tiên là Basic.
  - Server không tra được cookie → trả Basic, tắt cờ.
  - Cách sinh cookie/lưu T3 phía server do implementation quyết định.
- So với NTPv4 interleaved (chrony): v4 dùng heuristic tái sử dụng trường timestamp làm cookie (dễ nhập nhằng); v5 có cờ tường minh + cookie riêng.

Ví dụ dễ hiểu: Basic = ghi giờ gửi lên phong bì trước khi dán (thư còn nằm chờ trên bàn → giờ ghi sớm hơn thật). Interleaved = gửi xong mới ghi giờ chính xác, rồi báo giờ đó trong lá thư sau.

| Nguồn sai số | Basic | Interleaved | Correction field |
|---|---|---|---|
| Hàng đợi/xử lý trong server | ❌ | ✅ | — |
| Hàng đợi tại switch/router | ❌ | ❌ | ✅ nếu thiết bị hỗ trợ |
| Bất đối xứng đường truyền | ❌ | ❌ | chỉ phần residence time |

---

## 7. Đánh giá giao thức

### 7.1 Cải tiến đáng giá
1. Interleaved chính thức hoá + HW timestamp → loại ε phía server (chỉ phát huy đầy đủ với HW timestamp — không có trong lab).
2. Correction field: cơ chế duy nhất xử lý queueing delay trong mạng (cần switch/router hỗ trợ — thực tế chưa có).
3. Bảo mật: bỏ mode 6/7 (nguồn khuếch đại kiểu `monlist`); response ≤ request (hệ số khuếch đại ≤ 1, server phải drop nếu response dài hơn); client cookie chống giả mạo off-path; MAC trong EF; NTS cho xác thực/chống replay; cơ chế bảo mật do cấu hình nên không downgrade được.

### 7.2 Điểm yếu / phản biện
| # | Điểm yếu | Giải thích | Mức |
|---|---|---|---|
| 1 | Correction field không xác thực | Phải sửa được trên đường nên nằm ngoài MAC. Kẻ on-path bơm correction → lệch offset tới ~δ/2 **không cần làm trễ gói** (delay attack khó phát hiện). Draft chỉ giới hạn correction < delay đo được. | Cao |
| 2 | Delay attack / bất đối xứng | Draft thừa nhận không giải quyết; dựa vào max-delay và nhiều nguồn. NTS không giúp. | Cao (giới hạn chung) |
| 3 | Đầu độc Bloom filter | Upstream gửi filter toàn bit 1 → mọi client hạ nguồn tưởng có loop → loại nguồn hợp lệ, lan theo cây stratum. Chunk cập nhật không nguyên tử. | Trung bình |
| 4 | Dương tính giả Bloom | ~1e-12 @26 ID, ~1e-6 @118 ID. | Thấp ở LAN |
| 5 | Hạ phiên bản do mất gói | Mất 2 phản hồi → về v4 trong 256 request (poll 64 s ≈ 4,5 h; 1024 s ≈ 73 h). Drop có chọn lọc ép client về v4. "Không downgrade" chỉ đúng với cơ chế bảo mật. | Cao |
| 6 | Reflection | Khuếch đại ≤ 1 nhưng phản xạ 1:1 bằng IP giả vẫn được. | Thấp |
| 7 | Trạng thái server cho interleaved | Server lớn phải evict cookie → fallback Basic không dự đoán được. | Trung bình |

**Mất gói phá Interleaved:**
- Server lưu T3 theo cookie: mất response j+1 → client vẫn echo C_j → mẫu j cứu được nhưng trễ hơn. Tỷ lệ mẫu ≈ (1−p).
- Server chỉ lưu T3 mới nhất / bị evict: tỷ lệ mẫu ≈ (1−p)². Ví dụ p=30%: Basic 70%, Interleaved ≈ 49%.
- Burst loss → cookie stale → client đặt cookie = 0 → về Basic.
- Hệ quả đo được: offset có phân bố **hai đỉnh cách nhau ε/2** (mẫu Basic và Interleaved trộn lẫn). Trong lab ε nhỏ (µs) → hai đỉnh chỉ thấy ở S0 hoặc khi server bị tải CPU.

**Bất đối xứng:** cả 3 chế độ lệch cùng (d↑ − d↓)/2. Interleaved cho δ nhỏ/ổn định hơn → daemon "tự tin" hơn (root distance nhỏ) trong khi offset vẫn sai.

**Kết luận then chốt:** cùng implementation & cùng bộ lọc → **NTPv4 Basic ≈ NTPv5 Basic** về độ chính xác (cùng công thức, cùng ngữ nghĩa timestamp). Khác biệt lớn → nghi do implementation.

### 7.3 Phần thừa / over-engineered (ngữ cảnh LAN, Linux phổ thông)
| Thành phần | Nhận xét |
|---|---|
| Correction field | Cần switch/router NTP-aware (parse UDP/123, VN=5, sửa trường, vá checksum ở line-rate) — gần như không tồn tại; trong lab luôn = 0 |
| Bloom filter 512 B + Ref ID Req/Resp + chunking | Thừa với LAN 1–4 nguồn; nhưng server bắt buộc hỗ trợ |
| UT1 / Secondary Receive Timestamp | Ứng dụng hẹp (thiên văn) |
| Monotonic Receive Timestamp | Ngách |
| Reference Timestamp EF | Draft tự nghi ngờ |
| Server Information bitmask v1–v16 | Dư |
| Era 8 bit | Hợp lý dài hạn (mốc 2036) nhưng dư dải |
| Draft Identification | Tạm thời, không phải tính năng |

Lưu ý công bằng: Era, TAI, độ phân giải 4 ns không thừa nếu nhìn dài hạn.

---

## 8. Thiết kế thực nghiệm — BẪY NETEM & topology khuyến nghị (áp dụng cho T10)

> **CẬP NHẬT SAU KHI KIỂM TRA MÃ (grep ntpnode.py):** script **chỉ dùng timestamp userspace** (`time.time()` dòng 89, `sock.sendto` dòng 674; không có `SO_TIMESTAMPING`/`MSG_ERRQUEUE`/`recvmsg`). Netem là qdisc: `sendto()` trả về ngay khi gói được xếp vào qdisc, nên trễ netem luôn nằm **sau** mọi timestamp phía gửi và **trước** timestamp userspace phía nhận → được tính đúng là trễ mạng ở cả Basic lẫn Interleaved.
> → **Topology 2 namespace hiện tại DÙNG ĐƯỢC.** Đặt netem trên egress `veth-c` (C→S) và egress `veth-s` (S→C). Topology 3 namespace bên dưới chỉ là tuỳ chọn (sạch hơn khi trình bày). Việc còn lại: xác nhận T3 Interleaved được lấy *sau* `sendto()` (mục 11 #1).
> Hệ quả: ε (sai số Basic) = thời gian Python + stack từ `time.time()` đến khi gói rời → cỡ µs–chục µs; chỉ thấy được ở S0 hoặc khi server bị tải CPU.

Khung `config_scenario.sh` cho **2 namespace** (dùng ngay):
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

### (Phân tích gốc, trước khi kiểm tra mã) Vấn đề với topology 2 namespace nếu script dùng kernel timestamp
Muốn làm chậm chiều S→C thì phải đặt netem trên **egress của `veth-s`, tức ngay trong máy server**. Gói bị netem giữ lại *trong máy server*, nên kết quả phụ thuộc server ghi T3 ở đâu:
- Ghi T3 ở userspace trước `sendto()` (Basic) → trễ netem được tính là trễ mạng (đúng).
- Ghi T3 bằng **kernel software TX timestamp** (`SO_TIMESTAMPING`; với veth timestamp được ghi trong driver, *sau* qdisc) → trễ netem bị tính là "server giữ gói" → Interleaved sẽ **xoá mất** trễ chiều về → offset/delay của Interleaved sai lệch giả tạo, so sánh với Basic bị thiên vị.
- Tương tự phía client nếu client dùng kernel TX timestamp cho T1 (netem trên `veth-c` egress); đặt netem ở ingress (IFB) cũng rủi ro vì kernel RX timestamp có thể đã được ghi trước khi qua ingress qdisc.

→ Kết luận an toàn nhất, không phụ thuộc cách `ntpnode.py` ghi timestamp: **thêm namespace router thứ 3 (`ntp-r`) và chỉ đặt netem trên router.** Hai máy đầu cuối giữ sạch.

### Topology 3 namespace (thay T05)
```bash
# Xoá cặp veth cũ (xoá một đầu là mất cả cặp)
sudo ip -n ntp-c link del veth-c 2>/dev/null

sudo ip netns add ntp-r
sudo ip link add veth-c type veth peer name veth-rc
sudo ip link add veth-s type veth peer name veth-rs
sudo ip link set veth-c  netns ntp-c
sudo ip link set veth-rc netns ntp-r
sudo ip link set veth-s  netns ntp-s
sudo ip link set veth-rs netns ntp-r

sudo ip -n ntp-c addr add 10.10.1.1/24   dev veth-c
sudo ip -n ntp-r addr add 10.10.1.254/24 dev veth-rc
sudo ip -n ntp-s addr add 10.10.2.2/24   dev veth-s
sudo ip -n ntp-r addr add 10.10.2.254/24 dev veth-rs

for ns in ntp-c ntp-s ntp-r; do sudo ip -n $ns link set lo up; done
sudo ip -n ntp-c link set veth-c up
sudo ip -n ntp-s link set veth-s up
sudo ip -n ntp-r link set veth-rc up
sudo ip -n ntp-r link set veth-rs up

sudo ip netns exec ntp-r sysctl -w net.ipv4.ip_forward=1
sudo ip -n ntp-c route add default via 10.10.1.254
sudo ip -n ntp-s route add default via 10.10.2.254

sudo ip netns exec ntp-c ping -c 3 10.10.2.2     # kiểm tra
```
**Địa chỉ server đổi thành `10.10.2.2`** (cập nhật cheat sheet, runner).

Quy ước hướng (netem chỉ tác động lên egress):
- **C→S** = egress `veth-rs` (router → server)
- **S→C** = egress `veth-rc` (router → client)

### Kịch bản S0–S4 (T10)
| Kịch bản | C→S (`veth-rs`) | S→C (`veth-rc`) |
|---|---|---|
| S0 Baseline | không netem | không netem |
| S1 Delay đối xứng | `delay 10ms` | `delay 10ms` |
| S2 Jitter | `delay 20ms 10ms` | `delay 20ms 10ms` |
| S3 Loss + jitter | `delay 20ms 5ms loss 5%` | `delay 20ms 5ms loss 5%` |
| S4 Bất đối xứng | `delay 10ms` | `delay 40ms` |

Khung `config_scenario.sh`:
```bash
#!/usr/bin/env bash
set -e
R="sudo ip netns exec ntp-r"
reset() { for d in veth-rc veth-rs; do $R tc qdisc del dev $d root 2>/dev/null || true; done; }
apply() { $R tc qdisc add dev veth-rs root netem $1; $R tc qdisc add dev veth-rc root netem $2; }
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
for d in veth-rc veth-rs; do $R tc -s qdisc show dev $d; done
```
Ghi chú netem: jitter không khai báo `distribution` là **phân phối đều** (uniform); muốn chuẩn/đuôi dài thì thêm `distribution normal|pareto`. Ghi rõ phân phối trong Ch.3.

T11 kiểm chứng: `tc -s qdisc show`, rồi `ping -c 20 10.10.2.2` từ `ntp-c` → RTT ≈ tổng delay 2 chiều, loss ≈ 1−(1−p)².

---

## 9. Dự đoán lý thuyết theo kịch bản (để đối chiếu kết quả)

Offset thật = 0 (đồng hồ chung) → offset đo = sai số.

| Kịch bản | Delay kỳ vọng | Offset kỳ vọng | Khác biệt giữa 3 chế độ |
|---|---|---|---|
| S0 | ~0,05–0,1 ms | ~0 (µs) | **Chỉ ở đây thấy được** chênh lệch µs do ε (Basic vs Interleaved) |
| S1 | ~20 ms | ~0 | Không đáng kể |
| S2 | ~40 ms | trung bình ~0; **độ lệch chuẩn mỗi mẫu ≈ 4,1 ms** (jitter đều ±10 ms mỗi chiều: σ_chiều = 10/√3 ≈ 5,77; σ_offset = √2·5,77/2 ≈ 4,08) | Không đáng kể |
| S3 | ~40 ms | σ_offset ≈ 2,0 ms (±5 ms đều); tỷ lệ lần hỏi–đáp thành công ≈ 0,95² ≈ 90,3% | Interleaved: tỷ lệ mẫu hữu dụng trong khoảng 0,903 (server lưu T3 theo cookie) đến ~0,81 (chỉ lưu T3 mới nhất); có fallback Basic |
| S4 | ~50 ms | **lệch hệ thống ±15 ms** = (10 − 40)/2; dấu theo quy ước offset của script | **Cả 3 giống nhau** → chứng minh không phiên bản nào sửa được bất đối xứng |

Nếu kết quả đo lệch mạnh khỏi bảng → nghi cấu hình netem sai hoặc bẫy timestamp ở mục 8.

---

## 10. Quy ước dữ liệu (P1 – T07, T08)

- `mode_requested`: từ cờ dòng lệnh (`-v 4` → v4 Basic; `-v 5` → v5 Basic; `-v 5 -x` → v5 Interleaved).
- `mode_actual`: `export_logs.py` bắt chuỗi `Interleaved mode` trong log → `Interleaved`; không có → `Basic` (nhịp 1 hoặc fallback).
- Loại các mẫu warm-up trước khi tính KPI: tối thiểu đến khi client hết "waiting for complete refids" (≈ `-f` response đầu) và, với Interleaved, sau nhịp đầu tiên. Đơn giản: bỏ 60 s đầu mỗi run.
- Mẫu nằm trong log dạng `Basic mode offset=+0.000057 delay=0.000493 rdist=0.000247 stratum=1` / `Interleaved mode offset=...` (đơn vị giây).
- KPI: MAE và P95 của |offset|; trung bình/độ lệch chuẩn delay; **tỷ lệ mẫu hữu dụng** (số mẫu / số request); **tỷ lệ fallback** (`mode_actual = Basic` khi `mode_requested = Interleaved`).
- Biểu đồ nên có: offset theo thời gian (kèm đường lý thuyết S4); boxplot |offset| theo chế độ × kịch bản; histogram offset của Interleaved ở S3 (tìm hai đỉnh); sai số offset theo mức bất đối xứng (S5).

---

## 11. Xác minh `ntpnode.py`

### Đã xác minh
| # | Câu hỏi | Kết quả |
|---|---|---|
| 1 | Ghi timestamp ở đâu | **Userspace** `time.time()` (dòng 89, hàm sinh timestamp NTP, có XOR bit thấp — có thể là ngẫu nhiên hoá bit dưới độ phân giải). Không có kernel timestamp. `sendto` dòng 674. → bẫy netem mục 8 **không áp dụng**. |
| 2 | Client có chỉnh đồng hồ hệ thống không | **Không** (không có `adjtimex/clock_settime/settimeofday/adjtime`) → chỉ đo, an toàn với đồng hồ dùng chung. |
| 3 | Poll | `-i POLL` log2 giây, **mặc định 2 → 4 s/lần hỏi**. 10 phút ≈ 150 mẫu. |

### Tuỳ chọn dòng lệnh (`ntpnode.py -h`)
`-p PORT` (mặc định 10123) · `-v VERSION` (mặc định **negotiation**) · `-i POLL` (log2 s, mặc định 2) · `-f NUMBER` (số fragment Bloom filter, mặc định 4) · `-r RATE` (dispersion rate, 15e-6) · `-m DIST` (max root distance, 1.0) · `-l` local reference · `-x` interleaved · `-n` tắt kiểm tra loop refid NTPv4 · `-d` tăng debug.

| 4 | Hàm timestamp | `read_clock(precision)` = `time.time()` đổi sang NTP 64 bit, **XOR với `32+precision` bit ngẫu nhiên** (precision server = −20 → ngẫu nhiên hoá ~12 bit thấp ≈ **1 µs dither**). → Kết quả dưới ~1 µs là nhiễu, không diễn giải. |
| 5 | Server lấy T3 thế nào (`receive_request`, ~dòng 631–684) | `pre_transmit_ts` đọc **trước** `make_response()` → đặt vào gói (T3 của **Basic**). `transmit_ts` đọc **sau** `make_response()` nhưng **trước** `encode()` và `sendto()` → lưu bằng `save_timestamps()` để trả trong response sau (T3 của **Interleaved**). |
| 6 | Client fallback | `make_request()` dòng 314: "Do not make an interleaved request if too many responses were missed" → mất nhiều gói thì client tự gửi Basic. |
| 7 | Magic thương lượng | `Ntp4MagicRefTs.NTP5 = b"NTP5DRFT"` (giá trị dành cho bản draft). |
| 8 | Khởi động | Client log "Not selected (waiting for complete refids)" cho tới khi nhận đủ `-f` fragment → mặc định cần ~4 response (~16 s) trước khi nguồn được chọn; mất gói kéo dài thêm. Mẫu offset vẫn được log trong lúc này. |
| 9 | Mẫu S0 đầu tiên (v5 Basic) | `offset=+0.000057 delay=0.000493` (57 µs / 493 µs) — lớn hơn ping (~50 µs RTT) do overhead Python. |

**Hệ quả quan trọng của #5:** Interleaved trong `ntpnode.py` chỉ là **proof-of-concept**: T3 "chính xác hơn" vẫn lấy ở userspace, *trước* `encode()+sendto()`. Lợi ích của Interleaved trong lab = **chỉ bằng thời gian chạy `make_response()`** (Python, cỡ chục µs), không phải lợi ích của HW/kernel timestamp như thiết kế. Dự đoán S0: Interleaved có delay nhỏ hơn Basic đúng bằng khoảng đó, offset dịch một nửa. Ở S1–S4 (ms) chênh lệch này chìm trong nhiễu. Đồng thời xác nhận dứt khoát: netem (sau `sendto`) không bị "nuốt" → topology 2 namespace hợp lệ.

### Còn chưa xác minh
1. (đã xong — xem #5)
2. Server lưu T3 cho Interleaved thế nào (theo cookie hay theo client, giữ bao nhiêu bản) → đọc `save_timestamps` (dòng 619) và `make_response` (dòng 554–618, có comment dòng 598 về "clients getting stuck in interleaved mode") → công thức tỷ lệ mẫu ở S3.
3. (đã xong — mục 3 #1; xác nhận thêm bằng PCAP nếu cần)
4. Quy ước dấu offset → dấu ±15 ms ở S4 (đọc `receive_response`, dòng 403–480).
5. Có bộ lọc mẫu không, hay log từng mẫu thô.
6. `-m 1.0` (max root distance 1 s): ở S4/S5 delay lớn vẫn dưới ngưỡng, nhưng nếu mẫu bị loại thì kiểm tra tham số này.

---

## 12. Kịch bản S5 nâng cao (T21)

**S5a — Bất đối xứng + mất gói theo cụm:**
```bash
sudo ip netns exec ntp-r tc qdisc add dev veth-rs root netem delay 2ms 0.2ms distribution normal
sudo ip netns exec ntp-r tc qdisc add dev veth-rc root netem delay 22ms 2ms distribution pareto loss gemodel 5% 30% 70% 0.1%
```
- Quét d↓ − d↑ ∈ {0, 5, 10, 20, 50} ms → sai số offset tuyến tính hệ số 0,5, trùng nhau cho 3 chế độ.
- Interleaved: histogram offset, tỷ lệ fallback theo mức loss (0, 1, 5, 15, 30 %).

**S5b — Bất đối xứng thay đổi theo thời gian + tải server:**
```bash
sudo ip netns exec ntp-r tc qdisc add dev veth-rc root netem delay 5ms 10ms 25% rate 10mbit limit 1000
sudo ip netns exec ntp-s iperf3 -s &                          # tuỳ hướng cần làm nghẽn
sudo ip netns exec ntp-c iperf3 -c 10.10.2.2 -u -b 9M -t 120 -R   # -R: server→client, bật/tắt theo chu kỳ 120 s
sudo ip netns exec ntp-s stress-ng --cpu 2 --io 2             # phình ε phía server (cần cài stress-ng)
```
- Hàng đợi dâng một chiều → mẫu δ nhỏ nhất vẫn lệch → offset răng cưa theo chu kỳ tải.
- Tải CPU server → kịch bản Interleaved có khả năng thắng rõ nhất trong lab (ε tăng).

**S5c — Hạ phiên bản do mất gói (khai thác điểm yếu 7.2 #5):**
- Client chạy **không có `-v`** (negotiation), áp loss tăng dần (5 → 30 %, nên dùng `gemodel` để mất theo cụm).
- Ghi lại phiên bản thực tế từng mẫu theo thời gian → bắt thời điểm rơi về v4 và đo thời gian kẹt ở v4 (lý thuyết 256 request × 4 s ≈ 17 phút với `-i 2`).
- Cần thêm cột `version_actual` trong schema CSV (P1).

Ma trận tham số gợi ý:
| Biến | Giá trị |
|---|---|
| Loss (Gilbert-Elliott) | 0, 1, 5, 15, 30 % |
| Asymmetry d↓ − d↑ | 0, 5, 10, 20, 50 ms |
| Jitter | 0,1 / 1 / 5 / 10 ms (ghi rõ phân phối) |
| Poll | 2 mức (nếu `ntpnode.py` cho đổi) |
| Tải server | idle / stress |

Thông điệp cho chương kết quả: S4/S5a chứng minh **giới hạn chung** của cả 3 chế độ; S0/S5b chứng minh **khác biệt thật** của Interleaved.

---

## 13. Cheat sheet lệnh (topology 3 namespace)

```bash
cd ~/Desktop/ntp5-exp

# Server (Terminal 1)
sudo ip netns exec ntp-s python3 ntpnode.py -l -p 10123

# Client (Terminal 2)
sudo ip netns exec ntp-c python3 ntpnode.py -d -v 4    10.10.2.2:10123   # NTPv4 Basic
sudo ip netns exec ntp-c python3 ntpnode.py -d -v 5    10.10.2.2:10123   # NTPv5 Basic
sudo ip netns exec ntp-c python3 ntpnode.py -d -v 5 -x 10.10.2.2:10123   # NTPv5 Interleaved

# Kịch bản mạng
sudo ./config_scenario.sh S3
sudo ./config_scenario.sh reset

# Bắt gói (T19–T20)
sudo ip netns exec ntp-s tcpdump -i veth-s -w run.pcap udp port 10123
```
**Đang dùng topology 2 namespace (đã xác minh là đủ, mục 8): thay `10.10.2.2` bằng `10.10.0.2` trong các lệnh trên**, và `config_scenario.sh` dùng bản 2 namespace ở đầu mục 8.

---

## 14. Nhật ký phiên làm việc & việc tiếp theo

### Phiên 2026-10-24 (Tùng + AI)
1. Phân tích draft-ietf-ntp-ntpv5-09 (đọc trực tiếp văn bản IETF) → mục 4–7.
2. Đính chính "180 bytes": header 48 B; 180 B = header + 5 EF (bảng mục 3 #1). Đo xác nhận: `-f 4` → 180 B, `-f 8` → 148 B.
3. Kiểm tra `ntpnode.py` bằng grep/sed:
   - Timestamp chỉ ở userspace (`read_clock` = `time.time()` + dither ~1 µs).
   - Client không chỉnh đồng hồ hệ thống → an toàn với đồng hồ dùng chung.
   - T3 Interleaved lấy sau `make_response()` nhưng trước `encode()+sendto()` → Interleaved chỉ là proof-of-concept, lợi ích cỡ chục µs.
   - Mặc định `-v` = negotiation, `-i 2` (4 s), `-f 4`.
   - Script là bản "draft-09+", khác văn bản -09 ở Reference IDs và ngữ nghĩa flag 0x0001 (mục 3 #6).
4. Quyết định: **giữ topology 2 namespace** (`ntp-c` 10.10.0.1 ↔ `ntp-s` 10.10.0.2), **bỏ** phương án router 3 namespace. Netem đặt trên egress `veth-c` (C→S) và `veth-s` (S→C).
5. Bổ sung kịch bản S5c (hạ phiên bản khi mất gói, chạy client không `-v`); quy tắc bỏ 60 s warm-up.
6. Context v7 cần sửa: câu "Interleaved triệt tiêu sai số trễ hàng đợi" → "giảm sai số xử lý phía host server"; danh sách EF của 180 B (cookie nằm trong header, không phải EF).

### Việc tiếp theo (theo thứ tự)
- [ ] **T10 (P2):** tạo `~/Desktop/ntp5-exp/config_scenario.sh` (bản 2 namespace, mục 8), `chmod +x`.
- [ ] **T11 (P2):** với từng S1–S4: `sudo ./config_scenario.sh Sx` → `sudo ip netns exec ntp-c ping -c 20 10.10.0.2` → đối chiếu RTT/loss với bảng kỳ vọng (S0 <0,1 ms/0%; S1 ~20 ms/0%; S2 ~40 ms dao động/0%; S3 ~40 ms/~10%; S4 ~50 ms/0%) → `reset`.
- [ ] **Phụ (cho P1):** `sed -n '554,630p' ntpnode.py` → xác định server lưu T3 Interleaved thế nào (mục 11 "Còn chưa xác minh" #2).
- [ ] **Phụ:** đọc `receive_response` (dòng 403–480) → quy ước dấu offset (dấu ±15 ms ở S4).
- [ ] Sau T11: pilot T15–T17 (3 chế độ × S0, S4, vài phút mỗi run) → viết runner tự động.
