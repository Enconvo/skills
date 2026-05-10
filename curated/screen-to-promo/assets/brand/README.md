# Enconvo Brand Assets

Drop-in brand material for hook / CTA / outro cards when an Enconvo-branded video is being produced.

## Files

- `enconvo_icon_white.png` — Enconvo "leaf-fold" mark, pure white on transparent background, square aspect, ~2000×2000. Use on dark backgrounds (the default Apple Keynote-style #0a0a0a black).

## Usage

### HyperFrames hook / CTA card

```html
<img src="../assets/brand/enconvo_icon_white.png"
     alt="Enconvo"
     style="width: 96px; height: 96px; object-fit: contain;
            filter: drop-shadow(0 0 24px rgba(255,255,255,0.15));" />
```

Recommended sizes:
- Hook (top-left or centered above title): 64–96 px
- CTA hero: 120–160 px (paired with `ENCONVO` wordmark below at letter-spacing 0.3em)
- Outro corner watermark: 48 px at 60% opacity

### compose.py outro overlay

If overlaying the icon on a screen recording outro frame, scale to ~10–12% of frame width (≈ 220 px on a 1920 wide frame) and place top-right with 80 px margin. Apply same multi-layer drop shadow as captions for legibility.

## Aesthetic Rules (from SKILL.md Design Language)

- Background must be #0a0a0a or near-black — the icon is white and disappears on light backgrounds.
- NO color tinting. Keep the icon pure white.
- Subtle white glow (`drop-shadow(0 0 24px rgba(255,255,255,0.15))`) is approved; anything more reads neon and breaks the Keynote register.
- Pair with `ENCONVO` in SF Pro Display, weight 500, uppercase, letter-spacing 0.3em, white at 60% — never a colored wordmark.

## When to use

- Hook cards for any video where the user asks for an Enconvo-branded promo.
- CTA / outro cards on Enconvo product demos, channel agent videos, skill showcases, etc.
- DO NOT use on third-party product videos unless Enconvo is explicitly the producer/sponsor and the user asks for it.
