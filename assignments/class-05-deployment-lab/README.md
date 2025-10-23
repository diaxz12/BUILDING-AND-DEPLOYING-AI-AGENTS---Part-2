# Class 5 Mini Assignment — Tavily-Powered Agent

## Overview

Ship a lightweight agent that answers "How do I…?" questions about FastAPI and Streamlit by combining the Class 5 FastAPI backend, the Streamlit UI, [Tavily web search](https://www.tavily.com/), and Langfuse tracing. You will host the reasoning agent inside the FastAPI on Render, call it from the Streamlit client, and keep the deployment steps simple enough to reuse in later assignments.

## Learning Goals

- Deploy a LangGraph agent behind a FastAPI `/chat` endpoint and surface it in the Streamlit chat UI.
- Extend the agent with Tavily-powered search so answers stay current for FastAPI/Streamlit questions.
- Capture every conversation in Langfuse to monitor tool usage, latency, and fallback behaviour.
- Practice the deploy-ready habits used in the demo (virtualenvs, `.env` management, targeted requirements files).

## Prerequisites

- Local clone of this repository and the Class 5 demos under `classes/class-05-deployment-interfaces/demos/`.
- Python 3.10+ with `uvicorn`, `fastapi`, `langgraph`, `langchain`, `streamlit`, and `langfuse` installed (reuse the provided `requirements.txt`).
- API keys:
  - `OPENAI_API_KEY` for LangGraph (use `gpt-4o-mini`).
  - `TAVILY_API_KEY` for web search (`pip install tavily-python`).
  - Optional `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST`.

## Assignment Tasks

1. **Set up the FastAPI service.**
   - From `classes/class-05-deployment-interfaces/demos/fastapi-agent-service`, create/activate `.venv` and install requirements.
   - Add `tavily-python` to `requirements.txt` alongside any LangChain and LangGraph integrations you need.
2. **Add the Tavily search tool.**
   - In `main.py`, register a new LangChain tool inside `build_tools()` that wraps the Tavily client.
   - Blend Tavily snippets with a concise answer so the agent explains which sources it used.
3. **Prime the agent for the class 5 context.**
   - Update the system prompt or initial tool descriptions so the LangGraph agent emphasises deployment steps, environment setup, and debugging tips for the Class 5 demos.
   - Ensure responses mention both FastAPI API guidance and Streamlit UI pointers when relevant.
4. **Expose locally the API with monitoring enabled.**
   - Keep the `/chat` route contract intact.
   - The tavily tool calls should be visible in Langfuse.
5. **Update the Streamlit UI.**
   - Point the UI (`classes/class-05-deployment-interfaces/demos/streamlit-chat-ui/app.py`) to your API.
6. **Deploy the API + UI.**
   - Follow the class 5 demo `README.md` to push the FastAPI service to Render and host the Streamlit interface on the Streamlit Cloud Community. Double-check environment variables in both platforms.
7. **Document your work.**
   - Create a `README.md` describing the setup, key code changes, and any caveats.
   - Record 2–3 example questions with the corresponding responses (include at least one using Tavily results).

## Deliverables

- Share the source code of the assignment.
- `README.md` with sample Q&A transcript(s).
- Share the Streamlit UI URL with the working AI Agent.
- **Optional**: quick video showcasing that Tavily, LangGraph, and Langfuse all ran during testing.