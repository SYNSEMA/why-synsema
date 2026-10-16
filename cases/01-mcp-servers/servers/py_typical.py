"""The "typical" Python MCP server: written the way most are today. Tools return the full record and the model
decides what to show. Port 8101."""
from mcp.server.mcpserver import MCPServer
import catalog_py as c

mcp = MCPServer("catalog-python-typical", instructions="Product catalog for sales support.")


@mcp.tool()
def list_products(category: str = "") -> list[dict]:
    """List products, optionally filtered by category."""
    return [p for p in c.CATALOG if not category or p["category"] == category]


@mcp.tool()
def get_product(id: int) -> dict:
    """Show one product."""
    return c.find(id)


@mcp.tool()
def quote(id: int, quantity: int, discount_pct: float = 0) -> dict:
    """Quote a quantity of a product with a requested discount."""
    return c.quote(id, quantity, discount_pct)


@mcp.tool()
def product_detail(id: int) -> dict:
    """(Added later, for the purchasing team.) Full product detail."""
    return c.find(id)


if __name__ == "__main__":
    import asyncio
    asyncio.run(mcp.run_streamable_http_async(port=8101, json_response=True, stateless_http=True))
