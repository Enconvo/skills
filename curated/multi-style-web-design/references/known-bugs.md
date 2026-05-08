# Known bugs & lessons learned

Real failures from real builds. Read before building. Update when new ones surface.

---

## B1 · Decorative slabs leaking into content

**Symptom:** A 1px black/gold horizontal "depth marker" inside the hero appears as a strikethrough across the lede paragraph below.

**Cause:** `position: absolute` slab inside `.title-stack` (or hero), positioned with negative offsets like `bottom: -12%`, with parent `overflow: visible`. The slab leaks past its container.

**Fix:**
- Don't add decorative slabs unless they pay rent on real content.
- If you must, the parent must `overflow: hidden`, OR the slab must use `top: 0` / `bottom: 0` with no negative offsets.
- Better: layered headlines + drop shadows + blurs alone deliver depth — skip the slabs.

```css
/* ❌ BAD — slab leaks down */
.title-stack { overflow: visible; }
.slab-3 { position: absolute; bottom: -12%; height: 1px; background: black; }

/* ✅ GOOD — slab is contained */
.title-stack { overflow: hidden; padding-bottom: 12%; }
.slab-3 { position: absolute; bottom: 0; height: 1px; background: black; }
```

---

## B2 · Empty mono labels look like UI debris

**Symptom:** floating `LAYER · 01` / `DEPTH · ∞` mono labels confuse the user — "what's that, empty meaningless space?"

**Cause:** Importing decorative scaffolding from a hero-shader demo without earning it on the real page. These labels were chrome for a depth demo, not content for the user's site.

**Fix:** every visible label must carry meaning *for this site's content*. Examples of *earned* labels:
- `MODULE · 03` next to a real module
- `READING TIME · 45 MIN` next to a real article
- `VOL. I · 2026` masthead

If a label is filler, delete it. Period.

---

## B3 · Cache-stale screenshot

**Symptom:** user reloads, sees old version, says "no change".

**Cause:** Chrome disk cache.

**Fix:** ALWAYS append `?v=<timestamp>` when re-verifying:

```bash
open -a "Google Chrome" "http://127.0.0.1:7531/?v=$(date +%s)"
```

Tell the user to hard-refresh (Cmd+Shift+R) if they refresh manually.

---

## B4 · Local server refused after kill

**Symptom:** `127.0.0.1:7531 refused to connect` after `pkill`.

**Fix:**
- Either keep the server alive across iterations
- OR tell the user to open the file via `file:///` URL — the static site needs no server.

```
file:///Users/.../project/index.html
```

---

## B5 · Tilt is invisible in static screenshots

**Symptom:** "I see no 3D." A pointer-driven tilt shows the rest state in any screenshot.

**Fix:** Hero must show depth at rest. Static z-translated layers + drop shadows + subtle blurs first. Pointer interaction *enhances*, not *creates*, depth.

If a technique only "works" in motion, wrong technique for a screenshot-driven web.

---

## B6 · Tilt-only on type with no photo = "3D-adjacent, not 3D"

**Symptom:** user expects visible 3D, sees only a faint sheen on type.

**Fix:** for typographic heroes use **Volumetric Slices (E)**:
- back layer: large, blurred, low-opacity ink ghost
- middle layer: gold ghost, mid-blur, offset
- front layer: sharp ink with drop shadow

Three layers + parallax > pointer tilt alone.

---

## B7 · `mix-blend-mode: multiply` on translucent gold

**Symptom:** middle gold ghost goes brown/muddy on cream paper.

**Fix:** use `multiply` only on layers ≥ 50% opacity. For lighter ghosts, use plain `rgba()` + a saturated base color, no blend mode.

---

## B8 · Drop shadows clipped by `overflow: hidden`

**Symptom:** front-layer drop shadow cut off at the hero edge.

**Fix:** if `.hero` needs `overflow: hidden` (to clip back-slice drift), give `.title-stack` itself `overflow: visible` AND add bottom padding to `.hero` to hold the shadow.

---

## B9 · Demo/debug labels shipped to production

**Symptom:** user asks "what is `DEPTH · ∞` doing here?"

**Fix:** strip every label that's hard-coded scaffolding from the shader demo before shipping. Audit step before final delivery: search for `LAYER`, `DEPTH`, `DEMO`, `TODO` in the rendered DOM.

---

## B10 · Skill loaded twice on the same task

**Symptom:** `<inline_skill>` already includes SKILL.md content, but the agent calls `Skill` tool again.

**Fix:** if `<inline_skill>` is already in the conversation, follow it directly without reloading.

---

## P1 · "Use it anyway" with the wrong skill (process bug)

**Symptom:** user asks for X, agent honestly says "this skill is wrong for X, here's a better path", user insists.

**Fix:** when user overrides, comply *and* push the skill harder than usual to compensate. Pick a shell + hero combo that bends toward the user's actual goal even if the skill is technically out of its lane (e.g. a *lesson microsite* via `brutalist-index` shell with `none` hero — no need to invent a brand).

---

## P2 · Forgetting to verify in real Chrome (process bug)

**Symptom:** ship without screenshot verification. User finds the broken layout themselves.

**Fix:** Phase 7 is mandatory. No "I'll skip it this time". For Vercel-deployed sites, also use puppeteer with a `requestfailed` listener — only a real browser exposes B22-class relative-path bugs.

---

## P3 · Building without a 4-line direction brief (process bug)

**Symptom:** output drifts toward AI-slop because direction was never declared.

**Fix:** always write the 4-line brief in the reply BEFORE writing code:

```
Subject:    text-only
Reference:  Bloomberg Businessweek + Pentagram
Shell:      Brutalist Index
Hero:       E · Volumetric Slices (typographic)
Palette:    ink / paper / gold-leaf / oxblood / slate — finance domain vocabulary
```

---

## B11 · Waterfall single-flow page with no navigation

**Symptom:** user says "all pages are like waterfall, on page, kinda lack of navigation bar to make the page more structure".

**Cause:** historic builds shipped one long scroll page with no anchors, no TOC, no scroll progress. Fine for a 1-section landing page; regression-tier for any content with 3+ sections.

**Fix:** Phase 4.5 is now mandatory — every variant gets section IDs, smooth-scroll, scrollspy, and tier-appropriate nav. See `navigation-tiers.md`.

---

## B12 · Chrome content offset left, Safari perfectly centered — phantom horizontal overflow

**Symptom:** in Chrome the page sits visibly left-of-center on a wide monitor. Safari renders it correctly centered.

**Cause:** sticky `<nav>` with `flex-wrap: wrap` and a long brand string + 4 nav links + meta block computes a slightly different total width in Chrome's font metrics vs Safari's. Chrome renders the nav slightly past viewport edge, which makes `body.scrollWidth > body.clientWidth` — then every `margin: 0 auto` content section centers against the wider scroll-width and visually shifts.

**Fix:** **defensive overflow pattern** in every shell:

```css
html { overflow-x: clip; }
body { overflow-x: clip; width: 100%; max-width: 100vw; }
.nav-bar, .masthead-nav { width: 100%; box-sizing: border-box; }
.nav-inner { max-width: 1280px; margin: 0 auto; }
```

---

## B13 · `overflow-x: clip` silently chops content

**Symptom:** v6 Riso headline "MECHANICS!" was overflowing the viewport — `overflow-x: clip` hid the overflow so the page *looked* contained, but content was being chopped off the right edge.

**Cause:** defensive `overflow-x: clip` (added to fix B12) silently clips overflowing content. If a `clamp(min, vw, max)` headline is sized aggressively (e.g. `clamp(64px, 12vw, 180px)`), at 1440px viewport `12vw = 172.8px`, very close to the cap — with letter-spacing and per-character drift, the rendered word can exceed the viewport.

**Fix:** before shipping, audit every title's `clamp()` upper bound. **Rule of thumb:** at 1440px viewport, the rendered headline width must be ≤ 1280px (the content frame). Test specifically at 1440×900 and 1920×1080. **Don't trust `overflow: clip` to hide the bug.**

---

## B14 · Layered text-shadow `::before` desyncs from wrapping text

**Symptom:** v6 Riso pink underprint shadow showed orphan "MEME" fragments next to the actual word "MECHANICS". Pink shadow at one position, black text at another.

**Cause:** structure was `<span class="row3 pink-shadow" data-text="Mechanics!">Mechanics!</span>` with `::before { content: attr(data-text); position: absolute; left: -6px; }`. Two compounding bugs:
1. Staircase indent used `padding-left: 160px` on the parent span, but `position: absolute` children resolve `left: -6px` relative to the span's **padding box** — so the pink `::before` started at row-left while the black text started at row-left + 160px.
2. When the span was treated as inline (default for `<span>`), the `::before` only aligned with the first inline line-box, so any wrapping fragmented the shadow.

**Fix:** for any layered-shadow design (Riso, Memphis, neo-brutalist offset shadow):

```css
.shadow-row {
  display: inline-block;          /* gives ::before a proper bounding box */
  white-space: nowrap;            /* prevent internal wrapping */
  margin-left: 160px;             /* not padding-left for staircase indents */
}
.shadow-row::before {
  content: attr(data-text);
  position: absolute;
  left: -6px; top: 6px;
  color: var(--pink);
  z-index: -1;
}
```

---

## B15 · Light-shell got dark-glass nav (or vice versa)

**Symptom:** v15 Holographic Future has a near-white pastel hero, but the auto-injected Tier-A nav rendered with `rgba(8,10,20,0.65)` (dark navy translucent) — visually clashed.

**Cause:** shell tokens for `bg_glass` were assumed dark for all dark-bg shells, but v15's hero is actually **light** despite living in the "futuristic" category.

**Fix:** the `bg_glass` token must be derived from the shell's actual base luminance, not its category. Light-base shells get `rgba(255,255,255, 0.55–0.92)`; dark-base shells get `rgba(8–20, 8–20, 8–20, 0.65–0.88)`. Inspect the rendered shell at rest before picking glass.

---

## B16 · Markup parity bug — one row in a stanza forgot a class

**Symptom:** v6 Riso Pop's row 2 ("MARKETS &") had no pink underprint while rows 1 and 3 did — user spotted it.

**Cause:** simple typo. Row 1 had `class="row1 pink-shadow" data-text="Money,"`, row 3 had `class="row3 pink-shadow" data-text="Mechanics!"`, but row 2 had only `class="row2 blue"` — missing both `pink-shadow` and `data-text`.

**Fix:** for any design where a single visual treatment applies uniformly across a stanza of structural siblings, **verify class parity by grep before shipping**:

```bash
# Should equal the number of stanza rows
grep -c 'pink-shadow' index.html
```

---

## B17 · Section name variance breaks scrollspy

**Symptom:** v16 Reportage uses `<section class="pullquote">` instead of `<section class="equation">`, so the auto-injection script that adds `id="equation"` failed silently for that shell.

**Cause:** shell authors took creative liberty with section class names without updating the canonical alias map.

**Fix:** every shell's four canonical sections must end up with these IDs: `#hero`, `#curriculum` (or `#articles` aliased), `#equation` (or `#pullquote` aliased), `#takeaways`. The init script must accept aliases. Document any shell-specific aliases in that shell's `README.md`.

---

## B18 · "Card-with-image" syndrome on multi-image pages (rectangle syndrome)

**Symptom:** user says "pics of scenes are all rectangles, seem not designer's taste, simple html coding". Every figure on the page ends up as the same 3:2 or 2:3 box with the same border treatment and the same caption position. Reads as CMS template within seconds.

**Cause:** copying a single `<figure>` template across all images and just changing the `src`. Same aspect ratio + same border + same caption = visual tedium.

**Fix:** when a page carries ≥3 content photographs, follow `spread-typology.md` (§6.5) and use **at least 3 different spread types**. Repeating the same spread layout across 3+ modules in a row is a redesign trigger.

---

## B19 · Default `border: 1px solid` rings on content figures

**Symptom:** "rectangles, not designer's taste". Hairline borders around every photo are the universal CMS-template tell.

**Cause:** defaulting to `border: 1px solid var(--rule-strong)` on `<figure>` because it's the safe option.

**Fix:** **never wrap a content photograph in a 1px border by default.** The photo's edge IS the edge. Use tonal gradient falloff at bleeding edges instead:

```css
figure::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(to top, rgba(10,9,8,0.45), transparent 55%);
}
```

Borders only when the frame *evokes a specific medium* (polaroid, contact sheet, gallery mat) and earns its place — not as a default safety move.

---

## B20 · Captions all in the same lower-left gradient bar

**Symptom:** identical caption position + treatment across 6 images = the page reads as a slideshow.

**Cause:** reusing a single `figcaption` styled with `position: absolute; left: 14px; bottom: 12px;` + bottom gradient overlay across every figure.

**Fix:** caption position MUST vary by spread type. See `spread-typology.md` — each spread has a different caption convention (top-left mono stamp / italic Fraunces below the figure with gold left rule / vertical rotated mono in the gutter / mix-blend-mode against the photo / displaced open-quote glyph). Pick one PER spread, not one for all of them.

---

## B21 · Hosted-variant misclassification (text-only → founder-with-photo)

**Symptom:** original lesson built on Brutalist Index (correct for text-only finance). Then a host (Vivieen) is added with 6 portraits — but the page is still treated as text-only and the photos get bolted onto the same scaffold as rectangles.

**Cause:** the auto-pick table treats subject type as fixed at start of session. Adding a named human host with ≥3 photographs *changes the subject type* mid-task.

**Fix:** if a page acquires a named human host carrying ≥3 photographs, **switch shell** to Editorial Nightscape (or any Tier-B editorial shell), follow `spread-typology.md`, and apply the `editorial-details.md` checklist. The text-only Brutalist Index pick only applies when the type is the only protagonist.

---

## B22 · Relative image paths break under Vercel `cleanUrls` at non-trailing-slash URLs

**Symptom:** site works perfectly on `python3 -m http.server`, ships to Vercel, then ALL images fail to load — only `alt` text shows. Direct `curl` to `/path/images/foo.jpg` returns 200, but the browser silently 404s.

**Cause:** `vercel.json` has `"cleanUrls": true`. When the user visits `https://site.com/v17-page` (no trailing slash, no `.html`), Vercel internally rewrites that to `/v17-page/index.html` and serves it — but the URL bar stays `/v17-page`. The browser treats `/v17-page` as a *file*, not a directory. So when the HTML contains `<img src="images/foo.jpg">`, the browser resolves it relative to the parent of `/v17-page` → `/images/foo.jpg`, which 404s.

**Fix:** in any subfolder variant deployed under Vercel `cleanUrls`, use **absolute paths** rooted at the variant folder:

```bash
# Before deploying:
sed -i '' 's|src="images/|src="/<variant-folder>/images/|g' index.html
```

```html
<!-- ❌ Breaks under cleanUrls -->
<img src="images/scene-1.jpg" alt="...">

<!-- ✅ Works -->
<img src="/v17-page/images/scene-1.jpg" alt="...">
```

Alternative: turn off `cleanUrls` for subfolder pages, OR add a redirect rule that always appends a trailing slash. Absolute-path rewrite is the most portable fix.

**Watch for:** the bug is **invisible to `curl`** if you happen to type the right path manually — only a real browser (or `puppeteer.requestfailed` listener) will reveal the 404 because only the browser does relative-path resolution.

```js
// Recommended post-deploy verification snippet:
page.on('requestfailed', r => failures.push({ url: r.url(), reason: r.failure().errorText }));
page.on('response', r => { if (r.status() >= 400) failures.push({ url: r.url(), status: r.status() }); });
```
