from fasthtml.common import *

from utils.i18n import DEFAULT_LANG, t


INPUT_CLS = 'public-field'


def contact_page(name='', email='', message='', error='', sent=False, lang=DEFAULT_LANG):
    return Div(
        Section(
            Div(
                H1(t('contact_title', lang), cls='public-page-title'),
                P(t('contact_intro', lang), cls='public-page-intro'),
                cls='portal-container public-hero-content'
            ),
            cls='public-page-hero'
        ),
        Section(
            Div(
                Div(
                    Form(
                        *([P(error, cls='contact-error', role='alert')] if error else []),
                        *([P(t('contact_sent', lang), cls='contact-sent', role='status')] if sent else []),
                        # Honeypot: hidden from people and screen readers; bots that fill it are dropped.
                        Div(Input(type='text', name='website', tabindex='-1', autocomplete='off'),
                            cls='contact-hp', aria_hidden='true'),
                        Div(
                            Label(t('contact_name', lang), **{'for': 'contact-name'}, cls='field-label'),
                            Input(type='text', id='contact-name', name='name', placeholder=t('contact_name_ph', lang),
                                  value=name, autocomplete='name', required=True, cls=INPUT_CLS),
                        ),
                        Div(
                            Label(t('contact_email', lang), **{'for': 'contact-email'}, cls='field-label'),
                            Input(type='email', id='contact-email', name='email', placeholder='you@example.com',
                                  value=email, autocomplete='email', required=True, cls=INPUT_CLS),
                        ),
                        Div(
                            Label(t('contact_message', lang), **{'for': 'contact-message'}, cls='field-label'),
                            Textarea(message, id='contact-message', name='message', placeholder=t('contact_message_ph', lang), rows=5,
                                     required=True,
                                     cls=INPUT_CLS + ' resize-none'),
                        ),
                        Button(t('contact_send', lang), type='submit',
                               cls='public-button public-button-primary public-button-full'),
                        method='post', action='/contact',
                        cls='contact-form'
                    ),
                    cls='max-w-7xl mx-auto'
                ),
            ),
            cls='public-section public-section-alt contact-section'
        ),
    )
