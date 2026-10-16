# 1 · MCP servers that leak by accident

**Question:** what does the model receive from your MCP server when a teammate adds a tool that returns the whole record?

Three MCP servers with the same four tools over the same product catalog. Each product has public fields (name, list price, stock) and confidential ones (cost, supplier, minimum margin, maximum discount, internal note).

| Server | Port | What it stands for |
| --- | --- | --- |
| `servers/py_typical.py` | 8101 | The official Python SDK (mcp 2.3.0) written the usual way: tools return the record, the model decides what to show |
| `servers/py_hardened.py` | 8102 | The safe pattern by hand: public view, quotes computed on the server |
| `servers/mcp.syn` | 8103 | The same pattern in Synsema with `--labels`: confidential fields labeled when loaded |

In all three, `product_detail` was "added later for the purchasing team" and returns the whole record.

## Run

```bash
bash cases/01-mcp-servers/start.sh                  # starts the three servers
python cases/01-mcp-servers/bench/compare.py        # same calls on the three → results/responses.json
synsema code check cases/01-mcp-servers/servers/mcp.syn --json   # every declassify, before running anything
```

Connect any MCP client (Claude Code, Cursor) with `cases/01-mcp-servers/.mcp.json` and try your own requests.

## Result

| Tool | Python, typical | Python, hardened | Synsema |
| --- | --- | --- | --- |
| `list_products`, `get_product` | 5 confidential fields | public only | public only |
| `quote` | price only | price only | price only, each output declassified with a written reason |
| `product_detail` (added later) | 5 confidential fields | **5 confidential fields** | **refused** (HTTP 500, `label_violation`) |
| Know before running what can leave | no | no | yes: 4 declassify sites with line and reason |

## What it does not solve

- Labels are opt-in (`serve --labels`). Without the flag, `private()` fails on purpose.
- Propagation is conservative: public and confidential data must live in separate structures, or public reads come out private too.
- A violation returns HTTP 500, not a JSON-RPC error; it cannot be caught, because catching it would leak one bit per try.
- Labels protect confidentiality, not authorization: if quoting is allowed, the model can still ask for the maximum discount.
