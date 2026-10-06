# lietuva.chat brand kit

The mark is a **talking stone**: a sash-green block with one square corner that points at whoever is speaking, holding a bold geometric white **l**, for lietuva. It mirrors eesti.chat's stone and e.

lietuva.chat is an independent service, not a government one. The kit deliberately avoids state symbols: no Vytis, no flag tricolour, no styling borrowed from lrv.lt or epaslaugos.lt. Lithuanian character comes only from amber and the juosta (woven sash) pattern.

## Files

| File | Use |
| --- | --- |
| `logo.svg` | Horizontal lockup on white or light grounds (default) |
| `logo-reversed.svg` | On amber |
| `logo-ink.svg` | On ink / dark grounds |
| `mark.svg`, `mark-reversed.svg`, `mark-mono.svg` | Mark only: avatars, small slots |
| `app-icon.svg`, `app-icon-maskable.svg` | Sources for the PNG app icons |
| `icons/*.svg`, `icons/sprite.svg` | 24 px icon set (`<use href="sprite.svg#i-name">`) |
| `../favicon.svg`, `../favicon.ico` | Browser tab (heavy-e variant, dark-mode aware) |
| `../apple-touch-icon.png`, `../icon-192.png`, `../icon-512.png`, `../icon-maskable-512.png` | iOS / PWA |
| `../og-image.png` | 1200 × 630 social share image |

In Python templates use `utils/brand.py`: `Wordmark()`, `Mark()`, `Icon(name)`, `brand_head()`.

## Logo rules

- Clear space is half the height of the mark on every side.
- Minimum sizes: mark 16 px, horizontal lockup 96 px wide.
- Colourways:
  - Primary: green stone, white l, ink `lietuva`, green `.chat`.
  - On green: white stone, green l, white `lietuva`, light green `.chat`.
  - On ink: white stone, ink l, white `lietuva`, light green `.chat`.
- Don't round the speaker corner, add the flag tricolour, stretch the mark, or retype the wordmark. It stays lowercase, in Geist 600 at −4 % tracking (outlined in the SVG files).

## Colour

| Name | Hex | Token |
| --- | --- | --- |
| Žalia (sash green) | `#1E5B3F` | `--green`, buttons, links, mark tile |
| Geltona (flag yellow) | `#E8A317` | juosta |
| Raudona (sash red) | `#A6262E` | topic accent |
| Mėlyna (blue) | `#4B5A8C` | topic accent |
| Violetinė | `#6B4E9B` | topic accent |
| Linas (linen) | `#F4EFE6` | warm neutral |
| Ink | `#171717` | text |

The flag colours are never laid out as a tricolour stripe. See `DESIGN.md`.

## Type

- Palemonas (VLKK) for headlines, served unmodified per its licence; Geist for text; Geist Mono for labels, code and tool steps.
- Fallback stack: `Geist, system-ui, -apple-system, 'Segoe UI', sans-serif`.

## Icons

- 24 px grid, 2 px stroke, round caps and joins, outline only.
- Most icons leave one small opening in the outline.
- Colour with `currentColor`.

