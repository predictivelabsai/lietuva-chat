# Change Log

## v1.1.4 — 2026-10-06

**Allow Coolify to run the container HTTP health check.**

- Install `curl` in the Docker image so Coolify can probe `/health` on port 5011.

## v1.1.3 — 2026-10-06

**Require explicit credentials before creating an administrator account.**

- Database startup no longer creates an admin with a password embedded in the source code.
- Set `ADMIN_EMAIL` and `ADMIN_PASSWORD` (at least 12 characters) to seed an admin in a new deployment.
- Legacy `carhero` chat data is migrated only when `MIGRATE_LEGACY_CHAT=1` is set, so a fresh Lithuania deployment keeps its data separate.

## v1.1.2 — 2026-10-06

**Remove the guessable fallback for the API's token-signing secret.**

- `api/auth.py` no longer falls back to a fixed string when `JWT_SECRET` and `APP_SECRET` are unset. An empty value counts as unset too, so tokens are never signed with an empty key. The fallback is now a random key per process, as `main.py` already does for sessions.
- `.env.example` no longer ships `APP_SECRET=change-me`. It explains how to generate a real secret.
- `tests/test_auth_secret.py` forges tokens with the old strings and an empty key, and checks they are rejected.
- Deploy: set `APP_SECRET` (or `JWT_SECRET`) in production, or API logins reset on every restart.

## v1.1.1 — 2026-10-06

**Rebrand the UI to lietuva.chat: a white, conversation-first site with a Lithuanian heritage identity (woven-sash palette, Palemonas headlines, saulė mark) and liquid-glass details.**

- Identity:
  - New mark: eesti.chat's talking stone with a bold white l, on sash green.
  - `lietuva.chat` wordmark with a green `.chat`.
  - Logos, favicons, app icons and the social image are regenerated. No state symbols, and no tricolour stripe.
- Type: Palemonas (Lithuanian Language Commission) for headlines, served unmodified per its licence. Geist and Geist Mono (OFL) replace Aino.
- Colour: sash green leads (buttons, links, focus). Red, yellow, blue and violet mark the five life topics.
- Nav: floating rounded nav bar (logo, links, language, "Ask lietuva.chat"). It sits flat at the top and turns into liquid glass when you scroll. Phones get a full-screen menu instead.
- Home, rebuilt on the calm prototype C (simple, America.gov-level focus with our own touches):
  - A one-screen hero: a fine-line saulė that draws itself and turns slowly, the question "What do you need to sort out in Lithuania?", the glass composer, and the week's popular questions (or random ones) as quiet links.
  - "How it answers": three short steps beside the live demo chat window. The window types a real exchange for each life moment, with tabs to switch.
  - A life-moments row that drifts sideways.
  - The denser sections stay: question ticker, question cards, the bento of facts counted from the code, postcards with Lithuanian phrase stickers, and the six assistants.
  - Juosta strips and a big "Labas." close.
  - The suggestion pool only counts curated questions, never free text, and needs 5 sessions in 7 days (`utils/popular.py`).
  - One design language for every section: the same eyebrow-and-title header and the same flat grey card (no tilts, tints or shadows), with green as the only filled colour.
  - Copy in all nine interface languages (English, Lithuanian, Estonian, Russian, German, French, Swedish, Latvian, Finnish). Estonian moved to `locales/et.json`.
  - Prototypes A, B and C, plus a snapshot of the previous home, are in `static/prototypes/`.
- Chat page made easier for everyone, including older users:
  - bigger text and a text-size switch (A / A+ / A++);
  - labelled header buttons;
  - a "Before you start" card and an always-visible AI notice;
  - plain-language status while it works;
  - a Sources box with agency names under every answer, plus Copy, Listen and "Was this helpful? Yes / No";
  - voice input, larger follow-up chips and a simpler sidebar (history, then Topics).
- Answers are sanitised with DOMPurify before rendering. Saved answers now render as formatted text too.
- Assistants ask one clarifying question with options when the answer depends on a missing fact, and the option chips let you reply in one tap. Answers lead with a direct reply, then numbered steps in plain language.
- The site header shrinks into a frosted-glass capsule as you scroll.
- Footer in eesti.chat's structure, made our own: brand and description with a juosta strip, Ask about (the six assistants), lietuva.chat pages, official sources, and a legal row. "Powered by Ravien + Predictive Labs".
- One-line mono footer with the independence disclaimer.
- Light theme only.
- Hard-coded colours in Tailwind classes, admin and auth pages now use tokens.
- Lists in answers show their numbers and bullets again.
- Chat sidebar links now point to Lithuanian sources (epaslaugos.lt, migracija.lt, vmi.lt, sodra.lt, registrucentras.lt, globalilietuva.urm.lt, lrt.lt), and the fallback sample prompts are Lithuanian topics.
- All content now describes Lithuania:
  - UI copy in all nine interface languages;
  - the About, privacy and account pages;
  - the API, the email defaults and the README.
- Grounding: the search allowlist covers 29 official Lithuanian domains. There is a new Lithuania context prompt with an agency map, and all six assistant prompts are rewritten.
- Routing:
  - Keywords match whole words, so "taxi", "private" and "advisable" no longer trigger the tax or visa assistants.
  - Lithuanian and Russian keywords were added.
  - Only real routing prefixes (`tax:`, `move:`…) are stripped from messages, so "Note: …" is kept.
  - The LLM fallback accepts lightly decorated replies.
  - A bare prefix such as `tax:` is kept as the question instead of becoming an empty message.
  - City names alone no longer send a question to Discover ("declare residence in Vilnius" is a moving question).
  - Equal keyword scores go to the more specific topic (tax, then business), so "company + PVM" reaches Taxes.
  - More Lithuanian stems: sveikatos draudimas, individualios veiklos, grįžtu.
  - Over 470 routing tests: every keyword, every assistant's examples, the curated questions in all nine languages, and odd or random input.
- Assistants: "e-Residency & company" becomes "Business & company", and "Discover Estonia" becomes "Discover Lithuania". Slugs are unchanged, and `estonia:` links still route.
- The default database schema is now `lietuva` (override with `DB_SCHEMA`).

## v1.0.3 — 2026-10-01

**Add visitestonia.com to the official links in the chat sidebar.**

- New sidebar link: visitestonia.com (official tourism), alongside eesti.ee, eesti.ai,
  e-resident.gov.ee, rik.ee, emta.ee, ria.ee and err.ee.

## v1.0.2 — 2026-10-01

**Full UI localization for all nine languages — German, French, Swedish, Russian, Finnish, Latvian and Lithuanian now render natively (no more English fallback).**

- Translated the entire UI catalog (nav, hero, features, how-it-works, footer, chat,
  suggestions, the six assistant names/descriptions and four categories) into de, fr, sv,
  ru, fi, lv, lt — alongside the existing en and et.
- Translations now live in per-language `locales/<lang>.json` files, merged into the catalog
  at import by `_merge_locales()`; en + et remain inline. Easy to extend/edit going forward.
- Combined with IP geolocation (v1.0.1): a visitor from Sweden now sees Swedish, Germany
  German, etc., and the language switcher shows fully localized pages.

## v1.0.1 — 2026-10-01

**IP-based language defaulting — Estonian from an Estonian IP, each language from its own country, English everywhere else.**

- New `utils/geo.py`: layered IP→country detection (CDN country headers → ipapi.co / ip-api.com →
  emergency EE prefixes), stdlib-only, cached per IP, skips private IPs, short timeout, never blocks render.
- Country→language map: EE→et, RU→ru, DE/AT→de, FR→fr, SE→sv, LV→lv, FI→fi, LT→lt; anything else → English.
- A beforeware now sets the session language from the visitor's IP on first visit (a manual language
  choice always takes precedence). Previously the IP detection code never actually ran.

## v1.0.0 — 2026-10-01

**First versioned release of eesti.chat — the AI front door to Estonia.**

- AI chat portal with six specialist assistants (e-Residency & company, living & moving,
  taxes & finance, digital ID & e-services, public services, discover Estonia). Answers are
  grounded in official Estonian sources via live search and always cite their links, in the
  user's selected language.
- Access: 5 free questions, then Google SSO or email sign-up. Chat history persists for both
  guests and signed-in users (and recovers gracefully from stale sessions).
- Context-sensitive follow-up suggestion chips under the composer — starters by default and
  tailored follow-ups after each answer, so the user is never stuck.
- Working indicator rotates playful "thinking" synonyms per language; underlying tool calls
  (e.g. web search) are never surfaced in the UI.
- Official links in the sidebar: eesti.ee, eesti.ai, e-resident.gov.ee, rik.ee, emta.ee,
  ria.ee, err.ee.
- "Powered by Predictive Labs OÜ" and the app version shown near sign-in (version links here).
- White / black / Estonia-blue design in the Aino typeface; English + Estonian; live at
  https://eesti.chat. Inspired by america.gov and the U.S. State Department's ShareAmerica.
