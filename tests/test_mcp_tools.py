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
    assert "7 to 9 digits" in out["error"] and "web_search" not in out["error"]
    assert fake.requests == []


async def test_upstream_outage_is_reported_not_raised(mcp_upstream):
    mcp_upstream({"getCurrentFxRates": 503})
    from tools.mcp_tools import exchange_rate
    out = json.loads(await exchange_rate.ainvoke({"currency": "USD"}))
    assert "HTTP 503" in out["error"] and "web_search" in out["error"]


def test_long_results_stay_valid_json_and_keep_citations():
    from tools.mcp_tools import MAX_CHARS, _compact
    env = {"source_name": "TAR", "source_url": "https://get.data.gov.lt/x", "licence": "CC BY 4.0",
           "retrieved_at": "2026-10-13T00:00:00+00:00", "cached": False,
           "data": [{"title": "Įstatymas " + "x" * 2000, "url": f"https://e-tar.lt/{i}"} for i in range(40)]}
    out = _compact(env)
    parsed = json.loads(out)
    assert len(out) <= MAX_CHARS and parsed["truncated"] is True
    assert parsed["source_url"] == "https://get.data.gov.lt/x" and parsed["data"][0]["url"] == "https://e-tar.lt/0"


def test_short_results_are_untouched():
    from tools.mcp_tools import _compact
    assert json.loads(_compact({"data": [1, 2]})) == {"data": [1, 2]}


def test_any_oversized_value_still_gives_valid_json():
    from tools.mcp_tools import MAX_CHARS, _compact
    out = _compact({"x": "a" * 10_000, "y": {"z": "b" * 10_000}})
    assert len(out) <= MAX_CHARS and json.loads(out)["truncated"] is True


def test_assistants_get_the_structured_tools():
    from agents.business.eresidency import TOOLS as business
    from agents.living.tax import TOOLS as tax
    assert {t.name for t in business} == {"company_search", "company_details", "company_tax_data",
                                          "law_search", "law_consolidated", "exchange_rate", "web_search"}
    assert {t.name for t in tax} == {"company_tax_data", "law_search", "law_consolidated",
                                     "exchange_rate", "web_search"}
    assert business[-1].name == "web_search" and tax[-1].name == "web_search"
