# Design DNA library

Seven keynote-register directions, each modelled on the public look of a
well-known product and restated for slides. Consulting and banking decks use
the two DNAs in `register-dna.md` (8 Advisory Ink, 9 Board Ledger) instead. In
workflow step 2, pick the DNA whose world suits the subject and the room,
adapt it, and keep its guardrails. Never use a company's DNA on a deck that
competes with that company (no Product Whiteout for a consumer-hardware
pitch); build a fresh system instead.

How to use them:

- **Adapt, do not copy.** Take the colour logic, the type attitude, and the
  spacing rhythm, then compose slides with them. Nobody should mistake the deck
  for the product's website.
- **One DNA per deck.**
- **Font-ban exception.** The quality floor bans Inter, Arial, and Helvetica
  headlines *as defaults*. A DNA whose identity is one of those faces may use
  it on purpose, in HTML mode only. PPTX always takes the DNA's safe-font line.
- **Record the choice.** Note which DNA the last deck used; quality-floor
  rule 12 makes the next deck move on.
- **Keep the deck type scale.** Borrow faces, weights, tracking, and colour
  roles, not web pixel sizes.
- Most original display faces are paid. Each DNA names a Google-font
  stand-in (HTML) and a safe-list pairing (PPTX).

---

## 1 · Void Console (Linear-style dark minimalism)

- **Tokens:** bg `08090A` · surface `0F1011` · fg `F7F8F8` · secondary
  `8A8F98` · muted `62666D` · border `23252A` · accent `5E6AD2`
- **Type:** HTML Inter 510–600, tracking −0.02em, display leading 1.0–1.1,
  JetBrains Mono for figures. PPTX Calibri bold / Calibri / Courier New.
- **Feel:** grey everywhere except the one datum that matters, which takes
  the indigo. Hairlines instead of shadows; small even spacing (4/8/12/24).
- **Guardrails:** no full-bleed gradients; status colours live inside charts
  only; headlines never take the accent; display tracking stays tight.
- **Suits:** engineering reviews, infrastructure proposals, roadmaps for
  technical leaders.

## 2 · Black IDE (Framer-style tool black)

- **Tokens:** bg `000000` · surface `111111` / `1E1E1E` · fg `FFFFFF` ·
  secondary `999999` · muted `666666` · accent `0099FF` · one positive datum
  may use `00BB88`
- **Type:** HTML Figtree or Schibsted Grotesk 500 (−0.03em), Inter body,
  IBM Plex Mono details. PPTX Calibri bold / Arial.
- **Feel:** panels butt together like a tool window, corners 6–10px, light
  grain allowed on black. The blue appears as thin lines and one soft glow.
- **Guardrails:** the accent covers a small area only; display and body faces
  keep their jobs; chips get small radii, never pills.
- **Suits:** developer-tool pitches, creative-tool strategy, product demos.

## 3 · Nocturne Rail (Railway-style editorial dark)

- **Tokens:** bg `13111C` · surface `1C1A28` · fg `F7F7F8` · secondary
  `A1A0AB` · muted `6B7280` · border `33323E` · accent `59497A` (use `8B77B8`
  where it must be read on dark) · success `428A72`
- **Type:** HTML IBM Plex Serif 500 display (−0.02em), Inter body, JetBrains
  Mono labels. PPTX Cambria bold / Arial.
- **Feel:** a serif headline on a violet-black ground gives weight and calm.
  Generous section padding; at most one illustrated band.
- **Guardrails:** the serif stays in headlines; each hue has one job and
  structure stays grey; two-column stages rather than bento grids.
- **Suits:** re-platforming cases, technical strategy with a story, serious
  post-mortems.

## 4 · Product Whiteout (Apple-style flat retail light)

- **Tokens:** bg `FFFFFF` · band `F5F5F7` · fg `1D1D1F` · secondary tints of
  fg · accent `0071E3` · closing band `000000`
- **Type:** HTML system-ui 600 display (−0.01em), same family 400 body. PPTX
  Calibri bold / Calibri.
- **Feel:** hierarchy from weight alone. Slides alternate white and `F5F5F7`
  grounds in place of cards; one subject per slide; square panels.
- **Guardrails:** blue marks actions only, never headlines or grounds; no
  shadows on content; pills only on buttons and labels.
- **Suits:** launches, consumer proposals, any deck where restraint signals
  confidence.

## 5 · Warm Paper Editorial (Anthropic-style cream and ink)

- **Tokens:** bg `F0EEE6` · surface `E3DACC` · fg `141413` · muted `B0AEA5`
  (captions on cream: `8A867C`) · dark band `141413` with `FAF9F5` text ·
  accent `D97757`, rare
- **Type:** HTML Instrument Sans 600–700 display, Source Serif 4 body, IBM
  Plex Mono details. PPTX Calibri bold / Century Schoolbook.
- **Feel:** text-led slides divided by hairlines, not boxes. Content corners
  square; only the single dark band is rounded (16–24px). The clay accent
  shows up twice per deck at most.
- **Guardrails:** the dark band stays one contained element; no shadows or
  gradients behind lists; no stock imagery. This is the one DNA where a warm
  ground is the point rather than a default.
- **Suits:** research readouts, strategy memos as slides, argument-first
  board papers.

## 6 · Ink Documentation (Cursor-style paper IDE)

- **Tokens:** bg `F7F7F4` · surface `F2F1ED` / `E6E5E0` · fg `26251E` · ink
  `000000` · accent `F54E00` · gold chip `C08532`, once at most
- **Type:** HTML Archivo or Space Grotesk display, EB Garamond prose,
  JetBrains Mono data. PPTX Calibri bold / Century Schoolbook.
- **Feel:** flat window-style cards, 2px corners, hairline borders, wide gaps
  between sections. The serif is for quotes and long passages.
- **Guardrails:** no saturated grounds or gradients; orange and one gold chip
  are the only colour; serif never in titles or labels; corners sharp except
  pill buttons.
- **Suits:** documentation-heavy proposals, quality or process reviews,
  academic technical audiences.

## 7 · Meadow Ledger (Wise-style lime and heavy black)

- **Tokens:** bg `FFFFFF` · punch `9FE870` with `0E0F0C` · fg `0E0F0C` ·
  secondary `454745` · muted `6A6C6A` · calm `ECF9F9` · forest band `163300`
  with lime text · positive `008026`
- **Type:** HTML Anton or Archivo Black at leading ~0.9, Inter body. PPTX
  Arial Bold at maximum size contrast / Calibri; the condensed-heavy effect
  fully works only in HTML.
- **Feel:** a white money-app system with one loud lime slide. Forest carries
  structure; 30px corners on feature cards only; hairlines, no shadows.
- **Guardrails:** **one lime plane per deck**, on the title or the ask.
  Elsewhere lime is punctuation, **one mark per slide** (a bar, a cell, or a
  step dot); a second mark turns forest. Lime is a ground, never text on
  white (`9FE870` on white is 1.5:1): ink on lime is 13:1, lime on forest
  9.4:1. Never lighten the display weight. Forest band for trust or closing
  content only.
- **Suits:** fintech, pricing and cost decks, a young executive audience that
  wants one bold moment.

---

HTML motion that fits all seven: 100–160ms for colour and state changes, 160ms
`cubic-bezier(0.25, 0.46, 0.45, 0.94)` for reveals and panel moves, 400ms
ease-out for background fills. Quick and exact; nothing springs.
