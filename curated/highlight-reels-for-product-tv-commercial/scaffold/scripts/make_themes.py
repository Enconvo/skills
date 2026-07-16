#!/usr/bin/env python3
"""make_themes.py — generate theme skins of the canonical EnConvo VO composition.

The Minimal landscape/vertical templates are the CANONICAL structure (body + GSAP
timeline). A "theme" is a CSS skin only — we append an override <style> block so the
body, timeline, scene timings, and outro/CTA stay byte-identical across themes.

Run from the scaffold root:  python3 scripts/make_themes.py
"""
import re, pathlib

SC = pathlib.Path(__file__).resolve().parent.parent   # scaffold/

# ------------------------------------------------------------------ LINE ART ---
# Cream paper, bold navy ink, one gold accent, hand-drawn (flat-offset) frames.
# Overrides only the properties that change; every size/position inherits from the
# Minimal base, so the layout is provably identical.
LINEART = """/* ===== LINE ART SKIN (overrides Minimal base) =====
   paper #F2EEE1 · navy ink #1E2C62 / #15224E · gold accent #E7B62C
   signature move: flat-offset (blur-0) navy shadows = editorial line-art frames */
html, body { background: #F2EEE1; }
body { color: #1E2C62; }
#stage { background: radial-gradient(130% 100% at 50% 26%, #F8F4E9 0%, #F2EEE1 46%, #EBE6D6 100%); }
#glowsoft { background: radial-gradient(circle at 50% 50%, rgba(231,182,44,0.08), rgba(231,182,44,0) 62%); }
#vignette { background: radial-gradient(125% 105% at 50% 40%, transparent 58%, rgba(20,26,60,0.07) 100%); }
.eyebrow { color: #5A6488; }
.eyebrow::before { background: #E7B62C; }
.title { color: #1E2C62; font-weight: 800; }
.ticks { color: #5A6488; }
.ticks b { color: #1E2C62; }
.chip { color: #7A5B10; background: rgba(231,182,44,0.20); border-color: rgba(231,182,44,0.62); }
.head { color: #49517A; }
.mega { color: #15224E; }
.logomark { filter: drop-shadow(7px 9px 0 rgba(27,42,99,0.14)); }
.wordmark { color: #1E2C62; }
.kicker { color: #6A7099; }
.tagline { color: #38406B; }
.urltiny { color: #5A6488; }
.urltiny .d { background: #E7B62C; }
.keyglow { background: radial-gradient(circle at 50% 50%, rgba(231,182,44,0.36), rgba(231,182,44,0) 68%); }
.smartbar { background: #FBF7EC; border: 2.5px solid #1E2C62; box-shadow: 7px 7px 0 rgba(27,42,99,0.13); }
.smartbar .dot { background: radial-gradient(circle at 35% 30%, #F2D26A, #E7B62C 70%); }
.smartbar .ph { color: #5A6488; }
.smartbar .caret { background: #E7B62C; }
.smartbar .tag { color: #5A6488; background: rgba(27,42,99,0.06); border-color: rgba(27,42,99,0.14); }
.screen { border: 4px solid #1E2C62; border-radius: 12px;
  box-shadow: 16px 16px 0 rgba(27,42,99,0.15); }
.wallrow { color: #1E2C62; }
.wallrow .sep { color: #E7B62C; }"""

THEMES = {
    "lineart": {
        "css": LINEART,
        "landscape": ("minimal-landscape.html", "lineart-landscape.html", "minimal", "lineart", "EnConvo Launch Film — Line Art"),
        "vertical":  ("minimal-vertical.html",  "lineart-vertical.html",  "minimal-vertical", "lineart-vertical", "EnConvo — Line Art Vertical"),
    },
}

def build(css, src, dst, comp_from, comp_to, title):
    html = (SC / src).read_text()
    inject = f'<style id="{comp_to}-skin">\n{css}\n</style>\n  </head>'
    html = html.replace("</head>", inject, 1)
    html = html.replace(f'data-composition-id="{comp_from}"', f'data-composition-id="{comp_to}"')
    html = html.replace(f'__timelines["{comp_from}"]', f'__timelines["{comp_to}"]')
    html = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", html, count=1, flags=re.S)
    (SC / dst).write_text(html)
    return dst

if __name__ == "__main__":
    for name, spec in THEMES.items():
        for orient in ("landscape", "vertical"):
            out = build(spec["css"], *spec[orient])
            print(f"wrote {out}")
