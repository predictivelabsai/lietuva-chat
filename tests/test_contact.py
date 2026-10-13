"""The contact form actually delivers messages, safely (follow-up to issue #3)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from utils.contact import MAX_MESSAGE, check_contact, deliver_contact

ROOT = Path(__file__).resolve().parent.parent


class FakeSend:
    """Stands in for utils.email.send_email (injected, not patched)."""

    def __init__(self, result=None):
        self.calls, self.result = [], result or {"ErrorCode": 0, "MessageID": "m-1"}

    def __call__(self, **kw):
        self.calls.append(kw)
        return self.result


def test_valid_message_is_sent_to_the_inbox_with_reply_to():
    send = FakeSend()
    assert deliver_contact("Rūta", "ruta@example.lt", "Labas!", lang="lt", to="inbox@lietuva.chat", send=send)
    kw = send.calls[0]
    assert kw["to"] == "inbox@lietuva.chat" and kw["reply_to"] == "ruta@example.lt"
    assert "Rūta" in kw["subject"] and "Labas!" in kw["text_body"] and "lt" in kw["text_body"]


def test_user_text_cannot_inject_html_or_headers():
    send = FakeSend()
    deliver_contact("Eve\r\nBcc: x@y.z", "eve@example.com", "<script>alert(1)</script>", lang="en",
                    to="inbox@lietuva.chat", send=send)
    kw = send.calls[0]
    assert "\r" not in kw["subject"] and "\n" not in kw["subject"]
    assert "<script>" not in kw["html_body"] and "&lt;script&gt;" in kw["html_body"]


def test_provider_failure_is_reported():
    assert not deliver_contact("A", "a@example.com", "hi", lang="en", to="inbox@lietuva.chat",
                               send=FakeSend({"error": "POSTMARK_API_TOKEN not set"}))
    assert not deliver_contact("A", "a@example.com", "hi", lang="en", to="inbox@lietuva.chat",
                               send=FakeSend({"ErrorCode": 300, "Message": "Invalid email"}))


def test_checks():
    assert check_contact("A", "a@example.com", "hi") is None
    assert check_contact("A", "not-an-email", "hi") == "contact_error"
    for sneaky in ("a,b@example.com", "a@example.com;c@d.ee", "<a@example.com>", '"a"@example.com'):
        assert check_contact("A", sneaky, "hi") == "contact_error", sneaky
    assert check_contact("A", "a@example.com", "   ") == "contact_error"
    assert check_contact("A", "a@example.com", "x" * (MAX_MESSAGE + 1)) == "contact_too_long"
    assert check_contact("A" * 300, "a@example.com", "hi") == "contact_too_long"


ROUTE_CHECK = """
import json
from starlette.testclient import TestClient
from utils.i18n import t
import main
c = TestClient(main.app, follow_redirects=False)
c.get('/set-lang/lt')
ok = {'name': 'A', 'email': 'a@example.com', 'message': 'Labas'}
bot = c.post('/contact', data={**ok, 'website': 'http://spam'})
fail = c.post('/contact', data=ok)
sent = c.get('/contact?sent=1').text
bad = c.post('/contact', data={**ok, 'email': 'nope'}).text
print(json.dumps({
    'bot_redirect': bot.status_code == 303 and bot.headers['location'] == '/contact?sent=1',
    'failure_shown': fail.status_code == 200 and t('contact_send_failed', 'lt') in fail.text,
    'fields_kept': 'Labas' in fail.text,
    'thanks_shown': t('contact_sent', 'lt') in sent,
    'invalid_shown': t('contact_error', 'lt') in bad,
    'honeypot_hidden': 'name="website"' in sent and 'aria-hidden="true"' in sent,
}))
"""


def test_route_flow_without_a_mail_provider():
    # No Postmark token and no database: a real send fails, so failure handling is visible;
    # the honeypot path must still redirect without trying to send.
    env = {**os.environ, "DB_URL": "", "POSTMARK_API_TOKEN": ""}
    out = subprocess.run([sys.executable, "-c", ROUTE_CHECK], cwd=ROOT, env=env,
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr[-2000:]
    result = json.loads(out.stdout.strip().splitlines()[-1])
    assert result == {k: True for k in result}, result
