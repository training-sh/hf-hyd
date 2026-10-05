"""Launched by notebook 23; stdout is reserved for MCP protocol traffic."""
from mcp.server.fastmcp import FastMCP
from course import get_product

server = FastMCP("ecommerce_catalog")


@server.tool()
def lookup_product(product_id: str) -> dict:
    """Return a demo product's price, currency and stock."""
    return get_product(product_id)


if __name__ == "__main__":
    server.run(transport="stdio")
