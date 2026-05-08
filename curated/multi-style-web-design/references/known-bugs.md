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

## B11 · "Use it anyway" with the wrong skill

**Symptom:** user asks for X, agent honestly says "this skill is wrong for X, here's a better path", user insists.

**Fix:** when user overrides, comply *and* push the skill harder than usual to compensate. Pick a shell + hero combo that bends toward the user's actual goal even if the skill is technically out of its lane (e.g. a *lesson microsite* via `brutalist-index` shell with `none` hero — no need to invent a brand).

---

## B12 · Forgetting to verify in real Chrome

**Symptom:** ship without screenshot verification. User finds the broken layout themselves.

**Fix:** Phase 7 is mandatory. No "I'll skip it this time".

---

## B13 · Building without a 4-line direction brief

**Symptom:** output drifts toward AI-slop because direction was never declared.

**Fix:** always write the 4-line brief in the reply BEFORE writing code:

```
Subject:    text-only
Reference:  Bloomberg Businessweek + Pentagram
Shell:      Brutalist Index
Hero:       E · Volumetric Slices (typographic)
Palette:    ink / paper / gold-leaf / oxblood / slate — finance domain vocabulary
```
