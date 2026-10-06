"""Routing: prefix -> keywords -> LLM fallback. All tiers are tested without network access."""

import pytest

from agents import router
from agents.registry import AGENTS, AGENTS_BY_SLUG


class FakeLLM:
    """Stands in for the chat model in the LLM-fallback tier (injected, not patched)."""

    def __init__(self, reply=None, error=None):
        self.reply, self.error, self.prompts = reply, error, []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        if self.error:
            raise self.error
        return type("Msg", (), {"content": self.reply})()


def no_llm(message):
    raise AssertionError(f"LLM fallback should not be reached for: {message!r}")


# --- Tier 1: prefixes -------------------------------------------------------------------

@pytest.mark.parametrize("agent", AGENTS, ids=lambda a: a.slug)
def test_every_agent_prefix_routes_to_its_agent(agent):
    assert router.route(f"{agent.prefix} anything at all", classify=no_llm) == agent.slug


@pytest.mark.parametrize("message,slug", [
    ("BUSINESS: open a company", "eresidency"),        # case-insensitive
    ("move:residence permit", "moving"),                # no space after the colon
    ("  tax:   income tax", "tax"),                     # surrounding whitespace
    ("estonia: an old shared link", "explore"),         # legacy alias still works
])
def test_prefix_variants(message, slug):
    assert router.route(message, classify=no_llm) == slug


def test_prefix_beats_keywords():
    # Keywords say "tax", the explicit prefix says "digital".
    assert router.route("id: what VMI tax do I pay?", classify=no_llm) == "digital"


@pytest.mark.parametrize("message,stripped", [
    ("business: open a UAB", "open a UAB"),
    ("move:residence permit", "residence permit"),
    ("Note: I need help with taxes", "Note: I need help with taxes"),   # not a routing prefix
    ("Q: how do I vote?", "Q: how do I vote?"),
    ("Time 10:30 at the office", "Time 10:30 at the office"),
])
def test_strip_prefix_only_removes_known_prefixes(message, stripped):
    assert router.strip_prefix(message) == stripped


def test_unknown_prefix_is_not_a_route():
    assert router.route("Note: how much income tax do I pay?", classify=no_llm) == "tax"


# --- Tier 2: keywords -------------------------------------------------------------------

@pytest.mark.parametrize("question,slug", [
    # Living & moving
    ("How do I declare my residence in Vilnius?", "moving"),
    ("I want a residence permit via MIGRIS", "moving"),
    ("Do I need a visa to work in Lithuania?", "moving"),
    ("I am relocating with my family next month", "moving"),
    # Taxes
    ("What VMI taxes do I pay on my salary?", "tax"),
    ("When is the income declaration due?", "tax"),
    ("How much are Sodra contributions?", "tax"),
    ("Do I charge VAT as a freelancer?", "tax"),
    # Business
    ("How do I register a UAB online?", "eresidency"),
    ("Should I open an MB or a UAB?", "eresidency"),
    ("I am a founder, how do I incorporate here?", "eresidency"),
    # Digital
    ("How do I get Smart-ID?", "digital"),
    ("How do I sign a document with Mobile-ID?", "digital"),
    ("How do I log in to epaslaugos.lt?", "digital"),
    # Public services
    ("How do I register with a family doctor?", "services"),
    ("How do I vote in Lithuanian elections from abroad?", "services"),
    ("How do I renew my passport?", "services"),
    ("What child benefits can parents get?", "services"),
    # Discover / diaspora
    ("Tell me about the history of Kaunas", "explore"),
    ("What is Globali Lietuva?", "explore"),
])
def test_english_keyword_routing(question, slug):
    assert router.route(question, classify=no_llm) == slug


@pytest.mark.parametrize("question,slug", [
    ("Kaip gauti leidimą gyventi Lietuvoje?", "moving"),
    ("Kaip deklaruoti gyvenamąją vietą?", "moving"),
    ("Kiek mokesčių išskaičiuojama iš atlyginimo?", "tax"),
    ("Kaip įsteigti UAB internetu?", "eresidency"),
    ("Kaip prisirašyti prie šeimos gydytojo?", "services"),
    ("Kaip balsuoti rinkimuose iš užsienio?", "services"),
    ("Как получить вид на жительство в Литве?", "moving"),
    ("Какие налоги я плачу с зарплаты?", "tax"),
])
def test_lithuanian_and_russian_keyword_routing(question, slug):
    assert router.route(question, classify=no_llm) == slug


@pytest.mark.parametrize("innocent", [
    "Is a private clinic better?",      # 'vat' inside 'private'
    "Is it advisable to rent first?",   # 'visa' inside 'advisable'
    "That sounds weird",                # 'eid' inside 'weird'
    "Can I take a taxi from the airport?",  # 'tax' inside 'taxi'
])
def test_keywords_do_not_match_inside_other_words(innocent):
    scores = router._keyword_scores(innocent)
    assert "tax" not in scores and "moving" not in scores and "digital" not in scores, scores


# --- Tier 3: LLM fallback ---------------------------------------------------------------

def test_no_match_falls_through_to_the_classifier():
    seen = []
    assert router.route("Hello there", classify=lambda m: seen.append(m) or "services") == "services"
    assert seen == ["Hello there"]


@pytest.mark.parametrize("reply,slug", [
    ("tax", "tax"),
    ("  Moving.  ", "moving"),
    ('"digital"', "digital"),
    ("`services`", "services"),
])
def test_llm_classify_accepts_clean_and_lightly_decorated_slugs(reply, slug):
    assert router._llm_classify("whatever", llm=FakeLLM(reply)) == slug


def test_llm_classify_prompt_lists_every_slug():
    llm = FakeLLM("tax")
    router._llm_classify("whatever", llm=llm)
    assert all(slug in llm.prompts[0] for slug in AGENTS_BY_SLUG)


@pytest.mark.parametrize("llm", [FakeLLM("I think it is about taxes"), FakeLLM(error=RuntimeError("down"))])
def test_llm_classify_falls_back_to_explore(llm):
    assert router._llm_classify("whatever", llm=llm) == "explore"
