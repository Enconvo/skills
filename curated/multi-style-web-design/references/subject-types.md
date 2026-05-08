# Subject Types

Subject type drives Phase 2 asset prep and which hero techniques are appropriate.

## `human`
A photo of a person, face visible. Portrait, mid-shot, or full body.

- **Asset prep**: downscale to 900px wide → `hero.jpg`; depth map via Depth Anything V2 → `hero_depth.jpg`.
- **Good heroes**: A (depth displacement), B (tilt + sheen), E (volumetric slices).
- **Avoid**: C (particle sample dehumanises faces — eyes void out). Use D (glass refraction) only with caution; heavy distortion turns a face into noise.

## `product`
A single object, usually centered, on a neutral or contextual background (bottle of perfume, sneaker, gadget).

- **Asset prep**: downscale → `hero.jpg`; depth map → `hero_depth.jpg`; alpha matte via rembg → `hero_alpha.png` (so glass/particle effects don't bleed into the background).
- **Good heroes**: A, B, D, E, F.
- **Avoid**: C if the product needs to read clearly (it'll fragment the silhouette).

## `brand-mark`
A logo or wordmark. Usually flat vector or PNG with transparency.

- **Asset prep**: keep PNG with transparency; if SVG provided, store as-is. **Skip depth map** — flat artwork has no depth.
- **Good heroes**: B (tilt + sheen — gives the mark a "glossy print" feel), E (volumetric slices, stacked).
- **Avoid**: A (no depth map), D (refraction blurs vector edges into mush), C (logo silhouette gets shredded).

## `abstract`
A texture, gradient, mood photograph, or generative image with no clear subject.

- **Asset prep**: downscale only. Depth maps optional; usually skipped.
- **Good heroes**: All 6 work — abstracts are the most permissive subject type.
- **Best fits**: C (particle sample shines here), F (caustics), D (glass refraction).

## `scene`
A wide shot — interior, landscape, cityscape — where multiple objects share the frame.

- **Asset prep**: downscale → `hero.jpg`; depth map → `hero_depth.jpg`.
- **Good heroes**: A (parallax across foreground/middle/background reads beautifully), E (volumetric slices on a scene = best mobile read), D (mood-driven scenes love the glass treatment).
- **Avoid**: B (tilt-and-sheen on a wide scene flattens the depth cue you came for).

---

## Rule of thumb

If the user's request is "hero is the *thing*, look at the *thing*" → favor A or B.
If the user's request is "hero sets a *mood*, the thing is secondary" → favor D, F, or E.
If the user's request is "I want it weird / artistic / unforgettable" → C, but **never on a face**.
