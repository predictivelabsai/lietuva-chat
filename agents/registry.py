"""Central registry of all lietuva.chat specialist assistants."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AgentSpec:
    slug: str
    name: str
    category: str
    icon: str
    one_liner: str
    description: str
    prefix: str
    example_prompts: tuple[str, ...] = field(default_factory=tuple)


CATEGORIES: list[dict] = [
    {
        "key": "business",
        "name": "Business & Company",
        "blurb": "Register a Lithuanian company and use e-resident status where it applies.",
        "icon": "€",
    },
    {
        "key": "living",
        "name": "Living in Lithuania",
        "blurb": "Moving, residence, taxes, and everyday public services.",
        "icon": "⌂",
    },
    {
        "key": "digital",
        "name": "Digital identity",
        "blurb": "Smart-ID, Mobile-ID, ID-card e-signature, and epaslaugos.lt.",
        "icon": "#",
    },
    {
        "key": "discover",
        "name": "Discover Lithuania",
        "blurb": "The country, culture, and Lithuanians abroad.",
        "icon": "★",
    },
]


AGENTS: tuple[AgentSpec, ...] = (
    # Business
    AgentSpec(
        slug="eresidency", name="Business & Company",
        category="business", icon="€", prefix="business:",
        one_liner="Start a UAB, MB, or individuali veikla, and use e-resident status if you need it.",
        description=(
            "Helps founders register and run a Lithuanian business: UAB, MB, individuali veikla, "
            "Registrų centras (JAR) filings, and VMI taxpayer registration. Also explains Lithuanian "
            "e-resident status via MIGRIS as a digital-identity option — not citizenship, tax residency, "
            "or a residence permit. Grounds answers in official sources such as registrucentras.lt, "
            "vmi.lt and migracija.lt."
        ),
        example_prompts=(
            "business: how do I register a UAB with Registrų centras?",
            "business: what is the difference between UAB, MB, and individuali veikla?",
            "business: how does Lithuanian e-resident status work via MIGRIS?",
            "business: what do I file with VMI after I register a company?",
        ),
    ),
    # Living
    AgentSpec(
        slug="moving", name="Living & Moving",
        category="living", icon="⌂", prefix="move:",
        one_liner="Residence permits, MIGRIS, declaring residence, and settling in.",
        description=(
            "Guides people moving to or living in Lithuania: visas and residence permits, the MIGRIS "
            "portal, declaring place of residence with the municipality, and practical settling-in "
            "steps. Grounds answers in official sources such as migracija.lt (MIGRIS), migracija.lrv.lt "
            "and epaslaugos.lt."
        ),
        example_prompts=(
            "move: how do I apply for a temporary residence permit in MIGRIS?",
            "move: how do EU citizens declare residence in Lithuania?",
            "move: how do I declare my address with the municipality?",
            "move: what should I do after I arrive to settle in?",
        ),
    ),
    AgentSpec(
        slug="tax", name="Taxes & Finance",
        category="living", icon="%", prefix="tax:",
        one_liner="VMI, GPM, Sodra contributions, PSD, and annual declarations.",
        description=(
            "Explains Lithuanian taxation and social contributions for individuals and companies: "
            "GPM, VAT/PVM, VMI declarations, Sodra contributions, and PSD. Grounds answers in official "
            "sources, primarily vmi.lt and sodra.lt."
        ),
        example_prompts=(
            "tax: how do I file my annual GPM declaration with VMI?",
            "tax: when does a company have to register for PVM?",
            "tax: what Sodra contributions apply to individuali veikla?",
            "tax: how is PSD (compulsory health insurance) paid?",
        ),
    ),
    AgentSpec(
        slug="services", name="Public Services",
        category="living", icon="+", prefix="gov:",
        one_liner="Health (VLK), education, family benefits, voting (VRK), and municipalities.",
        description=(
            "Helps residents use everyday Lithuanian public services: health insurance and family-doctor "
            "registration, education, family benefits, pensions, voting (VRK), and municipal / seniūnija "
            "services. Grounds answers in official sources such as epaslaugos.lt, ligoniukasa.lrv.lt, "
            "sodra.lt and vrk.lt."
        ),
        example_prompts=(
            "gov: how do I register with a family doctor?",
            "gov: how does compulsory health insurance (PSD) work?",
            "gov: what family benefits can new parents look up on Sodra?",
            "gov: how do I vote from abroad (VRK)?",
        ),
    ),
    # Digital
    AgentSpec(
        slug="digital", name="Digital ID & e-Services",
        category="digital", icon="#", prefix="id:",
        one_liner="Smart-ID, Mobile-ID, ID-card e-signature, and epaslaugos.lt.",
        description=(
            "Explains Lithuania's digital identity and e-service login: ID card certificates, Smart-ID "
            "and Mobile-ID, qualified e-signatures (eIDAS), and logging into Elektroniniai valdžios "
            "vartai (epaslaugos.lt). Grounds answers in official sources such as epaslaugos.lt, "
            "vssa.lrv.lt and elektroninisparasas.lt."
        ),
        example_prompts=(
            "id: how do I set up Smart-ID or Mobile-ID?",
            "id: how do I digitally sign a document and is it legally binding?",
            "id: how do I log in to epaslaugos.lt from abroad?",
            "id: what is the difference between Smart-ID and Mobile-ID?",
        ),
    ),
    # Discover
    AgentSpec(
        slug="explore", name="Discover Lithuania",
        category="discover", icon="★", prefix="lithuania:",
        one_liner="Lithuania overview, culture, and Lithuanians abroad (Globali Lietuva).",
        description=(
            "A factual guide for an international audience: Lithuania as a country, culture and public "
            "life, plus citizenship, return, and diaspora topics (Globali Lietuva, URM consular pages). "
            "Grounds answers in reputable sources such as lrv.lt, urm.lt, globalilietuva.urm.lt and "
            "keliauk.urm.lt."
        ),
        example_prompts=(
            "lithuania: give me a short intro to Lithuania",
            "lithuania: how does Globali Lietuva help Lithuanians abroad?",
            "lithuania: where do I start if I want to return to Lithuania?",
            "lithuania: what should I know about citizenship questions as a Lithuanian abroad?",
        ),
    ),
)

AGENTS_BY_SLUG: dict[str, AgentSpec] = {a.slug: a for a in AGENTS}


def by_slug(slug: str) -> AgentSpec | None:
    return AGENTS_BY_SLUG.get(slug)
