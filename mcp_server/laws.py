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
    valid_to = (r.get("galioja_iki") or "")[:10] or None
    if valid_to and valid_to < day:
        return {**out, "consolidated": None,
                "note": f"The latest consolidated version ended on {valid_to}; link the original act and check e-TAR."}
    return {**out, "consolidated": {"url": r.get("nuoroda"),
                                    "valid_from": (r.get("galioja_nuo") or "")[:10] or None,
                                    "valid_to": valid_to}}


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
