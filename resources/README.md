# Resources Quickstart Guide

This guide shows you how to launch the bite-sized demos that live in the
`resources/` folder. Each section walks through the setup from scratch so you can
practice even if you have never used FastAPI, Streamlit, Guardrails AI, or Langfuse
before.

## Before You Start
1. Confirm you have Python 3.10 or newer:
   - macOS / Linux: `python3 --version`
   - Windows PowerShell: `py --version`
2. Clone (or pull) this repository and open a terminal in the project root.
3. Pick the demo you want to explore and follow the matching section below.

> Tip: Create a fresh virtual environment in each demo folder so the libraries stay
> isolated. When you finish, run `deactivate` to leave the environment.

---

## FastAPI Mini APIs (`resources/fastapi/`)
These files spin up tiny FastAPI apps that illustrate common patterns.

### 1. Setup
```bash
cd resources/fastapi
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Hello World (`hello_world.py`)
1. Start the server: `uvicorn hello_world:app --reload`
2. Open http://127.0.0.1:8000 in your browser to see the JSON response.
3. Stop with `Ctrl+C` when you are done.

### 3. Path and Query Parameters
- `uvicorn path_parameters:app --reload` then visit
  `http://127.0.0.1:8000/items/abc123`
- `uvicorn query_parameters:app --reload` then try
  `http://127.0.0.1:8000/items/?skip=1&limit=1`

### 4. Request Body Example
1. Launch: `uvicorn request_body:app --reload`
2. Send a POST with `curl` (or your favourite REST client):
   ```bash
   curl -X POST http://127.0.0.1:8000/items/ \
     -H "Content-Type: application/json" \
     -d '{"name": "Notebook", "price": 9.99, "tax": 1.99}'
   ```
3. FastAPI echoes the validated data back.

### 5. Authentication Flow (`authentication.py`)
1. Run `uvicorn authentication:app --reload`
2. Log in to get a token:
   ```bash
   curl -X POST http://127.0.0.1:8000/login \
     -H "Content-Type: application/json" \
     -d '{"username": "bod_doe", "password": "aitut"}'
   ```
3. Copy the `token` value from the response.
4. Fetch the profile with the token:
   ```bash
   curl http://127.0.0.1:8000/profile -H "X-Auth-Token: token-bod_doe"
   ```

### 6. Call an External API (`invoking_endpoint.py`)
1. Ensure your virtual environment is still active.
2. Run `python invoking_endpoint.py`
3. You should see live JSON weather data printed in your terminal.

### 7. Render Deployment Example
Review `render_deployment_example/README.md` inside the folder for step-by-step
deployment instructions that mirror Render’s hosting workflow.

---

## Streamlit UI Demos (`resources/streamlit/`)
Streamlit lets you create web apps straight from Python scripts.

### 1. Setup
```bash
cd resources/streamlit
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Your First App
```bash
streamlit run text_and_titles.py
```
- A browser tab opens automatically.
- Press `CTRL+C` in the terminal to stop the app when finished.

### 3. Explore Other Examples
- `streamlit run interactive_widgets.py` — play with user input controls.
- `streamlit run chat_ui.py` — try the chat interface (type prompts in the box).
- `streamlit run working_with_data.py` — load data frames and display tables.
- `streamlit run visualisation_components.py` — explore charts built with
  Matplotlib, Streamlit, and Plotly.

> If Streamlit asks to install extra packages (like `pydeck`), accept the prompt or
> add them with `pip install package-name`.

---

## Guardrails AI Validators (`resources/guardrails-ai/`)
These scripts show how to add safety checks around LLM outputs.

### 1. Setup
```bash
cd resources/guardrails-ai
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Hub Guardrail Example
```bash
python use_guardrail_hub.py
```
- Expected: the first phone number passes, the second raises an exception.

### 3. Combine Multiple Guardrails
```bash
python multiple_guardrails.py
```
- Notice the friendly input sails through.
- The second input triggers both guardrails and prints the error message.

### 4. Create a Custom Guardrail
1. Create a new file `my_custom_validators.py` alongside the scripts with the
   following content:
   ```python
   from typing import Dict
   from guardrails import OnFailAction
   from guardrails.validators import (
       FailResult,
       PassResult,
       RegisterableValidator,
       ValidationResult,
       register_validator,
   )


   class ToxicLanguage(RegisterableValidator):
       name = "custom_toxic_language"
       on_fail = OnFailAction.EXCEPTION

       def validate(self, value, metadata):
           if "awful" in value.lower():
               return self.fail("Detected the word 'awful'.")
           return self.pass_result()


   @register_validator(name="toxic-words", data_type="string")
   def toxic_words(value: str, metadata: Dict) -> ValidationResult:
       banned_words = []
       for word in ["butt", "poop", "booger"]:
           if word in value:
               banned_words.append(word)

       if banned_words:
           return FailResult(f"Detected banned words: {', '.join(banned_words)}")
       return PassResult()
   ```
2. Run `python custom_guard.py`
3. Try editing the list of forbidden words in `custom_guard.py` to see different
   failures.

---

## Langfuse + LangGraph Trace (`resources/langfuse/`)
This sample traces a LangGraph conversation into Langfuse.

### 1. Setup
```bash
cd resources/langfuse
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys
1. Create a Langfuse project (free tier is available) and note your
   `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST`.
2. Grab an OpenAI API key (or adjust the script to use a provider you have).
3. Replace the placeholder strings near the top of `langgraph_example.py` with your
   real keys, or set environment variables before running:
   - macOS / Linux:
     ```bash
     export LANGFUSE_PUBLIC_KEY=pk-...
     export LANGFUSE_SECRET_KEY=sk-...
     export LANGFUSE_HOST=https://cloud.langfuse.com
     export OPENAI_API_KEY=sk-...
     ```
   - Windows PowerShell:
     ```powershell
     setx LANGFUSE_PUBLIC_KEY "pk-..."
     setx LANGFUSE_SECRET_KEY "sk-..."
     setx LANGFUSE_HOST "https://cloud.langfuse.com"
     setx OPENAI_API_KEY "sk-..."
     ```
   - Restart the terminal after using `setx` so the new variables load.

### 3. Run the Trace
```bash
python langgraph_example.py
```
- The script streams state updates to your terminal.
- Visit the Langfuse dashboard to inspect the trace once the script finishes.

---

## Need a Reset?
- Use `deactivate` to leave a virtual environment.
- Remove the `.venv` folder in a demo directory if you want a clean slate.
- If a command fails, read the error message carefully—it usually suggests the
  missing package or typo to fix.
