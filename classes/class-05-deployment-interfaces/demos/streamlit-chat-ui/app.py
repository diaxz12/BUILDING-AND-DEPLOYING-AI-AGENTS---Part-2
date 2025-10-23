"""Streamlit chat page that talks to the FastAPI agent."""

import os
import uuid

import requests
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(page_title="Class 5 AI Agent Chat Demo", page_icon="🤖")

STREAMLIT_USERNAME = os.getenv("STREAMLIT_UI_USERNAME", "student")
STREAMLIT_PASSWORD = os.getenv("STREAMLIT_UI_PASSWORD", "streamlit-demo")

if "messages" not in st.session_state:
    st.session_state.messages = []  # keeps the chat visible after each rerun
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "api_base" not in st.session_state:
    st.session_state.api_base = os.getenv("AGENT_API_BASE", "http://localhost:8000")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "api_token" not in st.session_state:
    st.session_state.api_token = None
if "login_notice" not in st.session_state:
    st.session_state.login_notice = None

def authenticate_api(username: str, password: str) -> bool:
    """Request an auth token from the FastAPI backend."""

    url = f"{st.session_state.api_base}/login"
    try:
        response = requests.post(
            url,
            json={"username": username, "password": password},
            timeout=10,
        )
        response.raise_for_status()
        token = response.json().get("token")
        if not token:
            st.warning("Login succeeded but no token returned. Using offline tips instead.")
            st.session_state.api_token = None
            return False
        st.session_state.api_token = token
        return True
    except Exception as exc:
        st.warning(f"Could not authenticate with the FastAPI service ({exc}). Offline tips will be used.")
        st.session_state.api_token = None
        return False


def require_login() -> None:
    """Prompt for credentials before rendering the chat UI."""

    if st.session_state.authenticated:
        return
    login_placeholder = st.empty()
    feedback_placeholder = st.empty()

    with login_placeholder:
        st.title("Agent Chat Login")
        st.write("Enter the credentials shared in class to try the chat demo.")

        with st.form("login-form", clear_on_submit=False):
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in")

    if submitted:
        if username_input == STREAMLIT_USERNAME and password_input == STREAMLIT_PASSWORD:
            st.session_state.username = username_input
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            api_ready = authenticate_api(username_input, password_input)
            if api_ready:
                st.session_state.login_notice = ("success", "Login successful. Loading the chat interface…")
            else:
                st.session_state.login_notice = ("info", "Logged in. Chat requests will use offline answers until the FastAPI service accepts your credentials.")
            st.session_state.authenticated = True
            login_placeholder.empty()
            feedback_placeholder.empty()
            try:
                st.rerun()
            except AttributeError:  # Streamlit < 1.27 compatibility
                st.experimental_rerun()
        else:
            feedback_placeholder.error("Invalid username or password. Try again.")

    st.stop()


def send_to_api(user_text: str):
    payload = {"message": user_text, "session_id": st.session_state.session_id}
    url = f"{st.session_state.api_base}/chat"
    headers = {}
    if st.session_state.api_token:
        headers["x_auth_token"] = st.session_state.api_token
    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers or None,
            timeout=20,
        )
        if response.status_code == 401:
            st.warning("API token rejected. Log out and back in to refresh your session.")
            st.session_state.api_token = None
            response.raise_for_status()
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        st.warning(f"Could not reach the API ({exc}). Showing a built-in answer instead.")
        return {
            "reply": offline_tip(user_text),
            "source": "offline",
            "monitored": False,
            "session_id": st.session_state.session_id,
        }


def offline_tip(user_text: str) -> str:
    text = user_text.lower()
    if "streamlit" in text:
        return "Tip: Streamlit reruns the script top-to-bottom on every interaction."
    if "fastapi" in text:
        return "Tip: FastAPI gives you Swagger docs at /docs with no extra work."
    if "langfuse" in text or "monitor" in text:
        return "Tip: Set Langfuse keys to record each request and response."
    return "Try asking about Streamlit, FastAPI, or Langfuse to see targeted pointers."


require_login()

notice = st.session_state.login_notice
if notice:
    level, message = notice
    if level == "success":
        st.success(message)
    elif level == "info":
        st.info(message)
    elif level == "warning":
        st.warning(message)
    elif level == "error":
        st.error(message)
    st.session_state.login_notice = None

with st.sidebar:
    st.header("Account")
    st.caption(f"Signed in as: {st.session_state.username or STREAMLIT_USERNAME}")
    if st.button("Log out"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.api_token = None

    st.header("Setup")
    st.session_state.api_base = st.text_input(
        label="FastAPI base URL",
        value=st.session_state.api_base,
        help="Use the Render URL once the API is deployed.",
    )
    if st.button("Start over"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.info("Chat history cleared. New session ID created.")
    st.caption("Run `uvicorn main:app --reload` inside the API folder first.")
    st.caption(f"Current session: {st.session_state.session_id}")

st.title("Class 5 Playground")
st.write("Type a question about deploying agents. The UI forwards it to FastAPI.")

for entry in st.session_state.messages:
    st.chat_message(entry["role"]).markdown(entry["content"])

user_input = st.chat_input("Ask something about deployment")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Waiting for FastAPI..."):
            data = send_to_api(user_input)
        st.markdown(data["reply"])
        st.caption(f"Source: {data['source']} • Langfuse trace: {data['monitored']}")
        st.session_state.messages.append({"role": "assistant", "content": data["reply"]})
