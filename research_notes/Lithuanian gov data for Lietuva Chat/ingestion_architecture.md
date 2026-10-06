# Ingestion, indexing and freshness architecture for a Lithuanian-government RAG assistant

Scope note: about 17 tool calls were used. Several numbers below come from vendor or competitor blogs, and these are flagged where they appear. Prices that come from training knowledge rather than a fetched page are labelled "unverified".

## 1. Live search (Exa + domain allowlist) vs owned index (pgvector) vs hybrid

### Takeaway
Production government chatbots such as GOV.UK Chat and Bürokratt keep their own index of chunked authoritative content, with metadata-aware re-ranking. They do not use open web search. Exa with `includeDomains` and `maxAgeHours` is a cheap fallback for freshness and coverage alongside that index. The usual recommendation is hybrid: an owned index for the core corpus, plus live allowlisted search for gaps and for checking volatile facts.

### Cited Findings
- GOV.UK Chat is a RAG system grounded only in GOV.UK content. It rephrases the question, retrieves chunks from OpenSearch (vector retrieval), then calls Claude through Bedrock. Embeddings use Amazon Titan. — [deepwiki alphagov/govuk-chat](https://deepwiki.com/alphagov/govuk-chat); [GOV.UK Chat ADR 0001](https://docs.publishing.service.gov.uk/repos/govuk-chat/adr/0001-pilot-technical-architecture.html); [AI Knowledge Hub](https://ai.gov.uk/knowledge-hub/tools/gov.uk-chat/)
- GOV.UK Chat uses "hierarchical semantic chunking, splitting pages into coherent sections while preserving the HTML header structure". Retrieval is semantic search plus a "metadata-based re-ranking layer" built with content designers. The team tried hybrid search and cross-encoder re-ranking, and says retrieval is "still being actively developed". — [Inside GOV.UK blog, May 2026](https://insidegovuk.blog.gov.uk/2026/05/15/developing-gov-uk-chat-our-data-science-and-ai-engineering-journey/)
- GOV.UK Chat started with LangChain and Gradio and later moved to a Ruby/AWS stack. — [deepwiki](https://deepwiki.com/alphagov/govuk-chat)
- Estonia's Bürokratt has a Common Knowledge Base (CKB) project: an agency supplies a webpage through a UI, and the page is scraped and cleaned. It also has a BYK-RAG module that works with several LLM providers. The code is MIT-licensed. — [Bürokratt blueprint gist](https://gist.github.com/ottomattas/7921aafbefe02ae2e05003429b758c4c); [OSOR case study](https://interoperable-europe.ec.europa.eu/collection/open-source-observatory-osor/document/digital-public-services-based-open-source-case-study-burokratt); [kratid.ee](https://www.kratid.ee/en/burokratt)
- Exa `includeDomains` restricts search to the listed domains. It cannot be combined with `excludeDomains`. `livecrawl` is deprecated in favour of `maxAgeHours`: 0 means always fetch fresh, a positive value means use the cache if it is newer than N hours (maximum 720), and -1 means cache only. — [Exa Contents docs](https://exa.ai/docs/reference/get-contents); [Exa contents guide](https://exa.ai/docs/reference/contents-api-guide-for-coding-agents)
- Exa's advice is to omit `maxAgeHours` for most requests and set it only where stale content is unusable (prices and other frequently updated pages). Pair `maxAgeHours: 0` with `livecrawlTimeout` (default 10,000 ms; 12–15 s for slow sites). The contents API supports `subpages` and `subpageTarget` crawling. — [Exa contents best practices](https://exa.ai/docs/reference/contents-best-practices)
- Exa also offers "Monitors", a create/update API for watching for new content. — [Exa monitors](https://exa.ai/docs/reference/monitors/create-a-monitor)
- 2026 Exa pricing, from third-party pages that were not checked against Exa's own pricing page: Search costs $7 per 1k requests for up to 10 results, plus $1 per 1k for each extra result. Contents costs $1 per 1k pages per content type. Answer costs $5 per 1k, Deep Search $12–15 per 1k, and Monitors $15 per 1k. The base search price rose from $5 to $7. — [tinyfish](https://www.tinyfish.ai/blog/exa-pricing); [keirolabs](https://keirolabs.cloud/blog/exa-api-pricing-2026). Exa's own docs separately confirm "$1/1000 pages". — [Exa best practices](https://exa.ai/docs/reference/contents-best-practices)

### Inferences
- A live-search-only design gives no control over what is in scope. Coverage of small .lt agency sites in Exa's index is unknown, ranking is not tunable, and article-level legal citation is impossible. An owned index gives determinism, version history and article-level citation, which the government examples above rely on.
- Recommended hybrid for this app, which already uses LangGraph and optional Postgres:
  1. Primary: pgvector plus Postgres full-text search over a crawled allowlist (lrv.lt ministries, vmi.lt, sodra.lt, migracija.lt, e-tar.lt consolidated acts, epaslaugos.lt, keliauk/lithuania.lt, registrucentras.lt and similar).
  2. Secondary: an Exa search restricted with `includeDomains` to the same allowlist. Run it when owned retrieval scores fall below a threshold or the query is time-sensitive ("2026 minimum wage").
  3. Optional: `maxAgeHours: 0` re-fetch of the one or two cited source pages at answer time, for volatile facts.
- At about $7 per 1k searches, Exa fallback costs about $7 per 1k fallback queries. That is cheap next to LLM tokens, so cost is not the reason to own an index. Control, citation granularity and evaluability are.

### Gaps
- I found no public engineering write-up for Singapore's Pair or for US federal RAG pilots within the call budget.
- How completely Exa indexes Lithuanian .lt government subdomains is untested. Run 50 known-answer queries before relying on it.

## 2. Crawling: politeness, change detection, PDFs, diacritics, tools

### Takeaway
For gov sites, a self-hosted crawl that starts from sitemaps is cheap and controllable: Scrapy or a plain httpx loop, then trafilatura or Crawl4AI for HTML-to-markdown, and a PDF extractor. Change detection uses conditional GETs (ETag/Last-Modified) with a normalized-content-hash fallback. Legislation should come from the TAR open-data feed, not from scraping e-tar.lt.

### Cited Findings
- Firecrawl is a managed, API-first service. Crawl4AI is an open-source Python crawler you self-host, with the lowest cost at volume. Both output LLM-ready markdown. — [Firecrawl vs Crawl4AI (vendor page, biased)](https://www.firecrawl.dev/alternatives/firecrawl-vs-crawl4ai)
- A competitor's benchmark on 1,000 URLs reported markdown-for-RAG Recall@5 of Spider 91.5%, Firecrawl 89.0% and Crawl4AI 84.5%. Throughput was 74, 16 and 12 pages/s. On anti-bot-protected URLs, success rates were 99.6%, 88.4% and 72.0%. — [spider.cloud benchmark (published by a competitor; treat as biased)](https://spider.cloud/blog/firecrawl-vs-crawl4ai-vs-spider-honest-benchmark/)
- Trafilatura is cited as having "the highest F1 in the standard benchmark" for HTML-to-text/markdown extraction at scale. — [roundproxies (secondary)](https://roundproxies.com/blog/best-firecrawl-alternatives/)
- Lithuanian legislation is available as open data. The State Data Agency (VDA) and the Seimas Chancellery opened TAR data in open-data format, and the dataset has two models: documents and their consolidated versions. — [VDA announcement](https://vda.lrv.lt/lt/naujienos/valstybes-duomenu-agentura-ir-seimo-kanceliarija-teises-aktu-duomenis-atvere-inovacijoms-dabar-pasiekiami-atviru-duomenu-formatu/); [data.gov.lt dataset 2613](https://data.gov.lt/datasets/2613/) (WebFetch returned 403, so the dataset page itself was not inspected)
- TAR also has a system-integration API specification (DOK-6.1, v1.4). — [lrs.lt](https://www.lrs.lt/sip/getFile3?p_fid=32584)
- legalize.dev offers 15,088+ Lithuanian laws with amendment history as a free JSON REST API, derived from TAR data under CC BY 4.0. — [legalize.dev/lt](https://legalize.dev/lt) (third party; reliability not checked)

### Inferences
- The gov allowlist is probably low-thousands to tens of thousands of HTML pages plus PDFs. Gov sites seldom have anti-bot protection, so a managed crawler's main advantage (anti-bot success) matters less here. Self-hosted Crawl4AI or trafilatura is likely enough. Firecrawl is only worth it if the team wants zero ops.
- Polite crawling defaults (standard practice, not sourced here): respect robots.txt, one or two concurrent requests per host, a crawl-delay of 1 s or more, an identifying User-Agent with a contact address, and seeding from sitemap.xml `<lastmod>`.
- Change detection: store `etag`, `last_modified` and `sha256(normalized_text)` for each URL. Send `If-None-Match`/`If-Modified-Since` and skip on 304. If the page returns 200, re-chunk and re-embed only when the hash changed. Many CMS pages send no validators, so the hash is the real gate.
- Diacritics: store text as UTF-8 NFC (ą č ę ė į š ų ū ž). Index keyword search both with and without diacritics (Postgres `unaccent`) because users often type "zemes mokestis" without them. Watch for PDFs with broken ToUnicode maps, which produce mojibake. Validate by checking the ratio of Lithuanian letters to replacement characters per document.

### Gaps
- The TAR open-data API's exact field schema (effective-from/to fields, update cadence) could not be verified because data.gov.lt returned 403. Inspect it manually.
- I found no Lithuanian-specific PDF extraction benchmark.

## 3. Legal texts: chunking by article, versioning, effective dates

### Takeaway
Treat each consolidated version (suvestinė redakcija) from TAR as a versioned document. Chunk on the legal structure (straipsnis/article → dalis/part → punktas/point), and store the validity interval and a stable article ID with each chunk. Retrieval then filters to the version in force on the relevant date.

### Cited Findings
- The TAR dataset separates documents from consolidated versions. — [VDA](https://vda.lrv.lt/lt/naujienos/valstybes-duomenu-agentura-ir-seimo-kanceliarija-teises-aktu-duomenis-atvere-inovacijoms-dabar-pasiekiami-atviru-duomenu-formatu/)
- GOV.UK Chat's structure-preserving hierarchical chunking (by headings) is the production precedent for structural chunking. — [Inside GOV.UK](https://insidegovuk.blog.gov.uk/2026/05/15/developing-gov-uk-chat-our-data-science-and-ai-engineering-journey/)
- On the legal-retrieval benchmark MLEB, text-embedding-3-large scored 78.91 and jina-embeddings-v4 78.62. MLEB is not Lithuanian. — [MLEB paper](https://arxiv.org/pdf/2510.19365)

### Inferences
- Suggested chunk schema: `act_id, act_title, version_id, valid_from, valid_to, article_no, part_no, heading_path, text, source_url`. Add a breadcrumb prefix to each chunk before embedding ("Gyventojų pajamų mokesčio įstatymas › 6 straipsnis › 2 dalis").
- Index only the consolidated versions currently in force by default. Keep historical versions for "what was the rule in 2024" questions.

### Gaps
- I found no paper on RAG over Lithuanian legislation specifically.

## 4. Lithuanian embeddings and hybrid retrieval

### Takeaway
No public Lithuanian retrieval benchmark turned up. Use BGE-M3 (open, dense+sparse, MIRACL-leading) or a top commercial multilingual model as the shortlist, and decide with a small in-house Lithuanian query set. Add Postgres full-text search, which ships a Snowball Lithuanian stemmer, as the BM25-style leg.

### Cited Findings
- BGE-M3 covers 100+ languages and provides dense, multi-vector and sparse retrieval in one model. On MIRACL (18 languages) it scored nDCG@10 70.0 in all modes, against about 65.4 for mE5. — [aimultiple (secondary summary of the BGE-M3 paper)](https://aimultiple.com/open-source-embedding-models)
- In one comparison, multilingual-e5-large scored nDCG@10 0.628 (R@10 79.38%) and BGE-M3 dense 0.614 (R@10 79.50%), which is close to a tie. — [aimultiple](https://aimultiple.com/open-source-embedding-models)
- jina-embeddings-v3 reports better results than multilingual-e5-large-instruct on all multilingual tasks in its paper. — [jina-v3 paper](https://arxiv.org/pdf/2409.10173)
- MTEB(Multilingual) and MTEB(Europe) contain 343 and 228 tasks. I found no per-language Lithuanian retrieval leaderboard. — [MMTEB](https://arxiv.org/html/2502.13595v3)
- National project: on 3 Nov 2025 the State Digital Solutions Agency (VSSA/SDSA), with VMU, Neurotechnology, Tilde Lietuva and Krilas, released LT-MLKM-modernBERT. It is a Lithuanian ModernBERT-base trained on the BLKT corpus: 1.87B words and 49B training tokens, including legal and public-sector text. It is a masked LM, not a ready-made retrieval embedder. — [HF model card](https://huggingface.co/VSSA-SDSA/LT-MLKM-modernBERT); [CLARIN-LT](https://clarin-lt.lt/?p=3237)
- PostgreSQL's source includes the Snowball Lithuanian stemmer (`stem_UTF_8_lithuanian.c`). — [postgres/postgres libstemmer](https://github.com/postgres/postgres/tree/master/src/backend/snowball/libstemmer). The current docs page does not list it explicitly. — [PG docs](https://www.postgresql.org/docs/current/textsearch-dictionaries.html). Uncertain: this was checked on master only. Confirm on the deployed version with `\dF lithuanian` or `SELECT to_tsvector('lithuanian','mokesčių')`.
- Postgres also supports Hunspell dictionaries (a Lithuanian Hunspell dictionary exists via OpenOffice) and the `unaccent` filter. — [PG docs](https://www.postgresql.org/docs/current/textsearch-dictionaries.html)

### Inferences
- Lithuanian is highly inflected (7 cases), so pure keyword search without stemming misses a lot, and dense vectors cover the gap. A hybrid of `tsvector('lithuanian')` and pgvector, fused with reciprocal rank fusion, is the low-ops default. BGE-M3's sparse output is an alternative to Postgres FTS.
- Cross-lingual matters: a Russian or English query should retrieve a Lithuanian source. Use a model that is strong cross-lingually (BGE-M3 on MKQA, or commercial multilingual models), or translate the query to Lithuanian before retrieval. Test both.
- Build a 100–200 query Lithuanian/English/Russian eval set with gold source URLs, and compare candidate models on Recall@10. A day of work replaces the missing public benchmark.

### Gaps
- No Lithuanian-specific retrieval numbers for OpenAI text-embedding-3, Cohere embed-v3/v4, Jina v3 or BGE-M3 were found.
- Model prices were not verified in this session. From training knowledge, unverified: OpenAI text-embedding-3-small ≈ $0.02/1M tokens and -large ≈ $0.13/1M. BGE-M3 is free to self-host.

## 5. Lithuanian LLMs/NLP and how frontier models handle Lithuanian

### Takeaway
Open Lithuanian LLMs exist (Neurotechnology Lt-Llama-2 7B/13B), but as general assistants they trail current frontier models. For generation, GPT-class proprietary models are the practical choice. I found no Lithuanian evaluation of Grok. Lithuanian fluency (grammatical case) remains a measurable weak spot.

### Cited Findings
- Neurotechnology released Lt-Llama-2 7B and 13B, trained on 14B Lithuanian tokens, together with a 13,848-pair Q/A dataset and translated benchmarks. On Arc, Hellaswag and Winogrande, LT-Llama2-13B ranked 4th of 8, and newer SOTA open models generally did better. On Lithuanian text-generation quality it had a 0.98% error rate against 3.44% for GPT-4o. — [Informatica 2025](https://www.informatica.vu.lt/journal/INFORMATICA/article/1372/text); [arXiv 2408.12963](https://arxiv.org/pdf/2408.12963); [HF](https://huggingface.co/neurotechnology/Lt-Llama-2-7b-hf)
- An evaluation of open-weight models for the Baltic languages found that proprietary models (GPT-4o) outperformed open models, and Lithuanian lagged Latvian and Estonian. — [arXiv 2501.03952](https://arxiv.org/pdf/2501.03952) (summarized by a fetch tool; exact numbers not extracted)
- On Lithuanian grammatical case marking (305 minimal pairs), LLM accuracy ranged from 0.662 to 0.852. Monolingual Lithuanian models beat multilingual ones. — [Jakubauskaitė & Alhama, LoResLM 2026](https://aclanthology.org/2026.loreslm-1.32/)
- Lithuania takes part in ALT-EDIC/LLMs4EU through the Ministry of Culture. — [ALT-EDIC](https://www.alt-edic.eu/projects/llms4eu/)

### Inferences
- Keep Grok or GPT for generation, but add a Lithuanian-fluency check to the eval set (case agreement, terminology). Prefer quoting source wording for legal and tax terms rather than letting the model paraphrase.

### Gaps
- I found no published Lithuanian benchmarks for Grok 3/4 or GPT-5-class models.

## 6. Freshness, citation, evaluation; cost and scale

### Takeaway
Store `fetched_at`, `last_changed_at` and `source_url` with every chunk and show "source · last checked <date>" in answers. Re-crawl volatile pages (tax rates, minimum wage, deadlines) daily and the rest weekly, using conditional GETs. Evaluate on GOV.UK's pattern: automated LLM-as-judge on a gold set, expert/red-team review, and live monitoring.

### Cited Findings
- GOV.UK Chat's evaluation has three pillars: automated (LLM-as-a-judge and custom metrics), manual (expert analysis, red teaming with AISI, content designers) and live monitoring. Its criteria are groundedness, relevance, factual accuracy, completeness, reliability and reputational safety. It has two layers of guardrails, before and after generation. About 70% of 2023 prototype users found it useful. — [Inside GOV.UK](https://insidegovuk.blog.gov.uk/2026/05/15/developing-gov-uk-chat-our-data-science-and-ai-engineering-journey/)
- Exa `maxAgeHours: 0` is the documented way to force a fresh fetch for prices and other volatile pages. — [Exa best practices](https://exa.ai/docs/reference/contents-best-practices)
- Exa Contents costs $1 per 1k pages. — [Exa](https://exa.ai/docs/reference/contents-best-practices)

### Inferences (cost and scale; arithmetic on stated assumptions)
- Assume 100k pages × ~1,500 tokens ≈ 150M tokens, or about 300k chunks at ~500 tokens each.
  - Embedding with OpenAI 3-small: 150M × $0.02/1M ≈ **$3** (price unverified). With 3-large: ≈ **$20**. BGE-M3 self-hosted: compute only. Re-embedding is limited to changed pages, so ongoing cost is negligible.
  - Fetching with Exa Contents instead of crawling: 100k × $1/1k = **$100 per full pass**. A daily pass over 2k volatile pages is about $2/day. A self-hosted crawl costs only bandwidth and time: at 1 req/s/host across ~30 hosts in parallel, 100k pages take about an hour of wall-clock.
  - Storage: 300k × 1536-dim float32 ≈ 1.8 GB raw vectors (≈ 0.6 GB at 512 dims, or with halfvec). This fits comfortably in one Postgres with an HNSW index; no separate vector DB is needed at this scale.
- Gold eval set: 150–300 Q/A pairs across LT/EN/RU, each with an expected source URL and the key fact. Re-run it on every index or model change, and score retrieval recall plus LLM-judge groundedness and correctness. Volatile facts (minimum wage, VAT, Sodra rates) go in a "canary" subset that is re-checked whenever the crawl detects a change on the source page.

### Gaps
- pgvector HNSW performance docs were not fetched. The storage figures are arithmetic (dims × 4 bytes), not measured.
- Embedding and LLM prices not verified in this session.
