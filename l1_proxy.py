#!/usr/bin/env python3
"""
L1 RPC proxy for Nitro.

EtherEver L1 hides baseFeePerGas (so external MetaMask/Remix uses legacy txs).
Nitro needs baseFee for its Sequencer surplus calculation — without it,
sequencer.go updateExpectedSurplus panics with nil pointer deref.

Strategy: always inject baseFeePerGas=0x0 for block-shaped responses.

Downside: Nitro batch-poster + validator data-poster see baseFee and send
type-2 EIP-1559 transactions. EtherEver miner does not include type-2
transactions in blocks. → Pending txs accumulate.

Workaround: see scripts/replace_type2.sh — periodically replaces stuck type-2
txs from BatchPoster/Validator with legacy self-transfers, advancing nonces.
Nitro then retries with new nonces (still type-2, still stuck — loop).

True fix (TODO): patch Nitro source to force legacy tx type when chain has
baseFee but miner doesn't include type-2 (~1 line change in dataposter).
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import json
import urllib.request
import urllib.error
import sys

UPSTREAM = "https://rpc-ether.ever-chain.xyz"

def looks_like_block(obj):
    return (
        isinstance(obj, dict)
        and "number" in obj
        and "hash" in obj
        and "parentHash" in obj
    )

def inject_basefee(obj):
    if looks_like_block(obj) and "baseFeePerGas" not in obj:
        obj["baseFeePerGas"] = "0x0"

def patch_response(data):
    if isinstance(data, list):
        for item in data:
            patch_response(item)
        return
    if not isinstance(data, dict):
        return
    result = data.get("result")
    if result is None:
        return
    if isinstance(result, dict):
        inject_basefee(result)
    elif isinstance(result, list):
        for r in result:
            if isinstance(r, dict):
                inject_basefee(r)

class Proxy(BaseHTTPRequestHandler):
    def log_message(self, *a, **kw):
        pass
    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        body = self.rfile.read(length) if length else b""
        try:
            req = urllib.request.Request(
                UPSTREAM, data=body,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                    "Accept": "application/json",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                content = resp.read()
                status = resp.status
        except urllib.error.HTTPError as e:
            content = e.read()
            status = e.code
        except Exception as e:
            content = json.dumps({"error": str(e)}).encode()
            status = 500
        try:
            parsed = json.loads(content)
            patch_response(parsed)
            content = json.dumps(parsed).encode()
        except (json.JSONDecodeError, ValueError):
            pass
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"L1 baseFee proxy for Nitro - POST JSON-RPC here\n")

class ThreadingServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8547
    print(f"L1 proxy listening on 127.0.0.1:{port} → {UPSTREAM}", flush=True)
    ThreadingServer(("127.0.0.1", port), Proxy).serve_forever()
