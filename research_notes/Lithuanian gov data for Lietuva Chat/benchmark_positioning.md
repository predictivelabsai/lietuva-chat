# Government AI Chat Portals: Benchmark and Positioning for Lietuva Chat

## What is "america.gov"? (launch, vendor, features, privacy, criticism)

### Takeaway
"america.gov" is real and verified: America.gov, launched by the Trump administration on 29 September 2026. It is an AI search-and-referral chatbot across about 29,000 federal websites, built on Google Gemini with xAI Grok also used. At launch it only gave information and pointed users to other sites. Transactions are promised for 2027. Critics say it mostly links out and solves "the easiest 5%" of the problem.

### Cited Findings
- Launched 29 Sep 2026 by the Trump administration. Joe Gebbia (U.S. Chief Design Officer) led it. An executive order was signed at the launch event at the Andrew W. Mellon Auditorium — [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/)
- Tagline: "Whatever you need from government, start here." Pitched as a one-stop shop for federal questions — [Yahoo/News](https://www.yahoo.com/news/politics/articles/u-government-just-launched-ai-154507187.html); [NBC News](https://www.nbcnews.com/tech/tech-news/trump-america-gov-ai-chatbot-often-links-clinton-era-website-rcna600540)
- Officials framed it as "one front door for every single question", so people no longer search through "tens of thousands of government websites" — [TechCrunch](https://techcrunch.com/2026/09/29/can-a-chatbot-fix-the-government-maze-the-white-house-is-about-to-find-out/)
- Models: Google confirmed it is a partner and that Gemini is involved. Gebbia said Grok (xAI) was also used — [TechCrunch](https://techcrunch.com/2026/09/29/can-a-chatbot-fix-the-government-maze-the-white-house-is-about-to-find-out/); [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/)
- Scope: it searches about 29,000 government websites and gives plain-language answers grounded in official sources. Launch examples were Medicare eligibility, passports and federal jobs. Answers mostly direct users to existing agency sites — [Yahoo/News](https://www.yahoo.com/news/politics/articles/u-government-just-launched-ai-154507187.html)
- FedScoop also lists Social Security card replacement and national-park camping reservations among the covered topics — [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/)
- It cannot complete transactions. Direct Medicare enrollment, passport applications and federal job applications are "planned features, not available functions" — [Yahoo/News](https://www.yahoo.com/news/politics/articles/u-government-just-launched-ai-154507187.html). FedScoop says transactions and application-status tracking are planned for 2027 — [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/)
- Privacy: no account is needed. Queries are cached temporarily as a hash rather than as full prompt text — [Yahoo/News](https://www.yahoo.com/news/politics/articles/u-government-just-launched-ai-154507187.html). The privacy notice says "AI providers do not retain your prompts or responses" and responses are cached for up to two hours. Users are told to "share only what's needed" — [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/)
- Login.gov: FedScoop reports it as integrated. Yahoo says it is only "contemplated" for future identity-verified workflows, and that launch materials did not explain how this fits with the anonymous approach. The two sources partly conflict on the current status — [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/); [Yahoo/News](https://www.yahoo.com/news/politics/articles/u-government-just-launched-ai-154507187.html)
- Criticism: former USDS administrator Mikey Dickerson said it is "solving the easiest 5% of the problem" — [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/)
- Criticism: it often links to an existing federal site that dates from the Clinton era (about 26 years old, likely USA.gov/FirstGov). Its answers sometimes say less than the source sites — [NBC News](https://www.nbcnews.com/tech/tech-news/trump-america-gov-ai-chatbot-often-links-clinton-era-website-rcna600540)
- Criticism: hallucination risk for high-stakes topics (food stamps, visa renewals, taxes), where a wrong answer can mean missed deadlines or denied benefits. Some replies to off-topic queries (Minecraft) were "really weird" — [TechCrunch](https://techcrunch.com/2026/09/29/can-a-chatbot-fix-the-government-maze-the-white-house-is-about-to-find-out/)
- Not the same product as USAi (usai.gov). USAi is GSA's internal platform for federal employees, launched in August 2025. It offers models from Anthropic, OpenAI, Google and Meta — [GSA](https://www.gsa.gov/about-gsa/newsroom/news-releases/gsa-launches-usai-to-advance-white-house-americas-ai-action-plan-08142025). It is now paid ("platform fee plus passthrough usage costs") — [FedScoop](https://fedscoop.com/usai-is-no-longer-free-for-federal-agencies/)

### Inferences
- America.gov confirms that the format Lietuva Chat uses (answers grounded in official sources, with links out) is now mainstream at the top level of government. It also shows the format is easy to criticise as "a fancy search box" when it cannot do anything.
- Using a frontier model (Gemini/Grok) plus retrieval over official sites is the same stack Lietuva Chat uses (Grok and Exa grounding). The difference will come from scope, language and audience, not from the technology.

### Gaps
- Language support could not be confirmed (for example, whether Spanish works). None of the fetched sources said.
- No independent accuracy benchmark had been published at the time of writing (launch was 2 days earlier).
- The NBC article body was truncated in the fetch, so details of the critique beyond the headline are incomplete.

## Other comparators (GOV.UK Chat, Bürokratt, Diia.AI, mObywatel, Singapore, UAE, Latvia)

### Takeaway
Three models exist. (1) Information-only RAG over official content: GOV.UK Chat, mObywatel's assistant and America.gov. (2) Transactional agents connected to state registers: Diia.AI and Abu Dhabi's TAMM. (3) A federated network of agency bots: Bürokratt. Every state product covers a single country and its national registers. Several of them require sign-in or an app.

### Cited Findings
- **GOV.UK Chat (UK):** soft launch 26 Mar 2026, official launch 14 May 2026. Available only in the GOV.UK mobile app. Covers about 80,000 pages of guidance. Signposts users to the original guidance, gives no legal advice, filters personal information and was tested with the AI Security Institute. More than 7,800 users and 15,000 questions during the soft launch. Web rollout is planned — [GDS blog](https://gds.blog.gov.uk/2026/05/14/gov-uk-chat-launches/)
- GOV.UK Chat needs a GOV.UK One Login sign-in. Its accuracy target is 90% — [search summary of RSN / Tax Adviser coverage](https://rsnonline.org.uk/new-ai-powered-govuk-chat-tool-launched/). Tax bodies and charities raised concerns about misleading tax answers and about excluding people — [LITRG](https://www.litrg.org.uk/news/new-govuk-chatbot-can-you-rely-it-tax-information); [Resultsense](https://www.resultsense.com/news/2026-05-22-govuk-chat-launch-accessibility-concerns/)
- **Diia.AI (Ukraine):** launched September 2025 and billed as the first national government AI agent. Works by text or voice. Checks which services a user is eligible for, reads register data, and issues documents (an income certificate at launch). Built on Google Gemini. Over 5.5M users of its features in the app and over 1M in active dialogue — [GovInsider](https://govinsider.asia/intl-en/article/ukraine-launches-worlds-first-government-ai-agent); [Apolitical](https://apolitical.co/en/navigator/case-studies/diia-ai-ukraine-s-national-ai-assistant-for-government-services); voice expanded in July 2026 — [Biometric Update](https://www.biometricupdate.com/202607/ukraine-expands-diia-ai-with-voice-based-access-to-government-services)
- **mObywatel (Poland):** a virtual assistant built on the Polish PLLuM model, available to all app users since 31 Dec 2025 after a beta with 5% of users. It translates bureaucratic jargon and routes users to the right form. It refuses off-topic questions. It is anonymous and cannot see the user's mObywatel data — [iMagazine](https://imagazine.pl/2026/01/02/mobywatel-wchodzi-w-2026-rok-z-polskim-ai/); [ITwiz](https://itwiz.pl/asystent-ai-dostepny-w-mobywatelu/)
- **Bürokratt (Estonia):** an interoperable network of public-sector chatbots in which agencies embed one shared assistant — [e-Estonia](https://e-estonia.com/estonias-new-virtual-assistant-aims-to-rewrite-the-way-people-interact-with-public-services/); [OECD.AI](https://oecd.ai/en/dashboards/policy-initiatives/burokratt-government-ai-virtual-assisstant-1627). Estonia is also looking at cross-border interoperability — [GovInsider](https://govinsider.asia/intl-en/article/estonia-eyes-cross-border-interoperability-for-burokratt-its-siri-of-public-services). (Claims of "Bürokratt 2.0" and "50+ agency sites" came only from low-quality blogs on lync.me and are not relied on here.)
- **TAMM (Abu Dhabi, UAE):** TAMM 3.0, launched at GITEX 2024, puts a generative AI assistant at the centre of 940+ services. Reported 400k+ users, 1M+ messages and 95% of requests handled autonomously (self-reported) — [ITU WSIS](https://www.itu.int/net4/wsis/stocktaking/Prizes/Prizes/Details/17391993737703194)
- **Singapore Pair:** a tool for civil servants, not citizens. OGP has rolled it out since mid-2023 — [OGP](https://reports.open.gov.sg/pair); [UNDP](https://www.undp.org/policy-centre/singapore/blog/pairing-ai-public-sector-impact-singapore)

### Inferences
- The state assistants that people praise most are transactional (Diia.AI, TAMM). An independent assistant cannot match that because it has no access to state registers. It should compete on breadth, neutrality and audience instead.
- The UK and Polish assistants refuse off-topic questions and stick to one government's content. Questions that span bodies or borders (for example, a Lithuanian living in Ireland asking about Sodra pension plus Irish PRSI) fall outside their design.

### Gaps
- **Latvia:** not researched within the time budget. No findings on a Latvian national AI assistant (the latvija.gov.lv portal's assistant status is unknown).
- Singapore's citizen-facing generative assistant (as distinct from the internal Pair) was not confirmed.
- Model vendor for GOV.UK Chat is not given in the GDS post.

## Lithuania: what the state has done or plans

### Takeaway
Lithuania has only rule-based or NLU agency chatbots, no national generative citizen assistant. Examples are viLTė (the COVID-era government virtual agent, in Lithuanian and English), VMI's "Simas" built by Tilde (since 2021) and a beta chatbot at the healthcare accreditation service. The new National AI Strategic Guidelines 2026–2035 aim for "systematic" public-sector AI but do not specifically promise a citizen assistant. Open Lithuanian LLMs were released in 2026 and could be used to build one.

### Cited Findings
- viLTė: a government AI virtual agent that answers in Lithuanian or English on COVID rules, travel, support for entrepreneurs, unemployment and similar topics — [EIM, Artificial Intelligence page](https://eimin.lrv.lt/en/sector-activities/digital-policy/artificial-intelligence/)
- VMI "Simas": launched December 2021, built by Tilde, in Lithuanian. It handled 94,000+ inquiries and engaged 33,000+ consumers in its first five months. Topics include land and real-estate tax, individual activity, business certificates and fines — [Tilde case study](https://tilde.ai/case-study/artificial-intelligence-programs-used-to-consult-the-public-in-lithuania/)
- The State Consumer Rights Protection Authority is developing a "Virtual Market Assistant" — [Interoperable Europe](https://interoperable-europe.ec.europa.eu/collection/public-sector-tech-watch/protecting-consumers-age-ai-lithuanian-case)
- VASPVT (healthcare accreditation) released a beta chatbot that uses a Lithuanian NLU model and copes with missing diacritics — [VASPVT](https://vaspvt.lrv.lt/lt/naujienos/netrukus-akreditavimo-tarnyba-pristatys-ismanuji-pokalbiu-robota-CRc/)
- National AI Strategic Guidelines 2026–2035 come from EIM, the Innovation Agency, VSSA and the GovAI Competence Center. One of the four pillars is AI for public services, with "a more active role for the state." The document does not specifically address citizen-facing assistants. It lists preserving the Lithuanian language as a priority — [EU Digital Skills & Jobs](https://digital-skills-jobs.europa.eu/en/initiatives/national-strategies/lithuania-national-artificial-intelligence-strategic-guidelines)
- GovAI is the public-sector AI competence centre. It offers consulting, training and a sandbox — [EIM](https://eimin.lrv.lt/en/sector-activities/digital-policy/artificial-intelligence/)
- A 2024 Seimas resolution requires a human in the loop for state AI: no decision affecting a citizen's rights may be made solely by an algorithm — [infoerdve.lt](https://infoerdve.lt/en/lithuania-outlines-vision-for-ai-driven-digital-governance) (secondary source)
- A Lithuanian LLM based on the Llama 3 architecture was trained from scratch on the General Lithuanian Language Corpus (3.9B words) between Dec 2024 and Apr 2026. It is open on Hugging Face and CLARIN-LT — [VDU](https://sitti.vdu.lt/bendrasis-lietuviu-kalbos-tekstynas-ir-vektorizuoti-modeliai/); [VSSA](https://vssa.lrv.lt/lt/naujienos/sukurtas-pirmasis-lietuviu-kalbos-dirbtinio-intelekto-modelis-lietuviu-tyreju-zingsnis-i-di-ateiti-yx9/); [Alkas](https://alkas.lt/2026/07/29/sukurtas-lietuviu-kalbos-tekstynas-ir-du-dirbtinio-intelekto-modeliai/)
- Neurotechnology released a Lithuanian LLM — [technologijos.lt](https://m.technologijos.lt/cat/1/article/S-174000)
- Help for foreigners is mainly human-delivered. International House Vilnius (Go Vilnius + Work in Lithuania, since 2021) is a free one-stop centre covering permits, employment, social insurance and taxes. It reports 49,000+ clients. No chatbot was found — [InterregEurope](https://www.interregeurope.eu/good-practices/international-house-vilnius-one-stop-service-centre-for-international-talents); [ihvilnius.lt](https://ihvilnius.lt/)

### Inferences
- There is no Lithuanian equivalent of America.gov, GOV.UK Chat or mObywatel. The state assistants are scattered, single-agency and pre-LLM. That leaves a cross-agency, conversational gap that is open now. Given the strategy and the new Lithuanian LLMs, the state could fill it within a few years.
- Because of the human-in-the-loop rule, a state assistant would probably stay informational, which is the same lane an independent assistant occupies.

### Gaps
- No confirmed chatbot or AI assistant for Sodra, Migracijos departamentas (MIGRIS) or epaslaugos.lt in the sources found. Absence is not confirmed either.
- No public tender for a national citizen AI assistant was found (CVP IS was not searched).
- No private AI competitor aimed at foreigners or diaspora in Lithuania was found. Search coverage was light (wizeai.com and Tilde are B2G/B2B vendors, not consumer assistants).
- Current status of viLTė (whether it is still live) was not verified.

## Positioning: gaps an independent Lietuva Chat could fill

### Takeaway
Lietuva Chat should be the cross-agency, multilingual, cited assistant for people the national systems serve poorly: foreigners and relocators, the diaspora, and anyone whose question spans VMI, Sodra, the Migration Department and municipalities. It should not try to match transactional state agents.

### Cited Findings
- State assistants are confined to one government's content and refuse off-topic questions (mObywatel), or require an app and sign-in (GOV.UK Chat: app plus One Login) — [ITwiz](https://itwiz.pl/asystent-ai-dostepny-w-mobywatelu/); [GDS](https://gds.blog.gov.uk/2026/05/14/gov-uk-chat-launches/)
- Users valued plain-English questions and direct links back to the source guidance — [GDS](https://gds.blog.gov.uk/2026/05/14/gov-uk-chat-launches/)
- The main criticisms of state chatbots are that they only link out ("easiest 5%"), give thin answers and hallucinate on high-stakes topics — [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/); [NBC](https://www.nbcnews.com/tech/tech-news/trump-america-gov-ai-chatbot-often-links-clinton-era-website-rcna600540); [TechCrunch](https://techcrunch.com/2026/09/29/can-a-chatbot-fix-the-government-maze-the-white-house-is-about-to-find-out/)
- The privacy stance that worked elsewhere: anonymous by default (mObywatel, America.gov) with no prompt retention (America.gov) — [ITwiz](https://itwiz.pl/asystent-ai-dostepny-w-mobywatelu/); [FedScoop](https://fedscoop.com/trump-launches-ai-site-america-gov/)
- Lithuanian state bots operate only in Lithuanian or Lithuanian and English (Simas, viLTė) — [Tilde](https://tilde.ai/case-study/artificial-intelligence-programs-used-to-consult-the-public-in-lithuania/); [EIM](https://eimin.lrv.lt/en/sector-activities/digital-policy/artificial-intelligence/)

### Inferences
- **Languages:** offer LT, EN, RU, UK (there are large Ukrainian and Belarusian communities, and Russian is common among relocators) and possibly PL. Lithuanian state bots offer only LT or LT+EN.
- **Cross-agency answers:** combine VMI, Sodra, Migracijos departamentas, Užimtumo tarnyba and municipalities in one answer. This is the "maze" America.gov claims to solve, which nobody in Lithuania does with AI.
- **Diaspora focus:** cover dual citizenship, voting abroad, pensions and social security across EU states, returning-migrant support, and Lithuanian language for children. No national system targets these cross-border questions.
- **Citations and freshness:** link every claim to lrv.lt, vmi.lt, sodra.lt or migracija.lt with a date checked. This answers the main criticism of America.gov and GOV.UK Chat and fits the human-in-the-loop culture.
- **Privacy:** no login, no prompt retention by default, EU hosting. The state assistants now set this as the baseline, so it is required rather than optional.
- **Honest framing:** say clearly that it is independent and non-governmental. Do not imply official status (America.gov's credibility comes from the .gov domain, which Lietuva Chat must not imitate). Escalate to official channels such as International House Vilnius, VMI and Sodra for case-specific decisions.
- **Risk:** if the GovAI / VSSA strategy produces a free national assistant (for example, on the open Lithuanian LLM), the general Lithuanian-language citizen use case shrinks. The foreigner and diaspora niches and the multilingual, cross-border scope are the most defensible.

### Gaps
- No user-demand data for Lithuania (for example, query volumes from foreigners or diaspora size by country) was gathered in this pass.
- Accuracy of competing assistants on Lithuanian-specific questions has not been tested.
