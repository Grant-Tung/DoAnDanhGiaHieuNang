# Phản biện & nâng cấp phương pháp — Đồ án NTPv5

> Trả lời tài liệu "TÓM TẮT ĐỒ ÁN NTPv5 — BẢN GỬI AI RÀ SOÁT VÀ NÂNG CẤP" (24/10/2026).
> Người đọc: Tùng (P2), Tuyến (P1).
> Nguồn đã đọc trực tiếp ngày 24/10/2026: `ntpnode.py` nhánh `master` trên GitHub, RFC 9769 (rfc-editor.org), man page tc-netem (man7.org), trang Datatracker của draft-ietf-ntp-ntpv5. Thêm vào đó là output `grep`/`sed` Tùng chạy trên bản clone ở máy P2.

**Ký hiệu độ tin cậy** (dùng xuyên suốt, theo yêu cầu mục 9.7):

| Ký hiệu | Nghĩa |
|---|---|
| **[QS]** | Đã quan sát (chạy thật, có log) |
| **[MÃ]** | Có bằng chứng trong mã nguồn |
| **[TL]** | Có bằng chứng trong tài liệu (RFC, draft, man page) |
| **[GT]** | Giả thuyết, suy ra từ lý thuyết, chưa đo |
| **[CKC]** | Chưa kiểm chứng, không được viết như sự thật |

> ⚠️ Mã nguồn được đọc ở `master` trên GitHub. Bản clone của nhóm có thể ở commit khác: output `sed` của Tùng cho thấy `transmit_ts` được đọc **trước** `encode()`, còn bản tóm tắt `master` mô tả **sau** `encode()`. Việc đầu tiên là ghi hash commit (`git -C ~/Desktop/ntp5-exp rev-parse HEAD`) và kiểm tra lại các điểm [MÃ] dưới đây trên đúng commit đó.

---

## 0. Tóm tắt kết luận

1. **Đồng ý** với hầu hết đề xuất trong tài liệu: đổi tên đề tài, dùng 4 mode, S1/S4 cùng tổng trễ, S3 = S2 + loss, lưu dữ liệu 2 tầng, thống kê theo run.
2. **Bổ sung một chỉnh sửa:** S2/S3 nên dùng trễ trung bình 25 ms mỗi chiều (thay vì 20 ms). Khi đó cả S1–S4 có **cùng tổng trễ trung bình 50 ms**, và mỗi cặp kịch bản chỉ khác đúng một biến.
3. **Sáu đính chính kỹ thuật** (mục 3), trong đó quan trọng nhất:
   - NTPv4 Interleaved **chạy được** trong công cụ (`-v 4 -x`) [MÃ], và là chuẩn RFC 9769 [TL].
   - Hành vi hạ phiên bản của công cụ là **"hơn 8 lượt mất liên tiếp → về v4"**, không có cơ chế chờ 256 lượt [MÃ]. Hướng S5c vì vậy yếu.
   - Server v4 **xoá** timestamp đã dùng, server v5 **giữ lại** [MÃ]. Từ đó có giả thuyết kiểm định được: khi mất gói, M2 bị rơi về Basic nhiều hơn M4.
   - Man page NetEm **không nói** jitter mặc định là phân phối đều [TL]. Phải đo.
4. **Hướng nâng cao chọn duy nhất:** *chèn trễ xử lý có kiểm soát phía server* (mục 6). Đây là thí nghiệm có đáp án lý thuyết rõ ràng (Basic lệch −X/2, Interleaved ≈ 0), làm khoảng 1 ngày, và dễ bảo vệ.
5. **Hai rủi ro chưa ai nêu:** VMware Tools và `systemd-timesyncd` có thể **nhảy đồng hồ** giữa các run, tạo mẫu ngoại lai. Phải tắt cả hai trước khi chạy (mục 8).

---

## 1. Đề tài và RQ có khớp năng lực của ntp5-exp không

### 1.1 Tên đề tài
Đồng ý với đề xuất, chỉ thêm hai cơ chế cần so sánh vào tên:

> **Đánh giá hiệu năng ước lượng độ lệch thời gian của NTPv4 và NTPv5 ở chế độ Basic và Interleaved trong điều kiện mạng không ổn định**

Lý do [MÃ]: `ntpnode.py` không gọi `adjtimex`, `clock_settime` hay `settimeofday`. Công cụ chỉ **ước lượng** offset, không chỉnh đồng hồ. Vì vậy không được dùng các cụm "độ chính xác đồng bộ" hay "chỉnh giờ".

### 1.2 Bốn RQ
Các RQ khớp năng lực công cụ. Chỉ cần làm rõ để mỗi RQ có một giả thuyết kiểm định được:

| RQ | Giả thuyết kiểm định | Phép so | Độ tin cậy cơ sở |
|---|---|---|---|
| RQ1 Tác động delay/jitter/loss/bất đối xứng | H1a: trễ đối xứng ổn định (S1) không làm tăng sai số so với S0. H1b: jitter (S2) làm tăng độ phân tán nhưng không tạo lệch hệ thống. H1c: loss (S3−S2) không đổi sai số từng mẫu, chỉ giảm số mẫu | S1−S0, S2−S1, S3−S2 | [GT] |
| RQ2 Basic và Interleaved | H2a: ở S0–S4, chênh lệch sai số Basic/Interleaved nhỏ hơn ngưỡng tương đương đặt trước (mục 5.4). H2b: khi mất gói, tỷ lệ mẫu Interleaved thực tế của **M2 (v4) thấp hơn M4 (v5)** | M2−M1, M4−M3; tỷ lệ Interleaved M2 vs M4 ở S3 | H2a [GT], H2b [MÃ]→[GT] |
| RQ3 Bất đối xứng | H3: lệch S4 − lệch S1 ≈ (10 − 40)/2 = **−15 ms** | S4−S1, cùng tổng trễ 50 ms | Dấu: [MÃ]; giá trị: [GT] |
| RQ4 Đánh đổi | H4: v5 tốn ×3,75 byte/mẫu so với v4, độ chính xác không tốt hơn tương ứng | Byte/mẫu hợp lệ, tỷ lệ mẫu hợp lệ | Byte: [QS]; còn lại [GT] |

Dấu của H3 [MÃ]: công cụ tính `offset = 0.5 * ((T2 - T1) + (T3 - T4))`, tức server − client. Với d↑ = 10 ms (C→S) và d↓ = 40 ms (S→C): offset đo = θ + (d↑ − d↓)/2 = 0 + (10 − 40)/2 = **−15 ms**.

---

## 2. Rà soát thiết kế thí nghiệm

### 2.1 Bốn mode: đồng ý, đã xác minh làm được

| Mã | Lệnh client | Cơ chế trong công cụ [MÃ] |
|---|---|---|
| M1 | `-v 4` | Basic |
| M2 | `-v 4 -x` | Client đặt `origin_ts = prev_response.receive_ts`, `receive_ts` ngẫu nhiên (đúng cách nhận biết của RFC 9769). Server **xoá** timestamp sau khi trả, mỗi mục chỉ dùng một lần |
| M3 | `-v 5` | Basic |
| M4 | `-v 5 -x` | Client gửi lại server cookie. Server dùng `receive_ts` làm cookie và **không xoá** mục đã dùng (dictionary tối đa 1000 mục) |

Hệ quả cho H2b [GT, suy từ MÃ]:
- **M2 mất response k+1:** request kế tiếp mang cùng `origin_ts`, nhưng server đã xoá mục đó, nên trả Basic. Mỗi lần mất response tạo ra khoảng 1 mẫu Basic.
- **M4 mất response:** client gửi lại cookie cũ, server vẫn còn mục đó, nên vẫn trả Interleaved.
- Kỳ vọng ở S3 (loss 5% mỗi chiều): M2 có khoảng 5% mẫu Basic, M4 gần 0%. Đây là **khác biệt thật giữa v4 và v5**, đo được ngay trong ma trận chính, không cần kịch bản nâng cao.

⚠️ Phải kiểm tra trước [CKC]: khi mất response, client còn ghép đúng cặp T1/T4 với T2/T3 không. Mẫu Interleaved dùng `prev_transmit_ts`, `prev_receive_ts`, `prev_response`. Nếu `prev_transmit_ts` bị cập nhật ở **mỗi lần gửi** (kể cả lần bị mất), T1 sẽ lệch một chu kỳ poll và tạo mẫu ngoại lai cỡ giây. Đọc chỗ gán hai biến này trong `send_request` / `receive_response`.

### 2.2 Kịch bản: đồng ý, chỉnh thêm S2/S3

Đề xuất của tài liệu cô lập tốt S3−S2 và S4−S1. Tuy vậy S2/S3 (trung bình 20 ms) vẫn khác tổng trễ với S1/S4 (25 ms), nên S2−S1 lẫn hai biến cùng lúc. Chỉnh để **mọi kịch bản có trễ trung bình 25 ms mỗi chiều**:

| KB | C→S (egress `veth-c`) | S→C (egress `veth-s`) | Đối chứng sạch |
|---|---|---|---|
| S0 | — | — | Nền |
| S1 | `delay 25ms` | `delay 25ms` | S1−S0: chỉ thêm trễ |
| S2 | `delay 25ms 10ms` | `delay 25ms 10ms` | S2−S1: chỉ thêm jitter |
| S3 | `delay 25ms 10ms loss 5%` | `delay 25ms 10ms loss 5%` | S3−S2: chỉ thêm loss |
| S4 | `delay 10ms` | `delay 40ms` | S4−S1: chỉ thêm bất đối xứng |

Lưu ý NetEm:
- **Phân phối jitter** [TL]: man page **không nói** phân phối mặc định khi không khai `distribution`. Các phát biểu trước đây "mặc định là đều" là [CKC]. Cách xử lý:
  1. Chạy `ls /usr/lib/tc/ /usr/lib/x86_64-linux-gnu/tc/ 2>/dev/null` để xem có bảng phân phối nào.
  2. Áp S2, chạy `ping -i 0.2 -c 1000`, vẽ histogram RTT. Đều thì có dạng tam giác (tổng 2 phân phối đều); chuẩn thì có dạng chuông.
  3. Ghi **phân phối quan sát được** vào Ch.3. Muốn chuẩn hoá thì khai rõ `distribution normal`.
- **Đảo thứ tự gói** [TL]: jitter lớn có thể đảo thứ tự gói. Với NTP, gói cách nhau vài giây nên không ảnh hưởng. Nếu chạy kèm `iperf3` thì cần ghi nhận.
- **Seed** [TL]: man page có `seed VALUE` cho loss. Ubuntu 22.04 (iproute2/kernel 5.15) có thể chưa hỗ trợ [CKC], thử bằng `tc qdisc add ... netem loss 5% seed 1`. Nếu có, dùng seed khác nhau cho mỗi lần lặp và ghi vào metadata.
- `tc -s` và PCAP chỉ xác nhận cấu hình. Số liệu báo cáo phải là **RTT/loss quan sát được** (đồng ý với tài liệu).

### 2.3 Số run, thời lượng, thứ tự

- Ma trận: **4 mode × 5 KB × 5 lặp = 100 run**. Đồng ý.
- Mỗi run: **warm-up + ≥ 100 request đo**. Ước tính thời gian:

| Poll (`-i`) | Một run (60 s warm-up + 100 request) | 100 run |
|---|---|---|
| 2 (4 s, mặc định) | ~7,7 phút | **~13 giờ** |
| 1 (2 s) | ~4,3 phút | ~7 giờ |
| 0 (1 s) | ~2,7 phút | ~4,5 giờ |

  Trong lab này, poll **không ảnh hưởng** sai số từng mẫu: không có trôi đồng hồ và công cụ không lọc mẫu [MÃ]. Đề xuất `-i 1`, cố định cho mọi run, ghi vào metadata. Nếu dùng `-i 0`, cần kiểm tra server không giới hạn tốc độ [CKC].
- **Mỗi run khởi động lại cả server và client.** Server giữ dictionary timestamp giữa các request; không khởi động lại thì run trước ảnh hưởng run sau.
- **Xáo trộn thứ tự:** chia thành 5 khối (mỗi khối = 1 lần lặp đủ 20 ô mode × KB), xáo thứ tự trong từng khối với seed cố định. Tránh chạy toàn bộ M1 trước rồi mới đến M4.
- **Lưu mọi lần chạy**, kể cả lỗi (đồng ý).

### 2.4 Yếu tố gây nhiễu chưa được kiểm soát

| Yếu tố | Ảnh hưởng | Kiểm soát |
|---|---|---|
| **VMware Tools time sync** | Có thể nhảy đồng hồ khách định kỳ → mẫu ngoại lai | `vmware-toolbox-cmd timesync disable` (kiểm tra `status`) |
| **systemd-timesyncd / chrony trên máy ảo** | Chỉnh đồng hồ giữa một lượt hỏi–đáp | `sudo timedatectl set-ntp false`; kiểm tra `timedatectl` |
| Nhiễu lập lịch CPU của VM | Phân tán µs ở S0 | Không chạy việc khác; ghi số vCPU; có thể ghim CPU bằng `taskset` |
| Nhiễu cố ý trong `read_clock` (~1 µs) [MÃ] | Sàn phân giải | Không diễn giải chênh lệch < vài µs |
| `delay = abs(...)` [MÃ] | Che delay âm (dấu hiệu bất thường) | Ghi chú; kiểm tra T1..T4 thô nếu thấy delay ≈ 0 |
| Commit khác nhau | Kết quả không tái lập | Khoá hash commit, ghi vào metadata |
| Hai môi trường P1/P2 | Khác hypervisor, kernel, Python | Không gộp dữ liệu (đồng ý) |

---

## 3. Kiểm chứng kỹ thuật các phát biểu nghi vấn

| # | Phát biểu (trong tài liệu nhóm / phân tích trước) | Kết luận | Bằng chứng |
|---|---|---|---|
| 1 | NTPv4 Interleaved là chuẩn riêng RFC 9769 | **Đúng.** RFC 9769 *NTP Interleaved Modes*, Lichvar & Malhotra, 2025, **Proposed Standard**, cập nhật RFC 5905; gồm 3 chế độ (client/server, symmetric, broadcast). Nhận biết ngầm qua origin timestamp, không đổi header | [TL] |
| 2 | Công cụ hỗ trợ `-v 4 -x` | **Đúng** (cách làm ở mục 2.1). Vẫn phải chạy thử để thấy dòng `Interleaved mode` | [MÃ], cần [QS] |
| 3 | Mất 2 phản hồi → về v4, chờ 256 request | **Không phải hành vi công cụ.** Công cụ: mặc định khởi động **v4 kèm giá trị đặc biệt**, nâng lên v5 khi server echo lại; hạ về v4 khi **`missed_responses > 8`** (9 lượt mất liên tiếp); không có 256. Hành vi trong văn bản draft là [CKC], phải đọc nguyên văn mục thương lượng của draft-09 trước khi trích | [MÃ]; draft [CKC] |
| 4 | Interleaved tự tắt khi mất nhiều gói | **Đúng:** client chỉ gửi Interleaved khi `missed_responses <= 4` và response trước cùng phiên bản | [MÃ] |
| 5 | NetEm jitter mặc định phân phối đều | **Chưa kiểm chứng:** man page không nói | [TL] → [CKC] |
| 6 | Công cụ lọc mẫu (min-delay) | **Không:** không lọc best-of-N; mỗi response hợp lệ log 1 dòng `Basic/Interleaved mode offset=...` | [MÃ] |
| 7 | Dấu offset S4 | Server − client → **−15 ms** | [MÃ] + công thức |
| 8 | Server cookie | Công cụ dùng **receive timestamp của server** làm cookie (không ngẫu nhiên) | [MÃ] |
| 9 | Timeout có log | **Không.** Lượt mất chỉ được đếm ngầm. Đếm request bằng dòng `Sent NTPv… request`, response bằng `Received NTPv… response`, mẫu hợp lệ bằng dòng `mode offset=` | [MÃ] |
| 10 | 180 B = header 48 B + 5 EF | Khớp cả 180 B (`-f 4`) lẫn 148 B (`-f 8`), nhưng **phân rã từng EF vẫn là suy luận** | Tổng: [QS]; phân rã: [GT] → xác nhận bằng PCAP |
| 11 | Công cụ "09+" khác draft-09 (Reference IDs, cờ 0x0001) | Thấy trong log debug (`refids` 32 mục, `UNSYNCHRONIZED`) và văn bản draft | [QS] + [TL]; nên xác nhận bằng PCAP |
| 12 | Interleaved trong công cụ dùng timestamp phần mềm, lấy trước `sendto()` | **Đúng** | [MÃ] |
| 13 | P1: 196 mẫu yêu cầu Interleaved, 195 thực tế | Mẫu Basic còn lại gần như chắc chắn là **response đầu tiên** (request đầu chưa có response trước nên không thể Interleaved) | [MÃ]; xác nhận: kiểm tra `sample_no = 1` trong CSV |

**Đính chính tự nhận:** các tài liệu trước (`doan.md`, `phantich.md`) từng ghi "chờ 256 request", "jitter mặc định đều", "Lichvar là tác giả *bản nháp* Interleaved". Ba điểm này đã sửa trong `doan.md` (24/10/2026).

---

## 4. Tầng dữ liệu

Đồng ý với hai tầng như tài liệu đề xuất. Bổ sung:

**Raw sample CSV**, thêm các cột:
- `sample_no` (đánh số từ 1 trong mỗi run, dùng để kiểm tra mẫu đầu là Basic)
- `in_warmup` (bool; **không xoá** mẫu warm-up, chỉ đánh dấu)
- `request_no` gắn với mẫu, nếu ghép được từ thứ tự log

**Run metadata**, thêm các cột:
- `tool_commit`, `ntpnode_args` (dòng lệnh đầy đủ), `poll_log2`
- `netem_c2s`, `netem_s2c` (chuỗi đúng như lệnh `tc`), `netem_seed`
- `observed_rtt_mean/p95`, `observed_loss` (từ ping kiểm tra trước run, hoặc PCAP)
- `vm_timesync_disabled`, `timesyncd_disabled` (bool)
- `requests_sent`, `responses_received`, `valid_samples`, `interleaved_samples`
- `block_id`, `order_in_block` (phục vụ xáo trộn)

**Đếm từ log** [MÃ]:
`requests_sent` = số dòng `Sent NTPv`; `responses_received` = số dòng `Received NTPv` phía client; `valid_samples` = số dòng `mode offset=`; `interleaved_samples` = số dòng `Interleaved mode offset=`.
Kiểm tra chéo bằng PCAP: số gói request/response trên `veth-c`.

---

## 5. KPI, thống kê, biểu đồ

### 5.1 KPI (mỗi run → 1 dòng tóm tắt)

| KPI | Định nghĩa | Ghi chú |
|---|---|---|
| `bias` | trung bình offset (có dấu) | Dùng cho RQ3 (bất đối xứng) |
| `mae` | trung bình \|offset\| | |
| `p95` | phân vị 95 của \|offset\| | |
| `sd` | độ lệch chuẩn offset | Đo độ phân tán do jitter |
| `delay_mean`, `delay_p95` | | |
| `valid_ratio` | valid_samples / requests_sent | Không tính được nếu chỉ parse dòng offset |
| `il_ratio` | interleaved_samples / valid_samples | Chỉ cho M2, M4 |
| `bytes_per_valid` | (byte request + byte response) / valid_samples | Từ PCAP hoặc kích thước log × số gói |
| `first_valid_s` | thời gian tới mẫu hợp lệ đầu tiên | Không gọi là "thời gian đồng bộ" |

### 5.2 Đơn vị thống kê
**Run là đơn vị độc lập** (đồng ý với tài liệu). Các mẫu trong cùng run tương quan với nhau (cùng trạng thái server, cùng chuỗi ngẫu nhiên NetEm), nên không coi như các lần lặp độc lập.

### 5.3 Phép kiểm định phù hợp với n = 5 run/ô
- **So sánh hai mode trong cùng KB** (ví dụ M3 vs M1): **kiểm định hoán vị chính xác** trên KPI cấp run. 5 vs 5 cho C(10,5) = 252 hoán vị, không cần giả định phân phối, dễ giải thích. Báo cáo kèm **hiệu số và khoảng tin cậy bootstrap 95%**.
- **Kiểm tra lý thuyết S4** (H3): ước lượng (bias_S4 − bias_S1) theo từng mode, kèm CI 95%. Kết luận "khớp lý thuyết" nếu CI nằm trong −15 ms ± dung sai đặt trước (ví dụ ±0,5 ms).
- **Tỷ lệ** (`valid_ratio`, `il_ratio`): cộng dồn đếm theo ô, báo cáo **khoảng tin cậy Wilson**. So M2 vs M4 ở S3 bằng kiểm định hoán vị trên tỷ lệ cấp run.
- **Đừng dùng p-value lớn để kết luận "bằng nhau".** Với H2a và "v4 ≈ v5", dùng **kiểm định tương đương** (TOST) hoặc cách đơn giản hơn là "CI của hiệu số nằm trọn trong biên ±Δ".
  **Δ phải được chốt sau pilot và trước khi chạy 100 run.** Ví dụ Δ = 3 × độ lệch chuẩn giữa các run của bias ở S0, tối thiểu 10 µs. Ghi Δ vào `doan.md` trước khi chạy.
- Không cần hiệu chỉnh đa so sánh phức tạp. Chỉ cần nói rõ đâu là phép so chính (định trước) và đâu là khám phá thêm.

### 5.4 Biểu đồ (theo thứ tự ưu tiên)
1. **Bias (có dấu) theo KB**, 4 đường mode, error bar = CI 95% giữa các run. Là biểu đồ chính cho RQ1 và RQ3, đánh dấu đường lý thuyết −15 ms ở S4.
2. **ECDF của \|offset\|** theo mode, mỗi KB một ô nhỏ. Cho thấy cả MAE lẫn P95, tốt hơn boxplot.
3. **Chuỗi thời gian offset ở S4**, 4 mode và đường lý thuyết.
4. **`il_ratio` của M2 và M4 theo KB**, kèm CI Wilson. Là biểu đồ chính cho H2b.
5. **Byte trên mẫu hợp lệ theo mode**, cho RQ4.
6. (Nâng cao) **Bias theo X (trễ xử lý chèn vào)**, đường lý thuyết −X/2 cho Basic và 0 cho Interleaved (mục 6).

---

## 6. Một hướng nâng cao duy nhất: chèn trễ xử lý có kiểm soát phía server

### 6.1 Vì sao chọn hướng này

| Tiêu chí | Chèn trễ xử lý | Hạ phiên bản v5 → v4 (S5c) |
|---|---|---|
| Đáp án lý thuyết | **Rõ:** Basic lệch −X/2, delay +X; Interleaved ≈ 0 | Mơ hồ |
| Khớp hành vi công cụ | Khớp [MÃ] | Công cụ khác draft (cần >8 lượt mất, nâng lại ngay) → kết quả nói về công cụ, không về giao thức |
| Trả lời câu hỏi cốt lõi | "Interleaved sửa được gì?" (RQ2) | Ngoài 4 RQ |
| Công sức | ~1 ngày: sửa ~3 dòng, chạy 2 mode × 5 mức × 5 lặp | Cần loss cụm nặng, khó tái lập |
| Rủi ro bảo vệ | Thấp, nếu công bố rõ là bản đo có chèn mã | Cao: "đây là lỗi công cụ hay giao thức?" |

### 6.2 Cách làm
1. Tạo nhánh riêng: `git checkout -b inject-delay`. Ghi hash commit.
2. Trong `receive_request` của server, giữa lúc đọc `pre_transmit_ts` (giá trị ghi vào gói Basic) và lúc đọc `transmit_ts` (giá trị lưu cho Interleaved), chèn một lệnh ngủ có tham số:
   ```python
   # Chỉ dùng cho thí nghiệm nâng cao; X lấy từ biến môi trường, mặc định 0
   time.sleep(float(os.environ.get("NTP_INJECT_DELAY", "0")))
   ```
   Giữ mặc định = 0 để bản sửa không làm thay đổi ma trận chính.
3. Chạy với `NTP_INJECT_DELAY` ∈ {0; 0,0005; 0,001; 0,002; 0,005} giây, ở S0, cho cả 4 mode, 5 lần lặp mỗi ô.
4. Kỳ vọng [GT]:
   - M1, M3 (Basic): bias ≈ −X/2, delay ≈ nền + X.
   - M2, M4 (Interleaved): bias ≈ nền, delay ≈ nền.
5. Biểu đồ 6 (mục 5.4) có đường lý thuyết. Đây là bằng chứng trực tiếp nhất cho **cơ chế** Interleaved.

Lưu ý khi bảo vệ: phải nói rõ "trễ X mô phỏng thời gian xử lý hoặc xếp hàng phía máy server, là đúng loại sai số mà Interleaved được thiết kế để loại bỏ (RFC 9769)". Không nói là mô phỏng trễ mạng.

---

## 7. Kế hoạch thực thi và tiêu chí nghiệm thu

### Giai đoạn A — Chuẩn bị (trước mọi run chính)

| # | Việc | Ai | Nghiệm thu |
|---|---|---|---|
| A1 | Ghi hash commit; kiểm tra lại các điểm [MÃ] trên đúng commit (nhất là thứ tự `transmit_ts`/`encode`) | Tùng | Hash nằm trong `doan.md`; danh sách [MÃ] tick xong |
| A2 | Kiểm tra cách ghép T1/T4 khi mất response (mục 2.1 ⚠️) | Tuyến | Trả lời có/không, kèm dòng code |
| A3 | Tắt VMware timesync + timesyncd | Tùng | `vmware-toolbox-cmd timesync status` = Disabled; `timedatectl` cho `NTP service: inactive` |
| A4 | `config_scenario.sh` theo bảng 2.2 (trễ trung bình 25 ms) | Tùng | `tc -s qdisc` khớp từng chiều |
| A5 | Đo phân phối jitter thực tế (1000 ping ở S2) + kiểm tra hỗ trợ `seed` | Tùng | Histogram + kết luận phân phối ghi vào Ch.3 |
| A6 | Ping kiểm chứng S0–S4 | Tùng | RTT trung bình trong ±10% cấu hình; loss S3 trong khoảng hợp lý |
| A7 | Chạy thử 4 mode ở S0, xác nhận dòng `Interleaved mode` có ở M2 và M4 | Tuyến (localhost) + Tùng (namespace) | M2 và M4 có `il_ratio` > 90% ở S0 |
| A8 | Sửa `parse_log.py`: cột requested/actual, đếm Sent/Received/valid, `sample_no`, `in_warmup` | Tuyến | Chạy trên log A7 ra đúng schema 2 tầng |

### Giai đoạn B — Pilot

| # | Việc | Nghiệm thu |
|---|---|---|
| B1 | Runner tự động: khởi động lại server/client mỗi run, áp NetEm, ghi metadata, lưu log + PCAP | 1 run kết thúc sạch, đủ file |
| B2 | Pilot: 4 mode × {S0, S3, S4} × 2 lặp | Không crash; S4 bias ≈ −15 ms (dấu đúng); S3 có `valid_ratio` ≈ 0,90 |
| B3 | Tính độ lệch chuẩn giữa các run ở S0 → **chốt Δ tương đương** + chốt poll + số request | Δ, poll, N ghi vào `doan.md` **trước** giai đoạn C |

### Giai đoạn C — Ma trận chính (100 run)

| # | Việc | Nghiệm thu |
|---|---|---|
| C1 | Chạy 5 khối × 20 ô, xáo trộn trong khối | 100 dòng metadata, run lỗi được ghi lại và chạy bù |
| C2 | QA: số request/response khớp PCAP; không có delay ≈ 0 bất thường; không có mẫu ngoại lai cỡ giây | Báo cáo QA 1 trang |

### Giai đoạn D — Nâng cao (chỉ khi C xong)
Chèn trễ xử lý (mục 6): 4 mode × 5 mức X × 5 lặp ở S0.

### Giai đoạn E — Phân tích & viết
Tuyến: KPI, kiểm định, 5–6 biểu đồ, Ch.2 + Ch.4. Tùng: Ch.3 (gồm lý do topology, kiểm tra mã, xác minh NetEm, các yếu tố nhiễu đã kiểm soát).

### Câu hỏi bắt buộc trả lời trước khi chạy 100 run
1. Hash commit là gì, và các điểm [MÃ] có đúng trên commit đó không? (A1)
2. Khi mất response, mẫu Interleaved có ghép đúng T1/T4 không? (A2)
3. M2 (`-v 4 -x`) có thực sự sinh mẫu Interleaved không? (A7)
4. Phân phối jitter thực tế là gì; có `seed` không? (A5)
5. Đã tắt VMware timesync và timesyncd chưa? (A3)
6. Δ tương đương, poll, số request/run đã chốt và ghi lại chưa? (B3)
7. Dòng `Sent NTPv… request` có xuất hiện ở mức log đang dùng (`-d`) không? Nếu không, sẽ không tính được `valid_ratio`. (A8)
8. Khởi động lại server mỗi run đã có trong runner chưa? (B1)

---

## 8. Phân loại các kết luận hiện có

| Kết luận | Mức |
|---|---|
| Header NTPv5 48 B; gói công cụ 180 B (`-f 4`) / 148 B (`-f 8`) | [TL] + [QS] |
| Phân rã 180 B thành 5 EF cụ thể | [GT] → PCAP |
| Công cụ không chỉnh đồng hồ hệ thống | [MÃ] |
| Timestamp phần mềm, lấy trước `sendto()` | [MÃ] |
| Công cụ không lọc mẫu | [MÃ] |
| Dấu offset: server − client; S4 kỳ vọng −15 ms | [MÃ] + [GT] |
| M2 rơi về Basic nhiều hơn M4 khi mất response | [MÃ] → [GT], đo ở S3 |
| Hạ v4 khi > 8 lượt mất liên tiếp (công cụ) | [MÃ] |
| "Mất 2 → v4, chờ 256" (draft) | [CKC] |
| Jitter NetEm mặc định phân phối đều | [CKC] |
| Interleaved tốt hơn Basic trong lab | [GT], kỳ vọng chênh lệch nhỏ |
| v4 Basic ≈ v5 Basic về sai số | [GT], kiểm bằng tương đương với Δ |
| Các con số MAE/P95 dự đoán cho S2/S3 | [GT], **không đưa vào phần kết quả** |
| P1: 241 mẫu localhost | [QS], chỉ là smoke test |
| Draft-09: WG Document, IESG "I-D Exists", chưa là RFC | [TL] (Datatracker 24/10/2026) |
| RFC 9769: Proposed Standard, Lichvar & Malhotra | [TL] |
| Danh sách RFC của Mizrahi (7384, 7822, 8877) | [CKC] → tra rfc-editor.org |
| VMware/timesyncd có thể nhảy đồng hồ trong run | [GT] → kiểm soát ở A3 |
