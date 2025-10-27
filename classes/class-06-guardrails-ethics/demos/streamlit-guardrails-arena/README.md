# Guardrails Comparison Arena

This Streamlit UI lets you compare **Checkout Charlie** with and without guardrails. Launch both FastAPI demos, then use the arena to run the same prompt through each service and inspect the differences side by side.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # optional overrides
streamlit run app.py
```

By default the app points to:

- `http://localhost:8000/chat` – unguarded agent
- `http://localhost:8001/chat` – guardrails-enabled agent

Override these URLs with environment variables or via the sidebar inputs.

## Suggested Flow

1. Run the two FastAPI services in separate terminals:
   - `uvicorn ../ai-agent-no-guardrails/main:app --port 8000 --reload`
   - `uvicorn ../ai-agent-with-guardrails/main:app --port 8001 --reload`
2. Start the arena with `streamlit run app.py`.
3. Paste one of the suggested probe prompts (sidebar) or craft your own.
4. Review the responses, any logged guardrail violations, and open the "Raw response" expanders to inspect metadata.
5. Use the shared `session_id` displayed in the UI to line up logs or notebook experiments across both services.