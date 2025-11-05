# LangGraph Agent with Model Context Protocol

This demo pairs a LangGraph ReAct agent with a Model Context Protocol (MCP) server.
You can try the agent two ways: a simple CLI helper or a Streamlit chat UI.

## Requirements

Create a local virtual environment inside this folder and install the demo dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` (or create one) with at least:

```
OPENAI_API_KEY="your-openai-key"
OPENAI_MODEL="openai:gpt-4o-mini"  # optional, defaults to this value
LANGGRAPH_STREAMLIT_SYSTEM_PROMPT="You are an AI assistant..."  # optional
```

The Streamlit UI loads the same `.env` file, so you only need to set keys once.

## Option 1: Quick CLI Check

Run the helper script to verify the agent can talk to the MCP server:

```bash
python langgraph_mcp_client.py
```

The script sends a demo prompt and prints the assistant's final message.

## Option 2: Streamlit Chat UI

Launch the Streamlit chat experience (no authentication required):

```bash
streamlit run app.py
```

Use the sidebar to reset the conversation. The agent receives the full chat history and will decide when to invoke MCP tools.

## How It Works

1. The client connects to the MCP server over stdio and loads all advertised tools.
2. LangGraph's `create_react_agent` wraps the OpenAI model with those tools.
3. Each user turn sends the full chat history so the agent can plan tool calls.
4. The final assistant message (with any tool results) is rendered in the UI.

You can add more tools in `mcp-server.py` using the `@mcp.tool()` decorator—no Streamlit changes required.
