"""Utility helpers for invoking a LangGraph agent that is wired to an MCP server."""

import asyncio
import os
from pathlib import Path
from typing import List, Sequence, Union

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "openai:gpt-4o-mini")

RoleMessage = Union[BaseMessage, dict, str]

_ROLE_TO_MESSAGE = {
    "user": HumanMessage,
    "assistant": AIMessage,
    "system": SystemMessage,
}


def _to_message(entry: RoleMessage) -> BaseMessage:
    """Convert raw history entries to LangChain message objects."""

    if isinstance(entry, BaseMessage):
        return entry

    if isinstance(entry, dict):
        role = entry.get("role", "user").lower()
        content = entry.get("content", "")
        message_cls = _ROLE_TO_MESSAGE.get(role, HumanMessage)
        return message_cls(content=content)

    return HumanMessage(content=str(entry))


def _normalize_history(history: Sequence[RoleMessage]) -> List[BaseMessage]:
    if not history:
        raise ValueError("History must include at least one message before invoking the agent.")
    return [_to_message(item) for item in history]


def _server_params() -> StdioServerParameters:
    """Build Stdio server parameters that always resolve the MCP server path."""

    server_path = BASE_DIR / "mcp-server.py"
    return StdioServerParameters(
        command="python",
        args=[str(server_path)],
    )


async def ainvoke_agent(history: Sequence[RoleMessage]) -> dict:
    """Asynchronously invoke the LangGraph agent using the provided chat history."""

    async with stdio_client(_server_params()) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(DEFAULT_MODEL, tools)
            input_payload = {"messages": _normalize_history(history)}
            return await agent.ainvoke(input_payload)


def invoke_agent(history: Sequence[RoleMessage]) -> dict:
    """Synchronous wrapper around `ainvoke_agent` for environments like Streamlit."""

    return asyncio.run(ainvoke_agent(history))


if __name__ == "__main__":
    response = invoke_agent([{"role": "user", "content": "Summarize the content of the README.md"}])
    print("Agent Response:")
    print(response["messages"][-1].content)
