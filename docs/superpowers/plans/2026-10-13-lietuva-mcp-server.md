# lietuva.chat MCP Server Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish Lithuanian government open data (company register, VAT and taxes paid, legal acts, Bank of Lithuania rates, official-site search) as read-only MCP tools, and give the Business and Tax assistants the same tools.

**Architecture:** A `mcp_server/` package mirrors eesti-chat's server (FastMCP, envelope results, per-source politeness, TTL cache, API-key and rate-limit middleware). Unlike eesti, the registers are queried live on `get.data.gov.lt` (Spinta/UAPI answers filtered queries in 0.2–0.8 s), so there is no bulk SQLite mirror. `tools/mcp_tools.py` wraps the tools for LangChain: remote over streamable HTTP when `LIETUVA_MCP_URL` is set, otherwise it calls the same functions in-process.

**Tech Stack:** Python 3.14, `mcp>=1.20,<2` (FastMCP; 1.30.0 verified), httpx 0.28, cachetools 7.2, pytest + pytest-asyncio 1.0 (`asyncio_mode = auto`), LangChain `StructuredTool`.

**Spec:** No separate spec. The source of truth is (a) eesti-chat `docs/mcp_server.md` at commit `8177263`, which this mirrors, and (b) the **Verified upstream facts** section below, recorded from live calls on 2026-10-13.

## Verified upstream facts (live, 2026-10-13)

| Source | Endpoint / model | Notes |
|---|---|---|
| JAR companies | `https://get.data.gov.lt/datasets/gov/rc/jar/iregistruoti/JuridinisAsmuo` | Fields `ja_kodas` (int), `ja_pavadinimas`, `reg_data`, `isreg_data` (null = active), `forma._id`, `statusas._id`. Includes deregistered companies. |
| JAR legal forms / statuses | `…/rc/jar/formos_statusai/Forma`, `…/Statusas` | Look up by `_id="<uuid>"`; fields `kodas`, `pavadinimas` (LT), `name` (EN). |
| VMI taxpayer register | `…/vmi/mm_registras/MokesciuMoketojas` | Filter `ja_kodas=<int>`. VAT: `pvm_kodas_pref` + `pvm_kodas`, `pvm_iregistruota`, `pvm_isregistruota`. Several rows per company (one per taxpayer type), same VAT data. |
| VMI taxes paid | `…/vmi/ja_mokesciai/Moketojas` | `mm_kodas` references the JAR row, so `mm_kodas.ja_kodas=<int>` filters by company code. Fields `metai`, `menuo`, `suma`, `atnaujinta`. Semantics of `suma` (looks year-to-date: 21.06 M for 2026-08 against 21.27 M for 2025-12) are **not confirmed**. Report as published. |
| TAR legal acts | `…/lrsk/teises_aktai/Dokumentas` | `dokumento_id`, `pavadinimas`, `rusis`, `tar_kodas`, `priimtas`, `isigalioja`, `galioj_busena` (`galioja` / `negalioja`), `nuoroda` (e-tar.lt URL). `tekstas_lt` is the full text: never select it. |
| TAR consolidated versions | `…/lrsk/teises_aktai/Suvestine` | `dokumento_id`, `suvestines_id`, `nuoroda`, `galioja_nuo`, `galioja_iki` (null = current). `galioja_nuo<="YYYY-MM-DD"` + `sort(-galioja_nuo)` + `limit(1)` gives the version in force on a date. |
| Bank of Lithuania FX | `https://www.lb.lt/webservices/FxRates/FxRates.asmx/getCurrentFxRates?tp=EU` | XML, namespace `http://www.lb.lt/WebServices/FxRates`; one `<FxRate>` per currency (`<Dt>`, EUR=1 + the currency). 85 currencies. |
| Exa | `https://api.exa.ai/search` | Same domain list as `tools/search.py` `OFFICIAL_DOMAINS`. |

UAPI query rules, all confirmed live:
- `field.contains("x")` is **case-sensitive**. `field.lower().contains("x")` is not, so lowercase the user's text and use `lower()`.
- Non-ASCII literals must be percent-encoded, or the server returns nothing.
- `select(a,b)`, `sort(-a,-b)`, `limit(n)` and `=`, `<=` comparisons work. `limit(0)` is an error.
- A substring search on titles returns amending acts ("…pakeitimo įstatymas") ahead of the base act, so ranking happens on our side.

Out of scope for this plan, with reasons:
- **Statistics Lithuania:** SDMX only, and the dataflow list alone is 7 MB.
- **Address register:** a readable address needs a chain of lookups across several models.
- **Procurement (vpt):** dozens of form models.
- **Weather (api.meteo.lt):** CC BY-SA 4.0 and 180 requests/min/IP, but no assistant needs it.
- **atvira.sodra.lt:** returned 403 to automated requests.

## Global Constraints

- No AI attribution anywhere: no `Co-Authored-By` trailers, no "Generated with" lines in commits, PRs or docs.
- Every pushed change bumps `VERSION` (line 1 semver, line 2 `date -u +%Y-%m-%d`) and prepends a `docs/change_log.md` entry. This plan ships as **v1.2.0**.
- lietuva.chat is independent. Server instructions and docs must never call it official or government-run.
- Never accept, look up or log a personal code (asmens kodas, 11 digits). Company codes are 7–9 digits; anything else is refused before any upstream call.
- Every tool is read-only (`readOnlyHint: True`) and returns the envelope `{source_name, source_url, licence, retrieved_at, cached, data}`.
- User text reaches a UAPI query only through `clean_text()` (letters, digits, spaces, `-.,'„“`) or a strict validator. Never interpolate raw input.
- `User-Agent: lietuva.chat-mcp/0.1 (+https://lietuva.chat)` on every upstream call.
- Tests use no network and no module patching. Upstreams are faked through the injected transport seam `core.set_transport(httpx.MockTransport(...))`.
- Work on branch `feat/mcp-server` cut from `main`. Do not push or open a PR unless the user asks.

## Review Focus

1. **Query syntax inside user text** (`vinted")&limit(1000`) must not reach Spinta as operators. → Task 1 `test_clean_text_strips_query_syntax`, Task 3 `test_company_search_cannot_inject_operators`.
2. **A personal code (11 digits) given as a company code** is refused with no upstream call. → Task 3 `test_personal_code_is_refused_without_a_call`.
3. **Upstream 4xx/5xx** turns into a tool error that tells the agent to fall back to `web_search`, never a crash. → Task 1 `test_fetch_retries_5xx_then_raises`, Task 6 `test_tool_errors_tell_the_agent_to_fall_back`.
4. **Uppercase Lithuanian input** ("GYVENTOJŲ PAJAMŲ") still matches, because it is lowercased before `lower().contains`. → Task 4 `test_law_search_lowercases_lithuanian_input`.
5. **A company with no VMI record** returns `vat_number: None` instead of failing. → Task 3 `test_company_details_without_vat_record`.

---

## File structure

| File | Responsibility | Task |
|---|---|---|
| `pytest.ini` | `asyncio_mode = auto` | 1 |
| `requirements.txt` | add `mcp`, `cachetools` | 1 |
| `mcp_server/__init__.py` | package docstring, `__version__` | 1 |
| `mcp_server/config.py` | `MCPSettings` from env | 1 |
| `mcp_server/core.py` | sources, envelope, politeness limiter, HTTP client + transport seam, retry fetch, TTL cache | 1 |
| `mcp_server/uapi.py` | safe UAPI query building + row fetch | 1 |
| `tests/test_mcp_core.py` | core + uapi tests | 1 |
| `tests/mcp_upstream.py`, `tests/conftest.py` | fake upstream + `mcp_upstream` fixture | 2 |
| `tests/mcp_fixtures/*` | recorded responses | 2 |
| `mcp_server/companies.py` + `tests/test_mcp_companies.py` | company_search, company_details, company_tax_data | 3 |
| `mcp_server/laws.py` + `tests/test_mcp_laws.py` | law_search, law_consolidated | 4 |
| `mcp_server/rates.py`, `mcp_server/web.py` + `tests/test_mcp_rates_web.py` | exchange_rate, gov_web_search | 4 |
| `mcp_server/sources.py`, `server.py`, `auth.py`, `keys.py`, `__main__.py` + `tests/test_mcp_server.py`, `tests/test_mcp_auth.py` | registry, FastMCP app, auth, CLI | 5 |
| `tools/mcp_tools.py`, `agents/business/eresidency.py`, `agents/living/tax.py`, `prompts/system/eresidency.md`, `prompts/system/tax.md` + `tests/test_mcp_tools.py` | chat integration | 6 |
| `Dockerfile.mcp`, `docker-compose.mcp.yaml`, `requirements-mcp.txt`, `.env.example`, `docs/mcp_server.md`, `tests/test_mcp_live.py`, `VERSION`, `docs/change_log.md` | ship | 7 |

Dependency order: Tasks 1 and 2 can run in parallel. Tasks 3 and 4 need both and can run in parallel with each other (separate files). Task 5 needs 3 and 4. Task 6 needs 5. Task 7 needs 6.

---

### Task 0: Branch

- [ ] **Step 1: Cut the branch**

```bash
cd /Users/karl/orca/lietuva-chat
git switch main && git pull --ff-only
git switch -c feat/mcp-server
```

Expected: `Switched to a new branch 'feat/mcp-server'`.

---

### Task 1: Core plumbing and the UAPI query builder

**Files:**
- Create: `pytest.ini`, `mcp_server/__init__.py`, `mcp_server/config.py`, `mcp_server/core.py`, `mcp_server/uapi.py`, `tests/test_mcp_core.py`
- Modify: `requirements.txt`

**Interfaces:**
- Produces:
  - `core.SOURCES: dict[str, Source]` with keys `"jar"`, `"vmi"`, `"tar"`, `"lb"`, `"exa"`;
  - `core.envelope(source: str, source_url: str, data, *, cached=False, **extra) -> dict`;
  - `core.fetch(source: str, method: str, url: str, *, retries=2, **kw) -> httpx.Response` (raises `core.UpstreamError`);
  - `core.cached(key_parts: tuple, ttl_s: int, producer) -> dict`;
  - `core.set_transport(transport: httpx.AsyncBaseTransport | None) -> None`;
  - `core.reset() -> None`;
  - `config.mcp_settings() -> MCPSettings` (lru_cached);
  - `uapi.BASE`, `uapi.clean_text(s: str, *, min_len=2, max_len=100) -> str`, `uapi.lit(s: str) -> str`, `uapi.build_url(model: str, *filters: str, select=(), sort=(), limit=10) -> str`, `uapi.rows(source: str, url: str) -> list[dict]`.

- [ ] **Step 1: Add dependencies and pytest config**

Append to `requirements.txt`:

```text
# --- MCP server (mcp_server/) and MCP-backed agent tools ---
mcp>=1.20,<2
cachetools==7.2.1
```

Create `pytest.ini`:

```ini
[pytest]
asyncio_mode = auto
```

Run: `.venv/bin/pip install -r requirements.txt`
Expected: installs `mcp-1.x` and `cachetools-7.2.1` without errors.

- [ ] **Step 2: Write the failing tests**

Create `tests/test_mcp_core.py`:

```python
"""MCP core: safe UAPI queries, envelope, cache, retries. No network."""

from __future__ import annotations

from urllib.parse import unquote

import httpx
import pytest

from mcp_server import core, uapi
from mcp_server.config import MCPSettings


@pytest.fixture(autouse=True)
def _fresh():
    core.reset()
    yield
    core.set_transport(None)
    core.reset()


def test_clean_text_strips_query_syntax():
    assert uapi.clean_text('vinted")&limit(1000') == "vinted limit 1000"
    assert uapi.clean_text("  Gyventojų   pajamų „mokesčio“ ") == "Gyventojų pajamų „mokesčio“"


@pytest.mark.parametrize("bad", ["", " ", "!!", '")('])
def test_clean_text_refuses_empty_queries(bad):
    with pytest.raises(ValueError):
        uapi.clean_text(bad)


def test_clean_text_caps_length():
    assert len(uapi.clean_text("a" * 500)) == 100


def test_build_url_encodes_lithuanian_and_keeps_operators():
    url = uapi.build_url("datasets/gov/lrsk/teises_aktai/Dokumentas",
                         f'pavadinimas.lower().contains({uapi.lit("užsieniečių")})',
                         f'galioj_busena={uapi.lit("galioja")}',
                         select=("pavadinimas", "nuoroda"), sort=("-priimtas",), limit=5)
    assert " " not in url and "ž" not in url
    assert unquote(url) == (
        "https://get.data.gov.lt/datasets/gov/lrsk/teises_aktai/Dokumentas?"
        'pavadinimas.lower().contains("užsieniečių")&galioj_busena="galioja"'
        "&select(pavadinimas,nuoroda)&sort(-priimtas)&limit(5)")


def test_envelope_has_citation_fields():
    env = core.envelope("tar", "https://example/x", {"a": 1}, extra_field=2)
    assert {"source_name", "source_url", "licence", "retrieved_at", "cached", "data"} <= set(env)
    assert env["cached"] is False and env["extra_field"] == 2


async def test_cached_returns_hit_flagged_as_cached():
    calls = []

    async def produce():
        calls.append(1)
        return core.envelope("lb", "https://example/fx", {"x": 1})

    first = await core.cached(("k",), 60, produce)
    second = await core.cached(("k",), 60, produce)
    assert first["cached"] is False and second["cached"] is True and len(calls) == 1


async def test_fetch_retries_5xx_then_raises():
    hits = []

    def handler(request):
        hits.append(request)
        return httpx.Response(503)

    core.set_transport(httpx.MockTransport(handler))
    with pytest.raises(core.UpstreamError, match="HTTP 503"):
        await core.fetch("lb", "GET", "https://www.lb.lt/x")
    assert len(hits) == 3


async def test_fetch_does_not_retry_4xx():
    hits = []
    core.set_transport(httpx.MockTransport(lambda r: hits.append(r) or httpx.Response(404)))
    with pytest.raises(core.UpstreamError, match="HTTP 404"):
        await core.fetch("lb", "GET", "https://www.lb.lt/x")
    assert len(hits) == 1


async def test_fetch_sends_the_lietuva_user_agent():
    seen = []
    core.set_transport(httpx.MockTransport(lambda r: seen.append(r) or httpx.Response(200, json={})))
    await core.fetch("lb", "GET", "https://www.lb.lt/x")
    assert seen[0].headers["user-agent"].startswith("lietuva.chat-mcp/")


async def test_rows_returns_data_list():
    core.set_transport(httpx.MockTransport(lambda r: httpx.Response(200, json={"_data": [{"a": 1}]})))
    assert await uapi.rows("jar", uapi.BASE + "x?limit(1)") == [{"a": 1}]


def test_settings_defaults(monkeypatch):
    for name in ("MCP_ANON_RPM", "MCP_API_KEY_HASHES"):
        monkeypatch.delenv(name, raising=False)
    s = MCPSettings()
    assert s.anon_rpm == 30 and s.key_rpm == 300 and s.api_key_hashes == frozenset()
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_mcp_core.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'mcp_server'`.

- [ ] **Step 4: Implement the package**

Create `mcp_server/__init__.py`:

```python
"""lietuva.chat MCP server: Lithuanian government open data as MCP tools."""

__version__ = "0.1.0"
```

Create `mcp_server/config.py`:

```python
"""MCP server configuration (env vars, all optional)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache


def _int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


@dataclass(frozen=True)
class MCPSettings:
    host: str = field(default_factory=lambda: os.environ.get("MCP_HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: _int("MCP_PORT", 8000))
    # Comma-separated sha256 hex digests of issued API keys (never store raw keys).
    api_key_hashes: frozenset[str] = field(default_factory=lambda: frozenset(
        h.strip().lower() for h in os.environ.get("MCP_API_KEY_HASHES", "").split(",") if h.strip()))
    anon_rpm: int = field(default_factory=lambda: _int("MCP_ANON_RPM", 30))
    anon_rpd: int = field(default_factory=lambda: _int("MCP_ANON_RPD", 500))
    key_rpm: int = field(default_factory=lambda: _int("MCP_KEY_RPM", 300))
    key_rpd: int = field(default_factory=lambda: _int("MCP_KEY_RPD", 20000))
    exa_api_key: str = field(default_factory=lambda: os.environ.get("EXA_API_KEY", ""))
    user_agent: str = field(default_factory=lambda: os.environ.get(
        "MCP_USER_AGENT", "lietuva.chat-mcp/0.1 (+https://lietuva.chat)"))
    trust_proxy: bool = field(default_factory=lambda: os.environ.get("MCP_TRUST_PROXY", "1") == "1")


@lru_cache(maxsize=1)
def mcp_settings() -> MCPSettings:
    return MCPSettings()
```

Create `mcp_server/core.py`:

```python
"""Shared plumbing: HTTP client, per-source politeness, TTL cache, result envelope."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

import httpx
from cachetools import TTLCache

from mcp_server.config import mcp_settings


@dataclass(frozen=True)
class Source:
    key: str
    name: str
    licence: str
    min_interval_s: float  # minimum seconds between our calls to this upstream
    home: str


SOURCES: dict[str, Source] = {s.key: s for s in [
    Source("jar", "Registrų centras – Legal Entities Register (JAR), via data.gov.lt",
           "Open data on data.gov.lt; see the dataset page for its licence", 0.2,
           "https://data.gov.lt/datasets/1484/"),
    Source("vmi", "State Tax Inspectorate (VMI), via data.gov.lt",
           "Open data on data.gov.lt (taxes-paid dataset: CC BY 4.0)", 0.2,
           "https://data.gov.lt/datasets/673/"),
    Source("tar", "Register of Legal Acts (TAR), via data.gov.lt",
           "Legal acts are not protected by copyright (Law on Copyright and Related Rights, Art. 5)", 0.2,
           "https://data.gov.lt/datasets/2613/"),
    Source("lb", "Bank of Lithuania (Lietuvos bankas) euro reference rates",
           "Published by Lietuvos bankas; attribute the source", 0.5, "https://www.lb.lt"),
    Source("exa", "Exa web search (official Lithuanian domains)",
           "Third-party search results; see each URL", 0.1, "https://exa.ai"),
]}


class UpstreamError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def envelope(source: str, source_url: str, data: Any, *, cached: bool = False, **extra: Any) -> dict:
    src = SOURCES[source]
    out = {
        "source_name": src.name,
        "source_url": source_url,
        "licence": src.licence,
        "retrieved_at": now_iso(),
        "cached": cached,
        "data": data,
    }
    out.update(extra)
    return out


class _Limiter:
    def __init__(self, min_interval: float):
        self.min_interval = min_interval
        self._next = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            if self._next > now:
                await asyncio.sleep(self._next - now)
            self._next = max(now, self._next) + self.min_interval


_limiters: dict[str, _Limiter] = {}


def limiter(source: str) -> _Limiter:
    lim = _limiters.get(source)
    if lim is None:
        lim = _limiters[source] = _Limiter(SOURCES[source].min_interval_s)
    return lim


_client: httpx.AsyncClient | None = None
_transport: httpx.AsyncBaseTransport | None = None


def set_transport(transport: httpx.AsyncBaseTransport | None) -> None:
    """Route every upstream call through `transport` (tests pass an httpx.MockTransport)."""
    global _transport, _client
    _transport, _client = transport, None


def client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(
            timeout=httpx.Timeout(25.0, connect=10.0),
            follow_redirects=True,
            headers={"User-Agent": mcp_settings().user_agent},
            transport=_transport,
        )
    return _client


async def fetch(source: str, method: str, url: str, *, retries: int = 2, **kw) -> httpx.Response:
    """Polite request with retry and backoff on 429/5xx and transport errors."""
    last: Exception | None = None
    for attempt in range(retries + 1):
        await limiter(source).wait()
        try:
            r = await client().request(method, url, **kw)
            if r.status_code == 429 or r.status_code >= 500:
                last = UpstreamError(f"{SOURCES[source].name} returned HTTP {r.status_code}")
            elif r.status_code >= 400:
                raise UpstreamError(f"{SOURCES[source].name} returned HTTP {r.status_code}")
            else:
                return r
        except httpx.HTTPError as e:
            last = UpstreamError(f"{SOURCES[source].name} unreachable: {e.__class__.__name__}")
        if attempt < retries:
            await asyncio.sleep(0.5 * 2 ** attempt)
    raise last or UpstreamError("upstream error")


_cache: TTLCache = TTLCache(maxsize=4096, ttl=30 * 24 * 3600)
_cache_exp: dict[str, float] = {}


def reset() -> None:
    """Forget the HTTP client, cached results and limiters (used by tests)."""
    global _client
    _client = None
    _cache.clear()
    _cache_exp.clear()
    _limiters.clear()


async def cached(key_parts: tuple, ttl_s: int, producer: Callable[[], Awaitable[dict]]) -> dict:
    """Cache a result dict for ttl_s seconds; a cache hit comes back with cached=True."""
    key = hashlib.sha256(json.dumps(key_parts, sort_keys=True, default=str).encode()).hexdigest()
    hit = _cache.get(key)
    if hit is not None and _cache_exp.get(key, 0) > time.time():
        return {**hit, "cached": True}
    val = await producer()
    _cache[key] = val
    _cache_exp[key] = time.time() + ttl_s
    return val
```

Create `mcp_server/uapi.py`:

```python
"""get.data.gov.lt (Spinta / UAPI): build a safe query URL and fetch its rows.

User text only enters a query through clean_text(), which leaves letters, digits, spaces
and - . , ' „ “ — so it can never close a "…" literal or add & ( ) operators."""

from __future__ import annotations

import re
from urllib.parse import quote

from mcp_server.core import fetch

BASE = "https://get.data.gov.lt/"
_UNSAFE = re.compile(r"[^\w\s\-.,'„“]")


def clean_text(s: str, *, min_len: int = 2, max_len: int = 100) -> str:
    s = " ".join(_UNSAFE.sub(" ", s).split())
    if len(s) < min_len:
        raise ValueError(f"The search text needs at least {min_len} letters or digits.")
    return s[:max_len]


def lit(s: str) -> str:
    return f'"{s}"'


def build_url(model: str, *filters: str, select: tuple[str, ...] = (), sort: tuple[str, ...] = (),
              limit: int = 10) -> str:
    parts = list(filters)
    if select:
        parts.append(f"select({','.join(select)})")
    if sort:
        parts.append(f"sort({','.join(sort)})")
    parts.append(f"limit({limit})")
    # Non-ASCII must be percent-encoded or get.data.gov.lt matches nothing.
    return BASE + model + "?" + quote("&".join(parts), safe="/:()=&,\"<>*")


async def rows(source: str, url: str) -> list[dict]:
    r = await fetch(source, "GET", url)
    return r.json().get("_data") or []
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_mcp_core.py -q`
Expected: `14 passed` (the retry test takes about 1.5 s).

- [ ] **Step 6: Run the whole suite**

Run: `.venv/bin/python -m pytest -q --ignore=tests/test_api.py`
Expected: all pass. The earlier count was 496 passed and 1 skipped, so the new count is 496 + 14.

- [ ] **Step 7: Commit**

```bash
git add requirements.txt pytest.ini mcp_server/ tests/test_mcp_core.py
git commit -m "feat(mcp): core plumbing and safe get.data.gov.lt query builder"
```

---

### Task 2: Recorded fixtures and the fake upstream

**Files:**
- Create: `tests/mcp_upstream.py`, `tests/mcp_fixtures/` (11 files)
- Modify: `tests/conftest.py`

**Interfaces:**
- Consumes: `core.set_transport`, `core.reset`, `config.mcp_settings` (Task 1). If Task 1 isn't merged yet, the fixture still imports lazily, so this task can land first.
- Produces:
  - the pytest fixture `mcp_upstream`, a callable taking `{url substring: fixture filename | HTTP status int}` and returning an `Upstream` with `.requests: list[httpx.Request]` and `.urls: list[str]` (decoded);
  - fixture files named exactly as below.

All fixture data below is real, recorded from the live APIs on 2026-10-13 and trimmed. The exception is `exa.json`, which is hand-written because it fakes a third-party API.

- [ ] **Step 1: Create the fixture files**

`tests/mcp_fixtures/jar_search.json`:

```json
{"_data": [{"ja_kodas": 302767152, "ja_pavadinimas": "Vinted, UAB", "reg_data": "2012-04-23", "isreg_data": null}, {"ja_kodas": 305305400, "ja_pavadinimas": "Vinted Systems, UAB", "reg_data": "2019-10-28", "isreg_data": "2026-04-24"}, {"ja_kodas": 305959706, "ja_pavadinimas": "Vinted Go, UAB", "reg_data": "2021-12-20", "isreg_data": null}]}
```

`tests/mcp_fixtures/jar_one.json`:

```json
{"_data": [{"ja_kodas": 302767152, "ja_pavadinimas": "Vinted, UAB", "reg_data": "2012-04-23", "isreg_data": null, "forma": {"_id": "5c444113-5081-4d88-b94d-782c0779bb89"}, "statusas": {"_id": "5ef6b364-a5ff-47fb-8600-ff859214ef85"}}]}
```

`tests/mcp_fixtures/forma_uab.json`:

```json
{"_data": [{"kodas": 310, "pavadinimas": "Uždaroji akcinė bendrovė", "name": "Private Limited Liability Company"}]}
```

`tests/mcp_fixtures/statusas_ok.json`:

```json
{"_data": [{"kodas": 0, "pavadinimas": "Teisinis statusas neįregistruotas", "name": "No legal proceedings"}]}
```

`tests/mcp_fixtures/vmi_mm.json`:

```json
{"_data": [{"pvm_kodas_pref": "LT", "pvm_kodas": "100006918914", "pvm_iregistruota": "2012-06-19", "pvm_isregistruota": null}, {"pvm_kodas_pref": "LT", "pvm_kodas": "100006918914", "pvm_iregistruota": "2012-06-19", "pvm_isregistruota": null}]}
```

`tests/mcp_fixtures/vmi_tax.json`:

```json
{"_data": [{"pavadinimas": "Vinted, UAB", "metai": 2026, "menuo": 8, "suma": 21059261.66, "atnaujinta": "2026-09-11"}, {"pavadinimas": "Vinted, UAB", "metai": 2025, "menuo": 12, "suma": 21266813.83, "atnaujinta": "2026-01-09"}, {"pavadinimas": "Vinted, UAB", "metai": 2024, "menuo": 12, "suma": 18541853.16, "atnaujinta": "2025-01-15"}]}
```

`tests/mcp_fixtures/tar_aliens.json` (deliberately in the "wrong" order: amendment, implementing act, then base act):

```json
{"_data": [{"dokumento_id": "0968a7e0868a11e481c9c95e73113964", "pavadinimas": "Lietuvos Respublikos įstatymo „Dėl užsieniečių teisinės padėties“ Nr. IX-2206 pakeitimo įstatymas", "rusis": "Įstatymas", "tar_kodas": "2014-19923", "priimtas": "2014-12-09", "isigalioja": "2015-03-01", "galioj_busena": "galioja", "nuoroda": "https://e-tar.lt/portal/lt/legalAct/0968a7e0868a11e481c9c95e73113964"}, {"dokumento_id": "TAR.CCBCFBD70E83", "pavadinimas": "Lietuvos Respublikos įstatymo \"Dėl užsieniečių teisinės padėties\" įgyvendinimo įstatymas", "rusis": "Įstatymas", "tar_kodas": "1041010ISTA0IX-2207", "priimtas": "2004-04-29", "isigalioja": "2004-04-30", "galioj_busena": "galioja", "nuoroda": "https://e-tar.lt/portal/lt/legalAct/TAR.CCBCFBD70E83"}, {"dokumento_id": "TAR.42837E5A79DD", "pavadinimas": "Lietuvos Respublikos įstatymas dėl užsieniečių teisinės padėties", "rusis": "Įstatymas", "tar_kodas": "1041010ISTA0IX-2206", "priimtas": "2004-04-29", "isigalioja": "2004-04-30", "galioj_busena": "galioja", "nuoroda": "https://e-tar.lt/portal/lt/legalAct/TAR.42837E5A79DD"}]}
```

`tests/mcp_fixtures/tar_suvestine.json`:

```json
{"_data": [{"suvestines_id": "hhPqGFmNta", "nuoroda": "https://e-tar.lt/portal/lt/legalAct/TAR.C677663D2202/hhPqGFmNta", "galioja_nuo": "2025-01-02T00:00:00", "galioja_iki": null}]}
```

`tests/mcp_fixtures/empty.json`:

```json
{"_data": []}
```

`tests/mcp_fixtures/lb_fx.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<FxRates xmlns="http://www.lb.lt/WebServices/FxRates">
  <FxRate>
    <Tp>EU</Tp>
    <Dt>2026-10-12</Dt>
    <CcyAmt>
      <Ccy>EUR</Ccy>
      <Amt>1</Amt>
    </CcyAmt>
    <CcyAmt>
      <Ccy>GBP</Ccy>
      <Amt>0.844780</Amt>
    </CcyAmt>
  </FxRate>
  <FxRate>
    <Tp>EU</Tp>
    <Dt>2026-10-12</Dt>
    <CcyAmt>
      <Ccy>EUR</Ccy>
      <Amt>1</Amt>
    </CcyAmt>
    <CcyAmt>
      <Ccy>PLN</Ccy>
      <Amt>4.3850</Amt>
    </CcyAmt>
  </FxRate>
  <FxRate>
    <Tp>EU</Tp>
    <Dt>2026-10-12</Dt>
    <CcyAmt>
      <Ccy>EUR</Ccy>
      <Amt>1</Amt>
    </CcyAmt>
    <CcyAmt>
      <Ccy>USD</Ccy>
      <Amt>1.1181</Amt>
    </CcyAmt>
  </FxRate>
</FxRates>
```

`tests/mcp_fixtures/exa.json` (hand-written):

```json
{"results": [{"title": "Gyventojų pajamų mokestis", "url": "https://www.vmi.lt/evmi/gyventoju-pajamu-mokestis", "publishedDate": null, "highlights": ["GPM tarifai ir deklaravimas."], "text": "Gyventojų pajamų mokesčio tarifai, lengvatos ir deklaravimas."}]}
```

- [ ] **Step 2: Create the fake upstream**

`tests/mcp_upstream.py`:

```python
"""Fake upstream for MCP tool tests: serves recorded responses through httpx.MockTransport."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote

import httpx

FIXTURES = Path(__file__).parent / "mcp_fixtures"


class Upstream:
    """Answers each request with the first route whose key is a substring of the decoded URL.
    A route value is a fixture filename (200) or an int status. Unmatched URLs get 404."""

    def __init__(self, routes: dict[str, str | int]):
        self.routes = routes
        self.requests: list[httpx.Request] = []

    @property
    def urls(self) -> list[str]:
        return [unquote(str(r.url)) for r in self.requests]

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        url = unquote(str(request.url))
        for needle, answer in self.routes.items():
            if needle in url:
                if isinstance(answer, int):
                    return httpx.Response(answer)
                return httpx.Response(200, content=(FIXTURES / answer).read_bytes())
        return httpx.Response(404, json={"errors": [{"message": f"no fixture for {url}"}]})
```

- [ ] **Step 3: Add the fixture to `tests/conftest.py`**

Add `import pytest` to the imports at the top, then append:

```python
@pytest.fixture
def mcp_upstream(monkeypatch):
    """Point the MCP server's HTTP client at recorded responses.
    Call it with {url substring: fixture file or status}; it returns the Upstream."""
    import httpx

    from mcp_server import config, core
    from tests.mcp_upstream import Upstream

    monkeypatch.delenv("EXA_API_KEY", raising=False)
    monkeypatch.delenv("LIETUVA_MCP_URL", raising=False)
    config.mcp_settings.cache_clear()
    core.reset()

    def install(routes):
        fake = Upstream(routes)
        core.set_transport(httpx.MockTransport(fake))
        return fake

    yield install
    core.set_transport(None)
    core.reset()
    config.mcp_settings.cache_clear()
```

- [ ] **Step 4: Verify the fixtures parse and the suite still collects**

Run:

```bash
.venv/bin/python -c "import json,glob; [json.load(open(f)) for f in glob.glob('tests/mcp_fixtures/*.json')]; import xml.etree.ElementTree as E; E.parse('tests/mcp_fixtures/lb_fx.xml'); print('ok')"
.venv/bin/python -m pytest -q --ignore=tests/test_api.py
```

Expected: `ok`, then the same pass count as before this task.

- [ ] **Step 5: Commit**

```bash
git add tests/mcp_upstream.py tests/mcp_fixtures/ tests/conftest.py
git commit -m "test(mcp): recorded upstream fixtures and fake transport"
```

---

### Task 3: Company tools (JAR + VMI)

**Files:**
- Create: `mcp_server/companies.py`, `tests/test_mcp_companies.py`

**Interfaces:**
- Consumes: `uapi.build_url`, `uapi.clean_text`, `uapi.lit`, `uapi.rows`, `core.cached`, `core.envelope` (Task 1); `mcp_upstream` and fixtures (Task 2).
- Produces (the parameter names are the tool argument names and must not change):
  - `async def company_search(query: str, limit: int = 10) -> dict`
  - `async def company_details(company_code: str) -> dict`
  - `async def company_tax_data(company_code: str) -> dict`

  `data` shapes:
  - `company_search`: `list[{company_code, name, registered, deregistered, active}]`, active companies first.
  - `company_details`: `{company_code, name, legal_form, legal_form_en, legal_status, legal_status_en, registered, deregistered, active, vat_number, vat_registered, vat_deregistered}`, plus the envelope extra `vat_source_url`.
  - `company_tax_data`: `{company_code, name, periods: [{year, month, taxes_paid_eur, updated}], note}`.

- [ ] **Step 1: Write the failing tests**

`tests/test_mcp_companies.py`:

```python
"""Company tools against recorded JAR / VMI responses."""

from __future__ import annotations

import pytest

from mcp_server import companies
from mcp_server.core import UpstreamError

ENVELOPE = {"source_name", "source_url", "licence", "retrieved_at", "cached", "data"}
SEARCH = 'JuridinisAsmuo?ja_pavadinimas.lower().contains("vinted")'


async def test_company_search_lists_active_companies_first_and_caches(mcp_upstream):
    fake = mcp_upstream({SEARCH: "jar_search.json"})
    r = await companies.company_search("Vinted", 3)
    assert ENVELOPE <= set(r)
    assert [c["company_code"] for c in r["data"]] == ["302767152", "305959706", "305305400"]
    assert r["data"][-1]["active"] is False and r["data"][-1]["deregistered"] == "2026-04-24"
    again = await companies.company_search("VINTED", 3)
    assert again["cached"] is True and len(fake.requests) == 1


async def test_company_search_by_code(mcp_upstream):
    fake = mcp_upstream({"JuridinisAsmuo?ja_kodas=302767152": "jar_one.json"})
    r = await companies.company_search("302767152")
    assert r["data"][0]["name"] == "Vinted, UAB"
    assert "ja_kodas=302767152" in fake.urls[0]


async def test_company_search_cannot_inject_operators(mcp_upstream):
    fake = mcp_upstream({"JuridinisAsmuo": "empty.json"})
    await companies.company_search('vinted")&limit(1000')
    url = fake.urls[0]
    assert 'contains("vinted limit 1000")' in url and url.endswith("&limit(10)")


async def test_personal_code_is_refused_without_a_call(mcp_upstream):
    fake = mcp_upstream({})
    for call in (companies.company_details, companies.company_tax_data, companies.company_search):
        with pytest.raises(ValueError, match="7 to 9 digits"):
            await call("38001010000")
    assert fake.requests == []


async def test_company_details_combines_jar_and_vmi(mcp_upstream):
    mcp_upstream({
        "JuridinisAsmuo?ja_kodas=302767152": "jar_one.json",
        'Forma?_id="5c444113-5081-4d88-b94d-782c0779bb89"': "forma_uab.json",
        'Statusas?_id="5ef6b364-a5ff-47fb-8600-ff859214ef85"': "statusas_ok.json",
        "MokesciuMoketojas?ja_kodas=302767152": "vmi_mm.json",
    })
    r = await companies.company_details("302767152")
    d = r["data"]
    assert d["name"] == "Vinted, UAB" and d["active"] is True
    assert d["legal_form"] == "Uždaroji akcinė bendrovė"
    assert d["legal_form_en"] == "Private Limited Liability Company"
    assert d["legal_status_en"] == "No legal proceedings"
    assert d["vat_number"] == "LT100006918914" and d["vat_registered"] == "2012-06-19"
    assert r["vat_source_url"].startswith("https://get.data.gov.lt/")


async def test_company_details_without_vat_record(mcp_upstream):
    mcp_upstream({
        "JuridinisAsmuo?ja_kodas=302767152": "jar_one.json",
        "Forma?_id=": "forma_uab.json",
        "Statusas?_id=": "statusas_ok.json",
        "MokesciuMoketojas": "empty.json",
    })
    d = (await companies.company_details("302767152"))["data"]
    assert d["vat_number"] is None and d["vat_registered"] is None


async def test_company_details_unknown_code(mcp_upstream):
    mcp_upstream({"JuridinisAsmuo?ja_kodas=": "empty.json"})
    with pytest.raises(ValueError, match="No company with code 123456789"):
        await companies.company_details("123456789")


async def test_company_tax_data_latest_first(mcp_upstream):
    fake = mcp_upstream({"Moketojas?mm_kodas.ja_kodas=302767152": "vmi_tax.json"})
    d = (await companies.company_tax_data("302767152"))["data"]
    assert d["name"] == "Vinted, UAB"
    assert d["periods"][0] == {"year": 2026, "month": 8, "taxes_paid_eur": 21059261.66, "updated": "2026-09-11"}
    assert "as published" in d["note"]
    assert "sort(-metai,-menuo)" in fake.urls[0]


async def test_upstream_failure_raises_upstream_error(mcp_upstream):
    mcp_upstream({})  # every URL 404s
    with pytest.raises(UpstreamError):
        await companies.company_search("Vinted")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_mcp_companies.py -q`
Expected: `ImportError: cannot import name 'companies' from 'mcp_server'`.

- [ ] **Step 3: Implement `mcp_server/companies.py`**

```python
"""Company tools: Registrų centras JAR and VMI open data on get.data.gov.lt."""

from __future__ import annotations

import re

from mcp_server.core import cached, envelope
from mcp_server.uapi import build_url, clean_text, lit, rows

JAR = "datasets/gov/rc/jar/iregistruoti/JuridinisAsmuo"
FORMA = "datasets/gov/rc/jar/formos_statusai/Forma"
STATUSAS = "datasets/gov/rc/jar/formos_statusai/Statusas"
VMI_REG = "datasets/gov/vmi/mm_registras/MokesciuMoketojas"
VMI_TAX = "datasets/gov/vmi/ja_mokesciai/Moketojas"
DAY = 24 * 3600
_UUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
TAX_NOTE = ("Amounts as published by VMI in its taxes-paid-by-legal-entities dataset. How each period "
            "is totalled is defined at data.gov.lt/datasets/673 — do not call it a monthly figure.")


def _company_code(value: str) -> str:
    """Company codes have 7–9 digits. Anything else, including an 11-digit personal code, is refused."""
    v = value.strip()
    if not re.fullmatch(r"\d{7,9}", v):
        raise ValueError("A Lithuanian company code has 7 to 9 digits, e.g. 302767152. "
                         "Personal codes are never looked up.")
    return v


def parse_companies(data: list[dict]) -> list[dict]:
    out = [{
        "company_code": str(r["ja_kodas"]),
        "name": r.get("ja_pavadinimas"),
        "registered": r.get("reg_data"),
        "deregistered": r.get("isreg_data"),
        "active": r.get("isreg_data") is None,
    } for r in data]
    return sorted(out, key=lambda c: not c["active"])


def parse_company(row: dict, forma: dict, status: dict, vat_rows: list[dict]) -> dict:
    vat = next((v for v in vat_rows if v.get("pvm_kodas")), None)
    return {
        "company_code": str(row["ja_kodas"]),
        "name": row.get("ja_pavadinimas"),
        "legal_form": forma.get("pavadinimas"),
        "legal_form_en": forma.get("name"),
        "legal_status": status.get("pavadinimas"),
        "legal_status_en": status.get("name"),
        "registered": row.get("reg_data"),
        "deregistered": row.get("isreg_data"),
        "active": row.get("isreg_data") is None,
        "vat_number": f"{vat.get('pvm_kodas_pref') or ''}{vat['pvm_kodas']}" if vat else None,
        "vat_registered": vat.get("pvm_iregistruota") if vat else None,
        "vat_deregistered": vat.get("pvm_isregistruota") if vat else None,
    }


def parse_tax(data: list[dict]) -> list[dict]:
    return [{"year": r.get("metai"), "month": r.get("menuo"), "taxes_paid_eur": r.get("suma"),
             "updated": r.get("atnaujinta")} for r in data]


async def company_search(query: str, limit: int = 10) -> dict:
    limit = max(1, min(25, int(limit)))
    q = query.strip()
    if q.isdigit():
        flt = f"ja_kodas={_company_code(q)}"
    else:
        flt = f"ja_pavadinimas.lower().contains({lit(clean_text(q).lower())})"
    url = build_url(JAR, flt, select=("ja_kodas", "ja_pavadinimas", "reg_data", "isreg_data"), limit=limit)

    async def run():
        return envelope("jar", url, parse_companies(await rows("jar", url)))
    return await cached(("company_search", url), DAY, run)


async def _lookup(model: str, ref: dict | None) -> dict:
    rid = (ref or {}).get("_id") or ""
    if not _UUID.fullmatch(rid):
        return {}
    url = build_url(model, f"_id={lit(rid)}", select=("kodas", "pavadinimas", "name"), limit=1)

    async def run():
        found = await rows("jar", url)
        return {"row": found[0] if found else {}}
    return (await cached(("lookup", url), 7 * DAY, run))["row"]


async def company_details(company_code: str) -> dict:
    code = _company_code(company_code)
    url = build_url(JAR, f"ja_kodas={code}",
                    select=("ja_kodas", "ja_pavadinimas", "reg_data", "isreg_data", "forma", "statusas"), limit=1)
    vat_url = build_url(VMI_REG, f"ja_kodas={code}",
                        select=("pvm_kodas_pref", "pvm_kodas", "pvm_iregistruota", "pvm_isregistruota"), limit=5)

    async def run():
        found = await rows("jar", url)
        if not found:
            raise ValueError(f"No company with code {code} in the Legal Entities Register.")
        row = found[0]
        forma = await _lookup(FORMA, row.get("forma"))
        status = await _lookup(STATUSAS, row.get("statusas"))
        vat = await rows("vmi", vat_url)
        return envelope("jar", url, parse_company(row, forma, status, vat), vat_source_url=vat_url)
    return await cached(("company_details", code), DAY, run)


async def company_tax_data(company_code: str) -> dict:
    code = _company_code(company_code)
    url = build_url(VMI_TAX, f"mm_kodas.ja_kodas={code}",
                    select=("pavadinimas", "metai", "menuo", "suma", "atnaujinta"),
                    sort=("-metai", "-menuo"), limit=12)

    async def run():
        data = await rows("vmi", url)
        return envelope("vmi", url, {"company_code": code, "name": data[0].get("pavadinimas") if data else None,
                                     "periods": parse_tax(data), "note": TAX_NOTE})
    return await cached(("company_tax_data", code), DAY, run)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_mcp_companies.py -q`
Expected: `9 passed`.

- [ ] **Step 5: Commit**

```bash
git add mcp_server/companies.py tests/test_mcp_companies.py
git commit -m "feat(mcp): company search, details and taxes from JAR and VMI open data"
```

---

### Task 4: Law, exchange-rate and web-search tools

**Files:**
- Create: `mcp_server/laws.py`, `mcp_server/rates.py`, `mcp_server/web.py`, `tests/test_mcp_laws.py`, `tests/test_mcp_rates_web.py`

**Interfaces:**
- Consumes: Task 1 (`uapi`, `core`), Task 2 (`mcp_upstream`, fixtures), and `tools.search.OFFICIAL_DOMAINS` (existing).
- Produces (parameter names are the tool argument names):
  - `laws.law_search(query: str, only_in_force: bool = True, limit: int = 10) -> dict`, where `data` is `list[{document_id, title, type, tar_code, adopted, in_force_from, status, url}]`, base acts first.
  - `laws.law_consolidated(document_id: str, on_date: str | None = None) -> dict`, where `data` is `{document_id, on_date, original_url, consolidated: {url, valid_from, valid_to} | None[, note]}`.
  - `rates.exchange_rate(currency: str | None = None) -> dict`, where `data` is `{date, rates: {CCY: float}}`, or `{date, currency, per_eur}` when a currency is given.
  - `web.gov_web_search(query: str, max_results: int = 6, official_only: bool = True) -> dict`, where `data` is `list[{title, url, published, highlights, text}]`.

- [ ] **Step 1: Write the failing law tests**

`tests/test_mcp_laws.py`:

```python
"""Law tools against recorded TAR responses."""

from __future__ import annotations

import pytest

from mcp_server import laws

ALIENS = 'Dokumentas?pavadinimas.lower().contains("užsieniečių teisinės padėties")'


async def test_law_search_puts_the_base_act_first(mcp_upstream):
    fake = mcp_upstream({ALIENS: "tar_aliens.json"})
    r = await laws.law_search("Užsieniečių teisinės padėties", limit=3)
    ids = [a["document_id"] for a in r["data"]]
    assert ids[0] == "TAR.42837E5A79DD"
    assert r["data"][0]["url"] == "https://e-tar.lt/portal/lt/legalAct/TAR.42837E5A79DD"
    assert r["data"][0]["title"] == "Lietuvos Respublikos įstatymas dėl užsieniečių teisinės padėties"
    assert 'galioj_busena="galioja"' in fake.urls[0]
    assert "tekstas_lt" not in fake.urls[0]


async def test_law_search_lowercases_lithuanian_input(mcp_upstream):
    fake = mcp_upstream({ALIENS: "tar_aliens.json"})
    await laws.law_search("UŽSIENIEČIŲ TEISINĖS PADĖTIES")
    assert 'contains("užsieniečių teisinės padėties")' in fake.urls[0]


async def test_law_search_can_include_repealed_acts(mcp_upstream):
    fake = mcp_upstream({ALIENS: "tar_aliens.json"})
    await laws.law_search("užsieniečių teisinės padėties", only_in_force=False)
    assert "galioj_busena" not in fake.urls[0]


async def test_law_search_respects_limit(mcp_upstream):
    mcp_upstream({ALIENS: "tar_aliens.json"})
    assert len((await laws.law_search("užsieniečių teisinės padėties", limit=1))["data"]) == 1


async def test_law_consolidated_returns_version_in_force(mcp_upstream):
    fake = mcp_upstream({'Suvestine?dokumento_id="TAR.C677663D2202"': "tar_suvestine.json"})
    d = (await laws.law_consolidated("TAR.C677663D2202", "2026-10-13"))["data"]
    assert d["consolidated"] == {"url": "https://e-tar.lt/portal/lt/legalAct/TAR.C677663D2202/hhPqGFmNta",
                                 "valid_from": "2025-01-02", "valid_to": None}
    assert 'galioja_nuo<="2026-10-13"' in fake.urls[0] and "sort(-galioja_nuo)" in fake.urls[0]


async def test_law_consolidated_without_versions_links_the_original(mcp_upstream):
    mcp_upstream({"Suvestine?": "empty.json"})
    d = (await laws.law_consolidated("TAR.C677663D2202", "2026-10-13"))["data"]
    assert d["consolidated"] is None
    assert d["original_url"] == "https://e-tar.lt/portal/lt/legalAct/TAR.C677663D2202"


@pytest.mark.parametrize("doc,day", [('x"&limit(9)', None), ("TAR.C677663D2202", "13/10/2026")])
async def test_law_consolidated_validates_inputs(mcp_upstream, doc, day):
    fake = mcp_upstream({})
    with pytest.raises(ValueError):
        await laws.law_consolidated(doc, day)
    assert fake.requests == []
```

- [ ] **Step 2: Write the failing rate and web tests**

`tests/test_mcp_rates_web.py`:

```python
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
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_mcp_laws.py tests/test_mcp_rates_web.py -q`
Expected: `ImportError` for `laws`, `rates` and `web`.

- [ ] **Step 4: Implement `mcp_server/laws.py`**

```python
"""Law tools: the Register of Legal Acts (TAR) on get.data.gov.lt."""

from __future__ import annotations

import re
from datetime import date

from mcp_server.core import cached, envelope
from mcp_server.uapi import build_url, clean_text, lit, rows

TAR_DOC = "datasets/gov/lrsk/teises_aktai/Dokumentas"
TAR_CONS = "datasets/gov/lrsk/teises_aktai/Suvestine"
DAY = 24 * 3600
# Titles of acts that change, implement or repeal another act; the base act should rank above them.
_DERIVED = re.compile(r"pakeitimo|papildymo|įgyvendinimo|pripažinimo netekusi", re.IGNORECASE)


def _document_id(value: str) -> str:
    v = value.strip()
    if not re.fullmatch(r"[A-Za-z0-9.]{6,40}", v):
        raise ValueError("Use the document_id from law_search, e.g. TAR.C677663D2202.")
    return v


def _iso_date(value: str) -> str:
    try:
        return date.fromisoformat(value.strip()).isoformat()
    except ValueError:
        raise ValueError("Use a date like 2026-10-13.") from None


def parse_acts(data: list[dict]) -> list[dict]:
    acts = [{
        "document_id": r.get("dokumento_id"),
        "title": r.get("pavadinimas"),
        "type": r.get("rusis"),
        "tar_code": r.get("tar_kodas"),
        "adopted": r.get("priimtas"),
        "in_force_from": r.get("isigalioja"),
        "status": r.get("galioj_busena"),
        "url": r.get("nuoroda"),
    } for r in data]
    return sorted(acts, key=lambda a: (bool(_DERIVED.search(a["title"] or "")), len(a["title"] or "")))


def parse_consolidated(doc: str, day: str, found: list[dict]) -> dict:
    out = {"document_id": doc, "on_date": day, "original_url": f"https://e-tar.lt/portal/lt/legalAct/{doc}"}
    if not found:
        return {**out, "consolidated": None,
                "note": "No consolidated version starts on or before this date; link the original act."}
    r = found[0]
    return {**out, "consolidated": {"url": r.get("nuoroda"),
                                    "valid_from": (r.get("galioja_nuo") or "")[:10] or None,
                                    "valid_to": (r.get("galioja_iki") or "")[:10] or None}}


async def law_search(query: str, only_in_force: bool = True, limit: int = 10) -> dict:
    limit = max(1, min(25, int(limit)))
    filters = [f"pavadinimas.lower().contains({lit(clean_text(query).lower())})"]
    if only_in_force:
        filters.append(f"galioj_busena={lit('galioja')}")
    # ponytail: ranks only the first 50 title matches; add paging if a base act ever falls outside them
    url = build_url(TAR_DOC, *filters,
                    select=("dokumento_id", "pavadinimas", "rusis", "tar_kodas", "priimtas", "isigalioja",
                            "galioj_busena", "nuoroda"), limit=50)

    async def run():
        return envelope("tar", url, parse_acts(await rows("tar", url))[:limit])
    return await cached(("law_search", url, limit), DAY, run)


async def law_consolidated(document_id: str, on_date: str | None = None) -> dict:
    doc = _document_id(document_id)
    day = _iso_date(on_date) if on_date else date.today().isoformat()
    url = build_url(TAR_CONS, f"dokumento_id={lit(doc)}", f"galioja_nuo<={lit(day)}",
                    select=("suvestines_id", "nuoroda", "galioja_nuo", "galioja_iki"),
                    sort=("-galioja_nuo",), limit=1)

    async def run():
        return envelope("tar", url, parse_consolidated(doc, day, await rows("tar", url)))
    return await cached(("law_consolidated", url), DAY, run)
```

- [ ] **Step 5: Implement `mcp_server/rates.py`**

```python
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
```

- [ ] **Step 6: Implement `mcp_server/web.py`**

```python
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
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_mcp_laws.py tests/test_mcp_rates_web.py -q`
Expected: `14 passed` (8 law + 6 rate/web).

- [ ] **Step 8: Commit**

```bash
git add mcp_server/laws.py mcp_server/rates.py mcp_server/web.py tests/test_mcp_laws.py tests/test_mcp_rates_web.py
git commit -m "feat(mcp): TAR law search and consolidated versions, Bank of Lithuania rates, official web search"
```

---

### Task 5: Tool registry, FastMCP server, auth and CLI

**Files:**
- Create: `mcp_server/sources.py`, `mcp_server/server.py`, `mcp_server/auth.py`, `mcp_server/keys.py`, `mcp_server/__main__.py`, `tests/test_mcp_server.py`, `tests/test_mcp_auth.py`

**Interfaces:**
- Consumes: the tool functions from Tasks 3 and 4, and `MCPSettings` (Task 1).
- Produces:
  - `sources.TOOL_FUNCS: dict[str, Callable[..., Awaitable[dict]]]` with exactly these keys: `company_search`, `company_details`, `company_tax_data`, `law_search`, `law_consolidated`, `exchange_rate`, `gov_web_search`;
  - `server.mcp` (FastMCP), `server.http_app()`, `server.run(transport)`;
  - `auth.hash_key(key: str) -> str` and `auth.AuthRateLimitMiddleware(app, settings, protected_prefix="/mcp")`.

- [ ] **Step 1: Write the failing tests**

`tests/test_mcp_auth.py`:

```python
"""API-key auth and rate limits on the MCP HTTP transport."""

from __future__ import annotations

import httpx

from mcp_server.auth import AuthRateLimitMiddleware, hash_key
from mcp_server.config import MCPSettings


async def ok_app(scope, receive, send):
    await send({"type": "http.response.start", "status": 200, "headers": []})
    await send({"type": "http.response.body", "body": b"ok"})


def client(**settings) -> httpx.AsyncClient:
    app = AuthRateLimitMiddleware(ok_app, MCPSettings(**settings))
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test")


async def test_anonymous_limit_then_429():
    async with client(anon_rpm=2) as c:
        assert (await c.post("/mcp")).status_code == 200
        assert (await c.post("/mcp")).status_code == 200
        third = await c.post("/mcp")
    assert third.status_code == 429 and int(third.headers["retry-after"]) >= 1
    assert "anonymous tier" in third.json()["error"]


async def test_invalid_key_is_401():
    async with client() as c:
        r = await c.post("/mcp", headers={"Authorization": "Bearer lk_wrong"})
    assert r.status_code == 401 and "bearer" in r.headers["www-authenticate"].lower()


async def test_valid_key_gets_key_tier():
    good = "lk_good"
    async with client(anon_rpm=1, key_rpm=5, api_key_hashes=frozenset({hash_key(good)})) as c:
        codes = [(await c.post("/mcp", headers={"X-API-Key": good})).status_code for _ in range(5)]
    assert codes == [200] * 5


async def test_health_is_never_limited():
    async with client(anon_rpm=1) as c:
        codes = [(await c.get("/health")).status_code for _ in range(5)]
    assert codes == [200] * 5
```

`tests/test_mcp_server.py`:

```python
"""FastMCP wiring: every tool registered read-only, envelopes come back, HTTP app is guarded."""

from __future__ import annotations

from starlette.testclient import TestClient

from mcp_server.server import http_app, mcp
from mcp_server.sources import TOOL_FUNCS


async def test_every_tool_is_registered_read_only():
    tools = await mcp.list_tools()
    assert {t.name for t in tools} == set(TOOL_FUNCS) == {
        "company_search", "company_details", "company_tax_data", "law_search", "law_consolidated",
        "exchange_rate", "gov_web_search"}
    assert all(t.annotations and t.annotations.readOnlyHint for t in tools)
    assert all(t.description for t in tools)


async def test_call_tool_returns_the_envelope(mcp_upstream):
    mcp_upstream({"getCurrentFxRates": "lb_fx.xml"})
    _content, structured = await mcp.call_tool("exchange_rate", {"currency": "USD"})
    assert structured["data"]["per_eur"] == 1.1181
    assert structured["source_url"].startswith("https://www.lb.lt/")


def test_http_app_serves_health_and_guards_mcp():
    with TestClient(http_app()) as c:
        health = c.get("/health").json()
        assert health["status"] == "ok" and health["tools"] == len(TOOL_FUNCS)
        assert c.post("/mcp", headers={"Authorization": "Bearer lk_nope"}, json={}).status_code == 401
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_mcp_auth.py tests/test_mcp_server.py -q`
Expected: `ModuleNotFoundError: No module named 'mcp_server.auth'` / `'mcp_server.server'`.

- [ ] **Step 3: Implement `mcp_server/sources.py`**

```python
"""Every MCP tool by name. The server registers these; tools/mcp_tools.py calls them in-process."""

from mcp_server.companies import company_details, company_search, company_tax_data
from mcp_server.laws import law_consolidated, law_search
from mcp_server.rates import exchange_rate
from mcp_server.web import gov_web_search

TOOL_FUNCS = {f.__name__: f for f in (
    company_search, company_details, company_tax_data, law_search, law_consolidated, exchange_rate,
    gov_web_search)}
```

- [ ] **Step 4: Implement `mcp_server/auth.py`**

```python
"""API-key auth + per-client rate limiting for the HTTP transport (pure ASGI middleware).

- No key  -> anonymous tier (MCP_ANON_RPM / MCP_ANON_RPD per client IP).
- Valid key (Authorization: Bearer <key> or X-API-Key: <key>) -> key tier (MCP_KEY_RPM / MCP_KEY_RPD).
- Invalid key -> 401. Over limit -> 429 with Retry-After.
Keys are configured as sha256 hex digests in MCP_API_KEY_HASHES; issue one with
`python -m mcp_server.keys new`.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import deque

from mcp_server.config import MCPSettings


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


class _Window:
    """Sliding-window counter for one client (minute + day)."""
    __slots__ = ("minute", "day")

    def __init__(self):
        self.minute: deque[float] = deque()
        self.day: deque[float] = deque()

    def hit(self, now: float, rpm: int, rpd: int) -> float | None:
        while self.minute and now - self.minute[0] >= 60:
            self.minute.popleft()
        while self.day and now - self.day[0] >= 86400:
            self.day.popleft()
        if len(self.minute) >= rpm:
            return 60 - (now - self.minute[0])
        if len(self.day) >= rpd:
            return 86400 - (now - self.day[0])
        self.minute.append(now)
        self.day.append(now)
        return None


class AuthRateLimitMiddleware:
    def __init__(self, app, settings: MCPSettings, protected_prefix: str = "/mcp"):
        self.app = app
        self.s = settings
        self.prefix = protected_prefix
        self.windows: dict[str, _Window] = {}

    def _client_ip(self, scope) -> str:
        headers = dict(scope.get("headers") or [])
        if self.s.trust_proxy:
            xff = headers.get(b"x-forwarded-for", b"").decode().split(",")[0].strip()
            if xff:
                return xff
        client = scope.get("client") or ("unknown", 0)
        return client[0]

    async def _reject(self, send, status: int, msg: str, retry_after: float | None = None):
        headers = [(b"content-type", b"application/json")]
        if retry_after is not None:
            headers.append((b"retry-after", str(int(retry_after) + 1).encode()))
        if status == 401:
            headers.append((b"www-authenticate", b'Bearer realm="lietuva-mcp"'))
        await send({"type": "http.response.start", "status": status, "headers": headers})
        await send({"type": "http.response.body", "body": json.dumps({"error": msg}).encode()})

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or not scope["path"].startswith(self.prefix):
            return await self.app(scope, receive, send)
        headers = dict(scope.get("headers") or [])
        raw = headers.get(b"x-api-key", b"").decode().strip()
        auth = headers.get(b"authorization", b"").decode().strip()
        if not raw and auth.lower().startswith("bearer "):
            raw = auth[7:].strip()
        if raw:
            h = hash_key(raw)
            if h not in self.s.api_key_hashes:
                return await self._reject(send, 401, "invalid API key")
            ident, rpm, rpd, tier = f"key:{h[:16]}", self.s.key_rpm, self.s.key_rpd, "key"
        else:
            ident, rpm, rpd, tier = f"ip:{self._client_ip(scope)}", self.s.anon_rpm, self.s.anon_rpd, "anonymous"
        win = self.windows.setdefault(ident, _Window())
        wait = win.hit(time.time(), rpm, rpd)
        if wait is not None:
            return await self._reject(send, 429, f"rate limit exceeded ({tier} tier: {rpm}/min, {rpd}/day)", wait)
        if len(self.windows) > 50000:  # ponytail: crude memory guard; move counters to Redis before scaling out
            self.windows.clear()
        return await self.app(scope, receive, send)
```

- [ ] **Step 5: Implement `mcp_server/keys.py` and `mcp_server/__main__.py`**

`mcp_server/keys.py`:

```python
"""Issue API keys: `python -m mcp_server.keys new` prints a key and its hash.

Give the key to the client; add ONLY the hash to MCP_API_KEY_HASHES (comma-separated).
"""

import secrets
import sys

from mcp_server.auth import hash_key

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "hash":
        print(hash_key(sys.argv[2]))
    else:
        key = "lk_" + secrets.token_urlsafe(32)
        print(f"key:  {key}\nhash: {hash_key(key)}")
```

`mcp_server/__main__.py`:

```python
import argparse

from mcp_server.server import run

p = argparse.ArgumentParser(prog="python -m mcp_server")
p.add_argument("--transport", choices=["http", "stdio"], default="http")
run(p.parse_args().transport)
```

- [ ] **Step 6: Implement `mcp_server/server.py`**

```python
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
    official_only: bool = True,
) -> Env:
    """Web search over official Lithuanian government websites (Exa). Use when no structured tool fits."""
    return await web.gov_web_search(query, max_results, official_only)


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
    uvicorn.run(http_app(), host=s.host, port=s.port, proxy_headers=True, forwarded_allow_ips="*")
```

- [ ] **Step 7: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_mcp_auth.py tests/test_mcp_server.py -q`
Expected: `7 passed`. A `StarletteDeprecationWarning` about httpx in the TestClient is harmless.

- [ ] **Step 8: Smoke the stdio entry point starts**

Run: `printf '' | timeout 5 .venv/bin/python -m mcp_server --transport stdio; echo "exit $?"`
Expected: exits without a traceback. An exit code of 0 or 124 is fine.

- [ ] **Step 9: Commit**

```bash
git add mcp_server/sources.py mcp_server/server.py mcp_server/auth.py mcp_server/keys.py mcp_server/__main__.py tests/test_mcp_server.py tests/test_mcp_auth.py
git commit -m "feat(mcp): FastMCP server with API-key tiers and rate limits"
```

---

### Task 6: Give the Business and Tax assistants the tools

**Files:**
- Create: `tools/mcp_tools.py`, `tests/test_mcp_tools.py`
- Modify: `agents/business/eresidency.py`, `agents/living/tax.py`, `prompts/system/eresidency.md`, `prompts/system/tax.md`

**Interfaces:**
- Consumes: `sources.TOOL_FUNCS` (Task 5).
- Produces:
  - `tools.mcp_tools.call_mcp_tool(name: str, args: dict) -> dict`;
  - the LangChain tools `company_search`, `company_details`, `company_tax_data`, `law_search`, `law_consolidated`, `exchange_rate`;
  - the lists `BUSINESS_TOOLS` and `TAX_TOOLS`.

- [ ] **Step 1: Write the failing tests**

`tests/test_mcp_tools.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/test_mcp_tools.py -q`
Expected: `ModuleNotFoundError: No module named 'tools.mcp_tools'`.

- [ ] **Step 3: Implement `tools/mcp_tools.py`**

```python
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


def _compact(payload: Any) -> str:
    s = json.dumps(payload, ensure_ascii=False, default=str)
    return s if len(s) <= MAX_CHARS else s[:MAX_CHARS] + "… [truncated]"


async def call_mcp_tool(name: str, args: dict) -> dict:
    url = os.environ.get("LIETUVA_MCP_URL", "").strip()
    if not url:
        from mcp_server.sources import TOOL_FUNCS
        return await TOOL_FUNCS[name](**args)
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
    key = os.environ.get("LIETUVA_MCP_API_KEY", "").strip()
    headers = {"Authorization": f"Bearer {key}"} if key else None
    async with streamablehttp_client(url, headers=headers, timeout=30) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            res = await session.call_tool(name, args)
    if res.isError:
        return {"error": " ".join(getattr(c, "text", "") for c in res.content) or "tool failed"}
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
            return _compact({"error": f"{name} unavailable: {e}. Fall back to web_search."})

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
```

- [ ] **Step 4: Wire the agents**

In `agents/business/eresidency.py`, replace:

```python
from tools.search import web_search

SPEC = AGENTS_BY_SLUG["eresidency"]
TOOLS = [web_search]
```

with:

```python
from tools.mcp_tools import BUSINESS_TOOLS
from tools.search import web_search

SPEC = AGENTS_BY_SLUG["eresidency"]
# Structured government data first, Exa web search last.
TOOLS = [*BUSINESS_TOOLS, web_search]
```

Read `agents/living/tax.py` first: it has the same shape. Apply the same change there with `TAX_TOOLS`:

```python
from tools.mcp_tools import TAX_TOOLS
from tools.search import web_search

SPEC = AGENTS_BY_SLUG["tax"]
# Structured government data first, Exa web search last.
TOOLS = [*TAX_TOOLS, web_search]
```

- [ ] **Step 5: Update the two prompts**

In `prompts/system/eresidency.md`, replace the paragraph that begins `Always use \`web_search\` (official_only=true) to confirm current fees` with:

```markdown
**Tool order (official data first, web search second):**
1. For a specific company (does it exist, its code, status, legal form, VAT number) call `company_search` / `company_details` (Registrų centras JAR and VMI open data). For the taxes it has paid, call `company_tax_data`.
2. For laws (for example Akcinių bendrovių įstatymas or Mažųjų bendrijų įstatymas) call `law_search`, then `law_consolidated` to link the version in force today.
3. For currency conversion call `exchange_rate` (Bank of Lithuania).
4. Use `web_search` (official_only=true) for procedures, fees, steps and timelines, or when a structured tool returns nothing or an error.

Every structured result includes `source_url` and `retrieved_at`: cite the e-TAR `url` for laws and mention the data date when it matters. Clearly separate e-resident status from company formation — they are different procedures. Remind users that Lithuanian company registration does not remove tax or reporting duties in their home country. Never give a personal eligibility verdict. Route high-stakes formation, licensing, or immigration questions to Registrų centras, VMI, or the Migration Department. This service is independent and not a government service. Answer in the user's language.
```

In `prompts/system/tax.md`, insert this paragraph immediately before the paragraph that begins `Always use \`web_search\``:

```markdown
**Tool order:** for the wording of a tax law, call `law_search` (for example "gyventojų pajamų mokesčio įstatymas") and then `law_consolidated` to link the version in force; for a company's published tax payments call `company_tax_data`; for converting foreign-currency amounts call `exchange_rate` (Bank of Lithuania euro reference rates). Rates, thresholds, deadlines and procedures still come from `web_search` on vmi.lt and sodra.lt.
```

- [ ] **Step 6: Run the tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/test_mcp_tools.py -q`
Expected: `5 passed`.

- [ ] **Step 7: Run the whole suite**

Run: `.venv/bin/python -m pytest -q --ignore=tests/test_api.py`
Expected: all pass. The count is the previous total plus 5.

- [ ] **Step 8: Commit**

```bash
git add tools/mcp_tools.py tests/test_mcp_tools.py agents/business/eresidency.py agents/living/tax.py prompts/system/eresidency.md prompts/system/tax.md
git commit -m "feat(agents): Business and Tax assistants use structured government data before web search"
```

---

### Task 7: Packaging, docs, live smoke test, version

**Files:**
- Create: `requirements-mcp.txt`, `Dockerfile.mcp`, `docker-compose.mcp.yaml`, `docs/mcp_server.md`, `tests/test_mcp_live.py`
- Modify: `.env.example`, `VERSION`, `docs/change_log.md`

**Interfaces:**
- Consumes: everything above.
- Produces: a buildable image `lietuva-mcp`, and the documented env vars `LIETUVA_MCP_URL`, `LIETUVA_MCP_API_KEY` and `MCP_*`.

- [ ] **Step 1: Write the live smoke test (skipped unless `--run-integration`)**

`tests/test_mcp_live.py`:

```python
"""Live upstream smoke test. Run: pytest tests/test_mcp_live.py --run-integration -q
Government endpoints change without notice; this tells you when a recorded fixture has gone stale."""

from __future__ import annotations

import pytest

from mcp_server import companies, core, laws, rates

pytestmark = pytest.mark.skipif("not config.getoption('--run-integration')", reason="needs network")


@pytest.fixture(autouse=True)
def _real_network():
    core.set_transport(None)
    core.reset()
    yield
    core.reset()


async def test_live_company():
    r = await companies.company_search("Vinted", 5)
    assert "302767152" in {c["company_code"] for c in r["data"]}
    d = (await companies.company_details("302767152"))["data"]
    assert d["vat_number"] and d["legal_form"]


async def test_live_law():
    r = await laws.law_search("gyventojų pajamų mokesčio įstatymas", limit=3)
    assert r["data"][0]["document_id"] == "TAR.C677663D2202"
    c = (await laws.law_consolidated("TAR.C677663D2202"))["data"]
    assert c["consolidated"]["url"].startswith("https://e-tar.lt/portal/lt/legalAct/TAR.C677663D2202/")


async def test_live_rates():
    assert (await rates.exchange_rate("USD"))["data"]["per_eur"] > 0
```

Run: `.venv/bin/python -m pytest tests/test_mcp_live.py -q`
Expected: `3 skipped`.

Run: `.venv/bin/python -m pytest tests/test_mcp_live.py --run-integration -q`
Expected: `3 passed`. If one fails, the upstream changed: compare it with the Verified upstream facts and report the difference. Do not edit the assertion to make it pass.

- [ ] **Step 2: Container files**

`requirements-mcp.txt`:

```text
# Runtime deps for the standalone MCP server image (Dockerfile.mcp)
mcp>=1.20,<2
httpx==0.28.1
cachetools==7.2.1
pydantic==2.*
pydantic-settings==2.14.1
python-dotenv==1.2.2
uvicorn==0.49.0
langchain-core==1.4.1
```

`Dockerfile.mcp`:

```dockerfile
# lietuva.chat MCP server (mcp.lietuva.chat). Build: docker build -f Dockerfile.mcp -t lietuva-mcp .
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8000

WORKDIR /app

# Coolify's health check runs curl inside the container.
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

COPY requirements-mcp.txt .
RUN pip install --no-cache-dir -r requirements-mcp.txt

# Server package + the shared official-domain list it reuses for web search.
COPY mcp_server/ mcp_server/
COPY tools/__init__.py tools/search.py tools/
COPY utils/__init__.py utils/config.py utils/

RUN useradd --create-home --uid 10001 app
USER app
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

CMD ["python", "-m", "mcp_server", "--transport", "http"]
```

`docker-compose.mcp.yaml`:

```yaml
# Coolify "Docker Compose" alternative for the MCP server (or use Dockerfile.mcp directly).
services:
  mcp:
    build:
      context: .
      dockerfile: Dockerfile.mcp
    environment:
      - EXA_API_KEY=${EXA_API_KEY}
      - MCP_API_KEY_HASHES=${MCP_API_KEY_HASHES}
      - MCP_ANON_RPM=${MCP_ANON_RPM:-30}
      - MCP_ANON_RPD=${MCP_ANON_RPD:-500}
      - MCP_KEY_RPM=${MCP_KEY_RPM:-300}
      - MCP_KEY_RPD=${MCP_KEY_RPD:-20000}
    labels:
      - coolify.managed=true
      - coolify.port=8000
    restart: unless-stopped
```

Run: `docker build -f Dockerfile.mcp -t lietuva-mcp . && docker run --rm -d -p 8765:8000 --name lietuva-mcp-test lietuva-mcp && sleep 5 && curl -s localhost:8765/health; docker stop lietuva-mcp-test`
Expected: `{"status":"ok","version":"0.1.0","tools":7}`.

- [ ] **Step 3: Verify remote mode end to end**

This is the one path no unit test covers: the chat app calling the server over HTTP.

```bash
MCP_PORT=8766 .venv/bin/python -m mcp_server --transport http > /tmp/lietuva-mcp.log 2>&1 &
sleep 4
LIETUVA_MCP_URL=http://localhost:8766/mcp .venv/bin/python -c "
import asyncio, json
from tools.mcp_tools import law_search
print(json.loads(asyncio.run(law_search.ainvoke({'query': 'gyventojų pajamų mokesčio įstatymas', 'limit': 1})))['data'][0]['document_id'])"
kill %1
```

Expected: `TAR.C677663D2202`. This needs network access.

- [ ] **Step 4: `.env.example`**

Append:

```bash
# --- MCP server (optional) ---
# Chat app: call a deployed MCP server instead of in-process tools.
LIETUVA_MCP_URL=                  # e.g. https://mcp.lietuva.chat/mcp
LIETUVA_MCP_API_KEY=              # an lk_… key issued with `python -m mcp_server.keys new`
# MCP server process:
MCP_API_KEY_HASHES=               # comma-separated sha256 hashes of issued keys
MCP_ANON_RPM=30
MCP_ANON_RPD=500
MCP_KEY_RPM=300
MCP_KEY_RPD=20000
```

- [ ] **Step 5: `docs/mcp_server.md`**

Write the doc with these sections, in this order:

1. **Title and intro:** one paragraph saying the server is public, read-only, independent and not a government service. Planned production endpoint `https://mcp.lietuva.chat/mcp`.
2. **The envelope:** a JSON example of the envelope.
3. **Tools table:** columns Tool | Source | Upstream | Cache. Seven rows, with the TTLs from the code: company tools 24 h, legal-form/status lookups 7 days, laws 24 h, rates 6 h, Exa 6 h.
4. **Transports:** the two `python -m mcp_server` commands, plus a stdio client config for Claude Desktop / Cursor (`"lietuva-gov"`, `cwd` set to the checkout).
5. **Auth and limits:** the anonymous and key tiers, 401/429 behaviour, key issuing with `python -m mcp_server.keys new` (store only the hash), and the note that counters are in memory per container, so run one replica.
6. **Upstream protection:** per-source minimum interval (0.2 s for data.gov.lt, 0.5 s for lb.lt), retries on 429/5xx, and the User-Agent.
7. **Privacy:** company codes only. An 11-digit personal code is refused before any request, and nothing user-typed is logged.
8. **Chat app integration:** `LIETUVA_MCP_URL` / `LIETUVA_MCP_API_KEY`, the in-process default, and which assistants get which tools.
9. **Tests:** the fixture suite command and the live `--run-integration` command.
10. **Open questions:** copy the "Open questions" list from the end of this plan.

Do not invent deployment hosts, IDs or DNS details. Deployment gets one line: "Deploy `Dockerfile.mcp` as its own service; see `docker-compose.mcp.yaml`."

- [ ] **Step 6: Version and changelog**

Run `date -u +%Y-%m-%d` and use its output as DATE.

Set `VERSION` to:

```text
1.2.0
DATE
```

Prepend to `docs/change_log.md`, directly under `# Change Log`:

```markdown
## v1.2.0 — DATE

**A public MCP server for Lithuanian government open data, and the Business and Tax assistants now check official registers before searching the web.**

- New `mcp_server/` (FastMCP, read-only):
  - `company_search`, `company_details`, `company_tax_data`, from the Legal Entities Register (JAR) and VMI open data on data.gov.lt;
  - `law_search` and `law_consolidated`, from the Register of Legal Acts (TAR), with base acts ranked above their amendments;
  - `exchange_rate` (Bank of Lithuania);
  - `gov_web_search`, limited to official sites.
- Every result carries its source URL, licence note and retrieval time.
- Anonymous and API-key tiers with rate limits, and a polite per-source pace towards upstream servers.
- Company codes only: personal codes are refused before any request.
- The Business and Tax assistants get the tools in-process by default, or from a deployed server via `LIETUVA_MCP_URL`.
- `Dockerfile.mcp` and `docker-compose.mcp.yaml` for a separate deployment. Docs are in `docs/mcp_server.md`.
- Tests:
  - recorded-fixture tests, with no network and no patched modules;
  - a live smoke test behind `--run-integration`.
```

- [ ] **Step 7: Full verification**

```bash
.venv/bin/python -m pytest -q --ignore=tests/test_api.py
.venv/bin/python -m pytest tests/test_mcp_live.py --run-integration -q
git diff main --stat
```

Expected: the first command passes everything (previous total plus the new MCP tests), and the live tests give `3 passed`. The diff stat lists only files named in this plan.

- [ ] **Step 8: Commit**

```bash
git add requirements-mcp.txt Dockerfile.mcp docker-compose.mcp.yaml docs/mcp_server.md tests/test_mcp_live.py .env.example VERSION docs/change_log.md
git commit -m "v1.2.0: lietuva.chat MCP server for Lithuanian government open data"
```

Do not push. The user decides when to push and open a PR.

---

## Open questions (carry into docs/mcp_server.md; not blockers for building)

1. **Licences:** the exact licence of the JAR (data.gov.lt/datasets/1484) and VMI taxpayer-register datasets, and the Bank of Lithuania's reuse terms, were not read (data.gov.lt pages return 403 to scripts). Check them by hand before announcing the public endpoint, and update `SOURCES[...].licence`.
2. **What VMI's `suma` means:** monthly, cumulative or year-to-date. The tool reports it "as published" until this is confirmed.
3. **Deployment:** host, DNS (`mcp.lietuva.chat`) and CI deploy hook are the user's infrastructure decisions.
4. **Later tools,** if an assistant needs them:
   - weather (api.meteo.lt: CC BY-SA 4.0, 180 requests/min/IP, credit LHMT);
   - Statistics Lithuania (SDMX);
   - the address register;
   - procurement (vpt);
   - the data.gov.lt catalogue search.
