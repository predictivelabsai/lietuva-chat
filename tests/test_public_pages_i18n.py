"""About and Contact follow the selected language (issue #3), like the rest of the site."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from fasthtml.common import to_xml

from pages.about import about_page
from pages.contact import contact_page
from utils.i18n import LANGUAGES, TRANSLATIONS, t

ROOT = Path(__file__).resolve().parent.parent
PAGE_KEYS = sorted(k for k in TRANSLATIONS if k.startswith(("about_", "contact_"))) + ["nav_about", "nav_contact"]
OTHER_LANGS = [code for code in LANGUAGES if code != "en"]


@pytest.mark.parametrize("lang", OTHER_LANGS)
def test_every_about_and_contact_string_is_translated(lang):
    missing = [k for k in PAGE_KEYS if not TRANSLATIONS[k].get(lang, "").strip()]
    assert not missing, f"{lang} is missing {missing}"
    # Short labels can rightly match English ("Contact" in French); a whole sentence cannot.
    same = [k for k in PAGE_KEYS if k != "about_tech_p" and len(TRANSLATIONS[k]["en"]) > 30
            and TRANSLATIONS[k][lang] == TRANSLATIONS[k]["en"]]
    assert not same, f"{lang} still has English text for {same}"


@pytest.mark.parametrize("lang", OTHER_LANGS)
def test_pages_render_in_the_selected_language(lang):
    about = to_xml(about_page(lang))
    contact = to_xml(contact_page(lang=lang))
    assert t("about_intro", lang) in about and t("about_intro", "en") not in about
    assert t("contact_send", lang) in contact and t("contact_send", "en") not in contact


def test_contact_error_follows_the_language():
    html = to_xml(contact_page(error=t("contact_error", "lt"), lang="lt"))
    assert t("contact_error", "lt") in html


ROUTE_CHECK = """
import json
from starlette.testclient import TestClient
from utils.i18n import t
import main
c = TestClient(main.app)
c.get('/set-lang/lt')
about, contact = c.get('/about').text, c.get('/contact').text
bad = c.post('/contact', data={'name': 'A', 'email': 'nope', 'message': ''}).text
print(json.dumps({
    'about': t('about_intro', 'lt') in about and t('about_intro', 'en') not in about,
    'contact': t('contact_intro', 'lt') in contact and t('contact_intro', 'en') not in contact,
    'error': t('contact_error', 'lt') in bad,
    'title': '<title>' + t('nav_about', 'lt') in about,
}))
"""


def test_routes_use_the_language_chosen_with_set_lang():
    env = {**os.environ, "DB_URL": ""}  # never touch a configured database from a test
    out = subprocess.run([sys.executable, "-c", ROUTE_CHECK], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-2000:]
    assert json.loads(out.stdout.strip().splitlines()[-1]) == {"about": True, "contact": True, "error": True,
                                                                 "title": True}
