#!/usr/bin/env python3
"""
Premium macOS-style keycap renderer (screen-to-promo).

Produces commercial-grade key caps for the CTA outro keypress animation --
the Enconvo hero chord is Cmd-Shift-D. Renders each cap at 4x supersampling
then Lanczos-downscales for glass-smooth edges. That supersample step is the
single biggest jump from "flat gray box with a hard aliased outline" to "looks
like a real Mac key" -- a 1x rounded_rectangle with a thin outline aliases into
a cheap, jagged edge that a paying viewer WILL call out.

Each cap has:
  - a soft drop shadow (grounds the key on the dark canvas, doesn't float)
  - a top-lit vertical gradient body (lighter top, darker base) masked to a
    rounded rect  -> real depth, not a flat fill
  - a feathered gloss highlight in the upper face, clipped to the body
  - a faint inner rim light + a soft outer border
  - a crisp glyph with a subtle drop shadow for legibility

`illuminate()` brightens a cap for the "action fires" flash -- it adds white
*through the cap's own alpha* (<= ~40%), so the key GLOWS instead of washing
out to a flat white rectangle.

Geometry: returns a CANVAS x CANVAS RGBA image whose visible key is KEYVIS px,
centered, with PAD px of padding on every side for the shadow/glow. Composite
the whole canvas centered on the key's target center so shadow + key scale
together when you resize for the entrance pop.

Proven on the Enconvo Dynamic Island promo (2026-07-14). Reuse verbatim; only
retune KEYVIS / colors if the brand calls for it. This is the reference for the
"Premium keycap rendering" spec in SKILL.md -> Keypress Animation & SFX.

Deps: pillow, numpy. Fonts: Apple Symbols (Cmd/Shift glyphs), Arial Bold (letters).
Usage: python3 scripts/keycap.py [outdir]   # writes keycap_*.png + a preview row
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

SYM = "/System/Library/Fonts/Apple Symbols.ttf"
ARIAL_B = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

KEYVIS = 132            # visible keycap size (px, at 1x)
PAD = 36                # padding around the key for shadow + glow
CANVAS = KEYVIS + 2 * PAD

# top-lit charcoal -- matches Apple dark-mode keys sitting on #0a0a0a
BODY_TOP = (74, 75, 82)
BODY_BOT = (28, 28, 33)
GLYPH_COLOR = (242, 244, 249, 255)


def _vgrad(w, h, top, bot):
    """Vertical RGBA gradient, fully opaque, via numpy (fast)."""
    f = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    arr = np.zeros((h, w, 4), np.float32)
    for c in range(3):
        arr[:, :, c] = top[c] + (bot[c] - top[c]) * f
    arr[:, :, 3] = 255
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def keycap(glyph, font_path, fsize, ss=4):
    """Render one premium keycap. Returns CANVAS x CANVAS RGBA (key centered + shadow)."""
    C = CANVAS * ss
    kv = KEYVIS * ss
    off = PAD * ss
    rad = int(30 * ss)
    img = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    # soft drop shadow (grounds the key)
    sh = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle(
        [off, off + int(9 * ss), off + kv, off + kv + int(9 * ss)], radius=rad, fill=(0, 0, 0, 165))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12 * ss)))
    # rounded body mask (reused for gradient + gloss clip)
    fullmask = Image.new("L", (C, C), 0)
    ImageDraw.Draw(fullmask).rounded_rectangle([off, off, off + kv - 1, off + kv - 1], radius=rad, fill=255)
    # top-lit gradient body
    grad = _vgrad(kv, kv, BODY_TOP, BODY_BOT)
    body = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    body.paste(grad, (off, off))
    body.putalpha(ImageChops.multiply(body.split()[3], fullmask))
    img.alpha_composite(body)
    # feathered gloss highlight in the upper face, clipped to the body
    gl = Image.new("L", (C, C), 0)
    ImageDraw.Draw(gl).ellipse([off + int(kv * 0.08), off - int(kv * 0.34),
                               off + int(kv * 0.92), off + int(kv * 0.50)], fill=46)
    gl = ImageChops.multiply(gl.filter(ImageFilter.GaussianBlur(int(10 * ss))), fullmask)
    glw = Image.new("RGBA", (C, C), (255, 255, 255, 0))
    glw.putalpha(gl)
    img.alpha_composite(glw)
    # borders: soft outer + faint inner rim
    bd = ImageDraw.Draw(img)
    bd.rounded_rectangle([off, off, off + kv - 1, off + kv - 1], radius=rad,
                         outline=(255, 255, 255, 64), width=int(1.6 * ss))
    bd.rounded_rectangle([off + int(4 * ss), off + int(4 * ss),
                          off + kv - 1 - int(4 * ss), off + kv - 1 - int(4 * ss)],
                         radius=int(rad * 0.88), outline=(255, 255, 255, 24), width=int(1.0 * ss))
    # glyph with a subtle drop shadow for depth/legibility
    f = ImageFont.truetype(font_path, int(fsize * ss))
    bb = f.getbbox(glyph)
    gw = bb[2] - bb[0]
    gh = bb[3] - bb[1]
    gx = off + (kv - gw) // 2 - bb[0]
    gy = off + (kv - gh) // 2 - bb[1]
    gly = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gly)
    gd.text((gx, gy + int(2.5 * ss)), glyph, font=f, fill=(0, 0, 0, 130))
    gd.text((gx, gy), glyph, font=f, fill=GLYPH_COLOR)
    img.alpha_composite(gly)
    return img.resize((CANVAS, CANVAS), Image.LANCZOS)


def illuminate(cap, amount):
    """Brighten a cap THROUGH its own alpha (amount 0..1) for the fire flash.
    Glows instead of washing out. Use at the tock/action-fires moment."""
    amount = max(0.0, min(1.0, amount))
    if amount <= 0:
        return cap
    out = cap.copy()
    a = out.split()[3].point(lambda p: int(p * 0.40 * amount))
    wl = Image.new("RGBA", out.size, (255, 255, 255, 0))
    wl.putalpha(a)
    out.alpha_composite(wl)
    return out


def cmd_shift_d(ss=4):
    """The Enconvo hero chord. Returns [Cmd, Shift, D] premium caps.
    Falls back to text labels if Apple Symbols glyphs are unavailable."""
    sym_ok = ImageFont.truetype(SYM, 74).getbbox("\u2318")[2] > 0
    if sym_ok:
        spec = [("\u2318", SYM, 72), ("\u21e7", SYM, 76), ("D", ARIAL_B, 74)]
    else:
        spec = [("cmd", ARIAL_B, 40), ("shift", ARIAL_B, 40), ("D", ARIAL_B, 74)]
    return [keycap(g, p, s, ss) for g, p, s in spec]


if __name__ == "__main__":
    import sys
    outdir = sys.argv[1] if len(sys.argv) > 1 else "."
    caps = cmd_shift_d()
    for name, cap in zip(["cmd", "shift", "d"], caps):
        cap.save(f"{outdir}/keycap_{name}.png")
    # held row (top) + fire/illuminated row (bottom) on #0a0a0a for eyeballing
    prev = Image.new("RGBA", (CANVAS * 3 + 60, CANVAS * 2 + 40), (10, 10, 10, 255))
    for j, cap in enumerate(caps):
        prev.alpha_composite(cap, (30 + j * (CANVAS + 30), 10))
        prev.alpha_composite(illuminate(cap, 1.0), (30 + j * (CANVAS + 30), CANVAS + 30))
    prev.convert("RGB").save(f"{outdir}/keycap_preview.png")
    print(f"wrote keycap_cmd/shift/d.png + keycap_preview.png to {outdir}")
