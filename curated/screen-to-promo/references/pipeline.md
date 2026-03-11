# Screen-to-Promo Pipeline Reference

## Strategy Playbooks

The skill is goal-aware. Different user intents activate different playbooks that shape every decision from trimming to zooming to CTA.

### Viral Marketing Promo

**Goal**: Make viewers WANT to try the product. Optimize for shares, saves, and clicks.

**Structure**: Pain → Solution → Magic → Payoff (30-90s)

| Element | Approach |
|---------|----------|
| **Hook (0-3s)** | Open with a pain point or provocative question. "Building an AI agent used to mean... all of this." Show the mess first. |
| **Source trimming** | Ruthless — use only 20-30% of source. Only the "wow" moments. Reorder for dramatic arc, not chronological. |
| **Pacing** | Fast cuts (2-5s per shot in early section), dramatic pauses at reveals, accelerating rhythm toward payoff. |
| **Zooms** | Max 3-4. Each is a dramatic reveal: peek → sustained focus → payoff. Never for readability — for IMPACT. |
| **Captions** | Bold, large (96px), pop or karaoke style. Word-by-word for rhythm. All caps for impact words. |
| **VO** | Multi-voice for energy, or single dramatic narrator. Emotional range: frustrated → excited → triumphant. |
| **Music** | Dramatic bed, builds tension, drops at the payoff moment. |
| **CTA** | Hard CTA: product name + tagline + "link in bio" / social handles. End card with logo. |
| **Platform targets** | TikTok (9:16 or 16:9, 60s ideal), Reels (90s max), Shorts (60s), Twitter (2:20 max) |

**Narrative template:**
1. **Pain** (0-10s): Show the old painful way
2. **Introduce solution** (10-15s): "Meet [Product]"
3. **Magic** (15-50s): Show the product doing the thing, zoom on key moments
4. **Payoff** (50-60s): The result — it works, it's alive, it's beautiful
5. **CTA** (last 5s): Product name, tagline, call to action

### User Guide / Tutorial

**Goal**: Teach users how to accomplish a specific task. Optimize for clarity and completeness.

**Structure**: Setup → Step 1 → Step 2 → ... → Result (3-15min)

| Element | Approach |
|---------|----------|
| **Hook** | None needed — user chose to watch this. Brief "In this guide, you'll learn to..." |
| **Source trimming** | Minimal — use 80-90% of source, in order. Only skip dead time (loading, idle cursor). |
| **Pacing** | Slow, methodical. Follow the cursor. Pause after each step for comprehension. |
| **Zooms** | Many — zoom every time the user needs to read text, find a button, or see a detail. Stay zoomed until step completes. |
| **Captions** | Step labels ("Step 1: Create a new project"), numbered, persistent. Clean font, moderate size. |
| **VO** | Single calm narrator. Instructional tone. "Now click on Settings, then navigate to..." |
| **Music** | None or very subtle ambient. Never distracting. |
| **CTA** | Soft: "Now try it yourself" or "See our docs for more" |
| **Annotations** | Cursor highlights, click indicators, numbered callouts on UI elements |

**Narrative template:**
1. **Intro** (10-15s): What you'll learn, prerequisites
2. **Steps** (bulk): Each step = show action → explain → confirm result
3. **Summary** (10-15s): Recap what was accomplished
4. **Next steps**: Link to related guides

### Product Demo

**Goal**: Show features to convince a potential buyer/user. Balance between marketing and education.

**Structure**: Problem → Feature → Benefit → Repeat → CTA (1-3min)

| Element | Approach |
|---------|----------|
| **Hook** | Brief value prop: "See how [Product] handles [problem] in under 2 minutes" |
| **Source trimming** | Moderate — use 50-70% of source. Keep feature highlights, cut transitions/loading. |
| **Pacing** | Medium. Feature-by-feature, each gets its moment. Don't rush, don't linger. |
| **Zooms** | One per feature — zoom when the feature activates, zoom out when moving to next. |
| **Captions** | Clean, informative. Feature names as section headers. |
| **VO** | Confident, persuasive single narrator. "Notice how it automatically..." |
| **Music** | Subtle professional background. |
| **CTA** | "Get started at [url]" or "Free trial available" |

### Changelog / What's New

**Goal**: Quick showcase of new features for existing users.

**Structure**: Montage of features, 5-10s each (30-90s total)

| Element | Approach |
|---------|----------|
| **Source trimming** | Heavy — one clip per feature, best 5-10s each |
| **Pacing** | Fast montage, consistent rhythm |
| **Zooms** | Quick peek per feature, same pattern throughout |
| **Captions** | Feature name + one-line description overlay |
| **VO** | Upbeat, concise: "New in v2.5..." |

---

## Full Pipeline (7 Steps)

### 1. Analyze Source Material
```bash
# Prep each screen recording into 1920x1080 frames
scripts/prep_source.sh ~/Desktop/feature-demo.mov ./frames/feature1/ 30
```
- Note content bounds if letterboxed (CONTENT_BOUNDS output)
- Check key moments: when does the action happen? Map timestamps.

### 2. Generate Presenter (Optional)
- Use nanobanana skill with `--reference` for consistent character
- 1/5 left framing: presenter occupies leftmost 20-25%, right 75-80% pure white
- PHOTOREALISTIC style, not cartoon/3D
- Generate I2V clip via Veo skill (8s, native audio)
- Extract frames: `ffmpeg -i presenter.mp4 -r 30 -q:v 2 frames/presenter/f_%04d.jpg`
- rembg cutout: `from rembg import remove, new_session` (batch all frames)

### 3. Write Script + Generate VO
- Simple everyday words, dramatic delivery tone
- Use voicebox skill to clone presenter voice from Veo native audio
- Generate per-section VOs
- Get word timestamps: Groq Whisper API with `timestamp_granularities[]=word`

### 4. Time-Map VO to Source
Map VO script beats to source video timestamps:
```python
import numpy as np
vo_times = [0, 2.5, 5.0, 10.0, 15.0]   # when VO says each beat
src_times = [0, 2.0, 4.0, 8.0, 18.0]    # matching source moment
src_t = float(np.interp(vo_t, vo_times, src_times))
```

### 5. Build Config JSON
See compose.py docstring for full schema. Key decisions:
- Zoom targets: where does the action happen? (cx, cy coordinates)
- Transition type: overlay_dissolve for presenter→screenrec
- Smooth jumps: identify source times where UI changes abruptly

### 6. Compose + Mix Audio
```bash
python3 scripts/compose.py --config config.json --output-frames ./frames/output/
bash scripts/audio_mix.sh output.m4a -25 hook.wav gap explain_vo.wav transition_vo.wav spelling_vo.wav
```

### 7. Encode Final Video
```bash
# Option A: Use compose.py --output for one-step compose+encode
python3 scripts/compose.py --config config.json --output final.mp4 --audio output.m4a

# Option B: Manual encode from frames
ffmpeg -y -r 30 \
  -i ./frames/output/f_%04d.jpg \
  -i output.m4a \
  -c:v libx264 -preset fast -crf 23 -pix_fmt yuv420p \
  -vf "setsar=1" \
  -c:a copy -map 0:v -map 1:a \
  final.mp4
```

## Critical Rules (Learned the Hard Way)

### AR Distortion Prevention
- **ALWAYS** lock aspect ratio in zoom: `ch = cw × H / W`
- **NEVER** zoom letterboxed frames directly — crop content first, re-center, then zoom
- **ALWAYS** `setsar=1` in final encode
- **ALWAYS** send to Telegram with explicit `width=1920 height=1080`

### Audio Rules
- **Never loudnorm original Veo/source audio** — use untouched, it distorts quality
- **concat > amix** for sequential segments (amix divides amplitude)
- **Check word timestamps before cutting** — don't cut at round numbers, verify the last word ended
- **0.5s silence gaps** between sections for breathing room
- **Target -25 LUFS** for VO segments (loudnorm I=-25:TP=-3:LRA=11)

### Transitions
- Presenter→screenrec: use overlay_dissolve (cutout on top, BG fades in gradually, presenter fades out)
- BG fade should start 0.5-1s BEFORE presenter fade for smooth layered feel
- Cosine ease-in-out for all fades: `0.5 - 0.5 * cos(progress * π)`
- If source has UI jumps (panels appearing), add to smooth_jumps list

### Captions
- Word-level timestamps via Groq Whisper (`timestamp_granularities[]=word`)
- Pop style: scale bounce + underline swipe looks best on TikTok
- Position: H - 130px from bottom
- White text, black outline (3px), yellow accent underline

### Source Prep
- Always prep to 1920x1080 at 30fps regardless of source resolution/fps
- Record content bounds for letterboxed sources
- Screen recordings from retina displays may be 2x — scale down

---

## Planning Protocol

Before any production work, the agent MUST complete this analysis. Skipping planning leads to wrong zoom targets, bad timing, and wasted compose cycles.

1. **Probe source**: resolution, duration, fps, audio presence, letterboxing
   ```bash
   ffprobe -v quiet -print_format json -show_streams source.mov
   ```
2. **Extract key frames**: every 10s, visually identify what's on screen
   ```bash
   ffmpeg -i source.mov -vf "fps=0.1" -q:v 2 keyframes/kf_%04d.jpg
   ```
3. **Identify content regions**: app windows, chat areas, sidebars, toolbars — these become zoom targets. Measure actual pixel coordinates from key frames.
4. **Detect artifacts**: recording control bars, cursor idle periods, blank screens, notification popups — mark as "avoid" zones. Use `smooth_jumps` or time-map to skip/blend these.
5. **Map visual beats**: timestamp each meaningful action in the recording (feature appears, button clicked, result shown, etc.)
6. **Research context**: product/brand name, target audience, community terminology, platform constraints (TikTok 60s/3min, Reels 90s, Shorts 60s), language/localization needs
7. **Build zoom table** from actual frame analysis (not guessing):

   | Zoom | Purpose | Source frame | cx,cy | Scale | VO sync | Hold duration |
   |------|---------|-------------|-------|-------|---------|---------------|
   | 1 | Feature peek | f_0850 | 1200,185 | 2.0x | "Meet X" @0:22 | 10s |
   | 2 | Detail focus | f_2100 | 960,450 | 2.0x | "Watch this" @1:10 | 18s |
   | 3 | Result payoff | f_3400 | 1100,300 | 2.2x | "And there it is" @1:52 | 12s |

8. **Pre-validate** before production:
   - Check time-map for big jumps (add `smooth_jumps` entries)
   - Verify zoom windows actually contain the target content
   - Check font supports required characters (CJK needs `/Library/Fonts/Arial Unicode.ttf`)
   - Verify total duration fits platform limits
   - Confirm all source files exist and frame counts match expected durations

---

## Zoom Playbook

### Focus Area Accuracy
- **Never guess cx/cy** — extract the actual frame at zoom start, measure pixel coordinates from the image
- **Account for content drift** — use `cy_start`/`cy_end` to pan with scrolling content (compositor interpolates between them)
- **Safety margin** — at 2.0x on 1920×1080, viewport is 960×540. Target content must fit with ~50px padding on all sides
- **Edge check**: `cx ± (W/2/scale)` must stay within frame bounds and contain all target content
- **Letterboxed sources**: zoom coordinates are in the re-centered coordinate space (after content cropping), not the original letterboxed frame

### Timing
- Zoom in **1-2s BEFORE** the VO mentions it — gives audience time to orient
- Zoom out during a **natural pause or topic transition** — never mid-sentence
- Hold sweet spot: **8-20s** for focused moment, up to **45s** for sustained action
- Too short (<5s) feels jarring, too long (>60s) audience forgets the wide view
- `in_start` to `in_end`: 1.5s zoom-in with cosine ease
- `hold_end` to `out_end`: 1.5s zoom-out with cosine ease

### Frequency / Rhythm
- **Max 3-4 zooms per 2-minute video**
- **Minimum 15-20s** between zoom-out and next zoom-in
- Zoom pattern follows narrative arc:
  - **Zoom 1**: Quick peek (short hold) — "here's what we're looking at"
  - **Zoom 2**: Sustained focus (long hold) — "watch this happen in detail"
  - **Zoom 3**: Payoff moment (medium hold) — "look at the result"
- **Never stack zooms back-to-back** — unzoomed sections establish context and give visual breathing room
- Use the `zooms` array in config to define multiple zooms per segment

### Scale Discipline
- **2.0x** is the sweet spot for 1080p screen recordings
- **2.2-2.5x** only for small targets (single chat bubble, button, status indicator)
- **Never exceed 3.0x** — pixel quality degrades noticeably
- Keep scale **consistent** across zooms (e.g. 2.0x/2.0x/2.2x, not 1.5x/3.0x/1.8x)

---

## Caption Reference

### Styles

| Style | Behavior | Best for |
|-------|----------|----------|
| `pop` | Word-by-word display with scale bounce (0.15x for 0.3s) + accent underline swipe | English content, high-energy TikTok |
| `karaoke` | Full phrase visible, active word highlighted with accent color + pop bounce, inactive words dimmed. CJK-aware: no spaces between Chinese/Japanese characters | Chinese/CJK content, lyric-style narration |
| `static` | Simple static text, no animation | Subtitles, minimal style |

### Options

```json
{
  "captions": {
    "enabled": true,
    "style": "karaoke",
    "font": "/Library/Fonts/Arial Unicode.ttf",
    "font_size": 48,
    "position_y": -130,
    "color": [255, 255, 255],
    "outline_color": [0, 0, 0],
    "accent_color": [255, 200, 50],
    "no_outline": false
  }
}
```

| Option | Type | Default | Notes |
|--------|------|---------|-------|
| `font` | string | system default | Path to TTF/TTC. CJK requires a CJK font like Arial Unicode |
| `font_size` | int | 52 | Base size in px. Use 96 for large bold impact |
| `no_outline` | bool | false | Removes 3px stroke outline for clean solid text |
| `color` | [R,G,B] | [255,255,255] | Main text color |
| `accent_color` | [R,G,B] | [255,200,50] | Active word highlight + underline color |
| `outline_color` | [R,G,B] | [0,0,0] | Stroke color (ignored when no_outline is true) |
| `position_y` | int | -130 | Offset from frame bottom (negative = up from bottom edge) |

### Font Recommendations

- **English (bold impact)**: `/System/Library/Fonts/Supplemental/Arial Bold.ttf`
- **CJK (Chinese/Japanese)**: `/Library/Fonts/Arial Unicode.ttf` — REQUIRED for CJK content, system default fonts will show boxes
- **General fallback**: system Helvetica (macOS), DejaVu Sans Bold (Linux)

---

## Whisper Word Timestamp Gotchas

### English Brand Names in Non-English Audio
Whisper fragments English brand names when the surrounding audio is non-English. Examples:
- "EnConvo" → `"En" + "Con" + "vo"`
- "Telegram" → `"Te" + "le" + "gram"`
- "TikTok" → `"Tik" + "Tok"`

**Fix**: Always post-process word timestamps to merge known brand/product terms back together. This is project-specific — each project needs its own merge rules based on the brands/products mentioned in the script.

### CJK Content
- Whisper returns individual characters for Chinese/Japanese, not words
- The `karaoke` caption style handles this automatically via `active_word_group()` which groups nearby characters into display lines (configurable `window` parameter, default 6)
- No manual post-processing needed for CJK character grouping

### General Tips
- Always verify word timestamps against the audio before composing — off-by-one errors in timestamps cause visible caption desync
- Whisper sometimes merges words or splits them unexpectedly — spot-check the words JSON
- The compositor adds 0.15s grace period after each word's `end` time to avoid flickering
