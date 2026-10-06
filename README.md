# lietuva.chat

**An independent AI assistant for living, working and dealing with the state in Lithuania.**

Ask a question in plain language about residence permits, taxes and Sodra, health insurance,
starting a company, family matters or moving back home. A specialist assistant answers,
grounded in **official Lithuanian sources**, with links so you can check each step.

> lietuva.chat is an independent project. It is **not** a government service and is not
> affiliated with the Government of Lithuania.

## Assistants

| Assistant | Covers | Main sources |
| --- | --- | --- |
| **Business & company** | UAB, MB, individual activity, e-resident status | registrucentras.lt, vmi.lt, migracija.lt |
| **Living & moving** | residence permits, MIGRIS, declaring residence, settling in | migracija.lt, epaslaugos.lt |
| **Taxes & finance** | income tax (GPM), Sodra contributions, health insurance (PSD), declarations | vmi.lt, sodra.lt |
| **Digital ID & e-services** | Smart-ID, Mobile-ID, ID card e-signature, epaslaugos.lt | epaslaugos.lt |
| **Public services** | health (VLK), education, family benefits, voting, municipalities | ligoniukasa.lrv.lt, vrk.lt |
| **Discover Lithuania** | Lithuania overview, culture, Lithuanians abroad | globalilietuva.urm.lt, lietuva.lt |

A router dispatches each question by prefix → keyword heuristics → LLM fallback.
Every assistant grounds factual answers with live **Exa** web search restricted to
official Lithuanian domains (`tools/search.py`), and cites its sources.

## Stack

- **FastHTML**: server-rendered UI (see `DESIGN.md`)
- **LangGraph**: multi-agent ReAct orchestration
- **xAI Grok**: LLM (configurable to OpenAI via `LLM_PROVIDER`)
- **Exa**: live web search grounding
- **PostgreSQL**: chat history and users (optional; the app runs without login)
- Lithuanian and English content, more languages via the switcher

## Running locally

```bash
uv venv && uv pip install -r requirements.txt   # or: pip install -r requirements.txt
cp .env.example .env    # set XAI_API_KEY and EXA_API_KEY
python main.py          # serves on http://localhost:5011
```

Required environment variables (see `.env.example`):

- `XAI_API_KEY` (or `OPENAI_API_KEY` with `LLM_PROVIDER=openai`)
- `EXA_API_KEY` — for grounded web search
- `DB_URL` — optional; needed only for saved chat history and login

## Disclaimer

Answers are AI-generated from public sources and may be incomplete or out of date.
Always confirm with the official source before acting. This is not legal advice.
