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


def fetch_ticket_node(state: AgentState, llm: LLMClient) -> AgentState:
    """Contrato do Ex12: consulta a tool MCP de ticket e atualiza o state."""
    raise NotImplementedError("Ex12 ainda nao implementado")


def fetch_build_node(state: AgentState, llm: LLMClient) -> AgentState:
    """Contrato do Ex13: consulta a tool MCP de build e atualiza o state."""
    raise NotImplementedError("Ex13 ainda nao implementado")


def fetch_docs_node(state: AgentState, llm: LLMClient) -> AgentState:
    """Contrato do Ex14: le resource/prompt MCP e atualiza o context."""
    raise NotImplementedError("Ex14 ainda nao implementado")


def fallback_node(state: AgentState) -> AgentState:
    return update_state(
        state,
        error="Nao encontrei uma rota segura para esta pergunta.",
        final_answer="Nao consegui identificar se a pergunta e sobre ticket, build ou documentacao.",
    )


def final_answer_node(state: AgentState) -> AgentState:
    """Contrato do Ex15: transforma state/context em resposta final."""
    raise NotImplementedError("Ex15 ainda nao implementado")
