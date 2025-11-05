"""LangGraph travel planner agent used by the FastAPI backend."""

from __future__ import annotations

import json
from contextlib import AsyncExitStack, asynccontextmanager
from datetime import date, datetime
from dataclasses import dataclass
from typing import Any, Optional

from langchain_core.tools import tool

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .data import SAMPLE_ATTRACTIONS, SAMPLE_LISTINGS

SYSTEM_MESSAGE = (
    "You are a professional travel consultant AI that produces extremely detailed itineraries in a single response.\n"
    "Always act without asking the user follow-up questions.\n"
    "You must combine MCP tool data (Airbnb + Google Maps) with your own reasoning to craft complete travel plans.\n"
    "Use Google Maps results for distances, travel times, and navigation hints; use Airbnb data for real accommodation context.\n"
    "Keep the tone clear, structured, and friendly while covering every required section."
)


@dataclass
class AgentSettings:
    openai_api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = 0.3
    google_maps_api_key: str | None = None


def _extract_text(result: Any) -> Optional[str]:
    messages = result.get("messages") if isinstance(result, dict) else None
    if not messages:
        return None

    content = messages[-1].content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(str(part.get("text", part)) for part in content)
    return str(content)


def _build_fallback_tools() -> list[Any]:
    """Return simple LangChain tools when MCP is unavailable."""

    @tool
    def fetch_sample_listings(destination: str) -> str:
        """Return sample accommodation JSON for lessons."""
        key = destination.lower()
        listings = SAMPLE_LISTINGS.get(key)
        if not listings:
            listings = [
                {"name": "Sample Downtown Stay", "price": 160, "address": "Central Ave 1", "distance_city_center_km": 1.0},
                {"name": "Neighborhood Loft", "price": 120, "address": "Maple Street 5", "distance_city_center_km": 3.2},
            ]
        return json.dumps({"destination": destination, "listings": listings}, indent=2)

    @tool
    def fetch_sample_highlights(destination: str) -> str:
        """Return sample attraction JSON when MCP data is unavailable."""
        key = destination.lower()
        highlights = SAMPLE_ATTRACTIONS.get(key)
        if not highlights:
            highlights = [
                {"name": "City Welcome Center", "neighborhood": "Historic core", "open": "09:00-17:00", "tip": "Pick up a transit card and walking map."}
            ]
        return json.dumps({"destination": destination, "highlights": highlights}, indent=2)

    return [fetch_sample_listings, fetch_sample_highlights]


def _server_parameters(google_maps_key: Optional[str]) -> list[StdioServerParameters]:
    servers = [
        StdioServerParameters(
            command="npx",
            args=["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
        ),
    ]

    if google_maps_key:
        servers.append(
            StdioServerParameters(
                command="npx",
                args=["@gongrzhe/server-travelplanner-mcp"],
                env={"GOOGLE_MAPS_API_KEY": google_maps_key},
            )
        )
    return servers


@asynccontextmanager
async def travel_mcp_tools(google_maps_key: Optional[str]):
    """Yield MCP-backed LangChain tools for all configured servers."""

    server_params = _server_parameters(google_maps_key)
    stack = AsyncExitStack()
    try:
        combined_tools: list[Any] = []
        for params in server_params:
            client_ctx = await stack.enter_async_context(stdio_client(params))
            read, write = client_ctx
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            tools = await load_mcp_tools(session)
            combined_tools.extend(tools)

        if not combined_tools:
            raise RuntimeError("No MCP tools available.")

        yield combined_tools
    finally:
        await stack.aclose()


async def _invoke_with_tools(llm: ChatOpenAI, tools: list[Any], prompt: str, callbacks: Optional[list[Any]] = None) -> Optional[str]:
    config = {"callbacks": callbacks} if callbacks else None
    agent = create_react_agent(llm, tools, prompt=SYSTEM_MESSAGE)
    try:
        if config:
            result = await agent.ainvoke({"messages": [("user", prompt)]}, config=config)
        else:
            result = await agent.ainvoke({"messages": [("user", prompt)]})
    except Exception as exc:  # pragma: no cover - surface errors but keep API alive
        print(f"[Agent] Invocation failed: {exc}")
        return None

    return _extract_text(result)


@dataclass
class AgentRuntime:
    settings: AgentSettings

    async def plan(self, prompt: str, callbacks: Optional[list[Any]] = None) -> Optional[str]:
        if not self.settings.openai_api_key:
            print("[Agent] OPENAI_API_KEY missing; cannot contact OpenAI.")
            return None

        try:
            llm = ChatOpenAI(
                model=self.settings.model,
                temperature=self.settings.temperature,
                api_key=self.settings.openai_api_key,
            )
        except Exception as exc:  # pragma: no cover
            print(f"[Agent] Could not initialize OpenAI client: {exc}")
            return None

        try:
            async with travel_mcp_tools(self.settings.google_maps_api_key) as tools:
                if tools:
                    response = await _invoke_with_tools(llm, tools, prompt, callbacks)
                    if response:
                        return response
        except Exception as exc:  # pragma: no cover - fallback to offline tools
            print(f"[Agent] MCP tools unavailable, using fallback set. Error: {exc}")

        fallback_tools = _build_fallback_tools()
        return await _invoke_with_tools(llm, fallback_tools, prompt, callbacks)


def build_agent(settings: AgentSettings) -> AgentRuntime:
    if not settings.openai_api_key:
        print("[Agent] Warning: OPENAI_API_KEY not configured. Agent will fall back to offline tips.")
    return AgentRuntime(settings=settings)


def build_trip_prompt(payload: dict[str, Any]) -> str:
    """Format the user payload into a single user message similar to the original demo prompt."""
    destination = payload.get("destination")
    num_days = payload.get("num_days")
    budget = payload.get("budget")
    preferences = payload.get("preferences")
    start_date = payload.get("start_date")

    if isinstance(start_date, (datetime, date)):
        start_date_text = start_date.isoformat()
    elif start_date is None:
        start_date_text = "Not provided"
    else:
        start_date_text = str(start_date)

    return (
        f"IMMEDIATELY create an extremely detailed and comprehensive travel itinerary:\n\n"
        f"- Destination: {destination}\n"
        f"- Duration: {num_days} days\n"
        f"- Budget: ${budget} USD total\n"
        f"- Start date: {start_date_text}\n"
        f"- Preferences: {preferences}\n\n"
        "Do not ask questions—generate a complete itinerary now using all available MCP tools.\n"
        "Critical requirements:\n"
        "1. Use Google Maps MCP to calculate distances and travel times between EVERY location.\n"
        "2. Include specific addresses for each activity, restaurant, and attraction.\n"
        "3. Provide start/end times with buffer periods for travel and rest.\n"
        "4. Estimate transportation costs between locations and note ticket prices/opening hours.\n"
        "5. Suggest three Airbnb listings with prices, addresses, amenities, and distance from city center.\n"
        "6. Summarize weather insights, packing tips, cultural norms, safety advice, and communication options.\n"
        "7. Structure the answer with the sections below and keep the tone energetic but professional.\n\n"
        "Required output format:\n"
        "1. Trip Overview – summary, detailed weather forecast, and cost breakdown.\n"
        "2. Accommodation – three Airbnb options (name, price, address, distance to center, key amenities).\n"
        "3. Transportation Overview – recommended modes, passes, and cost estimates.\n"
        "4. Day-by-Day Itinerary – for each day include timed schedule, addresses, distances, travel times, "
        "opening hours, ticket prices, and buffer guidance.\n"
        "5. Dining Plan – restaurants with cuisine, price range, address, and proximity to lodging.\n"
        "6. Practical Information – currency tips, safety advice, emergency contacts, connectivity options, "
        "health notes, and shopping ideas.\n"
        "7. Optional Add-ons – extra experiences or day trips if time remains.\n"
        "Use MCP tool outputs directly and cite when you use Airbnb or Google Maps data."
    )
