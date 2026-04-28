from stack_sentinel.mcp_server import tools


def create_fastmcp_server():
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("stack-sentinel-mcp")

    @mcp.tool()
    def fetch_ticket_context(ticket_id: str) -> dict:
        """Busca contexto normalizado de um ticket."""
        return tools.fetch_ticket_context(ticket_id)

    @mcp.tool()
    def fetch_build_status(build_id: str) -> dict:
        """Busca status e evidências de um build pelo ID."""
        return tools.fetch_build_status(build_id)

    return mcp


def run_fastmcp_server() -> None:
    create_fastmcp_server().run()


if __name__ == "__main__":
    run_fastmcp_server()
