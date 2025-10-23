"""Tiny helper to check the FastAPI chat endpoint with authentication."""

import argparse
import os
import uuid

import httpx


def main():
    parser = argparse.ArgumentParser(description="Send a message to the agent API")
    parser.add_argument("message", help="Prompt for the agent")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="FastAPI base URL")
    parser.add_argument("--session-id", default=str(uuid.uuid4()), help="Session identifier")
    parser.add_argument("--username", default=os.getenv("AGENT_API_USERNAME"), help="Login username (falls back to AGENT_API_USERNAME env var)")
    parser.add_argument("--password", default=os.getenv("AGENT_API_PASSWORD"), help="Login password (falls back to AGENT_API_PASSWORD env var)")
    parser.add_argument("--token", default=os.getenv("AGENT_API_TOKEN"), help="Existing auth token to reuse")
    args = parser.parse_args()

    token = args.token
    if not token:
        if not args.username or not args.password:
            parser.error("Provide --token or username/password (via flags or environment variables).")
        login_payload = {"username": args.username, "password": args.password}
        login_res = httpx.post(f"{args.base_url}/login", json=login_payload, timeout=20)
        login_res.raise_for_status()
        token = login_res.json()["token"]

    payload = {"message": args.message, "session_id": args.session_id}
    headers = {"x_auth_token": token}
    response = httpx.post(f"{args.base_url}/chat", json=payload, headers=headers, timeout=20)
    response.raise_for_status()
    data = response.json()
    print(f"Reply: {data['reply']}")
    print(f"Source: {data['source']} • Langfuse trace: {data['monitored']} • Session: {data['session_id']}")
    print(f"Token used: {token}")


if __name__ == "__main__":
    main()
