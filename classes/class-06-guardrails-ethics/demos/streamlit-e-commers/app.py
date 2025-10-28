"""Minimal Streamlit chat UI for the no-guardrails e-commerce agent."""
import uuid
from typing import Any

import requests
import streamlit as st

DEFAULT_API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Checkout Charlie", page_icon="🛍️", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages: list[dict[str, str]] = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "api_base" not in st.session_state:
    st.session_state.api_base = DEFAULT_API_BASE.rstrip("/")


def reset_conversation() -> None:
    st.session_state.messages = []
    st.session_state.session_id = str(uuid.uuid4())


def send_to_api(user_text: str) -> dict[str, Any]:
    payload = {
        "message": user_text,
        "session_id": st.session_state.session_id,
        "messages": [dict(entry) for entry in st.session_state.messages],
    }
    url = f"{st.session_state.api_base}/chat"
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"API unreachable: {exc}")


with st.sidebar:
    st.header("Setup")
    st.session_state.api_base = st.text_input(
        "Agent API base",
        value=st.session_state.api_base,
        help="Point to the no-guardrails FastAPI service (default http://localhost:8000).",
    ).rstrip("/") or st.session_state.api_base
    st.caption(f"Session ID: {st.session_state.session_id}")

    if st.button("Start new conversation"):
        reset_conversation()
        st.toast("New session created", icon="🔄")

st.title("Checkout Charlie")
st.write(
    "Use this chat to explore the unsafe and safe e-commerce agent."
)

for entry in st.session_state.messages:
    st.chat_message(entry["role"]).markdown(entry["content"])

prompt = st.chat_input("Ask Checkout Charlie anything…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Querying Checkout Charlie…"):
                response = send_to_api(prompt)
        except RuntimeError as exc:
            st.error(str(exc))
        else:
            reply_text = response.get("reply", "<no reply>")
            st.markdown(reply_text)
            if response.get("guardrails_applied"):
                st.warning("Guardrail violations reported.", icon="⚠️")
            st.session_state.messages.append({"role": "assistant", "content": reply_text})
