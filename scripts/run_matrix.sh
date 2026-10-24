#!/usr/bin/env bash
# run_matrix.sh — chạy ma trận thí nghiệm NTPv4/NTPv5 (đồ án đánh giá hiệu năng)
# Đặt cùng thư mục với ntpnode.py và config_scenario.sh.
# Dùng: sudo ./run_matrix.sh pilot   (4 mode × S0,S4 × 1 lặp = 8 run, ~42 phút)
#       sudo ./run_matrix.sh main    (4 mode × S0–S4 × 5 lặp = 100 run, ~9 giờ)
# Bị ngắt giữa chừng → chạy lại đúng lệnh cũ: run đã "ok" được bỏ qua.
set -u
cd "$(dirname "$0")"

PHASE="${1:-}"
[ "$PHASE" = pilot ] || [ "$PHASE" = main ] || { echo "Dùng: sudo $0 pilot|main"; exit 1; }
[ "$EUID" -eq 0 ] || { echo "Phải chạy bằng sudo: sudo $0 $PHASE"; exit 1; }

POLL=1            # -i 1 → hỏi 2 s/lần
CLIENT_SECS=300   # 60 s warm-up + 120 request × 2 s
SERVER_SECS=310
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
modes = ["M1", "M2", "M3", "M4"]
scens, reps = (["S0", "S4"], 1) if phase == "pilot" else (["S0", "S1", "S2", "S3", "S4"], 5)
print("run_id,block,order,rep,scenario,mode")
for rep in range(1, reps + 1):
    cells = [(s, m) for s in scens for m in modes]
    random.Random(1000 + rep).shuffle(cells)
    for i, (s, m) in enumerate(cells, 1):
        print(f"{phase}-b{rep}-{i:02d}_{s}_{m},{rep},{i},{rep},{s},{m}")
PY
fi
[ -f "$META" ] || echo "run_id,block,order,rep,scenario,mode,mode_args,netem_c2s,netem_s2c,tool_commit,poll_log2,start_epoch,end_epoch,requests_sent,responses_received,valid_samples,interleaved_samples,status" > "$META"

mode_args() { case "$1" in M1) echo "-v 4";; M2) echo "-v 4 -x";; M3) echo "-v 5";; M4) echo "-v 5 -x";; esac; }
cnt() { grep -c "$1" "$2" || true; }

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
  ip netns exec ntp-c timeout $CLIENT_SECS python3 -u ntpnode.py -d -i $POLL $ARGS $SERVER < /dev/null 2>&1 \
    | python3 -u -c 'import sys, time
for l in sys.stdin: sys.stdout.write(f"{time.time():.6f} {l}")' > "$D/client.log"
  END=$(date +%s.%N)
  wait

  { ip netns exec ntp-c tc -s qdisc show dev veth-c; ip netns exec ntp-s tc -s qdisc show dev veth-s; } > "$D/tc_after.txt"
  SENT=$(cnt "Sent NTPv" "$D/client.log"); RECV=$(cnt "Received NTPv" "$D/client.log")
  VALID=$(cnt "mode offset=" "$D/client.log"); IL=$(cnt "Interleaved mode offset=" "$D/client.log")
  STATUS=ok; [ "$VALID" -gt 0 ] || STATUS=fail
  echo "$RUN,$BLOCK,$ORDER,$REP,$SCEN,$MODE,\"$ARGS\",\"$NC2S\",\"$NS2C\",$COMMIT,$POLL,$START,$END,$SENT,$RECV,$VALID,$IL,$STATUS" >> "$META"
  echo "    mau=$VALID  interleaved=$IL  sent=$SENT  recv=$RECV  -> $STATUS"
done < <(tail -n +2 "$PLAN")

./config_scenario.sh reset > /dev/null 2>&1
echo "Xong. Metadata: $META"
