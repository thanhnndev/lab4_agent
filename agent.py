from __future__ import annotations

import os
import re
import time
import sys
from typing import Annotated, Sequence

from dotenv import load_dotenv
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    AIMessageChunk,
    BaseMessage,
    ToolMessage,
)
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import InMemorySaver
from typing_extensions import TypedDict

from tools import calculate_budget, search_flights, search_hotels

load_dotenv()


with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


class AgentState(TypedDict):
    """State for the agent with properly typed messages."""

    messages: Annotated[Sequence[BaseMessage], add_messages]


tools_list = [search_flights, search_hotels, calculate_budget]
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "llama3.1:8b"),
    base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
    temperature=0,
)
llm_with_tools = llm.bind_tools(tools_list)

DEV_MODE = os.getenv("DEV", "false").lower() == "true"


def agent_node(state: AgentState) -> dict:
    """
    Agent node that processes messages and generates responses.
    The SystemMessage is always added at the beginning of the conversation.
    """
    messages = list(state["messages"])

    # Always ensure SystemMessage is first
    # Remove any existing SystemMessage to avoid duplicates, then add fresh one
    messages = [msg for msg in messages if not isinstance(msg, SystemMessage)]
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def get_last_ai_message_content(messages: Sequence[BaseMessage]) -> str:
    """
    Extract the content from the last AIMessage that has actual content.
    This handles cases where the last message might be a ToolMessage or
    an AIMessage with only tool_calls and no content.
    """
    # Iterate backwards through messages to find the last AIMessage with content
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            # Skip messages that only have tool_calls but no content
            if msg.content:
                return str(msg.content)
            # If this AIMessage has tool_calls but no content, continue looking
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                continue
    return ""


def get_last_ai_message(messages: Sequence[BaseMessage]) -> AIMessage | None:
    """
    Get the last AIMessage from the messages list.
    Returns None if no AIMessage found.
    """
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            return msg
    return None


# Regex patterns for thinking extraction
THINKING_PATTERNS = [
    re.compile(r"<thinking>(.*?)</thinking>", re.DOTALL | re.IGNORECASE),
    re.compile(
        r"<\|begin▁of▁sentence\|>(.*?)<\|end▁of▁sentence\|>", re.DOTALL | re.IGNORECASE
    ),
    re.compile(r"<thought>(.*?)</thought>", re.DOTALL | re.IGNORECASE),
    re.compile(r"<reasoning>(.*?)</reasoning>", re.DOTALL | re.IGNORECASE),
]


def extract_thinking(text: str) -> tuple[str | None, str]:
    """
    Extract thinking content from model output.
    Returns: (thinking_content or None, clean_text_without_thinking)
    """
    if not text:
        return None, ""

    for pattern in THINKING_PATTERNS:
        match = pattern.search(text)
        if match:
            thinking = match.group(1).strip()
            # Remove the thinking tag from the text to get clean answer
            clean_text = pattern.sub("", text).strip()
            return thinking, clean_text
    return None, text


def process_content_blocks(message: AIMessageChunk) -> tuple[str | None, str]:
    """
    Try to extract reasoning from content_blocks if available.
    Some models (like newer Ollama versions) provide separate content blocks.
    """
    thinking_parts = []
    text_parts = []

    # Check if message has content_blocks attribute
    if hasattr(message, "content_blocks") and message.content_blocks:
        for block in message.content_blocks:
            if isinstance(block, dict):
                block_type = block.get("type", "text")
                if block_type == "reasoning" or block_type == "think":
                    thinking_parts.append(block.get("text", ""))
                elif block_type == "text":
                    text_parts.append(block.get("text", ""))
            else:
                # Handle string content blocks
                text_parts.append(str(block))

        if thinking_parts:
            return "\n".join(thinking_parts), "\n".join(text_parts)

    # Fallback: return None to indicate content_blocks weren't used
    return None, None


# Build the graph with checkpointer for state persistence
memory = InMemorySaver()

builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools_list))

# Simple flow: agent -> (tools) -> agent -> END
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent", tools_condition, {"tools": "tools", "__end__": END}
)
# After tools, go back to agent for final response
builder.add_edge("tools", "agent")

graph = builder.compile(checkpointer=memory)


def format_tool_call(tool_call: dict) -> str:
    """Format a tool call for display."""
    name = tool_call.get("name", "unknown")
    args = tool_call.get("args", {})

    # Format arguments nicely
    if isinstance(args, dict):
        args_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
    else:
        args_str = str(args)

    return f"{name}({args_str})"


def stream_agent_interaction(
    graph, user_message: HumanMessage, config: dict
) -> tuple[str, list, float]:
    """
    Stream the agent interaction and show intermediate steps.

    Returns:
        - final_response: The final text response
        - all_messages: All messages generated during the interaction
        - elapsed_time: Total time taken
    """
    start_time = time.time()
    all_messages = []
    tool_calls_made = []
    thinking_content = None

    # Track which steps we've shown
    showed_thinking = False
    showed_tool_call = False

    print("\n🤔 Agent đang suy nghĩ...")
    sys.stdout.flush()

    # Stream through the graph
    for chunk in graph.stream(
        {"messages": [user_message]},
        config=config,
        stream_mode="updates",  # This gives us updates at each node
    ):
        for node_name, node_output in chunk.items():
            if node_name == "agent":
                # Agent node executed
                messages = node_output.get("messages", [])
                all_messages.extend(messages)

                for msg in messages:
                    if isinstance(msg, AIMessage):
                        # Check for tool calls
                        if hasattr(msg, "tool_calls") and msg.tool_calls:
                            if not showed_tool_call:
                                print(f"\n🔧 Đang gọi công cụ:")
                                showed_tool_call = True

                            for tc in msg.tool_calls:
                                formatted = format_tool_call(tc)
                                tool_calls_made.append(tc)
                                print(f"   📞 {formatted}")
                                sys.stdout.flush()

                        # Check for content (thinking or response)
                        if msg.content:
                            # Try to extract thinking
                            thinking, clean = extract_thinking(msg.content)
                            if thinking and not showed_thinking:
                                thinking_content = thinking
                                if DEV_MODE:
                                    print(
                                        f"\n🧠 Phát hiện suy nghĩ nội bộ ({len(thinking)} ký tự)"
                                    )
                                    sys.stdout.flush()
                                showed_thinking = True

                            # If this is a response with no tool calls, it's the final answer
                            if not (hasattr(msg, "tool_calls") and msg.tool_calls):
                                print(f"\n📝 Agent đang hoàn thiện câu trả lời...")
                                sys.stdout.flush()

            elif node_name == "tools":
                # Tools node executed
                messages = node_output.get("messages", [])
                all_messages.extend(messages)

                for msg in messages:
                    if isinstance(msg, ToolMessage):
                        # Truncate long tool results
                        content_preview = (
                            msg.content[:200] if len(msg.content) > 200 else msg.content
                        )
                        if len(msg.content) > 200:
                            content_preview += "..."
                        print(f"\n✅ Kết quả từ '{msg.name}': {content_preview}")
                        sys.stdout.flush()

                # After tools, agent will think again
                showed_thinking = False
                print(f"\n🤔 Agent đang phân tích kết quả...")
                sys.stdout.flush()

    elapsed_time = time.time() - start_time

    # Get the final response
    final_response = get_last_ai_message_content(all_messages)

    return final_response, all_messages, elapsed_time, thinking_content


if __name__ == "__main__":
    print("=" * 60)
    print("TravelBuddy (Interactive) - Ollama Backend")
    if DEV_MODE:
        print("Mode: DEVELOPMENT (debug enabled)")
    print("Type 'quit' to exit.")
    print("=" * 60)
    print(
        "\n💡 Tính năng mới: Bạn sẽ thấy quá trình suy nghĩ và gọi công cụ của Agent!"
    )
    print("-" * 60)

    # Use thread_id for persistent conversation state
    config = {"configurable": {"thread_id": "travelbuddy-session"}}

    while True:
        try:
            user_input = input("\n🧑 Bạn: ").strip()
        except EOFError:
            break

        if user_input.lower() in {"quit", "exit", "q"}:
            break

        if not user_input:
            continue

        # Create a HumanMessage from user input
        user_message = HumanMessage(content=user_input)

        try:
            # Stream the interaction with visible intermediate steps
            final_response, all_messages, elapsed_time, thinking_content = (
                stream_agent_interaction(graph, user_message, config)
            )

            # If no content found, show error
            if not final_response:
                print("\n🤖 TravelBuddy: (Xin lỗi, tôi không thể tạo phản hồi)")
                if DEV_MODE and all_messages:
                    print(f"\n  Debug: Có {len(all_messages)} messages trong state")
                continue

            # Extract thinking and clean answer
            extracted_thinking, clean_answer = extract_thinking(final_response)
            if extracted_thinking:
                thinking_content = extracted_thinking

            # Ensure we have something to display
            if not clean_answer:
                clean_answer = final_response

            # Print the final answer
            print(f"\n🤖 TravelBuddy: ", end="", flush=True)

            # Simulate streaming by printing character by character with small delay
            import time as time_module

            for i, char in enumerate(clean_answer):
                print(char, end="", flush=True)
                # Small delay every 3 characters for streaming effect
                if i % 3 == 0:
                    time_module.sleep(0.005)

            print()  # New line after response
            sys.stdout.flush()

            # Calculate timing
            chars_per_sec = len(clean_answer) / elapsed_time if elapsed_time > 0 else 0

        except Exception as e:
            print(f"\n\n❌ Lỗi: {e}", flush=True)
            import traceback

            traceback.print_exc()
            continue

        # DEV MODE DEBUG INFO - Show thinking block HERE, after answer
        if DEV_MODE and clean_answer:
            print("\n" + "=" * 50)
            print("🔍 THÔNG TIN DEBUG")
            print("=" * 50)

            if thinking_content:
                print("\n🧠 THINKING BLOCK:")
                print("-" * 50)
                preview = thinking_content[:800]
                print(preview + ("..." if len(thinking_content) > 800 else ""))
                print("-" * 50)

            print(f"\n📊 Hiệu suất:")
            print(f"  • Tổng ký tự: {len(clean_answer)}")
            print(
                f"  • Thời gian tạo: {elapsed_time:.2f}s ({chars_per_sec:.1f} ký tự/s)"
            )

            print(f"\n🔧 Quá trình thực thi:")
            print(f"  • Nhận phản hồi thành công")

            # Show all messages in state
            try:
                state = graph.get_state(config)
                msg_count = len(state.values.get("messages", []))
                print(f"\n💬 Tổng messages trong state: {msg_count}")

                # Show message types for debugging
                if all_messages:
                    print("\n📨 Chi tiết messages:")
                    for i, msg in enumerate(all_messages):
                        msg_type = type(msg).__name__
                        has_content = bool(getattr(msg, "content", None))
                        has_tools = bool(getattr(msg, "tool_calls", None))
                        content_preview = ""
                        if has_content and msg.content:
                            content_preview = (
                                str(msg.content)[:60] + "..."
                                if len(str(msg.content)) > 60
                                else str(msg.content)
                            )
                        print(
                            f"    [{i}] {msg_type}: content={has_content}, tools={has_tools}"
                        )
                        if content_preview:
                            print(f"        └─ {content_preview}")

            except Exception as e:
                if DEV_MODE:
                    print(f"\n  Debug error getting state: {e}")

            print("=" * 50)
            sys.stdout.flush()
