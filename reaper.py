#!/usr/bin/env python3
"""
type-2 reaper — EtherEver miner doesn't include EIP-1559 type-2 transactions.
Nitro's batch-poster + validator data-poster send type-2 → stuck forever.

This script periodically:
1. Scans txpool_content for pending txs from BatchPoster (0x5F91BA...) and Validator (0x45BFF8...)
2. If a pending tx is type 0x2 and stuck, replaces it with a legacy zero-value
   self-transfer at the same nonce + 50% higher gasPrice
3. The legacy tx gets mined → nonce advances → Nitro retries with next nonce

Runs as a systemd service.
"""
import json
import time
import urllib.request
import sys

L1_RPC = "https://rpc-ether.ever-chain.xyz"
INTERVAL = 30  # seconds
GAS_PRICE_FLOOR = 20_000_000_000  # 20 gwei (well above Nitro's 11 gwei type-2)

# Read keys
def load_key(path):
    with open(path) as f:
        return json.load(f)

BP = load_key("/root/ArbiEver/keys/batchposter.json")
VAL = load_key("/root/ArbiEver/keys/validator.json")
TARGETS = {
    BP["address"].lower(): BP["privateKey"],
    VAL["address"].lower(): VAL["privateKey"],
}

import subprocess

def rpc(method, params):
    body = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}
    req = urllib.request.Request(
        L1_RPC,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read()).get("result")

def get_stuck_type2(addr_lower):
    pool = rpc("txpool_content", [])
    out = []
    for cat in ("pending", "queued"):
        addr_pool = pool.get(cat, {})
        for a, txs in addr_pool.items():
            if a.lower() != addr_lower:
                continue
            for n, t in sorted(txs.items(), key=lambda x: int(x[0])):
                if t.get("type") in ("0x2", "0x1"):  # any non-legacy
                    out.append({
                        "nonce": int(n),
                        "type": t.get("type"),
                        "gasPrice": int(t.get("gasPrice", "0x0"), 16),
                    })
    return out

def replace_with_legacy(pk, addr, nonce, old_gas_price):
    # Use cast send with --legacy + much higher gas
    target_gas = max(GAS_PRICE_FLOOR, int(old_gas_price * 1.5))
    cmd = [
        "/root/.foundry/bin/cast", "send",
        "--rpc-url", L1_RPC,
        "--private-key", pk,
        "--legacy",
        "--gas-price", str(target_gas),
        "--gas-limit", "21000",
        "--nonce", str(nonce),
        "--value", "0",
        addr,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        ok = "status               1" in r.stdout
        print(f"  REPLACE {addr[:14]}.. nonce={nonce} → {'OK' if ok else 'FAIL'}", flush=True)
        if not ok:
            print(f"    stderr: {r.stderr[:200]}", flush=True)
    except Exception as e:
        print(f"  REPLACE error: {e}", flush=True)

def cycle():
    for addr_lower, pk in TARGETS.items():
        stuck = get_stuck_type2(addr_lower)
        if not stuck:
            continue
        print(f"[{time.strftime('%H:%M:%S')}] {addr_lower[:14]}.. has {len(stuck)} stuck non-legacy", flush=True)
        for tx in stuck:
            replace_with_legacy(pk, addr_lower, tx["nonce"], tx["gasPrice"])

def main():
    print(f"reaper starting, interval={INTERVAL}s", flush=True)
    while True:
        try:
            cycle()
        except Exception as e:
            print(f"cycle error: {e}", flush=True)
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
