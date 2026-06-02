---
name: finance-capital-markets-video-maker
description: Produce multi-act long-form Mandarin financial analysis videos for social-media upload (TikTok/Bilibili/YouTube/WeChat视频号/X). Given any input source (news article, earnings call, IPO filing, macro print, chart, tweet thread, raw data), build a broadcast-grade anchor-led explainer using a locked pipeline — script in tight 5字/second cadence, render anchor with xAI Grok Imagine Video i2v with baked Mandarin VO and locked identity, composite editorial GSAP overlay panels via HyperFrames in the right 40% of frame, concat acts, mix BGM, ship MP4. Use when the user gives a finance/markets/macro/equity/options/IPO/crypto source and asks for a viral video, a 解读视频, a 拆解视频, an explainer, a TG/SNS-ready clip, or simply says "make a video about this". Also use when the user says "finance-capital-markets-video-maker", "FCM video", "market video", "anchor video", or "Vivieen video".
---

# Finance & Capital Markets Video Maker

This is the locked playbook for shipping Vivieen-style anchor-led Mandarin financial analysis videos. Architecture, palette, pacing, and pipeline are non-negotiable defaults; deviate only when the source genuinely demands it.

## What This Skill Produces

- **Format:** 1280x720 MP4, 30fps. Vertical 1080x1920 variants on request.
- **Length:** 30s–12min, organized into ACTs of ~40–120s.
- **Style:** Female Mandarin anchor (Vivieen DNA, red blazer, news desk) on left 60% + dark editorial overlay panel on right 40%. Persistent lower-left chyron. Optional BGM bed.
- **Voice:** Calm institutional broadcast Mandarin, baked into the video via xAI i2v prompt — NO separate TTS layer.
- **Pacing (CN):** 5 字/s = 300 字/min monologue. 10s clip = 50 字. 6s clip = 30 字.
- **Pacing (EN):** ~150 wpm (~2.5 words/s) for an authoritative anchor read. 10s clip = ~25 words (cap ~28). 14s clip = ~33–35 words. Under-filling a clip (e.g. ~18 words over 14s ≈ 95–110 wpm) makes Grok pad the delivery into a slow-"poem" drag — match word count to clip length. NEVER word-for-word translate EN↔CN and expect matching timing: 25 EN words ≈ 45–55 字. Write each language to its OWN rate budget.

## Locked Architecture (do not deviate)

1. **Anchor is the base video, full duration of every scene.** All audio (speech) comes from the i2v render. No separate TTS, no separate audio track.
2. **Background is STATIC.** The studio LED plate behind the anchor never drifts, pans, or animates. Only the anchor moves. All motion lives in the HF overlay layer.
3. **Right 40% of frame is reserved negative space** — anchor's hands stay locked on the desk, no gestures into that region. The HF overlay panel fills exactly that area.
4. **Frame continuity = endframe chain WITHIN ACT, hard reset AT ACT boundary.** This is the empirically-confirmed doctrine (do not regress to v3 "canonical reset every clip" — see below).
   - **NO FaceFusion / faceswap. Ever.** Trialed and abandoned — output looks plastic/ugly and *adds* drift instead of fixing it. Identity is held by endframe-chain + per-act canonical-reference reset ONLY. Never add a faceswap pass to the pipeline, even if memory suggests it.
   - **Within an ACT:** clip N+1's start image = clip N's last frame (extract via `ffmpeg -sseof -0.1`, upload via `enconvo/upload_file`) — EXCEPT the 3rd clip of every ACT (see next rule).
   - **Mid-ACT canonical re-anchor at clip 3 (REQUIRED).** The 3rd clip of every ACT does NOT chain from clip 2's endframe — it resets to the ORIGINAL canonical anchor reference image, exactly like an ACT-boundary reset. Empirically, by the endframe of clip 2 the anchor has already drifted enough that clips 4-6 chained off it reach the act's FINAL frame looking visibly unlike the reference. So each ACT now has TWO anchor points: `S01 (canonical) → S02 (chain) | S03 (canonical again) → S04 → S05/S06 (chain)`. This caps the longest unbroken chain at ≤2 clips. Safe re: burn-in because every prompt now carries the mandatory BURN-IN LOCK block, which suppresses the broadcaster-text hallucination that made the old *every-clip* reset unusable — an occasional reset at clip 3 does not reintroduce it.
   - **At ACT boundary:** first clip of next ACT resets to the canonical locked anchor reference URL. Identity is re-anchored, drift counter zeros.
   - **At every 10s seam (including ACT joins):** mask the micro-cut with a 0.15s `ffmpeg xfade` (video) + `acrossfade` (audio). Concat formula in scripts/concat_with_xfade.sh.
   - **Why not full canonical reset (v3, deprecated):** starting every clip from a still photo causes the i2v model to interpret it as a fresh "this is a TV broadcast" prompt and hallucinate on-air graphics — chyrons, lower-thirds, tickers, and literal text words like CAPTAIN, BREAKING, LIVE burned into the render. Starting from the previous clip's actual last video frame suppresses this because the model treats it as continuation of an already-established (clean) plate, not a new broadcast to dress with text. Endframe chain killed burn-in immediately when canonical reset could not.
   - **Why chain at all + why re-anchor at clip 3:** drift compounds clip-by-clip (head angle creep, slow zoom, scale-to-frame shift, micro-expression intensity). It is faster than expected — by ~clip 3-4 of a continuous chain the face has crept enough that the act's FINAL frame reads as a different woman. Capping the unbroken chain at ≤2 clips (re-anchor at clip 3 + reset at ACT boundary) keeps every frame close to the reference, while still chaining endframes on the chained clips to suppress burn-in. The old "4 chained clips ≈ 40s is fine" tolerance was too loose; the act-final frame is the strict test, not the average.
5. **Identity lock.** Anchor reference image is the source of truth for face, blazer, lighting, set. Reuse the same reference URL across the entire video.
6. **Per-act composition.** Each ACT (~40–120s) gets its own HF composition HTML that takes the concat'd anchor video as base and adds GSAP overlay scenes. Acts concat at the end with optional BGM.
7. **Burn-in lock — name the words, ban the structures, sterilize the background.** Generic "no text" prompts are insufficient. The lock that actually works names specific hallucinated tokens AND structural elements AND background sources:
   - Banned words by name: CAPTAIN, BREAKING, LIVE, CNBC, BLOOMBERG, plus any English or Chinese characters as on-air graphics.
   - Banned structures: captions, subtitles, chyrons, lower-thirds, breaking-news banners, tickers, logos, watermarks, station IDs, show titles, timecodes, frame counters, speech bubbles.
   - Banned background sources: "studio set behind her has NO visible text on any monitor, NO scrolling text, NO labeled banners."
   - Closing phrase: "All graphics added in post — render must be 100% text-free."
   - Include this block in every i2v prompt.
8. **Scale lock — freeze the cinematography.** i2v models slow-zoom and scale-to-frame even with "static" set locks. Pin it explicitly: "fixed 35mm equivalent, NO zoom, NO dolly, NO pan, NO parallax, NO scale-to-frame. Anchor's head occupies the SAME frame fraction at second 0 and second 10." Add "return to neutral resting pose by second 10" so the endframe is a clean handoff for chaining.
9. **Subject framing — whole body inside the frame.** Anchor fills the LEFT ~55%, head near the top edge, with crown, shoulders, elbows, and hands all comfortably INSIDE the frame, never cropped or touching an edge. RIGHT ~45% stays clean negative space for the overlay. If a render clips the subject or you want the body to reach an edge, REGENERATE LARGER — never centered zoom-crop a finished render, which only re-crops the same overflow and pushes parts further out. The canonical anchor is the raw model output with nothing clipped.

Full architecture detail in `references/architecture.md`.

## End-to-End Workflow

Run these phases in order. Do not skip phase 0 or phase 6.

### Preflight — Verify HyperFrames is installed (run before Phase 0)

HyperFrames is required for Phase 4 overlay composition. Check it immediately so the user knows before any rendering work begins — not mid-pipeline.

```bash
hyperframes --version
```

**If the command succeeds:** proceed normally.

**If the command is not found:** stop and tell the user:

> HyperFrames is not installed — this skill needs it to build the overlay panels (Phase 4).
>
> To install it, open EnConvo and add these two skills:
> - **`hyperframes`** — the composition authoring skill (HTML + GSAP patterns)
> - **`hyperframes-cli`** — the CLI dev loop (`lint`, `validate`, `render`)
>
> Both are available in the EnConvo skill library. Once installed, restart this session and try again.

Do NOT proceed past this check if HyperFrames is missing. Phases 1–3 could run, but Phase 4 would hard-fail and waste the user's time and rendering credits.

### Phase 0 — Source intake & angle lock

1. Read every source the user provided (URL, file, screenshot, tweet, dataset).
2. Identify the **viral angle**: the contrarian take, the hidden mechanism, the mean-reversion case, the regime change, or the asymmetric risk. Boring angles ship boring videos.
3. Pick the **act count and total runtime**:
   - 1–2 min (1–2 acts) for a single hot take
   - 3–5 min (3–5 acts) for a stock/IPO/earnings deep-dive
   - 8–12 min (8–10 acts) for a multi-mechanism dissection (default for IPO and regime-change pieces)
4. Confirm angle + runtime with the user before writing script. One sentence is enough.

### Phase 1 — Script the monologue

- Write the full monologue in Mandarin, broken into ACTs and into 10s / 6s segments.
- Hold the cadence at **5 字/second**. Count characters per segment.
- Open with hook, close with poem or one-line takeaway.
- No sources, no "according to X" — deliver as anchor-authored analysis.
- **Keep brand / product / technical / person terms in ENGLISH — do not translate, INCLUDING in the spoken VO.** Even in a Chinese cut, proper nouns and jargon stay English: company/product/tech names (OpenAI, OpenClaw, Transformer), finance acronyms (IEX, RBC, Reg NMS, NBBO, SOR, BATS), AND person names (Brad Katsuyama, not 布拉德·胜山). The anchor SPEAKS them in English mid-Mandarin, and overlays show the English form. In the i2v VO block, explicitly note the English proper nouns are pronounced naturally in English (e.g. "with 'Brad Katsuyama' and 'RBC' pronounced naturally in English") so the model doesn't mangle or transliterate them. Translating these reads as amateur dubbing. This is part of the Native-Speaker Gate.
- **Native-Speaker Gate (HARD):** the VO is AUTHORED in the target language, never translated into it. Run the read-aloud test on every line — if a clause maps word-for-word onto English syntax or uses dictionary-literal verbs (读到, 冲向, 跑赢了你), it is a defect; rewrite it the way a native finance commentator actually speaks (一看出, 赶到, 布好局, 说白了…反手赚了你的钱). When adapting an approved EN script to CN, the versions are PARALLEL AUTHORED, not mirror-translated. Full gate + worked example in `references/script-writing.md`.
- Save to session workspace as `{slug}_script_v1.md`.

#### Phase 1.5 — Cadence timing audit gate (MANDATORY — do not render before this passes)

Under-filled VO makes Grok stretch the read into slow poem cadence. Treat timing as a hard render gate, not a suggestion.

1. Create `{slug}_script_timing_audit.md` before any i2v call. Include one row per clip:
   - `act`, `clip`, `duration_s`, `vo_line`, `cjk_chars`, `english_tokens`, `numbers_symbols`, `effective_cjk_equiv`, `target_range`, `status`.
2. Count cadence with CJK-equivalent timing, not raw visible characters:
   - CJK character = 1 unit.
   - Short English acronym/token such as `AI`, `GW`, `IPO`, `ETF` = 2–3 units depending on spoken syllables.
   - English word/proper noun such as `capex`, `OpenAI`, `RBC` = 2–4 units depending on natural spoken length.
   - Compact numbers and money figures such as `$60–80B`, `5–7年`, `1–2T` = count by how they are spoken, not by glyph count.
3. Required target ranges:
   - 10s Mandarin clip: **50–58 effective CJK-equivalent units**. Below 48 = FAIL unless the clip duration is shortened.
   - 6s Mandarin clip: **30–35 effective CJK-equivalent units**. Below 28 = FAIL unless the clip duration is shortened.
   - English-only clip: ~2.5 words/s; 10s = 25 words, cap ~28. Below 22 words in 10s = FAIL unless deliberately slow and approved.
4. If any clip is under-filled, do ONE of these before rendering:
   - rewrite the VO line to hit the target range;
   - shorten that clip duration to match the actual count;
   - split/rebalance adjacent clips.
5. Add this exact delivery instruction to every i2v prompt's VO block: **"Fast institutional Mandarin business-news read, continuous cadence, no poetic pauses, no dramatic spacing, no slow inspirational delivery."** Keep the 5 字/s line too.
6. Render only the first clip, listen/check cadence, and stop for correction if it sounds padded or poem-slow. Do not batch-render the rest until the first clip cadence is acceptable.
7. Only proceed to Phase 2 when every audit row is `PASS` and the first rendered clip cadence is acceptable.

Detail + voice DNA + structural patterns in `references/script-writing.md`.

### Phase 2 — Render anchor clips sequentially (i2v)

For each segment in the script, render an anchor clip with baked VO.

1. First clip of every ACT uses the canonical locked anchor reference URL.
2. **Within an ACT, chain endframes:** extract clip N's last frame (`ffmpeg -sseof -0.1 -i clipN.mp4 -frames:v 1 -q:v 2 endframe.jpg`), upload via `enconvo/upload_file`, pass the returned URL as `image` for clip N+1 — EXCEPT clip 3 (next rule).
3. **Re-anchor the 3rd clip of every ACT to the canonical reference URL** (NOT clip 2's endframe). Anchor points per ACT = clip 1 and clip 3; chains are clip 2 (off clip 1) and clips 4/5/6 (off clip 3). This keeps the longest unbroken chain at ≤2 clips so the act's final frame stays on-model. For a 2-clip ACT there is no clip 3, so no mid-act reset; for 3+ clips it is mandatory.
4. **At every ACT boundary, hard-reset back to the canonical locked anchor URL.** Identity drift counter zeros at every ACT join.
5. Every prompt MUST include all eight blocks: VO LINE, IDENTITY LOCK, SET LOCK, CAMERA LOCK, MOTION LOCK, SCALE LOCK, BURN-IN LOCK, SUBJECT FRAMING. The last three are NON-NEGOTIABLE — omit SCALE/BURN-IN and you get slow-zoom drift and broadcaster-text burn-in; omit SUBJECT FRAMING and the body drifts off-center or gets clipped at the edges. Template at `templates/anchor_i2v_prompt.txt`.
6. Concat per-act with a 0.15s xfade at every seam: `ffmpeg -i a.mp4 -i b.mp4 -filter_complex "[0:v][1:v]xfade=transition=fade:duration=0.15:offset=9.85[v];[0:a][1:a]acrossfade=d=0.15[a]" -map [v] -map [a] out.mp4`. For N clips, chain N−1 xfades; offset of each is (cumulative_duration − 0.15). Helper: `scripts/concat_with_xfade.sh`.
7. Save clips to `{session}/v{N}_clips/v{N}_s{NN}.mp4`.

**Provider routing is HARDCODED to EnConvo's configured default.** Always call the exact `Route` shown in the agent's runtime `<Video_Create>` ability block. NO fallback, NO provider switching, NO trying alternate providers when one fails. If the configured default fails, stop and tell the user.

Full prompt template, lock-ins, and endframe pipeline in `references/i2v-pipeline.md`. Reusable shell script at `scripts/extract_endframe.sh`.

### Phase 3 — Concat anchor clips per ACT

When all clips in an ACT are rendered:

```bash
bash scripts/concat_clips.sh <act_dir> <output_mp4>
```

This produces `act{N}_anchor.mp4` (e.g. 40s for a 4-clip ACT). Place it inside the matching `hf_act{N}/` directory before HF compose.

### Phase 4 — Build HF overlay composition per ACT

For each ACT:

1. Copy `templates/act_composition_template.html` to `hf_act{N}/index.html`.
2. Replace scene blocks with this act's copy (Chinese), keeping right-40 panel, persistent chyron, contained shimmer, dark editorial palette.
3. Define per-scene GSAP entrances + mid-scene pulses (counters, glow text-shadow, shimmer sweeps, scale punches).
4. Lint: `hyperframes lint` — must be 0 errors.
5. Validate: `hyperframes validate --no-contrast` — must be 0 errors.
6. Render: `hyperframes render --output act{N}_composite.mp4` from inside `hf_act{N}/`.

Palette, fonts, animation library, and the full HTML/CSS/GSAP patterns in `references/hf-composition.md`. Template at `templates/act_composition_template.html`.

### Phase 4.5 — Layout audit BEFORE ship (MANDATORY — do not skip)

Lint + validate check structure, NOT visual layout. A composite can lint 0-errors and still have ugly text overflow burned into the video. **After every render, extract one frame at each scene's text peak and look at it** — never ship a composite you haven't eyeballed frame-by-frame.

1. For each scene, extract its busiest frame: `ffmpeg -y -ss <scene_mid_sec> -i act{N}_composite.mp4 -frames:v 1 -q:v 2 qa_<sec>.jpg` (one per scene).
2. Open each with `read_file` and visually confirm, per frame:
   - **No wrapping defects** — a seal/verdict/title must NOT break with a lone trailing glyph on a new line (the classic `其余凭空消失` → `失` orphan). Either it fits on its intended line count cleanly, or it must be shortened.
   - **No overflow** past the panel's right edge or out the bottom.
   - **No clipping** of text or the anchor's crown/elbow/hands at any frame edge.
   - **Alignment + CJK glyphs render** (no tofu boxes, no mis-baseline).
3. If ANY frame fails, fix the HTML/CSS (shorten copy, add `white-space:nowrap`, drop letter-spacing, resize), re-render, and re-audit. Only a clean audit unlocks Phase 5.

**Guardrail (bake into the composition, not just the audit):** seals/verdicts/card-titles get `white-space:nowrap` + short copy (a seal ≤ 8 CJK glyphs) + restrained letter-spacing (~0.14em) so they physically cannot wrap. The audit is the backstop; the CSS guardrail is the primary defense.

### Phase 5 — Ship to user for verdict per ACT

After each ACT renders, send `act{N}_composite.mp4` to the user via the bound IM channel. Wait for verdict before moving to the next ACT. Iterate ACT-by-ACT — do not batch-render all acts and then ask.

### Phase 6 — Final assembly

Only when all ACTs are individually approved:

1. **Join ACT composites with a single-pass `xfade` — NEVER the ffmpeg concat demuxer / `-c copy`.** Stream-copy concatenating two already-composited MP4s corrupts at the seam (mis-aligned keyframes → freeze/garble/desync). Re-encode through one xfade pass with a dense GOP at the ACT boundary:
   ```bash
   ffmpeg -i act1_composite.mp4 -i act2_composite.mp4 -filter_complex \
     "[0:v][1:v]xfade=transition=fade:duration=0.3:offset=<act1_dur-0.3>[v];[0:a][1:a]acrossfade=d=0.3[a]" \
     -map [v] -map [a] -c:v libx264 -r 30 -g 30 -keyint_min 30 -crf 19 \
     -preset medium -movflags +faststart -c:a aac -b:a 192k {slug}_final.mp4
   ```
   For 3+ ACTs, chain the xfades pairwise. **Trim the dangling tail:** HF composites often run ~1–2 frames longer than the anchor source; set the final offset just inside the last clip so no blank/frozen frame survives, and QA the tail by byte size (a real final frame ≈ full-size; a blank tail frame is a small fraction of it).
2. Generate or select BGM bed (see `references/audio-music.md`), seamless-loop it to length (triangular acrossfade), and **sidechain-duck it under the VO at broadcast levels** (bed −18 to −23 LUFS / 6–10 dB under voice, program ~−14 LUFS, true peak ≤ −1 dBTP — full filtergraph in `references/audio-music.md`). If the bed is from Suno, pull it via the CDN-href trick and preview-before-mix (gacha). Ship the clean (no-BGM) cut first; the BGM version is opt-in, and bed volume is a per-user taste dial (drop in ~2 dB steps on request).
3. Optional: cut a 9:16 vertical version with `crop=w=ih*9/16` + repositioned overlay.
4. Deliver final MP4(s) via the `Deliverable` tool.

## Provider Routing Discipline (HARDCODED, NO FALLBACK)

This skill ALWAYS routes media generation through EnConvo's configured default provider for each capability. There is no fallback, no provider switching, no "try X then try Y" logic. The runtime ability blocks in the agent system prompt are the single source of truth:

| Capability   | Source of truth (runtime)                    | Behavior on failure |
| ------------ | -------------------------------------------- | ------------------- |
| Image gen    | `<Image_Create>` ability block → `Route`     | Stop & report. Do not switch provider. |
| Video gen    | `<Video_Create>` ability block → `Route`     | Stop & report. Do not switch provider. |
| TTS          | `<TTS>` ability block → `Route` (rare — see below) | Stop & report. |
| OCR          | `<OCR_Action>` ability block → `Route`       | Stop & report. |
| Music / BGM  | `acestep` skill locally, OR suno.ai via browser — see `references/audio-music.md` | Stop & report. |

**TTS is intentionally suppressed in this pipeline.** All speech is baked into the i2v render. Do NOT invoke any TTS endpoint for anchor voice. TTS may only be used for non-anchor narration overlays (rare, opt-in by user).

When you read SKILL.md and the references, treat every `video_create/features/...` or `image_create/features/...` path as illustrative only. The real call uses the `Route` value from the runtime ability block.

## Anti-Patterns (caught the hard way)

- **Provider fallback or switching.** Banned. Use the configured EnConvo default exactly. If it fails, stop and report — do not silently swap providers.
- **Shimmer pseudo-element leaking onto the anchor.** Always use a real `<span class="shimmer">` inside an `overflow: hidden` panel. Never `::before` with `mix-blend-mode: screen` and no overflow lock.
- **`box-shadow: -18px 0 60px ...` on the panel.** Leaks shadow into anchor domain. Use `inset` shadows only.
- **`:nth-of-type` selectors in GSAP targets.** HF lint blocks them. Use explicit IDs or unique classes.
- **Overlapping GSAP tweens on the same property/element.** Use `overwrite: 'auto'` or move start times.
- **Missing `data-start="0"` on root composition.** Renderer cannot probe duration. Always include.
- **Forgetting CJK fonts.** macOS PingFang SC does not exist in HF's headless Chromium. Use `Noto Sans SC` + `Noto Serif SC` and include them via `<link>` to Google Fonts — HF will auto-fetch and inline.
- **Shipping a composite without a frame-by-frame layout audit.** Banned. Lint/validate pass structure, not pixels — text can wrap, overflow, or clip and still lint clean and burn straight into the MP4. A seal once shipped wrapping `其余凭空消失` with a lone `失` on line 2. ALWAYS run Phase 4.5: extract a frame per scene, eyeball each. Seals/verdicts/titles get `white-space:nowrap` + short copy (≤8 CJK glyphs) + ~0.14em tracking so they can't wrap in the first place.
- **Translating brand / tech / proper-noun terms in a Chinese cut.** Banned. OpenAI, Transformer, IEX, RBC, Reg NMS, NBBO, SOR stay English. Person names are SPOKEN in English in the VO (Brad Katsuyama, not 布拉德·胜山) and shown in English on overlays; flag the English tokens in the i2v VO block so the model pronounces them naturally. See Phase 1.
- **TTS layered on top of i2v.** Banned. Audio must be baked into i2v. Double audio = unusable.
- **Translationese VO.** Banned. A line that is grammatically correct but reads like translated English (literal verbs like 读到/冲向, English clause-chaining with 而/然后/因为, over-literal possessives like 在你自己的交易上) is a defect even if accurate. Author in the target language and run the read-aloud test per line. See the Native-Speaker Gate in `references/script-writing.md`.
- **Animating background drift.** Banned. Static plate only. Only anchor moves.
- **ffmpeg concat demuxer (`-c copy`) to join composited ACTs.** Banned. Stream-copy concatenating two already-rendered composite MP4s corrupts at the seam (freeze/garble/desync from mis-aligned keyframes). Join with a single re-encoding `xfade` pass + dense GOP (`-g 30 -keyint_min 30`). See Phase 6.
- **Dangling tail frame.** HF composites run ~1–2 frames longer than the anchor source; a naive join leaves a frozen/blank final frame. Trim inside the final xfade and QA the tail by byte size.
- **Centered zoom-crop to force the subject to the frame edges.** Banned. If the anchor's crown/elbow/fingers are clipped, or you want the body to reach an edge, REGENERATE at a larger scale — zoom-cropping a finished render only re-crops the same overflow and pushes parts further out of frame.
- **Canonical-reset every clip (v3 doctrine, deprecated).** Starting every clip from the static photo — instead of chaining endframes within an ACT — makes the i2v model hallucinate broadcaster text overlays (chyrons, CAPTAIN/BREAKING/LIVE word burn-in, lower-thirds). The model reads the still photo as "new TV broadcast, decorate it." Endframe chain reads as "continue this already-clean shot" and suppresses the hallucination. Doctrine: chain within ACT, reset at ACT boundary only.
- **Generic "no text" burn-in prompts.** Insufficient. You must name the specific hallucinated words (CAPTAIN, BREAKING, LIVE, CNBC, BLOOMBERG), the structural elements (chyrons, lower-thirds, tickers, watermarks, station IDs, show titles), AND the background sources ("monitors behind her show no text, no scrolling text, no labeled banners"). Close with "all graphics added in post — render must be 100% text-free."
- **Omitting scale lock.** Without explicit "NO zoom, NO dolly, NO scale-to-frame, head occupies same frame fraction at second 0 and second 10," the i2v model slow-zooms across the 10s clip. By second 10 the anchor's face is noticeably larger, and the endframe handoff to the next clip becomes a visible jump cut.

Full war stories + symptoms + fixes in `references/troubleshooting.md`.

## Tool & Environment Requirements

- `hyperframes` CLI at `/opt/homebrew/bin/hyperframes` (v0.6.61+). Verify with `hyperframes --version`. **If missing, see the Preflight section above** — the user must install the `hyperframes` and `hyperframes-cli` skills from the EnConvo skill library before this pipeline can run.
- `ffmpeg` 6+ for endframe extraction and concat.
- xAI credentials configured for `video_create/features/x_ai/create` (Grok Imagine Video).
- `enconvo/upload_file` available for hosting endframes.
- **Canonical default anchor image: `assets/anchor_canonical_default.png`** (Vivieen at the news desk, scarlet Saint Laurent Le Smoking peak-lapel blazer, ivory silk shell, pearl-drop gold earrings, slim Cartier Tank watch, Eurasian early-30s, moderate neckline, night-skyline studio, identity-locked to her real portrait). This is the DEFAULT anchor for every new project unless the user supplies a different reference. It is left-weighted (anchor LEFT ~55%, clean negative space RIGHT ~45%) for the standard overlay layout. Re-upload it via `enconvo/upload_file` at the start of each session to get a fresh hosted URL (tmp URLs expire), then use that URL as the canonical locked reference for the per-act and clip-3 resets.
- **Candidate anchor library (`assets/anchor_canonical_2.png`, `_3.png`, `_4.png`).** Additional pre-vetted, left-weighted anchor references in the same news-desk wardrobe/lighting DNA. At project kickoff, OFFER the user a choice between `anchor_canonical_default.png` and these candidates (show or describe them); whichever they pick becomes that project's locked canonical reference for ALL anchor points (clip 1, clip 3 re-anchor, and every ACT-boundary reset). Do not mix references within one video — one locked reference per project. `anchor_canonical_default_prev_*.png` is a timestamped backup of a previous default, not a selectable candidate.

## Reference Index

- `references/architecture.md` — the locked anchor + HF overlay pattern, scene blocking, identity lock
- `references/script-writing.md` — voice DNA, 5 字/s pacing, 10-act structure templates, hook + close patterns
- `references/i2v-pipeline.md` — i2v prompt template, lock-ins, sequential pipeline, endframe handoff (provider = EnConvo default)
- `references/hf-composition.md` — full HTML/CSS/GSAP composition recipe, palette, fonts, animation library
- `references/audio-music.md` — BGM generation: acestep skill primary, suno.ai browser-automation fallback
- `references/troubleshooting.md` — every bug we hit and how to avoid it next time
- `templates/act_composition_template.html` — reusable HF starter for any new ACT
- `templates/anchor_i2v_prompt.txt` — reusable i2v prompt skeleton
- `scripts/extract_endframe.sh` — single-clip endframe extraction
- `scripts/concat_clips.sh` — ACT-level concat
