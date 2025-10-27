# Building & Deploying AI Agents Applications

This repository is the shared workspace for the course on building, evaluating, and deploying agentic applications. Every session drops code samples, lecture notes, and assignments here so you always know where to look next.

## Student Prerequisites
- **GitHub account** – all demos assume you can clone this repository, push your own forks, and connect GitHub repos when deploying to Render or Streamlit Cloud.
- **Render account (free tier is fine)** – used to host the FastAPI agent and as deployment lab that expects you to provision a web service and manage environment variables there.
- **Streamlit Community Cloud account** – required to publish the chat UI and later variations straight from GitHub.
- **Model provider access** – an `OPENAI_API_KEY` is the default for the LangGraph agents. The key will be provided to the students.
- **Tavily account** – assignments add a Tavily-powered search tool, so keep a `TAVILY_API_KEY` handy.
- **Langfuse workspace** – monitoring labs trace every run. Grab `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and optionally `LANGFUSE_HOST`.
- **Local tooling** – Python 3.10+, `pip`, and Git installed on your laptop, plus the ability to create per-demo virtual environments (`python3 -m venv .venv`).

## Quick Start
1. Install Python 3.10+, the latest `pip`, and Git (`python3 --version`, `python3 -m pip install --upgrade pip`, `git --version`).
2. Clone the repository and pull updates before each class.
3. Inside any demo folder, create a virtual environment (`python3 -m venv .venv && source .venv/bin/activate`) and install the local `requirements.txt`.
4. Run demos with the provided commands (example):
   - `uvicorn classes.class-05-deployment-interfaces.demos.fastapi-agent-service.main:app --reload`
   - `python classes/class-05-deployment-interfaces/demos/fastapi-agent-service/demo_client.py "Status check"`
   - `streamlit run classes/class-05-deployment-interfaces/demos/streamlit-chat-ui/app.py`
5. Store API keys (for example `OPENAI_API_KEY`, `TAVILY_API_KEY`, `LANGFUSE_*`) in local `.env` files and mirror them in Streamlit or Render secret managers when deploying.

## Repository Layout
- `classes/` — session-by-session lecture decks, demos, and reference notes.
  - `class-05-deployment-interfaces/` — FastAPI agent service, Streamlit chat UI, and deployment checklists.
  - `class-06-guardrails-ethics/` — guardrailed versus unguarded agents plus safety playgrounds.
- `assignments/` — lab prompts and submission templates aligned to each class.
- `resources/` — curated quickstarts for FastAPI, Streamlit, Guardrails AI, and Langfuse.

## Sessions at a Glance
### Class 5 — Deployment & Interfaces
Build a FastAPI endpoint backed by a LangGraph agent, pair it with the Streamlit chat UI, and practice shipping to Render and Streamlit Community Cloud. All code lives under `classes/class-05-deployment-interfaces/`.

### Class 6 — Guardrails, Ethics & Responsible AI
Add Guardrails AI protections, safety prompts, and validation datasets to the Class 5 agent. Compare "no guardrails" and "guardrails on" demos in `classes/class-06-guardrails-ethics/`.

## Assignments
- `assignments/class-05-deployment-lab/` — ship a Tavily-powered agent with FastAPI, Streamlit, and Langfuse tracing.

- `assignments/class-06-guardrails-lab/` — layer safety checks onto the Class 5 agent and document your guardrail strategy.

Each assignment folder includes its own README with deliverables, prerequisites, and upload expectations.

## Resource Library
- `resources/fastapi/` — API quickstarts and deployment tips for FastAPI.
- `resources/guardrails-ai/` — starter configs and safety playbooks for Guardrails AI.
- `resources/langfuse/` — tracing tutorials and dashboards for monitoring agent behaviour.
- `resources/streamlit/` — Streamlit Cloud setup, component patterns, and UI guides.

---

## ⚠️ Intellectual Property Notice

**Important**: This course material is the intellectual property of the course instructors and should not be distributed, shared, or reproduced without their explicit written consent. All content, exercises, and materials are protected by copyright and are intended solely for enrolled students of this course.
