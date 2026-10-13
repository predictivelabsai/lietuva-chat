"""Bank of Lithuania rates and Exa search against recorded / hand-written responses."""

from __future__ import annotations

import json

import pytest

from mcp_server import rates, web
from mcp_server.core import UpstreamError


async def test_exchange_rate_all_and_one(mcp_upstream):
    fake = mcp_upstream({"getCurrentFxRates": "lb_fx.xml"})
    data = (await rates.exchange_rate())["data"]
    assert data["latest_date"] == "2026-10-12"
    assert data["rates"]["USD"] == {"per_eur": 1.1181, "date": "2026-10-12"}
    assert data["rates"]["AED"] == {"per_eur": 4.1032, "date": "2026-09-29"}
    assert set(data["rates"]) == {"GBP", "PLN", "USD", "AED", "RUB"}
    one = await rates.exchange_rate("usd")
    assert one["data"] == {"currency": "USD", "per_eur": 1.1181, "date": "2026-10-12", "stale": False}
    assert one["cached"] is True and len(fake.requests) == 1


async def test_each_rate_keeps_its_own_date(mcp_upstream):
    """Bank of Lithuania's own rates are published less often than the ECB's: never relabel them."""
    mcp_upstream({"getCurrentFxRates": "lb_fx.xml"})
    aed = (await rates.exchange_rate("AED"))["data"]
    assert aed["date"] == "2026-09-29" and aed["stale"] is False


async def test_a_rate_no_longer_published_is_flagged(mcp_upstream):
    mcp_upstream({"getCurrentFxRates": "lb_fx.xml"})
    rub = (await rates.exchange_rate("RUB"))["data"]
    assert rub["date"] == "2022-03-01" and rub["stale"] is True
    assert "2022-03-01" in rub["note"] and "not current" in rub["note"]


def test_rates_are_described_as_information_only():
    from mcp_server.core import SOURCES
    assert "Bank of Lithuania" in SOURCES["lb"].name and "ECB" in SOURCES["lb"].name
    assert "information only" in SOURCES["lb"].licence


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


async def test_gov_web_search_refuses_personal_codes(mcp_upstream, monkeypatch):
    monkeypatch.setenv("EXA_API_KEY", "test-key")
    fake = mcp_upstream({"api.exa.ai/search": "exa.json"})
    with pytest.raises(ValueError, match="personal code"):
        await web.gov_web_search("mano kodas 38001010000 deklaracija")
    assert fake.requests == []


def test_gov_web_search_has_no_open_web_switch():
    import inspect
    assert "official_only" not in inspect.signature(web.gov_web_search).parameters


async def test_exchange_rate_on_a_date_uses_the_last_rate_published_by_then(mcp_upstream):
    """2026-03-15 is a Sunday: the rate is Friday's, as Article 5 of the Financial Accounting Law expects."""
    fake = mcp_upstream({"getFxRates?tp=EU&dt=2026-03-15": "lb_fx_2026-03-15.xml"})
    usd = (await rates.exchange_rate("USD", on_date="2026-03-15"))["data"]
    assert usd == {"currency": "USD", "per_eur": 1.1476, "date": "2026-03-13", "stale": False, "on_date": "2026-03-15"}
    rub = (await rates.exchange_rate("RUB", on_date="2026-03-15"))["data"]
    assert rub["stale"] is True and rub["date"] == "2022-03-01"
    assert len(fake.requests) == 1


@pytest.mark.parametrize("bad", ["15/03/2026", "2999-01-01"])
async def test_exchange_rate_rejects_bad_or_future_dates(mcp_upstream, bad):
    fake = mcp_upstream({})
    with pytest.raises(ValueError):
        await rates.exchange_rate("USD", on_date=bad)
    assert fake.requests == []
