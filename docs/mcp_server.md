# lietuva.chat MCP server

`mcp_server/` exposes Lithuanian government open data as read-only
[Model Context Protocol](https://modelcontextprotocol.io) tools. It is public,
read-only, independent and **not a government service** (lietuva.chat is an
independent project). The planned production endpoint is
`https://mcp.lietuva.chat/mcp`.

Every tool queries the upstream register live and returns a JSON envelope with
its provenance. There is no bulk mirror and no database.

## The envelope

Every tool returns the same envelope:

```json
{
  "source_name": "Registrų centras – Legal Entities Register (JAR), via data.gov.lt",
  "source_url": "https://get.data.gov.lt/datasets/gov/rc/jar/iregistruoti/JuridinisAsmuo?ja_pavadinimas.lower().contains(%22vinted%22)&select(ja_kodas,ja_pavadinimas,reg_data,isreg_data)&limit(10)",
  "licence": "CC BY 4.0 (Registrų centras, data.gov.lt dataset 1484)",
  "retrieved_at": "2026-10-13T09:15:02+00:00",
  "cached": false,
  "data": [
    {"company_code": "302767152", "name": "Vinted, UAB", "registered": "2012-04-23", "deregistered": null, "active": true}
  ]
}
```

`cached` is `true` when the result came from the in-process TTL cache rather
than a fresh upstream call.

## Tools

| Tool | Source | Upstream | Cache |
|---|---|---|---|
| `company_search` | Legal Entities Register (JAR) | `get.data.gov.lt` `/rc/jar/iregistruoti` | 24 h |
| `company_details` | JAR + VMI taxpayer register | `get.data.gov.lt` `/rc/jar`, `/vmi/mm_registras` | 24 h; legal-form/status lookups 7 days |
| `company_tax_data` | VMI taxes paid | `get.data.gov.lt` `/vmi/ja_mokesciai` | 24 h |
| `law_search` | Register of Legal Acts (TAR) | `get.data.gov.lt` `/lrsk/teises_aktai` | 24 h |
| `law_consolidated` | TAR consolidated versions | `get.data.gov.lt` `/lrsk/teises_aktai` | 24 h |
| `exchange_rate` | Bank of Lithuania euro rates | `lb.lt` FX rates webservice | 6 h |
| `gov_web_search` | Official Lithuanian sites only (Exa allowlist, always on) | `api.exa.ai` | 6 h |

`company_search` ranks active companies first; `law_search` ranks base acts
above their amending acts; `company_tax_data` returns the latest periods first.

`company_tax_data` reports `taxes_paid_year_to_date_eur`: per VMI's dataset
description, current-year amounts are cumulative from 1 January to the end of the
given month. They cover taxes and duties paid to VMI's budget accounts, not Sodra
contributions, and are updated monthly.

## Licences

Checked on each dataset's data.gov.lt page on 2026-10-13:

| Data | Dataset | Licence |
|---|---|---|
| Legal Entities Register (JAR) | [1484](https://data.gov.lt/datasets/1484/) | CC BY 4.0 |
| VMI taxpayer register (VAT) | [607](https://data.gov.lt/datasets/607/) | CC BY 4.0 |
| Taxes paid by legal entities | [673](https://data.gov.lt/datasets/673/) | CC BY 4.0 |
| Register of Legal Acts (TAR) | [2613](https://data.gov.lt/datasets/2613/) | CC BY 4.0; the acts themselves are not protected by copyright |
| Euro exchange rates | ECB reference rates published by Lietuvos bankas | attribute the source |

CC BY 4.0 requires attribution, which every envelope carries in `source_name`,
`source_url` and `licence`.

## Transports

Streamable HTTP (default), on `MCP_HOST`/`MCP_PORT` (`0.0.0.0:8000` by
default), with `/mcp` as the endpoint and `/health` for probes:

```bash
python -m mcp_server --transport http
```

stdio, for local clients:

```bash
python -m mcp_server --transport stdio
```

A stdio client config for Claude Desktop or Cursor, with `cwd` set to the
checkout:

```json
{
  "mcpServers": {
    "lietuva-gov": {
      "command": "python",
      "args": ["-m", "mcp_server", "--transport", "stdio"],
      "cwd": "/path/to/lietuva-chat"
    }
  }
}
```

## Auth and limits

Two tiers, enforced by pure ASGI middleware on the `/mcp` path:

- **Anonymous** (no key): `MCP_ANON_RPM` / `MCP_ANON_RPD` requests per client
  IP, 30/min and 500/day by default.
- **API key** (`Authorization: Bearer <key>` or `X-API-Key: <key>`):
  `MCP_KEY_RPM` / `MCP_KEY_RPD`, 300/min and 20000/day by default.

An invalid key is rejected with `401`; exceeding a limit gives `429` with a
`Retry-After` header.

Issue a key with:

```bash
python -m mcp_server.keys new
```

It prints the key (`lk_…`) and its sha256 hash. Give the key to the client and
put **only the hash** in `MCP_API_KEY_HASHES` (comma-separated). Raw keys are
never stored.

The client IP is the **right-most** `X-Forwarded-For` entry, the one the reverse proxy
appends (entries to its left come from the client and are ignored). This needs a proxy
that appends the caller's address. If the server is exposed directly, set
`MCP_TRUST_PROXY=0` so the TCP peer address is used instead.

The rate-limit counters are in memory, per container, so run **one replica**;
scaling out needs shared counters (Redis).

## Upstream protection

We are a guest on government infrastructure:

- a per-source minimum interval between our calls — 0.2 s for `data.gov.lt`,
  0.5 s for `lb.lt`;
- retries with backoff on `429` and `5xx` (and on transport errors);
- `User-Agent: lietuva.chat-mcp/0.1 (+https://lietuva.chat)` on every request.

## Privacy

Tools accept **company codes only** (7–9 digits). An 11-digit personal code
(*asmens kodas*) is refused before any upstream request — as a company code, and
anywhere inside free text sent to JAR, TAR or web search — and the refusal message does not
repeat it, so it never reaches a log either. User text reaches an upstream query only through a sanitizer
(letters, digits, spaces and a small punctuation set) or a strict validator, so
query syntax cannot be injected.

## Chat app integration

The Business and Tax assistants get these tools as LangChain tools from
`tools/mcp_tools.py`:

- **In-process by default** — with no `LIETUVA_MCP_URL`, the tools call the same
  functions directly, so local development needs no server.
- **Remote** — set `LIETUVA_MCP_URL` (e.g. `https://mcp.lietuva.chat/mcp`) to
  call a deployed server over streamable HTTP, sending `LIETUVA_MCP_API_KEY` as
  a bearer token when present.

The Business assistant gets `company_search`, `company_details`,
`company_tax_data`, `law_search`, `law_consolidated` and `exchange_rate`. The
Tax assistant gets `company_tax_data`, `law_search`, `law_consolidated` and
`exchange_rate`.

## Tests

The fixture suite runs offline, with no network and no patched modules
(upstreams are faked through the injected transport seam):

```bash
pytest tests/test_mcp_*.py -q
```

The live smoke test hits the real upstreams and is skipped unless
`--run-integration` is given:

```bash
pytest tests/test_mcp_live.py --run-integration -q
```

Run it when you suspect a recorded fixture has gone stale. If one fails, the
upstream changed: compare it with "Verified upstream facts" in
`docs/superpowers/plans/2026-10-13-lietuva-mcp-server.md` and report the difference — do not edit the assertion to make it pass.

## Deployment

Deploy `Dockerfile.mcp` as its own service; see `docker-compose.mcp.yaml`.

## Open questions

1. **Bank of Lithuania terms:** lb.lt returns 403 to scripts, so its own reuse
   terms were not read. The rates are the ECB's euro reference rates; check
   lb.lt by hand before the public launch.
2. **Dataset 607 ↔ `mm_registras`:** matched by title and publisher (VMI); the
   page does not name the model path.
3. **Deployment:** the host, the DNS record for `mcp.lietuva.chat` and a CI
   deploy hook are not set up yet.
4. **Later tools,** if an assistant needs them:
   - weather (api.meteo.lt: CC BY-SA 4.0, 180 requests/min/IP, credit LHMT);
   - Statistics Lithuania (SDMX);
   - the address register;
   - procurement (vpt);
   - the data.gov.lt catalogue search.
