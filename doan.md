# Đồ án: Đánh giá hiệu năng NTPv4 / NTPv5 trong các điều kiện mạng giả lập

Nhóm 14 – Nguyễn Ngọc Tuyến (24521958), Nguyễn Công Tùng (24521948)
GVHD: Đặng Lê Bảo Chương – Khoa MMT&TT, UIT

## 1. Đề tài

Đo sai số ước lượng clock offset của NTPv4 và NTPv5 (bản thử nghiệm `ntp5-exp`) khi mạng có trễ, jitter, mất gói và bất đối xứng. So sánh thêm chế độ Basic và Interleaved, và chi phí byte của mỗi phiên bản.

Câu hỏi nghiên cứu:
- **RQ1:** Delay, jitter, loss và bất đối xứng ảnh hưởng thế nào đến offset?
- **RQ2:** Basic và Interleaved khác nhau ra sao về sai số và fallback?
- **RQ3:** Bias do bất đối xứng có gần giá trị lý thuyết −15 ms không?
- **RQ4:** Chất lượng ước lượng đánh đổi thế nào với chi phí truyền thông?

Phân công:
- Tùng: lab, NetEm, runner, chạy thực nghiệm, Chương 3.
- Tuyến: lý thuyết, parser, KPI, biểu đồ, Chương 2 và 4.

## 2. Phạm vi (chốt 24/10/2026)

| Mục | Nội dung |
|---|---|
| Chế độ | M1 v4 Basic, M2 v4 Interleaved, M3 v5 Basic, M4 v5 Interleaved |
| Lab | 1 VM Ubuntu, 2 namespace `ntp-c` (10.10.0.1) – `ntp-s` (10.10.0.2), nối veth |
| Công cụ | `ntp5-exp` commit `fe19210` (`ntpnode.py`) |
| Kịch bản | S0 không trễ · S1 25/25 ms · S2 25±10 ms · S3 = S2 + loss 5% · S4 10/40 ms |
| Số run | 4 mode × 5 kịch bản × 5 lần lặp = 100 run |
| Mỗi run | `-i 1` (2 s/request), bỏ 60 s warm-up, đo 120 request |
| Trước khi chạy | Tắt timesync của VMware và Ubuntu, khởi động lại server mỗi run |
| KPI | Bias, MAE, P95 \|offset\|, valid ratio, tỷ lệ fallback, byte |

Không làm: máy thật, timestamp phần cứng, NTS, Bloom filter, Correction field. Các mục này đưa vào phần hướng phát triển ở Chương 5.

Hai namespace dùng chung đồng hồ kernel, nên offset thật bằng 0. Offset NTP đo được chính là sai số.

## 3. Kết quả chính (100/100 run, 07/11/2026)

- 12.000 request MEASURE, 11.748 mẫu hợp lệ (97,9%). 252 request không có mẫu, đều thuộc S3.
- Bảng KPI: `runs/main/kpi_by_mode_scenario.csv`. Biểu đồ: `runs/main/charts/`.

MAE trung bình (ms, trung bình 5 run):

| KB | M1 | M2 | M3 | M4 |
|---|---|---|---|---|
| S0 | 0,128 | 0,128 | 0,148 | 0,127 |
| S1 | 0,081 | 0,070 | 0,073 | 0,079 |
| S2 | 3,300 | 3,396 | 3,177 | 3,380 |
| S3 | 3,440 | 60,935 | 3,283 | 109,453 |
| S4 | 15,011 | 15,000 | 15,021 | 15,008 |

Nhận xét:
- **RQ1:** Jitter làm MAE tăng lên khoảng 3,2–3,4 ms. Loss làm giảm valid ratio. Bất đối xứng gây ra bias cố định.
- **RQ2:**
  - Ở S0–S2, Basic và Interleaved gần như bằng nhau.
  - Ở S3, M2 có 26 outlier và M4 có 51 outlier (\|offset\| > 100 ms). Các outlier tập trung quanh −1000 và −2000 ms, tức lệch đúng 1–2 chu kỳ poll: khi mất request, Interleaved ghép nhầm timestamp của lượt cũ.
  - Median \|offset\| ở S3 của cả 4 mode chỉ khoảng 3,0–3,3 ms (xem `scripts/s3_robust_stats.py`).
  - Fallback: M2 có 31/532 mẫu (5,83%), M4 không có mẫu nào.
- **RQ3:** Ở S4, bias của cả 4 mode đều khoảng −15 ms, khớp công thức −Δ/2.
- **RQ4:** Payload UDP của NTPv4 là 48 B, của NTPv5 là 180 B (gấp 3,75 lần). Tính theo frame Ethernet thì gấp khoảng 2,47 lần. MAE của NTPv5 không tốt hơn một cách nhất quán.

## 4. Lưu ý khi viết báo cáo

- Header NTPv5 vẫn là 48 B. Con số 180 B là payload của `ntp5-exp` gồm cả các extension field.
- NTPv5 hiện là Internet-Draft, chưa phải RFC.
- Công cụ chỉ ước lượng offset, không chỉnh đồng hồ.
- Interleaved chỉ giảm sai số timestamp phía server, không loại bỏ được trễ hàng đợi trên mạng.
- Outlier ở S3 là đặc điểm của bản triển khai `ntp5-exp`, không phải lỗi của chuẩn NTP.
- MAE chính thức tính trên tất cả mẫu hợp lệ, kể cả mẫu fallback và outlier.

## 5. Giới hạn

1. Hai namespace dùng chung đồng hồ, nên không đo được trôi đồng hồ giữa hai máy thật.
2. Không có timestamp phần cứng (veth và Python), nên Interleaved chỉ thể hiện được một phần lợi ích.
3. Chỉ có một bản triển khai (`ntp5-exp` draft-09+) và 5 kịch bản NetEm.
4. Mỗi nhóm chỉ có 5 run, chưa làm kiểm định thống kê.
5. Chạy trên VM nên có nhiễu ở mức µs.

## 6. Tiến độ

| Việc | Người | Trạng thái |
|---|---|---|
| Lab 2 namespace, NetEm S0–S4 | Tùng | Xong |
| Runner + pilot S0/S4 (8/8 ok, S4 ≈ −15 ms) | Tùng | Xong 24/10 |
| Parser, KPI (`batch_process.py`, `analyze_runs.py`) | Tuyến | Xong |
| Chạy 100 run chính | Tùng | Xong 07/11 |
| KPI, biểu đồ, kiểm tra PCAP | Tuyến | Xong |
| Báo cáo 5 chương, slide | Cả hai | Xong 09/11 |
| Chuẩn bị bảo vệ | Cả hai | Đang làm |

## 7. Lệnh hay dùng

```bash
cd ~/Desktop/ntp5-exp
vmware-toolbox-cmd timesync disable && sudo timedatectl set-ntp false

# Server / client
sudo ip netns exec ntp-s python3 ntpnode.py -l -p 10123
sudo ip netns exec ntp-c python3 ntpnode.py -d -i 1 -v 5 -x 10.10.0.2:10123   # M4; bỏ -x là Basic, -v 4 là NTPv4

# Kịch bản mạng
sudo ./config_scenario.sh S3
sudo ./config_scenario.sh reset

# Chạy ma trận
sudo ./run_matrix.sh test    # 1 run thử
sudo ./run_matrix.sh main    # 100 run, khoảng 9 giờ

# Bắt gói
sudo ip netns exec ntp-s tcpdump -i veth-s -w run.pcap udp port 10123
```

Lỗi hay gặp:
- `Not selected (missing sample)`: server thiếu `-l`.
- `Address already in use`: còn tiến trình cũ, chạy `sudo pkill -f ntpnode.py`.
- `Connection refused`: server chưa chạy hoặc sai IP/cổng.

## 8. Tài liệu tham khảo

- RFC 5905 – NTPv4
- RFC 9769 – NTP Interleaved Modes
- RFC 8915 – Network Time Security
- draft-ietf-ntp-ntpv5 (Lichvar, Mizrahi)
- `ntp5-exp`: https://github.com/mlichvar/ntp5-exp (commit `fe19210`)
