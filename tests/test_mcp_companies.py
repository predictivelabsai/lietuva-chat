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
