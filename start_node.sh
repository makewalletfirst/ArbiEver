#!/bin/bash

# 기존 프로세스가 있다면 종료
pkill -9 nitro || true

# ArbiEver 시퀀서 노드 백그라운드 기동
nohup ./nitro \
  --dev \
  --http.addr="0.0.0.0" \
  --http.port=8449 \
  --http.vhosts="*" \
  --http.corsdomain="*" \
  > arbiever.log 2>&1 &

echo "ArbiEver L2 Node has started in background."
echo "You can check the logs using: tail -f arbiever.log"
