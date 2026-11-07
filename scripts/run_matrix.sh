#!/usr/bin/env bash
# run_matrix.sh — chạy ma trận thí nghiệm NTPv4/NTPv5 (đồ án đánh giá hiệu năng)
# Đặt cùng thư mục với ntpnode.py và config_scenario.sh.
# Dùng: sudo ./run_matrix.sh test    (S0 × M4 × 1 lặp = 1 run, ~5 phút — kiểm thử runner)
#       sudo ./run_matrix.sh s3      (4 mode × S3 × 1 lặp = 4 run, ~22 phút — pilot mất gói)
#       sudo ./run_matrix.sh pilot   (4 mode × S0,S4 × 1 lặp = 8 run, ~42 phút)
#       sudo ./run_matrix.sh main    (4 mode × S0–S4 × 5 lặp = 100 run, ~9 giờ)
# Bị ngắt giữa chừng → chạy lại đúng lệnh cũ: run đã "ok" được bỏ qua.
set -u
cd "$(dirname "$0")"

PHASE="${1:-}"
case "$PHASE" in test|s3|pilot|main) ;; *) echo "Dùng: sudo $0 test|s3|pilot|main"; exit 1;; esac
[ "$EUID" -eq 0 ] || { echo "Phải chạy bằng sudo: sudo $0 $PHASE"; exit 1; }

POLL=1            # -i 1 → hỏi ~2,02 s/lần (đo ở pilot)
WARMUP=60         # bỏ 60 s đầu, tính từ request đầu tiên
MEASURE_N=120     # dừng client ngay sau request MEASURE thứ 120 (+ GRACE chờ response)
GRACE=1.5         # phải < chu kỳ hỏi để không gửi thêm request
CLIENT_MAX=420    # chốt an toàn; bình thường client dừng ở ~303 s
SERVER_SECS=430
SERVER=10.10.0.2:10123
COMMIT=$(git rev-parse HEAD)
OUT=runs/$PHASE
PLAN=$OUT/plan.csv
META=$OUT/metadata.csv
mkdir -p "$OUT"

# Đồng bộ giờ phải tắt, nếu không đồng hồ có thể nhảy giữa run
[ "$(timedatectl show -p NTP --value)" = "no" ] || { echo "LỖI: chạy 'sudo timedatectl set-ntp false' trước"; exit 1; }
vmware-toolbox-cmd timesync status 2>/dev/null | grep -qi disabled || { echo "LỖI: chạy 'vmware-toolbox-cmd timesync disable' trước"; exit 1; }

# Kế hoạch chạy: xáo trộn thứ tự trong từng khối (1 khối = 1 lần lặp), seed cố định
if [ ! -f "$PLAN" ]; then
  python3 - "$PHASE" > "$PLAN" <<'PY'
import random, sys
phase = sys.argv[1]
modes = ["M4"] if phase == "test" else ["M1", "M2", "M3", "M4"]
scens, reps = {"test": (["S0"], 1), "s3": (["S3"], 1), "pilot": (["S0", "S4"], 1)}.get(phase, (["S0", "S1", "S2", "S3", "S4"], 5))
print("run_id,block,order,rep,scenario,mode")
for rep in range(1, reps + 1):
    cells = [(s, m) for s in scens for m in modes]
    random.Random(1000 + rep).shuffle(cells)
    for i, (s, m) in enumerate(cells, 1):
        print(f"{phase}-b{rep}-{i:02d}_{s}_{m},{rep},{i},{rep},{s},{m}")
PY
fi
HEADER="run_id,block,order,rep,scenario,mode,mode_args,netem_c2s,netem_s2c,tool_commit,poll_log2,start_epoch,end_epoch,requests_sent,responses_received,valid_samples,interleaved_samples,warmup_requests,measure_requests,measure_responses,measure_valid,measure_interleaved,status"
[ -f "$META" ] || echo "$HEADER" > "$META"
[ "$(head -1 "$META")" = "$HEADER" ] || { echo "LỖI: $META có cột kiểu runner cũ — đổi tên/di chuyển thư mục $OUT rồi chạy lại"; exit 1; }

mode_args() { case "$1" in M1) echo "-v 4";; M2) echo "-v 4 -x";; M3) echo "-v 5";; M4) echo "-v 5 -x";; esac; }
cnt() { grep -c "$1" "$2" || true; }

# Gắn epoch vào đầu mỗi dòng log client, đếm theo pha của request (WARMUP/MEASURE),
# dừng client sau request MEASURE thứ MEASURE_N + GRACE. In: warmup_sent measure_sent measure_recv measure_valid measure_il
CTRL=$(cat <<'PY'
import select, subprocess, sys, time
warmup, n, grace, out = float(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
c = {p: dict(sent=0, recv=0, valid=0, il=0) for p in ("W", "M")}
t0 = phase = deadline = None
raw = sys.stdin.buffer.raw  # không đệm: select() không bỏ sót dòng đã đọc sẵn
with open(out, "w") as log:
    while True:
        if deadline is not None:
            left = deadline - time.time()
            if left <= 0 or not select.select([raw], [], [], left)[0]:
                break
        line = raw.readline().decode("utf-8", "replace")
        if not line:
            break
        now = time.time()
        log.write(f"{now:.6f} {line}")
        if "Sent NTPv" in line:
            t0 = t0 or now
            phase = "W" if now - t0 < warmup else "M"
            c[phase]["sent"] += 1
            if phase == "M" and c["M"]["sent"] == n:
                deadline = now + grace
        elif phase and "Received NTPv" in line:
            c[phase]["recv"] += 1  # response/mẫu tính theo pha của request gần nhất
        elif phase and "mode offset=" in line:
            c[phase]["valid"] += 1
            c[phase]["il"] += "Interleaved mode offset=" in line
subprocess.run(["pkill", "-f", "^python3 -u ntpnode.py -d"])  # neo ^: không tự khớp chính mình
m = c["M"]
print(c["W"]["sent"], m["sent"], m["recv"], m["valid"], m["il"])
PY
)

while IFS=, read -r RUN BLOCK ORDER REP SCEN MODE; do
  if grep -q "^$RUN,.*,ok$" "$META"; then echo "Bỏ qua $RUN (đã ok)"; continue; fi
  D=$OUT/$RUN
  [ -d "$D" ] && mv "$D" "$D.loi.$(date +%s)"   # giữ lại dữ liệu lần chạy lỗi
  mkdir -p "$D"
  ARGS=$(mode_args "$MODE")
  echo "[$(date +%H:%M:%S)] $RUN  ($SCEN, $MODE: $ARGS)"

  pkill -f ntpnode.py 2>/dev/null; pkill -f "tcpdump -i veth-c" 2>/dev/null; sleep 1
  ./config_scenario.sh "$SCEN" > "$D/tc_before.txt" 2>&1
  NC2S=$(ip netns exec ntp-c tc qdisc show dev veth-c | head -1)
  NS2C=$(ip netns exec ntp-s tc qdisc show dev veth-s | head -1)

  START=$(date +%s.%N)
  ip netns exec ntp-s timeout $SERVER_SECS python3 -u ntpnode.py -l -p 10123 < /dev/null > "$D/server.log" 2>&1 &
  ip netns exec ntp-c timeout $SERVER_SECS tcpdump -i veth-c -w "$D/capture.pcap" udp port 10123 < /dev/null > /dev/null 2>&1 &
  sleep 2
  # Mỗi dòng log client được gắn thời gian epoch (giây) ở đầu dòng
  read -r WSENT MSENT MRECV MVALID MIL < <(
    ip netns exec ntp-c timeout $CLIENT_MAX python3 -u ntpnode.py -d -i $POLL $ARGS $SERVER < /dev/null 2>&1 \
      | python3 -u -c "$CTRL" $WARMUP $MEASURE_N $GRACE "$D/client.log")
  END=$(date +%s.%N)
  sleep 1   # cho tcpdump ghi nốt gói cuối
  pkill -f "^python3 -u ntpnode.py -l"; pkill -f "tcpdump -i veth-c"
  wait

  { ip netns exec ntp-c tc -s qdisc show dev veth-c; ip netns exec ntp-s tc -s qdisc show dev veth-s; } > "$D/tc_after.txt"
  SENT=$(cnt "Sent NTPv" "$D/client.log"); RECV=$(cnt "Received NTPv" "$D/client.log")
  VALID=$(cnt "mode offset=" "$D/client.log"); IL=$(cnt "Interleaved mode offset=" "$D/client.log")
  # ok khi: đúng MEASURE_N request đo; response ≤ request; mẫu ≤ response;
  # không mất gói (mọi KB trừ S3) thì phải đủ MEASURE_N mẫu; S3 cho phép thiếu nhưng phải > 0
  STATUS=ok
  [ "${MSENT:-0}" -eq "$MEASURE_N" ] || STATUS=fail
  [ "${MRECV:-0}" -le "${MSENT:-0}" ] && [ "${MVALID:-0}" -le "${MRECV:-0}" ] && [ "${MVALID:-0}" -gt 0 ] || STATUS=fail
  [ "$SCEN" = S3 ] || [ "${MVALID:-0}" -eq "$MEASURE_N" ] || STATUS=fail
  echo "$RUN,$BLOCK,$ORDER,$REP,$SCEN,$MODE,\"$ARGS\",\"$NC2S\",\"$NS2C\",$COMMIT,$POLL,$START,$END,$SENT,$RECV,$VALID,$IL,${WSENT:-0},${MSENT:-0},${MRECV:-0},${MVALID:-0},${MIL:-0},$STATUS" >> "$META"
  echo "    warmup=${WSENT:-0}  measure: sent=${MSENT:-0} recv=${MRECV:-0} mau=${MVALID:-0} interleaved=${MIL:-0}  -> $STATUS"
done < <(tail -n +2 "$PLAN")

./config_scenario.sh reset > /dev/null 2>&1
echo "Xong. Metadata: $META"
