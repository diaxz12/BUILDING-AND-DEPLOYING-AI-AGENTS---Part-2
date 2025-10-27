# Class 6 Lab — Friendly Guardrails & Safety Checks

## Overview

You now have a working AI Agent from class 5 that can answer questions about FastAPI and Streamlit. In Class 6 you will give that agent a safety net. The goal is to add a few approachable guardrails that beginners can understand, then prove they work with a small set of practice prompts. You will finish Part 1 by creating one custom guardrail that catches any request to search the dark web and responds safely. Part 2 looks ahead to your capstone: you will map the guardrails and risks your future project will need so you can plan with confidence.

Think of this lab as the first guardrail pass you would make before sharing the capstone project on Medium. Focus on simple ideas that are easy to explain and debug.

## Learning Goals

- Understand what a guardrail is and where it fits in the FastAPI + LangGraph + Streamlit flow.
- Implement at least two "starter" guardrails using Guardrails AI.
- Create a custom guardrail that detects dark-web search requests and replaces the reply with a clear refusal.
- Collect or generate a lightweight prompt dataset to show that the guardrails trigger when they should and stay quiet when everything is safe.
- Analyze your capstone concept to identify future guardrail needs, ranked by risk level and impact.

## Prerequisites

- Completed Class 5 assignment with the FastAPI `/chat` endpoint, Streamlit UI, and Tavily-enabled LangGraph agent.
- Python 3.10+ and the existing virtual environment in `classes/class-05-deployment-interfaces/demos/fastapi-agent-service`.
- Access to `OPENAI_API_KEY` (or another model provider), `TAVILY_API_KEY`, and optional Langfuse keys.
- Basic familiarity with running `uvicorn main:app --reload`, the Streamlit UI, and `demo_client.py` from Class 5.

---

## Guardrails for the Class 5 Agent

1. **Refresh your Class 5 setup.**
   - Re-activate the `.venv` in the FastAPI demo folder and make sure the `/chat` endpoint still returns helpful answers.
   - Skim your Class 5 `README.md` so you remember the current routing and logging.

2. **Pick two starter guardrails.**
   Choose from the list below (or propose alternatives in your notes):
   - Leverage Guardrails AI and prebuilt guardrails to block or warn on unsafe content.
   - Document which ones you selected and what they do on a `README.md`.

3. **Implement the started guardrails.**
   - Update `classes/class-05-deployment-interfaces/demos/fastapi-agent-service/main.py` so every incoming prompt runs through your starter guardrails **before** LangGraph executes.
   - If a guardrail triggers, return a friendly JSON payload such as `{ "message": "We can’t help with that", "guardrail": "moderation" }` and skip the agent call.
   - Log guardrail decisions to Langfuse (prompt, guardrail name, action taken).

4. **Build the custom dark-web guardrail.**
   - Create a custom guardrail that checks whether the user is asking for dark-web content (mentioning "dark web", ".onion", "hidden service", etc.).
   - When detected, respond with a short refusal that explains the policy. Example: "For safety reasons I can’t help with dark web content."
   - Make sure this guardrail runs for every request.

5. **Add a reply falback if the custom guardrail is activated (optional but encouraged).**
   - After the agent drafts a reply, quickly verify it meets your policy (e.g., no dark-web hints slipped through, answer includes citations, etc.).
   - If the reply fails, replace it with a safe fallback and note that in the logs.

6. **Update the Streamlit UI.**
   - Display the guardrail outcome next to each chat bubble (e.g., badge text like "allowed", "blocked", "dark-web" in a subtle color).
   - Add a small `st.expander("Guardrail logs")` with the most recent guardrail messages so testers can inspect what happened.

7. **Create a friendly prompt dataset.**
   - Add `classes/class-05-deployment-interfaces/demos/fastapi-agent-service/tests/data/guardrail_prompts.jsonl`.
   - Include at least 10 prompts: mix normal Class 5 questions, obvious dark-web requests, and a few edge cases for your starter guardrails.
   - For each prompt, record: `id`, `prompt`, `category` (e.g., `"safe"`, `"dark_web"`), and `expected_outcome` (`"allow"`, `"block"`, or `"warn"`).

8. **Test your guardrails.**
   - Write `tests/test_guardrails.py` that loads the JSONL file, sends each prompt to the FastAPI app (use FastAPI `TestClient` or call `demo_client.py`), and asserts the response matches `expected_outcome`.
   - Save a short summary of the results to `tests/guardrail_results.json` (e.g., number allowed vs. blocked).
   - If you find a failing prompt, update the guardrail or document why it remains tricky in `evaluation.md` (optional).

9. **Document the changes.**
   - Update the FastAPI demo `README.md` with setup instructions, new environment variables (e.g., `GUARDRAILS_API_KEY`), and how to run the guardrail tests.
   - Extend `IMPLEMENTATION_NOTES.md` with:
     - Guardrail list (starter guardrails + dark-web guardrail).
     - How to read the logs/Streamlit panel.
     - A quick summary of your dataset results.

## Deliverables

- Share the source code of the assignment.
- Updated FastAPI service and Streamlit UI code with the new guardrails.
- Prompt dataset and tests: `tests/data/guardrail_prompts.jsonl`, `tests/test_guardrails.py`, and generated `tests/guardrail_results.json`.
- Documentation updates (`README.md` and optional `evaluation.md`) explaining setup, guardrails, and evidence.
- Optional: quick video demonstrating a blocked dark-web request.