"""Simple API key authentication dependency for FastAPI routes."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Header, HTTPException, status

# Load project .env so APP_API_KEY works when running with uvicorn (no shell export).
_DOTENV_PATH = Path(__file__).resolve().parent / ".env"
# override=True: if APP_API_KEY is set but empty in the OS environment, .env still wins.
load_dotenv(_DOTENV_PATH, override=True)


def _read_key_from_dotenv_file(key: str) -> str:
    """Parse KEY=value from .env without relying solely on python-dotenv (BOM, CRLF, etc.)."""
    if not _DOTENV_PATH.exists():
        return ""
    try:
        text = _DOTENV_PATH.read_text(encoding="utf-8")
    except OSError:
        return ""
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        name, _, value = line.partition("=")
        name = name.strip().lstrip("\ufeff")
        value = value.strip().strip('"').strip("'")
        if name == key and value:
            return value
    return ""


def _load_expected_api_key() -> str:
    """
    Load API key from env first, then optional config.json fallback.

    Environment variable:
        APP_API_KEY
    """
    env_key = os.getenv("APP_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    file_key = _read_key_from_dotenv_file("APP_API_KEY")
    if file_key:
        return file_key

    config_path = Path(__file__).resolve().parent / "config.json"
    if config_path.exists():
        try:
            with config_path.open("r", encoding="utf-8") as file:
                config = json.load(file)
                config_key = config.get("app_api_key")
                if config_key and str(config_key).strip():
                    return str(config_key).strip()
        except Exception:
            return ""

    return ""


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> None:
    """
    Dependency that enforces API key auth via `X-API-Key` request header.
    """
    expected_key = _load_expected_api_key()
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server auth is not configured. Set APP_API_KEY in environment.",
        )

    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key. Provide X-API-Key header.",
        )

    if x_api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )
