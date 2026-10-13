"""FastMCP server exposing Lithuanian government open data.

Run:
    python -m mcp_server --transport http   # streamable HTTP on :8000/mcp (+ /health)
    python -m mcp_server --transport stdio  # local clients (Claude Desktop, Cursor, ...)
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

from mcp_server import __version__, companies, laws, rates, web
from mcp_server.config import mcp_settings
from mcp_server.sources import TOOL_FUNCS

INSTRUCTIONS = """Lithuanian government open data, served by lietuva.chat, an independent project
(not a government service). Tools return JSON envelopes with source_name, source_url, licence,
retrieved_at and data. Always cite source_url (for laws, the e-TAR url) when you use a result.
Covers: the Legal Entities Register (JAR) and VMI taxpayer and taxes-paid data, the Register of
Legal Acts (TAR) with consolidated versions, Bank of Lithuania euro rates, and web search limited
to official Lithuanian sites. Company codes only: personal codes are never accepted."""

mcp = FastMCP(
    "lietuva-gov",
    instructions=INSTRUCTIONS,
    website_url="https://lietuva.chat",
    stateless_http=True,
    json_response=True,
    streamable_http_path="/mcp",
    # Public, cookie-less server behind a reverse proxy, so the DNS-rebinding guard is not needed.
    transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False),
)

RO = {"readOnlyHint": True, "openWorldHint": True}
Env = dict[str, Any]
CompanyCode = Annotated[str, Field(description="Lithuanian company code (juridinio asmens kodas), 7–9 digits, "
                                               "e.g. 302767152")]


@mcp.tool(annotations=RO)
async def company_search(
    query: Annotated[str, Field(description="Company name or part of it (any case), or a company code",
                                min_length=2, max_length=100)],
    limit: Annotated[int, Field(ge=1, le=25)] = 10,
) -> Env:
    """Search the Lithuanian Legal Entities Register (JAR) by name or company code. Active companies first."""
    return await companies.company_search(query, limit)


@mcp.tool(annotations=RO)
async def company_details(company_code: CompanyCode) -> Env:
    """Company details from JAR and VMI open data: legal form, legal status, registration and
    deregistration dates, VAT (PVM) number and VAT registration dates."""
    return await companies.company_details(company_code)


@mcp.tool(annotations=RO)
async def company_tax_data(company_code: CompanyCode) -> Env:
    """Taxes paid by a company as published by the State Tax Inspectorate (VMI), latest periods first."""
    return await companies.company_tax_data(company_code)


@mcp.tool(annotations=RO)
async def law_search(
    query: Annotated[str, Field(description="Words from the act title in Lithuanian, "
                                            "e.g. 'gyventojų pajamų mokesčio įstatymas'", max_length=100)],
    only_in_force: Annotated[bool, Field(description="Only acts currently in force")] = True,
    limit: Annotated[int, Field(ge=1, le=25)] = 10,
) -> Env:
    """Search the Register of Legal Acts (TAR) by title. Base acts rank above their amending acts."""
    return await laws.law_search(query, only_in_force, limit)


@mcp.tool(annotations=RO)
async def law_consolidated(
    document_id: Annotated[str, Field(description="document_id from law_search, e.g. TAR.C677663D2202")],
    on_date: Annotated[str | None, Field(description="YYYY-MM-DD; defaults to today")] = None,
) -> Env:
    """The consolidated version (suvestinė redakcija) of a legal act in force on a date, with its e-TAR link."""
    return await laws.law_consolidated(document_id, on_date)


@mcp.tool(annotations=RO)
async def exchange_rate(
    currency: Annotated[str | None, Field(description="ISO code, e.g. 'USD'. Omit for all rates.")] = None,
) -> Env:
    """Latest euro reference exchange rates published by the Bank of Lithuania."""
    return await rates.exchange_rate(currency)


@mcp.tool(annotations=RO)
async def gov_web_search(
    query: Annotated[str, Field(min_length=2, max_length=300)],
    max_results: Annotated[int, Field(ge=1, le=15)] = 6,
) -> Env:
    """Web search over official Lithuanian government websites (Exa). Use when no structured tool fits."""
    return await web.gov_web_search(query, max_results)


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"status": "ok", "version": __version__, "tools": len(TOOL_FUNCS)})


@mcp.custom_route("/", methods=["GET"])
async def index(_: Request) -> JSONResponse:
    return JSONResponse({"name": "lietuva-gov MCP server", "version": __version__, "mcp_endpoint": "/mcp",
                         "docs": "https://github.com/predictivelabsai/lietuva-chat/blob/main/docs/mcp_server.md"})


def http_app():
    from mcp_server.auth import AuthRateLimitMiddleware
    return AuthRateLimitMiddleware(mcp.streamable_http_app(), mcp_settings())


def run(transport: str = "http") -> None:
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if transport == "stdio":
        mcp.run("stdio")
        return
    import uvicorn
    s = mcp_settings()
    uvicorn.run(http_app(), host=s.host, port=s.port)
