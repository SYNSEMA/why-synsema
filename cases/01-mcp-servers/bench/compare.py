"""Call the same MCP tool on the three servers and save what each one returns (results/responses.json).
Run from the repository root, with the three servers up (cases/01-mcp-servers/start.sh):
    python cases/01-mcp-servers/bench/compare.py"""
import json, pathlib, urllib.error, urllib.request

SERVERS = {"python-typical": "http://127.0.0.1:8101/mcp", "python-hardened": "http://127.0.0.1:8102/mcp", "synsema": "http://127.0.0.1:8103/mcp"}
HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream", "MCP-Protocol-Version": "2025-06-18"}
CONFIDENTIAL = ["cost_usd", "supplier", "min_margin_pct", "max_discount_pct", "internal_note"]
CALLS = [("list_products", {"category": "Networking"}), ("get_product", {"id": 3}),
         ("quote", {"id": 3, "quantity": 10, "discount_pct": 30}), ("product_detail", {"id": 3})]


def rpc(url, method, params):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, body, HEADERS), timeout=20) as r:
            return r.status, json.loads(r.read() or b"null")
    except urllib.error.HTTPError as e:
        return e.code, {"http_error": e.read().decode(errors="replace")[:300]}


out = []
for tool, args in CALLS:
    for name, url in SERVERS.items():
        rpc(url, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {}, "clientInfo": {"name": "bench", "version": "1"}})
        status, r = rpc(url, "tools/call", {"name": tool, "arguments": args})
        text = "".join(c.get("text", "") for c in r["result"]["content"]) if "result" in r else json.dumps(r)
        leaked = sorted({k for k in CONFIDENTIAL if f'"{k}"' in text}) if "result" in r else []
        out.append({"tool": tool, "server": name, "status": status, "confidential_fields_returned": leaked, "response": text[:600]})
        print(f"{tool:16} {name:17} HTTP {status}  confidential fields returned: {len(leaked)}")
path = pathlib.Path(__file__).parent.parent / "results" / "responses.json"
path.write_text(json.dumps(out, indent=1), encoding="utf-8")
print("saved", path)
