# FastAPI Agent Service

A small API that powers the Streamlit demo. The entire project fits in this folder so you can see how UI, API, and monitoring connect. The `/chat` endpoint now uses a LangGraph ReAct agent with two simple tools so you can show students how agents access helper functions.

## What you need first

- Python 3.10 or newer installed on your machine.
- The course repository already cloned (you should be inside `classes/class-05-deployment-interfaces/demos/fastapi-agent-service`).
- An internet connection when installing packages.
- Credentials for the demo stored in your environment (set `AGENT_API_USERNAME` and `AGENT_API_PASSWORD` in `.env`).

## Step-by-step: run the API locally

1. **Create a virtual environment** (keeps packages isolated).
   - macOS / Linux:
     ```bash
     python3 -m venv .venv
     ```
   - Windows (PowerShell):
     ```powershell
     py -3 -m venv .venv
     ```

2. **Activate the environment** so `pip` installs into `.venv`.
   - macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
   After activation your prompt should show `(.venv)` at the start.

3. **Install the Python packages** listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```
   This pulls in FastAPI plus the LangGraph + LangChain libraries used by the agent.

4. **Create your `.env` file** (stores API keys and login credentials):
   ```bash
   cp .env.example .env  # on Windows use: copy .env.example .env
   ```
   Open `.env` in any editor and set at least `AGENT_API_USERNAME` and `AGENT_API_PASSWORD`. Add OpenAI or Langfuse keys later if you want those integrations and replace the sample Langfuse secret with your actual value.
   > Tip: reuse the same username/password in the Streamlit UI `.env` so the front-end can log in to this API automatically.

5. **Start the FastAPI server** with auto-reload for development:
   ```bash
   uvicorn main:app --reload
   ```
   (From the repo root you can use `uvicorn classes.class-05-deployment-interfaces.demos.fastapi-agent-service.main:app --reload`.)
   You should see a message similar to `Uvicorn running on http://127.0.0.1:8000`.

6. **Try the built-in docs** in your browser: http://127.0.0.1:8000/docs.
   - Authenticate first: expand `/login`, choose “Try it out”, and submit your username/password from `.env`.
   - Copy the returned `token` and pass it as the `x_auth_token` header when you call `/chat` (many clients show it as `X-Auth-Token`).
   - The chat response shows the agent’s reply plus flags for `source` and `monitored`.

7. **Send a CLI test request** (optional but useful for debugging):
   ```bash
   export AGENT_API_USERNAME=your-username
   export AGENT_API_PASSWORD=your-password
   python demo_client.py "What does Langfuse help with?"
   ```
   Example output:
   ```
   Reply: Langfuse links inputs and outputs. Set the keys to see traces pop up in the dashboard.
   Source: rule-based • Langfuse trace: False • Session: 123e4567-e89b-12d3-a456-426614174000
   Token used: token-1c2b3b1a-...-your-username
   ```

8. **Stop the server** by pressing `CTRL+C` in the terminal when you are done.

## How the agent works

- When an OpenAI key is available, the app builds a LangGraph ReAct agent (`langgraph.prebuilt.create_react_agent`).
- Two tools are registered:
  1. `streamlit_playbook` – returns quick tips about Streamlit features.
  2. `deployment_checklist` – outlines steps for deploying APIs and adding monitoring.
- The agent decides when to call a tool. If it cannot run (missing key or dependency) the API falls back to the rule-based helper sentences so nobody is blocked.
- The response `source` field will show `langgraph:<model>` when the agent is used, and `rule-based` otherwise.

## Enable OpenAI-powered agent replies

1. Open `.env` and fill in `OPENAI_API_KEY` and (optionally) `OPENAI_MODEL`.
2. Restart `uvicorn`. Ask the agent something that should trigger a tool, e.g. “Give me a checklist for deploying FastAPI”.
3. Watch the terminal: you will see log lines for the tool calls as the agent reasons and interacts.

## Enable Langfuse monitoring

1. Add `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and (optionally) `LANGFUSE_HOST`/`LANGFUSE_TRACING_ENVIRONMENT` to `.env`.
2. Restart `uvicorn` and make another `/chat` request.
3. Go to the Langfuse dashboard and confirm a trace named `fastapi.chat` appears. The trace captures the user message, final reply, and whether the agent called a tool.

## Deploying the API to Render (free tier)

1. Create a new GitHub repository with the following files: `main.py`, `requirements.txt`, `demo_client.py` and `.env.example`.
2. Go to https://render.com/ and create an account (or sign in).
3. Click **New +** → **Web Service**, then connect your GitHub repository.
4. Choose the repository and branch, and set these build details:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Scroll to **Environment Variables** and add any keys (`AGENT_API_USERNAME`, `AGENT_API_PASSWORD`, `OPENAI_API_KEY`, `LANGFUSE_PUBLIC_KEY`, etc.).
6. Click **Create Web Service**. Render will install dependencies, then start the server. The dashboard shows a public URL such as `https://class5-agent.onrender.com`.
7. Visit `<public-url>/docs` to confirm the API is live. Re-point your Streamlit UI to the new URL and run through a full chat.
8. Each time you push changes to GitHub, Render redeploys automatically. Use the Render logs to debug build or runtime issues.

**Reminder:** keep `.env` out of version control. Only `.env.example` should be committed so students know which keys exist.
