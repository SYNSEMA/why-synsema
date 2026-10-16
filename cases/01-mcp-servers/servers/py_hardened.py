"""The "hardened" Python MCP server: the same safe pattern as the Synsema one, done by hand.
The model only sees public fields and quotes are computed on the server.
But product_detail was added later by another developer, and nothing in Python can stop it. Port 8102."""
from mcp.server.mcpserver import MCPServer
import catalog_py as c

mcp = MCPServer("catalog-python-hardened", instructions="Product catalog for sales support.")


@mcp.tool()
def list_products(category: str = "") -> list[dict]:
    """List products (public fields only), optionally filtered by category."""
    return [c.public_view(p) for p in c.CATALOG if not category or p["category"] == category]


@mcp.tool()
def get_product(id: int) -> dict:
    """Show one product (public fields only)."""
    return c.public_view(c.find(id))


@mcp.tool()
def quote(id: int, quantity: int, discount_pct: float = 0) -> dict:
    """Quote on the server: cost and margins never leave."""
    return c.quote(id, quantity, discount_pct)


@mcp.tool()
def product_detail(id: int) -> dict:
    """(Added later, for the purchasing team.) Full product detail."""
    return c.find(id)   # the slip: returns the whole record, and nothing prevents it


if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_streamable_http_async(port=8102, json_response=True, stateless_http=True))
