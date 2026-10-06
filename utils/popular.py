"""Home-page question suggestions: the week's most asked curated questions, topped up at random.

Only questions from the curated pool are ever counted or shown, never free text people typed:
real questions can carry personal codes, health or immigration details, and must not surface
on a public page. A question counts as popular once MIN_SESSIONS different sessions asked it
in the last WINDOW_DAYS days.
"""

from __future__ import annotations

import random
import time
from typing import Callable

from utils.i18n import t

WINDOW_DAYS = 7
MIN_SESSIONS = 5
CACHE_SECONDS = 600

POOL_KEYS = (
    [f'ask_{k}_q' for k in ('residence', 'tax', 'health', 'family', 'business', 'abroad')]
    + [f'tick_{n}' for n in range(1, 9)]
    + [f'life_0{n}_q' for n in range(1, 6)]
)

_cache: dict[str, tuple[float, list[tuple[str, int]]]] = {}


def pool(lang: str) -> list[str]:
    return list(dict.fromkeys(t(k, lang) for k in POOL_KEYS))


def _norm(q: str) -> str:
    return q.strip().lower()


def _db_counts(questions: list[str]) -> list[tuple[str, int]]:
    """(normalised question, distinct sessions) for curated questions asked this week."""
    from db import DB_ENABLED, SCHEMA, engine
    if not DB_ENABLED:
        return []
    from sqlalchemy import bindparam, text
    stmt = text(
        f"""SELECT q, COUNT(DISTINCT session_id) AS n FROM (
                SELECT regexp_replace(lower(trim(content)), '^[a-z]+:\\s*', '') AS q, session_id
                FROM {SCHEMA}.chat_messages
                WHERE role = 'user' AND created_at > now() - make_interval(days => :days)
            ) asked
            WHERE q IN :pool
            GROUP BY q HAVING COUNT(DISTINCT session_id) >= :min
            ORDER BY n DESC"""
    ).bindparams(bindparam('pool', expanding=True))
    with engine.connect() as conn:
        rows = conn.execute(stmt, {'days': WINDOW_DAYS, 'pool': [_norm(q) for q in questions],
                                   'min': MIN_SESSIONS}).all()
    return [(r[0], int(r[1])) for r in rows]


def suggestions(lang: str, k: int = 3, counts: Callable[[list[str]], list[tuple[str, int]]] = _db_counts,
                rng: random.Random | None = None) -> list[str]:
    """Up to k questions: most asked this week first, the remaining slots filled at random."""
    questions = pool(lang)
    hit = _cache.get(lang)
    if counts is _db_counts and hit and time.monotonic() - hit[0] < CACHE_SECONDS:
        ranked = hit[1]
    else:
        try:
            ranked = counts(questions)
        except Exception:
            ranked = []  # popularity is a nicety; never break the home page over it
        if counts is _db_counts:
            _cache[lang] = (time.monotonic(), ranked)
    by_norm = {_norm(q): q for q in questions}
    picked = [by_norm[q] for q, _ in ranked if q in by_norm][:k]
    rest = [q for q in questions if q not in picked]
    picked += (rng or random).sample(rest, min(k - len(picked), len(rest)))
    return picked
