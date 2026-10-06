from fasthtml.common import *


def about_page():
    return Div(
        Section(
            Div(
                H1('About lietuva', Span('.chat', cls='wordmark-suffix'),
                   cls='public-page-title'),
                P('An independent AI assistant for living, working and dealing with the state in Lithuania.',
                  cls='public-page-intro'),
                cls='portal-container public-hero-content'
            ),
            cls='public-page-hero'
        ),
        Section(
            Div(
                Div(
                    H2('What we do', cls='public-subtitle'),
                    P('lietuva.chat helps residents, newcomers and Lithuanians abroad find their way through '
                      'Lithuanian public services. Ask in plain language about residence permits, taxes and Sodra, '
                      'health insurance, starting a company, family matters or moving back home. A specialist '
                      'assistant answers from official Lithuanian sources and links them so you can check each step.',
                      cls='public-paragraph'),
                    H2('How it works', cls='public-subtitle'),
                    P('You describe what you need instead of working out which agency is responsible. A router sends '
                      'your question to the right assistant, which searches official sites such as epaslaugos.lt, '
                      'migracija.lt, vmi.lt, sodra.lt, the Health Insurance Fund, the Centre of Registers and e-TAR, '
                      'reads the current guidance and replies with citations.',
                      cls='public-paragraph'),
                    H2('Technology', cls='public-subtitle'),
                    P('Built with FastHTML, LangGraph multi-agent orchestration, xAI Grok and live Exa web search. '
                      'The interface is available in Lithuanian, English and several other languages.',
                      cls='public-paragraph'),
                    Div(
                        P('Disclaimer', cls='callout-title'),
                        P('lietuva.chat is an independent project. It is not a government service and is not '
                          'affiliated with the Government of Lithuania. Answers are AI-generated from public sources '
                          'and may be incomplete or out of date. Always confirm details with the responsible agency '
                          'before acting. This is not legal advice.',
                          cls='callout-copy'),
                        cls='public-callout',
                    ),
                    cls='public-reading-column'
                ),
                cls='portal-container'
            ),
            cls='public-section public-section-alt'
        ),
    )
