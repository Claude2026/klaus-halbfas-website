# Waterline — the KEEL design language

Waterline is the design language for **KEEL**, an operations management SaaS.
A keel is the spine that keeps a ship steady and on course; the language is
drawn from the world of marine navigation — specifically the nautical chart,
the calmest high-density information display ever printed.

## The five bearings

1. **The waterline** — every screen has one horizontal datum. Calm summary
   above (gauges), dense working depth below (ledgers, detail).
2. **Color is state** — the chrome is colorless chart paper. Beacon magenta
   marks what you can act on (after the chart convention that magenta marks
   human-made, actionable information); buoyage colors report condition.
   No decorative color exists.
3. **Contours, not shadows** — depth is drawn with hairlines and tonal steps.
   One shadow (`--wl-cast`) exists, reserved for truly floating layers.
4. **Numbers are the interface** — every figure in Spline Sans Mono with
   tabular numerals, right-aligned, comparable.
5. **One motion** — a single easing (`cubic-bezier(.22,.61,.21,1)`), three
   durations (120/240/420 ms), motion only to show causality.

## Palette

| Role | Daywatch | Nightwatch |
|---|---|---|
| Ground (Chart Paper / Deep) | `#F3F1E9` | `#0D1514` |
| Ink | `#1A2421` | `#E8E5D8` |
| **Beacon** (interactive) | `#B62E63` | `#E5719F` |
| Shoal (selection) | `#DCE7E0` | `#1B2E28` |
| Starboard / Quarantine / Port / Fog | `#177049` / `#8F6700` / `#B93A21` / `#5C6A64` | `#4EC38E` / `#E0B33F` / `#EC6E50` / `#8FA097` |

Type: **Schibsted Grotesk** (human voice) + **Spline Sans Mono** (instrument
voice). Spacing: the fathom grid, 1 fathom = 8 px.

## Files

- `waterline.css` — design tokens (both themes) + core component library
  (`wl-btn`, `wl-pennant`, `wl-gauge`, `wl-ledger`, `wl-plate`, `wl-hail`, …)
- `index.html` — the full specification, written in the language itself
- `demo.html` — **KEEL Console**, a working operations screen proving the
  language: helm, rail, gauges above the waterline, exception-first ledger,
  watch log, live chart, keyboard navigation, theme cycle (system/light/dark)
