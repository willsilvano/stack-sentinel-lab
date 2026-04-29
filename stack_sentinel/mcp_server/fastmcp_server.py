from stack_sentinel.mcp_server import tools
from stack_sentinel.mcp_server import resources
from stack_sentinel.mcp_server import prompts
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


def register_prompts(mcp) -> None:
    """Registra todos os prompts do dominio no servidor FastMCP."""

    @mcp.prompt()
    def incident_triage_prompt(user_question: str, available_context: str) -> str:
        """Prompt de triagem de incidente."""
        return prompts.incident_triage_prompt(user_question, available_context)

    @mcp.prompt()
    def build_failure_analysis_prompt(
        build_status: str, failed_step: str, log_excerpt: str
    ) -> str:
        """Prompt para analise de build quebrado."""
        return prompts.build_failure_analysis_prompt(build_status, failed_step, log_excerpt)


def create_fastmcp_server(**kwargs):
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("stack-sentinel-mcp", **kwargs)
    register_tools(mcp)
    register_resources(mcp)
    register_prompts(mcp)
    return mcp


def run_fastmcp_server() -> None:
    create_fastmcp_server().run(transport="stdio")


if __name__ == "__main__":
    run_fastmcp_server()
