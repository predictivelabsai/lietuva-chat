"""API-key auth and rate limits on the MCP HTTP transport."""

from __future__ import annotations

import httpx

from mcp_server.auth import AuthRateLimitMiddleware, hash_key
from mcp_server.config import MCPSettings


async def ok_app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


def client(**settings) -> httpx.AsyncClient:
    app = AuthRateLimitMiddleware(ok_app, MCPSettings(**settings))
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_anonymous_limit_then_429():
    async with client(anon_rpm=2) as c:
        assert (await c.post("/mcp")).status_code == 200
        assert (await c.post("/mcp")).status_code == 200
        third = await c.post("/mcp")
    assert third.status_code == 429 and int(third.headers["retry-after"]) >= 1
    assert "anonymous tier" in third.json()["error"]


async def test_invalid_key_is_401():
    async with client() as c:
        r = await c.post("/mcp", headers={"Authorization": "Bearer lk_wrong"})
    assert r.status_code == 401 and "bearer" in r.headers["www-authenticate"].lower()


async def test_valid_key_gets_key_tier():
    good = "lk_good"
    async with client(anon_rpm=1, key_rpm=5, api_key_hashes=frozenset({hash_key(good)})) as c:
        codes = [(await c.post("/mcp", headers={"X-API-Key": good})).status_code for _ in range(5)]
    assert codes == [200] * 5


async def test_health_is_never_limited():
    async with client(anon_rpm=1) as c:
        codes = [(await c.get("/health")).status_code for _ in range(5)]
    assert codes == [200] * 5


async def test_forwarded_for_uses_the_address_our_proxy_added():
    # The proxy appends the real client address; anything to its left came from the client.
    async with client(anon_rpm=1, trust_proxy=True) as c:
        first = await c.post("/mcp", headers={"X-Forwarded-For": "1.1.1.1, 203.0.113.7"})
        spoofed = await c.post("/mcp", headers={"X-Forwarded-For": "2.2.2.2, 203.0.113.7"})
    assert first.status_code == 200 and spoofed.status_code == 429


async def test_forwarded_for_is_ignored_without_a_trusted_proxy():
    async with client(anon_rpm=1, trust_proxy=False) as c:
        first = await c.post("/mcp", headers={"X-Forwarded-For": "1.1.1.1"})
        second = await c.post("/mcp", headers={"X-Forwarded-For": "2.2.2.2"})
    assert first.status_code == 200 and second.status_code == 429
