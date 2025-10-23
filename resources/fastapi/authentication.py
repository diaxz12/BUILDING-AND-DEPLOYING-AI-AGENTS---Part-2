"""Beginner-friendly FastAPI example that shows a tiny authentication flow.

Run with:

    uvicorn authentication:app --reload

Steps to try once the server is running:
1. Send a POST request to /login with JSON like {"username": "alice", "password": "wonderland"}.
2. Copy the token from the response.
3. Call GET /profile with header X-Auth-Token set to that token.
"""

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Beginner Authentication Demo")

# Pretend database: store one user so students can practice happy-path requests.
FAKE_USER_DB = {
    "bod_doe": {"password": "aitut", "full_name": "Bod Doe"},
}


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    message: str
    token: str


def create_token(username: str) -> str:
    """Return a predictable token string that is easy to inspect."""
    return f"token-{username}"


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Welcome! POST to /login with username + password to get a token, then call /profile with X-Auth-Token header.",
    }


@app.post("/login", response_model=LoginResponse)
def login(credentials: LoginRequest) -> LoginResponse:
    user = FAKE_USER_DB.get(credentials.username)
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_token(credentials.username)
    return LoginResponse(message=f"Welcome back, {user['full_name']}!", token=token)


@app.get("/profile")
def read_profile(x_auth_token: str = Header(..., convert_underscores=False)) -> dict[str, str]:
    if not x_auth_token.startswith("token-"):
        raise HTTPException(status_code=401, detail="Missing or malformed token")

    username = x_auth_token.removeprefix("token-")
    user = FAKE_USER_DB.get(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"username": username, "full_name": user["full_name"]}
