import os
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel


router = APIRouter(tags=["auth"])
USERS_FILE = "users.json"
DEFAULT_USERS = [{"email": "admin@ats.com", "password": "password123"}]
USERS_FILE_PATH = Path(__file__).resolve().parents[1] / USERS_FILE


class LoginRequest(BaseModel):
    email: str
    password: str


def _read_users() -> list[dict]:
    if not USERS_FILE_PATH.exists():
        _write_users(DEFAULT_USERS)
        return DEFAULT_USERS.copy()

    try:
        raw = USERS_FILE_PATH.read_text(encoding="utf-8").strip()
        if not raw:
            _write_users(DEFAULT_USERS)
            return DEFAULT_USERS.copy()

        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return [user for user in parsed if isinstance(user, dict)]
    except Exception:
        pass

    _write_users(DEFAULT_USERS)
    return DEFAULT_USERS.copy()


def _write_users(users: list[dict]) -> None:
    USERS_FILE_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


@router.post("/api/auth/register")
def register(payload: LoginRequest) -> dict:
    users = _read_users()
    normalized_email = payload.email.strip().lower()

    if any(str(user.get("email", "")).strip().lower() == normalized_email for user in users):
        raise HTTPException(status_code=400, detail="Email already registered.")

    users.append({"email": payload.email.strip(), "password": payload.password})
    _write_users(users)
    return {"message": "Registration successful."}


@router.post("/api/auth/login")
def login(payload: LoginRequest) -> dict:
    users = _read_users()
    normalized_email = payload.email.strip().lower()

    matched_user = next(
        (
            user
            for user in users
            if str(user.get("email", "")).strip().lower() == normalized_email
            and str(user.get("password", "")) == payload.password
        ),
        None,
    )

    if not matched_user:
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    jwt_secret = os.getenv("JWT_SECRET", "super-secret-ats-key")
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    token = jwt.encode(
        {"sub": payload.email.strip(), "exp": expires_at},
        jwt_secret,
        algorithm="HS256",
    )

    return {"access_token": token, "token_type": "bearer"}
