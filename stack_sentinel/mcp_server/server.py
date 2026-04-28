from stack_sentinel.mcp_server.registry import (
    PromptDefinition,
    ResourceDefinition,
    SimpleMCPServer,
    ToolDefinition,
)
from stack_sentinel.mcp_server import prompts, resources, tools
from stack_sentinel.shared.contracts import (
    BUILD_TOOL_NAME,
    INCIDENT_TRIAGE_PROMPT,
    TICKET_TOOL_NAME,
)


def create_mcp_server() -> SimpleMCPServer:
    """Contrato do Ex03: cria o servidor MCP minimo do dominio Stack Sentinel."""
    return SimpleMCPServer(
        name="stack-sentinel-mcp",
        description="MCP para chamados",
        metadata={
            "domain": "incident-investigation",
            "version": "0.1.0"
        },
        tools={},
        resources={},
        prompts={}
    )


def register_ticket_tool(server: SimpleMCPServer) -> SimpleMCPServer:
    """Contrato do Ex04: registra a tool de ticket no servidor informado."""
    server.register_tool(
        ToolDefinition(
            name=TICKET_TOOL_NAME,
            handler=tools.fetch_ticket_context,
            description="Busca tickets",
            input_schema={"type": "object", "required": ["ticket_id"],},
        )
    )
    return server


def register_build_tool(server: SimpleMCPServer) -> SimpleMCPServer:
    """Ex05: registre fetch_build_status no servidor MCP."""
    server.register_tool(
        ToolDefinition(
            name=BUILD_TOOL_NAME,
            description="Busca status e evidencias de um build.",
            input_schema={"type": "object", "required": ["build_id"], "properties": {"build_id": {"type": "string"}}},
            handler=tools.fetch_build_status,
        )
    )
    return server


def register_doc_resources(server: SimpleMCPServer) -> SimpleMCPServer:
    """Ex06: registre os resources de documentacao no servidor."""
    for item in resources.list_doc_resources():
        uri = item["uri"]
        server.register_resource(
            ResourceDefinition(
                uri=uri,
                name=item["name"],
                description=item["description"],
                handler=lambda uri=uri: resources.read_doc_resource(uri),
            )
        )
    return server


def register_prompts(server: SimpleMCPServer) -> SimpleMCPServer:
    """Ex07: registre prompts do dominio Stack Sentinel."""
    server.register_prompt(
        PromptDefinition(
            name=INCIDENT_TRIAGE_PROMPT,
            description="Prompt para triagem de incidentes usando contexto disponivel.",
            arguments=["user_question", "available_context"],
            handler=prompts.incident_triage_prompt,
        )
    )
    return server


def create_configured_mcp_server() -> SimpleMCPServer:
    """Cria o servidor completo usado nos exercicios finais."""
    server = create_mcp_server()
    register_ticket_tool(server)
    register_build_tool(server)
    register_doc_resources(server)
    register_prompts(server)
    return server
