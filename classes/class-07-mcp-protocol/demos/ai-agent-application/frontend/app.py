"""Streamlit UI for the travel planner demo."""

from __future__ import annotations

import os
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import requests
import streamlit as st
from icalendar import Calendar, Event
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")
load_dotenv()


def generate_ics_content(plan_text: str, start_date: datetime) -> bytes:
    """Convert itinerary text into a simple calendar (.ics) file."""

    cal = Calendar()
    cal.add("prodid", "-//AI Travel Planner//class-demo//")
    cal.add("version", "2.0")

    day = 0
    for block in plan_text.split("\n\n"):
        header = block.strip().lower()
        if header.startswith("day"):
            day += 1
        if not block.strip():
            continue

        event = Event()
        event.add("summary", f"Travel Day {max(day, 1)}")
        event.add("description", block.strip())
        event_date = (start_date + timedelta(days=max(day - 1, 0))).date()
        event.add("dtstart", event_date)
        event.add("dtend", event_date)
        event.add("dtstamp", datetime.now())
        cal.add_component(event)

    return cal.to_ical()


STREAMLIT_USERNAME = os.getenv("STREAMLIT_UI_USERNAME", "student")
STREAMLIT_PASSWORD = os.getenv("STREAMLIT_UI_PASSWORD", "streamlit-demo")
DEFAULT_API_BASE = os.getenv("AGENT_API_BASE", "http://localhost:8000")

st.set_page_config(page_title="MCP Travel Planner", page_icon="✈️", layout="wide")


def init_state() -> None:
    defaults = {
        "messages": [],
        "session_id": str(uuid.uuid4()),
        "api_base": DEFAULT_API_BASE,
        "authenticated": False,
        "username": "",
        "api_token": None,
        "itinerary": None,
        "guardrails_note": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def authenticate_api(username: str, password: str) -> bool:
    url = f"{st.session_state.api_base}/login"
    try:
        response = requests.post(url, json={"username": username, "password": password}, timeout=10)
        response.raise_for_status()
        token = response.json().get("token")
        if not token:
            st.warning("Login succeeded but the API did not respond with a token.")
            st.session_state.api_token = None
            return False
        st.session_state.api_token = token
        return True
    except Exception as exc:
        st.error(f"Could not authenticate with FastAPI ({exc}).")
        st.session_state.api_token = None
        return False


def require_login() -> None:
    if st.session_state.authenticated:
        return

    st.title("Travel Planner Login")
    st.caption("Use the classroom credentials to unlock the planner API.")

    with st.form("login-form", clear_on_submit=False):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if username_input == STREAMLIT_USERNAME and password_input == STREAMLIT_PASSWORD:
            st.session_state.username = username_input
            st.session_state.session_id = str(uuid.uuid4())
            if authenticate_api(username_input, password_input):
                st.success("Login successful. Loading planner UI…")
            else:
                st.info("Logged in locally. Requests will fall back to offline tips.")
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password.")

    st.stop()


def call_backend(payload: dict) -> Optional[dict]:
    url = f"{st.session_state.api_base}/plan"
    headers = {}
    if st.session_state.api_token:
        headers["x_auth_token"] = st.session_state.api_token

    try:
        response = requests.post(url, json=payload, headers=headers or None, timeout=120)
        if response.status_code == 401:
            st.warning("Session expired. Please log in again.")
            st.session_state.authenticated = False
            st.session_state.api_token = None
            st.session_state.itinerary = None
            st.experimental_rerun()
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        st.error(f"Backend request failed: {exc}")
        return None


def render_sidebar() -> None:
    with st.sidebar:
        st.header("Account")
        st.caption(f"Signed in as {st.session_state.username}")
        if st.button("Log out"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.api_token = None
            st.session_state.itinerary = None
            st.session_state.guardrails_note = None
            st.experimental_rerun()

        st.header("Backend")
        st.session_state.api_base = st.text_input(
            "FastAPI base URL",
            value=st.session_state.api_base,
            help="Run `uvicorn backend.main:app --reload` locally.",
        )
        if st.button("Reset session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.itinerary = None
            st.info("Session reset. Ready for a new trip.")


def render_planner_ui():
    st.title("✈️ MCP Travel Planner")
    st.caption("Plan classroom trips with LangGraph, Guardrails, MCP stubs, and Langfuse monitoring.")

    col1, col2 = st.columns(2)
    with col1:
        destination = st.text_input("Destination", placeholder="e.g., Paris, Tokyo, New York")
        num_days = st.number_input("Number of days", min_value=1, max_value=21, value=5)
    with col2:
        budget = st.number_input("Budget (USD)", min_value=100, max_value=20000, value=1500, step=100)
        start_date = st.date_input("Trip start date", min_value=date.today(), value=date.today())

    preferences = st.text_area(
        "Travel style and must-dos",
        placeholder="Tell the agent what kind of trip you want (food, museums, outdoors, etc.).",
        height=120,
    )

    if st.button("Generate itinerary", type="primary"):
        if not destination:
            st.error("Please choose a destination before planning.")
            return

        payload = {
            "destination": destination,
            "num_days": int(num_days),
            "budget": int(budget),
            "preferences": preferences or "General sightseeing",
            "session_id": st.session_state.session_id,
            "start_date": start_date.isoformat(),
        }

        with st.spinner("Planning your adventure..."):
            data = call_backend(payload)

        if data:
            st.session_state.itinerary = data.get("itinerary")
            st.session_state.guardrails_note = data.get("guardrails_note")
            st.session_state.session_id = data.get("session_id", st.session_state.session_id)

    if st.session_state.itinerary:
        st.subheader("📋 Itinerary")
        st.markdown(st.session_state.itinerary)

        if st.session_state.guardrails_note:
            st.info(st.session_state.guardrails_note)

        ics_bytes = generate_ics_content(
            st.session_state.itinerary,
            datetime.combine(start_date, datetime.min.time()),
        )
        st.download_button(
            "📅 Download as .ics",
            data=ics_bytes,
            file_name="travel_itinerary.ics",
            mime="text/calendar",
        )


def main() -> None:
    init_state()
    require_login()
    render_sidebar()
    render_planner_ui()


if __name__ == "__main__":
    main()
