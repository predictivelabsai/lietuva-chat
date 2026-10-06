# Inventory of official Lithuanian government sources for Lietuva Chat

Research date: 2026-10-01. About 19 search and fetch calls. Several `*.lrv.lt` and `vmi.lt` pages returned **HTTP 403 to the automated fetcher**: migracija.lrv.lt, vmi.lt/cms/atviri-duomenys and data.gov.lt/datasets/2613. That block is itself a finding for ingestion (see the Inferences under Q1). Where a page could not be fetched, the facts come from search-result snippets of the official page and are marked "(snippet)".

## Q1. Central portals: epaslaugos.lt, lrv.lt, lietuva.lt, gov.lt. How are they structured?

### Takeaway
The single citizen-facing entry point is **Elektroniniai valdžios vartai (EVV, epaslaugos.lt)**, run by the **Valstybės skaitmeninių sprendimų agentūra (VSSA)**. It underwent its largest modernisation in 15 years in mid-August 2026, so older URLs and structure may be stale. Ministries and agencies sit on the common **`<institution>.lrv.lt`** website platform, which follows government-wide website requirements coordinated by VSSA (formerly IVPK). That platform gives a predictable URL shape (`/lt/...`, `/en/...`) but blocks naive bots.

### Cited Findings
- EVV (epaslaugos.lt) is the portal administered by the State Digital Solutions Agency. It lists information and links to public and administrative e-services provided in Lithuania. — [vda.lrv.lt](https://vda.lrv.lt/lt/paslaugos/elektroniniai-valdzios-vartai/); [epaslaugos.lt](https://www.epaslaugos.lt/portal/)
- In mid-August 2026 VSSA began the largest modernisation of epaslaugos.lt in 15 years. It covers a new tech platform, new UI, stronger security and an updated service catalogue in which institutions' e-services are presented more consistently, with an accessibility focus. — [15min.lt](https://www.15min.lt/verslas/naujiena/mokslas-it/elektroniniai-valdzios-vartai-atsinaujina-gyventoju-laukia-svarbus-pokyciai-1290-2745150) (secondary news source; the date comes from the search summary)
- EVV has topic content pages per life event. Examples: health / compulsory health insurance at `epaslaugos.lt/portal/content/42839` and EHIC at `/portal/content/43220`. — [epaslaugos.lt content 42839](https://www.epaslaugos.lt/portal/content/42839); [43220](https://www.epaslaugos.lt/portal/content/43220)
- There is a separate EVV services subdomain at `spp.epaslaugos.lt`, possibly the new service platform. — [spp.epaslaugos.lt](https://spp.epaslaugos.lt/lt)
- VSSA runs a "Skaitmeninių paslaugų platforma" (Digital Services Platform) project. Its aim is a unified technology platform for residents and businesses to use public services. — [vssa.lrv.lt](https://vssa.lrv.lt/lt/naujienos/skaitmeniniu-paslaugu-platformos-projektas-igauna-pagreiti-ivyko-visu-partneriu-susitikimas/)
- VSSA coordinates the general requirements for state and municipal institution websites and apps. It audits compliance: municipalities 96%, their subordinate bodies 77%. — [vssa.lrv.lt institucijų svetainės](https://vssa.lrv.lt/lt/veiklos-sritys/instituciju-interneto-svetaines/); [vssa.lrv.lt assessment](https://vssa.lrv.lt/lt/naujienos/ivertintas-valstybes-ir-savivaldybiu-instituciju-ir-istaigu-interneto-svetainiu-atitikimas-bendriesiems-reikalavimams-tom/)
- Examples of agencies on the lrv.lt pattern: migracija.lrv.lt, ligoniukasa.lrv.lt, vssa.lrv.lt, socmin.lrv.lt, nvsc.lrv.lt, vda.lrv.lt, ivpk.lrv.lt. — see the URLs cited throughout this file.
- The automated fetcher got HTTP 403 from migracija.lrv.lt and vmi.lt. — direct observation in this session.

### Inferences
- epaslaugos.lt is the right top-level "service catalogue" to index. Re-crawl it after the August 2026 relaunch, because old `/portal/content/NNNNN` IDs may have changed.
- The shared lrv.lt template means one scraper can cover most ministries and agencies. Expect bot protection, though: use a real UA, respect robots.txt, and consider asking VSSA for access or relying on Exa-cached content.
- VSSA (vssa.lrv.lt) appears to have absorbed IVPK's website-standards role, while ivpk.lrv.lt still exists. The relationship is not confirmed here.

### Gaps
- No primary page was found describing lietuva.lt, lithuania.lt or gov.lt as a current citizen portal. Their 2026 status is unverified. lrv.lt (Government) is the institutional hub.
- No terms of use ("Naudojimo sąlygos") for epaslaugos.lt or lrv.lt content reuse were retrieved.
- No public API for the EVV service catalogue was found.
- Language coverage of EVV after the relaunch (EN/RU) is unverified.

## Q2. Taxes and social: VMI, Sodra, VLK. What content and APIs exist?

### Takeaway
VMI and Sodra both publish real open data. VMI publishes taxpayer register data and taxes paid on data.gov.lt under **CC BY 4.0**, updated daily. Sodra publishes per-employer insured counts, wages, contributions and debts at **atvira.sodra.lt**, with monthly JSON/CSV and a SOAP service. These are mostly business and statistical data. Citizen guidance (how to declare, benefits) is HTML on vmi.lt, sodra.lt and ligoniukasa.lrv.lt, and must be scraped.

### Cited Findings
- **VMI open data page** is at vmi.lt/cms/atviri-duomenys; there are also "Rinkmenos / Atviri duomenys" and "Įmonių duomenys" pages. — [vmi.lt atviri duomenys](https://www.vmi.lt/cms/atviri-duomenys); [vmi.lt rinkmenos](https://www.vmi.lt/evmi/rinkmenos); [vmi.lt įmonių duomenys](https://www.vmi.lt/evmi/imoniu-duomenys)
- The data.gov.lt dataset "Juridinių asmenų sumokėti mokesčiai" (taxes paid by legal entities, per Tax Administration Law Art. 13) is updated daily, open, and licensed **CC BY 4.0** (snippet). — [data.gov.lt/datasets/673](https://data.gov.lt/datasets/673/)
- VMI taxpayer register data for legal entities and VAT payers is on data.gov.lt in Storage API (UAPI), JSON, JSONL, RDF and CSV formats (snippet). — [data.gov.lt taxpayer register](https://data.gov.lt/dataset/informacija-apie-mokesciu-moketojus-pvm-moketojus/)
- VMI i.MAS (smart tax administration system) offers web services. Subscribed users can query and verify VAT-payer status and similar data, so these are not anonymous public APIs. — [vmi.lt i.MAS](https://www.vmi.lt/evmi/bendroji-informacija-apie-i.mas)
- VMI publishes statistics at vmi.lt/evmi/statistiniai-duomenys. — [vmi.lt](https://www.vmi.lt/evmi/statistiniai-duomenys)
- **Sodra open data (atvira.sodra.lt)**: monthly employer-level data on insured persons, average wages, contributions and debts, in JSON and CSV by year and month. A SOAP web service exposes GetChartList, GetChartParams and GetChartData. — [atvira.sodra.lt rinkiniai](https://atvira.sodra.lt/imones/rinkiniai/index.html); [atvira.sodra.lt web-services](https://atvira.sodra.lt/web-services/)
- sodra.lt has an English version (`?lang=en`). — [sodra.lt](https://sodra.lt/?lang=en)
- **VLK (Valstybinė ligonių kasa)**: institutional site ligoniukasa.lrv.lt, e-services at e.vlk.lt (EHIC orders, PSD details). Anyone can check their PSD insurance status at **dpsdr.vlk.lt** by entering gender, birth date and the last 4 digits of their personal code (snippet). — [e.vlk.lt](https://e.vlk.lt/); [ligoniukasa.lrv.lt e-paslaugos](https://ligoniukasa.lrv.lt/lt/naujienos/ligoniu-kasu-elektronines-paslaugos-daugiau-patogumo-gyventojams/); [vlmedicina.lt](https://www.vlmedicina.lt/lt/vlk-internetu-galima-suzinoti-ar-esate-draustas-sveikatos-draudimu)
- PSD coverage for foreigners: permanent residents who pay PSD, and temporarily residing foreigners who work legally. People without PSD pay for care themselves except emergency care (snippet, secondary). — [LRT](https://www.lrt.lt/naujienos/sveikata/682/2454293/ligoniu-kasos-apie-sveikatos-draudima-kaip-isvengti-skolu-ir-gydytis-nemokamai)

### Inferences
- For a chatbot, the useful VMI and Sodra content is the explanatory guidance (declarations, GPM rates, benefits), which is HTML only. The open datasets mainly serve company look-ups, for example "is company X a VAT payer / how many employees". That use is optional.
- dpsdr.vlk.lt is a lookup tool that needs personal data. The bot should link to it, not call it.

### Gaps
- Language availability of vmi.lt guidance (EN pages exist but their coverage is unknown) was not verified; 403 blocked the fetch.
- No terms of use for vmi.lt or sodra.lt content were retrieved.
- No API for VLK or e-sveikata (esveikata.lt) public content was found.

## Q3. Migration: Migracijos departamentas, MIGRIS, permits, visas, startup visa, e-residency

### Takeaway
There are two domains. **migracija.lrv.lt** is the institutional site (LT/EN news, fees, forms). **migracija.lt** is the MIGRIS portal itself, with EN service-guide pages ("I want to get/renew a temporary residence permit"). All applications go through MIGRIS. Lithuanian **e-resident status is still listed as a service in 2026** (90 EUR, 3 years, applied for via MIGRIS), but it is limited and requires in-person biometrics.

### Cited Findings
- MIGRIS (migracija.lt) has EN service guides, e.g. `/en/noriu-gauti-pakeisti-leidima-laikinai-gyventi` (temporary residence permit), `/en/Šeima` (family), and a temporary residence certificate page. — [migracija.lt TRP](https://www.migracija.lt/en/noriu-gauti-pakeisti-leidima-laikinai-gyventi); [migracija.lt family](https://www.migracija.lt/en/%C5%A0eima); [migracija.lt home](https://www.migracija.lt/home?lang=en)
- The Migration Department advises applying to renew a residence permit 4 months before expiry, and offers automatic document-expiry notifications in MIGRIS. — [migracija.lrv.lt/en news](https://migracija.lrv.lt/en/news/foreigners-who-have-residence-permits-in-lithuania-should-take-care-of-changing-them-in-time/)
- Application form index: migracija.lrv.lt/lt/paslaugos/elektronines-paslaugos/prasymu-formos. — [migracija.lrv.lt](https://migracija.lrv.lt/lt/paslaugos/elektronines-paslaugos/prasymu-formos/)
- E-resident status: the fee is **90 EUR**, status is granted for **3 years**, the applicant must be 18 or older, and the application is filed via MIGRIS and must be submitted within 4 months of filling in the form (snippet of the official fees page; the page itself returned 403). — [migracija.lrv.lt e-rezidento statusas](https://migracija.lrv.lt/lt/paslaugos/valstybes-rinkliavu-sarasas/e-rezidento-statusas/)
- E-residency launched 2021-01-01. It allows EVV login, MIGRIS access, qualified e-signature and registering a UAB or foreign branch. Applicants must travel to give biometrics and to collect the card. — [Wikipedia: E-Residency of Lithuania](https://en.wikipedia.org/wiki/E-Residency_of_Lithuania) (secondary). A 2021 law-firm note said the launch slipped beyond 2021-01-01. — [Thompson&Stein, 2021-06-15](https://www.thompsonstein.com/en/what-next-for-the-lithuanian-e-residency-programme/)
- From 2026-09-15, acceptance of non-priority requests was reportedly suspended in Kyrgyzstan, Uzbekistan and Zimbabwe (from the search summary of migracija pages; the context is visa/permit intake at those consular points, not e-residency). — [migracija.lrv.lt](https://migracija.lrv.lt/lt/paslaugos/valstybes-rinkliavu-sarasas/e-rezidento-statusas/) (snippet, unverified)
- The 2026 financial-means requirement for a temporary residence permit equals the minimum monthly wage (**€1,153**), or half that for science-based grounds or minors (third-party blog; verify against migracija). — [workinlithuania.com](https://workinlithuania.com/blog/residence-permit-lithuania/)
- micenter.lt (Migration Information Centre) has EN guides on TRP, PRP and e-services. It replaced renkuosilietuva.lt ("moving to a new website www.micenter.lt"). — [micenter.lt e-services](https://micenter.lt/en/e-services); [renkuosilietuva.lt](https://www.renkuosilietuva.lt/lt/create-pdf/581)

### Inferences
- Index migracija.lt service guides in both EN and LT, and migracija.lrv.lt for fees and news. Keep micenter.lt as a plain-language secondary source; its operator was not verified.
- Startup visa: Startup Lithuania / Migration pages were not retrieved, so this is a gap.

### Gaps
- Startup visa: no current-status source was retrieved.
- The visa service (Schengen and national D visas via VFS / urm.lt) was not researched in detail.
- No MIGRIS public API or open dataset was found. Migration statistics are likely on data.gov.lt or osp.stat.gov.lt but were not verified.
- Whether new e-resident applications are actually being processed in 2026 (as opposed to the fee page merely existing) was not confirmed.

## Q4. Legal texts: e-TAR, Seimas (e-seimas.lrs.lt). API, bulk, consolidated versions, English?

### Takeaway
**TAR (e-tar.lt)**, run by the **Seimo kanceliarija**, is the sole official, free source of promulgated legal acts. Its data, both documents and **consolidated versions** ("suvestinės redakcijos"), is published as an open dataset via the data.gov.lt Storage API (UAPI, JSON). A separate TAR integration API exists under a data-access agreement. e-seimas.lrs.lt gives the same acts plus draft bills (TAP). Lithuanian legal texts and their official translations are **not copyright-protected** (Copyright Law Art. 5).

### Cited Findings
- TAR is the primary state register and the first and only free, open, official electronic source of Lithuanian legal acts. Its data is public and free of charge. — [lrs.lt TARIS apie](https://www.lrs.lt/sip/portal.show?p_r=39291&p_k=1&p_a=257&p_kade_id=10)
- The data.gov.lt dataset "Teisės aktų registro duomenys" has two models, documents and consolidated versions, available via the Storage API in JSON. The controller is the Seimas Chancellery (snippet; the page returned 403). — [data.gov.lt/datasets/2613](https://data.gov.lt/datasets/2613/); [data.gov.lt request 14363](https://data.gov.lt/requests/14363/)
- A TAR integration API spec (DOK-6.1 "TAR integravimo su kitomis sistemomis API") exists. Access is via a data-access agreement (snippet). — [lrs.lt DOK-6.1 PDF](https://www.lrs.lt/sip/getFile3?p_fid=32584)
- Search UIs: e-tar.lt/portal/lt/legalActSearch and e-seimas.lrs.lt/portal/legalActSearch/lt; draft bills at e-seimas.lrs.lt/portal/legalActProjectSearch/lt. — [e-tar search](https://www.e-tar.lt/portal/lt/legalActSearch); [e-seimas search](https://e-seimas.lrs.lt/portal/legalActSearch/lt); [e-seimas projects](https://e-seimas.lrs.lt/portal/legalActProjectSearch/lt)
- Stable act URL patterns: `e-seimas.lrs.lt/portal/legalAct/lt/TAD/<id>`, `e-tar.lt/portal/lt/legalAct/<id>`, and `/asr` for the consolidated version (e.g. the VIII-1524 consolidated text). — [e-tar VIII-1524 asr](https://www.e-tar.lt/portal/lt/legalAct/TAR.FA13E28615F6/asr)
- Seimas "Atvira teisėkūra" (open law-making and IT solutions for the public) presentation. — [lrs.lt PDF](https://www.lrs.lt/sip/getFile3?p_fid=37095)
- N-Lex (EU) describes the Lithuanian national legal database. — [N-Lex LT](https://n-lex.europa.eu/n-lex/info/info-lt/index?lang=lt)
- **Copyright Law (VIII-1185) Art. 5**: legal acts and official administrative, legal or normative documents (resolutions, court judgments, statutes, norms, territorial planning documents) and their **official translations** are not protected. Neither are state symbols, officially registered draft legal acts, or plain informational news about events. — [e-seimas VIII-1185](https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/TAIS.81676); [infolex Art. 5](https://www.infolex.lt/ta/23542:str5)
- **Reuse law**: the Law on the Right to Obtain Information and Data Reuse (VIII-1524) was amended by **XV-564**, adopted 2025-11-20 and in force from **2026-01-01**. It amends Articles 2, 3, 10, 14 and 17 and requires state and municipal institutions and their subordinate bodies to open data (snippet). — [e-seimas XV-564](https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/d9c2b5a2c61311f08962cdb35f3f1615); [e-tar XV-564](https://www.e-tar.lt/portal/lt/legalAct/facb8422cc3511f08918e1adc7c5b1ec); [VIII-1524 editions](https://e-seimas.lrs.lt/portal/legalActEditions/lt/TAD/TAIS.94745)

### Inferences
- The best route for grounding on statute text is the TAR dataset via `get.data.gov.lt` (consolidated versions, no auth), with e-tar.lt deep links for citations. The legal texts are reusable without copyright restriction. Ministry explanatory pages (HTML guidance) are *not* covered by Art. 5, so their reuse terms are governed by the reuse law and site terms.
- English: e-seimas carries some unofficial EN translations of key laws. This was not verified this session.

### Gaps
- The exact UAPI namespace path for the TAR dataset (e.g. `datasets/gov/lrsk/teises_aktai/...`) was not retrieved because of the 403.
- The extent and currency of English translations on e-seimas were not verified.
- The specific contents of the XV-564 amendments (e.g. a default licence) were not read.

## Q5. Business: Registrų centras, JAR, Invest Lithuania, Startup Lithuania, Verslo vartai

### Takeaway
**JAR (Juridinių asmenų registras)**, run by VĮ Registrų centras, is open on data.gov.lt with daily updates. Combined with VMI and Sodra open data, it gives full public company profiles. Invest Lithuania, Startup Lithuania and Verslo vartai were not verified in this session.

### Cited Findings
- data.gov.lt dataset "Juridinių asmenų registre įregistruoti juridiniai asmenys (RAW data)". — [data.gov.lt/datasets/1484](https://data.gov.lt/datasets/1484/)
- JAR open data covers name, code, legal form, address, manager and EVRK activity code. That is about 226k active and 313k deregistered entities, about 538k records since 1990, updated daily. Most JAR information has been free via data.gov.lt since 2019 (secondary blog; treat the counts as approximate). — [kriptika.lt](https://kriptika.lt/tinklarastis/registru-centras-atviri-duomenys/); [scoris.lt](https://scoris.lt/en/izvalgos/imoniu-duomenu-baze-lietuvoje)
- The Registrų centras self-service portal accepts login via online banking, e-signature tokens and cards, mobile e-signature, or EVV for foreigners (snippet). — [taxexpert.lt](https://taxexpert.lt/en/company-formation-in-lithuania-online/) (secondary)
- Spatial and cadastral open data: geoportal.lt open data and open.geodata.gov.lt. — [geoportal.lt](https://www.geoportal.lt/geoportal/atviri-duomenys); [open.geodata.gov.lt](https://open.geodata.gov.lt/)

### Gaps
- Not researched due to call budget: Invest Lithuania (investlithuania.com), Startup Lithuania (startuplithuania.com), Verslo vartai (verslovartai.lt), and the Registrų centras Real Property Register / address register (ADR) open data and their licences.

## Q6. Digital identity and e-signature

### Takeaway
Login to EVV and most services uses **ID card, Mobile-ID (SIM), Smart-ID (app), e-banking, or USB/qualified e-signature**, all under eIDAS. Foreigners without LT credentials depend on e-resident status or eIDAS-notified foreign eIDs.

### Cited Findings
- Lithuania uses Mobile-ID (SIM-based) and Smart-ID (app-based). E-signatures are governed by national law plus eIDAS (EU 910/2014) (secondary). — [agrello.io](https://www.agrello.io/en/blog/cross-border-digital-identity-and-e-signing-in-the-baltic-states-a-practical-guide-for-smes/)
- National trusted service list: elektroninisparasas.lt/en/trusted-service-list. — [elektroninisparasas.lt](https://elektroninisparasas.lt/en/trusted-service-list/)
- ID cards and their e-signature certificates: the Personalisation of Identity Documents Centre (nsc.vrm.lt). — [nsc.vrm.lt](https://www.nsc.vrm.lt/default_en.htm)
- Foreigners with a residence permit can use e-services for documents, status tracking, inviting visitors, vehicle registration and payments. Those without one can seek e-resident status. — [micenter.lt e-services](https://micenter.lt/en/e-services)

### Gaps
- The supervisory body (RRT) and eIDAS-notified scheme details were not retrieved. Whether EVV accepts other EU eIDs via the eIDAS node in 2026 was not verified.

## Q7. Open data: data.gov.lt, Spinta / UAPI

### Takeaway
data.gov.lt (operated by VSSA) is the national catalogue. Its storage **get.data.gov.lt** serves datasets in the national **UAPI** standard through the open-source **Spinta** engine. Reads are public with no auth. It supports filter, select, sort, limit and cursor pagination, a `/:changes` incremental feed, and JSON, CSV and ASCII output. This is the most machine-friendly layer, but it holds registers and statistics, not service guidance.

### Cited Findings
- Storage: `https://get.data.gov.lt/` is the public read-only endpoint; `https://put.data.gov.lt/` is for providers (OAuth2 client credentials). Test environments use the `-test` suffix. — [docs.data.gov.lt API](https://docs.data.gov.lt/projects/atviriduomenys/latest/api/index.html)
- Query syntax: `/datasets/gov/dc/geo/City?name.contains("Vilnius")&select(name,country.name)&sort(-population)&limit(10)`. Formats via `/:format/csv` and similar. Pagination via `limit(n)&page("<token>")` with `_page.next`. Change feed via `/:changes/<cid>?limit(100)`, returning `_op` values insert, patch and delete. — [docs.data.gov.lt API](https://docs.data.gov.lt/projects/atviriduomenys/latest/api/index.html)
- Spinta is a framework, built by VSSA, to describe, extract and publish data. In 2025 it was used to publish **904 datasets from 177 organisations**, as presented at SEMIC 2025. — [data.gov.lt blog](https://data.gov.lt/blog/); [github.com/atviriduomenys](https://github.com/atviriduomenys)
- The catalogue itself has an API: "Viešasis katalogo API". — [data.gov.lt/datasets/3845](https://data.gov.lt/datasets/3845/?resource_version=1047)
- Data-opening guide ("Duomenų atvėrimo vadovas") including terms and the "Agentas" component. — [docs.data.gov.lt](https://docs.data.gov.lt/projects/atviriduomenys/latest/agentas.html); [savokos](https://docs.data.gov.lt/projects/atviriduomenys/latest/savokos.html)
- Datasets carry per-dataset licences. The VMI example is CC BY 4.0. — [data.gov.lt/datasets/673](https://data.gov.lt/datasets/673/)
- Old portal (old.data.gov.lt) still indexed: outdated. — [old.data.gov.lt](https://old.data.gov.lt/datasets;jsessionid=EEB0253DD5491AD731D4539E52FF6B10?q=&category_id=240&tags=licencija&format=UAPI)
- Technical contact: atviriduomenys@vssa.lt (snippet). — [data.gov.lt/datasets/2613](https://data.gov.lt/datasets/2613/)

### Inferences
- Datasets that matter for a services chatbot: TAR (legal acts plus consolidated versions), JAR, VMI taxpayers and VAT payers, Sodra employer data, and possibly the address register and municipalities lists. Use the `/:changes` feed for incremental sync.
- data.gov.lt pages returned 403 to the fetcher. The `get.data.gov.lt` API is the intended machine path; it was not test-called this session.

### Gaps
- The `get.data.gov.lt` endpoints were not actually called, so availability and exact dataset paths are not verified.
- Whether a portal-wide default licence exists (e.g. CC BY 4.0 for all) was not confirmed.

## Q8. Diaspora: Global Lithuania, URM consular, citizenship, voting abroad, return

### Takeaway
Diaspora and return information has consolidated under the **Ministry of Foreign Affairs (URM)**. **globalilietuva.urm.lt** is the diaspora portal, with the **"Grįžtu LT"** one-stop return consultation centre (griztu.lt). Consular and citizenship information is at **keliauk.urm.lt**. The older **"Renkuosi Lietuvą"** centre is outdated.

### Cited Findings
- Globali Lietuva portal: globalilietuva.urm.lt, including "Apie Globalią Lietuvą", return guides (e.g. returning from the UK) and Grįžtu.lt. — [globalilietuva.urm.lt](https://globalilietuva.urm.lt/); [Grįžtu.lt](https://globalilietuva.urm.lt/griztu.lt/4); [return from UK](https://globalilietuva.urm.lt/kita-informacija/pasiruosimas-grizimui/grizimas-is-jungtines-karalystes-jk.-ka-reiketu-zinoti/155)
- URM took over return information on a single-window basis through its Department for Return to Lithuania. "Renkuosi Lietuvą", which had been handling over 400 enquiries a month, continued only until 1 March of the transition year. — [LRT Lituanica](https://www.lrt.lt/lituanica/norintiems-sugrizti/754/2161674/uzsienio-reikalu-ministerija-pradeda-teikti-informacija-grizimo-i-lietuva-klausimais) (the transition year is not stated in the snippet)
- Citizenship (consular functions for LT citizens abroad): keliauk.urm.lt/gyvenantiems-uzsienyje/konsulines-funkcijos-lietuvos-pilieciams/lietuvos-respublikos-pilietybe. — [keliauk.urm.lt](https://keliauk.urm.lt/gyvenantiems-uzsienyje/konsulines-funkcijos-lietuvos-pilieciams/lietuvos-respublikos-pilietybe)
- Other return-related pages: SADM "Informacija grįžtantiems migrantams" and Užimtumo tarnyba "Grįžtantiems į Lietuvą". — [socmin.lrv.lt](https://socmin.lrv.lt/lt/veiklos-sritys/socialine-integracija/informacija-griztantiems-migrantams/); [uzt.lt](https://uzt.lt/griztantiems-i-lietuva/109)

### Gaps
- Voting abroad (VRK, vrk.lt) was not researched.
- The status of the dual-citizenship referendum and law was not researched. The 2024 referendum failed on turnout, but that comes from model knowledge, is unverified here, and must be checked.
- URM language versions were not checked.

## Q9. Municipalities: common layer or 60 separate sites?

### Takeaway
No shared municipal services content layer was found. Each of the **60 municipalities** runs its own website, many from private vendors. Common elements are VSSA's mandatory website requirements and the fact that municipal e-services are listed on EVV. A municipality bot layer must handle the 60 sites separately, with EVV as the cross-cutting index.

### Cited Findings
- VSSA sets general requirements for state and municipal websites, including a common required-content structure. A separate IVPK guidance document covers municipal website changes. — [vssa.lrv.lt](https://vssa.lrv.lt/lt/veiklos-sritys/instituciju-interneto-svetaines/); [ivpk PDF](https://ivpk.lrv.lt/uploads/ivpk/documents/files/Veikla/Veiklos_sritys/Reikalavimai_interneto_svetainems/Savivaldybems_Bendrieji_pakeitimai_interneto_svetainese.pdf)
- Municipal sites are 96% compliant with those requirements. — [vssa.lrv.lt](https://vssa.lrv.lt/lt/naujienos/ivertintas-valstybes-ir-savivaldybiu-instituciju-ir-istaigu-interneto-svetainiu-atitikimas-bendriesiems-reikalavimams-tom/)
- Private vendors market municipal website solutions in 2026, which indicates no single mandated platform. — [tobalt.lt](https://tobalt.lt/svetaines-savivaldybems-2026/) (vendor source)
- XV-564 (in force 2026-01-01) extends data-opening duties to municipal institutions (snippet). — [e-seimas XV-564](https://e-seimas.lrs.lt/portal/legalAct/lt/TAD/d9c2b5a2c61311f08962cdb35f3f1615)

### Inferences
- Because the content structure is mandated, scraping each site's required sections (services, contacts) is feasible. The national Digital Services Platform could become a common layer later; that is speculative.

### Gaps
- No master list of municipal URLs was retrieved. The Association of Lithuanian Municipalities (lsa.lt) is a likely source but was not verified.
