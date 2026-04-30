from stack_sentinel.agent.state import AgentState, update_state
from stack_sentinel.clients.mcp_client import MCPClient
from stack_sentinel.llm.base import LLMClient
from stack_sentinel.shared.contracts import (
    BUILD_TOOL_NAME,
    INCIDENT_RESPONSE_RESOURCE,
    INCIDENT_TRIAGE_PROMPT,
    TICKET_TOOL_NAME,
)
from stack_sentinel.shared.utils import extract_build_id, extract_ticket_id


def classify_intent_node(state: AgentState, llm: LLMClient) -> AgentState:
    """Contrato do Ex10: classifica a intencao e atualiza state['intent']."""
    valid_intents = {"ticket", "build", "docs", "unknown"}
    intent = llm.classify_intent(state["user_input"])
    if intent not in valid_intents:
        intent = "unknown"
    return update_state(state, intent=intent)


def fetch_ticket_node(state: AgentState, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex12: consulta a tool MCP de ticket e atualiza o state."""
    ticket_id = state.get("ticket_id") or extract_ticket_id(state.get("user_input", ""))
    if not ticket_id:
        return update_state(state, error="Nenhum ticket_id encontrado no state ou no texto.", context=None)

    result = mcp_client.call_tool(TICKET_TOOL_NAME, {"ticket_id": ticket_id})
    if result.get("ok"):
        return update_state(state, ticket_id=ticket_id, context=result, error=None)
    return update_state(state, error=result.get("error", "Erro ao consultar ticket"), context=None)


def fetch_build_node(state: AgentState, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex13: consulta a tool MCP de build e atualiza o state."""
    build_id = state.get("build_id") or extract_build_id(state.get("user_input", ""))
    if not build_id:
        return update_state(state, error="Nenhum build_id encontrado no state ou no texto.", context=None)

    result = mcp_client.call_tool(BUILD_TOOL_NAME, {"build_id": build_id})
    if result.get("ok"):
        return update_state(state, build_id=build_id, context=result, error=None)
    return update_state(state, error=result.get("error", "Erro ao consultar build"), context=None)


def fetch_docs_node(state: AgentState, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex14: le resource/prompt MCP e atualiza o context."""
    try:
        resource = mcp_client.read_resource(INCIDENT_RESPONSE_RESOURCE)
        available_context = resource.get("content", "") if resource.get("ok") else ""

        prompt = mcp_client.get_prompt(
            INCIDENT_TRIAGE_PROMPT,
            {
                "user_question": state.get("user_input", ""),
                "available_context": available_context,
            },
        )

        return update_state(
            state,
            context={"resource": resource, "prompt": prompt},
            error=None,
        )
    except Exception as exc:
        return update_state(state, error=str(exc), context=None)


def fallback_node(state: AgentState) -> AgentState:
    return update_state(
        state,
        error="Nao encontrei uma rota segura para esta pergunta.",
        final_answer="Nao consegui identificar se a pergunta e sobre ticket, build ou documentacao.",
    )


def final_answer_node(state: AgentState) -> AgentState:
    """Contrato do Ex15: transforma state/context em resposta final."""
    intent = state.get("intent")
    context = state.get("context")
    error = state.get("error")

    if intent == "unknown" or error:
        return update_state(
            state,
            final_answer="Nao consegui identificar uma rota segura para responder sua pergunta.",
        )

    if intent == "ticket" and context and context.get("ok"):
        answer = (
            f"## Resumo\n"
            f"{context.get('summary', 'Sem resumo disponivel.')}\n\n"
            f"## Evidencias\n"
            f"- ID: {context.get('id')}\n"
            f"- Severidade: {context.get('severity')}\n"
            f"- Servico: {context.get('service')}\n"
            f"- Status: {context.get('status')}\n"
            f"- Build associado: {context.get('build_id')}\n\n"
            f"## Proximo passo\n"
            f"Investigar o build {context.get('build_id')} associado ao ticket {context.get('id')} "
            f"para identificar a causa raiz."
        )
        return update_state(state, final_answer=answer)

    if intent == "build" and context and context.get("ok"):
        answer = (
            f"## Resumo\n"
            f"Build {context.get('id')} com status {context.get('status')}.\n\n"
            f"## Evidencias\n"
            f"- ID: {context.get('id')}\n"
            f"- Status: {context.get('status')}\n"
            f"- Servico: {context.get('service')}\n"
            f"- Branch: {context.get('branch')}\n"
            f"- Etapa que falhou: {context.get('failed_step')}\n"
            f"- Log: {context.get('log_excerpt')}\n\n"
            f"## Proximo passo\n"
            f"Analisar a etapa {context.get('failed_step')} e o log para identificar a causa da falha."
        )
        return update_state(state, final_answer=answer)

    if intent == "docs" and context:
        resource = context.get("resource", {})
        prompt = context.get("prompt", {})
        resource_title = resource.get("title", "Documento desconhecido")
        resource_content = resource.get("content", "")
        prompt_content = prompt.get("content", "")
        answer = (
            f"## Resumo\n"
            f"Consulta ao documento: {resource_title}\n\n"
            f"## Evidencias\n"
            f"{resource_content}\n\n"
            f"## Proximo passo\n"
            f"{prompt_content}"
        )
        return update_state(state, final_answer=answer)

    return update_state(
        state,
        final_answer="Nao consegui gerar uma resposta a partir do contexto disponivel.",
    )
