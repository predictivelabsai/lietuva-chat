# Lithuania grounding switch — acceptance

Owned files updated: `tools/search.py`, `tools/__init__.py` (docstring; required so `tools/` grep is clean), `prompts/shared/lithuania_context.md` (replaces `estonia_context.md`), `prompts/system/{digital,eresidency,explore,moving,services,tax}.md`, `agents/base.py`, `agents/registry.py`, `agents/router.py`, `agents/*/__init__.py`.

Slugs unchanged. Explore prefix is `lithuania:`; `estonia:` remains an alias in `agents/router.py` line 13.

## Observable acceptance (2026-10-02)

```
=== GREP 1 ===
agents/router.py:13:_PREFIX_MAP["estonia"] = "explore"  # alias so old lithuania: / estonia: links still work
=== GREP 2 ===
=== DOMAINS ===
29 []
=== PYTEST ===
........s..                                                              [100%]
10 passed, 1 skipped in 0.14s
```

Commands:

- `grep -rniE "eston|eesti|\.ee\b|tallinn|x-tee|mobiil|emta|\bOÜ\b" tools/ prompts/ agents/`
- `grep -rn "estonia_context" --include=*.py .`
- `.venv/bin/python -c "from tools.search import OFFICIAL_DOMAINS; print(len(OFFICIAL_DOMAINS), [d for d in OFFICIAL_DOMAINS if not d.endswith(('.lt','.com'))])"`
- `.venv/bin/python -m pytest -q --ignore=tests/test_api.py`

`__pycache__` under `tools/` and `agents/` was removed so grep did not hit stale bytecode.

## References not edited (other agents own those trees)

`estonia_context` no longer appears anywhere. Estonia / eesti / `.ee` copy still exists outside owned paths, including: `utils/i18n.py`, `utils/geo.py`, `utils/email.py`, `utils/config.py`, `pages/` (about, legal, contact, changelog), `components/layout.py`, `chat/components.py`, `chat/routes.py`, `PRODUCT.md`, `DESIGN.md`, `docs/`, `db.py`, `api/app.py`, `api/auth.py`, `auth/__init__.py`, `tests/test_api.py` (still uses `estonia:` which the router alias still accepts), `tests/test_email.py`, `tests/test_legal_pages.py`.

## Domains

29 hosts, all `.lt` or `.com`. Required list included plus `migracija.lrv.lt`, `ligoniukasa.lrv.lt`, `socmin.lrv.lt`, `vssa.lrv.lt`, `vda.lrv.lt`, `elektroninisparasas.lt`. Exa `includeDomains` payload shape unchanged.
