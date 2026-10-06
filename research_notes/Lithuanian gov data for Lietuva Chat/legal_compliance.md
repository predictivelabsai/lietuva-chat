# Legal and compliance constraints for "Lietuva Chat" (private AI assistant over Lithuanian government content)

Scope note: Lithuania/EU, as of 2026-10-01. These are research notes, not legal advice. Items marked **[LAWYER]** need a Lithuanian-qualified lawyer. Several primary texts (e-tar.lt, e-seimas.lrs.lt) returned HTTP 403 or empty bodies to automated fetching, so some Lithuanian provisions are cited via secondary sources; this is flagged where it applies. EU primary-law URLs that are marked "not re-fetched" are standard EUR-Lex references whose cited content was not re-checked during this session.

## 1. Reuse rights: official texts, government web content, open data, database rights

### Takeaway
Lithuanian legal acts and official administrative documents, and their official translations, are excluded from copyright (Copyright Law Art. 5), so quoting and indexing them is low-risk. Ordinary government website content does not automatically fall under that exclusion: explainer articles, FAQs, photos and design may be copyrighted. Reuse of state-held data is governed by the Law on the Right to Obtain Information and Data Reuse (VIII-1524), which implements the Open Data Directive. Registers such as Registrų centras can carry sui generis database rights and contractual terms, so wholesale extraction from them is the riskiest activity.

### Cited Findings
- Lithuanian Law on Copyright and Related Rights No. VIII-1185, Art. 5, excludes from copyright protection: "legal acts, official documents texts of administrative, legal or regulative nature" (decisions, rulings, regulations, norms, territorial planning and other official documents) and their official translations (Art. 5(2)); "officially registered drafts of legal acts" (Art. 5(4)); "regular information reports on events" (Art. 5(5)); "ideas, procedures, processes ... or mere data" (Art. 5(1)); and "official State symbols and insignia (flags, coat-of-arms, anthems...)" (Art. 5(3)). — [Wikimedia Commons: Copyright rules – Lithuania](https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Lithuania); law text: [WIPO Lex, Law No. VIII-1185](https://wipolex.wipo.int/en/legislation/details/15422); official consolidated text: [e-seimas VIII-1185](https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/5f13b560b2b511e59010bea026bdb259)
- The Wikimedia/WIPO summary quotes the law as amended up to Law No. XII-1183 of 2014. Later amendments, including the 2022 DSM transposition, were not checked against Art. 5 in this session. — [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:Copyright_rules_by_territory/Lithuania)
- Quotation exceptions are in Copyright Law Art. 24(1). Its specific conditions were not retrieved. — [copyrightexceptions.eu – Lithuania](https://www.copyrightexceptions.eu/jurisdictions/lt/)
- Lithuania's open-data/PSI framework is the Law on the Right to Obtain Information and Data Reuse (Teisės gauti informaciją ir duomenų pakartotinio naudojimo įstatymas, No. VIII-1524). It was amended on 30 June 2021 by Law No. XIV-491 and implemented by Government Resolution No. 849 of 13 October 2021. — [e-tar.lt VIII-1524](https://www.e-tar.lt/portal/lt/legalAct/TAR.FA13E28615F6/asr); [e-seimas editions](https://e-seimas.lrs.lt/portal/legalActEditions/lt/TAD/TAIS.94745); [Infolex, Resolution 849](https://www.infolex.lt/ta/716436)
- Public-sector bodies must inventory the data they hold. Data may be published for reuse where that does not breach the law, and it is listed on the Lithuanian Open Data Portal (data.gov.lt), run by the State Digital Solutions Agency. — [data.gov.lt regulation page](https://data.gov.lt/more/regulation/regulation_legal/); [EIMIN open data](https://eimin.lrv.lt/lt/veiklos-sritys/skaitmenine-politika/atviri-duomenys-1/atviri-duomenys-3/)
- The Open Data Directive (EU) 2019/1024 covers reuse of public-sector information such as legal, statistical and land-registry information. It entered into force on 16 July 2019, with transposition due by 16 July 2021. — [EUR-Lex summary](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=LEGISSUM:4405374); [Directive text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32019L1024)
- Under Lithuanian law, sui generis database-maker rights protect a substantial investment in obtaining, verifying or presenting contents and last 15 years. The Lithuanian Supreme Court (LAT) has said infringement requires (1) extraction or reuse of a quantitatively or qualitatively substantial part and (2) a threat to the maker's interest in recovering its investment. — [LAT news on sui generis conditions](https://www.lat.lt/naujienos/lat-isaiskino-duomenu-baziu-gamintojo-sui-generis-teisiu-apsaugos-salygas/1610); [Database Directive 96/9/EC (LT)](https://eur-lex.europa.eu/eli/dir/1996/9/oj/lit/html)

### Inferences
- Laws, government resolutions, ministerial orders and official forms or decisions published on e-tar.lt are safe to ingest and quote verbatim (Art. 5(2)). Attributing them and linking to the official source is still good practice.
- Explanatory web pages on ministry, Migration Department (migracija.lt) or VMI sites may be copyrighted works rather than "official documents of administrative nature". Copying them verbatim at scale is a grey area. The lower-risk pattern is to index them, retrieve short passages, summarise, and always link back. **[LAWYER: whether ministry FAQ/explainer pages count as "official documents" under Art. 5(2)]**
- The Open Data Directive gives the strongest reuse basis only for datasets actually released on data.gov.lt or under an open licence. Prefer those datasets over scraping the same data from web pages.
- Registrų centras (company, real estate and address registers) has paid and contractual data services. Bulk extraction from its search UIs could conflict with both sui generis rights and its service terms. Use only open datasets on data.gov.lt, or link users to the official search instead of mirroring the registers. **[LAWYER if any register data is mirrored]**

### Gaps
- Could not retrieve the current consolidated text of VIII-1524 (e-tar returned 403). Not verified: whether reuse is free of charge, whether a source must be credited, the ban on distorting data, or the treatment of third-party IP and personal data.
- Did not retrieve site-specific terms of use for lrv.lt, migracija.lt, vmi.lt, sodra.lt or registrucentras.lt. Read each site's "Naudojimosi sąlygos" or "Autorių teisės" page before ingesting it.
- No source found on whether Lithuanian ministries license web content under CC-BY or a similar licence by default.

## 2. Crawling, robots.txt and text-and-data-mining (TDM) exceptions

### Takeaway
Lithuania transposed the DSM Directive with effect from 1 May 2022. DSM Art. 3 (research TDM) became Copyright Law Art. 22¹ and Art. 4 (general TDM, subject to opt-out) became Art. 22². A commercial chatbot can rely only on the Art. 22² general exception, so it must honour rights-holders' machine-readable opt-outs; robots.txt and TDM-reservation signals are the practical proxy. For official texts excluded by Art. 5, no copyright exception is needed.

### Cited Findings
- Seimas adopted the DSM transposition on 24 March 2022, and the amendments to the Copyright Law entered into force on 1 May 2022. — [Europeana: closer look at Lithuania](https://pro.europeana.eu/post/copyright-directive-series-a-closer-look-at-lithuania); [Petošević: Lithuania transposes the DSM Directive](https://www.petosevic.com/resources/news/2022/05/4618)
- DSM Art. 3 is implemented in Art. 22¹ and DSM Art. 4 in Art. 22² of Law No. VIII-1185. — [copyrightexceptions.eu – Lithuania](https://www.copyrightexceptions.eu/jurisdictions/lt/)
- Lithuania adopted the general TDM exception "with the possibility for rightsholders to prohibit the use of their materials in this way". The research exception is limited to research organisations and cultural heritage institutions for non-commercial research. — [Europeana](https://pro.europeana.eu/post/copyright-directive-series-a-closer-look-at-lithuania)
- DSM Art. 2(2) defines TDM as "any automated analytical technique aimed at analysing text and data in digital form to generate information which includes but is not limited to patterns, trends and correlations". — [Reed Smith: TDM in the EU](https://www.reedsmith.com/articles/entertainment-media-guide-to-ai-three-years-on/text-data-mining-in-the-eu/); [Directive 2019/790, not re-fetched](https://eur-lex.europa.eu/eli/dir/2019/790/oj)
- Under DSM Art. 4(3), the general exception applies only where use "has not been expressly reserved ... in an appropriate manner, such as machine-readable means in the case of content made publicly available online". — [Directive 2019/790 Art. 4(3), not re-fetched](https://eur-lex.europa.eu/eli/dir/2019/790/oj); [CMS: AI and copyright TDM exceptions](https://cms.law/en/bel/legal-updates/ai-and-copyright-exploring-exceptions-for-text-and-data-mining)

### Inferences
- A privately run, commercial or commercially capable service is not a "research organisation", so Art. 22¹ is unavailable. It relies on Art. 22², the opt-out-able general TDM exception.
- Mitigations:
  - Respect robots.txt and any TDM-reservation signals (meta tags, `TDMRep`, ai.txt) when crawling.
  - Use an identifiable User-Agent with a contact URL.
  - Rate-limit requests.
  - Log the fetch date and the robots.txt state at crawl time as evidence.
  - Keep provenance (URL and fetch timestamp) for every chunk.
- Retrieval-augmented generation (RAG) that stores copies and serves passages to users goes beyond pure "analysis". Displaying long verbatim extracts of copyrighted, non-official pages could fall outside TDM, which covers reproduction for mining and not communication to the public. Keep displayed quotes short and attributed, which also fits the quotation exception (Art. 24). **[LAWYER: whether RAG display of retrieved passages is covered by Art. 22² + Art. 24]**
- Official legal acts (Art. 5) need no TDM exception, so a robots.txt disallow on e-tar.lt is a terms-of-service and technical-courtesy issue rather than a copyright issue. Still, respect it and prefer the official API or open-data exports where they exist.

### Gaps
- Did not obtain the verbatim text of Art. 22² or any Lithuanian guidance on what counts as a valid "machine-readable" reservation.
- No Lithuanian case law on AI or TDM opt-outs was found. The German Kneschke v LAION decision (2024) is relevant comparative guidance but was not fetched here.

## 3. Naming and branding: "Lietuva", Vytis, the flag, and official look-alike risk

### Takeaway
State symbols are uncopyrighted (Art. 5(3)), but their use is regulated by dedicated laws. Trademark law bars registering marks made of the state's official or short name, its coat of arms or flag, or imitations of them, without a permit from the Minister of Justice. Using "Lietuva" in a domain or service name is not shown to be unlawful by itself. Combined with Vytis, the flag, gov-like styling or wording such as "official", however, it creates impersonation and unfair-commercial-practice risk. The safe pattern is no state heraldry, a clearly private visual identity, and a prominent "not affiliated" disclaimer.

### Cited Findings
- The Lithuanian Constitution defines the state coat of arms as a white Vytis on a red field and provides that the coat of arms, flag and their use are established by law. — [Seimas: Symbols of the Republic of Lithuania](https://www.lrs.lt/sip/portal.show?p_r=35580&p_k=2&p_a=1710&p_kade_id=10); [Constitutional Court: Constitution](https://lrkt.lt/en/about-the-court/legal-information/the-constitution/192)
- The use of coats of arms, heraldic flags, heraldic signs and seals that do not comply with their approved standards, or that otherwise violates the law, is prohibited. This is in the Law "Dėl Lietuvos valstybės herbo" (Law on the State Coat of Arms, Other Coats of Arms and Armorial Signs). — [e-seimas: amendment to the Law on the State Coat of Arms](https://e-seimas.lrs.lt/rs/legalact/TAD/TAIS.318092/); [Infolex: new wording](https://www.infolex.lt/teise/DocumentSinglePart.aspx?AktoId=12227&StrNr=1); [Wikipedia: Coat of arms of Lithuania](https://en.wikipedia.org/wiki/Coat_of_arms_of_Lithuania)
- Under the Trademark Law (VIII-1981), a trademark may not consist of the official or traditional (short) name of the Republic of Lithuania, its coat of arms, flag or other state heraldic objects or imitations of them. A mark with state symbols is registrable only with permission from the Minister of Justice. — [Infolex: Trademark Law VIII-1981](https://www.infolex.lt/teise/DocumentSinglePart.aspx?AktoId=513242&StrNr=1); [V. Mizaras (Vilnius Univ.) trademark theses](https://web.vu.lt/tf/v.mizaras/wp-content/uploads/2016/04/Prekiu-zenklai_tezes.pdf)
- The Law on the State Flag allows the flag's likeness to be used "for decoration in general so that no disrespect shall be shown". The manufacture and sale of state flags follow a Government-set procedure. — [Law on the Lithuanian State Flag (English, MOFCOM copy)](https://images.policy.mofcom.gov.cn/flaw/201411/0088742D-8F4E-4998-8E7B-DC5D6C624F1F.pdf); [FOTW: Lithuania flag legislation](https://www.crwflags.com/fotw/flags/lt_leg.html)
- The Unfair Commercial Practices Directive is transposed by the Law on Prohibition of Unfair Business-to-Consumer Commercial Practices. A practice is unfair if it is contrary to professional diligence and materially distorts, or is likely to distort, the average consumer's economic behaviour. Misleading actions and omissions are the main categories, and the State Consumer Rights Protection Authority (VVTAT) enforces the law. — [VVTAT: Unfair commercial practices](https://www.vvtat.lt/en/fields-of-activity/unfair-commercial-practices/736); [ScienceDirect: misleading actions vs omissions](https://www.sciencedirect.com/science/article/pii/S2351667416300051)
- Under the Law on Advertising, misleading advertising includes an implied inaccurate claim conveyed by the manner or form of presentation. — [EBN: Misleading advertising](https://ebn.lt/news-and-events/news/misleading-advertising-and-problems-of-its-interpretation); [Law on Advertising (EN)](https://e-seimas.lrs.lt/rs/legalact/TAD/TAIS.379796/format/ISO_PDF/)

### Inferences
- **Do not use Vytis, the state flag in a logo, the Columns of Gediminas, the Double Cross, or ministry or lrv.lt design elements.** Using them risks breaching the heraldry law and makes the misleading-impression argument much stronger.
- **"Lietuva" as a word mark:** the Trademark Law bar means "Lietuva Chat" is likely unregistrable as a trademark without a Minister of Justice permit, and possibly not even then. This limits brand protection but does not by itself make using the domain unlawful. **[LAWYER: registrability and any company-name restrictions (Registrų centras name rules) if a UAB is formed with "Lietuva" in its name]**
- If the service ever charges money, carries ads or collects leads, the B2C unfair-practices law applies. Implying government affiliation would then be a classic misleading action, and "official" or "valstybinis" wording should be avoided entirely.
- Recommended disclaimer (site header or footer, plus the first chat message):

```
Lietuva Chat is an independent, privately run service. It is not affiliated with, endorsed by, or operated by the Government of the Republic of Lithuania or any state institution. Answers are generated by AI from public sources and may be inaccurate or out of date. For official information, use the linked government sources (e.g. lrv.lt, migracija.lt, vmi.lt, sodra.lt, e-tar.lt).
```

- Also consider:
  - A distinct, non-gov colour palette and typography.
  - No ".gov"-style wording.
  - Not mimicking the epaslaugos.lt or "Elektroniniai valdžios vartai" layout.
  - Never asking users to log in with bank-link or eID credentials, which would look like phishing.

### Gaps
- Could not retrieve the full current text of the Law on the State Coat of Arms on the use of Vytis by private legal persons (for example, whether any non-official use needs permission from the Heraldry Commission).
- No source found on restrictions on using "Lietuva" in domain names (.chat is not a .lt domain, so DOMREG rules do not apply) or in company names.
- No VVTAT decisions on private sites impersonating government services were found.

## 4. EU AI Act obligations for a general-purpose chatbot deployer

### Takeaway
The main obligation is Article 50(1) transparency, in force since 2 August 2026 and not postponed by the Digital Omnibus: users must be told they are talking to an AI no later than their first interaction. Art. 50(2) machine-readable marking applies to providers of generative systems, with a grace period to 2 December 2026 for systems already on the market. A private Q&A assistant is very unlikely to be high-risk: the relevant Annex III entries (5(a) public-assistance eligibility, 7 migration) cover systems used by or on behalf of public authorities. Even so, the assistant should not make eligibility determinations. Art. 4 AI literacy also applies, in softened form.

### Cited Findings
- Art. 50(1): "Providers shall ensure that AI systems intended to interact directly with natural persons are designed and developed in such a way that the natural persons concerned are informed that they are interacting with an AI system", unless this is obvious to a reasonably informed person. — [artificialintelligenceact.eu – Article 50](https://artificialintelligenceact.eu/article/50/)
- Art. 50(2): providers of systems generating synthetic text, audio, images or video must ensure outputs are "marked in a machine-readable format and detectable as artificially generated". — [artificialintelligenceact.eu – Article 50](https://artificialintelligenceact.eu/article/50/)
- Art. 50(4): deployers of a system that generates text "published to inform on public interest matters" must disclose that it is AI-generated, unless it has undergone human editorial review. — [artificialintelligenceact.eu – Article 50](https://artificialintelligenceact.eu/article/50/)
- Art. 50(5): the information must be given "in a clear and distinguishable manner at the latest at the time of the first interaction or exposure". — [artificialintelligenceact.eu – Article 50](https://artificialintelligenceact.eu/article/50/)
- Annex III 5(a) covers "AI systems intended to be used by public authorities or on behalf of public authorities to evaluate the eligibility of natural persons for essential public assistance benefits and services ... as well as to grant, reduce, revoke, or reclaim such benefits". Annex III 7 (migration, asylum, border control) likewise covers systems used "by or on behalf of competent public authorities". — [artificialintelligenceact.eu – Annex III](https://artificialintelligenceact.eu/annex/3/)
- Digital Omnibus on AI: provisional agreement on 6 May 2026. It moves Annex III high-risk obligations to 2 December 2027 and Annex I obligations to 2 August 2028, softens Art. 4 AI literacy to "support staff development", gives a grace period to 2 December 2026 for Art. 50(2) marking for systems already on the market, and leaves Art. 50(1) unchanged. — [Gibson Dunn (27 May 2026)](https://www.gibsondunn.com/eu-ai-act-omnibus-agreement-postponed-high-risk-deadlines-and-other-key-changes/)
- Adoption steps: Parliament approved on 16 June 2026, the Council adopted on 29 June 2026, the regulation was signed on 8 July 2026 and it entered into force on 27 July 2026. Art. 50 deployer obligations applied from 2 August 2026. — [Usercentrics](https://usercentrics.com/knowledge-hub/eu-ai-act-high-risk-delay-article-50-transparency-consent/); consistent with [Jones Walker](https://www.joneswalker.com/en/insights/blogs/ai-law-blog/yes-august-2-still-matters-the-eu-approved-a-high-risk-ai-delay-but-most-trans.html?id=102nbon) and [Plesner](https://plesner.com/en/news/ai-act-august-2026-what-expect-delayed-standards-pending-guidance-and-digital-omnibus-ai). (Gibson Dunn, writing on 27 May, described adoption as still pending. The later sources report it completed. These adoption dates come from secondary sources, not the Official Journal.)

### Inferences
- **Role:** Lietuva Chat integrates third-party general-purpose models (xAI Grok or OpenAI) into its own user-facing system under its own name. That arguably makes it the *provider* of the chatbot AI system for Art. 50(1) purposes, as well as a deployer. It should therefore build in the AI-interaction notice itself rather than relying on the model vendor. Art. 50(2) marking is mainly met upstream by the GPAI model providers, but check their compliance. **[LAWYER: provider vs. deployer classification]**
- **Art. 50(1) implementation:**
  - A persistent "AI assistant" label on the chat UI.
  - First-message disclosure.
  - The notice in the user's language (LT, EN, RU, UA).
- **Art. 50(4)** applies only if the service *publishes* AI-generated text on public-interest matters, for example auto-generated public guide pages. Chat answers to an individual user are arguably not "published". If the site generates public SEO pages, label them as AI-generated or put them through human editorial review.
- **High-risk:** Annex III 5(a) and 7 are tied to public authorities or their agents. A private, informational assistant does not decide eligibility, so it is likely outside high-risk. That changes if the service partners with or is commissioned by a Lithuanian authority (for example Migracijos departamentas or Sodra), or outputs eligibility "decisions". Mitigations:
  - Phrase answers as general information.
  - Never say "you are eligible" or "you will be granted".
  - Always route the user to the official procedure.
  - Keep a written Art. 6(3) self-assessment on file.
- Lithuanian national AI Act enforcement bodies (market surveillance authority) were not researched here.

### Gaps
- Official Journal reference for the Digital Omnibus on AI not retrieved.
- The Commission's Art. 50 Code of Practice and guidelines were not retrieved; check them for implementation details on chatbot disclosure.
- Lithuania's designated AI Act market-surveillance authority was not identified in this session.

## 5. GDPR and Lithuanian data protection (VDAI): chat logs with asmens kodas, immigration status, health data

### Takeaway
Chat logs are personal data, and they will predictably contain special-category data (health, and religion or ethnicity in asylum contexts) as well as Lithuanian personal codes. Lithuania adds national restrictions on asmens kodas in Art. 7 of the Law on Legal Protection of Personal Data (ADTAĮ): no public disclosure, no direct marketing, and a narrow set of lawful grounds. The safe design is to discourage and auto-redact identifiers at input, keep logs as short as possible, avoid using logs for training without a clear legal basis, and be transparent about which LLM vendors and processors receive the data. VDAI is the supervisory authority.

### Cited Findings
- ADTAĮ Art. 7 prohibits publicly disclosing the personal code ("asmens kodą skelbti viešai") and processing it for direct marketing ("tiesioginės rinkodaros tikslu"). — [Triniti: Personal code processing under ADTAĮ and GDPR](https://triniti.eu/lt/izvalgos/asmens-kodo-kaip-duomens-teisetas-tvarkymas-pagal-lr-adtai-ir-bendraji-duomenu-apsaugos-reglamenta-ar-kas-nors-keiciasi/); [Legiscope: Asmens kodas Lietuvoje](https://www.legiscope.com/blog/asmens-kodo-naudojimas-lietuvoje.html)
- Under the current ADTAĮ as described by Triniti, a personal code may be processed only with consent, except in the Art. 7(3) cases (scientific or statistical research, state registers, lending, debt collection, insurance, healthcare, classified data). A proposed amendment would align the lawful grounds with GDPR Art. 6, keep the prohibitions, and ban using the personal code as the sole search criterion in databases. — [Triniti](https://triniti.eu/lt/izvalgos/asmens-kodo-kaip-duomens-teisetas-tvarkymas-pagal-lr-adtai-ir-bendraji-duomenu-apsaugos-reglamenta-ar-kas-nors-keiciasi/). **Conflict/uncertainty:** a search summary stated that a personal code may be processed where any GDPR Art. 6(1) condition is met, which suggests the amendment may have passed. Which version is in force was not verified. **[LAWYER]**
- VDAI has published GDPR guidance for SMEs and for data subjects (SolPriPa project), a summary of complaints about processing personal codes, and guidelines for assessing requests for disclosure of personal data (v4, 23 April 2025). — [VDAI SME guidelines](https://vdai.lrv.lt/uploads/vdai/documents/files/01_%20SolPriPa%20Asmens%20duomenu%20apsaugos%20gaires%20SMULKIAJAM%20IR%20VIDUTINIAM%20VERSLUI%202019-11-08.pdf); [VDAI personal-code complaints summary](https://vdai.lrv.lt/uploads/vdai/documents/files/Apibendrinimas%20pagal%20skundus%20del%20asmens%20kodo20080717.pdf); [VDAI request-assessment guidelines v4](https://vdai.lrv.lt/public/canonical/1745386841/841/2025-04-23%20atnaujintos%20Prasymu%20del%20AD%20teikimo%20vertinimo%20gaires.pdf)
- GDPR obligations that apply directly (primary text, not re-fetched):
  - Art. 5(1)(c) data minimisation and Art. 5(1)(e) storage limitation.
  - Art. 9: processing health data, or data revealing racial or ethnic origin or religious beliefs, needs an Art. 9(2) condition; for a chatbot that realistically means explicit consent.
  - Art. 13 transparency notice.
  - Art. 28 processor contracts (LLM API, Exa, hosting).
  - Arts. 44–49 international transfers, relevant to US-based xAI and OpenAI.
  - Art. 35 DPIA where processing is likely high-risk.
  - [GDPR, Regulation (EU) 2016/679](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

### Inferences
- **Asmens kodas:** the service has no need for it. Mitigations:
  - Client-side or server-side regex detection of the 11-digit LT personal code pattern (first digit 1–6, YYMMDD, 4 more digits), redacted before logging and before sending to the LLM or Exa.
  - A UI warning not to enter personal codes, passport numbers or health details.
  - Never echo codes back.
  - Never use logs for marketing, since that is banned outright by Art. 7.
- **Special categories:** users asking about residence permits, asylum, disability benefits or health insurance will disclose Art. 9 data unprompted. A DPIA is prudent, given vulnerable users (migrants), special-category data, and a new technology (LLMs).
- **Retention:**
  - Default to no server-side storage of conversation content for anonymous users, or keep it for a short fixed period, such as 30 days, for abuse and debugging.
  - Signed-in history only on opt-in, with user-initiated deletion.
  - Aggregate analytics without content.
  - Document all of this in the record of processing (Art. 30).
- **Vendors:** check xAI, OpenAI and Exa data-processing terms (zero-retention or no-training options, EU data residency, SCCs or DPF). Name them in the privacy notice. If the optional PostgreSQL store holds chat logs, the database host is a processor too.
- **Training:** do not fine-tune on user chats without a separate legal basis and notice. Legitimate interest is weak where special-category data is involved.
- Is a DPO required (Art. 37)? Probably not for a small operator, unless large-scale processing of Art. 9 data is a "core activity". **[LAWYER]**

### Gaps
- Not verified: the current in-force wording of ADTAĮ Art. 7, including whether the amendment aligning it with GDPR Art. 6 was adopted.
- No VDAI guidance specific to AI chatbots or LLM chat logs was found. The EDPB Opinion 28/2024 on AI models is relevant but was not fetched.
- No VDAI enforcement cases involving chatbots were found.

## 6. Liability for incorrect advice (tax, immigration) and disclaimer patterns

### Takeaway
No Lithuanian authority specific to AI-advice liability was found in this session. The general position is that civil liability under the Lithuanian Civil Code (fault-based tort or contract) and consumer law limit how far a disclaimer can protect the operator. A clear "general information, not legal or tax advice" notice, source citations, freshness dates and routing to the competent authority reduce both the risk of harm and the risk of liability. They do not exclude liability for gross negligence, and B2C terms are subject to unfair-terms review. Commercial users additionally fall under the unfair-practices rules (Section 3).

### Cited Findings
- Misleading actions or omissions that distort consumer decisions are unfair commercial practices enforced by VVTAT. This becomes relevant if the service presents AI answers as authoritative while monetising. — [VVTAT](https://www.vvtat.lt/en/fields-of-activity/unfair-commercial-practices/736)
- AI Act Art. 50(1)/(5) requires telling users they are interacting with AI at first interaction. This doubles as a reliance-limiting disclosure. — [artificialintelligenceact.eu – Article 50](https://artificialintelligenceact.eu/article/50/)

### Inferences
- **Liability exposure points:**
  - Wrong deadlines (tax declaration dates, permit renewal windows).
  - Wrong amounts (fees, benefit amounts).
  - Wrong eligibility statements.
  - Outdated law, since ingested content goes stale.
  - Hallucinated procedures.
  
  Migrants who miss a permit deadline because of a wrong answer suffer serious harm, which is foreseeable.
- **Recommended patterns:**
  1. Persistent banner plus first-message notice: AI, independent, general information only, not legal, tax or immigration advice, may be wrong or outdated.
  2. Every answer cites its source URLs with a "last checked" date. Refuse or hedge when no source was retrieved.
  3. For high-stakes topics (residence permits, asylum, tax liability amounts, benefit eligibility, deadlines), add an inline line such as "Confirm with Migracijos departamentas / VMI / Sodra before acting" and link to their contact or consultation channel (for example VMI's consultation line or Migris).
  4. No personalised determinations ("you qualify", "you owe X EUR"). Explain the rule and point to the official calculator or procedure.
  5. Terms of use: limitation of liability "to the extent permitted by law", consumer-law carve-outs, governing law and jurisdiction (Lithuania), and no warranty of accuracy. Note that these are reviewed for fairness in B2C contexts. **[LAWYER: drafting enforceable limitation clauses under the Lithuanian Civil Code and consumer law]**
  6. Operational: a content-freshness pipeline (re-crawl and diff), a feedback or "report wrong answer" button, and a correction log.
- If the service is offered free with no contract, liability would be tort-based. Clear disclaimers and source-linking support the argument that reliance without verification was unreasonable, but this is untested. **[LAWYER]**
- Tax and immigration advice by unlicensed persons: some jurisdictions regulate legal or tax advisory services. Whether Lithuanian rules on advocates or tax advisers restrict a general-information service was not researched. **[LAWYER]**

### Gaps
- No Lithuanian case law or law-firm briefing (Sorainen, Ellex, Cobalt, TGS Baltic) on liability for AI-generated advice was found within the search budget.
- The EU Product Liability Directive (EU) 2024/2853, which covers software including AI and must be transposed by December 2026, was not researched. It concerns defect liability for personal injury, property damage and data loss, not pure economic loss, but it is worth checking with counsel.
- The Lithuanian Civil Code articles on limitation-of-liability clauses (for example Art. 6.252) were not retrieved or verified.
