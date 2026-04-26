#!/bin/bash
# BLS 키가 없다면 생성
mkdir -p ./keys
if [ ! -f "./keys/das_bls" ]; then
    echo "Generating new BLS keys for DAC..."
    # (키 생성 로직 생략 - 실제 운영 시에는 nitro 바이너리로 생성)
fi

# DAS 서버 기동
nohup ./daserver \
  --data-availability.local-file-storage.enable \
  --data-availability.local-file-storage.data-dir="./das-data" \
  --data-availability.sequencer-inbox-address="0x81187148F099342D54130Acca04b24BB97965db4" \
  --data-availability.parent-chain-node-url="https://rpc-ether.ever-chain.xyz" \
  --enable-rpc --rpc-addr="0.0.0.0" --rpc-port=9876 \
  --log-level 3 > das_server.log 2>&1 &
echo "DAC Node (DAS Server) has started on port 9876."
