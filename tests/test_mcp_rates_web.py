"""Bank of Lithuania rates and Exa search against recorded / hand-written responses."""

from __future__ import annotations

import json

import pytest

from mcp_server import rates, web
from mcp_server.core import UpstreamError


async def test_exchange_rate_all_and_one(mcp_upstream):
    fake = mcp_upstream({"getCurrentFxRates": "lb_fx.xml"})
    all_rates = await rates.exchange_rate()
    assert all_rates["data"] == {"date": "2026-10-12", "rates": {"GBP": 0.84478, "PLN": 4.385, "USD": 1.1181}}
    one = await rates.exchange_rate("usd")
    assert one["data"] == {"date": "2026-10-12", "currency": "USD", "per_eur": 1.1181}
    assert one["cached"] is True and len(fake.requests) == 1


@pytest.mark.parametrize("bad", ["JPY", "dollars", "U$D"])
async def test_exchange_rate_unknown_currency(mcp_upstream, bad):
    mcp_upstream({"getCurrentFxRates": "lb_fx.xml"})
    with pytest.raises(ValueError, match="No Bank of Lithuania rate"):
        await rates.exchange_rate(bad)


async def test_gov_web_search_needs_a_key(mcp_upstream):
    mcp_upstream({})
    with pytest.raises(UpstreamError, match="not configured"):
        await web.gov_web_search("GPM tarifas")


async def test_gov_web_search_limits_to_official_domains(mcp_upstream, monkeypatch):
    monkeypatch.setenv("EXA_API_KEY", "test-key")
    fake = mcp_upstream({"api.exa.ai/search": "exa.json"})
    r = await web.gov_web_search("GPM tarifas", 3)
    assert r["data"][0]["url"] == "https://www.vmi.lt/evmi/gyventoju-pajamu-mokestis"
    body = json.loads(fake.requests[0].content)
    assert "vmi.lt" in body["includeDomains"] and body["numResults"] == 3
    assert fake.requests[0].headers["x-api-key"] == "test-key"
