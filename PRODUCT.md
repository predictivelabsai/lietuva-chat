# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Residents of Lithuania, newcomers planning to move, work, study or start a company there, and Lithuanians abroad (citizenship, voting, returning home). They use the service when they need a plain-language answer and a direct path to authoritative Lithuanian sources.

## Product Purpose

lietuva.chat is an independent conversational assistant for Lithuanian public services. It routes questions to specialist assistants, searches official sources, and returns a clear answer with links so people can verify the guidance.

## Positioning

The product combines a single conversational entry point with specialist routing and live grounding in official Lithuanian domains. It is independent: not a government service, never presented as official.

## Operating Context

The public site introduces the service and its topics. The /app workspace supports asking questions, reviewing a streamed answer, switching specialist assistants, opening artifacts, and returning to saved sessions.

## Capabilities and Constraints

- FastHTML renders the public pages and chat workspace.
- Specialist LangGraph agents cover business and companies, moving, taxes, digital identity, public services, and discovering Lithuania (including Lithuanians abroad).
- Chat responses use official Lithuanian sources and expose source links.
- Lithuanian and English are first-class; other languages come through the language switcher.
- Existing routes, SSE streaming, sharing, authentication, i18n strings, and mobile pane behavior must remain functional.

## Brand Commitments

The name is lietuva.chat. The visual direction is a white, Vercel-style interface with Lithuanian heritage accents: the woven-sash palette (sash green leading, with red, yellow, blue and violet), Palemonas headlines and the green talking-stone mark. The wordmark stays lowercase with the `.chat` suffix in green, paired with the saulė mark. It is an independent service and must not use state symbols (Vytis, flag) or imitate government sites.

## Evidence on Hand

Existing copy and specialist-agent definitions in the repository are the source of truth. No testimonials, customer claims, or official-government affiliation should be fabricated.

## Product Principles

- Make public-service guidance feel approachable without weakening trust.
- Put the user's question at the center of the experience.
- Keep source verification visible and easy.
- Use specialist routing to reduce navigation overhead.

## Accessibility & Inclusion

The web experience must render in light mode, maintain high text contrast, keep visible keyboard focus, and remain usable at 375px wide. Reduced-motion preferences should be respected.
