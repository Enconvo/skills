# Visual Styles — 11 Presets

Each preset is a complete visual identity. When you pick one, the spec's DESIGN.md section copies that preset's palette / typography / motion / anti-patterns verbatim.

## Domain → Default Style

When the user gives no style direction, use this table:

| Content domain | Default style |
|---|---|
| Aerospace, engineering, scientific missions | **Mission Control Cinematic** |
| SaaS product launch, startup, dev tool | **Swiss Pulse** |
| Luxury brand, fashion, hospitality, real estate | **Velvet Standard** |
| Financial report, dashboard, analytics | **Data Drift** |
| Music release, cultural manifesto, sport hype | **Maximalist Type** |
| Wellness, lifestyle, personal story, non-profit | **Soft Signal** |
| Gaming, nightlife, crypto, culture drop | **Neon Frequency** |
| Sustainability, artisan, outdoor, food/drink | **Folk Frequency** |
| Investigative, crime, hard news, thriller | **Shadow Cut** |
| Art piece, think-piece, avant-garde editorial | **Deconstructed** |
| Breaking news, live operations brief, government | **Broadcast Bulletin** |

---

## 1. Mission Control Cinematic

**Mood:** dark, precise, weighted. Think NASA flight dynamics console meeting a space documentary.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#05070D` | body background |
| Surface | `#0B1426` | panels, stat cards |
| Foreground | `#E8EEF7` | all text (cool-tinted, never pure white) |
| Ignition | `#FF6B35` | burns, launches, CTAs |
| Telemetry | `#4FC3F7` | trajectories, data labels |
| Lunar gold | `#FFD166` | closest-approach, final stats |

**Typography:** Space Grotesk (display, 500/700) + JetBrains Mono (telemetry, 500, `tabular-nums` always on).

**Motion signature:** `power3.out` / `expo.out` for entrances (0.5–0.8s). `sine.inOut` for ambient loops (3–6s). Counters on `power1.out`. NO bouncy eases. Starfield parallax ambient on every scene.

**Transitions:** CSS sine crossfade 0.6s; if shaders available, cross-warp morph or cinematic zoom.

**Anti-patterns:**
- ❌ Generic tech-blue (#3B82F6, #0EA5E9). Telemetry cyan is `#4FC3F7` only.
- ❌ Roboto / Inter / Montserrat. Space Grotesk + JetBrains Mono, nothing else.
- ❌ back.out, elastic, any overshoot.
- ❌ Full-screen linear gradients on dark (H.264 banding).
- ❌ Emoji / clipart rockets. Line-art SVG only.

**Example:** NASA Artemis II crewed lunar flyby explainer. See [../examples/artemis-ii-spec.md](../examples/artemis-ii-spec.md).

---

## 2. Swiss Pulse

**Mood:** minimal, disciplined, rhythmic. International Typographic Style with a heartbeat.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#FFFFFF` | body bg |
| Ink | `#0A0A0A` | primary text |
| Paper grey | `#E8E8E8` | rules, dividers |
| Signal red | `#E53935` | accents, underlines, one hero mark per scene |
| Cool grey | `#6B6B6B` | secondary text |

**Typography:** Inter Tight (display, 600/800) + Inter (body, 400). All body at 20px minimum. Grid snapped to 8px.

**Motion signature:** `power4.out` (0.25s) for type slams. `expo.inOut` for scaled reveals. Short, disciplined, rhythmic. No ease-in-out on entrances (feels lazy). Red mark pulses on `sine.inOut` 1.2s cycle.

**Transitions:** Push slide horizontal 0.3s `power3.inOut`. One-direction only (never back-and-forth).

**Anti-patterns:**
- ❌ Drop shadows. Ever.
- ❌ More than one red mark visible at a time.
- ❌ Gradient text.
- ❌ Animated entrances over 0.4s (feels sluggish for this style).
- ❌ Breaking the 8px grid.

**Example:** SaaS product launch, "The new dashboard, in 45 seconds."

---

## 3. Velvet Standard

**Mood:** editorial, restrained, premium. Quiet luxury; the video equivalent of a Loewe print ad.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#F5F1EA` | warm bone |
| Ink | `#1C1B18` | primary text |
| Ochre | `#B4894A` | hero accent, one per scene |
| Deep plum | `#3A1F2C` | dark surface variant |
| Paper mid | `#D6CFBF` | rules |

**Typography:** GT Sectra (display serif, 400/500, italic allowed) + Söhne (body sans, 400). Generous letter-spacing on captions (+0.12em small-caps).

**Motion signature:** `power1.inOut` 0.8–1.2s. Everything slow. Objects drift rather than snap. Subtle film-grain overlay (8% opacity, seeded).

**Transitions:** Blur crossfade 0.8s 20px peak blur. Or focus-pull.

**Anti-patterns:**
- ❌ Any sans-serif for titles.
- ❌ Animation under 0.6s. Restraint is the point.
- ❌ Saturated brights. Every colour reads like it was printed on matte paper.
- ❌ Ticker / monospace / telemetry tropes.
- ❌ More than one hero accent colour visible at once.

**Example:** Five-star hotel brand reel, "A day at The Connaught."

---

## 4. Data Drift

**Mood:** calm, instrumented, analytical. Bloomberg terminal if it were designed by Muji.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#0E1116` | dark slate |
| Surface | `#171B22` | panels |
| Ink | `#D4DAE3` | primary text |
| Chart teal | `#4DD0C1` | primary data |
| Chart amber | `#FFB648` | secondary data, warnings |
| Chart magenta | `#E573C7` | tertiary |

**Typography:** IBM Plex Sans (display, 500/600) + IBM Plex Mono (numbers, 500 `tabular-nums`). Consistent x-height.

**Motion signature:** `power2.out` for counters (0.6s). Line charts draw on `power1.inOut` over 1–2s. NOTHING bounces. Values tween to final; no wobble past target.

**Transitions:** Fade 0.25s. Absolutely nothing fancy — this is an analyst's video.

**Anti-patterns:**
- ❌ 3D chart anything.
- ❌ Decorative icons on data.
- ❌ Colour without meaning (every hue maps to a data category).
- ❌ Over-bright accents — saturate stays below 80.
- ❌ Animating values past their final number (no overshoot on counters).

**Example:** Quarterly earnings recap video, "Q3 by the numbers."

---

## 5. Maximalist Type

**Mood:** loud, kinetic, typographic. Words ARE the visual.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#111111` | near-black |
| Hero | `#FFE500` | huge type fill |
| Counter | `#FF2E63` | clash accent |
| Ink | `#F2F2F2` | secondary type |
| Deep | `#2A1F4D` | mood surface |

**Typography:** Redaction (display serif, ultra-bold 900) + Söhne Breit (heavy sans). Sizes: hero 280–420px on 1080p landscape. Words go edge-to-edge.

**Motion signature:** `expo.out` snap (0.2s) for type entrances. `power4.in` for exits. Type rotates, stretches, clip-paths. Beats sync to audio if music is present (see `hyperframes` audio-reactive reference).

**Transitions:** Cuts. Hard cuts with 1–3 frame flashes of hero colour. No crossfades.

**Anti-patterns:**
- ❌ Polite sizing. If the hero word fits with padding, it's too small.
- ❌ Rounded sans-serifs. This style is sharp.
- ❌ Centered layouts for every scene. Asymmetry is the point.
- ❌ Drop shadows.
- ❌ Dulled colours. Every hue is at full chroma.

**Example:** Music release drop, "LOUD. NEW. NOW."

---

## 6. Soft Signal

**Mood:** warm, human, soft-focus. Independent documentary.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#F7F3EC` | warm cream |
| Ink | `#2A2824` | primary |
| Dusty rose | `#D8A29C` | accent |
| Sage | `#A8B09A` | support |
| Terracotta | `#C05E3C` | emphasis |

**Typography:** Fraunces (display serif, 400/500 with soft curves) + Söhne (body, 400, 22px+). Generous line height 1.6.

**Motion signature:** `sine.inOut` 0.9–1.4s. Cross-fades. Camera-like drifts (2–4% scale over many seconds). Gentle breathe on decoratives. 0.3s offsets create calm.

**Transitions:** Gentle blur crossfade 1.0s 30px blur.

**Anti-patterns:**
- ❌ Hard cuts.
- ❌ Mono fonts (wrong register entirely).
- ❌ High-saturation accents — every hue looks sun-washed.
- ❌ Fast entrances. If it feels urgent, it's the wrong style.
- ❌ Pure black. Ink is `#2A2824` for a reason.

**Example:** Nonprofit story, "Maria's garden, one season later."

---

## 7. Neon Frequency

**Mood:** saturated, electric, late-night. CRT glow, chromatic aberration, arcade heartbeat.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#0A0018` | near-black violet |
| Neon cyan | `#00F0FF` | primary accent |
| Neon magenta | `#FF2EC8` | secondary accent |
| Acid lime | `#C6FF3A` | hero pop |
| Ink | `#EAE6F0` | text (tinted cool) |

**Typography:** Space Grotesk (display, 700) + VCR OSD Mono (mono/ticker, 500). Optional: all-caps with +0.1em tracking.

**Motion signature:** `power4.inOut` snaps. RGB chromatic-split on entrance (3–6px red/cyan offset, resolves). Scan-line overlay. Glow pulses on `sine.inOut` 0.8s.

**Transitions:** Glitch / chromatic split 0.3s. Sometimes a hard cut with a single-frame color flash.

**Anti-patterns:**
- ❌ Serifs. Anywhere.
- ❌ Muted neutrals. If it's grey, it's tinted cyan or magenta.
- ❌ Subtle animation. Subtlety is the opposite of this style.
- ❌ Over 3 hues in a single scene (chaos vs intentional).
- ❌ Real-world photography as full-bleed (clashes with synthetic palette; use duotone).

**Example:** Indie game launch teaser, "PULSE // drops Oct 31."

---

## 8. Folk Frequency

**Mood:** earthen, hand-made, organic. Farmers-market poster aesthetic.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Paper | `#EFE6D2` | warm beige |
| Ink | `#2B2416` | dark umber |
| Clay | `#B15A33` | primary accent |
| Moss | `#5B6A3B` | secondary |
| Marigold | `#E5A443` | pop |

**Typography:** Fraunces (display serif, 600 italic allowed) + IBM Plex Sans (body). Optional: hand-written touches via rough SVG (never a script font).

**Motion signature:** `power1.out` 0.7s. Gentle sway on decoratives (`sine.inOut` 4s). Rough-edged clip-paths for reveal. Paper-texture overlay 12% opacity.

**Transitions:** Paper-tear reveal or gentle crossfade 0.7s.

**Anti-patterns:**
- ❌ Pure white (`#FFFFFF`). Paper is always tinted.
- ❌ Sans-serif displays.
- ❌ Digital-feeling UI chrome (progress bars, telemetry tickers, counters).
- ❌ Pure geometric shapes without hand-drawn imperfection.
- ❌ Saturated neon anywhere.

**Example:** Organic olive oil brand story, "From grove to bottle."

---

## 9. Shadow Cut

**Mood:** monochrome, dramatic, noir. A documentary that knows where the bodies are buried.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#08080A` | near-black |
| Ink | `#E4E4E4` | primary text |
| Mid grey | `#6E6E70` | secondary text |
| Deep red | `#8B1A1A` | single hero accent, used sparingly |
| Paper rule | `#2A2A2C` | dividers |

**Typography:** GT America Condensed (display, 700) + GT America (body, 400). Upper-case headlines. Mono allowed for metadata (locations, dates).

**Motion signature:** `power4.in` type slams. Hard cuts. Single scene may hold 4–5s on a fixed frame before cutting. Type locks into place; nothing drifts. Grain overlay (15% opacity, seeded).

**Transitions:** Hard cut. Occasional 1-frame black flash.

**Anti-patterns:**
- ❌ Any colour except the single red accent.
- ❌ Curved / rounded anything.
- ❌ Gradients.
- ❌ Animations > 0.4s (feels too soft).
- ❌ Overlapping type layers. One headline at a time.

**Example:** Investigative short, "The missing seven hours."

---

## 10. Deconstructed

**Mood:** broken grids, raw, experimental. Reads like an art school zine.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#F2EEE7` | off-cream |
| Ink | `#111111` | primary |
| Electric blue | `#2B44FF` | accent |
| Highlighter | `#D8F23C` | emphasis |
| Printer magenta | `#E0148C` | secondary accent |

**Typography:** Neue Haas Grotesk Display (700) + Times New Roman (serif body, 400). Mixing sans and vintage serif is intentional. Letter-spacing varies per scene.

**Motion signature:** `expo.out` slams for type. Decoratives rotate slightly off-grid (-2° to +3°). Some elements clip outside the 1920×1080 frame deliberately. Markers / underlines hand-drawn via SVG path animation.

**Transitions:** Hard cut with a layout break (type jumps to a different grid orientation).

**Anti-patterns:**
- ❌ Symmetry.
- ❌ Everything snapped to grid. Break it deliberately in each scene.
- ❌ Subtle colour. When accents appear, they're full-chroma.
- ❌ Fewer than 3 type sizes per scene.
- ❌ "Clean" composition. This style is controlled-chaos.

**Example:** Art-fair promo, "PROCESS / MATTER / REPEAT."

---

## 11. Broadcast Bulletin

**Mood:** news-room, authoritative, ticker-driven. Live-ops dashboard energy.

**Palette:**
| Role | Hex | Use |
|---|---|---|
| Canvas | `#0C0F14` | deep slate |
| Chyron red | `#C8102E` | lower-third, breaking flag |
| Alert amber | `#F2A900` | advisories |
| Ink | `#F5F7FA` | primary text |
| Rule grey | `#2A2F38` | panel borders |
| Data cyan | `#4DB8FF` | ticker / data |

**Typography:** Roboto Condensed (display, 700) + JetBrains Mono (ticker / metadata, 500 tabular-nums). All lower-thirds in upper-case.

**Motion signature:** `power3.inOut` slides for lower-thirds (0.35s). Ticker scrolls linearly `none` ease, constant speed. Chyron flag pulses `sine.inOut` 1.2s. Map/data draws on `power2.out` 0.8s.

**Transitions:** Wipe 0.25s or hard cut. Chyron may stay fixed while scene wipes behind it.

**Anti-patterns:**
- ❌ Serif fonts anywhere.
- ❌ Slow entrances (>0.5s). Broadcast is urgent.
- ❌ Pastel tints. Every colour is saturated news-room.
- ❌ Removing the ticker. The ticker is the spine of this style.
- ❌ Breaking the lower-third grid.

**Example:** Government agency status update, "Hurricane advisory — Day 3."

---

## Custom style

If the user's request doesn't fit any preset, author a Custom entry in the spec with the same 4-section structure: **Palette (6 hex + roles), Typography (display + mono), Motion signature, Anti-patterns (5+ bullets)**. A Custom style is valid; skipping the structure is not.

## Hybrid is banned

Don't combine "Swiss Pulse typography with Neon Frequency colour." It reads as confused. Pick one preset, or build a Custom one. Hybrids always flop in production.
