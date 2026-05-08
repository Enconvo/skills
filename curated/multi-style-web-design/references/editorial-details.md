# Editorial Details — The Marginalia That Separates Designed From Templated

Companion to **§0.5** of `SKILL.md`. Any editorial-register page (Editorial Nightscape, Brutalist Index, Atelier Couture, Reportage, Quartermaster) should hit **at least 5** of these. If it has zero, it's a template.

---

## 1. Plate folios

Every photograph gets a `Plate I/II/III…` label somewhere. Mono uppercase, gold accent.

```html
<figcaption class="plate"><em>Plate III</em> · The Library Corner</figcaption>
```

```css
.plate { font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: 0.18em; color: var(--gold); text-transform: uppercase; }
.plate em { font-style: normal; color: var(--gold); padding-right: 4px; }
```

---

## 2. Drop cap on the lede

```css
.lede::first-letter,
.dropcap {
  font-family: "Fraunces", serif;
  font-size: 1.6em;
  float: left;
  padding: 6px 10px 0 0;
  color: var(--gold);
  font-weight: 500;
  font-style: italic;
  line-height: 1;
}
```

```html
<p class="lede"><span class="dropcap">A</span> grounded tour through how money is created…</p>
```

---

## 3. Marginalia rule (Pentagram annual-report move)

```css
.margin-quote {
  border-left: 1px solid var(--gold);
  padding-left: 18px;
  font-family: "Fraunces", serif;
  font-style: italic;
  color: var(--ink-soft);
}
```

Use it next to italic captions, pull quotes, kicker quotes inside modules.

---

## 4. Displaced quote glyph

For any oversized quoted blurb:

```css
.quote-glyph {
  position: absolute;
  top: -60px; left: -40px;
  font-family: "Fraunces", serif;
  font-style: italic;
  font-size: clamp(220px, 26vw, 360px);
  color: var(--gold);
  opacity: 0.16;
  pointer-events: none;
  line-height: 1;
}
```

Single character, serif italic, accent color, behind the text not in front.

---

## 5. Vertical rotated mono captions in gutters

```css
.gutter-mark {
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  letter-spacing: 0.2em;
  color: var(--gold);
  text-transform: uppercase;
}
```

For figure stamps like `FIG. IV · PLATE III` running up the left or right margin.

---

## 6. Folio edition mark in masthead

```html
<span class="folio-mark">№ 001 — 2026</span>
<!-- or -->
<span class="folio-mark">Vol. I · 2026</span>
```

```css
.folio-mark { font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: 0.12em; color: var(--gold); }
```

---

## 7. Hanging Roman numerals (book-index style)

Use for ordered lists when the page has editorial register. NOT mono "— I" tags — those read corporate.

```html
<ol class="roman-list">
  <li><i>I</i> Money is a balance-sheet artifact, <em>not a thing</em>.</li>
  <li><i>II</i> A company is three statements in conversation.</li>
  <li><i>III</i> Markets price future expectations.</li>
  <li><i>IV</i> Risk management is the entire game.</li>
</ol>
```

```css
.roman-list { list-style: none; padding: 0; }
.roman-list li { padding-left: 48px; position: relative; line-height: 1.5;
  margin-bottom: 18px; }
.roman-list li i { position: absolute; left: 0; top: 0;
  font-family: "Fraunces", serif; font-style: italic;
  color: var(--gold); font-size: clamp(28px, 3vw, 36px); line-height: 1; }
```

---

## 8. Em-dash flanked labels

```css
.section-label {
  font-family: "JetBrains Mono", monospace;
  font-size: 11px;
  letter-spacing: 0.18em;
  color: var(--gold);
  text-transform: uppercase;
  display: flex; align-items: center; gap: 14px;
}
.section-label::before,
.section-label::after { content: "——"; color: var(--ink-faint); }
```

```html
<div class="section-label">A note from your host</div>
```

Renders as `—— A NOTE FROM YOUR HOST ——`.

---

## 9. Colophon

Italic serif, lowercase, a real sentence. NOT a copyright line.

```html
<p class="colophon">
  <em>Set in Fraunces, Inter Tight, and JetBrains Mono.
  Six plates photographed for this edition. Hosted by Vivieen.</em>
</p>
```

```css
.colophon { font-family: "Fraunces", serif; font-style: italic;
  font-size: 13px; color: var(--ink-soft); line-height: 1.6;
  max-width: 440px; }
```

---

## 10. Ligature-aware variable-axis typography

```css
h1, h2, .display {
  font-family: "Fraunces", serif;
  font-variation-settings: "SOFT" 30, "opsz" 144;
  font-feature-settings: "liga" 1, "dlig" 1;
}
.body, p {
  font-feature-settings: "kern" 1, "liga" 1;
}
```

`SOFT 30` softens the terminals on Fraunces titles; `opsz 144` triggers the display-size optical adjustments. Without these, the type looks like a default Google Fonts render.

---

## Hit rate

- **0/10** → it's a template. Redesign.
- **1–2/10** → it's a stylesheet, not a designed page.
- **3–4/10** → starting to read designed.
- **5+/10** → reads designed-by-a-human.
- **8+/10** → reads designed-by-Pentagram.

Aim for 5+ on any editorial-register page. Don't stack all 10 on one page — that's overkill and reads precious. Pick the ones that fit the subject.
