# E-commerce Agent With Guardrails

This demo reprises **Checkout Charlie**, but this time the agent is wrapped in three concrete guardrail passes:

- **Prompt Guard** – every user turn is screened with the `SensitiveTopic` (blocking politics) and `ToxicLanguage` guards. Violations short-circuit the agent and the API returns an apologetic fallback reply.
- **Response Guard** – the same content guard runs on the model output before we send it back, ensuring it stays civil and on policy.
- **Relevance Guard** – `QARelevanceLLMEval` checks whether the answer addresses the latest user request. Failures trigger a nudge asking for more product detail.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
guardrails hub install hub://guardrails/sensitive_topics # install the sensitive guardrails guardrails
guardrails hub install hub://guardrails/toxic_language # install the toxic language detection guardrails
guardrails hub install hub://guardrails/qa_relevance_llm_eval # install the relevance check guardrails
cp .env.example .env  # add keys
uvicorn main:app --reload --port 8001  # or python main.py
```

During normal interactions, the JSON response omits `guardrails_applied`. When any guard rejects a turn the field is included with a short explanation so clients can surface the enforcement to end users or logs.

## Guardrail Showcases

Try these scenarios:

- Ask about politics or use toxic language to exercise the prompt guard.
- Force the model off-topic (e.g., "tell me a bedtime story") to see the relevance guard correction.
- Provide a valid shopping question to observe a clean response without the `guardrails_applied` key.

## Environment

```
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## Demo Flow

1. Create a Guardrails AI account and configure the API key.
2. Boot the server with `python main.py` or `uvicorn main:app --reload --port 8001`. We will use a different port so we can test the agent with no guardrails.
3. Compare the behaviour with the unguarded demo using the provided prompts on the `streamlit-guardrails-arena`
