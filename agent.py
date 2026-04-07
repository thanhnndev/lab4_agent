from __future__ import annotations

import os
from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels

load_dotenv()


with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools_list)


def agent_node(state: AgentState) -> dict:
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools_list))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition, {"tools": "tools", "__end__": END})
builder.add_edge("tools", "agent")
graph = builder.compile()


if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy (Base) - Ollama Backend")
    print("Type 'quit' to exit.")
    print("=" * 60)

    while True:
        user_input = input("\nBan: ").strip()
        if user_input.lower() in {"quit", "exit", "q"}:
            break
        result = graph.invoke({"messages": [("human", user_input)]})
        print(f"\nTravelBuddy: {result['messages'][-1].content}")
