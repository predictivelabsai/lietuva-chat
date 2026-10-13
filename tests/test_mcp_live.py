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
