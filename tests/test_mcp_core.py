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
