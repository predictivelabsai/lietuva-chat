# lietuva.chat visual system

## Direction

The base is a white, Vercel-style UI: white page and cards, `#171717` ink, a fine gray scale, hairline borders and soft stacked shadows. Lithuanian character comes from three heritage sources:

- **Colour from woven sashes (*juostos*):** sash green leads. Red, yellow, blue and violet are accents, the colours traditionally woven on linen, with flag yellow among them.
- **Palemonas:** the Lithuanian Language Commission's typeface, used for headlines.
- **The talking-stone mark:** eesti.chat's stone (a rounded block with one square "speaker" corner) holding a bold geometric white l, on sash green.

There is one Apple-style liquid-glass treatment, for the composer and the scrolled nav. The site is light only.

It must never look like a government site:
- no coat of arms (Vytis);
- the flag colours are never laid out as a tricolour stripe, only mixed in the juosta ornament;
- no state-portal styling;
- never call ourselves "official".

References from [awesome-design-md](https://github.com/voltagent/awesome-design-md): the **Apple** DESIGN.md sets the page rhythm, type scale, shadow and radius rules, and the **Vercel** DESIGN.md sets the UI tokens. Also eesti.chat (nav, assistants rows) and Lithuanian sash ornament.

### Apple rules we follow
- **One interactive colour:** sash green is our "Action Blue" for links, buttons and focus. Topic hues are only non-interactive dots and tints.
- **Text:** ink `#1D1D1F`. Body copy is 17 px / 1.47 with slight negative tracking. The weight ladder is 300 / 400 / 600 / 700, never 500.
- **One shadow, only on "product" objects:** `--shadow-product` (`3px 5px 30px rgba(0,0,0,.22)`) on the demo windows and postcards. Chips and cards use a hairline ring (`--ring`) or a flat parchment fill.
- **No decorative gradients:** rhythm comes from surface alternation. The story and assistants sections are full-bleed parchment (`--panel` `#F5F5F7`), and so is the footer. Sections are never separated by rules.
- **Radius grammar:** 8 px for utility controls, 18 px for cards, pills for actions. Full-bleed sections are square.
- **Press state:** every button presses with `transform: scale(0.95)`.
- **Display type:** section titles at 40 px (Apple display-lg), the closing at about 64 px, nav links and the nav button at 14 px, the primary CTA at 17 px / 400.

We deliberately keep a few things Apple doesn't do: Palemonas serif headlines (the national typeface), the floating glass nav (instead of Apple's black bar), and the juosta strips.

## Layout

- **Site frame:** every public page sits inside one rounded white frame, inset 12 px with a 32 px radius.
- **Nav:** a floating rounded pill (eesti.chat layout).
  - Contents: wordmark, then Home / Ask AI / Topics / About / Contact, then the language switcher and a green "Ask lietuva.chat" pill.
  - The current page gets a small green dot.
  - It is flat and transparent at the top of the page and turns to liquid glass once the page scrolls (`.site-header.is-glass`).
  - Below 768 px the links fold into a Menu pill that opens the full-screen menu.
- **Home (calm, from prototype C)**, in order:
  1. **Hero, one screen:** a fine-line saulė draws itself, turns slowly and is masked away from the text. Then a mono "Labas" line, the Palemonas question "What do you need to sort out in *Lithuania?*", the glass composer, and the popular or random suggestions as quiet text links. A thin scroll cue sits at the bottom.
  2. **Juosta strip, then the question ticker.**
  3. **How it answers:** a parchment band with the section header, three numbered steps on the left and the live demo window on the right (`static/home-demo.js`). The window types a question, shows "Reading <sources>", types the answer and then the source chips. It cycles through the five life moments with topic-coloured tabs, starts when scrolled into view, stops when a tab is clicked, and is static under reduced motion.
  4. **01 Question cards:** tilted, topic-tinted.
  5. **Life moments:** one row of five cards that drifts sideways with the scroll, and becomes a snap carousel on phones.
  6. **Bento:** facts counted from the code.
  7. **03 Postcards:** with Lithuanian phrase stickers.
  8. **04 Assistants:** six rows.
  9. **Juosta strip, then the closing:** a huge "Labas*.*", the independence line and the composer again.
- The previous homepage is kept as a static snapshot in `static/prototypes/previous-home.html`, with its CSS frozen.
- **Footer:** one mono line with the independence disclaimer, privacy, version and operator.
- **Inner pages** (About, Contact, Privacy, Changelog) use the same frame and nav, with Palemonas page titles.
- **`/app`:** the chat workspace keeps its own three-pane layout and the liquid-glass composer.

## Tokens

The tokens are defined on `:root` in `static/app.css`. Tailwind colours map to the same CSS variables.

| Token | Value | Use |
| --- | --- | --- |
| `--green` / `--green-soft` | `#1E5B3F` / 14 % | Lead colour: mark tile, focus ring, dots, title accent |
| `--accent`, `--accent-fill` | `#1E5B3F` (hover `#164A33`) | Links and primary buttons |
| `--on-accent` | `#FFFFFF` | Text on primary buttons (7.7 : 1) |
| `--yellow` | `#E8A317` | Juosta |
| `--red` / `--blue` / `--violet` | `#A6262E` / `#4B5A8C` / `#6B4E9B` | Topic accents, juosta |
| `--c-green`, `--c-blue`, `--c-yellow`, `--c-red`, `--c-violet` | per topic | Demo window, topic dots, audience cards |
| `--linen` | `#F4EFE6` | Warm neutral, reserved |
| `--ink` / `--ink-2` / `--ink-3` | `#171717` / `#4D4D4D` / `#666666` | Text |
| `--paper` / `--surface` / `--frame` | `#FAFAFA` / `#FFFFFF` / `#FFFFFF` | Page, cards, frame |
| `--line` | `#EBEBEB` | Hairlines |
| `--shadow-card`, `--shadow-float` | stacked 1 px ring + small offsets | Cards, menus, demo window |
| `--glass-*`, `--glow` | see below | Composer and nav |

Topic order is the same everywhere: 1 green, 2 blue, 3 yellow, 4 red, 5 violet.

## One language for every section

- **Section header:** a mono eyebrow (`01 · …`, 12 px, `--ink-3`, number in green) above a Palemonas title (30–40 px, `-0.03em`). Left-aligned in the shared container. No side label column.
- **Card:** `--panel` fill, 18 px radius, flat (no tilt, no tint, no shadow). Hover is `--card-hover` (8 % green on panel) plus a 4 px lift. Question cards, moments, bento cards and postcards all use it. Only the story's answer card carries `--shadow-product`.
- **Colour:** green is the only filled block (the assistants bento card and the buttons). Topic hues survive only as the phrase stickers.
- **Rhythm:** every section uses the same vertical padding (72–120 px); parchment sections alternate with white.

## Chat workspace (`/app`): built for every age

Based on the GOV.UK Chat testing lessons, the patterns of the top chat apps, and research on chat interfaces for older adults.

- **Readable by default:** answers at 17 px / 1.6, user messages at 16.5 px, sidebar text at 14–15 px, 44 px touch targets.
- **Text size switch** (A / A+ / A++, saved on the device): `zoom` 1 / 1.12 / 1.25 on the messages, composer, follow-ups and sidebar.
- **Words, not just icons:** header buttons read Share, Copy chat and Tables. Icons only on phones, where Copy chat moves into each answer.
- **Onboarding card** on the empty chat, GOV.UK's three points: what it covers, check the source, don't share personal codes (and that it is independent). A permanent AI notice sits under the composer (EU AI Act Art. 50).
- **Plain status while working:** "Understanding your question…" → "Searching official websites: "<query>"…", with elapsed seconds. No playful thinking synonyms.
- **Under every answer:**
  - a **Sources** box (agency names linked, domain in mono, "check these pages before you act");
  - **Copy** and **Listen** (speech synthesis);
  - **Was this helpful? Yes / No**.
- **Voice input** (Web Speech API) in the interface language, only where the browser supports it.
- **Follow-ups** as large chips under "You could also ask". When the assistant asks a clarifying question, the chips become the answer options.
- **Sidebar:** history first, then a flat Topics list of the six assistants. Official websites fold away under a disclosure.
- **Security:** rendered markdown is always passed through DOMPurify (vendored `static/purify.min.js`) because answers can echo text from searched pages.

## Type

**Palemonas** (VLKK) for headlines, the menu's large links and the audience card titles, in Regular and Italic.
- Its licence allows free public and private use and free redistribution, but **forbids modification**.
- The original `.otf` files are therefore served byte-for-byte unchanged: no subsetting, no WOFF2 conversion. The licence text is `static/fonts/Palemonas-LICENSE-lt.txt`.

**Geist** for UI and body text, and **Geist Mono** for labels and numbers. Both are self-hosted under the OFL and cover Lithuanian and Cyrillic.

- **Headlines:** sentence case, often ending with a period, with slight negative tracking.
- **Body:** 14–17 px. Geist never goes above weight 600.
- **Eyebrows and labels:** Geist Mono 12 px.

The Beržulis faces (Studio Cryo, Lithuanian mythology) were evaluated and not used. They are too decorative for an information service, and their licence forbids redistribution.

## Liquid-glass treatment

The home composer, the chat composer, the follow-up chips and the scrolled nav share one glass treatment:
- a translucent white gradient (`--glass-bg`) behind a 14–18 px blur at 180 % saturation;
- a bright 1 px top edge and a soft inner glow at the bottom;
- a hairline outer ring and a soft drop shadow.

The chat composer floats over the conversation, so messages scroll under it. The send buttons are green circles that scale to 0.94 on press. On focus, the composer gets a green halo.

## Motion

The personality is Premium:
- **Easing:** one signature ease-out, `--ease: cubic-bezier(0.16, 1, 0.3, 1)`.
- **Durations:** `--d1` 160 ms for hover and press, `--d2` 360 ms for state changes, `--d3` 700 ms for reveals.
- **Entrance:** rise 24 px and scale up from 0.97, staggered 70 ms (well under the 500 ms stagger budget).
- **Layers:** the scroll story (statement, walk-through) is primary, card lift is secondary, and the aurora drift and greeting cycle are ambient.
- **Scroll-linked layer** (`static/home-motion.js` plus the marked block at the end of `app.css`):
  - CSS scroll-driven animations (`animation-timeline: view()`) inside `@supports`. They use the individual `translate` / `scale` properties so they compose with reveals and hover lifts.
  - The statement tile opens from a rounded `scale(0.94)` card to full width.
  - The hero demo window drifts up slower than the page (`--hero-p`, set by JS), and the copy fades slightly.
  - Juosta strips drift a few px sideways.
  - Section titles rise and fade in.
  - Postcards and bento cards get a light alternating depth.
  - Phones get no parallax.
- **Reduced motion:** everything settles to its final state.

## Shape and depth

| Element | Radius |
| --- | --- |
| In-app buttons, inputs | 6 px |
| Cards | 12–24 px |
| Demo window | 28 px |
| Nav, CTAs, chips, composer | full pill |

Shadows always combine a hairline ring with small stacked offsets, never one heavy drop.

## Logo & icons

The mark is a **talking stone**: a sash-green block with 16-unit radii and one square corner (bottom-left, pointing at the speaker), holding a bold geometric white **l** (stem plus a curved foot, an 8-unit stroke, 9.5 at 16–20 px). It mirrors eesti.chat's mark, with an l and green.

The wordmark is `lietuva` in ink with `.chat` in green, set in Geist and lowercase. Icons are a 24 px, 2 px-stroke outline set (`Icon(name)`). The kit is in `static/brand/README.md`.
