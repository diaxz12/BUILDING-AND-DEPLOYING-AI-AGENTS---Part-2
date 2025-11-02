# MCP Travel Planner Demo

Classroom demo that connects the dots from class 05 (FastAPI deployment + Langfuse), class 06 (Guardrails AI), and class 07 (MCP servers) into one approachable project. The repository now splits the Streamlit UI and LangGraph-powered backend so students can focus on each layer separately while still seeing how the pieces fit together.

## Project Layout
- `frontend/app.py` – Streamlit chat UI that authenticates with the backend, calls `/plan`, renders the itinerary, and exports `.ics` calendar files.
- `backend/main.py` – FastAPI service with login, token checks, guardrails, Langfuse tracing, and a LangGraph agent.
- `backend/agent.py` – Builds the LangGraph runtime, connects to the Airbnb and Google Maps MCP servers, and falls back to classroom tools when keys are missing.
- `backend/guardrails.py` – Prompt and answer checks using Guardrails AI.
- `app.py` – Compatibility shim so `streamlit run app.py` still launches the UI.

## Prerequisites
1. Python 3.9+ (matching the other class demos).
2. OpenAI API key with access to `gpt-4o-mini` or compatible.
3. Node.js 18+ so `npx` can start the MCP servers (`@openbnb/mcp-server-airbnb`, `@gongrzhe/server-travelplanner-mcp`).
4. (Optional) Langfuse project keys if you want live traces.
5. The credentials shared in class or set your own through env variables:
   - `AGENT_API_USERNAME` / `AGENT_API_PASSWORD`
   - `STREAMLIT_UI_USERNAME` / `STREAMLIT_UI_PASSWORD`

## Setup

### 1. Clone & Create a Virtual Environment
```bash
git clone https://github.com/YOUR-ORG/YOUR-REPO.git
cd YOUR-REPO/classes/class-07-mcp-protocol/demos/ai-agent-application
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 2. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install MCP Server Packages (Node.js)
```bash
npm install -g npm@latest                       # optional but keeps npm current
npm install -g @openbnb/mcp-server-airbnb @gongrzhe/server-travelplanner-mcp
```
Global installs speed up startup. If you cannot install globally, `npx` will download them on first use.

### 4. Configure Environment Files
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```
- `backend/.env` – add your `OPENAI_API_KEY` (required), `GOOGLE_MAPS_API_KEY` (required for Google MCP), optional Langfuse keys, and backend login credentials.
- `frontend/.env` – set the Streamlit login pair and `AGENT_API_BASE`. Point to your Render backend URL once deployed.

### 5. Optional: Cache MCP Packages Locally
If you prefer project-local installs:
```bash
npm install @openbnb/mcp-server-airbnb @gongrzhe/server-travelplanner-mcp
```
Then adjust the commands in `backend/agent.py` to point at `node_modules/.bin/...` if desired.

## Running Locally
1. **Start the FastAPI backend**
   ```bash
   uvicorn backend.main:app --reload
   ```
   On the first `/plan` request the backend launches both MCP servers via `npx`, using the Google Maps key from the environment. If either server fails to start, the agent falls back to sample tools so the lesson can continue.

2. **Launch the Streamlit frontend**
   ```bash
   streamlit run frontend/app.py
   ```
   Log in with the configured Streamlit credentials, fill in trip details, and generate a plan. The UI shows Langfuse/guardrail status and exposes the itinerary download link.

3. **Alternate launch shortcut**
   ```bash
   streamlit run app.py
   ```
   The root entrypoint simply forwards to `frontend/app.py` for folks used to `streamlit run app.py`.

## How MCP Fits In
- `backend/agent.py` uses the pattern from `langgraph_mcp_client.py` to open stdio connections to the public MCP servers (`npx -y @openbnb/mcp-server-airbnb` and `npx @gongrzhe/server-travelplanner-mcp`) and pass their tools into LangGraph’s ReAct agent on each request.
- If either MCP server fails to start (for example, the Google key is missing), the agent automatically falls back to built-in classroom tools so the lesson can continue.

## Guardrails & Monitoring
- Incoming prompts pass through `check_user_prompt` to block toxic or off-topic requests.
- Completed itineraries run through `check_agent_answer` for relevance; guardrail notes reach the UI so students see the enforcement in action.
- Langfuse callbacks are attached whenever credentials are provided, giving full request/response traces under the span name `travel-planner`.

## Troubleshooting
- **401 errors**: Restart the Streamlit app, log in again, or verify `AGENT_API_*` keys on both UI and API.
- **OpenAI errors**: Ensure `OPENAI_API_KEY` is set in the backend environment; the agent prints a warning if the key is missing.
- **MCP failures**: The console will show the exact subprocess error (for example, missing Google Maps key). The fallback toolset keeps the demo running while you debug.
- **Guardrails warning**: If you see “Could not obtain an event loop. Falling back to synchronous validation,” Guardrails is still working—it just runs synchronously. Harmless for classroom demos.
- **Langfuse not monitoring**: Check the `.env` values and confirm `langfuse auth_check()` prints success in the backend logs.

## Deployment Notes
- **Backend (Render or other PaaS)**: Upload the contents of `backend/`, point to `backend.main:app`, and set environment variables from `backend/.env.example` (ensure Node 18+ is available for the MCP servers). Enable persistent disk or build-time installs if you want to preinstall the MCP packages.
- **Frontend (Streamlit Community Cloud)**: Deploy `frontend/app.py`, copy the keys from `frontend/.env.example` into Streamlit’s Secrets manager, and set `AGENT_API_BASE` to the deployed backend URL.
- Both services must share the same login credentials so the Streamlit UI can authenticate successfully against the FastAPI API.

This setup keeps the code approachable for new Python learners while showcasing how agent backends, guardrails, monitoring, and MCP integrations come together. Encourage students to explore each folder, swap the MCP server for real data, and enhance the guardrails as exercises.
