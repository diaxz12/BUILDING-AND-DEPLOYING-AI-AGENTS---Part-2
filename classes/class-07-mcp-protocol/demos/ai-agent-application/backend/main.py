"""FastAPI backend that exposes the LangGraph travel planner agent."""

from __future__ import annotations

import os
import uuid
from typing import Optional

from datetime import date

from contextlib import nullcontext
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langfuse import get_client
from langfuse.langchain import CallbackHandler
from pydantic import BaseModel, Field

from agent import AgentSettings, AgentRuntime, build_agent, build_trip_prompt
from agent_guardrails import check_agent_answer, check_user_prompt

# Load variables from .env during local development
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()

# --- Settings ---------------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

LANGFUSE_PUBLIC = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

API_USERNAME = os.getenv("AGENT_API_USERNAME", "student")
API_PASSWORD = os.getenv("AGENT_API_PASSWORD", "travel-demo")


# --- FastAPI app ------------------------------------------------------------
app = FastAPI(title="Class 7 Travel Planner API", description="FastAPI + LangGraph + Guardrails + Langfuse demo.")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.agent = build_agent(
    AgentSettings(
        openai_api_key=OPENAI_API_KEY,
        model=OPENAI_MODEL,
        temperature=0.2,
        google_maps_api_key=GOOGLE_MAPS_API_KEY,
    )
)
app.state.active_tokens: dict[str, str] = {}


# --- Schemas ----------------------------------------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    token: str


class PlanRequest(BaseModel):
    destination: str = Field(..., description="City or place you want to visit.")
    num_days: int = Field(ge=1, le=21, description="Number of travel days.")
    budget: int = Field(ge=100, le=20000, description="Overall budget in USD.")
    preferences: str = Field(default="General sightseeing", description="What kind of trip you want.")
    session_id: Optional[str] = None
    start_date: date = Field(..., description="Trip start date.")


class PlanResponse(BaseModel):
    itinerary: str
    session_id: str
    monitored: bool
    source: str
    guardrails_note: Optional[str] = None


# --- Helpers ----------------------------------------------------------------
def create_token(username: str) -> str:
    return f"token-{uuid.uuid4()}-{username}"


def save_token(token: str, username: str) -> None:
    app.state.active_tokens[token] = username


def verify_token(x_auth_token: str = Header(..., convert_underscores=False)) -> str:
    username = app.state.active_tokens.get(x_auth_token)
    if not username:
        raise HTTPException(status_code=401, detail="Missing or invalid authentication token")
    return username


def build_fallback_reply(payload: PlanRequest) -> str:
    return (
        f"Here's a quick starter itinerary for {payload.destination}.\n"
        "- Morning: Explore the historic downtown and visit a popular museum.\n"
        "- Afternoon: Walk through a local park and sample regional cuisine.\n"
        "- Evening: Find a rooftop view for sunset.\n"
        "Upgrade your API keys to unlock richer MCP-powered suggestions."
    )


# --- Routes -----------------------------------------------------------------
@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest) -> LoginResponse:
    if credentials.username != API_USERNAME or credentials.password != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(credentials.username)
    save_token(token, credentials.username)
    return LoginResponse(message=f"Welcome back, {credentials.username}!", token=token)


@app.post("/plan", response_model=PlanResponse)
async def plan_trip(payload: PlanRequest, username: str = Depends(verify_token)) -> PlanResponse:
    session_id = payload.session_id or str(uuid.uuid4())
    user_prompt = build_trip_prompt(payload.dict())

    status, guardrails_message = check_user_prompt(user_prompt)
    if status != "ok":
        raise HTTPException(status_code=400, detail=guardrails_message or "Prompt blocked by guardrails.")

    langfuse_client = get_client()
    monitored = bool(langfuse_client.auth_check())

    callbacks = []
    if monitored:
        callbacks.append(CallbackHandler())

    span_context = (
        langfuse_client.start_as_current_span(name="travel-planner") if monitored else nullcontext()
    )

    with span_context as span:
        if span:
            span.update_trace(input=user_prompt, session_id=session_id)

        agent: AgentRuntime = app.state.agent
        itinerary = await agent.plan(user_prompt, callbacks=callbacks or None)

        if span:
            span.update_trace(output=itinerary or "fallback")

    source = f"langgraph:{OPENAI_MODEL}" if itinerary else "fallback"

    if not itinerary:
        itinerary = build_fallback_reply(payload)
    else:
        status, response_note = check_agent_answer(user_prompt, itinerary)
        if status != "ok":
            itinerary = build_fallback_reply(payload)
            source = "fallback"
            guardrails_message = response_note

    return PlanResponse(
        itinerary=itinerary,
        session_id=session_id,
        monitored=monitored,
        source=source,
        guardrails_note=guardrails_message,
    )
