# HyperFrames Composition (v4.2 aesthetic — locked)

## Project Layout per ACT

```
hf_act{N}/
├── index.html              # the composition
├── act{N}_anchor.mp4       # concat'd anchor base video for this ACT
└── act{N}_composite.mp4    # rendered output
```

No `package.json` needed. The `hyperframes` CLI runs against `index.html` in cwd.

## Canvas & Tracks

- Root: `<div data-composition-id="root" data-start="0" data-width="1280" data-height="720">`
- Track 0: anchor `<video>` element (full-frame base, never a side card)
- Track 1: anchor `<audio>` element (same file, audio track)
- Track 2: floating-glass chyron bug
- Track 3: scene panel divs (start/duration per scene)

## v4.2 Aesthetic Doctrine

Four rules that drive every visual decision:

1. **Overlay floats on the studio plate.** The right-42% panel is fully transparent. NO panel gradient, NO vertical divider line, NO vignette. Text + cards live directly on top of the anchor video. Per-element shadow and per-card frosted glass carry the structure.
2. **No reds, no pinks, no magenta.** The palette is ink + champagne ivory + gold. Reserve `--oxblood` for genuine emergencies only (and even then, prefer the stamped-seal pattern below). Alert callouts are an **ink + double-gold-border stamped seal**, not a red banner.
3. **Bright premium emphasis = champagne ivory (`#fff4c4`).** Use it for hero numbers that need to pop, emphasized inline terms (`<em>`), verdict strongs, callout bullets (5×, 3×, etc.). NEVER coral, NEVER pink.
4. **Chyron is a floating glass bug, not a banner.** Anchored bottom-left at 40/36px inset, frosted-glass background, compact type. It identifies the broadcaster; it does not partition the lower-third.

## Locked Palette (v4.2)

```css
--paper:    #fff7e6;    /* primary text on dark */
--paper-2:  #f3e7c8;    /* slightly warmer */
--ink:      #0a0807;    /* near-black background */
--ink-2:    #16110b;    /* slightly warmer black */
--ink-soft: rgba(255,247,230,0.72);   /* labels */
--ink-mute: rgba(255,247,230,0.45);   /* meta */
--gold:     #ffd668;    /* primary accent, kickers, rules, ticker dot, seal border */
--gold-2:   #f7c844;    /* gradient pair */
--gold-3:   #c9962f;    /* deeper gradient pair */
--oxblood:  #e63f4a;    /* RESERVED — use only for true emergencies. Default unused. */
--accent-bright: #fff4c4;            /* champagne ivory — hero number accent + emphasis */
--accent-glow:   rgba(255,244,196,0.55);
--green:    #4cd16b;    /* positive deltas (rare) */
--oxblood-2: #fff4c4;   /* legacy var name kept; value swapped to champagne ivory */
```

Glows use `text-shadow` with the matching accent color at 0.45–0.95 alpha. Every glow on a transparent panel is **paired with a black halo first** so text stays legible against any anchor frame.

Example for hero numbers:
```css
text-shadow:
  0 0 38px rgba(0,0,0,0.92),         /* black anchor halo */
  0 0 64px rgba(0,0,0,0.55),         /* soft black bloom */
  0 0 22px rgba(255,247,230,0.32);   /* warm ivory inner glow */
```

## Typography

- **Numbers (hero):** `'Fraunces', 'Noto Serif SC', 'Playfair Display', serif` — 700 weight
- **Display (CJK):** `'Noto Sans SC', 'PingFang SC', sans-serif` — 700/800 weight
- **Monospace (kickers, tickers):** `'JetBrains Mono', monospace` — 700 weight

Load CJK fonts via Google Fonts `<link>` in `<head>`. The HF compiler will auto-fetch and inline these. The lint warning about `google_fonts_import` is acceptable in exchange for full CJK coverage.

## Font Sizes (locked v4.2 defaults)

- Hero numbers: 150px
- Scene kickers: 26px (CJK) / 22px (mono)
- Layer titles: 40px
- Fact rows: 30px
- Roadmap text: 28px
- Labels (meta): 24px
- Stamped-seal callout: 26px (CJK, 0.32em tracking)
- Chyron agent name: **28px** (was 34 in v3)
- Chyron role: **17px** (was 20)
- Chyron progress: **14px** (was 16)

## Panel Anatomy (v4.2)

```html
<div class="panel clip" id="s1" data-start="0" data-duration="10" data-track-index="3">
  <span class="shimmer"></span>
  <!-- scene content here — cards / facts / numbers / seals -->
</div>
```

Notes:
- **No `<span class="vignette">`.** Removed in v4.2 — the overlay is transparent now.
- `panel` is `overflow: hidden`, `background: transparent`, `box-shadow: none`. NO vertical gold left border. NO inset gold rule on the panel itself.
- `.shimmer` is a real `<span>` inside the panel; transform-X animated by GSAP. Contained by `overflow: hidden`.

## Card / Fact / Roadmap (frosted-glass base)

Any structured content block uses this background pattern:

```css
background: rgba(10,8,7,0.42);
backdrop-filter: blur(8px);
-webkit-backdrop-filter: blur(8px);
border-left: 4px solid var(--gold);
border-radius: 0 6px 6px 0;
box-shadow: 0 10px 38px rgba(0,0,0,0.6), inset 0 0 0 1px rgba(255,214,104,0.24);
```

Darker blur for fact lists and roadmap items uses the same recipe with slightly lighter shadows. Never use the old `rgba(255,247,230,0.06)` paper tint as a card background — it disappears on a transparent panel.

## Ticker Dot (LIVE marker)

**Gold, never red.** The dot identifies an active data feed; in the v4.2 system, urgency = gold intensity, not a CNN-red emergency dot.

```css
.ticker-dot {
  width: 14px; height: 14px; border-radius: 50%;
  background: var(--gold);
  box-shadow:
    0 0 0 5px rgba(255,214,104,0.22),
    0 0 24px rgba(255,214,104,0.85),
    0 0 8px rgba(0,0,0,0.6);
}
```

Pulse animation (avoid lint warning with `overwrite: 'auto'`):
```js
tl.from('#s1 .ticker-dot', { scale: 0, opacity: 0, duration: 0.5, ease: 'back.out(2)' }, 0.7);
tl.to('#s1 .ticker-dot', { scale: 1.35, duration: 0.45, ease: 'sine.inOut', yoyo: true, repeat: 11, overwrite: 'auto' }, 1.4);
```

## Stamped Editorial Seal (replaces red alert banners)

When the script needs a warning, trap, or hard-call callout, use the seal pattern. Reads as an embossed luxury-watch certificate stamp, not a CNN alert chip.

```css
.seal {
  position: relative;
  margin-top: 10px; padding: 22px 26px;
  background: linear-gradient(90deg, rgba(10,8,7,0.78) 0%, rgba(22,17,11,0.82) 50%, rgba(10,8,7,0.78) 100%);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  color: var(--gold);
  font-family: 'Noto Sans SC', 'PingFang SC', sans-serif;
  font-weight: 800; font-size: 26px;
  letter-spacing: 0.32em; text-align: center;
  white-space: nowrap;            /* GUARDRAIL: a seal must NEVER wrap */
  border-radius: 2px;
  box-shadow:
    0 12px 44px rgba(0,0,0,0.65),
    0 0 0 1px var(--gold),                       /* outer 1px gold edge */
    inset 0 0 0 5px rgba(10,8,7,0.0),             /* spacer */
    inset 0 0 0 6px rgba(255,214,104,0.55);       /* inner gold ring */
  text-shadow: 0 0 18px rgba(255,214,104,0.5), 0 0 6px rgba(0,0,0,0.7);
}
```

**Text-fit guardrail (do not skip):** a seal / verdict / card-title must fit on its intended line count. `white-space: nowrap` forbids wrapping; pair it with SHORT copy (a seal ≤ **8 CJK glyphs**). If the phrase is longer, shorten the copy first; only then drop `font-size` (~23px) and `letter-spacing` (~0.14em) to make it fit. A seal that wrapped `其余凭空消失` with a lone `失` orphaned on line 2 once shipped into a burned video — nowrap + short copy is the primary defense, the Phase 4.5 frame audit is the backstop.

Entrance + emphasis flash uses a **gold ring pulse**, NOT a backgroundColor swap to red:
```js
tl.from('#s1 .seal', { scale: 0.6, opacity: 0, duration: 0.75, ease: 'back.out(1.9)' }, 7.4);
tl.fromTo('#s1 .seal',
  { boxShadow: '0 12px 44px rgba(0,0,0,0.65), 0 0 0 1px #ffd668, inset 0 0 0 5px rgba(10,8,7,0), inset 0 0 0 6px rgba(255,214,104,0.55)' },
  { boxShadow: '0 12px 44px rgba(0,0,0,0.65), 0 0 0 1px #ffd668, 0 0 56px rgba(255,214,104,0.7), inset 0 0 0 5px rgba(10,8,7,0), inset 0 0 0 6px rgba(255,214,104,0.95)',
    duration: 0.4, yoyo: true, repeat: 1, ease: 'power2.out' }, 8.3);
```

## Floating Glass Chyron Bug

```css
.chyron {
  position: absolute; left: 40px; bottom: 36px;
  padding: 12px 24px;
  background: rgba(10,8,7,0.42);
  backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
  border-left: 3px solid var(--gold);
  border-radius: 0 4px 4px 0;
  box-shadow: 0 8px 28px rgba(0,0,0,0.6), inset 0 0 0 1px rgba(255,214,104,0.22);
  display: flex; align-items: baseline; gap: 18px;
}
```

Do NOT use the v3 bottom-anchored dark-gradient strip. It cuts the frame.

## Critical Containment Rule

The panel still has `overflow: hidden` so the `.shimmer` sweep stays contained. With v4.2 the **panel itself is transparent**, so all readability comes from:

- Per-element text-shadow with black halo paired with warm-tone glow
- Per-card frosted-glass backgrounds with `backdrop-filter: blur(8-10px)`
- Heavy `box-shadow` drop with high alpha black to separate cards from anchor

No `::before` pseudo-elements with `mix-blend-mode: screen`. No outward panel `box-shadow` with negative x-offset. Shimmer remains a real `<span>` inside the panel.

## Emphasis Color Rule

Wherever you would have written a coral / pink / magenta emphasis color, use:

```css
color: var(--accent-bright); /* #fff4c4 */
text-shadow: 0 0 22px var(--accent-glow), 0 0 10px rgba(0,0,0,0.7);
```

Applies to: hero number variants, `<em>` inside fact-text, `<strong>` inside verdict cards, roadmap bullets, called-out figures.

## GSAP Animation Library (v4.2 updated)

All timelines paused and registered as `window.__timelines['root']`. HF drives playback.

### Counter rolling (numbers that count up)

```js
function counter(selector, atTime, dur, target, decimals) {
  const obj = { v: 0 };
  tl.to(obj, {
    v: target, duration: dur, ease: 'power2.out',
    onUpdate: () => {
      const el = document.querySelector(selector);
      if (el) el.textContent = decimals ? obj.v.toFixed(decimals) : Math.round(obj.v);
    }
  }, atTime);
}
```

### Contained shimmer sweep

```js
function shimmer(scopeSel, atTime) {
  tl.fromTo(scopeSel + ' .shimmer',
    { x: '-110%' },
    { x: '110%', duration: 1.6, ease: 'power2.inOut' }, atTime);
}
```

### Gold rule sweep + glow pulse

```js
tl.from('#s1 .gold-rule', { scaleX: 0, transformOrigin: 'left center', duration: 0.55, ease: 'power2.out' }, 1.2);
tl.fromTo('#s1 .gold-rule',
  { boxShadow: '0 0 0 rgba(255,214,104,0)' },
  { boxShadow: '0 0 32px rgba(255,214,104,0.8)', duration: 0.5, yoyo: true, repeat: 1, ease: 'sine.inOut' }, 1.7);
```

### Hero number entrance + scale-pulse + glow-pulse (v4.2 black-haloed)

```js
tl.from('#s1 .raise', { y: 50, scale: 0.7, opacity: 0, duration: 0.7, ease: 'expo.out' }, 2.2);
counter('#s1 .raise .counter', 2.2, 1.6, 75, 0);
tl.to('#s1 .raise', { scale: 1.06, duration: 0.28, ease: 'power2.out', yoyo: true, repeat: 1 }, 3.8);
tl.fromTo('#s1 .raise',
  { textShadow: '0 0 38px rgba(0,0,0,0.92), 0 0 22px rgba(255,247,230,0.32)' },
  { textShadow: '0 0 38px rgba(0,0,0,0.92), 0 0 60px rgba(255,247,230,0.85)',
    duration: 0.35, yoyo: true, repeat: 1, ease: 'sine.inOut' }, 3.85);
```

### Champagne-ivory accent glow (replaces every pink rgba(255,107,115,...))

```js
tl.fromTo('#s1 .valuation',
  { textShadow: '0 0 38px rgba(0,0,0,0.92), 0 0 26px rgba(255,244,196,0.6)' },
  { textShadow: '0 0 38px rgba(0,0,0,0.92), 0 0 64px rgba(255,244,196,0.95)',
    duration: 0.35, yoyo: true, repeat: 1, ease: 'sine.inOut' }, 6.25);
```

### Stamped-seal callout entrance + gold ring flash

```js
tl.from('#s1 .seal', { scale: 0.6, opacity: 0, duration: 0.75, ease: 'back.out(1.9)' }, 7.4);
tl.fromTo('#s1 .seal',
  { boxShadow: '0 12px 44px rgba(0,0,0,0.65), 0 0 0 1px #ffd668, inset 0 0 0 5px rgba(10,8,7,0), inset 0 0 0 6px rgba(255,214,104,0.55)' },
  { boxShadow: '0 12px 44px rgba(0,0,0,0.65), 0 0 0 1px #ffd668, 0 0 56px rgba(255,214,104,0.7), inset 0 0 0 5px rgba(10,8,7,0), inset 0 0 0 6px rgba(255,214,104,0.95)',
    duration: 0.4, yoyo: true, repeat: 1, ease: 'power2.out' }, 8.3);
tl.to('#s1 .seal', { scale: 1.03, duration: 0.35, ease: 'sine.inOut', yoyo: true, repeat: 1 }, 9.0);
```

**DEPRECATED in v4.2:** `tl.to('#s1 .trap', { backgroundColor: '#ff5666', ... })` and any GSAP that animates background-color into a red. Do not use.

### Pulsing ticker dot (gold)

```js
tl.from('#s1 .ticker-dot', { scale: 0, opacity: 0, duration: 0.5, ease: 'back.out(2)' }, 0.7);
tl.to('#s1 .ticker-dot', { scale: 1.35, duration: 0.45, ease: 'sine.inOut', yoyo: true, repeat: 11, overwrite: 'auto' }, 1.4);
```

The `overwrite: 'auto'` is critical to avoid lint warnings on overlapping tweens.

## Selector Discipline (HF lint)

- Use unique IDs or unique classes for every GSAP target.
- NEVER `:nth-of-type`, `:nth-child`, or `:first-of-type` — they fail to resolve and HF lint flags them.
- ALWAYS add `data-start="0"` on the root composition div, even if it seems redundant.

## Render Commands

From inside `hf_act{N}/`:

```bash
hyperframes lint
hyperframes render --output act{N}_composite.mp4
```

Both should return `0 errors`. Warnings are acceptable. Render time ≈35–60s for a 40s composition on M-series Mac.

## Pre-ship Layout Audit (MANDATORY — SKILL.md Phase 4.5)

Lint/validate verify STRUCTURE, not pixels. Text can wrap, overflow, or clip and still lint clean and burn straight into the MP4. After every render, extract one frame at each scene's text peak and EYEBALL it before shipping:

```bash
for t in 6 16 26 36 46; do ffmpeg -y -ss $t -i act{N}_composite.mp4 -frames:v 1 -q:v 2 qa_$t.jpg; done
```

Open each frame and confirm, per scene: no wrap orphan (lone trailing glyph), no overflow past the panel's right/bottom edge, no clipped text or anchor crown/elbow/hands, CJK glyphs render (no tofu), alignment clean. Any failure → fix HTML/CSS (shorten copy, `white-space:nowrap`, drop tracking, resize), re-render, re-audit. Only a clean audit unlocks ship.

## Acceptable Lint Warnings

These four warnings are expected and acceptable:

- `composition_self_attribute_selector` (root data-composition-id)
- `timeline_track_too_dense` (multi-scene track 3)
- `google_fonts_import` (CJK font fetch)
- `font_family_without_font_face` (PingFang SC fallback only)

Any OTHER warning, or any error, must be fixed before render.

## v3 → v4.2 Migration Checklist

If you find yourself iterating on an older composition:

- [ ] Remove `<span class="vignette">` from every scene panel.
- [ ] Remove `.panel .vignette { ... }` CSS rule.
- [ ] Set `.panel { background: transparent; box-shadow: none; }` (delete the radial+linear gradient and the gold inset box-shadow).
- [ ] Change every card/fact/roadmap background from `rgba(255,247,230,0.06)` to `rgba(10,8,7,0.42)` + `backdrop-filter: blur(8px)`.
- [ ] Set `--oxblood-2: #fff4c4`.
- [ ] Replace every `rgba(255,107,115,...)` shadow with `rgba(255,244,196,...)`.
- [ ] Add a black-halo first stop to every hero-number/emphasis text-shadow (`0 0 38px rgba(0,0,0,0.92)` then the warm glow).
- [ ] Replace any red trap banner with `.seal` stamped pattern.
- [ ] Change ticker dot from `--oxblood` to `--gold`.
- [ ] Move the chyron from a full-width bottom strip to the floating-glass bug (left:40, bottom:36).
- [ ] Delete any `tl.to('.X', { backgroundColor: '#ff...' })` red flash; replace with gold-ring `boxShadow` flash.
