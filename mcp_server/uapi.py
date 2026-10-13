"""get.data.gov.lt (Spinta / UAPI): build a safe query URL and fetch its rows.

User text only enters a query through clean_text(), which leaves letters, digits, spaces
and - . , ' „ “ — so it can never close a "…" literal or add & ( ) operators."""

from __future__ import annotations

import re
from urllib.parse import quote

from mcp_server.core import fetch

BASE = "https://get.data.gov.lt/"
_UNSAFE = re.compile(r"[^\w\s\-.,'„“]")
# Lithuanian personal codes (asmens kodas): 11 digits, the first 1–6.
_PERSONAL_CODE = re.compile(r"(?<!\d)[1-6]\d{10}(?!\d)")


def refuse_personal_code(s: str) -> str:
    """Stop any text holding a personal code before it reaches an upstream; never repeat the code."""
    if _PERSONAL_CODE.search(s):
        raise ValueError("This looks like a personal code (asmens kodas). Personal codes are never looked up "
                         "or sent anywhere; ask with a company name or company code instead.")
    return s


def clean_text(s: str, *, min_len: int = 2, max_len: int = 100) -> str:
    s = " ".join(_UNSAFE.sub(" ", refuse_personal_code(s)).split())
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
