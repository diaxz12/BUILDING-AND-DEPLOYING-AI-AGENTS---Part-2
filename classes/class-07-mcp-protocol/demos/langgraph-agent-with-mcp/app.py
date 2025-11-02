"""Streamlit UI for chatting with the LangGraph + MCP agent."""

import os
from typing import Dict, List

import streamlit as st
from dotenv import load_dotenv

from langgraph_mcp_client import invoke_agent

# Load environment variables from .env so Streamlit sees the same config as the CLI demo.
load_dotenv()

st.set_page_config(page_title="LangGraph MCP Agent", page_icon="🛠️")

SYSTEM_PROMPT = os.getenv(
    "LANGGRAPH_STREAMLIT_SYSTEM_PROMPT",
    "You are an AI assistant that can call MCP tools to inspect files inside this project.",
)

if "messages" not in st.session_state:
    st.session_state.messages: List[Dict[str, str]] = []
    if SYSTEM_PROMPT:
        st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})


def reset_conversation() -> None:
    """Clear the Streamlit chat history while preserving the system prompt."""

    initial_history = []
    if SYSTEM_PROMPT:
        initial_history.append({"role": "system", "content": SYSTEM_PROMPT})
    st.session_state.messages = initial_history


st.title("LangGraph MCP Agent Sandbox")
st.caption("Ask questions, and the agent will decide when to call MCP tools exposed by `mcp-server.py`.")

with st.sidebar:
    st.header("Controls")
    if st.button("Reset conversation"):
        reset_conversation()
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()

    st.write(
        "Set your OpenAI key in `.env` and start the MCP server tools by running "
        "`python mcp-server.py` in this directory."
    )

for message in st.session_state.messages:
    if message["role"] == "system":
        st.info(message["content"])
        continue
    st.chat_message(message["role"]).markdown(message["content"])

user_input = st.chat_input("Send a message to the agent")
if not user_input:
    st.stop()

st.session_state.messages.append({"role": "user", "content": user_input})
st.chat_message("user").markdown(user_input)

with st.chat_message("assistant"):
    with st.spinner("Running LangGraph agent..."):
        try:
            result = invoke_agent(st.session_state.messages)
            agent_message = result["messages"][-1]
            assistant_reply = getattr(agent_message, "content", str(agent_message))
        except Exception as exc:  # surface failures without breaking the UI loop
            assistant_reply = f"Sorry, something went wrong invoking the agent: {exc}"
    st.markdown(assistant_reply)

st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
