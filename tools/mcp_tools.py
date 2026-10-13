"""LangChain tools backed by the lietuva.chat MCP server (mcp_server/).

If LIETUVA_MCP_URL is set (e.g. https://mcp.lietuva.chat/mcp) the tools call the remote server
over streamable HTTP, sending LIETUVA_MCP_API_KEY as a bearer token when present. Otherwise they
call the same functions in-process, so development needs no extra deployment.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Optional

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

log = logging.getLogger(__name__)

MAX_CHARS = 6000


def _dumps(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, default=str)


def _shorten(value: Any, limit: int = 400) -> Any:
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + "…"
    if isinstance(value, list):
        return [_shorten(v, limit) for v in value]
    if isinstance(value, dict):
        return {k: _shorten(v, limit) for k, v in value.items()}
    return value


def _compact(payload: Any) -> str:
    """JSON for the model, at most MAX_CHARS: shorten long strings, then drop trailing data items.
    The envelope's citation fields come first and are always kept."""
    s = _dumps(payload)
    if len(s) <= MAX_CHARS:
        return s
    small = _shorten(payload) if isinstance(payload, dict) else {"data": _shorten(payload)}
    small["truncated"] = True
    items = small.get("data")
    while isinstance(items, list) and items and len(_dumps(small)) > MAX_CHARS:
        items.pop()
    if len(_dumps(small)) > MAX_CHARS:
        small = {k: small[k] for k in ("source_name", "source_url", "licence", "retrieved_at") if k in small}
        small.update(data=None, truncated=True)
    return _dumps(small)


async def call_mcp_tool(name: str, args: dict) -> dict:
    url = os.environ.get("LIETUVA_MCP_URL", "").strip()
    if not url:
        from mcp_server.sources import TOOL_FUNCS
        return await TOOL_FUNCS[name](**args)
    import httpx
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client
    key = os.environ.get("LIETUVA_MCP_API_KEY", "").strip()
    headers = {"Authorization": f"Bearer {key}"} if key else None
    async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(30.0, read=300.0),
                                 follow_redirects=True) as http:
        async with streamable_http_client(url, http_client=http) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                res = await session.call_tool(name, args)
    if res.isError:
        raise RuntimeError(" ".join(getattr(c, "text", "") for c in res.content) or "tool failed")
    if res.structuredContent is not None:
        sc = res.structuredContent
        return sc.get("result", sc) if isinstance(sc, dict) and set(sc) == {"result"} else sc
    text = " ".join(getattr(c, "text", "") for c in res.content)
    try:
        return json.loads(text)
    except ValueError:
        return {"text": text}


def _make(name: str, description: str, schema: type[BaseModel]) -> StructuredTool:
    async def _run(**kwargs) -> str:
        args = {k: v for k, v in kwargs.items() if v is not None}
        try:
            return _compact(await call_mcp_tool(name, args))
        except Exception as e:  # noqa: BLE001 — any failure becomes advice to the agent, never a crash
            while isinstance(e, BaseExceptionGroup) and e.exceptions:
                e = e.exceptions[0]
            log.warning("MCP tool %s failed: %s", name, e)
            msg = str(e).rstrip(".")
            # Searching the web with a personal code would leak it; only other failures get the fallback.
            advice = "" if "personal code" in msg.lower() else " Fall back to web_search."
            return _compact({"error": f"{name} unavailable: {msg}.{advice}"})

    return StructuredTool.from_function(coroutine=_run, name=name, description=description, args_schema=schema)


class _CompanySearch(BaseModel):
    query: str = Field(description="Company name (or part) or company code")
    limit: int = Field(default=5, ge=1, le=25)


class _CompanyCode(BaseModel):
    company_code: str = Field(description="Lithuanian company code, 7–9 digits (never a personal code)")


class _LawSearch(BaseModel):
    query: str = Field(description="Words from the act title in Lithuanian, e.g. 'akcinių bendrovių įstatymas'")
    only_in_force: bool = Field(default=True, description="Only acts currently in force")
    limit: int = Field(default=5, ge=1, le=20)


class _LawConsolidated(BaseModel):
    document_id: str = Field(description="document_id from law_search, e.g. TAR.C677663D2202")
    on_date: Optional[str] = Field(default=None, description="YYYY-MM-DD; defaults to today")


class _Fx(BaseModel):
    currency: Optional[str] = Field(default=None, description="ISO currency code, e.g. USD")


company_search = _make(
    "company_search",
    "Search the official Lithuanian Legal Entities Register (JAR) by company name or code. "
    "Use to check whether a name is taken or to find a company's code.", _CompanySearch)
company_details = _make(
    "company_details",
    "Official JAR and VMI data for a company: legal form, legal status, registration dates, VAT number.",
    _CompanyCode)
company_tax_data = _make(
    "company_tax_data", "Taxes paid by a company as published by VMI (latest periods first).", _CompanyCode)
law_search = _make(
    "law_search", "Search Lithuanian legal acts in the TAR register by title (Lithuanian words).", _LawSearch)
law_consolidated = _make(
    "law_consolidated",
    "Link to the consolidated version of a legal act in force on a date (from law_search's document_id).",
    _LawConsolidated)
exchange_rate = _make(
    "exchange_rate", "Latest euro reference exchange rates published by the Bank of Lithuania.", _Fx)

BUSINESS_TOOLS = [company_search, company_details, company_tax_data, law_search, law_consolidated, exchange_rate]
TAX_TOOLS = [company_tax_data, law_search, law_consolidated, exchange_rate]
