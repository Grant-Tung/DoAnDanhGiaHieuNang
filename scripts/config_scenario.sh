#!/usr/bin/env bash
set -e
C="sudo ip netns exec ntp-c"; S="sudo ip netns exec ntp-s"
reset() { $C tc qdisc del dev veth-c root 2>/dev/null || true; $S tc qdisc del dev veth-s root 2>/dev/null || true; }
apply() { $C tc qdisc add dev veth-c root netem $1; $S tc qdisc add dev veth-s root netem $2; }   # $1 = C→S, $2 = S→C
reset
case "$1" in
  S0)    ;;
  S1)    apply "delay 25ms"               "delay 25ms" ;;
  S2)    apply "delay 25ms 10ms"          "delay 25ms 10ms" ;;
  S3)    apply "delay 25ms 10ms loss 5%"  "delay 25ms 10ms loss 5%" ;;
  S4)    apply "delay 10ms"               "delay 40ms" ;;
  reset) ;;
  *) echo "usage: $0 S0|S1|S2|S3|S4|reset"; exit 1 ;;
esac
$C tc -s qdisc show dev veth-c; $S tc -s qdisc show dev veth-s
