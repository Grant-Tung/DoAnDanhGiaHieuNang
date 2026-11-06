#!/usr/bin/env bash
# setup_lab.sh — Tạo 2 network namespaces ntp-c và ntp-s cho lab NTPv5
# Chạy lại script này mỗi khi khởi động lại máy ảo Ubuntu.
set -e

[ "$EUID" -eq 0 ] || { echo "Phải chạy bằng sudo: sudo $0"; exit 1; }

echo "[1/4] Dọn dẹp cấu hình cũ (nếu có)..."
ip netns del ntp-c 2>/dev/null || true
ip netns del ntp-s 2>/dev/null || true
ip link del veth-c 2>/dev/null || true
ip link del veth-s 2>/dev/null || true

echo "[2/4] Tạo 2 network namespaces: ntp-c (client) và ntp-s (server)..."
ip netns add ntp-c
ip netns add ntp-s

echo "[3/4] Tạo cặp veth nối giữa ntp-c (10.10.0.1) và ntp-s (10.10.0.2)..."
ip link add veth-c type veth peer name veth-s
ip link set veth-c netns ntp-c
ip link set veth-s netns ntp-s

ip -n ntp-c addr add 10.10.0.1/24 dev veth-c
ip -n ntp-s addr add 10.10.0.2/24 dev veth-s

ip -n ntp-c link set lo up
ip -n ntp-s link set lo up
ip -n ntp-c link set veth-c up
ip -n ntp-s link set veth-s up

echo "[4/4] Kiểm tra kết nối ping giữa 2 namespace..."
ip netns exec ntp-c ping -c 3 10.10.0.2

echo ""
echo "✅ HOÀN TẤT: Lab 2 namespace (ntp-c ↔ ntp-s) đã sẵn sàng!"
