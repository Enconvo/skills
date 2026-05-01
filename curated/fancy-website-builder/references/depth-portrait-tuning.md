# Depth Portrait Tuning (Variant A)

Knobs for the Apple-style depth-displacement hero. Defaults are battle-tested on the Cleo project (the user's portrait, photographed at f/1.4 on a Singapore rooftop).

## `uStrength` — vertex Z-displacement

How far the foreground pushes toward the camera in plane units.

- `0.0` — flat plane, no 3D feel.
- `0.20` — subtle, conservative, B2B-safe.
- **`0.36` (default)** — clearly 3D, doesn't deform features.
- `0.55` — exaggerated; nose/jaw start looking sculpted, not photographed.
- `0.80+` — face turns into a relief sculpture; usually too much for a brand site.

Reduce to `0.22` for product subjects (products have less depth variation than faces; high uStrength makes the silhouette warp).

## `uParallax` — fragment-shader UV shift

How much the cursor pushes the per-pixel sample. Combined with depth, closer pixels move faster.

- `0.08` — barely there.
- **`0.16` (default)** — face/glass clearly slide vs. background; eyes follow the cursor.
- `0.28` — strong; can show the texture sampling clamp at edges.
- `0.40+` — visible UV stretching, especially near the figure boundary.

## `PlaneGeometry` segmentation

Vertex grid resolution. Higher = smoother displacement, more GPU.

- `(64, 86)` — okay on iPhone 8-class iGPU; visible faceting on faces.
- **`(220, 290)` (default)** — ~64k verts; smooth on Apple Silicon, fine on integrated graphics.
- `(360, 480)` — overkill; keep for reference shots / high-DPI demos.

## `uVignette`

How dark the corners go vs. center.

- `0.95` — almost off; minimal vignette.
- **`0.85` (default)** — clear corner darkening, focuses attention on the face.
- `0.65` — heavy vignette; pushes the look toward "Hollywood portrait."

## Camera dolly amplitude

In the loop:
```js
cam.position.x = mouse.x * 0.05;
cam.position.y = -mouse.y * 0.04 + Math.sin(t*0.4)*0.005;
```

- `0.05 / 0.04` — subtle, pleasant; default.
- `0.10 / 0.08` — more obvious head-tracking; can feel "wobbly."
- `0.0` — disable; only use if `prefers-reduced-motion` or the user reports motion sickness.

The `Math.sin(t*0.4)*0.005` adds a 0.5px autonomous breathe so the portrait lives even when idle. Disable if reduced-motion is set (already handled in the default block).

## Mouse easing

```js
mouse.x += (mouse.tx - mouse.x) * 0.06;
```

- `0.04` — slow, syrup-like; can feel laggy.
- **`0.06` (default)** — natural inertia.
- `0.10` — snappy; loses the "expensive optics" feel.
- `1.0` — no easing; feels brittle.

## Common failure modes

1. **Visible UV clamp at edges**: increase `mesh.scale.setScalar(scale * 1.02)` to `1.05`. The 5% overscan hides the parallax stretching at the figure border.
2. **Face looks "rubbery"**: reduce `uStrength` from 0.36 → 0.22.
3. **Background dominates / face doesn't pop**: increase `uVignette` darkening (lower the value: 0.85 → 0.65) and increase `uStrength` slightly.
4. **Performance drops on integrated graphics**: lower segmentation to `(140, 184)` and `setPixelRatio(1)` instead of `Math.min(2, ...)`.
5. **Eyes look "dead"**: this is a depth-map problem, not a shader problem. The Depth Anything output may have flattened the eye sockets. Re-run depth estimation with the larger Depth-Anything-V2-Base or Large model for higher fidelity around delicate features.

## When to switch to a different variant

- If the depth map lacks fidelity around the face (fuzzy boundaries, eyes flat) → try B (Tilt & Sheen) — doesn't need a depth map.
- If the user is on a B2B site and wants something more restrained → E (Volumetric Slices) — same idea, less expensive feel.
- If the photo is of a product, not a face → A still works, but tune `uStrength` down to 0.22.
