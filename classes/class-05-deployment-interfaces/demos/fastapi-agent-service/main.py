"""FastAPI chat service with a LangGraph ReAct agent plus simple fallbacks."""

import os
from typing import Any, Optional
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI 
from langchain_core.tools import tool  
from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

# Load environment variables from .env file
load_dotenv()

# Pydantic python data models to ensure data integrity and validity
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    source: str
    monitored: bool
    session_id: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    message: str
    token: str


# Initializes the FastAPI
app = FastAPI(title="Class 5 Agent API", description="ReAct agent with tool access and monitoring.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.active_tokens: dict[str, str] = {}


# --- Setup helpers ---------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

LANGFUSE_PUBLIC = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")
LANGFUSE_ENV = os.getenv("LANGFUSE_TRACING_ENVIRONMENT", "development")
AGENT_API_USERNAME = os.getenv("AGENT_API_USERNAME")
AGENT_API_PASSWORD = os.getenv("AGENT_API_PASSWORD")

if not AGENT_API_USERNAME or not AGENT_API_PASSWORD:
    print("[Auth] Warning: AGENT_API_USERNAME or AGENT_API_PASSWORD is missing. Login will fail until both are set.")

def build_tools():
    """Create helper tools the agent can call."""

    if tool is None:
        return []

    @tool
    def streamlit_playbook(question: str) -> str:
        """Return short tips for building Streamlit interfaces."""

        question = question.lower()
        print("[Tool] streamlit_playbook called")
        if "deploy" in question:
            return "Push to GitHub, then deploy on Streamlit Community Cloud with your main app file."
        if "state" in question:
            return "Use st.session_state to remember chat history or cached data between reruns."
        return "Streamlit reruns your script from top to bottom. Keep UI simple and react to user inputs."  # noqa: E501

    @tool
    def deployment_checklist(topic: str) -> str:
        """Outline the steps to expose an agent via API."""

        topic = topic.lower()
        print("[Tool] deployment_checklist called")
        if "fastapi" in topic:
            return "Create endpoints, test with /docs, add CORS for the UI, and deploy via Render or similar."
        if "monitor" in topic or "langfuse" in topic:
            return "Capture traces per request, store inputs/outputs, review failures, then iterate on prompts/tools."
        return "General flow: build API locally, write a health check, containerize or deploy to Render, add monitoring."  # noqa: E501

    return [streamlit_playbook, deployment_checklist]


def build_agent_runner():
    """Instantiate the LangGraph ReAct agent if dependencies and keys exist."""

    if not (OPENAI_API_KEY and create_react_agent and ChatOpenAI):
        return None

    tools = build_tools()
    if not tools:
        return None

    try:
        llm = ChatOpenAI(model=OPENAI_MODEL, temperature=0, api_key=OPENAI_API_KEY)
        return create_react_agent(llm, tools)
    except Exception as exc:  # keep the API functional without the agent
        print(f"[LangGraph] could not create agent, using rule-based replies. Error: {exc}")
        return None


agent_runner = build_agent_runner()


def run_agent(message: str) -> Optional[str]:
    """Ask the LangGraph agent for a reply; return None if unavailable."""
 
    # Initialize Langfuse CallbackHandler for Langchain (tracing)
    langfuse_handler = CallbackHandler()

    if agent_runner is None:
        return None

    try:
        result = agent_runner.invoke({"messages": [("user", message)]}, config={"callbacks": [langfuse_handler]})
    except Exception as exc:  # fall back to rule-based helper on errors
        print(f"[LangGraph] agent invocation failed: {exc}")
        return None

    messages = result.get("messages") if isinstance(result, dict) else None
    if not messages:
        return None

    last_message = messages[-1]
    content = getattr(last_message, "content", last_message)
    return _content_to_text(content)


def _content_to_text(content: Any) -> Optional[str]:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        chunks = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                chunks.append(str(item["text"]))
            elif isinstance(item, str):
                chunks.append(item)
        return "\n".join(chunks).strip() if chunks else None
    if isinstance(content, dict) and "text" in content:
        return str(content["text"])
    return str(content) if content is not None else None


# --- Fallback replies ------------------------------------------------------
def build_offline_reply(message: str) -> str:
    text = message.lower()
    if "streamlit" in text:
        return "Streamlit reruns your script after every click. Keep anything you need in st.session_state."
    if "fastapi" in text:
        return "FastAPI ships with automatic docs at /docs. Try them once the server is running!"
    if "langfuse" in text or "monitor" in text:
        return "Langfuse links inputs and outputs. Set the keys to see traces pop up in the dashboard."
    if "deploy" in text:
        return "Deploy the API first, then point your Streamlit app to the live URL to share it."
    return "I am in offline mode. Ask about Streamlit, FastAPI, or Langfuse to see directed tips."


def invoke_agent(message: str, langfuse_client: Langfuse, session_id: str) -> tuple[str, str]:
    # Use the predefined session ID with trace_context
    with langfuse_client.start_as_current_span(
        name="🤖-fastapi-agent"
    ) as span:
        span.update_trace(input=message, session_id="chat_tutai_123")

        agent_reply = run_agent(message)

        span.update_trace(output=agent_reply)

    if agent_reply:
        return agent_reply, f"langgraph:{OPENAI_MODEL}"
    return build_offline_reply(message), "rule-based"

# Generate token for authentication
def create_token(username: str) -> str:
    return f"token-{uuid4()}-{username}"

# Persist the token on the "memory" of the API
def save_token(token: str, username: str) -> None:
    app.state.active_tokens[token] = username

# Validate if the token passed by the user matches the one that was generated by the API
def verify_token(x_auth_token: str = Header(..., convert_underscores=False)) -> str:
    username = app.state.active_tokens.get(x_auth_token)
    if not username:
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    return username


# --- Routes -----------------------------------------------------------------
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest) -> LoginResponse:
    if not AGENT_API_USERNAME or not AGENT_API_PASSWORD:
        raise HTTPException(status_code=500, detail="Server credentials are not configured")

    if credentials.username != AGENT_API_USERNAME or credentials.password != AGENT_API_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(credentials.username)
    save_token(token, credentials.username)
    return LoginResponse(message=f"Welcome back, {credentials.username}!", token=token)


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, username: str = Depends(verify_token)) -> ChatResponse:
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="message cannot be empty")

    # ID of the conversation
    session_id = payload.session_id
 
    # Verify connection
    langfuse_client = get_client()
    if langfuse_client.auth_check():
        print("Langfuse client is authenticated and ready!")
        monitored = True
    else:
        print("Authentication failed. Please check your credentials and host.")
        monitored = False

    # invoke the agent
    reply, source = invoke_agent(
        message=message,
        langfuse_client=langfuse_client,
        session_id=session_id
    )

    return ChatResponse(
        reply=reply,
        source=source,
        monitored=monitored,
        session_id=session_id
    )
