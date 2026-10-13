"""Contact form: validate a message and deliver it to the lietuva.chat inbox via Postmark."""

from __future__ import annotations

import html
import logging
import os
import re
from typing import Callable

from utils.email import send_email

log = logging.getLogger(__name__)

MAX_NAME = 200
MAX_MESSAGE = 5000
# No whitespace or list/quote characters, so the address is also safe as a single Reply-To.
_EMAIL = re.compile(r"[^@\s,;<>\"]+@[^@\s,;<>\"]+\.[^@\s,;<>\"]+")
_CONTROL = re.compile(r"[\x00-\x1f\x7f]+")


def check_contact(name: str, email: str, message: str) -> str | None:
    """Translation key of the problem with the form, or None when it can be sent."""
    if not _EMAIL.fullmatch((email or "").strip()) or not (message or "").strip():
        return "contact_error"
    if len(name or "") > MAX_NAME or len(message) > MAX_MESSAGE:
        return "contact_too_long"
    return None


def contact_inbox() -> str:
    return os.getenv("TO_EMAIL", "").strip() or os.getenv("FROM_EMAIL", "info@lietuva.chat")


def deliver_contact(name: str, email: str, message: str, *, lang: str, to: str | None = None,
                    send: Callable[..., dict] = send_email) -> bool:
    """Send one contact message; True only when the provider accepted it."""
    email = email.strip()
    who = _CONTROL.sub(" ", (name or "").strip())[:MAX_NAME] or email
    text = f"From: {who} <{email}>\nLanguage: {lang}\n\n{message}"
    body = (f"<p><strong>From:</strong> {html.escape(who)} &lt;{html.escape(email)}&gt;<br>"
            f"<strong>Language:</strong> {html.escape(lang)}</p>"
            f"<p style=\"white-space:pre-wrap\">{html.escape(message)}</p>")
    result = send(to=to or contact_inbox(), subject=f"lietuva.chat contact: {who}", html_body=body,
                  text_body=text, reply_to=email, tag="contact")
    if result.get("ErrorCode") == 0:
        return True
    log.error("contact message not delivered: %s", result.get("error") or result.get("Message"))
    return False
