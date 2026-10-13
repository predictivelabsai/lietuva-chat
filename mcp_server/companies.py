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
TAX_NOTE = ("Taxes and duties paid to VMI's budget accounts, cumulative from 1 January to the end of the given "
            "month (data.gov.lt dataset 673); not Sodra contributions. Updated monthly.")


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
    return [{"year": r.get("metai"), "month": r.get("menuo"), "taxes_paid_year_to_date_eur": r.get("suma"),
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
