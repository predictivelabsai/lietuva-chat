"""FastMCP wiring: every tool registered read-only, envelopes come back, HTTP app is guarded."""

from __future__ import annotations

from starlette.testclient import TestClient

from mcp_server.server import http_app, mcp
from mcp_server.sources import TOOL_FUNCS


async def test_every_tool_is_registered_read_only():
    tools = await mcp.list_tools()
    assert {t.name for t in tools} == set(TOOL_FUNCS) == {
        "company_search", "company_details", "company_tax_data", "law_search", "law_consolidated",
        "exchange_rate", "gov_web_search"}
    assert all(t.annotations and t.annotations.readOnlyHint for t in tools)
    assert all(t.description for t in tools)


async def test_call_tool_returns_the_envelope(mcp_upstream):
    mcp_upstream({"getCurrentFxRates": "lb_fx.xml"})
    _content, structured = await mcp.call_tool("exchange_rate", {"currency": "USD"})
    assert structured["data"]["per_eur"] == 1.1181
    assert structured["source_url"].startswith("https://www.lb.lt/")


def test_http_app_serves_health_and_guards_mcp():
    with TestClient(http_app()) as c:
        health = c.get("/health").json()
        assert health["status"] == "ok" and health["tools"] == len(TOOL_FUNCS)
        assert c.post("/mcp", headers={"Authorization": "Bearer lk_nope"}, json={}).status_code == 401
