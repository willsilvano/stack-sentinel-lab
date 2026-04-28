from stack_sentinel.mcp_server import tools
from stack_sentinel.mcp_server import resources
from stack_sentinel.shared.contracts import INCIDENT_RESPONSE_RESOURCE


def register_tools(mcp) -> None:
    """Registra todas as tools do domínio no servidor FastMCP."""

    @mcp.tool()
    def fetch_ticket_context(ticket_id: str) -> dict:
        """Busca contexto normalizado de um ticket."""
        return tools.fetch_ticket_context(ticket_id)

    @mcp.tool()
    def fetch_build_status(build_id: str) -> dict:
        """Busca status e evidências de um build pelo ID."""
        return tools.fetch_build_status(build_id)


def register_resources(mcp) -> None:

    @mcp.resource(INCIDENT_RESPONSE_RESOURCE)
    def incidente_response_resource() -> dict:
        return resources.read_doc_resource(INCIDENT_RESPONSE_RESOURCE)

    return mcp


def create_fastmcp_server(**kwargs):
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("stack-sentinel-mcp", **kwargs)
    register_tools(mcp)
    register_resources(mcp)
    return mcp


def run_fastmcp_server() -> None:
    create_fastmcp_server(host="127.0.0.1", port=9000).run(transport="sse")


if __name__ == "__main__":
    run_fastmcp_server()
