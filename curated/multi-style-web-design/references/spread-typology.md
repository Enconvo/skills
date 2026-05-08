# Spread Typology — 6 Editorial Spread Types

Companion to **§6.5** of `SKILL.md`. Use this catalog whenever a page carries **≥3 content photographs**. Pick at least 3 *different* spread types and never repeat the same type 3+ times in a row.

---

## Composition rule (the one that prevents B18 rectangle syndrome)

- **3 photographs** → 3 distinct spread types
- **4–6 photographs** → 4 distinct spread types, with at least one typographic-only module between consecutive spreads
- **7+ photographs** → reconsider whether this should be a one-page site (multi-page is out of scope)

Vary three axes simultaneously across spreads:

1. **Aspect ratio** — alternate 3:2 / 4:5 / 21:9 / 3:4. Never repeat twice in a row.
2. **Caption position** — top-left mono stamp / below-figure with rule / vertical-rotated gutter / mix-blend overlay / displaced-quote anchored.
3. **Bleed direction** — left-bleed / right-bleed / full-bleed / inset-with-gutter.

If you can't name 3+ distinct treatments before writing the first `<figure>`, you're about to ship rectangles. Stop and re-plan.

---

## A · Full-bleed split

**When:** hero, opening of a section, host band.
**Aspect:** 3:2 or 16:10. Image bleeds to one viewport edge.
**Caption:** mono stamp on photo top-left **or** vertical rotated mono in the margin.

```html
<section class="hero-grid">
  <div class="hero-text">
    <h1>Money, <em>Markets</em> & <em>Mechanics.</em></h1>
    <p class="lede"><span class="dropcap">A</span> grounded tour through how money is created…</p>
  </div>
  <figure class="hero-figure fx3d">
    <img src="/v17-page/images/scene-1.jpg" alt="…" />
    <figcaption class="plate-stamp"><em>Plate I</em> · The Penthouse · Blue Hour</figcaption>
  </figure>
</section>
```

```css
.hero-grid { display: grid; grid-template-columns: 1fr 1fr; min-height: 640px; }
.hero-figure { position: relative; margin-right: -32px; overflow: hidden;
  min-height: 640px; border-radius: 16px; }
.hero-figure img { width: 100%; height: 100%; object-fit: cover; }
.hero-figure::before { content: ""; position: absolute; inset: 0;
  background: linear-gradient(to right, rgba(10,9,8,0.55), transparent 55%);
  pointer-events: none; }
.plate-stamp { position: absolute; top: 18px; left: 22px;
  font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: 0.18em; color: var(--gold); text-transform: uppercase; }
```

**Don't** wrap in `border: 1px solid …` — the photo's edge IS the edge.

---

## B · Gutter mark + tall inset

**When:** module dividers in long content, when the lesson rhythm needs a vertical breath.
**Aspect:** 4:5 portrait inset on the right, body column in the middle.
**Caption:** italic Fraunces *below* the figure with a gold 1px left rule.

```html
<section class="spread-04">
  <span class="gutter-mark">FIG. IV · Plate III</span>
  <div class="body-col">
    <span class="module-num">03</span>
    <h2>Companies & Statements</h2>
    <p>…</p>
  </div>
  <figure class="figure fx3d">
    <img src="/v17-page/images/scene-3.jpg" alt="…" />
    <figcaption><em>Plate III</em> — The Library Corner</figcaption>
  </figure>
</section>
```

```css
.spread-04 { display: grid; grid-template-columns: 60px 1fr 320px; gap: 48px; align-items: start; }
.gutter-mark { writing-mode: vertical-rl; transform: rotate(180deg);
  font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: 0.2em; color: var(--gold); text-transform: uppercase; }
.spread-04 .figure { border-radius: 12px; aspect-ratio: 4/5; overflow: hidden; }
.spread-04 .figure img { width: 100%; height: 100%; object-fit: cover; }
.spread-04 .figure figcaption { margin-top: 14px; padding-left: 14px;
  border-left: 1px solid var(--gold); font-family: "Fraunces", serif;
  font-style: italic; font-size: 14px; color: var(--ink-soft); }
```

**Never** overlay the caption on the photo — the marginal rule does the framing.

---

## C · Cinematic 21:9 letterbox

**When:** standout module that needs movie-poster drama.
**Aspect:** wide 21:9 crop, full viewport edge-to-edge.
**Caption:** italic Fraunces inside the photo at lower-left, with a giant displaced open-quote glyph anchoring it.

```html
<section class="spread-06">
  <h2>Markets & Trading</h2>
  <figure class="cinema fx3d">
    <img src="/v17-page/images/scene-4.jpg" alt="…" />
    <figcaption class="cinema-cap">
      <em>Markets price expectations of the future, not facts about the present.</em>
    </figcaption>
  </figure>
</section>
```

```css
.cinema { position: relative; aspect-ratio: 21/9; overflow: hidden;
  margin-left: -32px; margin-right: -32px; width: calc(100% + 64px);
  border-radius: 16px; }
.cinema img { width: 100%; height: 100%; object-fit: cover; }
.cinema-cap { position: absolute; left: 64px; bottom: 48px;
  font-family: "Fraunces", serif; font-style: italic;
  font-size: clamp(20px, 2.2vw, 28px); color: var(--paper); max-width: 640px; }
.cinema-cap::before { content: "“"; position: absolute; left: -42px; top: -28px;
  font-size: 96px; color: var(--gold); opacity: 0.5; line-height: 1;
  font-family: "Fraunces", serif; }
```

---

## D · Pull-quote dominant + edge-bleed image

**When:** the *idea* in the pull quote is bigger than the photograph illustrating it.
**Aspect:** 3:4 portrait at right with right-edge bleed.
**Caption:** folio at image lower-left in mono.

```html
<section class="spread-07">
  <span class="gutter-mark">FIG. VII · Plate V</span>
  <div class="body-col">
    <span class="big-num">07</span>
    <blockquote class="pull-quote">
      <span class="rule"></span>
      Be right and you can still go to <span class="accent">zero</span>.
      Survive long enough to be wrong, then right, then right again.
    </blockquote>
  </div>
  <figure class="figure fx3d">
    <img src="/v17-page/images/scene-5.jpg" alt="…" />
    <figcaption class="folio"><em>Plate V</em> — Mykonos · Golden Hour</figcaption>
  </figure>
</section>
```

```css
.pull-quote { position: relative; padding-left: 28px;
  font-family: "Fraunces", serif; font-style: italic;
  font-size: clamp(28px, 3vw, 36px); line-height: 1.3; color: var(--ink); }
.pull-quote .rule { position: absolute; left: 0; top: 8px; bottom: 8px;
  width: 2px; background: var(--gold); }
.pull-quote .accent { color: var(--gold); }
.spread-07 .figure { margin-right: -32px; aspect-ratio: 3/4;
  border-radius: 12px; overflow: hidden; }
.folio { position: absolute; bottom: 16px; left: 18px;
  font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: 0.18em; color: var(--gold); text-transform: uppercase; }
```

---

## E · Half-circle break

**When:** host band, "about the author", testimonial.
**Aspect:** 1:1 cropped to circle (140–180px), with subtle gold ring + radial highlight.
**Caption:** none — the displaced quote glyph and italic blurb do the work.

```html
<section class="host-band">
  <figure class="host-portrait fx3d fx3d-round">
    <img src="/v17-page/images/host-avatar.jpg" alt="Host portrait" />
  </figure>
  <div class="host-blurb">
    <span class="quote-glyph">“</span>
    <p>I read markets the way a doctor reads a chart…</p>
    <span class="host-meta">Calm authority · Dry wit · Respects risk above all.</span>
  </div>
</section>
```

```css
.host-portrait { width: 160px; height: 160px; }
.host-portrait::before { content: ""; position: absolute; inset: -3px;
  border-radius: 50%; border: 1px solid var(--gold); opacity: 0.6;
  pointer-events: none; }
.host-blurb { position: relative; }
.quote-glyph { position: absolute; top: -60px; left: -40px;
  font-family: "Fraunces", serif; font-style: italic;
  font-size: clamp(220px, 26vw, 360px); color: var(--gold);
  opacity: 0.16; pointer-events: none; line-height: 1; }
```

---

## F · Right-edge break-out

**When:** closer / sign-off / takeaways pair.
**Aspect:** 3:4. Image extends past the right viewport edge.
**Caption:** folio at top-left in mono, italic Fraunces sign-off at bottom-left.

```html
<section class="closer-pair">
  <div class="closer-text">
    <h2>Four ideas that <em>actually</em> stick once the jargon fades.</h2>
    <ol class="roman-list">
      <li><i>I</i> Money is a balance-sheet artifact, <em>not a thing</em>.</li>
      <li><i>II</i> A company is three statements in conversation.</li>
      <li><i>III</i> Markets price future expectations, <em>not present facts</em>.</li>
      <li><i>IV</i> Risk management is the entire game.</li>
    </ol>
  </div>
  <figure class="closer-figure fx3d">
    <img src="/v17-page/images/scene-6.jpg" alt="…" />
    <figcaption class="folio"><em>Plate VI</em> — The Closer</figcaption>
    <p class="signoff">End · Vol I<br/><em>See you in the next lesson.</em></p>
  </figure>
</section>
```

```css
.closer-figure { position: relative; margin-right: -80px; aspect-ratio: 3/4;
  border-radius: 16px; overflow: hidden; }
.closer-figure::after { content: ""; position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(10,9,8,0.7), transparent 50%);
  pointer-events: none; }
.signoff { position: absolute; left: 28px; bottom: 28px;
  font-family: "Fraunces", serif; color: var(--paper); }
.signoff em { font-size: 22px; }
.roman-list { list-style: none; padding: 0; }
.roman-list li i { display: inline-block; width: 36px;
  font-family: "Fraunces", serif; font-style: italic;
  color: var(--gold); font-size: 22px; }
```

---

## Anti-patterns (caught by §8 of SKILL.md)

- ❌ All photographs in same 3:2 box with same `border: 1px solid …`
- ❌ Every caption in the same lower-left gradient bar
- ❌ Repeated card layout for 3+ content modules in a row
- ❌ Mono `— I` / `— II` tags as ordered list markers (use Roman numerals in italic gold serif)

## Hosted-variant rule (B21 fix)

If a "lesson / essay / report / finance" page acquires a named human host carrying ≥3 photographs of them → switch shell to **Editorial Nightscape** (or any Tier-B editorial shell), apply this typology, and run the §0.5 editorial details checklist. Subject type is not fixed at start of session.
