"""Euro exchange rates from the Bank of Lithuania's FxRates service (ECB reference rates plus its own)."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import date, timedelta

from mcp_server.core import cached, envelope, fetch

LB_FX = "https://www.lb.lt/webservices/FxRates/FxRates.asmx/getCurrentFxRates?tp=EU"
# For a date the service returns the last rate published on or before it, the rule in
# Article 5 of the Financial Accounting Law.
LB_FX_ON = "https://www.lb.lt/webservices/FxRates/FxRates.asmx/getFxRates?tp=EU&dt={day}"
_NS = {"lb": "http://www.lb.lt/WebServices/FxRates"}
# The bank publishes its own (non-ECB) rates less often than daily; a rate much older than
# the newest one in the feed is no longer being published (e.g. RUB, frozen since 2022-03-01).
STALE_AFTER = timedelta(days=31)


def parse_lb(xml: bytes | str) -> dict:
    """Every currency keeps the date it was published on; the feed mixes several."""
    root = ET.fromstring(xml)
    out: dict[str, dict] = {}
    for fx in root.findall("lb:FxRate", _NS):
        day = fx.findtext("lb:Dt", namespaces=_NS)
        for amt in fx.findall("lb:CcyAmt", _NS):
            ccy = amt.findtext("lb:Ccy", namespaces=_NS)
            if ccy and ccy != "EUR":
                out[ccy] = {"per_eur": float(amt.findtext("lb:Amt", namespaces=_NS)), "date": day}
    return {"latest_date": max((r["date"] for r in out.values() if r["date"]), default=None), "rates": out}


def _one(data: dict, ccy: str) -> dict:
    rate = data["rates"][ccy]
    stale = bool(rate["date"] and data["latest_date"] and
                 date.fromisoformat(data["latest_date"]) - date.fromisoformat(rate["date"]) > STALE_AFTER)
    out = {"currency": ccy, "per_eur": rate["per_eur"], "date": rate["date"], "stale": stale}
    if stale:
        out["note"] = f"Last published on {rate['date']}; this rate is not current and should not be used as one."
    return out


def _past_date(value: str) -> str:
    try:
        day = date.fromisoformat(value.strip())
    except ValueError:
        raise ValueError("Use a date like 2026-03-15.") from None
    if day > date.today():
        raise ValueError("Exchange rates are only published for past dates.")
    return day.isoformat()


async def exchange_rate(currency: str | None = None, on_date: str | None = None) -> dict:
    day = _past_date(on_date) if on_date else None
    url = LB_FX_ON.format(day=day) if day else LB_FX

    async def run():
        r = await fetch("lb", "GET", url)
        return envelope("lb", url, parse_lb(r.content))
    # A past day's rates never change; today's (and the latest) arrive during the day, around 17:00.
    settled = day is not None and day < date.today().isoformat()
    env = await cached(("lb_fx", day), 30 * 24 * 3600 if settled else 6 * 3600, run)
    if currency is None:
        return env
    ccy = currency.strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", ccy) or ccy not in env["data"]["rates"]:
        raise ValueError(f"No Bank of Lithuania rate for {currency!r}.")
    one = _one(env["data"], ccy)
    return {**env, "data": {**one, "on_date": day} if day else one}
