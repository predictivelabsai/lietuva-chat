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
    # select() still names the column; this checks the in-force filter is absent.
    assert 'galioj_busena="' not in fake.urls[0]


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
