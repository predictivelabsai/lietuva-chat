"""The API's JWT signing secret must never fall back to a guessable value.
Each case runs in a fresh interpreter because the secret is read at import time."""

import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Forge a token with a known secret, then ask the real module to accept it.
FORGE = """
import base64, hashlib, hmac, json, time
from api.auth import JWT_SECRET, decode_token
b = lambda d: base64.urlsafe_b64encode(d).rstrip(b"=").decode()
head = b(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
body = b(json.dumps({"sub": 1, "email": "x@y.z", "exp": int(time.time()) + 60}).encode())
sig = b(hmac.new(%r.encode(), f"{head}.{body}".encode(), hashlib.sha256).digest())
print("ACCEPTED" if decode_token(f"{head}.{body}.{sig}") else "REJECTED", len(JWT_SECRET))
"""


def run(guess: str, **env: str) -> str:
    clean = {k: v for k, v in os.environ.items() if k not in ("JWT_SECRET", "APP_SECRET")}
    out = subprocess.run([sys.executable, "-c", FORGE % guess], cwd=ROOT, env={**clean, **env},
                         capture_output=True, text=True, check=True)
    return out.stdout.strip()


@pytest.mark.parametrize("guess", ["lietuva-chat-app-2026", "eesti-chat-app-2026", ""])
@pytest.mark.parametrize("env", [{}, {"JWT_SECRET": "", "APP_SECRET": ""}], ids=["unset", "empty"])
def test_missing_secret_cannot_be_guessed(env, guess):
    verdict, length = run(guess, **env).split()
    assert verdict == "REJECTED"
    assert int(length) == 64  # random token_hex(32)


def test_configured_secrets_are_used_in_order():
    assert run("from-jwt", JWT_SECRET="from-jwt", APP_SECRET="from-app").startswith("ACCEPTED")
    assert run("from-app", JWT_SECRET="", APP_SECRET="from-app").startswith("ACCEPTED")
