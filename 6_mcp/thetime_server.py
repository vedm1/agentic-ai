from mcp.server.fastmcp import FastMCP
import datetime

mcp = FastMCP("thetime_server")

@mcp.tool()
async def get_todaydate() -> str:
    """Get today's date

    """
    return datetime.date.today()

if __name__ == "__main__":
    mcp.run(transport="stdio")
