"""Web search tool — Exa, biased to official Lithuanian government sources."""

from __future__ import annotations

import logging
from typing import Optional

import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from utils.config import settings

log = logging.getLogger(__name__)

EXA_URL = "https://api.exa.ai/search"

# Official / authoritative Lithuanian domains, used when official_only=True.
# Exa includeDomains is a host allowlist passed unchanged as payload["includeDomains"].
# Parent hosts such as lrv.lt and urm.lt are listed so ministry/agency subdomains
# (migracija.lrv.lt, ligoniukasa.lrv.lt, globalilietuva.urm.lt, …) can match; specific
# hosts are also listed so ranking is not left only to suffix matching.
OFFICIAL_DOMAINS: list[str] = [
    "epaslaugos.lt",
    "lrv.lt",
    "migracija.lrv.lt",
    "ligoniukasa.lrv.lt",
    "socmin.lrv.lt",
    "vssa.lrv.lt",
    "vdai.lrv.lt",
    "vda.lrv.lt",
    "migracija.lt",
    "vmi.lt",
    "sodra.lt",
    "vlk.lt",
    "registrucentras.lt",
    "e-tar.lt",
    "lrs.lt",
    "urm.lt",
    "globalilietuva.urm.lt",
    "keliauk.urm.lt",
    "uzt.lt",
    "vrk.lt",
    "data.gov.lt",
    "lietuva.lt",
    "vilnius.lt",
    "kaunas.lt",
    "klaipeda.lt",
    "stat.gov.lt",
    "investlithuania.com",
    "startuplithuania.com",
    "elektroninisparasas.lt",
]


class SearchArgs(BaseModel):
    query: str = Field(
        description="Natural-language web search query about Lithuanian government services, "
                    "residence permits, taxes, digital identity, moving to Lithuania, or Lithuania in general."
    )
    max_results: int = Field(default=6, ge=1, le=15)
    official_only: bool = Field(
        default=True,
        description="If true (default), restrict results to official/authoritative Lithuanian "
                    "domains (epaslaugos.lt, lrv.lt, migracija.lt, vmi.lt, sodra.lt, etc.). "
                    "Set to false for broader topics like culture, tourism, or history.",
    )
    days: Optional[int] = Field(default=None, description="Recency window in days (optional).")


def _exa(query: str, max_results: int, official_only: bool, days: int | None) -> dict | None:
    key = settings().exa_api_key
    if not key:
        return None
    payload = {
        "query": query,
        "numResults": max_results,
        "type": "auto",
        "contents": {"text": {"maxCharacters": 1000}, "highlights": {"numSentences": 3}},
    }
    if official_only:
        payload["includeDomains"] = OFFICIAL_DOMAINS
    if days:
        from datetime import datetime, timedelta
        payload["startPublishedDate"] = (datetime.utcnow() - timedelta(days=days)).isoformat()
    headers = {"x-api-key": key, "content-type": "application/json"}
    try:
        r = httpx.post(EXA_URL, json=payload, headers=headers, timeout=20.0)
        r.raise_for_status()
        data = r.json()
        return {
            "provider": "exa",
            "results": [
                {"title": h.get("title"), "url": h.get("url"),
                 "snippet": (h.get("text") or "")[:1000],
                 "score": h.get("score")}
                for h in (data.get("results") or [])
            ],
        }
    except Exception as e:
        log.warning("exa failed: %s", e)
        return None


def _web_search(**kw) -> str:
    args = SearchArgs(**kw)
    data = _exa(args.query, args.max_results, args.official_only, args.days)
    # If an official-only search comes back empty, retry once across the open web.
    if data and not data["results"] and args.official_only:
        data = _exa(args.query, args.max_results, False, args.days)
    if not data:
        return "Search unavailable — no EXA_API_KEY configured or provider failed."

    items = data["results"]
    scope = "official Lithuanian sources" if args.official_only else "the web"
    lines = [f"Search over {scope}: {args.query} ({len(items)} results)\n"]
    for it in items:
        title = it.get("title") or "Untitled"
        url = it.get("url") or ""
        snippet = (it.get("snippet") or "")[:300]
        lines.append(f"- **{title}**\n  {url}\n  {snippet}\n")
    return "\n".join(lines)


web_search = StructuredTool.from_function(
    func=_web_search,
    name="web_search",
    description=(
        "Search the web for authoritative information about Lithuania — company registration, "
        "taxes, digital ID (Smart-ID / Mobile-ID / ID-card e-signature), residence permits, "
        "public services, and life in Lithuania. By default it restricts results to official "
        "Lithuanian government and authoritative domains; set official_only=false for broader topics "
        "like culture, tourism, or history. Returns title + URL + snippet. ALWAYS cite the URLs you "
        "use so the user can verify the answer."
    ),
    args_schema=SearchArgs,
)
