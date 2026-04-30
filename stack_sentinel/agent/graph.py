from functools import partial
from typing import Callable, List

from stack_sentinel.agent.state import AgentState, create_initial_state
from stack_sentinel.clients.mcp_client import MCPClient
from stack_sentinel.llm.base import LLMClient
from langgraph.graph import StateGraph, START, END
from stack_sentinel.agent import nodes


Node = Callable[[AgentState], AgentState]


class SimpleGraph:
    def __init__(self):
        self.nodes: List[Node] = []

    def add_node(self, node: Node) -> None:
        self.nodes.append(node)

    def run(self, state: AgentState) -> AgentState:
        current = state
        for node in self.nodes:
            current = node(current)
        return current

def route_by_intent(state: AgentState) -> str:
    """Contrato do Ex11: retorna a rota a partir de state['intent']."""
    routes = {
        "ticket": "fetch_ticket",
        "build": "fetch_build",
        "docs": "fetch_docs",
    }
    return routes.get(state.get("intent"), "fallback")


def run_stack_sentinel_flow(state: AgentState, llm: LLMClient, mcp_client: MCPClient) -> AgentState:
    """Contrato do Ex16: executa o fluxo final ponta a ponta."""
    graph = compile_minimal_graph(llm=llm, mcp_client=mcp_client)
    return graph.invoke(state)


def compile_minimal_graph(llm=None, mcp_client=None):
    """Contrato do Ex08: cria um grafo minimo executavel."""
    from stack_sentinel.llm.fake_client import FakeLLMClient
    from stack_sentinel.mcp_server.server import create_configured_mcp_server

    if llm is None:
        llm = FakeLLMClient()
    if mcp_client is None:
        mcp_client = MCPClient(create_configured_mcp_server())

    from stack_sentinel.shared.utils import extract_ticket_id, extract_build_id

    def extract_ticket_id_node(state: AgentState) -> AgentState:
        ticket_id = extract_ticket_id(state.get("user_input", ""))
        return {**state, "ticket_id": ticket_id}

    def extract_build_id_node(state: AgentState) -> AgentState:
        build_id = extract_build_id(state.get("user_input", ""))
        return {**state, "build_id": build_id}

    agent_builder = StateGraph(AgentState)

    agent_builder.add_node("classify_intent", partial(nodes.classify_intent_node, llm=llm))
    agent_builder.add_node("extract_ticket_id", extract_ticket_id_node)
    agent_builder.add_node("extract_build_id", extract_build_id_node)
    agent_builder.add_node("fetch_ticket", partial(nodes.fetch_ticket_node, mcp_client=mcp_client))
    agent_builder.add_node("fetch_build", partial(nodes.fetch_build_node, mcp_client=mcp_client))
    agent_builder.add_node("fetch_docs", partial(nodes.fetch_docs_node, mcp_client=mcp_client))
    agent_builder.add_node("fallback", nodes.fallback_node)
    agent_builder.add_node("final_answer", nodes.final_answer_node)

    agent_builder.add_edge(START, "classify_intent")
    agent_builder.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "fetch_ticket": "extract_ticket_id",
            "fetch_build": "extract_build_id",
            "fetch_docs": "fetch_docs",
            "fallback": "fallback",
        },
    )
    agent_builder.add_edge("extract_ticket_id", "fetch_ticket")
    agent_builder.add_edge("extract_build_id", "fetch_build")
    agent_builder.add_edge("fetch_ticket", "final_answer")
    agent_builder.add_edge("fetch_build", "final_answer")
    agent_builder.add_edge("fetch_docs", "final_answer")
    agent_builder.add_edge("fallback", "final_answer")
    agent_builder.add_edge("final_answer", END)

    return agent_builder.compile()


if __name__ == "__main__":
    agent = compile_minimal_graph()

    with open('docs/graph.png', 'wb') as f:
        f.write(agent.get_graph().draw_mermaid_png())

    user_input = input("Qual a mensagem? ")
    messages = [create_initial_state(user_input)]
    response = agent.invoke(messages[0])
    print(response)


