"""Web search over official Lithuanian sites (Exa), for questions no structured tool covers."""

from __future__ import annotations

from mcp_server.config import mcp_settings
from mcp_server.core import UpstreamError, cached, envelope, fetch

EXA_URL = "https://api.exa.ai/search"


async def gov_web_search(query: str, max_results: int = 6, official_only: bool = True) -> dict:
    from tools.search import OFFICIAL_DOMAINS  # the chat app's allowlist, so both stay in step

    key = mcp_settings().exa_api_key
    if not key:
        raise UpstreamError("web search is not configured on this server")
    n = max(1, min(15, int(max_results)))
    payload = {"query": query, "numResults": n, "type": "auto",
               "contents": {"text": {"maxCharacters": 1000}, "highlights": {"numSentences": 3}}}
    if official_only:
        payload["includeDomains"] = OFFICIAL_DOMAINS

    async def run():
        r = await fetch("exa", "POST", EXA_URL, json=payload,
                        headers={"x-api-key": key, "content-type": "application/json"}, retries=1)
        res = [{"title": x.get("title"), "url": x.get("url"), "published": x.get("publishedDate"),
                "highlights": x.get("highlights") or [], "text": (x.get("text") or "")[:1000]}
               for x in r.json().get("results", [])]
        return envelope("exa", EXA_URL, res)
    return await cached(("exa", query.lower(), n, official_only), 6 * 3600, run)
