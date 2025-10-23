# Class 5 Demo Suite

These demos follow the Class 5 story: a Streamlit user interface, a FastAPI backend, and optional Langfuse monitoring. The code uses only beginner-friendly Python so that students can read and tweak it easily.

| Demo | Folder | Purpose |
| --- | --- | --- |
| Streamlit Chat UI | `streamlit-chat-ui/` | Minimal chat interface that calls the FastAPI `/chat` endpoint and shows where responses come from. |
| FastAPI Agent Service | `fastapi-agent-service/` | Chat API that wraps a LangGraph ReAct agent (two tools) with a rule-based fallback and Langfuse traces when keys are provided. |

## Before you start

- Install Python 3.10 or newer.
- Make sure you can open a terminal (macOS/Linux Terminal, Windows PowerShell).
- Every demo includes a `requirements.txt` file listing the packages you need.
- Run the backend first, then launch the Streamlit UI so the chat button has somewhere to send requests.

Open each demo’s README and follow the numbered checklist. Every step shows the exact command to copy so you can reproduce the class walkthrough on your own laptop.

> **Tip:** Leave the API keys blank during class practice and the demos will still run using the built-in helper replies.
