"""LangChain wrappers around the MCP tools, and which assistants get them."""

from __future__ import annotations

import json


async def test_in_process_tool_returns_compact_json(mcp_upstream):
    mcp_upstream({'JuridinisAsmuo?ja_pavadinimas.lower().contains("vinted")': "jar_search.json"})
    from tools.mcp_tools import company_search
    out = json.loads(await company_search.ainvoke({"query": "Vinted", "limit": 3}))
    assert out["data"][0]["company_code"] == "302767152" and out["source_url"].startswith("https://")


async def test_tool_errors_tell_the_agent_to_fall_back(mcp_upstream):
    fake = mcp_upstream({})
    from tools.mcp_tools import company_details
    out = json.loads(await company_details.ainvoke({"company_code": "38001010000"}))
    assert "7 to 9 digits" in out["error"] and "web_search" in out["error"]
    assert fake.requests == []


async def test_upstream_outage_is_reported_not_raised(mcp_upstream):
    mcp_upstream({"getCurrentFxRates": 503})
    from tools.mcp_tools import exchange_rate
    out = json.loads(await exchange_rate.ainvoke({"currency": "USD"}))
    assert "HTTP 503" in out["error"]


def test_long_results_are_truncated():
    from tools.mcp_tools import MAX_CHARS, _compact
    assert len(_compact({"x": "a" * 10_000})) <= MAX_CHARS + len("… [truncated]")


def test_assistants_get_the_structured_tools():
    from agents.business.eresidency import TOOLS as business
    from agents.living.tax import TOOLS as tax
    assert {t.name for t in business} == {"company_search", "company_details", "company_tax_data",
                                          "law_search", "law_consolidated", "exchange_rate", "web_search"}
    assert {t.name for t in tax} == {"company_tax_data", "law_search", "law_consolidated",
                                     "exchange_rate", "web_search"}
    assert business[-1].name == "web_search" and tax[-1].name == "web_search"
