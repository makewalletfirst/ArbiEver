#!/bin/bash
pkill -9 nitro || true
# 사용자 지갑(0x8a9b...) 자금 주입 옵션 포함
nohup ./nitro \
  --dev \
  --init.dev-init \
  --init.dev-init-address="0x8a9b7384195d39890B335BC78a576E0ae5d07A9e" \
  --http.addr="0.0.0.0" \
  --http.port=8449 \
  --http.vhosts="*" \
  --http.corsdomain="*" \
  --http.api="net,web3,eth,arb,debug" \
  > arbiever.log 2>&1 &
echo "ArbiEver L2 Node v1.1 Started."
