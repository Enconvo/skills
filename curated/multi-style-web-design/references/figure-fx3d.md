# `.fx3d` — Figure-Grid Tilt + Sheen + Lift Effect

Companion to **§4.6** of `SKILL.md`. The shared-physics opt-in figure effect for **multi-image editorial pages**. Distinct from §4 hero shaders — those run once on the hero, `.fx3d` runs on every figure container in the article.

## What it does

- **Static depth at rest** (visible in screenshots, satisfies critical rule 12): multi-layer `box-shadow` (deep ambient + inset highlight + 1px gold rim) makes each figure float off the page background.
- **Pointer-driven tilt** (±5° / ±4°): mousemove updates `--rx` / `--ry` CSS variables; the container `transform: perspective(1400px) rotateX rotateY` follows the cursor with a 0.18s ease.
- **Pointer-driven sheen**: a `radial-gradient` `::after` with `mix-blend-mode: screen` follows the cursor (`--mx` / `--my`), revealing a soft warm highlight.
- **Image parallax** on hover only: the `<img>` translates `Z(40px)` and `scale(1.025)` against its frame. *Never at rest* — this avoids the B-fx3d-clip overflow bug.
- **Reduced-motion respect**: `prefers-reduced-motion: reduce` retains the static box-shadow lift but drops all transform / sheen.

---

## CSS — drop into shell stylesheet, after the figure typography rules

```css
.fx3d {
  --rx: 0deg; --ry: 0deg;
  --mx: 50%; --my: 50%;
  --lift: 0px;
  --fx-radius: 14px;
  border-radius: var(--fx-radius);
  position: relative;
  transform-style: preserve-3d;
  transform: perspective(1400px)
             rotateX(var(--rx)) rotateY(var(--ry))
             translateZ(var(--lift));
  transition: transform 0.45s cubic-bezier(0.2, 0.7, 0.2, 1),
              box-shadow 0.45s cubic-bezier(0.2, 0.7, 0.2, 1);
  will-change: transform;
  box-shadow:
    0 1px 0 rgba(243,237,225,0.06) inset,
    0 -1px 0 rgba(0,0,0,0.4) inset,
    0 18px 40px -12px rgba(0,0,0,0.55),
    0 40px 80px -20px rgba(0,0,0,0.45),
    0 0 0 1px rgba(212,175,91,0.08);
}

.fx3d > img {
  border-radius: inherit;
  transition: transform 0.45s cubic-bezier(0.2, 0.7, 0.2, 1);
}

.fx3d:hover {
  --lift: 6px;
  transition-duration: 0.18s;
  box-shadow:
    0 1px 0 rgba(243,237,225,0.10) inset,
    0 -1px 0 rgba(0,0,0,0.5) inset,
    0 24px 56px -10px rgba(0,0,0,0.65),
    0 56px 110px -16px rgba(0,0,0,0.55),
    0 0 0 1px rgba(212,175,91,0.18);
}
.fx3d:hover > img {
  transition-duration: 0.18s;
  transform: translateZ(40px) scale(1.025);
}

.fx3d::after {
  content: "";
  position: absolute; inset: 0; pointer-events: none;
  z-index: 4;
  border-radius: inherit;
  background: radial-gradient(circle at var(--mx) var(--my),
              rgba(232,201,122,0.18), transparent 40%);
  opacity: 0;
  transition: opacity 0.35s ease;
  mix-blend-mode: screen;
}
.fx3d:hover::after { opacity: 1; }

.fx3d.fx3d-round { --fx-radius: 50%; border-radius: 50%; }
.fx3d.fx3d-round::after { border-radius: 50%; }

@media (prefers-reduced-motion: reduce) {
  .fx3d, .fx3d > img { transition: none; transform: none; }
  .fx3d:hover, .fx3d:hover > img { transform: none; }
  .fx3d::after, .fx3d:hover::after { opacity: 0; }
}
```

---

## JS — vanilla, no dependencies, ~30 lines

```js
(function () {
  if (window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  document.querySelectorAll('.fx3d').forEach(function (el) {
    var raf = null, lastE = null;

    function apply() {
      if (!lastE) return;
      var r = el.getBoundingClientRect();
      var x = (lastE.clientX - r.left) / r.width;   // 0..1
      var y = (lastE.clientY - r.top)  / r.height;  // 0..1
      el.style.setProperty('--rx', ((0.5 - y) * 8).toFixed(2) + 'deg');
      el.style.setProperty('--ry', ((x - 0.5) * 10).toFixed(2) + 'deg');
      el.style.setProperty('--mx', (x * 100).toFixed(1) + '%');
      el.style.setProperty('--my', (y * 100).toFixed(1) + '%');
      raf = null;
    }

    el.addEventListener('mousemove', function (e) {
      lastE = e;
      if (!raf) raf = requestAnimationFrame(apply);
    });

    el.addEventListener('mouseleave', function () {
      el.style.setProperty('--rx', '0deg');
      el.style.setProperty('--ry', '0deg');
      el.style.setProperty('--mx', '50%');
      el.style.setProperty('--my', '50%');
      lastE = null;
    });
  });
})();
```

---

## Wiring

Add the `fx3d` class to every figure container that wraps a content photo:

```html
<figure class="hero-figure fx3d">…</figure>
<figure class="figure fx3d">…</figure>
<figure class="cinema fx3d">…</figure>
<figure class="closer-figure fx3d">…</figure>
```

For circular portraits (host band, testimonial avatar) add `fx3d-round`:

```html
<figure class="host-portrait fx3d fx3d-round">
  <img src="/v17-page/images/host-avatar.jpg" alt="…" />
</figure>
```

---

## Per-figure radius tuning

Drop into the shell stylesheet to override the 14px default:

| Figure size / role | `--fx-radius` |
|---|---|
| Hero figure, closer figure, cinematic 21:9 | `16px` |
| Default full-bleed split (Spread A) | `14px` (the `.fx3d` baseline) |
| Tall inset (Spread B), pull-quote inset (Spread D) | `12px` |
| Round portrait (Spread E half-circle) | `50%` (via `.fx3d-round`) |

```css
.hero-figure.fx3d,
.closer-figure.fx3d,
.spread-06 .cinema.fx3d {
  --fx-radius: 16px; border-radius: 16px;
}
.spread-04 .figure.fx3d,
.spread-07 .figure.fx3d {
  --fx-radius: 12px; border-radius: 12px;
}
```

---

## Tuning knobs

| Knob | Default | Range | Effect |
|---|---|---|---|
| Tilt amount on Y | `(x - 0.5) * 10` | `*4` (subtle) → `*16` (showy) | Side-to-side rotation |
| Tilt amount on X | `(0.5 - y) * 8` | `*3` → `*12` | Up/down rotation |
| Lift on hover | `--lift: 6px` | `2px`–`12px` | How far the figure pops |
| Image translateZ | `translateZ(40px)` | `20px`–`60px` | Parallax intensity inside frame |
| Image scale | `scale(1.025)` | `1.01`–`1.05` | Crop-in on hover |
| Sheen color | `rgba(232,201,122,0.18)` | match shell accent | Highlight tint |
| Sheen radius | `40%` falloff | `30%`–`55%` | Highlight spread |
| Rim opacity | `rgba(212,175,91,0.08)` rest, `0.18` hover | `0`–`0.3` | Gold edge presence |
| Shadow ambient | `40px 80px -20px rgba(0,0,0,0.45)` | tune for shell luminance | Resting depth |

---

## Where it earns its place

✅ Use when:

- **Multi-image editorial pages** (§6.5 spread typology) where photographs are protagonist-grade and need to feel lifted off the dark page background.
- **Hosted-edition variants** (B21 fix) — makes the host's portraits feel cinematic rather than CMS rectangles.
- **Personal brand / founder portfolio sites** with 3+ supporting photos.

## Where to NOT use it

❌ Skip on:

- **Single-hero pages** — §4 hero shaders A–F already provide depth there. Don't compound.
- **Light-paper shells** (`glass-library`, `gallery-white`, `soft-organic`) — the dark `box-shadow` reads as muddy on cream paper. Either tune the shadow stack to *much* lighter / smaller offsets, or skip entirely.
- **Comic / Riso / Panel shells** (`riso-pop`, `panel`) — flat-color register actively rejects soft 3D depth; the playful flatness *is* the design.
- **Newspaper / Reportage shells** (`reportage`) — newsprint is meant to look 2D. Lifting figures violates the medium.

## Compatibility with §4 hero shaders

**Orthogonal.** A page can run hero shader B (Tilt & Sheen) on the hero photograph AND run `.fx3d` on every supporting figure below — they share the same physics vocabulary and don't fight each other visually. Just don't apply `.fx3d` to the hero figure if it's already running hero shader A/B/D/F.

---

## Light-shell variant (when you really want it on cream paper)

Tune the shadow stack down ~70%, swap rim color from gold to ink, and reduce sheen opacity:

```css
.shell-light .fx3d {
  box-shadow:
    0 1px 0 rgba(255,255,255,0.4) inset,
    0 -1px 0 rgba(0,0,0,0.06) inset,
    0 8px 18px -6px rgba(20,17,15,0.18),
    0 18px 36px -12px rgba(20,17,15,0.10),
    0 0 0 1px rgba(20,17,15,0.06);
}
.shell-light .fx3d:hover {
  box-shadow:
    0 1px 0 rgba(255,255,255,0.5) inset,
    0 -1px 0 rgba(0,0,0,0.08) inset,
    0 12px 24px -6px rgba(20,17,15,0.22),
    0 24px 48px -10px rgba(20,17,15,0.14),
    0 0 0 1px rgba(20,17,15,0.10);
}
.shell-light .fx3d::after {
  background: radial-gradient(circle at var(--mx) var(--my),
              rgba(255,255,255,0.35), transparent 35%);
  mix-blend-mode: soft-light;
}
```

This is a deliberate downshift — even with this it's risky on cream. Test before shipping.

---

## Known bugs avoided

- **B-fx3d-clip** — initial v1 had `.fx3d > img { transform: translateZ(20px) scale(1.02); }` *at rest*, which combined with `overflow: hidden` on the figure container chopped portraits at their edges. **Fix**: only apply `translateZ` + `scale` on `:hover`, never at rest.
- **B22** — when shipping under Vercel `cleanUrls`, image `src` paths must be absolute (`/v17-page/images/foo.jpg`), not relative (`images/foo.jpg`). See `known-bugs.md`.
