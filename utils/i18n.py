"""Language support: session-based language with IP detection.

English (en) and one additional language (et) live inline below; the other UI languages
(ru, de, fr, sv, lv, fi, lt) are supplied as JSON files in ``locales/`` and
merged in at import by ``_merge_locales()``. Anything still missing for a
language falls back to English via ``t()``.
"""

from __future__ import annotations

from typing import Any

DEFAULT_LANG = "en"

# UI flags are rendered from utils.i18n_flags.py SVGs; these legacy emoji values are unused by the UI.
LANGUAGES: dict[str, dict] = {
    "en": {"name": "English",    "native": "English",    "flag": "\U0001f1ec\U0001f1e7"},
    "et": {"name": "Estonian",   "native": "Eesti",      "flag": "\U0001f1ea\U0001f1ea"},
    "ru": {"name": "Russian",    "native": "Русский",    "flag": "\U0001f1f7\U0001f1fa"},
    "de": {"name": "German",     "native": "Deutsch",    "flag": "\U0001f1e9\U0001f1ea"},
    "fr": {"name": "French",     "native": "Français", "flag": "\U0001f1eb\U0001f1f7"},
    "sv": {"name": "Swedish",    "native": "Svenska",    "flag": "\U0001f1f8\U0001f1ea"},
    "lv": {"name": "Latvian",    "native": "Latviešu", "flag": "\U0001f1f1\U0001f1fb"},
    "fi": {"name": "Finnish",    "native": "Suomi",      "flag": "\U0001f1eb\U0001f1ee"},
    "lt": {"name": "Lithuanian", "native": "Lietuvių",  "flag": "\U0001f1f1\U0001f1f9"},
}

SUPPORTED_LANGS = set(LANGUAGES.keys())

# IP-country → UI language. A visitor from each language's country defaults to
# that language; everyone else defaults to English.
COUNTRY_LANG: dict[str, str] = {
    "ee": "et",   # country code EE
    "ru": "ru",   # Russia
    "de": "de",   # Germany
    "at": "de",   # Austria
    "fr": "fr",   # France
    "se": "sv",   # Sweden
    "lv": "lv",   # Latvia
    "fi": "fi",   # Finland
    "lt": "lt",   # Lithuania
}


def detect_language(request) -> str | None:
    """Map the request's IP-country to a UI language. Returns a supported language
    code, or None if the country could not be determined (caller keeps the default)."""
    try:
        from utils.geo import country_from_request
        country = country_from_request(request)
    except Exception:
        country = None
    if not country:
        return None
    return COUNTRY_LANG.get(country, DEFAULT_LANG)


def ensure_detected_lang(sess: dict[str, Any], request) -> None:
    """On first visit, set the session language from IP geolocation. A manual
    choice (set_lang) is already stored and is never overwritten here."""
    if (sess.get("lang") or "").lower() in SUPPORTED_LANGS:
        return
    detected = detect_language(request)
    if detected in SUPPORTED_LANGS:
        sess["lang"] = detected


def get_lang(sess: dict[str, Any], request=None) -> str:
    lang = (sess.get("lang") or "").lower()
    if lang in SUPPORTED_LANGS:
        return lang
    if request:
        detected = detect_language(request)
        if detected in SUPPORTED_LANGS:
            sess["lang"] = detected
            return detected
    return DEFAULT_LANG


def set_lang(sess: dict[str, Any], lang: str) -> str:
    code = (lang or "").lower()
    if code in SUPPORTED_LANGS:
        sess["lang"] = code
    return get_lang(sess)


def t(key: str, lang: str = DEFAULT_LANG) -> str:
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("en", key))


def agent_t(slug: str, field: str, lang: str = DEFAULT_LANG) -> str:
    entry = AGENT_TRANSLATIONS.get(slug, {}).get(field)
    if not entry:
        return slug if field == "name" else ""
    return entry.get(lang, entry.get("en", slug))


def category_t(key: str, field: str, lang: str = DEFAULT_LANG) -> str:
    entry = CATEGORY_TRANSLATIONS.get(key, {}).get(field)
    if not entry:
        return key if field == "name" else ""
    return entry.get(lang, entry.get("en", key))


def js_translations(lang: str = DEFAULT_LANG) -> dict[str, str]:
    js_keys = {k for k in TRANSLATIONS if k.startswith("js_")}
    js_keys.update({"chat_fb_up", "chat_fb_down", "chat_fb_thanks", "chat_retry"})
    return {k.removeprefix("js_"): t(k, lang) for k in js_keys}


# ---------------------------------------------------------------------------
# Translation catalog  (en + et; other languages fall back to en)
# ---------------------------------------------------------------------------

TRANSLATIONS: dict[str, dict[str, str]] = {

    # -- Navigation --
    "nav_home": {"en": "Home", "et": "Avaleht"},
    "nav_ask": {"en": "Ask AI", "et": "Küsi"},
    "nav_topics": {"en": "Topics", "et": "Teemad"},
    "nav_about": {"en": "About", "et": "Meist"},
    "nav_contact": {"en": "Contact", "et": "Kontakt"},
    "nav_open_app": {"en": "Ask lietuva.chat", "et": "Küsi lietuva.chat"},
    "nav_login": {"en": "Log in", "et": "Logi sisse"},
    "nav_logout": {"en": "Log out", "et": "Logi välja"},

    # -- Hero --
    "home_greeting": {"en": "Labas.", "lt": "Labas."},
    "home_sub": {
        "en": "Ask anything about living, working and dealing with the state in Lithuania.",
        "lt": "Klauskite apie gyvenimą, darbą ir reikalus su valstybe Lietuvoje.",
    },
    "home_independent": {
        "en": "Independent service · not affiliated with the Government of Lithuania",
        "lt": "Nepriklausoma paslauga · nesusijusi su Lietuvos Vyriausybe",
    },
    "home_try": {"en": "Try", "lt": "Pabandykite"},
    "home_prev": {"en": "Previous", "lt": "Ankstesnis"},
    "home_next": {"en": "Next", "lt": "Kitas"},
    "home_pause": {"en": "Pause", "lt": "Pristabdyti"},
    "home_play": {"en": "Play", "lt": "Paleisti"},
    "home_sources": {"en": "Answers from", "lt": "Atsakymai iš"},
    "menu": {"en": "Menu", "lt": "Meniu"},
    "menu_close": {"en": "Close", "lt": "Uždaryti"},
    "menu_ask_about": {"en": "Ask about", "lt": "Klauskite apie"},
    "menu_service": {"en": "lietuva.chat", "lt": "lietuva.chat"},
    "menu_sign_in": {"en": "Sign in", "lt": "Prisijungti"},
    "life_01": {"en": "Moving here", "lt": "Atsikraustymas"},
    "life_01_q": {"en": "How do I declare my place of residence in Vilnius?", "lt": "Kaip deklaruoti gyvenamąją vietą Vilniuje?"},
    "life_02": {"en": "Work and taxes", "lt": "Darbas ir mokesčiai"},
    "life_02_q": {"en": "What taxes are deducted from a Lithuanian salary?", "lt": "Kokie mokesčiai išskaičiuojami iš atlyginimo?"},
    "life_03": {"en": "Family and health", "lt": "Šeima ir sveikata"},
    "life_03_q": {"en": "How do I get compulsory health insurance?", "lt": "Kaip gauti privalomąjį sveikatos draudimą?"},
    "life_04": {"en": "Starting a company", "lt": "Įmonės steigimas"},
    "life_04_q": {"en": "How do I register a UAB online?", "lt": "Kaip įsteigti UAB internetu?"},
    "life_05": {"en": "Coming home", "lt": "Grįžimas namo"},
    "life_05_q": {"en": "I am moving back to Lithuania. Where do I start?", "lt": "Grįžtu gyventi į Lietuvą. Nuo ko pradėti?"},
    "info_01": {"en": "What you can ask", "lt": "Ko galite klausti"},
    "info_01_title": {"en": "Everyday questions, answered from the source.", "lt": "Kasdieniai klausimai su atsakymais iš šaltinio."},
    "ask_residence": {"en": "Residence and permits", "lt": "Gyvenamoji vieta ir leidimai"},
    "ask_residence_q": {"en": "Do I need a temporary residence permit to work here?", "lt": "Ar man reikia leidimo laikinai gyventi, kad galėčiau čia dirbti?"},
    "ask_tax": {"en": "Taxes and Sodra", "lt": "Mokesčiai ir „Sodra“"},
    "ask_tax_q": {"en": "How much is withheld from my gross salary?", "lt": "Kiek išskaičiuojama iš mano atlyginimo „ant popieriaus“?"},
    "ask_health": {"en": "Health insurance", "lt": "Sveikatos draudimas"},
    "ask_health_q": {"en": "Am I covered by compulsory health insurance?", "lt": "Ar esu apdraustas privalomuoju sveikatos draudimu?"},
    "ask_family": {"en": "Family", "lt": "Šeima"},
    "ask_family_q": {"en": "How do I register my child's birth?", "lt": "Kaip įregistruoti vaiko gimimą?"},
    "ask_business": {"en": "Business", "lt": "Verslas"},
    "ask_business_q": {"en": "Should I open an MB or a UAB?", "lt": "Steigti MB ar UAB?"},
    "ask_abroad": {"en": "Lithuanians abroad", "lt": "Lietuviai užsienyje"},
    "ask_abroad_q": {"en": "How do I vote in Lithuanian elections from abroad?", "lt": "Kaip balsuoti Lietuvos rinkimuose iš užsienio?"},
    "info_02": {"en": "How it answers", "lt": "Kaip atsako"},
    "info_02_title": {"en": "Plain language in, official sources out.", "lt": "Klausiate paprastai, atsakymas – iš oficialių šaltinių."},
    "how_a": {"en": "Describe your situation", "lt": "Apibūdinkite savo situaciją"},
    "how_a_body": {"en": "Write it the way you would explain it to a friend, in your own language. No forms, no agency names to know in advance.", "lt": "Rašykite taip, kaip paaiškintumėte draugui, savo kalba. Nereikia formų ir nereikia iš anksto žinoti, kuri institucija atsakinga."},
    "how_b": {"en": "It reads the responsible agency", "lt": "Skaito atsakingos institucijos puslapius"},
    "how_b_body": {"en": "A specialist assistant looks up the agency's own pages, not forums or blogs, and puts together the parts that apply to you.", "lt": "Specializuotas asistentas ieško pačios institucijos puslapiuose, ne forumuose ar tinklaraščiuose, ir atrenka tai, kas tinka jums."},
    "how_c": {"en": "You see where it came from", "lt": "Matote, iš kur atsakymas"},
    "how_c_body": {"en": "Every answer links to its sources, so you can check each step before you act.", "lt": "Kiekvienas atsakymas turi nuorodas į šaltinius, todėl galite viską patikrinti prieš veikdami."},
    "demo_q": {"en": "I just moved to Vilnius. How do I declare my residence?", "lt": "Ką tik persikėliau į Vilnių. Kaip deklaruoti gyvenamąją vietą?"},
    "demo_a": {"en": "Declaring your place of residence is handled by your municipality and can be done online through the e-government gateway. Here is what to prepare before you start.", "lt": "Gyvenamąją vietą deklaruoja savivaldybė, tai galima padaryti ir internetu per Elektroninius valdžios vartus. Štai ką paruošti prieš pradedant."},
    "info_03": {"en": "Who it is for", "lt": "Kam skirta"},
    "info_03_title": {"en": "One place to ask, wherever you are starting from.", "lt": "Viena vieta klausti, nuo ko bepradėtumėte."},
    "who_res": {"en": "Residents", "lt": "Gyventojams"},
    "who_res_body": {"en": "Taxes, benefits, health insurance and everyday paperwork, without hunting across a dozen agency websites.", "lt": "Mokesčiai, išmokos, sveikatos draudimas ir kasdieniai dokumentai be klaidžiojimo po dešimtis institucijų svetainių."},
    "who_new": {"en": "Newcomers", "lt": "Atvykstantiems"},
    "who_new_body": {"en": "Permits, registration, work and banking, explained in plain language before your first appointment.", "lt": "Leidimai, registracija, darbas ir bankai, paaiškinti paprastai dar prieš pirmąjį vizitą."},
    "who_abroad": {"en": "Lithuanians abroad", "lt": "Lietuviams užsienyje"},
    "who_abroad_body": {"en": "Citizenship, voting from abroad, documents and coming home, with the consular pages that apply.", "lt": "Pilietybė, balsavimas iš užsienio, dokumentai ir grįžimas namo, su atitinkamais konsuliniais puslapiais."},
    "info_04": {"en": "Where answers come from", "lt": "Iš kur atsakymai"},
    "info_04_title": {"en": "We read official public sources. We are not them.", "lt": "Remiamės oficialiais viešais šaltiniais. Bet nesame jų dalis."},
    "info_04_body": {"en": "lietuva.chat is an independent service. Answers are AI-generated and can be incomplete or out of date, so confirm details with the agency before you act.", "lt": "lietuva.chat yra nepriklausoma paslauga. Atsakymus generuoja dirbtinis intelektas, jie gali būti neišsamūs ar pasenę, todėl prieš veikdami pasitikslinkite institucijoje."},
    "src_epaslaugos": {"en": "E-government gateway", "lt": "Elektroniniai valdžios vartai"},
    "src_migracija": {"en": "Migration Department, MIGRIS", "lt": "Migracijos departamentas, MIGRIS"},
    "src_vmi": {"en": "State Tax Inspectorate", "lt": "Valstybinė mokesčių inspekcija"},
    "src_sodra": {"en": "State Social Insurance Fund", "lt": "Valstybinio socialinio draudimo fondo valdyba"},
    "src_vlk": {"en": "National Health Insurance Fund", "lt": "Valstybinė ligonių kasa"},
    "src_rc": {"en": "Centre of Registers", "lt": "Registrų centras"},
    "src_etar": {"en": "Register of Legal Acts", "lt": "Teisės aktų registras"},
    "src_urm": {"en": "Ministry of Foreign Affairs, Global Lithuania", "lt": "Užsienio reikalų ministerija, Globali Lietuva"},
    "closing": {"en": "Ask your first question.", "lt": "Užduokite pirmąjį klausimą."},
    "closing_cta": {"en": "Start asking", "lt": "Pradėti"},
    "header_cta": {"en": "Ask lietuva.chat", "lt": "Klausti"},
    "home_eyebrow": {"en": "Labas · independent AI assistant", "lt": "Labas · nepriklausomas DI asistentas"},
    "home_title": {"en": "Ask anything about life in Lithuania.", "lt": "Klauskite apie gyvenimą Lietuvoje."},
    "home_lede": {"en": "Permits, taxes, Sodra, health insurance, business and coming home. Plain answers with links to the official source.", "lt": "Leidimai, mokesčiai, „Sodra“, sveikatos draudimas, verslas ir grįžimas namo. Aiškūs atsakymai su nuorodomis į oficialų šaltinį."},
    "home_placeholder": {"en": "Ask a question…", "lt": "Užduokite klausimą…"},
    "home_reading": {"en": "Reading", "lt": "Skaitoma"},
    "life_01_a": {"en": "You can declare your place of residence at your local ward office (seniūnija) or online through epaslaugos.lt. Bring your ID document, and if you rent, the owner needs to give consent.", "lt": "Gyvenamąją vietą galite deklaruoti seniūnijoje arba internetu per epaslaugos.lt. Reikės asmens dokumento, o jei nuomojatės – savininko sutikimo."},
    "life_02_a": {"en": "Your employer withholds personal income tax and your social insurance contributions, including health insurance, before paying you. You can check what was declared for you in Mano VMI and your Sodra account.", "lt": "Darbdavys prieš išmokėdamas atlyginimą išskaičiuoja gyventojų pajamų mokestį ir socialinio draudimo įmokas, įskaitant sveikatos draudimą. Ką už jus deklaravo, galite pasitikrinti „Mano VMI“ ir „Sodros“ paskyroje."},
    "life_03_a": {"en": "If you work in Lithuania, contributions are usually paid for you. You can check your insurance status on the National Health Insurance Fund's site, then register with a primary care clinic.", "lt": "Jei dirbate Lietuvoje, įmokos paprastai mokamos už jus. Draudimo statusą galite pasitikrinti Valstybinės ligonių kasos svetainėje, o tada prisirašyti prie pirminės sveikatos priežiūros įstaigos."},
    "life_04_a": {"en": "A UAB can be registered online through the Centre of Registers' self-service, signing with a qualified e-signature. Prepare the articles of association first, and optionally reserve the company name.", "lt": "UAB galima įsteigti internetu per Registrų centro savitarną, pasirašant kvalifikuotu el. parašu. Pirmiausia paruoškite įstatus, o pavadinimą galite iš anksto rezervuoti."},
    "life_05_a": {"en": "Start with the Global Lithuania pages of the Ministry of Foreign Affairs. They gather what returning citizens need: documents, declaring residence, social insurance and finding work.", "lt": "Pradėkite nuo Užsienio reikalų ministerijos „Globali Lietuva“ puslapių. Ten surinkta, ko reikia grįžtantiems: dokumentai, gyvenamosios vietos deklaravimas, socialinis draudimas ir darbo paieška."},
    "tick_1": {"en": "Where do I exchange my driving licence?", "lt": "Kur pasikeisti vairuotojo pažymėjimą?"},
    "tick_2": {"en": "How do I get Smart-ID?", "lt": "Kaip gauti „Smart-ID“?"},
    "tick_3": {"en": "Can I use my European health insurance card here?", "lt": "Ar galiu čia naudotis Europos sveikatos draudimo kortele?"},
    "tick_4": {"en": "How do I enrol my child in kindergarten?", "lt": "Kaip užregistruoti vaiką į darželį?"},
    "tick_5": {"en": "What is an individual activity certificate?", "lt": "Kas yra individualios veiklos pažyma?"},
    "tick_6": {"en": "How do I register a car bought abroad?", "lt": "Kaip įregistruoti užsienyje pirktą automobilį?"},
    "tick_7": {"en": "When is the annual income declaration due?", "lt": "Iki kada reikia pateikti metinę pajamų deklaraciją?"},
    "tick_8": {"en": "How do I get a Lithuanian personal code?", "lt": "Kaip gauti Lietuvos asmens kodą?"},
    "phrase_label": {"en": "Say it in Lithuanian", "lt": "Pasakykite lietuviškai"},
    "phrase_1_meaning": {"en": "hello", "lt": "pasisveikinimas"},
    "phrase_2_meaning": {"en": "thank you", "lt": "padėka"},
    "phrase_3_meaning": {"en": "welcome", "lt": "sutikimas atvykus"},
    "how_scroll_hint": {"en": "Scroll to follow one question through", "lt": "Slinkite ir sekite vieno klausimo kelią"},
    "statement": {"en": "Ask in your own words. It finds the agency, reads today's official page, and answers with the link, so you can check every step yourself.", "lt": "Klauskite savais žodžiais. Jis suranda instituciją, perskaito šiandienos oficialų puslapį ir atsako su nuoroda, kad kiekvieną žingsnį galėtumėte pasitikrinti patys."},
    "bento_label": {"en": "Under the hood", "lt": "Kaip tai veikia"},
    "bento_title": {"en": "Built on official sources, not on guesses.", "lt": "Remiamasi oficialiais šaltiniais, ne spėjimais."},
    "bento_sources": {"en": "official Lithuanian domains it searches", "lt": "oficialių Lietuvos domenų, kuriuose ieško"},
    "bento_agents": {"en": "specialist assistants, one per part of life", "lt": "specializuoti asistentai, po vieną gyvenimo sričiai"},
    "bento_langs": {"en": "interface languages", "lt": "sąsajos kalbų"},
    "bento_cite": {"en": "Every answer links its sources", "lt": "Kiekvienas atsakymas su šaltiniais"},
    "bento_cite_body": {"en": "You see which page each step came from before you act on it.", "lt": "Prieš veikdami matote, iš kurio puslapio kilo kiekvienas žingsnis."},
    "bento_independent": {"en": "Independent", "lt": "Nepriklausoma"},
    "bento_independent_body": {"en": "Not a government service, and never presented as one. No ads.", "lt": "Tai ne valstybės paslauga ir niekada taip nepristatoma. Be reklamos."},
    "home_question": {"en": "What do you need to sort out in Lithuania?", "lt": "Ką reikia susitvarkyti Lietuvoje?"},
    "story_1": {"en": "Ask in your|own words.", "lt": "Klauskite|savais žodžiais."},
    "story_2": {"en": "It reads the|responsible agency.", "lt": "Jis skaito|atsakingos institucijos puslapius."},
    "story_3": {"en": "You get the answer,|with the link.", "lt": "Gaunate atsakymą|su nuoroda."},
    "moments_title": {"en": "For the moments that need paperwork.", "lt": "Akimirkoms, kai reikia tvarkyti dokumentus."},
    "close_placeholder": {"en": "Ask your first question…", "lt": "Užduokite pirmąjį klausimą…"},
    "ask_cta": {"en": "Ask", "lt": "Klausti"},
    "chat_onboard_title": {"en": "Before you start", "lt": "Prieš pradedant"},
    "chat_onboard_1": {"en": "Ask about life in Lithuania: permits, taxes, Sodra, health, family, business or coming home.", "lt": "Klauskite apie gyvenimą Lietuvoje: leidimus, mokesčius, „Sodrą“, sveikatą, šeimą, verslą ar grįžimą namo."},
    "chat_onboard_2": {"en": "Answers are written by AI from official websites. Always check the source link before you act.", "lt": "Atsakymus rašo dirbtinis intelektas pagal oficialias svetaines. Prieš veikdami visada patikrinkite šaltinio nuorodą."},
    "chat_onboard_3": {"en": "Don't type personal codes or passwords. lietuva.chat is independent, not a government service.", "lt": "Neįveskite asmens kodų ar slaptažodžių. lietuva.chat yra nepriklausoma paslauga, ne valstybės."},
    "chat_ai_notice": {"en": "You are chatting with an AI assistant. Check the source link before you act.", "lt": "Jūs bendraujate su dirbtinio intelekto asistentu. Prieš veikdami patikrinkite šaltinio nuorodą."},
    "chat_topics": {"en": "Topics", "lt": "Temos"},
    "chat_official_sites": {"en": "Official websites", "lt": "Oficialios svetainės"},
    "chat_text_size": {"en": "Text size", "lt": "Teksto dydis"},
    "chat_share_label": {"en": "Share", "lt": "Dalintis"},
    "chat_copy_label": {"en": "Copy chat", "lt": "Kopijuoti"},
    "chat_results_label": {"en": "Tables", "lt": "Lentelės"},
    "chat_new_plain": {"en": "New chat", "lt": "Naujas pokalbis"},
    "chat_speak": {"en": "Speak", "lt": "Kalbėti"},
    "js_voice_connecting": {"en": "Connecting…", "lt": "Jungiamasi…"},
    "js_voice_mic": {"en": "Requesting microphone…", "lt": "Prašoma mikrofono…"},
    "js_voice_listening": {"en": "Listening…", "lt": "Klausoma…"},
    "js_voice_thinking": {"en": "Thinking…", "lt": "Galvojama…"},
    "js_voice_speaking": {"en": "Speaking…", "lt": "Kalba…"},
    "js_voice_mic_blocked": {
        "en": "Microphone blocked. Allow access and tap the mic again.",
        "lt": "Mikrofonas užblokuotas. Leiskite prieigą ir bakstelėkite mikrofoną dar kartą.",
    },
    "js_voice_error": {"en": "Voice error", "lt": "Balso klaida"},
    "js_voice_end": {"en": "End voice", "lt": "Baigti balsą"},
    "js_voice_hint_title": {"en": "You can talk.", "lt": "Galite kalbėti."},
    "js_voice_hint_body": {
        "en": "Tap the microphone to ask out loud. Your browser will ask to use the microphone.",
        "lt": "Bakstelėkite mikrofoną ir klauskite balsu. Naršyklė paprašys leidimo naudoti mikrofoną.",
    },
    "js_status_understanding": {"en": "Understanding your question", "lt": "Suprantu jūsų klausimą"},
    "js_status_searching": {"en": "Searching official websites", "lt": "Ieškau oficialiose svetainėse"},
    "js_status_writing": {"en": "Writing your answer", "lt": "Rašau atsakymą"},
    "js_sources": {"en": "Sources", "lt": "Šaltiniai"},
    "js_sources_note": {"en": "Check these official pages before you act.", "lt": "Prieš veikdami patikrinkite šiuos oficialius puslapius."},
    "js_copy": {"en": "Copy", "lt": "Kopijuoti"},
    "js_copied": {"en": "Copied", "lt": "Nukopijuota"},
    "js_listen": {"en": "Listen", "lt": "Klausytis"},
    "js_stop": {"en": "Stop", "lt": "Sustabdyti"},
    "js_helpful": {"en": "Was this helpful?", "lt": "Ar tai padėjo?"},
    "js_yes": {"en": "Yes", "lt": "Taip"},
    "js_no": {"en": "No", "lt": "Ne"},
    "js_listening": {"en": "Listening… speak now", "lt": "Klausau… kalbėkite"},
    "js_followups_label": {"en": "You could also ask", "lt": "Taip pat galite paklausti"},
    "footer_sources": {"en": "Official sources", "lt": "Oficialūs šaltiniai"},
    "footer_delete": {"en": "Delete account", "lt": "Ištrinti paskyrą"},
    "footer_changelog": {"en": "Changelog", "lt": "Pakeitimų žurnalas"},
    "hero_h1": {
        "en": "The AI front door to Lithuania.",
        "et": "Tehisintellektil põhinev uks Leetu.",
    },
    "hero_h2": {
        "en": "Ask anything about business, digital ID, taxes, moving, and public services.",
        "et": "Küsi kõike ettevõtluse, digi-ID, maksude, kolimise ja avalike teenuste kohta.",
    },
    "hero_body": {
        "en": "lietuva.chat is a conversational portal to everyday life in Lithuania. "
              "Ask in plain language. Get clear answers from official Lithuanian sources, "
              "with links to check each step.",
        "et": "lietuva.chat on vestluspõhine värav igapäevaellu Leedus. "
              "Küsi tavakeeles. Saa selged vastused Leedu ametlikest allikatest ja lingid, "
              "mille abil iga sammu kontrollida.",
    },
    "hero_cta_start": {"en": "Ask a question", "et": "Esita küsimus"},
    "hero_cta_explore": {"en": "Explore topics", "et": "Vaata teemasid"},

    "home_statement": {
        "en": "Answers are [[AI-generated]]. They come only from [[official Lithuanian sources]], are [[free of ads]], and are always shown with [[links]].",
        "et": "Vastused on [[tehisintellekti loodud]]. Need pärinevad ainult [[Leedu ametlikest allikatest]], on [[reklaamivabad]] ja alati koos [[linkidega]].",
    },

    # -- Stats (numbers hardcoded in template; only labels translated) --
    "stat_services": {"en": "Public services explained", "et": "Avalikud teenused selgelt"},
    "stat_xroad": {"en": "Official sources linked", "et": "Ametlikud allikad viidatud"},
    "stat_eres": {"en": "Company forms covered", "et": "Ettevõttevormid kaetud"},
    "stat_signatures": {"en": "Digital signing covered", "et": "Digiallkirjastamine kaetud"},

    # -- Features --
    "feat_ask": {"en": "Ask, don't navigate", "et": "Küsi, ära otsi"},
    "feat_ask_body": {
        "en": "Skip the maze of agency websites. Describe what you need in your own words and the "
              "right specialist assistant answers about business, tax, digital ID, moving, or public services.",
        "et": "Jäta ametiasutuste veebilehtede rägastik vahele. Kirjelda oma sõnadega, mida vajad, "
              "ja õige eriabiline vastab ettevõtluse, maksude, digi-ID, kolimise või avalike teenuste kohta.",
    },
    "feat_ask_link": {"en": "Start a conversation", "et": "Alusta vestlust"},
    "feat_sources": {"en": "Grounded in official sources", "et": "Põhineb ametlikel allikatel"},
    "feat_sources_body": {
        "en": "Every answer uses live search across official domains, including epaslaugos.lt, migracija.lt, "
              "vmi.lt, sodra.lt, and registrucentras.lt. It cites the sources so you can check them.",
        "et": "Iga vastus põhineb reaalajas otsingul ametlikel domeenidel, sealhulgas epaslaugos.lt, migracija.lt, "
              "vmi.lt, sodra.lt ja registrucentras.lt. Allikaviited aitavad neid kontrollida.",
    },
    "feat_sources_link": {"en": "See how it works", "et": "Vaata, kuidas see töötab"},
    "feat_lithuania": {"en": "Built for Lithuania", "et": "Loodud Leedu jaoks"},
    "feat_lithuania_body": {
        "en": "It adds a conversational layer to Lithuania's public services: one assistant finds the right "
              "agency, reads its current guidance, and puts together what applies to you.",
        "et": "See lisab vestluskihi Leedu avalikele teenustele: üks abiline leiab õige ametiasutuse, "
              "loeb kehtivat juhendit ja koondab sinu olukorra jaoks vajaliku.",
    },
    "feat_lithuania_link": {"en": "About Lithuania", "et": "Leedust lähemalt"},

    # -- Topics / agents section --
    "topics_title": {"en": "Six specialist assistants", "et": "Kuus eriabilist"},
    "topics_subtitle": {
        "en": "Each assistant focuses on one part of life in Lithuania and uses official sources.",
        "et": "Iga abiline keskendub ühele Leeduga seotud teemale ja vastab ametlike allikate põhjal.",
    },

    # -- How It Works --
    "how_title": {"en": "How lietuva.chat works", "et": "Kuidas lietuva.chat töötab"},
    "how_01_title": {"en": "Ask", "et": "Küsi"},
    "how_01_body": {
        "en": "Type your question in any of our languages. \"How do I register a UAB?\", "
              "\"What tax do I pay as a sole trader?\" No forms, no jargon.",
        "et": "Kirjuta oma küsimus ükskõik millises meie keeles. Näiteks: „Kuidas asutada UAB-i?“ "
              "või „Millist maksu maksan füüsilisest isikust ettevõtjana?“. Sa ei vaja vorme ega ametikeelt.",
    },
    "how_02_title": {"en": "We search official sources", "et": "Otsime ametlikest allikatest"},
    "how_02_body": {
        "en": "The right assistant searches official Lithuanian sites in real time, reads the "
              "current guidance, and brings together the parts that apply to you.",
        "et": "Õige abiline otsib reaalajas Leedu ametlikelt veebilehtedelt, loeb kehtivat "
              "juhendit ja koondab sinu olukorra jaoks vajaliku teabe.",
    },
    "how_03_title": {"en": "Answer with sources", "et": "Vastus koos allikatega"},
    "how_03_body": {
        "en": "You get a clear answer with links to the official pages, so you can check each step yourself.",
        "et": "Saad selge vastuse koos linkidega ametlikele lehtedele, et saaksid iga sammu ise kontrollida.",
    },

    # -- CTA --
    "cta_headline": {"en": "Everything Lithuania, one conversation away.", "et": "Kogu Leedu ühe vestluse kaugusel."},
    "cta_body": {
        "en": "Ask lietuva.chat about starting a company, filing your taxes, or renewing your ID card. "
              "The answers come from official sources.",
        "et": "Küsi lietuva.chatilt ettevõtte asutamise, maksude deklareerimise või ID-kaardi uuendamise kohta. "
              "Vastused põhinevad ametlikel allikatel.",
    },

    # -- Footer --
    "footer_desc": {
        "en": "A conversational AI portal to Lithuania. We help residents, newcomers, and Lithuanians "
              "abroad find, understand, and use Lithuanian public services. Answers are based on official sources.",
        "et": "Vestluspõhine tehisintellektiportaal Leetu. Aitame elanikel, saabujatel ja välismaal elavatel "
              "leedulastel leida, mõista ja kasutada Leedu avalikke teenuseid. Vastused põhinevad ametlikel allikatel.",
    },
    "footer_platform": {"en": "Portal", "et": "Portaal"},
    "footer_resources": {"en": "Resources", "et": "Ressursid"},
    "footer_legal": {"en": "Legal", "et": "Juriidiline"},
    "footer_terms": {"en": "Terms of service", "et": "Kasutustingimused"},
    "footer_privacy": {"en": "Privacy policy", "et": "Privaatsuspoliitika"},
    "footer_copyright": {
        "en": "© 2026 lietuva.chat. An independent project, not a government service.",
        "et": "© 2026 lietuva.chat. Sõltumatu projekt, mitte riiklik teenus.",
    },
    "footer_disclaimer": {
        "en": "Answers are AI-generated from public sources and may be incomplete or out of date. "
              "Always verify with the official source before acting. Not legal advice.",
        "et": "Vastused on tehisintellekti loodud avalike allikate põhjal ning võivad olla puudulikud "
              "või aegunud. Enne tegutsemist kontrolli alati ametlikust allikast. Ei ole õigusnõu.",
    },

    # -- Chat UI --
    "chat_new": {"en": "+ New chat", "et": "+ Uus vestlus"},
    "chat_history": {"en": "History", "et": "Ajalugu"},
    "chat_agents": {"en": "Assistants", "et": "Abilised"},
    "chat_welcome_title": {"en": "Ask lietuva.chat", "et": "Küsi lietuva.chat"},
    "chat_welcome_body": {
        "en": "Ask about business, digital ID, taxes, moving to Lithuania, or any public service. "
              "Each answer includes links to official sources.",
        "et": "Küsi ettevõtluse, digi-ID, maksude, Leetu kolimise või ükskõik millise avaliku "
              "teenuse kohta. Iga vastus sisaldab linke ametlikele allikatele.",
    },
    "chat_placeholder": {
        "en": "Ask about business, taxes, digital ID, moving to Lithuania...",
        "et": "Küsi ettevõtluse, maksude, digi-ID, Leetu kolimise kohta...",
    },
    "chat_no_sessions": {"en": "No conversations yet", "et": "Vestlusi pole veel"},
    "chat_copy": {"en": "Copy", "et": "Kopeeri"},
    "chat_share": {"en": "Share", "et": "Jaga"},
    "chat_canvas": {"en": "Canvas", "et": "Lõuend"},
    "chat_signin_title": {"en": "Sign in", "et": "Logi sisse"},
    "chat_signin_body": {"en": "Enter your email to save your chat history.", "et": "Sisesta oma e-post vestlusajaloo salvestamiseks."},
    "chat_sign_in": {"en": "Sign in", "et": "Logi sisse"},
    "chat_sign_out": {"en": "Sign out", "et": "Logi välja"},
    "chat_cancel": {"en": "Cancel", "et": "Tühista"},
    "chat_suggestions_label": {"en": "Suggestions", "et": "Soovitused"},
    "chat_artifacts_title": {"en": "Sources and results", "et": "Allikad ja tulemused"},
    "chat_artifacts_subtitle": {"en": "Official links, tables, and charts", "et": "Ametlikud lingid, tabelid ja graafikud"},
    "chat_fb_up": {
        "en": "Helpful", "et": "Kasulik", "ru": "Полезно", "de": "Hilfreich",
        "fr": "Utile", "sv": "Hjälpsamt", "lv": "Noderīgi", "fi": "Hyödyllinen",
        "lt": "Naudinga",
    },
    "chat_fb_down": {
        "en": "Not helpful", "et": "Pole kasulik", "ru": "Не помогло", "de": "Nicht hilfreich",
        "fr": "Pas utile", "sv": "Inte hjälpsamt", "lv": "Nederīgi", "fi": "Ei hyödyllinen",
        "lt": "Nenaudinga",
    },
    "chat_fb_thanks": {
        "en": "Feedback noted", "et": "Tagasiside salvestatud", "ru": "Отзыв сохранён",
        "de": "Feedback gespeichert", "fr": "Avis enregistré", "sv": "Feedback sparad",
        "lv": "Atsauksme saglabāta", "fi": "Palaute tallennettu", "lt": "Atsiliepimas išsaugotas",
    },
    "chat_retry": {
        "en": "Try again", "et": "Proovi uuesti", "ru": "Повторить — попробовать снова",
        "de": "Erneut versuchen", "fr": "Réessayer", "sv": "Försök igen", "lv": "Mēģināt vēlreiz",
        "fi": "Yritä uudelleen", "lt": "Bandyti dar kartą",
    },

    # -- JS strings --
    "js_thinking": {"en": "Thinking", "et": "Mõtleb"},
    "js_calling": {"en": "Searching", "et": "Otsib"},
    "js_copy_csv": {"en": "Copy CSV", "et": "Kopeeri CSV"},
    "js_copied": {"en": "Copied!", "et": "Kopeeritud!"},

    # -- Default suggestion prompts (welcome screen chips) --
    "js_sug1": {
        "en": "How do I declare my place of residence in Lithuania?",
        "et": "Kuidas Leedus elukohta registreerida?",
    },
    "js_sug2": {
        "en": "How do I register a UAB online?",
        "et": "Kuidas UAB-i internetis registreerida?",
    },
    "js_sug3": {
        "en": "How are salaries taxed in Lithuania?",
        "et": "Kuidas Leedus palka maksustatakse?",
    },
    "js_sug4": {
        "en": "How do I set up Smart-ID or Mobile-ID?",
        "et": "Kuidas seadistada Smart-ID või Mobile-ID?",
    },
    "js_sug5": {
        "en": "How do I get a residence permit to work in Lithuania?",
        "et": "Kuidas saada elamisluba Leedus töötamiseks?",
    },
}

# -- Agent translations --
AGENT_TRANSLATIONS: dict[str, dict[str, dict[str, str]]] = {
    "eresidency": {
        "name": {"en": "Business & company", "et": "Ettevõtlus ja ettevõte"},
        "one_liner": {
            "en": "Starting or running a company in Lithuania: UAB, MB, and individual activity.",
            "et": "Ettevõtte asutamine või juhtimine Leedus: UAB, MB ja füüsilisest isikust ettevõtja.",
        },
    },
    "moving": {
        "name": {"en": "Living & moving", "et": "Elamine ja kolimine"},
        "one_liner": {
            "en": "Residence permits, visas, registering your address, and settling in.",
            "et": "Elamisload, viisad, elukoha registreerimine ja sisseelamine.",
        },
    },
    "tax": {
        "name": {"en": "Taxes & finance", "et": "Maksud ja rahandus"},
        "one_liner": {
            "en": "Income tax, VAT, and filing through Mano VMI.",
            "et": "Tulumaks, käibemaks ja deklareerimine Mano VMI kaudu.",
        },
    },
    "digital": {
        "name": {"en": "Digital ID & e-services", "et": "Digi-ID ja e-teenused"},
        "one_liner": {
            "en": "Smart-ID, Mobile-ID, ID card, and digital signatures.",
            "et": "Smart-ID, Mobile-ID, ID-kaart ja digiallkirjad.",
        },
    },
    "services": {
        "name": {"en": "Public services", "et": "Avalikud teenused"},
        "one_liner": {
            "en": "Health, education, family benefits, voting, and everyday state services.",
            "et": "Tervis, haridus, peretoetused, valimised ja igapäevased riigiteenused.",
        },
    },
    "explore": {
        "name": {"en": "Discover Lithuania", "et": "Avasta Leedu"},
        "one_liner": {
            "en": "History, culture, digital society, and life in Lithuania.",
            "et": "Ajalugu, kultuur, digiühiskond ja elu Leedus.",
        },
    },
}

# -- Category translations --
CATEGORY_TRANSLATIONS: dict[str, dict[str, dict[str, str]]] = {
    "business": {"name": {"en": "Business & company", "et": "Ettevõtlus ja ettevõte"}},
    "living": {"name": {"en": "Living in Lithuania", "et": "Elamine Leedus"}},
    "digital": {"name": {"en": "Digital society", "et": "Digiühiskond"}},
    "discover": {"name": {"en": "Discover Lithuania", "et": "Avasta Leedu"}},
}


# ---------------------------------------------------------------------------
# Merge per-language locale files (locales/<lang>.json) into the catalogs above.
# en + et live inline; ru/de/fr/sv/lv/fi/lt are supplied as JSON locale files.
# Schema: {"ui": {key: str}, "agents": {slug: {name, one_liner}}, "categories": {key: str}}
# ---------------------------------------------------------------------------

def _merge_locales() -> None:
    import json
    from pathlib import Path
    locales_dir = Path(__file__).resolve().parent.parent / "locales"
    if not locales_dir.is_dir():
        return
    for path in locales_dir.glob("*.json"):
        lang = path.stem
        if lang.startswith("_") or lang not in SUPPORTED_LANGS:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        for key, val in (data.get("ui") or {}).items():
            if key in TRANSLATIONS and isinstance(val, str) and val.strip():
                TRANSLATIONS[key][lang] = val
        for slug, fields in (data.get("agents") or {}).items():
            if slug in AGENT_TRANSLATIONS and isinstance(fields, dict):
                for field, val in fields.items():
                    if field in AGENT_TRANSLATIONS[slug] and isinstance(val, str) and val.strip():
                        AGENT_TRANSLATIONS[slug][field][lang] = val
        for key, val in (data.get("categories") or {}).items():
            if key in CATEGORY_TRANSLATIONS and isinstance(val, str) and val.strip():
                CATEGORY_TRANSLATIONS[key]["name"][lang] = val


_merge_locales()
