#!/usr/bin/env bash
# Start the three MCP servers. Run from the repository root:  bash cases/01-mcp-servers/start.sh
# MCP endpoints: 8101 (Python typical), 8102 (Python hardened), 8103 (Synsema with --labels)
set -e
(cd cases/01-mcp-servers/servers && uv run --quiet --with "mcp==2.3.0" python py_typical.py &)
(cd cases/01-mcp-servers/servers && uv run --quiet --with "mcp==2.3.0" python py_hardened.py &)
synsema serve --labels cases/01-mcp-servers/servers/mcp.syn &
sleep 6
echo "Servers up on 8101, 8102, 8103. Compare them with: python cases/01-mcp-servers/bench/compare.py"
