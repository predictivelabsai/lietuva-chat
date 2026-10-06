"""Deeper routing checks: keyword hygiene, the product's own questions in every language,
and hostile or odd input. No network access; the LLM tier is replaced via injection."""

import random
import string

import pytest

from agents import router
from agents.registry import AGENTS
from utils.i18n import LANGUAGES, t


def no_llm(message):
    raise AssertionError(f"LLM fallback reached for: {message!r}")


# --- Keyword hygiene ----------------------------------------------------------------------

def _all_keywords():
    return [(slug, kw) for slug, kws in router._SLUG_KEYWORDS.items() for kw in kws]


@pytest.mark.parametrize("slug,kw", _all_keywords(), ids=lambda v: str(v))
def test_every_keyword_matches_its_own_text(slug, kw):
    text = f"question about {kw.rstrip('*')} please"
    assert router._keyword_scores(text).get(slug, 0) >= 1


def test_no_keyword_is_listed_under_two_topics():
    seen = {}
    for slug, kw in _all_keywords():
        assert kw.lower() not in seen, f"{kw!r} is in both {seen.get(kw.lower())} and {slug}"
        seen[kw.lower()] = slug


def test_every_keyword_topic_is_a_real_agent():
    assert set(router._SLUG_KEYWORDS) == {a.slug for a in AGENTS}


# --- The assistants' own example prompts ---------------------------------------------------

@pytest.mark.parametrize("agent,prompt", [(a, p) for a in AGENTS for p in a.example_prompts],
                         ids=lambda v: getattr(v, "slug", None) or str(v)[:40])
def test_example_prompts_route_to_their_own_agent(agent, prompt):
    assert router.route(prompt, classify=no_llm) == agent.slug


@pytest.mark.parametrize("agent,prompt", [(a, p) for a in AGENTS for p in a.example_prompts],
                         ids=lambda v: getattr(v, "slug", None) or str(v)[:40])
def test_example_prompts_also_route_without_their_prefix(agent, prompt):
    """The topic words alone should be enough; the prefix only removes doubt."""
    bare = router.strip_prefix(prompt)
    got = router.route(bare, classify=lambda m: "LLM")
    allowed = {agent.slug, "LLM"} | SHARED_TOPICS.get(bare, set())
    assert got in allowed, f"{bare!r} went to {got}, expected {agent.slug}"


# Questions that two assistants can answer equally well.
SHARED_TOPICS = {"how is PSD (compulsory health insurance) paid?": {"services"}}  # PSD is VLK's insurance


# --- The product's curated questions, in every interface language --------------------------

# Which assistant(s) may answer each curated question; None = no keyword expected (LLM decides).
CURATED = {
    "ask_residence_q": {"moving"}, "ask_tax_q": {"tax"}, "ask_health_q": {"services", "tax"},
    "ask_family_q": {"services"}, "ask_business_q": {"eresidency"}, "ask_abroad_q": {"services", "explore"},
    "tick_2": {"digital"}, "tick_3": {"services"}, "tick_4": {"services"}, "tick_5": {"eresidency", "tax"},
    "tick_7": {"tax"}, "life_01_q": {"moving"}, "life_02_q": {"tax"}, "life_03_q": {"services", "tax"},
    "life_04_q": {"eresidency"}, "life_05_q": {"explore", "moving"}, "demo_q": {"moving"},
    "tick_1": None, "tick_6": None, "tick_8": None,
}


@pytest.mark.parametrize("lang", list(LANGUAGES))
@pytest.mark.parametrize("key", list(CURATED))
def test_curated_questions_never_go_to_a_wrong_assistant(lang, key):
    """In any language, a keyword match must point to an allowed assistant (or fall to the LLM)."""
    text = t(key, lang)
    got = router.route(text, classify=lambda m: "LLM")
    allowed = CURATED[key]
    assert got == "LLM" or allowed is None or got in allowed, f"[{lang}] {text!r} -> {got}"


@pytest.mark.parametrize("lang", ["en", "lt"])
@pytest.mark.parametrize("key", [k for k, v in CURATED.items() if v])
def test_curated_questions_route_by_keyword_in_english_and_lithuanian(lang, key):
    text = t(key, lang)
    assert router.route(text, classify=no_llm) in CURATED[key], f"[{lang}] {text!r}"


# --- Odd and hostile input -----------------------------------------------------------------

@pytest.mark.parametrize("message", ["", "   ", "\n\t", "?", "🙂🇱🇹", "tax", "TAX!!!", ":", "::", "tax:"])
def test_odd_input_never_crashes(message):
    assert router.route(message, classify=lambda m: "explore") in {a.slug for a in AGENTS}


@pytest.mark.parametrize("message", ["tax:", "tax:   ", "  move:\n"])
def test_prefix_without_a_question_keeps_the_text(message):
    """A bare prefix must not become an empty question for the assistant."""
    assert router.strip_prefix(message) != ""


def test_html_in_messages_is_just_text():
    msg = '<script>alert("vmi")</script> how much tax?'
    assert router.route(msg, classify=no_llm) == "tax"
    assert router.strip_prefix(msg) == msg


def test_prefix_on_a_later_line_is_not_a_prefix():
    msg = "I have a question\ntax: how much?"
    assert router._prefix_match(msg) is None
    assert router.strip_prefix(msg) == msg


def test_very_long_messages_route_quickly():
    import time
    msg = ("lorem ipsum " * 2000) + " Sodra contributions"
    start = time.perf_counter()
    assert router.route(msg, classify=no_llm) == "tax"
    assert time.perf_counter() - start < 0.5


def test_ties_go_to_the_more_specific_topic():
    assert router._keyword_scores("company tax") == {"tax": 1, "eresidency": 1}
    assert {router.route("company tax", classify=no_llm) for _ in range(20)} == {"tax"}


@pytest.mark.parametrize("message,slug", [
    ("Wie melde ich meinen Wohnsitz in Vilnius an?", "LLM"),   # a city name alone is not a topic
    ("How do I declare my residence in Vilnius?", "moving"),
    ("Tell me about Kaunas history", "explore"),
])
def test_city_names_do_not_decide_the_topic(message, slug):
    assert router.route(message, classify=lambda m: "LLM") == slug


def test_random_text_never_crashes():
    rng = random.Random(1234)
    alphabet = string.printable + "ąčęėįšųūžĄČĘĖĮŠŲŪŽабвгдежзийклмнопрстуфхцчшщ🙂:"
    slugs = {a.slug for a in AGENTS}
    for _ in range(2000):
        msg = "".join(rng.choice(alphabet) for _ in range(rng.randint(0, 120)))
        assert router.route(msg, classify=lambda m: "explore") in slugs
        assert isinstance(router.strip_prefix(msg), str)
