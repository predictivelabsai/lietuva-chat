from fasthtml.common import *

from utils.i18n import DEFAULT_LANG, t


def about_page(lang=DEFAULT_LANG):
    return Div(
        Section(
            Div(
                H1(f"{t('about_h1_prefix', lang)} lietuva", Span('.chat', cls='wordmark-suffix'),
                   cls='public-page-title'),
                P(t('about_intro', lang),
                  cls='public-page-intro'),
                cls='portal-container public-hero-content'
            ),
            cls='public-page-hero'
        ),
        Section(
            Div(
                Div(
                    H2(t('about_what_h', lang), cls='public-subtitle'),
                    P(t('about_what_p', lang), cls='public-paragraph'),
                    H2(t('about_how_h', lang), cls='public-subtitle'),
                    P(t('about_how_p', lang), cls='public-paragraph'),
                    H2(t('about_tech_h', lang), cls='public-subtitle'),
                    P(t('about_tech_p', lang), cls='public-paragraph'),
                    Div(
                        P(t('about_disclaimer_h', lang), cls='callout-title'),
                        P(t('about_disclaimer_p', lang), cls='callout-copy'),
                        cls='public-callout',
                    ),
                    cls='public-reading-column'
                ),
                cls='portal-container'
            ),
            cls='public-section public-section-alt'
        ),
    )
