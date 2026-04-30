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
    raise NotImplementedError("Ex16 ainda nao implementado")


def compile_minimal_graph():
    """Contrato do Ex08: cria um grafo minimo executavel."""
    from stack_sentinel.llm.fake_client import FakeLLMClient    

    llm = FakeLLMClient()
  
    agent_builder = StateGraph(AgentState)    

    agent_builder.add_node("classify_intent", partial(nodes.classify_intent_node, llm=llm))
    agent_builder.add_node("fetch_ticket", partial(nodes.fetch_ticket_node, llm=llm))
    agent_builder.add_node("fetch_build", partial(nodes.fetch_build_node, llm=llm))
    agent_builder.add_node("fetch_docs", partial(nodes.fetch_docs_node, llm=llm))
    agent_builder.add_node("fallback", partial(nodes.fallback_node))

    agent_builder.add_edge(START, "classify_intent")
    agent_builder.add_conditional_edges(
        "classify_intent",
        route_by_intent,
        {
            "fetch_ticket": "fetch_ticket",
            "fetch_build": "fetch_build",
            "fetch_docs": "fetch_docs",
            "fallback": "fallback",
        },
    )
    agent_builder.add_edge("fetch_ticket", END)
    agent_builder.add_edge("fetch_build", END)
    agent_builder.add_edge("fetch_docs", END)
    agent_builder.add_edge("fallback", END)

    return agent_builder.compile()


agent = compile_minimal_graph()

with open('docs/graph.png', 'wb') as f:
  f.write(agent.get_graph().draw_mermaid_png())

user_input = input("Qual a mensagem? ")
messages = [create_initial_state(user_input)]
response = agent.invoke(messages[0])
print(response)


