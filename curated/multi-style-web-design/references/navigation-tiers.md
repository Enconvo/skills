# Navigation Tiers — Tier A / Tier B / Tier C

Companion to **§4.5** of `SKILL.md`. Pick **one tier per shell** based on its register; never skip nav on pages with ≥3 sections.

| Tier | Register | Components | Default for these shells |
|---|---|---|---|
| **A — Full** | App-polish, sticky pill nav | Sticky blur-glass nav bar + 4 link pills + active-section dot + scroll-progress bar + kbd hint chip + floating back-to-top | `studio-black` `stadium` `neon-arcade` `holographic-future` `reportage` |
| **B — Editorial** | Sticky masthead-style TOC | Sticky thin masthead + 4 mono uppercase TOC links separated by hairline rules + section-symbol active marker + 1px scroll progress | `brutalist-index` `editorial-nightscape` `atelier-couture` `studio-spectrum` `panel` `quartermaster` |
| **C — Whisper-quiet** | Almost invisible | Right-edge dot rail (5px dots) + tiny scroll-progress hairline; **both fade in only after scrolling past 200px**; original masthead stays untouched | `glass-library` `swiss-modernist` `riso-pop` `gallery-white` `soft-organic` |

---

## Required structural pieces (every variant, every tier)

```html
<html lang="en">
<head>
  <style>
    html { scroll-behavior: smooth; overflow-x: clip; }
    body { overflow-x: clip; width: 100%; max-width: 100vw; }
    section[id], article[id] { scroll-margin-top: 72px; }
  </style>
</head>
<body>
  <section id="hero">…</section>
  <section id="curriculum">…</section>   <!-- alias: products / features / articles -->
  <section id="equation">…</section>     <!-- alias: pullquote / cinematic-block -->
  <section id="takeaways">…</section>
</body>
```

The four canonical IDs are **mandatory** so the scrollspy script can target them by name. Per-shell aliases are accepted (e.g. Reportage uses `pullquote` instead of `equation`); document any aliases in that shell's `README.md` (B17 fix).

---

## Tier A — Full

**HTML:**

```html
<nav class="nav-bar">
  <div class="nav-inner">
    <a class="brand" href="#hero">M.M.M.<span class="brand-meta">L01/07</span></a>
    <ul class="nav-links">
      <li><a href="#hero" class="nav-link">Hero</a></li>
      <li><a href="#curriculum" class="nav-link">Curriculum</a></li>
      <li><a href="#equation" class="nav-link">Equation</a></li>
      <li><a href="#takeaways" class="nav-link">Takeaways</a></li>
    </ul>
    <kbd class="nav-kbd">⌘K</kbd>
  </div>
  <div class="scroll-progress"></div>
</nav>
<button class="to-top" aria-label="Back to top">↑</button>
```

**CSS:**

```css
.nav-bar { position: sticky; top: 0; z-index: 50; backdrop-filter: blur(14px) saturate(1.1);
  background: rgba(8,10,12,0.65); border-bottom: 1px solid rgba(255,255,255,0.08); }
.nav-inner { max-width: 1280px; margin: 0 auto; padding: 14px 32px;
  display: flex; align-items: center; gap: 24px; }
.brand { font-family: "Fraunces", serif; font-style: italic; font-size: 18px; color: var(--ink); text-decoration: none; }
.brand-meta { margin-left: 10px; font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: 0.08em; color: var(--ink-faint); text-transform: uppercase; }
.nav-links { list-style: none; display: flex; gap: 4px; margin: 0 auto; padding: 0; }
.nav-link { padding: 6px 14px; border-radius: 999px; font-size: 13px; color: var(--ink-soft);
  text-decoration: none; transition: background 0.2s, color 0.2s; }
.nav-link:hover, .nav-link.active { background: rgba(255,255,255,0.08); color: var(--ink); }
.nav-link.active::before { content: "● "; color: var(--gold); }
.nav-kbd { font-family: "JetBrains Mono", monospace; font-size: 11px; padding: 3px 8px;
  border: 1px solid rgba(255,255,255,0.15); border-radius: 5px; color: var(--ink-faint); }
.scroll-progress { position: absolute; left: 0; bottom: -1px; height: 2px;
  width: var(--progress, 0%); background: var(--gold); transition: width 0.05s linear; }
.to-top { position: fixed; right: 24px; bottom: 24px; width: 44px; height: 44px;
  border-radius: 50%; border: 1px solid var(--gold); background: rgba(8,10,12,0.85);
  color: var(--gold); font-size: 18px; cursor: pointer; opacity: 0;
  transform: translateY(8px); transition: all 0.25s; z-index: 60; }
.to-top.show { opacity: 1; transform: translateY(0); }
```

**JS (scrollspy + back-to-top + progress):**

```js
(function () {
  const links = document.querySelectorAll('.nav-link');
  const sections = Array.from(links).map(l => document.querySelector(l.getAttribute('href'))).filter(Boolean);
  const bar = document.querySelector('.scroll-progress');
  const top = document.querySelector('.to-top');
  function onScroll() {
    const y = window.scrollY;
    const max = document.body.scrollHeight - window.innerHeight;
    if (bar) bar.style.setProperty('--progress', (y / max * 100).toFixed(2) + '%');
    if (top) top.classList.toggle('show', y > 600);
    let i = 0;
    sections.forEach((s, idx) => { if (s.getBoundingClientRect().top < 120) i = idx; });
    links.forEach((l, idx) => l.classList.toggle('active', idx === i));
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  if (top) top.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
  onScroll();
})();
```

**Tier-A label conventions** (the kbd chip must carry shell-flavored personality — never "Menu"):

| Shell | Brand label | kbd chip |
|---|---|---|
| Studio Black | `L01/07` | `⌘K` |
| Stadium | `L01/07` | `GAME 01` |
| Neon Arcade | `EP 01/07` | `NOW PLAYING` |
| Holographic Future | `v1.0` | `⌘K` |
| Reportage | `Section A 01` | `Vol I` |

---

## Tier B — Editorial

**HTML:**

```html
<header class="masthead-nav">
  <div class="nav-inner">
    <span class="ed-mark">M·M·M  ·  Vol I  ·  No 001</span>
    <nav class="ed-toc">
      <a href="#hero">§ Cover</a>
      <a href="#curriculum">§ Curriculum</a>
      <a href="#equation">§ The Lesson</a>
      <a href="#takeaways">§ Takeaways</a>
    </nav>
    <span class="ed-folio">Folio · 2026</span>
  </div>
  <div class="ed-progress"></div>
</header>
```

**CSS:**

```css
.masthead-nav { position: sticky; top: 0; z-index: 50;
  background: var(--paper); border-bottom: 1px solid var(--rule);
  font-family: "JetBrains Mono", monospace; font-size: 11px;
  letter-spacing: 0.12em; text-transform: uppercase; }
.ed-toc { display: flex; gap: 0; }
.ed-toc a { padding: 14px 18px; color: var(--ink-soft); text-decoration: none;
  border-right: 1px solid var(--rule); transition: color 0.2s, background 0.2s; }
.ed-toc a:first-child { border-left: 1px solid var(--rule); }
.ed-toc a:hover, .ed-toc a.active { color: var(--ink); background: rgba(0,0,0,0.03); }
.ed-toc a.active::before { content: "▣ "; color: var(--accent); }
.ed-progress { height: 1px; background: var(--accent);
  width: var(--progress, 0%); transition: width 0.05s linear; }
```

JS is the same scrollspy as Tier A (just bind `.ed-toc a` instead of `.nav-link`).

---

## Tier C — Whisper-quiet

**HTML:**

```html
<aside class="dot-rail" aria-hidden="true">
  <a href="#hero" class="dot" data-label="Cover"></a>
  <a href="#curriculum" class="dot" data-label="Curriculum"></a>
  <a href="#equation" class="dot" data-label="Lesson"></a>
  <a href="#takeaways" class="dot" data-label="Takeaways"></a>
</aside>
<div class="hairline-progress"></div>
```

**CSS:**

```css
.dot-rail { position: fixed; right: 22px; top: 50%; transform: translateY(-50%);
  display: flex; flex-direction: column; gap: 14px; z-index: 40;
  opacity: 0; transition: opacity 0.4s ease; }
.dot-rail.show { opacity: 1; }
.dot { width: 5px; height: 5px; border-radius: 50%; background: var(--ink-faint);
  position: relative; transition: background 0.2s, transform 0.2s; }
.dot:hover, .dot.active { background: var(--accent); transform: scale(1.6); }
.dot::after { content: attr(data-label); position: absolute; right: 16px; top: 50%;
  transform: translateY(-50%); font-family: "JetBrains Mono", monospace;
  font-size: 10px; letter-spacing: 0.1em; color: var(--ink-soft);
  opacity: 0; pointer-events: none; transition: opacity 0.15s; white-space: nowrap; }
.dot:hover::after { opacity: 1; }
.hairline-progress { position: fixed; left: 0; top: 0; height: 1px;
  width: var(--progress, 0%); background: var(--accent); z-index: 41;
  opacity: 0; transition: opacity 0.4s; }
.hairline-progress.show { opacity: 0.5; }
```

**JS** — same scrollspy + a `show` toggle after `scrollY > 200`.

---

## Defensive overflow pattern (mandatory in every shell, B12 fix)

```css
html { overflow-x: clip; }
body { overflow-x: clip; width: 100%; max-width: 100vw; }
.nav-bar, .masthead-nav { width: 100%; box-sizing: border-box; }
.nav-inner { max-width: 1280px; margin: 0 auto; }
```

Without this, Chrome and Safari render different widths because of font-metric drift, and content shifts left in Chrome only.

## Glass tint follows base luminance (B15 fix)

- **Light-base shell** → `rgba(255,255,255, 0.55–0.92)` for `.nav-bar` background
- **Dark-base shell** → `rgba(8–20, 8–20, 8–20, 0.65–0.88)`

Inspect the shell at rest before picking glass tint — don't infer from category alone.
