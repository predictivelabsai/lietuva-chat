import json
from urllib.parse import quote

from fasthtml.common import *
from utils.i18n import t, agent_t, get_lang
from utils.brand import Icon, Mark
from utils.version import app_version
from utils.i18n import LANGUAGES
from agents.registry import AGENTS, AGENTS_BY_SLUG
from tools.search import OFFICIAL_DOMAINS
from utils.brand import AGENT_ICONS
from utils import popular

# Life moments the hero conversation plays through: (number, sources read). Question, answer and
# label strings live in utils/i18n.py under life_<n>, life_<n>_q and life_<n>_a.
LIFE_MOMENTS = [
    ('01', ('epaslaugos.lt', 'migracija.lt')),
    ('02', ('vmi.lt', 'sodra.lt')),
    ('03', ('ligoniukasa.lrv.lt',)),
    ('04', ('registrucentras.lt',)),
    ('05', ('globalilietuva.urm.lt',)),
]


def _accent_last(text):
    """Split off the last word so it can carry the brand colour ("…in <em>Lithuania.</em>")."""
    head, _, last = text.rpartition(' ')
    return (head + ' ', Em(last, cls='home-title-accent')) if head else (text,)


def _composer(lang, field_id, placeholder):
    return Form(
        Label(placeholder, **{'for': field_id}, cls='visually-hidden'),
        Input(type='text', name='q', id=field_id, autocomplete='off', cls='home-composer-input', placeholder=placeholder),
        Button(Icon('mic', 18), type='button', cls='voice-btn home-voice-btn',
               title=t('chat_speak', lang), aria_label=t('chat_speak', lang),
               onclick='toggleVoice(event)'),
        Button(Icon('arrow-right', 20), type='submit', cls='home-composer-send',
               title=t('hero_cta_start', lang), aria_label=t('hero_cta_start', lang)),
        action='/app', method='get', role='search', cls='home-composer',
    )


SUN_LINES = ('M50 14 86 50 50 86 14 50Z M50 30 70 50 50 70 30 50Z M50 42 58 50 50 58 42 50Z '
             'M50 14V2 M50 98V86 M14 50H2 M98 50H86 M24.5 24.5 16 16 M75.5 24.5 84 16 M24.5 75.5 16 84 M75.5 75.5 84 84')


def _demo_script(lang):
    """The conversations as JSON for static/home-demo.js; the first one is also rendered server-side."""
    return json.dumps([
        {'q': t(f'life_{n}_q', lang), 'a': t(f'life_{n}_a', lang), 'src': list(src)}
        for n, src in LIFE_MOMENTS
    ], ensure_ascii=False)


def _demo(lang):
    """A window that looks like the product and plays a real exchange per life moment."""
    n, src = LIFE_MOMENTS[0]
    return Div(
        Div(
            Span(Mark(16), 'lietuva.chat', cls='demo-window-brand'),
            Span(t(f'life_{n}', lang), cls='demo-window-topic'),
            cls='demo-window-bar',
        ),
        Div(
            P(t(f'life_{n}_q', lang), cls='demo-q'),
            P(Span(cls='demo-dot'), t('home_reading', lang), ' ', Span(' · '.join(src), cls='demo-reading-src'),
              cls='demo-reading'),
            P(t(f'life_{n}_a', lang), cls='demo-a'),
            Div(*[Span(d, cls='demo-chip') for d in src], cls='demo-chips'),
            cls='demo-thread', aria_live='polite',
        ),
        Div(*[Button(Span(num, cls='demo-tab-num'), t(f'life_{num}', lang), type='button',
                     cls='demo-tab' + (' is-active' if k == 0 else ''), data_index=str(k),
                     aria_pressed='true' if k == 0 else 'false')
              for k, (num, _) in enumerate(LIFE_MOMENTS)], cls='demo-tabs'),
        cls='demo-window', data_topic='1', data_script=_demo_script(lang),
    )


def _how(lang):
    """How it answers: three short steps beside the live demo window."""
    steps = Ol(*[Li(B(f'0{n}'), Strong(t(f'how_{k}', lang)), Span(t(f'how_{k}_body', lang)))
                 for n, k in enumerate('abc', 1)], cls='how-steps')
    return Section(
        Div(
            P(Span('02', cls='info-num'), t('info_02', lang), cls='info-label'),
            H2(t('info_02_title', lang), cls='info-title'),
            Div(steps, _demo(lang), cls='how-grid'),
            cls='portal-container',
        ),
        cls='how',
    )


def _moments(lang):
    """Life moments as one row that drifts sideways while you scroll (home-story.js)."""
    cards = [A(Small(f'{n} · {t(f"life_{n}", lang)}'), Span(t(f'life_{n}_q', lang), cls='moment-q'),
               B(t('ask_cta', lang) + ' →', cls='moment-go'), href=_ask_href(t(f'life_{n}_q', lang)), cls='moment')
             for n, _ in LIFE_MOMENTS]
    return Section(
        H2(t('moments_title', lang), cls='moments-title fade'),
        Div(*cards, cls='moments-track', id='moments-track'),
        cls='moments', id='moments',
    )


# Questions people bring, each opening the chat with that question.
ASK_TOPICS = ['residence', 'tax', 'health', 'family', 'business', 'abroad']

# Lithuanian phrases on the audience postcards: (word, pronunciation).
PHRASES = [('Labas', 'LAH-bahs'), ('Ačiū', 'AH-chyoo'), ('Sveiki atvykę', 'SVAY-kee aht-VEE-keh')]


def _info(num, label, title, *body, id=None):
    return Section(
        Div(
            P(Span(num, cls='info-num'), label, cls='info-label'),
            Div(H2(title, cls='info-title'), *body, cls='info-body'),
            cls='portal-container info-grid',
        ),
        cls='info', id=id,
    )


def _ask_href(text):
    return f"/app?q={quote(text)}"


def _ticker(lang):
    """A slow marquee of real questions; the list is doubled so the loop is seamless."""
    items = [t(f'tick_{n}', lang) for n in range(1, 9)]
    row = [A(Span(cls='tick-dot'), q, href=_ask_href(q), cls='tick') for q in items]
    return Div(
        Div(*row, *[A(Span(cls='tick-dot'), q, href=_ask_href(q), cls='tick', tabindex='-1', aria_hidden='true')
                    for q in items], cls='ticker-track'),
        cls='ticker', aria_label=t('info_01', lang),
    )


def _juosta():
    return Div(cls='juosta', aria_hidden='true')


def _bento(lang):
    """Product facts counted from the code, so they never drift: domains searched, assistants, languages."""
    domains = Div(*[Span(d, cls='bento-domain') for d in OFFICIAL_DOMAINS[:14]], cls='bento-domains', aria_hidden='true')
    agents = Div(*[Span(Icon(AGENT_ICONS.get(a.slug, 'chat'), 22), cls='bento-agent') for a in AGENTS],
                 cls='bento-agents', aria_hidden='true')
    hellos = Div(*[Span(w, cls='bento-hello') for w in ('Labas', 'Hello', 'Привет', 'Hallo', 'Bonjour', 'Hej', 'Sveiki', 'Moi', 'Tere')],
                 cls='bento-hellos', aria_hidden='true')
    return Section(
        Div(
            P(t('bento_label', lang), cls='bento-label'),
            H2(t('bento_title', lang), cls='bento-title'),
            Div(
                Div(P(Span(str(len(OFFICIAL_DOMAINS)), cls='bento-num', data_count=str(len(OFFICIAL_DOMAINS))),
                      t('bento_sources', lang), cls='bento-stat'), domains, cls='bento-card bento-wide reveal'),
                Div(P(Span(str(len(AGENTS)), cls='bento-num', data_count=str(len(AGENTS))), t('bento_agents', lang),
                      cls='bento-stat'), agents, cls='bento-card bento-green reveal'),
                Div(P(Span(str(len(LANGUAGES)), cls='bento-num', data_count=str(len(LANGUAGES))), t('bento_langs', lang),
                      cls='bento-stat'), hellos, cls='bento-card reveal'),
                Div(H3(t('bento_cite', lang), cls='bento-h'), P(t('bento_cite_body', lang), cls='bento-p'),
                    Div(Span('vmi.lt'), Span('sodra.lt'), Span('e-tar.lt'), cls='bento-chips', aria_hidden='true'),
                    cls='bento-card bento-wide reveal'),
                Div(Mark(40), H3(t('bento_independent', lang), cls='bento-h'), P(t('bento_independent_body', lang), cls='bento-p'),
                    cls='bento-card bento-wide bento-ink reveal'),
                cls='bento-grid',
            ),
            cls='portal-container',
        ),
        cls='bento',
    )


def _info_sections(lang):
    asks = Div(*[A(Span(Span(cls='card-dot'), t(f'ask_{k}', lang), cls='qcard-topic'),
                   Span(t(f'ask_{k}_q', lang), cls='qcard-q'),
                   Span(Icon('arrow-right', 18), cls='qcard-go'),
                   href=_ask_href(t(f'ask_{k}_q', lang)), cls='qcard reveal')
                 for k in ASK_TOPICS], cls='qcards')

    who = Div(*[Div(
        Div(Span(word, cls='phrase-word'), Span(f'[{say}]', cls='phrase-say'),
            Span(t(f'phrase_{n}_meaning', lang), cls='phrase-meaning'), cls='phrase', aria_label=t('phrase_label', lang)),
        H3(t(f'who_{k}', lang), cls='who-h'), P(t(f'who_{k}_body', lang), cls='who-p'),
        cls='who-item reveal')
        for n, (k, (word, say)) in enumerate(zip(('res', 'new', 'abroad'), PHRASES), 1)], cls='who-grid')

    agents = Div(*[A(Span(Icon(AGENT_ICONS.get(a.slug, 'chat'), 26), cls='agent-row-icon'),
                     Span(Span(agent_t(a.slug, 'name', lang), cls='agent-row-name'),
                          Span(agent_t(a.slug, 'one_liner', lang), cls='agent-row-copy'), cls='agent-row-text'),
                     href=f"/app?q={quote(a.prefix)}", cls='agent-row reveal')
                   for a in AGENTS], cls='agent-rows')

    closing = Section(
        Div(
            H2(t('home_greeting', lang).rstrip('.'), Em('.'), cls='closing-title'),
            P(t('home_independent', lang), cls='closing-note fade'),
            _composer(lang, 'close-q', t('close_placeholder', lang)),
            cls='portal-container closing-inner',
        ),
        cls='closing',
    )

    return (
        _juosta(),
        _ticker(lang),
        _how(lang),
        _info('01', t('info_01', lang), t('info_01_title', lang), asks, id='topics'),
        _moments(lang),
        _bento(lang),
        _info('03', t('info_03', lang), t('info_03_title', lang), who),
        _info('04', t('topics_title', lang), t('topics_subtitle', lang), agents, P(t('info_04_body', lang), cls='src-note')),
        _juosta(),
        closing,
        Script(src=f'/static/home-story.js?v={app_version()}', defer=True),
        Script(src=f'/static/home-demo.js?v={app_version()}', defer=True),
    )


def home_page(sess=None):
    lang = get_lang(sess or {})
    hero = Section(
        Div(NotStr(f'<svg viewBox="0 0 100 100" aria-hidden="true"><path d="{SUN_LINES}"/></svg>'), cls='sun', aria_hidden='true'),
        Div(
            P(t('home_eyebrow', lang), cls='home-hello'),
            H1(*_accent_last(t('home_question', lang)), cls='home-question'),
            _composer(lang, 'home-q', t('home_placeholder', lang)),
            Div(*[A(q, href=_ask_href(q)) for q in popular.suggestions(lang)], cls='home-quiet'),
            cls='home-inner',
        ),
        Span(cls='scroll-cue', aria_hidden='true'),
        cls='home',
    )
    return (hero, *_info_sections(lang))
