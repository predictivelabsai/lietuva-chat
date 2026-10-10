from fasthtml.common import *
from utils.i18n import t, agent_t, LANGUAGES, get_lang, DEFAULT_LANG
from utils.i18n_flags import flag_svg
from utils.brand import Wordmark, brand_head
from utils.version import app_version


def app_styles():
    return (
        Meta(charset='utf-8'),
        *brand_head(),
        Style("""
        @font-face {
          font-family: 'Geist';
          src: url('/static/fonts/Geist.woff2') format('woff2');
          font-weight: 100 900;
          font-style: normal;
          font-display: swap;
        }
        @font-face {
          font-family: 'Geist';
          src: url('/static/fonts/Geist-Italic.woff2') format('woff2');
          font-weight: 100 900;
          font-style: italic;
          font-display: swap;
        }
        @font-face {
          font-family: 'Palemonas';
          src: url('/static/fonts/Palemonas-Regular.otf') format('opentype');
          font-weight: 400;
          font-style: normal;
          font-display: swap;
        }
        @font-face {
          font-family: 'Palemonas';
          src: url('/static/fonts/Palemonas-Italic.otf') format('opentype');
          font-weight: 400;
          font-style: italic;
          font-display: swap;
        }
        @font-face {
          font-family: 'Geist Mono';
          src: url('/static/fonts/GeistMono.woff2') format('woff2');
          font-weight: 100 900;
          font-style: normal;
          font-display: swap;
        }
        """),
        Meta(name='color-scheme', content='light'),
        Meta(name='viewport', content='width=device-width, initial-scale=1'),
        Link(rel='stylesheet', href='/static/tw.css'),
        Link(rel='stylesheet', href=f'/static/app.css?v={app_version()}'),
    )


def _lang_switcher(lang: str = "en"):
    current = LANGUAGES.get(lang, LANGUAGES["en"])
    current_code = lang.upper() if lang in LANGUAGES else "EN"
    options = []
    for code, info in LANGUAGES.items():
        active_cls = ' font-semibold text-ink' if code == lang else ''
        options.append(
            A(Span(NotStr(flag_svg(code)), cls='mr-2 lang-dd-flag'), Span(info["native"], cls='text-xs'),
              href=f'/set-lang/{code}',
              cls=f'lang-option flex items-center gap-1 px-3 py-1.5 text-sm text-ink-3 hover:bg-bg-alt hover:text-accent transition-colors no-underline{active_cls}')
        )
    return Div(
        Button(
               Span(NotStr(flag_svg(current_code.lower())), cls='lang-trigger-flag'),
               Span(current_code, cls='lang-trigger-code'),
               NotStr('<svg class="lang-trigger-chevron" aria-hidden="true" width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="m2 3.5 3 3 3-3"/></svg>'),
               type='button',
               cls='lang-trigger',
               aria_haspopup='true', aria_expanded='false',
               onclick="this.nextElementSibling.classList.toggle('hidden'); this.setAttribute('aria-expanded', this.nextElementSibling.classList.contains('hidden') ? 'false' : 'true')"),
        Div(*options,
            cls='hidden absolute right-0 top-full mt-1 bg-surface border border-line rounded shadow-sm z-50 py-1 min-w-[130px] flex flex-col'),
        cls='relative',
    )


def SiteHeader(active='home', sess=None):
    """Floating rounded nav. It sits flat at the top and turns to liquid glass once the page scrolls."""
    lang = get_lang(sess or {})
    links = [
        ('home', '/', t('nav_home', lang)),
        ('advisory', '/app', t('nav_ask', lang)),
        ('topics', '/#topics', t('nav_topics', lang)),
        ('about', '/about', t('nav_about', lang)),
        ('contact', '/contact', t('nav_contact', lang)),
    ]
    return Header(
        Div(
            Wordmark('/', mark_size=28),
            Nav(*[A(label, href=href, cls='site-nav-link' + (' active' if key == active else ''),
                    aria_current='page' if key == active else None) for key, href, label in links],
                cls='site-nav-links', aria_label='Main'),
            Div(
                _lang_switcher(lang),
                A(t('header_cta', lang), href='/app', cls='site-nav-cta'),
                Button(t('menu', lang), type='button', cls='menu-pill site-nav-menu', aria_controls='site-menu',
                       aria_expanded='false', onclick="openMenu(this)"),
                cls='site-header-actions',
            ),
            cls='site-nav',
        ),
        cls='site-header',
    )


def SiteMenu(active='home', sess=None):
    from agents.registry import AGENTS_BY_SLUG
    lang = get_lang(sess or {})
    topics = ["eresidency", "moving", "tax", "digital", "services", "explore"]
    pages = [
        ('home', '/', t('nav_home', lang)),
        ('advisory', '/app', t('nav_ask', lang)),
        ('about', '/about', t('nav_about', lang)),
        ('contact', '/contact', t('nav_contact', lang)),
    ]
    quiet = [
        ('privacy', '/privacy', t('footer_privacy', lang)),
        ('changelog', '/changelog', f'Changelog · v{app_version()}'),
        ('signin', '/app', t('menu_sign_in', lang)),
    ]
    return Div(
        Div(
            Div(
                Wordmark('/', mark_size=28),
                Button(t('menu_close', lang), type='button', cls='menu-pill', onclick='closeMenu()'),
                cls='site-menu-head',
            ),
            Div(
                Nav(
                    P(t('menu_service', lang), cls='menu-label'),
                    *[A(label, href=href, cls='menu-link' + (' active' if key == active else ''),
                        aria_current='page' if key == active else None) for key, href, label in pages],
                    Div(*[A(label, href=href, cls='menu-quiet-link', aria_current='page' if key == active else None)
                          for key, href, label in quiet], cls='menu-quiet'),
                    cls='menu-col',
                ),
                Nav(
                    P(t('menu_ask_about', lang), cls='menu-label'),
                    *[A(agent_t(slug, 'name', lang), href=f"/app?q={AGENTS_BY_SLUG[slug].prefix.strip()}",
                        cls='menu-topic') for slug in topics],
                    cls='menu-col',
                ),
                cls='menu-body',
            ),
            P(t('home_independent', lang), cls='menu-foot'),
            cls='site-menu-inner',
        ),
        id='site-menu', cls='site-menu', role='dialog', aria_modal='true', aria_label=t('menu', lang), hidden=True,
    )


def SiteFooter(lang: str = "en"):
    """eesti.chat's footer structure (brand, three link columns, legal row), in lietuva.chat's own voice."""
    from fasthtml.components import Footer as FooterTag
    from agents.registry import AGENTS
    from urllib.parse import quote

    def col(title, *links):
        return Div(H4(title, cls='footer-heading'), Ul(*[Li(link) for link in links], cls='footer-links'), cls='footer-col')

    def ext(name, url):
        return A(name, href=url, target='_blank', rel='noopener noreferrer')

    return FooterTag(
        Div(
            Div(
                Wordmark('/', mark_size=30),
                P(t('footer_desc', lang), cls='footer-desc'),
                Div(cls='footer-juosta', aria_hidden='true'),
                cls='footer-brand',
            ),
            col(t('menu_ask_about', lang),
                *[A(agent_t(a.slug, 'name', lang), href=f'/app?q={quote(a.prefix)}') for a in AGENTS]),
            col(t('menu_service', lang),
                A(t('nav_about', lang), href='/about'), A(t('nav_contact', lang), href='/contact'),
                A(t('footer_changelog', lang), href='/changelog'), A(t('footer_privacy', lang), href='/privacy'),
                A(t('footer_delete', lang), href='/delete-account')),
            col(t('footer_sources', lang),
                ext('epaslaugos.lt', 'https://www.epaslaugos.lt'), ext('migracija.lt', 'https://www.migracija.lt'),
                ext('vmi.lt', 'https://www.vmi.lt'), ext('sodra.lt', 'https://www.sodra.lt'),
                ext('e-tar.lt', 'https://www.e-tar.lt')),
            cls='footer-grid',
        ),
        Div(
            P(t('footer_copyright', lang), ' · ', A(f'v{app_version()}', href='/changelog'), ' · Powered by ',
              ext('Ravien', 'https://ravien.eu'), ' + ', ext('Predictive Labs', 'https://predictivelabs.ai'),
              cls='footer-meta'),
            P(t('footer_disclaimer', lang), cls='footer-disclaimer'),
            cls='footer-bottom',
        ),
        cls='site-footer',
    )


MENU_JS = """
function openMenu(btn) {
    var m = document.getElementById('site-menu');
    m.hidden = false; document.body.classList.add('menu-open');
    if (btn) btn.setAttribute('aria-expanded', 'true');
    var first = m.querySelector('.menu-link'); if (first) first.focus();
}
function closeMenu() {
    var m = document.getElementById('site-menu');
    m.hidden = true; document.body.classList.remove('menu-open');
    var b = document.querySelector('.site-nav-menu');
    if (b) { b.setAttribute('aria-expanded', 'false'); b.focus(); }
}
document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && !document.getElementById('site-menu').hidden) closeMenu();
});
(function () {
    var header = document.querySelector('.site-header');
    if (!header) return;
    function sync() { header.classList.toggle('is-glass', window.scrollY > 8); }
    sync();
    window.addEventListener('scroll', sync, { passive: true });
})();
document.addEventListener('click', function (e) {
    var dd = e.target.closest('.relative');
    document.querySelectorAll('.relative > div').forEach(function (d) {
        if (d.parentElement !== dd) d.classList.add('hidden');
    });
});
"""


def Page(content, active='home', title='', sess=None):
    import json as _json
    from utils.i18n import js_translations
    lang = get_lang(sess or {})
    return (
        A('Skip to main content', href='#main-content', cls='skip-link'),
        Title(f'{title} | lietuva.chat · AI assistant for Lithuania') if title else Title('lietuva.chat · AI assistant for Lithuania'),
        Div(
            SiteHeader(active, sess=sess),
            Main(content, id='main-content', cls=f'site-main site-main-{active}'),
            SiteFooter(lang),
            cls='site-frame' + (' site-frame-home' if active == 'home' else ''),
        ),
        SiteMenu(active, sess=sess),
        Script(MENU_JS),
        Script(_json.dumps(js_translations(lang), ensure_ascii=False), id='i18n-data', type='application/json'),
        Script(src=f'/static/voice.js?v={app_version()}'),
    )
