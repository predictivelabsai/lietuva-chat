"""Euro reference exchange rates published by the Bank of Lithuania."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from mcp_server.core import cached, envelope, fetch

LB_FX = "https://www.lb.lt/webservices/FxRates/FxRates.asmx/getCurrentFxRates?tp=EU"
_NS = {"lb": "http://www.lb.lt/WebServices/FxRates"}


def parse_lb(xml: bytes | str) -> dict:
    root = ET.fromstring(xml)
    day, out = None, {}
    for fx in root.findall("lb:FxRate", _NS):
        day = fx.findtext("lb:Dt", namespaces=_NS) or day
        for amt in fx.findall("lb:CcyAmt", _NS):
            ccy = amt.findtext("lb:Ccy", namespaces=_NS)
            if ccy and ccy != "EUR":
                out[ccy] = float(amt.findtext("lb:Amt", namespaces=_NS))
    return {"date": day, "rates": out}


async def exchange_rate(currency: str | None = None) -> dict:
    async def run():
        r = await fetch("lb", "GET", LB_FX)
        return envelope("lb", LB_FX, parse_lb(r.content))
    env = await cached(("lb_fx",), 6 * 3600, run)
    if currency is None:
        return env
    ccy = currency.strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", ccy) or ccy not in env["data"]["rates"]:
        raise ValueError(f"No Bank of Lithuania rate for {currency!r}.")
    return {**env, "data": {"date": env["data"]["date"], "currency": ccy, "per_eur": env["data"]["rates"][ccy]}}
