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


def inject_custom_css() -> None:
    """Inject a light design system so the app feels modern and responsive."""

    st.markdown(
        """
        <style>
            :root {
                --bg-gradient: linear-gradient(135deg, #1c1b29 0%, #152238 50%, #102a43 100%);
                --card-bg: #111827;
                --muted: #94a3b8;
                --primary: #f87171;
                --border: rgba(148, 163, 184, 0.2);
            }
            .main,
            .block-container {
                padding-top: 1.25rem;
                max-width: 1100px;
            }
            body {
                background: #0b1220;
            }
            .stSidebar {
                background: #111827;
            }
            .hero-card {
                position: relative;
                overflow: hidden;
                background: var(--bg-gradient);
                color: #fff;
                border-radius: 24px;
                padding: 2.5rem 2.75rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 42px 80px rgba(15, 23, 42, 0.55);
            }
            .hero-card:after {
                content: "";
                position: absolute;
                inset: -40%;
                background: radial-gradient(circle at 30% 30%, rgba(248,113,113,0.55), transparent 40%),
                            radial-gradient(circle at 70% 20%, rgba(59,130,246,0.45), transparent 30%);
                animation: drift 14s linear infinite;
                z-index: 1;
            }
            .hero-card > * {
                position: relative;
                z-index: 2;
            }
            @keyframes drift {
                0% { transform: rotate(0deg) scale(1);}
                50% { transform: rotate(5deg) scale(1.05);}
                100% { transform: rotate(0deg) scale(1);}
            }
            .hero-card h1 {
                margin-bottom: 0.5rem;
                font-size: clamp(2rem, 3.5vw, 3.25rem);
            }
            .login-hero {
                padding: 2.5rem;
                border-radius: 24px;
                color: #fff;
                background: radial-gradient(circle at 15% 20%, rgba(248,113,113,0.35), transparent 40%),
                            radial-gradient(circle at 80% 0%, rgba(59,130,246,0.35), transparent 45%),
                            var(--bg-gradient);
                box-shadow: 0 35px 70px rgba(15, 23, 42, 0.6);
            }
            .login-hero h1 {
                margin-bottom: 0.8rem;
                font-size: clamp(2.4rem, 4vw, 3.3rem);
            }
            .login-badge {
                display: inline-flex;
                gap: 0.35rem;
                align-items: center;
                border-radius: 999px;
                padding: 0.35rem 0.8rem;
                background: rgba(15,23,42,0.45);
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.12em;
            }
            .login-checklist {
                list-style: none;
                margin: 1.3rem 0 0;
                padding: 0;
                display: grid;
                gap: 0.65rem;
            }
            .login-checklist li {
                display: flex;
                gap: 0.6rem;
                align-items: flex-start;
                color: rgba(255,255,255,0.88);
            }
            .login-checklist li span {
                font-size: 1.1rem;
            }
            .hero-eyebrow {
                text-transform: uppercase;
                letter-spacing: 0.25em;
                font-size: 0.72rem;
                color: rgba(255,255,255,0.82);
                margin-bottom: 0.65rem;
            }
            .hero-pill {
                display: inline-flex;
                align-items: center;
                gap: 0.6rem;
                padding: 0.55rem 1.1rem;
                border-radius: 999px;
                background: rgba(15,23,42,0.45);
                border: 1px solid rgba(255,255,255,0.25);
                font-size: 0.9rem;
                margin-top: 0.75rem;
                box-shadow: inset 0 0 10px rgba(255,255,255,0.1);
            }
            .feature-card {
                background: rgba(15, 23, 42, 0.75);
                border-radius: 18px;
                padding: 1rem;
                border: 1px solid var(--border);
                box-shadow: 0 25px 40px rgba(15, 23, 42, 0.35);
                min-height: 140px;
            }
            .feature-card h3 {
                margin-bottom: 0.4rem;
                font-size: 1rem;
            }
            .feature-icon {
                font-size: 1.5rem;
            }
            .trip-card {
                background: rgba(17, 24, 39, 0.95);
                border-radius: 22px;
                padding: 1.5rem;
                border: 1px solid var(--border);
                box-shadow: 0 35px 70px rgba(15, 23, 42, 0.5);
            }
            .stat-card {
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 18px;
                padding: 1rem 1.2rem;
                background: rgba(15, 23, 42, 0.65);
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02);
            }
            .stat-card span {
                color: var(--muted);
                font-size: 0.8rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
            }
            .stat-card h3 {
                margin: 0.35rem 0 0;
                font-size: 1.4rem;
                color: #f8fafc;
            }
            .login-footnote {
                color: rgba(148,163,184,0.85);
                font-size: 0.9rem;
                margin-top: 1.5rem;
            }
            .login-form-tip {
                font-size: 0.85rem;
                color: rgba(148,163,184,0.9);
                margin-bottom: 1rem;
            }
            .stTabs [data-baseweb="tab-list"] button {
                padding: 0.6rem 1.2rem;
                border-radius: 999px;
            }
            .stTabs [data-baseweb="tab-highlight"] {
                background: rgba(248,113,113,0.2);
            }
            .stTextInput>div>div>input,
            .stNumberInput input,
            .stDateInput input,
            textarea {
                border-radius: 12px !important;
                border: 1px solid rgba(148,163,184,0.35) !important;
                background: rgba(15,23,42,0.65) !important;
                color: #f1f5f9 !important;
            }
            .stTextInput>div>div>input:focus,
            .stNumberInput input:focus,
            .stDateInput input:focus,
            textarea:focus {
                border-color: #f87171 !important;
                box-shadow: 0 0 0 1px rgba(248,113,113,0.6) !important;
            }
            .stButton button {
                border-radius: 14px !important;
                font-weight: 600;
                letter-spacing: 0.02em;
            }
            .stExpander {
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 18px !important;
                background: rgba(15, 23, 42, 0.7);
            }
            .stExpander div[role="button"] p {
                font-weight: 600;
            }
            @media (max-width: 768px) {
                .hero-card {
                    padding: 1.7rem;
                }
                .trip-card {
                    padding: 1.2rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_preferences_text(
    base_preferences: str,
    vibe: str,
    pacing: str,
    highlights: list[str],
) -> str:
    """Blend advanced inputs into a single preference string for the backend."""

    notes: list[str] = []
    if vibe != "No preference":
        notes.append(f"Overall vibe: {vibe.lower()}")
    if pacing != "Balanced":
        notes.append(f"Daily pacing should feel {pacing.lower()}")
    if highlights:
        notes.append("Key highlights: " + ", ".join(highlights))

    combined = base_preferences.strip()
    if notes:
        notes_text = " | ".join(notes)
        combined = f"{combined}\n\nPlanner notes: {notes_text}" if combined else f"Planner notes: {notes_text}"

    return combined or "General sightseeing"


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
        "latest_trip": None,
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

    st.markdown(
        """
        <style>
            .login-card-marker + div[data-testid="stForm"] {
                background: rgba(17, 24, 39, 0.95);
                border-radius: 24px;
                padding: 2rem 1.75rem;
                border: 1px solid rgba(148, 163, 184, 0.25);
                box-shadow: 0 35px 80px rgba(15, 23, 42, 0.55);
            }
            .login-card-marker + div[data-testid="stForm"] label {
                font-weight: 500;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    hero_col, form_col = st.columns((1.35, 1))

    with hero_col:
        st.markdown(
            """
            <div class="login-hero">
                <div class="login-badge">Class demo</div>
                <h1>Travel Agent</h1>
                <p style="font-size:1.05rem; color:rgba(255,255,255,0.9);">
                    Sign in with the shared credentials to connect the Streamlit UI with the FastAPI backend,
                    LangGraph agent, and guardrails policies.
                </p>
                <ul class="login-checklist">
                    <li><span>✅</span>One login powers Streamlit + FastAPI tokens</li>
                    <li><span>🛡</span>Guardrails enforce safe classroom itineraries</li>
                    <li><span>🚀</span>Session IDs refresh on every login for easier demos</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with form_col:
        st.markdown('<div class="login-card-marker"></div>', unsafe_allow_html=True)
        with st.form("login-form", clear_on_submit=False):
            st.markdown("#### Classroom credentials")
            st.caption("Use the standard username/password from the instructor slide.")
            username_input = st.text_input("Username")
            password_input = st.text_input("Password", type="password")
            st.markdown(
                '<div class="login-form-tip">Tip: the FastAPI token request happens right after you sign in.</div>',
                unsafe_allow_html=True,
            )
            submitted = st.form_submit_button("Sign in", use_container_width=True)

        st.caption("Need help? Ask the instructor for the classroom credentials.")
    st.markdown(
        '<p class="login-footnote">Your credentials stay local—no keys or tokens are stored in the repo.</p>',
        unsafe_allow_html=True,
    )

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
            st.session_state.latest_trip = None
            st.rerun()
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        st.error(f"Backend request failed: {exc}")
        return None


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("#### Account")
        st.caption(f"Signed in as **{st.session_state.username or '—'}**")
        if st.button("Log out"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.api_token = None
            st.session_state.itinerary = None
            st.session_state.guardrails_note = None
            st.session_state.latest_trip = None
            st.rerun()

        st.markdown("#### Backend")
        st.session_state.api_base = st.text_input(
            "FastAPI base URL",
            value=st.session_state.api_base,
            help="Run `uvicorn backend.main:app --reload` locally.",
        )
        if st.button("Reset session"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.itinerary = None
            st.session_state.latest_trip = None
            st.info("Session reset. Ready for a new trip.")


def render_planner_ui():
    st.markdown(
        """
        <div class="hero-card">
            <h1>Plan immersive travel adventures in minutes</h1>
            <p style="margin-bottom:0.6rem;">
                Blend curated itineraries, budget insights, and safety guardrails in a single modern workspace.
            </p>
            <div class="hero-pill">
                ✨ Fresh ideas, structured days, export-ready calendars
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown("#### Trip brief")
        with st.form("planner-form", clear_on_submit=False):
            essentials_tab, advanced_tab = st.tabs(["Essentials", "Advanced"])

            with essentials_tab:
                col1, col2 = st.columns((1.5, 1))
                with col1:
                    destination = st.text_input(
                        "Destination",
                        placeholder="e.g., Paris, Tokyo, New York",
                    )
                    start_date = st.date_input("Trip start date", min_value=date.today(), value=date.today())
                with col2:
                    num_days = st.number_input("Number of days", min_value=1, max_value=21, value=5)
                    budget = st.number_input(
                        "Budget (USD)",
                        min_value=100,
                        max_value=20000,
                        value=1500,
                        step=100,
                    )

            with advanced_tab:
                base_preferences = st.text_area(
                    "Travel style and must-dos",
                    placeholder="Tell the agent what kind of trip you want (food, museums, outdoors, etc.).",
                    height=150,
                )
                vibe = st.selectbox(
                    "Trip vibe",
                    ["No preference", "Foodie tour", "Art & culture", "Nature escape", "Tech & innovation"],
                    index=0,
                )
                pacing = st.selectbox("Daily pacing", ["Balanced", "Leisurely", "Fast-paced"], index=0)
                highlights = st.multiselect(
                    "Focus areas",
                    ["Local food", "Hidden gems", "Museums", "Nightlife", "Family-friendly"],
                    default=[],
                )

            preferences = build_preferences_text(base_preferences, vibe, pacing, highlights)

            submitted = st.form_submit_button(
                "Generate itinerary",
                type="primary",
                use_container_width=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not destination:
                st.error("Please choose a destination before planning.")
                return

            payload = {
                "destination": destination,
                "num_days": int(num_days),
                "budget": int(budget),
                "preferences": preferences,
                "session_id": st.session_state.session_id,
                "start_date": start_date.isoformat(),
            }

            with st.spinner("Planning your adventure..."):
                data = call_backend(payload)

            if data:
                st.session_state.itinerary = data.get("itinerary")
                st.session_state.guardrails_note = data.get("guardrails_note")
                st.session_state.session_id = data.get("session_id", st.session_state.session_id)
                st.session_state.latest_trip = {
                    "destination": destination,
                    "num_days": int(num_days),
                    "budget": int(budget),
                    "start_date": start_date.isoformat(),
                }

    if st.session_state.itinerary:
        trip_meta = st.session_state.get("latest_trip")
        if trip_meta:
            meta_cols = st.columns(3)
            meta_cols[0].markdown(
                f"""<div class="stat-card"><span>Destination</span><h3>{trip_meta["destination"]}</h3></div>""",
                unsafe_allow_html=True,
            )
            meta_cols[1].markdown(
                f"""<div class="stat-card"><span>Trip length</span><h3>{trip_meta["num_days"]} days</h3></div>""",
                unsafe_allow_html=True,
            )
            meta_cols[2].markdown(
                f"""<div class="stat-card"><span>Budget</span><h3>${trip_meta["budget"]:,.0f}</h3></div>""",
                unsafe_allow_html=True,
            )

        st.subheader("📋 Itinerary")
        st.markdown(
            """
            <div style="
                background: rgba(15, 23, 42, 0.85);
                border-radius: 20px;
                padding: 1.5rem;
                border: 1px solid rgba(148, 163, 184, 0.2);
                box-shadow: 0 35px 80px rgba(15, 23, 42, 0.45);
            ">
            """,
            unsafe_allow_html=True,
        )
        st.markdown(st.session_state.itinerary)
        st.markdown("</div>", unsafe_allow_html=True)

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
            use_container_width=True,
        )


def main() -> None:
    init_state()
    inject_custom_css()
    require_login()
    render_sidebar()
    render_planner_ui()


if __name__ == "__main__":
    main()
