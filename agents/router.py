"""3-tier agent routing: prefix match -> keyword heuristics -> LLM fallback."""

from __future__ import annotations

import logging
import re

from agents.registry import AGENTS, AGENTS_BY_SLUG

log = logging.getLogger(__name__)

_PREFIX_MAP: dict[str, str] = {a.prefix.rstrip(":"): a.slug for a in AGENTS if a.prefix}
_PREFIX_MAP["estonia"] = "explore"  # alias so links shared from the eesti.chat era still route

# Keywords match whole words, case-insensitively. A trailing * marks a deliberate stem
# ("relocat*" matches relocate, relocating); without it, "tax" will not match "taxi".
# English plus the most common Lithuanian and Russian wording for each topic.
_SLUG_KEYWORDS: dict[str, list[str]] = {
    # Order matters: equal scores go to the earlier, more specific topic ("company" + "PVM" is a tax question).
    "tax": ["tax", "taxes", "taxed", "taxation", "vat", "pvm", "gpm", "vmi", "sodra", "psd",
            "income declaration", "annual declaration", "tax return", "salary", "salaries", "withheld",
            "deduction*", "refund*", "contribution*", "mokes*", "atlygin*", "išskaičiuo*", "deklaracij*",
            "налог*", "зарплат*"],
    "eresidency": ["e-residen*", "company", "companies", "uab", "mb", "individuali veikla",
                   "individualios veiklos", "individual activity", "start a business", "register a company",
                   "startup*", "business bank*", "founder*", "incorporat*", "registrų centr*", "registru centr*",
                   "įmon*", "steigti", "įsteigti", "verslo", "компани*", "бизнес*"],
    "moving": ["move to lithuania", "moving", "relocat*", "residence", "visa", "visas", "migris",
               "migracij*", "work permit", "study permit", "immigration", "settl*", "deklaruo*",
               "gyvenam*", "leidim*", "persikel*", "вид на жительство", "внж", "виз*", "переезд*"],
    "digital": ["digital id", "e-id", "eid", "id card", "smart-id", "smart id", "mobile-id", "mobile id",
                "digital signature", "sign a document", "e-signature", "epaslaug*", "e-service*", "log in",
                "login", "authenticat*", "parašas", "parasas"],
    "services": ["health", "insurance", "vlk", "ligoni*", "doctor*", "gydytoj*", "sveikat*", "school*",
                 "mokykl*", "education", "university", "benefit*", "pension*", "pensij*", "family", "šeim*",
                 "parental", "child*", "vaik*", "voting", "vote", "election*", "vrk", "rinkim*", "balsuo*",
                 "passport*", "renew*", "marriage", "birth*", "gimim*", "врач*", "пенси*"],
    # City names alone are not a topic: "declare residence in Vilnius" is a moving question.
    "explore": ["why lithuania", "culture", "history", "tourism", "visit*", "travel*", "about lithuania",
                "story", "invest*", "innovation", "diaspora", "globali lietuva", "returning", "coming home",
                "grįž*", "grizt*"],
}


def _keyword_pattern(kw: str) -> re.Pattern:
    stem = kw.endswith("*")
    body = re.escape(kw.rstrip("*"))
    return re.compile(r"(?<!\w)" + body + ("" if stem else r"(?!\w)"), re.IGNORECASE)


_SLUG_PATTERNS = {slug: [_keyword_pattern(kw) for kw in kws] for slug, kws in _SLUG_KEYWORDS.items()}
_PREFIX_RE = re.compile(r"^\s*(\w+):\s*")


def _prefix_match(message: str) -> str | None:
    m = _PREFIX_RE.match(message)
    return _PREFIX_MAP.get(m.group(1).lower()) if m else None


def _keyword_scores(message: str) -> dict[str, int]:
    scores: dict[str, int] = {}
    for slug, patterns in _SLUG_PATTERNS.items():
        score = sum(1 for p in patterns if p.search(message))
        if score:
            scores[slug] = score
    return scores


def _llm_classify(message: str, llm=None) -> str:
    try:
        if llm is None:
            from utils.llm import build_llm
            llm = build_llm(temperature=0)
        slugs = ", ".join(AGENTS_BY_SLUG.keys())
        prompt = (
            f"Classify this user message into exactly one of these agent slugs: {slugs}\n"
            f"Message: {message}\n"
            f"Reply with ONLY the slug, nothing else."
        )
        resp = str(llm.invoke(prompt).content).strip().strip(".`'\" ").lower()
        if resp in AGENTS_BY_SLUG:
            return resp
    except Exception as e:
        log.warning("LLM classify failed: %s", e)
    return "explore"


def route(message: str, classify=None) -> str:
    """Prefix first, then the best keyword score (ties go to the earlier topic), then the LLM."""
    slug = _prefix_match(message)
    if slug:
        return slug

    scores = _keyword_scores(message)
    if scores:
        return max(scores, key=scores.get)

    return (classify or _llm_classify)(message)


def strip_prefix(message: str) -> str:
    """Remove a routing prefix like "tax: ", but leave ordinary text such as "Note: ..." alone.
    A bare prefix ("tax:") is kept as the question rather than becoming an empty one."""
    if not _prefix_match(message):
        return message.strip()
    return _PREFIX_RE.sub("", message, count=1).strip() or message.strip()
