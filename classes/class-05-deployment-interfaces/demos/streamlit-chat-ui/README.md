# Streamlit Chat UI

A beginner-friendly front-end for the Class 5 agent API. Everything is in one file (`app.py`) so you can trace the flow from input → request → response.

## Before you launch the UI

- Make sure the FastAPI demo is already running on `http://127.0.0.1:8000` (or a deployed URL).
- Stay inside this folder: `classes/class-05-deployment-interfaces/demos/streamlit-chat-ui`.
- Python 3.10+ needs to be installed on your machine.
- Copy `.env.example` to `.env` if you want to change the default classroom login (`student` / `streamlit-demo`). Keep the same values in the FastAPI demo so the UI can request an API token after sign-in.

## Step-by-step: run Streamlit locally

1. **Create a virtual environment** (skip if you reuse the one from the API):
   - macOS / Linux:
     ```bash
     python3 -m venv .venv
     ```
   - Windows (PowerShell):
     ```powershell
     py -3 -m venv .venv
     ```

2. **Activate the environment**:
   - macOS / Linux:
     ```bash
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```powershell
     .venv\Scripts\Activate.ps1
     ```

3. **Install the requirements** listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```
   Streamlit opens a browser tab at http://localhost:8501. If it does not, copy the displayed URL into your browser.

5. **Sign in on the login screen** using the credentials from your `.env` file (defaults: `student` / `streamlit-demo`). The app reuses those credentials to obtain an API token automatically.

6. **Try the chat**:
   - Type a question such as “How do I deploy FastAPI?”
   - Watch the assistant reply and check the caption for `Source`. It shows `langgraph:<model>` when the agent runs with tools, or `offline` when the helper fallback answered.
   - The caption also reports whether Langfuse recorded a trace.

7. **Reset the conversation** by clicking “Start over” in the sidebar. This clears the history and generates a new session ID.

8. **Stop Streamlit** with `CTRL+C` in the terminal when you have finished experimenting.

## Pointing the UI to a deployed API

- Use the sidebar field “FastAPI base URL” to swap `http://localhost:8000` for your Render URL (e.g. `https://my-agent.onrender.com`).
- To pre-fill the URL when hosting this UI on Streamlit Cloud, add the following secret:
  ```toml
  # .streamlit/secrets.toml on Streamlit Cloud
  AGENT_API_BASE = "https://my-agent.onrender.com"
  ```

## Deploying to Streamlit Community Cloud

1. Create a new GitHub repository with the following files: `app.py`, `requirements.txt` and `.env.example`.
2. Visit https://share.streamlit.io/ and sign in with your GitHub account.
3. Click **Create app**, choose the repository and branch, and set the main file path to `app.py`.
4. Under **Advanced settings**, add any secrets (for example `AGENT_API_BASE`) so the UI knows where your FastAPI service lives.
5. Press **Deploy**. Streamlit will build the app, install packages from `requirements.txt`, and give you a public URL to share with classmates.
6. After deployment, try the app from the public URL and verify the caption shows the correct API source and monitoring status.

The app prints a short caption under every answer so students can see whether it came from OpenAI or from the built-in helper and whether Langfuse monitoring was active.
