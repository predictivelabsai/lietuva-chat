"""Reusable FastHTML components for the 3-pane chat UI."""

from __future__ import annotations

import json

from fasthtml.common import (
    Div, Span, H1, H2, H3, H4, P, A, Button, Form, Input, Textarea,
    Script, NotStr, Details, Summary, Ul, Li,
)
from agents.registry import CATEGORIES, AGENTS, AGENTS_BY_SLUG
from utils.i18n import t, agent_t, category_t, LANGUAGES, js_translations
from utils.i18n_flags import flag_svg
from utils.brand import Icon, Mark, Wordmark, AGENT_ICONS, CATEGORY_ICONS
from utils.version import app_version


def _chat_lang_dropdown(lang: str = "en"):
    current = LANGUAGES.get(lang, LANGUAGES["en"])
    options = [
        Button(
            Span(NotStr(flag_svg(code)), cls="lang-dd-flag"),
            Span(info["native"], cls="lang-dd-label"),
            cls=f"lang-dd-item{' active' if code == lang else ''}",
            onclick=f"fetch('/app/config',{{method:'POST',body:new URLSearchParams({{lang:'{code}'}})}}).then(()=>location.reload())",
        )
        for code, info in LANGUAGES.items()
    ]
    return Div(
        Button(Span(NotStr(flag_svg(lang if lang in LANGUAGES else "en")), cls="lang-trigger-flag"),
               cls="lang-trigger", aria_haspopup="true", aria_expanded="false",
               onclick="toggleLangDropdown(event)"),
        Div(*options, cls="lang-dd-menu", id="lang-dd-menu"),
        cls="lang-dropdown",
    )


def signin_overlay(lang: str = "en"):
    return Div(
        Div(
            # Tab switcher
            Div(
                Button("Sign In", id="auth-tab-login", cls="auth-tab active",
                       onclick="switchAuthTab('login')"),
                Button("Register", id="auth-tab-register", cls="auth-tab",
                       onclick="switchAuthTab('register')"),
                cls="auth-tabs",
            ),
            # Login form
            Div(
                P("Sign in to your lietuva.chat account", cls="auth-copy"),
                A(
                    Span(NotStr('<svg width="18" height="18" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg"><path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.874 2.684-6.615z" fill="#4285F4"/><path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/><path d="M3.964 10.71c-.18-.54-.282-1.117-.282-1.71s.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9s.348 1.452.957 2.042l3.007-2.332z" fill="#FBBC05"/><path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/></svg>'),
                     cls="google-btn-icon"),
                    Span("Continue with Google", cls="google-btn-text"),
                    href="/auth/google",
                    cls="google-btn",
                ),
                Div(Span(cls="google-divider-line"), Span("or", cls="google-divider-text"), Span(cls="google-divider-line"), cls="google-divider"),
                Input(type="email", id="login-email", placeholder="Email", aria_label="Email",
                      cls="auth-field",
                      onkeydown="if(event.key==='Enter')document.getElementById('login-password').focus()"),
                Input(type="password", id="login-password", placeholder="Password", aria_label="Password",
                      cls="auth-field auth-field-last",
                      onkeydown="if(event.key==='Enter')doLogin()"),
                A("Forgot password?", href="#", onclick="showForgotPassword(event)",
                  cls="auth-link auth-forgot"),
                Div(id="login-error", role="alert", cls="auth-error"),
                Div(
                    Button("Sign In", onclick="doLogin()",
                           cls="auth-action auth-primary"),
                    Button("Cancel", onclick="document.getElementById('signin-overlay').classList.remove('visible')",
                           cls="auth-action auth-secondary ml-2"),
                    cls="auth-actions",
                ),
                id="auth-form-login",
            ),
            # Register form
            Div(
                P("Create an lietuva.chat account", cls="auth-copy"),
                Input(type="text", id="reg-name", placeholder="Name (optional)", aria_label="Name (optional)",
                      cls="auth-field"),
                Input(type="email", id="reg-email", placeholder="Email", aria_label="Email",
                      cls="auth-field"),
                Input(type="password", id="reg-password", placeholder="Password (min 6 chars)", aria_label="Password (min 6 chars)",
                      cls="auth-field" ,
                      onkeydown="if(event.key==='Enter')doRegister()"),
                Div(id="reg-error", role="alert", cls="auth-error"),
                Div(id="reg-success", aria_live="polite", cls="auth-success"),
                Div(
                    Button("Register", onclick="doRegister()",
                           cls="auth-action auth-primary"),
                    Button("Cancel", onclick="document.getElementById('signin-overlay').classList.remove('visible')",
                           cls="auth-action auth-secondary ml-2"),
                    cls="auth-actions",
                ),
                id="auth-form-register",
                style="display:none",
            ),
            # Forgot password form
            Div(
                P("Enter your email to receive a reset link", cls="auth-copy"),
                Input(type="email", id="forgot-email", placeholder="Email", aria_label="Email",
                      cls="auth-field",
                      onkeydown="if(event.key==='Enter')doForgot()"),
                Div(id="forgot-msg", aria_live="polite", cls="auth-message"),
                Div(
                    Button("Send Reset Link", onclick="doForgot()",
                           cls="auth-action auth-primary"),
                    A("Back to login", href="#", onclick="switchAuthTab('login');return false",
                      cls="auth-link ml-3"),
                    cls="auth-actions items-center",
                ),
                id="auth-form-forgot",
                style="display:none",
            ),
            cls="auth-panel",
        ),
        id="signin-overlay", role="dialog", aria_modal="true", aria_label="Sign in",
        cls="signin-overlay",
    )


def left_pane(user_email=None, sessions=None, current_sid="", current_agent_slug=None, lang: str = "en"):
    sessions = sessions or []

    session_items = []
    for s in sessions[:30]:
        sid = str(s.get("id", ""))
        title = (s.get("title") or "New chat")[:40]
        active_cls = " active" if sid == current_sid else ""
        session_items.append(
            Div(
                A(title, href=f"/app?sid={sid}", cls="session-item-link"),
                Button(
                    Icon("link", 14),
                    cls="session-share-btn",
                     title="Copy share link", aria_label="Copy conversation link",
                    onclick=f"event.preventDefault();event.stopPropagation();shareSession('{sid}',this)",
                ),
                cls=f"session-item{active_cls}",
            )
        )

    topic_items = [
        Button(
            Span(Icon(AGENT_ICONS.get(a.slug, "chat"), 18), cls="agent-icon"),
            Span(agent_t(a.slug, "name", lang), cls="agent-name"),
            cls=f"agent-item{' active' if a.slug == current_agent_slug else ''}",
            data_slug=a.slug,
            onclick=f"fillChat('{a.prefix} ')",
        )
        for a in AGENTS
    ]
    official_sites = [
        ("epaslaugos.lt", "https://www.epaslaugos.lt"), ("migracija.lt", "https://www.migracija.lt"),
        ("vmi.lt", "https://www.vmi.lt"), ("sodra.lt", "https://www.sodra.lt"),
        ("registrucentras.lt", "https://www.registrucentras.lt"), ("globalilietuva.urm.lt", "https://globalilietuva.urm.lt"),
    ]

    auth_section = (
        Div(
            Span(user_email, cls="account-email"),
            Button(t("chat_sign_out", lang), onclick="signOut()", cls="account-action"),
            cls="account-row",
        ) if user_email else
        Button(t("chat_sign_in", lang), onclick="showSignIn()",
               cls="auth-action auth-primary auth-full")
    )

    return Div(
        Div(
            Wordmark("/", cls="workspace-wordmark", mark_size=26),
            Button(t("chat_new", lang), onclick="newChat()",
                   cls="new-chat-btn"),
            cls="px-3 pt-3",
        ),
        Div(
            H4(t("chat_history", lang), cls="section-label"),
            Div(*session_items, cls="session-list") if session_items else
            P(t("chat_no_sessions", lang), cls="empty-copy"),
            cls="history-section",
        ),
        Div(
            H4(t("chat_topics", lang), cls="section-label"),
            Div(*topic_items, cls="topic-list"),
            Details(
                Summary(t("chat_official_sites", lang), cls="section-label sites-summary"),
                *[A(name, href=url, target="_blank", rel="noopener noreferrer", cls="workspace-link") for name, url in official_sites],
                cls="sites",
            ),
            cls="agents-section",
        ),
        Div(auth_section, cls="auth-section"),
        P(
            A(f"v{app_version()}", href="/changelog", cls="powered-by-link", title="Changelog"),
            " · Powered by ",
            A("Ravien", href="https://ravien.eu", target="_blank", rel="noopener noreferrer", cls="powered-by-link"),
            " + ",
            A("Predictive Labs", href="https://predictivelabs.ai", target="_blank",
              rel="noopener noreferrer", cls="powered-by-link"),
            cls="powered-by"),
        cls="left-pane",
    )


def center_pane(messages=None, current_agent_slug=None, lang: str = "en"):
    messages = messages or []

    msg_els = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        agent = m.get("agent_slug")
        bubble = Div(content, cls="msg-bubble")
        feedback = Div(
            Button(
                Icon("thumbs-up", 14), type="button", cls="feedback-btn feedback-up",
                data_rating="up", aria_label=t("chat_fb_up", lang),
            ),
            Button(
                Icon("thumbs-down", 14), type="button", cls="feedback-btn feedback-down",
                data_rating="down", aria_label=t("chat_fb_down", lang),
            ),
            Span(t("chat_fb_thanks", lang), cls="feedback-note", style="display:none"),
            cls="feedback-row", data_content=content, data_agent_slug=agent or "",
        )
        if role == "assistant" and agent:
            spec = AGENTS_BY_SLUG.get(agent)
            agent_label = Div(
                Mark(16, cls="msg-agent-icon"),
                Span(spec.name if spec else agent, cls="msg-agent-label"),
                cls="msg-agent",
            )
            msg_els.append(Div(agent_label, bubble, feedback, cls=f"msg msg-{role}"))
        elif role == "assistant":
            msg_els.append(Div(bubble, feedback, cls=f"msg msg-{role}"))
        else:
            msg_els.append(Div(bubble, cls=f"msg msg-{role}"))

    current_agent = AGENTS_BY_SLUG.get(current_agent_slug)

    welcome = Div(
        H1(t("chat_welcome_title", lang), cls="welcome-title"),
        P(t("chat_welcome_body", lang), cls="welcome-copy"),
        Div(
            P(Icon("info", 16), t("chat_onboard_title", lang), cls="onboard-title"),
            Ul(Li(Icon("chat", 18), Span(t("chat_onboard_1", lang))),
               Li(Icon("source", 18), Span(t("chat_onboard_2", lang))),
               Li(Icon("warning", 18), Span(t("chat_onboard_3", lang))), cls="onboard-list"),
            cls="onboard",
        ),
        Div(id="sample-cards-row", cls="sample-cards-row"),
        id="welcome-hero",
        cls="welcome-hero",
        style="" if not messages else "display:none",
    )

    header_title = current_agent.name if current_agent else "lietuva.chat"

    return Div(
        Div(
            Div(
                Button(Icon("menu", 20), cls="mobile-menu-btn", aria_expanded="false", aria_label="Open conversation list", onclick="toggleLeftPane()"),
                A(Mark(20, cls="chat-header-logo"), href="/", aria_label="lietuva.chat home"),
                Span(header_title, id="current-agent-label", cls="chat-header-title"),
                cls="chat-header-left",
            ),
            Div(
                Div(
                    *[Button(label, type="button", cls="size-btn", data_size=size, aria_pressed="false",
                             aria_label=f"{t('chat_text_size', lang)} {label}", onclick=f"setTextSize('{size}')")
                      for size, label in (("m", "A"), ("l", "A+"), ("xl", "A++"))],
                    cls="size-switch", role="group", aria_label=t("chat_text_size", lang),
                ),
                _chat_lang_dropdown(lang),
                Button(Icon("share", 16), Span(t("chat_share_label", lang), cls="hdr-label"),
                       id="share-chat-btn", onclick="shareChat()", cls="header-btn"),
                Button(Icon("copy", 16), Span(t("chat_copy_label", lang), cls="hdr-label"),
                       id="copy-chat-btn", onclick="copyChat()", cls="header-btn"),
                Button(Icon("panel", 16), Span(t("chat_results_label", lang), cls="hdr-label"),
                       id="artifact-btn", onclick="toggleArtifactPane()", cls="header-btn"),
                cls="chat-header-actions",
            ),
            cls="chat-header",
        ),
        Div(
            welcome,
            *msg_els,
            id="messages",
            cls="messages",
        ),
        Form(
            Textarea(
                id="chat-input", name="msg", rows="1",
                placeholder=t("home_placeholder", lang), aria_label=t("home_placeholder", lang),
                onkeydown="handleKey(event)", oninput="autoResize(this); onInputChange(this)",
            ),
            Button(Icon("mic", 18), id="voice-btn", type="button", cls="voice-btn",
                   aria_label=t("chat_speak", lang), title=t("chat_speak", lang),
                   aria_pressed="false", onclick="toggleVoice(event)"),
            Button(Icon("send", 20), id="send-btn", type="button", aria_label="Send message", onclick="sendMessage(event)",
                   cls="send-btn"),
            cls="chat-form", data_lang=lang,
        ),
        P(t("chat_ai_notice", lang), cls="ai-notice"),
        # Always-present, context-sensitive suggestion chips under the composer
        # (starters by default; replaced with follow-ups after each answer).
        Div(id="followups", cls="followups", aria_label=t("chat_suggestions_label", lang)),
        Script(json.dumps({a.slug: list(a.example_prompts) for a in AGENTS}),
               id="agent-prompts-data", type="application/json"),
        Script(json.dumps({a.slug: a.name for a in AGENTS}),
               id="agent-names-data", type="application/json"),
        Script(json.dumps({a.prefix.rstrip(":"): a.slug for a in AGENTS if a.prefix}),
               id="agent-prefix-map", type="application/json"),
        cls="center-pane",
    )


def right_pane(lang: str = "en"):
    return Div(
        Div(
            Div(
                H4(t("chat_artifacts_title", lang), cls="artifact-title"),
                Span(t("chat_artifacts_subtitle", lang), id="artifact-subtitle", cls="artifact-subtitle"),
            ),
            Button(Icon("close", 16), cls="right-pane-close", aria_label="Close results", onclick="toggleArtifactPane()"),
            cls="artifact-header",
        ),
        Div(
            P("Charts and tables will appear here.", cls="artifact-empty-copy"),
            id="artifact-empty",
            cls="artifact-empty",
        ),
        Div(id="artifact-body", cls="artifact-body", style="display:none"),
        id="right-pane",
        cls="right-pane",
    )
