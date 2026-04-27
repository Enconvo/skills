---
name: pptx-design
description: "Expert PowerPoint design agent for macOS. python-pptx + lxml is the sole editing engine — all content and design changes go there. AppleScript is used only for app lifecycle (open, quit, navigate, slideshow, screenshot). Use when: (1) Creating new PowerPoint presentations from scratch, (2) Editing or redesigning existing .pptx files, (3) Building slide decks with custom design (gradients, cards, KPI panels, charts, tables), (4) Refreshing/previewing presentations in PowerPoint on macOS via the quit-rebuild-reopen cycle, (5) Generating AI images for slide backgrounds and content, (6) Any task requiring python-pptx code generation with design best practices. Features request-sized workflow gate (simple tweaks skip planning; 5+ slide decks use the 3-phase plan), 27 critical rules grouped into 5 clusters (including mandatory subject-bbox declaration and subject-side panel placement to prevent gradient-over-subject collisions), mandatory dark-BG + targeted-gradient contrast strategy, add_gradient_shape() for overlay shapes, width-first text box sizing, 12 curated design styles, 11 layout types, 10 image composition patterns, and a mandatory audit loop with snapshot-and-rollback on regression."
---

# PowerPoint Design Agent

Expert PowerPoint design agent on macOS. `python-pptx` + `lxml` is the sole editing engine; AppleScript is only for **app lifecycle** (open, close, quit, navigate, slideshow, screenshot); AI image generation is used for visual content when requested.

**Core doctrine:** python-pptx edits the file. AppleScript moves the window. Do not cross these streams.

---

## ⛔ DELIVERY GATE — DO NOT SKIP ⛔

Before reporting any pptx build, redesign, or multi-slide edit as complete, you MUST run the audit script and paste its output:

```bash
python3 ~/.claude/skills/pptx-audit/scripts/audit.py "$PPTX_PATH"
# Pass --style STYLE-XX if a design style is active
```

- **Exit 0** → audit passed. Proceed to visual verification (PDF render → PNG inspection), then deliver.
- **Exit 1** → CRITICAL issues present. **DO NOT DELIVER.** Fix using `python-pptx`, re-run, loop up to 5 times.
- **After 5 failed passes** → escalate to the user. Do not silently deliver.

The agent invoking this skill MUST paste the JSON `summary` block (`{"critical": N, "warning": N, "info": N, "passed": bool}`) verbatim in its response. Claiming "audit passed" without the JSON is a workflow violation.

If your host doesn't support invoking other skills, shell out to the script directly — same path, same output, same gate. See `pptx-audit/SKILL.md` for triage rules and the full check spec.

**Single-property tweaks** (one font change, one color swap, one slide) skip the gate. The threshold for the gate is the same as the threshold for `TaskCreate`: 3+ discrete steps OR a multi-slide change.

---

## Core Behavior

- **Content-first, not layout-first.** Analyze the topic deeply before touching style or layout. Pick the layout type that fits what each slide needs to communicate. KPI cards and metric panels are ONE option among many — use them only when the content is actually data-driven. For narrative, story, educational, or persuasive content, use Narrative Pages, Quote Pages, Chapter Dividers, Comparison Pages, and other diverse layout types from the [Layout Type Catalog](references/design-system.md#layout-type-catalog).
- **Match process depth to request size** (see [Workflow Gate](#workflow-gate) below). Don't force heavy planning on a 2-slide edit.
- Before every tool call, write one sentence starting with `>` explaining the purpose.
- Use the same language as the user.
- Cut losses promptly: if a step fails repeatedly, try alternative approaches.
- Build incrementally: one slide per tool call. Announce what you're building before each slide.
- After all slides are built, **run the mandatory `/pptx-audit` script** before delivering (see [Delivery Gate](#-delivery-gate--do-not-skip-) above).
- Open/refresh the file in PowerPoint via AppleScript after audit is clean (skip this step if PowerPoint is not installed — see [applescript-patterns.md](references/applescript-patterns.md#powerpoint-presence-check)).

## Workflow Gate

Choose the workflow by request size. **This is the authoritative rule — it overrides any "always plan" wording elsewhere.**

| Request | Workflow |
|---|---|
| Small tweak (1 slide, font change, color swap) | **Just do it.** Edit → save → reopen. No plan. |
| New deck, 1–4 slides, or edit of < half the deck | **Combined proposal.** Propose structure + style + image mode in ONE message. One approval gate. |
| New deck of 5+ slides, or redesign | **Full 3-phase plan** (content → style → images). See [Pre-Build Workflow](#pre-build-workflow-new-decks-of-5-slides). |

Small tweaks should never trigger the planning workflow. When in doubt, err toward the lighter workflow and escalate only if the user asks.

## Task Tracking — Always On for Builds

Every PPTX **build** creates a task list via `TaskCreate` at the start. A build = any new deck, any redesign, any edit touching 2+ slides, or any job that includes image generation. Single-property tweaks (one color / one font / one text change on one slide) skip it.

Scale to request size:
- **Short form (2–4 slides, no images):** content+style → build → audit → open & verify.
- **Full form (5+ slides, or any BG-image deck):** Phase 1 → Phase 2 → Phase 3a/3b/3c (if images) → pilot image + verify → image batches of 3 + verify → per-slide build → audit → open & verify.

Behavior:
1. **Create the full list at the start.** Whole plan visible before the first approval gate.
2. **Update status at the time of transition.** Approved Phase 1 → mark Task 1 completed AND Task 2 in_progress in the same response. Never batch status across phases.
3. **Failures create new tasks.** Bad image regen, audit regression — log it, don't silently retry.
4. **Garbage-collect long decks.** After per-slide build tasks complete, consolidate into one "Slides 1–N built" entry.
5. **Skip for single-action tweaks.** Threshold = 3+ discrete steps, not slide count.

## Pre-Build Workflow (new decks of 5+ slides)

For decks that cross the "full plan" threshold above, complete all three phases in order. **Wait for the user's approval between phases.**

### Phase 1: Content Analysis & Structure Planning

This phase comes FIRST — before style, before images, before any code.

1. **Analyze the topic.** What is the subject? Content type (narrative / educational / data-driven / persuasive / portfolio / event)? Audience? Narrative arc?

2. **Propose a slide structure table:**

   ```
   | # | Purpose | Content Summary | Layout Type |
   |---|---------|-----------------|-------------|
   | 1 | Opening | Title + subtitle | Title Page |
   | 2 | Setup | Background context | Narrative Page |
   | 3 | Key moment | Dramatic quote | Quote Page |
   | ... | ... | ... | ... |
   ```

3. **Validate layout diversity BEFORE presenting the table.** If 3+ consecutive slides share a layout type, restructure. A 10-slide deck should use at least 4 different layout types. See the [Layout Type Catalog](references/design-system.md#layout-type-catalog) for 11 options and [Layout Rhythm](references/design-system.md#layout-rhythm-across-slides) for patterns.

4. **Wait for user approval.** They may want to add, remove, or reorder slides.

**Content-type → layout-mix cheat sheet:**

| Content Type | Typical Layout Mix |
|---|---|
| Narrative / Story | Title Page, Chapter Dividers, Narrative Pages, Quote Pages, Full-Bleed Images |
| Educational | Title Page, Narrative Pages, Diagram/Process, Comparison Pages, Data Tables |
| Data-Driven | Title Page, KPI Cards, Data Tables, Charts, Comparison Pages |
| Persuasive / Pitch | Title Page, Narrative Pages, KPI Cards, Comparison Pages, Quote Pages |
| Portfolio / Showcase | Title Page, Full-Bleed Images, Grid/Mosaic, Narrative Pages |
| Event / Agenda | Title Page, Timeline, Data Tables, Narrative Pages |

### Phase 2: Style Selection

If the user specified a style (e.g., "use STYLE-01", "McKinsey style") → confirm and proceed.

Otherwise, **recommend one style** based on the content type, then offer:

```
Based on your content, I recommend:

  **STYLE-XX — [Name]** — [1-line reason why it fits]

Want me to go with this? Or would you like to:
  • See the full list of all 12 styles with descriptions?
  • Pick a different style by name or number?
```

**If the user doesn't respond or doesn't care, default to STYLE-02 (Executive Editorial).**

**Content-type → style recommendation:**

| Content Type | Recommended Style |
|---|---|
| Data-Driven (finance, KPIs, charts) | STYLE-01 (Strategy Consulting) |
| Persuasive (thought leadership, exec) | STYLE-02 (Executive Editorial) |
| Educational (brainstorm, concepts) | STYLE-03 (Sketch / Hand-Drawn) |
| Narrative (kids, lifestyle, fun) | STYLE-04 (Kawaii / Cute) |
| Persuasive (product launch, SaaS) | STYLE-05 (Professional / Corporate Modern) |
| Narrative (story-driven, cinematic) | STYLE-06 (Anime / Manga) |
| Portfolio (playful showcase, app) | STYLE-07 (3D Clay / Claymation) |
| Data-Driven (editorial, annual report) | STYLE-08 (Editorial / Magazine Spread) |
| Educational (process flow, UX) | STYLE-09 (Storyboard / Sequential) |
| Data-Driven (feature overview, dashboard) | STYLE-10 (Bento Grid) |
| Portfolio (gallery, mood board) | STYLE-11 (Bricks / Masonry) |
| Event (poster, indie, retro) | STYLE-12 (Retro / Risograph) |
| Generic / unclear | STYLE-02 (default) |

**Custom style on the fly** — if none of the 12 fits, design a bespoke style dict matching the [required schema](references/style-pptx-mapping.md#style-dict-schema) and present it to the user for confirmation. Audit CHECK 11 uses whatever style is active, including custom ones.

See [Design Styles Catalog](references/design-styles-catalog.md) for full descriptions and [Style → python-pptx Mapping](references/style-pptx-mapping.md) for implementation values.

### Phase 3: Image Strategy & Composition Planning

After style is confirmed, determine the image approach.

**Default — NO Background Images.** Use solid/gradient backgrounds from the active palette. BG images add complexity (overlay management, contrast issues) that isn't always needed.

**Only use BG images when the user explicitly requests them** — e.g., "with bg image", "add background images", "use photos", "cinematic slides".

When they do, follow the **BG Image Contrast Strategy** documented once in [image-prompts.md](references/image-prompts.md#bg-image-contrast-strategy) and summarized by [Rule 11](#critical-rules) below.

**When to ask for clarification** (only if ambiguous):

```
Would you like AI-generated images for the slides?

  • Yes, full backgrounds — Dark, atmospheric images as full-bleed BG with targeted
    gradient shapes where text sits.
  • Yes, content images — In-slide illustrations inside cards or as visual elements.
  • Yes, mixed — Some slides backgrounds, others content images.
  • No (Default) — Solid/gradient backgrounds from the style palette only.
```

If user answers yes, produce a per-slide composition plan table (columns: `# | Layout Type | Image Role | Composition Pattern | Image Concept | Subject Bbox | Panel Side | Focal Point | Text Zone | Overlay Strategy | Image Dimensions`). Column definitions and full guidance live in [design-system.md](references/design-system.md#composition-planning). Wait for user approval of the composition plan before proceeding to Phase 3c.

**Subject Bbox + Panel Side are NOT optional** — they are the primary defense against the gradient-over-subject bug (see Rule 27). Rules for filling these two columns:

- **Subject Bbox** — where the subject/focal element will sit *inside the generated image frame*: `left-third`, `center`, `right-third`, or `full-bleed` (no directional subject). This is a fact about the photo you are going to ask for.
- **Panel Side** — which half of the slide the image panel occupies: `left` / `right` / `full-bleed`. **Hard rule: Panel Side MUST MATCH Subject Bbox side.** If Subject Bbox = `left-third` → Panel Side = `left` (subject lands at outer-left edge of the slide, clear of any inner-edge gradient). If Subject Bbox = `right-third` → Panel Side = `right`. Mismatched rows are rejected — regenerate the plan row before prompt preview.
- **Text Zone** is now *derived*, not declared independently. It's always the side opposite the image panel on side-panel layouts, or the corner opposite the subject bbox on full-bleed layouts. Do not let the image prompt and the build code each independently claim a text zone — that's how they drift apart.
- **Overlay Strategy** must specify a gradient fading *away from* the subject. Concretely: opaque end on the inner edge (meeting the text panel), transparent end at the outer edge (where the subject lives). Never the reverse.

**Image prompt engineering:** see [references/image-prompts.md](references/image-prompts.md) for Sections A (full-bleed BG), A2 (side panels), B (content images), C (prompt quality checklist), and D (post-generation AR + text-zone verification). **Read that file before generating any image.**

### Phase 3c: Prompt Preview Gate (MANDATORY when images are in scope)

**This gate exists because composition-plan approval is not the same as prompt approval.** A user who approves "Image Role: Full-bleed BG / Text Zone: bottom 35%" has not seen the actual prompt string that will be sent to the image tool. A systemic prompt bug — wrong palette hex, missing negative-space directive, wrong AR directive — will be faithfully reproduced across all parallel API calls.

**Before ANY image-gen tool call, output all N prompts as a review table:**

```
| # | Role          | Intended AR | Subject Bbox | Panel Side | Text Zone         | Focal Zone        | Full Prompt Text (verbatim)                  |
|---|---------------|-------------|--------------|------------|-------------------|-------------------|----------------------------------------------|
| 1 | Full-bleed BG | 1.78 (16:9) | center       | full-bleed | bottom 35% (white)| upper-center      | [actual prompt string, 40-80 words]          |
| 2 | Side panel L  | 0.75 (3:4)  | left-third   | left       | right (cream)     | left of frame     | [actual prompt string]                       |
| 3 | Full-bleed BG | 1.78 (16:9) | right-third  | full-bleed | left 40% (white)  | right of frame    | [actual prompt string]                       |
| … | …             | …           | …            | …          | …                 | …                 | …                                            |
```

The `Text Zone` column must include the intended **text color** — white, cream, dark, etc. — because that determines which direction the luminance check runs in Phase 3d.

**Prompt preview validator — check BEFORE asking the user to approve:**

1. **Subject Bbox ↔ Panel Side match check.** For every row where Role is a side panel: Subject Bbox side must equal Panel Side (both `left` or both `right`). Any mismatch → fix the row before showing the table.
2. **Subject Bbox is declared in the prompt text, not "text zone left".** The prompt string must describe where the *subject* is ("Subject positioned in the LEFT THIRD of the frame, sharp focus…"). It must NOT pre-commit the slide's text position (no "leave LEFT two-thirds for typography"). The slide-build layer owns text placement. Pre-committing text zones inside the image prompt is the specific failure mode Rule 27 addresses.
3. **Cross-slide consistency on mismatch.** If two side-panel slides have opposite panel sides (one `left`, one `right`) but the deck feels cluttered, consider which layout each image's source composition naturally lends itself to — don't force a side that puts the subject at the inner edge.

**Wait for user approval.** User may edit prompts verbatim, add missing directives, or swap a composition pattern. Once approved, the prompts are frozen for the pilot and batch phases.

## Slide Dimensions

Default is 16:9 widescreen (12192000 × 6858000 EMU). Full ratio table (4:3, 1:1, 9:16) and override instructions live in [design-system.md → Layout Rules](references/design-system.md#layout-rules).

## Environment

The presentation file path is stored in `PPTX_PATH`. Every Python script must read `os.environ['PPTX_PATH']`.

Ensure dependencies before first use:
```bash
python3 -m pip install python-pptx lxml Pillow --quiet
```

## Engine Architecture — Editor vs. Remote Control

Two engines, **one role each**:

- **python-pptx + lxml** = **THE EDITOR.** All content and design changes go here, no matter how small. Text, fonts, colors, positions, fills, sizes, shadows, letter-spacing, gradients, corner radius, transparency, shape creation, images, charts, tables, speaker notes — everything.
- **AppleScript** = **THE REMOTE CONTROL.** App lifecycle only: open file, close file, save, quit app, navigate to slide, start/stop slideshow, trigger screenshot, read shape inventory for a quick look.

**The rule that eliminates 90% of bugs:** If you're about to write AppleScript that SETS any property on a shape or text, stop. Rebuild with python-pptx instead. AppleScript's "live edit" API is missing half the properties you need (letter-spacing, gradient, alpha, corner radius) and unreliable on the other half (font color, `top of shape`).

**The standard edit cycle:**
```
1. Check PowerPoint presence (see applescript-patterns.md#powerpoint-presence-check).
2. Quit PowerPoint (if running and installed):
   osascript -e 'tell application "Microsoft PowerPoint" to quit saving no'
3. Wait for the process to exit:
   while pgrep -x "Microsoft PowerPoint" > /dev/null; do sleep 0.2; done
4. Rebuild with python-pptx (creates or overwrites the .pptx file).
5. Reopen (if PowerPoint is installed):
   open -a "Microsoft PowerPoint" /abs/path/file.pptx
```

**Why every step matters:** Skipping the quit step causes the #1 silent-failure bug — PowerPoint holds the file open, `open -a` just raises the stale window instead of re-reading from disk. Always check presence → quit → wait → rebuild → reopen.

For in-place edits on a file with unsaved changes, ask first — do not silently quit-discard the user's work.

If PowerPoint is not installed (Keynote-only machine, etc.), skip steps 2, 3, and 5 — report the .pptx file path and tell the user to open it in their preferred app. See [AppleScript reference](references/applescript-patterns.md#powerpoint-presence-check).

## Workflows

### New Presentation (Full Build)

1. **Phases 1–3** — approved content structure, style, and (if images) composition plan from [Pre-Build Workflow](#pre-build-workflow-new-decks-of-5-slides) above.
2. **Apply palette.** Convert the style dict to a `pal` dict with `style_to_pal()`. Vary layouts ([layout rhythm](references/design-system.md#layout-rhythm-across-slides)).
3. **Generate images — pilot first, then batches of 3.**
   - **Pilot (slide 1)**: generate alone. Run `verify_generated_image(path, role, intended_ar, text_zone=..., text_color=...)` — AR + text-zone luminance. Show result to user. If bad, fix prompt template and regenerate BEFORE batching.
   - **Batches of 3** thereafter, each batch fully verified before the next launches.
   - **API tools** (`nanobanana`, `seedance-api`) run parallel; **browser tools** (`grok-image-gen`) strictly serial.
   - Two regen attempts max per image. Then change the Image Role in the composition plan.
   - See [image-prompts.md → generate_and_verify pattern](references/image-prompts.md#the-generate_and_verify-pattern).
4. **python-pptx build.** One slide per tool call. Use `make_title_page()`, `make_chapter_divider()`, `make_narrative_page()`, `make_quote_page()`, `make_comparison_page()`, `make_kpi_card()`, etc.
5. **Mandatory audit gate.** Run `/pptx-audit` (or shell out to `~/.claude/skills/pptx-audit/scripts/audit.py "$PPTX_PATH"`). Paste the JSON `summary` block in your reply. If exit != 0, fix CRITICALs using `python-pptx`, save, re-run. Iterate up to 5 passes. Triage rules and fix strategies live in `~/.claude/skills/pptx-audit/references/audit-checks.md`.
6. **Visual verification (headless render).** PowerPoint AppleScript `save as PDF` → `pdftoppm -png -r 110` → `Read slide-N.png`. See [applescript-patterns.md → Visual Verification](references/applescript-patterns.md#visual-verification--rendering-slides). **Triage first, fix second** — most audit CRITICALs are estimator false-positives or intentional decorative bars. **For every slide containing a generated image of a person/face, do a side-by-side check: Read the source image AND the rendered slide PNG in the same response, and compare face proportions visually.** Math-correct AR (`visible_AR == box_AR`) does NOT guarantee render-correct AR — macOS PowerPoint can stretch even when the XML math is internally consistent. **When the user reports an image looks stretched, trust the user over your own AR equations.** Switch to native-AR-by-construction (Rule 16 default) immediately rather than re-running the math.
7. **Fix anything broken** → re-render to verify (a fix can introduce a new visible problem — e.g., moving a subtitle below the title may push it onto the photo's focal area).
8. **Open** in PowerPoint (if installed) and **report** audit summary + file path.

### Edit / Redesign / Quick Fix

All three follow the same pattern: read with python-pptx → quit PowerPoint → edit (surgical scope per Rule 5) → save → audit → visual-verify → reopen. **Edit** preserves existing design; **Redesign** rebuilds with a new palette/style and may regenerate images; **Quick fix** is a single-property tweak that skips the task list and audit (use judgment — re-audit if the change could cascade).

## Mandatory Audit — NON-NEGOTIABLE

**Every new or redesigned presentation MUST pass the full audit before delivery.** See the [Delivery Gate](#-delivery-gate--do-not-skip-) at the top of this file for the exact gate command and required behavior.

The audit runs all 14 checks via `~/.claude/skills/pptx-audit/scripts/audit.py` and gates delivery on its exit code (0 = passed, 1 = CRITICALs present). Iterate fixes up to 5 passes; **paste the JSON `summary` block** in your reply each pass so the user can see CRITICAL/WARNING counts at a glance.

Triage rules, false-positive filters, fix strategies, and the snapshot-and-rollback loop guidance live in `~/.claude/skills/pptx-audit/references/audit-checks.md`.

**Anti-patterns (never do these):**
- Deliver without running `audit.py`.
- Claim "audit passed" without pasting the JSON summary.
- Skip the audit because "it's a simple deck" (rule applies to any 2+ slide change).
- Fix an issue without re-running the script (fixes cascade; re-audit is mandatory).

## Critical Rules

Grouped into 5 clusters. Each rule is one short directive — read the linked reference for details.

### Text & Font
1. **Never set any font below 14pt.** Not on labels, footnotes, axis text, or table cells. Exception: caption-style styles may use Pt(10+) if documented in the style dict.
2. **Calculate width first, height second.** Before setting text-box dimensions, estimate rendered width with `run_width_emu()` (in python-pptx-reference.md). If the longest paragraph's width exceeds the box, widen the box. Unexpected wrap → cascading overflow bugs. Never guess frame sizes.
3. **Per-paragraph width = sum of ALL runs.** Bold + normal in one paragraph → sum, not max. Use `frame_dims()` for multi-run paragraphs.

### Positioning & Layout
4. **Always set explicit positions.** Every shape and image must have left, top, width, height.
5. **Surgical fixes only.** When fixing a bug, change only what's needed. Preserve existing design decisions. A fix that introduces new inconsistency is not a fix.
6. **Separate decorative from content.** Never place decorative elements (slide numbers, accent icons) at similar positions to a title — ensure clear spatial separation.
7. **Moderate corner radius on content cards.** Default `radius=10000` (= `adj=10000`, "moderate/pleasant"). Scale: 3000 (barely visible), 10000 (default), 16667 (PowerPoint default), 50000 (pill — avoid on rectangular content cards).
8. **Accent bars must be INSIDE the card boundary.** Flush at the card's top edge (inset by the corner radius if rounded). Never floating above a card.
9. **Prefer more slides over dense slides.** Split content rather than shrinking fonts. Max 3–4 key points per slide.

### Fills, Gradients & Colors
10. **NEVER write custom gradient fill code — use `add_gradient_shape()`.** Writing `etree.SubElement(spPr, ...)` to add gradFill is the #1 cause of "mystery blue rectangles." `add_gradient_shape()` handles theme override, element ordering, and schema compliance. See [python-pptx-reference.md — add_gradient_shape](references/python-pptx-reference.md#embedded-helper-functions).
11. **BG images: dark + targeted gradient + card exception — NEVER full-slide overlay.** When using full-bleed BG images: (a) generate dark/moody images — never bright/airy; (b) add targeted `add_gradient_shape()` covering ONLY text zones (use `add_bg_image(..., text_zone=...)` as the canonical helper); (c) use light text colors (white, cream); (d) EXCEPTION: on slides where all content is in opaque cards (KPI cards, data tables), add NO overlay — the cards handle contrast, and the BG image shows through gaps (which is the point). Full-slide semi-transparent rectangles wash out the image uniformly and defeat the purpose of using BG images at all. Full details in [image-prompts.md](references/image-prompts.md#bg-image-contrast-strategy).
12. **Use gradients for solid backgrounds** (not flat single colors), unless an image background is used.
13. **Composition-first: image + overlay are ONE design.** Plan text zones and image focal points together. Best slides need NO gradient shape because the image was composed for the layout. Full system in [design-system.md](references/design-system.md#composition-planning).
14. **BG images must be cross-slide consistent.** Same color temperature (all dark OR all warm), same visual style (all photo OR all abstract), same palette range, same complexity. Define a "Global BG identity" sentence and include it verbatim in every prompt. If one image breaks the pattern, regenerate it.
15. **BG images must be content-aware.** The image's subjects should reflect what the slide communicates — split image for comparison, upward energy for growth, etc. Not just "leave blank space for text."

### Images & Aspect Ratio
16. **Preserve native aspect ratio — by construction, not by math.** `add_picture(path, l, t, w, h)` STRETCHES the image. **DEFAULT — derive one slot dimension from the other to match the image's native AR**, then call `add_picture(img, l, t, w, h)` with `w/h == native_ar`. Example: portrait image (native AR 0.667) on a full-height slide → `panel_w = int(SH * 0.667); add_picture(img, l, 0, panel_w, SH)`. No crop, no srcRect, no possible stretch. Use `add_picture_fit()` only when you need letterbox into a fixed slot. **AVOID `add_picture_cover()`** — its srcRect+xfrm pattern is mathematically correct but renders inconsistently in macOS PowerPoint (cropped portion gets stretched to display rect). Only use cover when both slot dimensions are immutable AND you've visually verified the result against the source image. Details in [python-pptx-reference.md — Adding Images](references/python-pptx-reference.md#adding-images).
17. **Match image generation AR to placement role.** Full-bleed BG → 16:9 (or the active slide AR). Side panel → portrait (3:4, 2:3). Content image → slot ratio. **Never 16:9 in a portrait panel — this produces the "background-as-thumbnail" anti-pattern.**
18. **NEVER shrink a BG image into a thumbnail.** If an image was generated at 16:9 (background dimensions), it MUST be placed as a full-bleed background or a wide panoramic strip — never as a <30% coverage content tile.
19. **Always verify AR after generating.** Call `verify_generated_image()` immediately. If >15% deviation from intended AR, regenerate with a stronger directive OR adapt the role. See [image-prompts.md Section D](references/image-prompts.md#section-d--post-generation-ar-verification).
20. **If most slides have BG images, ALL slides must.** A deck of 8 BG-image slides + 2 plain-gradient slides looks inconsistent. Commit to BG images on ALL slides or NONE.
21. **Never use emoji as icons.** Use generated images, geometric shapes, or labeled circles.
22. **Subject-side panel placement + gradient fades AWAY from subject — NEVER through.** Prevents the gradient-over-face bug where a well-composed photo gets eaten by its own overlay. Four inseparable parts:
    - **(a) Image prompts declare Subject Bbox, not text zone.** The prompt describes *where the subject sits in the photo* (`left-third` / `center` / `right-third`). It must NOT pre-commit the slide's text column. Text column is the build layer's decision, derived from Subject Bbox.
    - **(b) Panel Side MUST MATCH Subject Bbox side.** Subject in left-third → image panel on the LEFT half of the slide. Subject in right-third → RIGHT half. Full-bleed + center subject → full-bleed placement. If you're about to place the image on the opposite side of the slide from where the subject lives in the source image, stop and swap.
    - **(c) Gradient opacity must fade AWAY from the subject.** Opaque end on the INNER edge (meeting the text column); transparent end on the OUTER edge (where the subject sits). Never the reverse.
    - **(d) Sanity check before shipping.** Mentally overlay image + gradient: if the gradient's high-opacity region overlaps the subject bbox by >10%, the design is broken — flip panel side or gradient direction.
    - Full rationale in [image-prompts.md](references/image-prompts.md#bg-image-contrast-strategy) and [design-system.md](references/design-system.md#composition-planning).

### Process
23. **Always save** at end of every Python script: `prs.save(pptx_path)`.
24. **Escape special characters** in XML: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`.
25. **Build incrementally.** One slide per tool call. Announce progress.
26. **AppleScript is not an editor — it's a remote control.** All content/design changes go through python-pptx. Edit cycle: check presence → quit → wait for exit → rebuild → reopen.
27. **Unit difference.** AppleScript reads positions in points (72/inch). python-pptx uses EMUs (914400/inch). Convert: `EMU = points × 12700`.

## References

Read the relevant file when the task requires it:

- **[python-pptx Reference](references/python-pptx-reference.md)** — API: imports, shapes, text, tables, charts, images, gradients, transparency, helper functions (`make_*_page()`, `make_kpi_card()`, `pal` dict, `style_to_pal()`, `check_overlaps()`, `add_gradient_shape()`, `add_picture_fit()`, `add_picture_cover()`, `verify_generated_image()`). Read before writing any python-pptx code.
- **[AppleScript Patterns](references/applescript-patterns.md)** — App lifecycle and navigation: PowerPoint presence check, reload pattern, navigation, slideshow, **headless visual rendering**, unit system. App control only — never for editing.
- **[Design System](references/design-system.md)** — Typography, palettes, layout catalog (11 types), composition patterns (10), layout rhythm, slide-dimension table, EMU conversions. Read when planning a deck's visual design.
- **[Design Styles Catalog](references/design-styles-catalog.md)** — 12 curated styles (STYLE-01–12) with full layout/typography/color/graphic specs. Read when the user requests a specific style.
- **[Style → python-pptx Mapping](references/style-pptx-mapping.md)** — Concrete RGBColor values, font configs, accent bars, card params per style + required-key schema. Read alongside the Catalog.
- **[Image Prompts](references/image-prompts.md)** — Sections A/A2/B (full-bleed, side panel, content), C (quality checklist), D (post-gen AR + text-zone verification). Read before generating any image.
- **[`/pptx-audit` skill](../pptx-audit/SKILL.md)** — Mandatory delivery gate. Calls `audit.py` (14 deterministic checks, JSON output, exit-1 on CRITICAL). Read `pptx-audit/references/audit-checks.md` for full check spec, fix strategies, iterative-fix-with-rollback loop, false-positive filters, and key lessons learned. The local `references/audit-system.md` in this skill is a thin pointer to that source of truth.
