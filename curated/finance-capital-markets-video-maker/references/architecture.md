# Architecture

## Visual Blocking

```
┌───────────────────────────────────────────────────────────┐ ← 1280 x 720
│                                          │  RIGHT 42%       │
│           ANCHOR (left 58%)              │  Dark editorial  │
│           Red blazer, news desk,         │  GSAP overlay    │
│           hands locked on desk,          │  panel:          │
│           subtle head/eye motion,        │   - kicker       │
│           static studio LED plate        │   - hero numbers │
│           behind her.                    │   - shimmer      │
│                                          │   - chyron bar   │
│  ⌈Vivieen │ SpaceX IPO 拆解   ACT 01⌉   │  (lower-left)    │
└───────────────────────────────────────────────────────────┘
```

## Why This Architecture

- **Anchor full-duration base** — keeps continuity, lets us bake VO speech into i2v so lipsync is native (no separate TTS layer to drift).
- **Static background** — the studio LED plate is a billion-dollar TV-set illusion. The instant it drifts, the brain sees "AI video". Static plate + moving anchor = real broadcast feel.
- **Right-40 reserved** — negative-space discipline gives the overlay panel a clean canvas every scene without bumping into the anchor's silhouette. Hands locked on desk enforces this.
- **HF overlay layer for all motion** — numbers, charts, callouts, transitions live in HTML+GSAP. Iterable in seconds. Anchor i2v renders are expensive (~30s/clip), HF re-renders are cheap.
- **Frame continuity *within* an ACT, RESET *between* ACTs.** Inside one ACT, strict endframe-to-startframe handoff makes the multi-clip anchor read as one continuous shot — without this, blink-cuts and color jumps shatter the illusion. But at every ACT boundary, the chain HARD-RESETS to the canonical locked anchor reference image. The first clip of every new ACT uses that locked reference URL, never the previous ACT's endframe. Cumulative drift (face / wardrobe / background / anchor position) compounds clip-by-clip; without the per-act reset, by ACT 5 or 6 the anchor visibly looks like a different person. The reset caps drift to within-act only and locks identity at every act boundary.

## Identity Lock

The anchor reference image is the SOURCE OF TRUTH. Every clip's i2v prompt re-asserts:

- Same face geometry (chin shape, brow, eye spacing)
- Same hair (sleek blowout, slight side part)
- Same wardrobe (scarlet Saint Laurent Le Smoking peak-lapel blazer, ivory silk shell, pearl-drop gold earrings, slim Cartier Tank watch)
- Same set (contemporary studio, out-of-focus night-city skyline through angled glass, amber key left + cool blue rim right, dark news desk, no visible screens/text)
- Same lighting (warm key from left, soft fill, rim from amber LED)

Deviation from any of these = identity break.

## Track Layout (HF composition)

```
track 0: anchor base video (full duration)
track 1: anchor base audio (full duration, baked VO)
track 2: persistent chyron (full duration)
track 3: scene panels (start/duration per scene)
track 4: BGM bed (full duration, ducked under VO)  [optional]
```

## Anchor Camera & Framing Lock

- Camera: locked-off medium close-up, anchor framed chest-up, eyeline slightly camera-right (toward the overlay panel zone)
- Background: static studio LED plate, amber tungsten with cool blue rim
- Hands: rest on desk, no gestures
- Head/eye: subtle natural movement only — small nods, blinks, slow eyeline shifts
- No zoom, no pan, no dolly

## ACT vs Scene

- **ACT** = one HF composition, one anchor concat video, ~40–120s. Has its own `hf_act{N}/` directory.
- **Scene** = one overlay panel inside an ACT, ~10s typical. Shares the same anchor base video, takes over the right-40 panel for its `data-start` window.

A 4-scene ACT = 4 panels in `hf_act{N}/index.html` + 4 anchor i2v clips concatenated as `act{N}_anchor.mp4` base track.
