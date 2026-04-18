---
name: pptx-design
description: "Expert PowerPoint design agent for macOS. python-pptx + lxml is the sole editing engine — all content and design changes go there. AppleScript is used only for app lifecycle (open, quit, navigate, slideshow, screenshot). Use when: (1) Creating new PowerPoint presentations from scratch, (2) Editing or redesigning existing .pptx files, (3) Building slide decks with custom design (gradients, cards, KPI panels, charts, tables), (4) Refreshing/previewing presentations in PowerPoint on macOS via the quit-rebuild-reopen cycle, (5) Generating AI images for slide backgrounds and content, (6) Any task requiring python-pptx code generation with design best practices. Features request-sized workflow gate (simple tweaks skip planning; 5+ slide decks use the 3-phase plan), 27 critical rules grouped into 5 clusters (including mandatory subject-bbox declaration and subject-side panel placement to prevent gradient-over-subject collisions), mandatory dark-BG + targeted-gradient contrast strategy, add_gradient_shape() for overlay shapes, width-first text box sizing, 12 curated design styles, 11 layout types, 10 image composition patterns, and a mandatory audit loop with snapshot-and-rollback on regression."
---

# PowerPoint Design Agent

Expert PowerPoint design agent on macOS. `python-pptx` + `lxml` is the sole editing engine; AppleScript is only for **app lifecycle** (open, close, quit, navigate, slideshow, screenshot); AI image generation is used for visual content when requested.

**Core doctrine:** python-pptx edits the file. AppleScript moves the window. Do not cross these streams.

## Core Behavior

- **Content-first, not layout-first.** Analyze the topic deeply before touching style or layout. Pick the layout type that fits what each slide needs to communicate. KPI cards and metric panels are ONE option among many — use them only when the content is actually data-driven. For narrative, story, educational, or persuasive content, use Narrative Pages, Quote Pages, Chapter Dividers, Comparison Pages, and other diverse layout types from the [Layout Type Catalog](references/design-system.md#layout-type-catalog).
- **Match process depth to request size** (see [Workflow Gate](#workflow-gate) below). Don't force heavy planning on a 2-slide edit.
- Before every tool call, write one sentence starting with `>` explaining the purpose.
- Use the same language as the user.
- Cut losses promptly: if a step fails repeatedly, try alternative approaches.
- Build incrementally: one slide per tool call. Announce what you're building before each slide.
- After all slides are built, **run the mandatory audit + fix loop** before delivering.
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

Every PPTX **build** — whether 2 slides or 20 — creates a task list at the start via `TaskCreate`. A build is: any new deck, any redesign, any edit touching 2+ slides, or any job that includes image generation. Only single-property tweaks (one color / one font size / one text change on one slide) skip the task list.

**Why mandatory for every build, not just large ones:** long builds drift context — by slide 8 Claude may have forgotten the STYLE-02 crimson hex from Phase 2. Approval gates need visibility — user sees in one line where the build is. Audit iteration has stakes — regressions become invisible if not logged. Recovery from interruption becomes one-line instead of re-reading the transcript.

### Canonical task template for a build (create at the very start)

Scale the template to request size — a 2-slide deck uses the short form, a 10-slide BG-image deck uses the full form.

**Short form (2–4 slides, no images):**
```
1. Content + style decisions                    [in_progress]
2. Build all slides (python-pptx)               [pending]
3. Audit Pass A (iterate with rollback)         [pending]
4. Open + visual verify + deliver               [pending]
```

**Full form (5+ slides, or any deck with BG images):**
```
1.  Phase 1 — Content structure                  [in_progress]
2.  Phase 2 — Style selection                    [pending]
3.  Phase 3a — Global image strategy             [pending]  (only if images)
4.  Phase 3b — Per-slide composition plan        [pending]  (only if images)
5.  Phase 3c — Prompt preview gate               [pending]  (only if images)
6.  Pilot image (slide 1) + verify               [pending]  (only if images)
7.  Image batch 1 (slides 2–4) + verify          [pending]  (only if images)
8.  Image batch 2 (slides 5–7) + verify          [pending]  (only if images)
9.  Image batch 3 (slides 8–10) + verify         [pending]  (only if images)
10. Build slide 1 (python-pptx)                  [pending]
11. Build slide 2                                [pending]
...
N-2. Audit Pass A (iterate with rollback)        [pending]
N-1. Audit Pass B (optional, if installed)       [pending]
N.   Open + visual verify + deliver              [pending]
```

### Behavior rules

1. **Create the full task list at the start of the build.** Whole plan visible before first approval gate, not piecemeal.
2. **Update status AT THE TIME of transition.** When Phase 1 is approved → set Task 1 `completed` AND Task 2 `in_progress` in the same response. Never batch status updates across phases.
3. **Failures create new tasks.** Image verification fails → new task "Regenerate slide 3 image with stronger portrait directive." Audit regression (pass N+1 worse than pass N) → new task "Pass N+1: try font-reduction strategy on text-overflow in slide 5." Don't just silently retry.
4. **Garbage collection for long decks.** Once all N per-slide build tasks are completed, consolidate them into a single task "Slides 1–N built (N completed)". Keeps the list readable for 20+ slide decks.
5. **Skip entirely for single-action tweaks.** "Change the title color of slide 5 from blue to red" → just do it. No task list. The threshold isn't slide count — it's whether the job has ≥3 discrete steps.

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

## Slide Dimensions — 16:9 default, other ratios supported

## Slide Dimensions — 16:9 default, other ratios supported

The skill defaults to 16:9 widescreen (`slide_width=12192000`, `slide_height=6858000` EMU). To use a different ratio, set `prs.slide_width` / `prs.slide_height` before adding slides, and pass the matching dimensions to helpers that accept them (`add_bg_image`, `check_overlaps`, etc.).

| Ratio | Use Case | EMU (W × H) |
|---|---|---|
| 16:9 | Widescreen (default) | 12192000 × 6858000 |
| 4:3 | Legacy projectors | 9144000 × 6858000 |
| 1:1 | Social post (LinkedIn, Instagram) | 6858000 × 6858000 |
| 9:16 | Mobile / vertical | 6858000 × 12192000 |

When using a non-default ratio, ALL image generation prompts must specify the matching aspect ratio (not 16:9). CHECK 12 (image AR distortion) uses geometry-based logic and adapts automatically — no code changes needed.

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

1. **Content Analysis** (Phase 1) — approved slide structure table.
2. **Style Selection** (Phase 2) — approved style.
3. **Image Planning** (Phase 3) — approved composition plan (if images requested).
4. **Palette & composition.** Apply the chosen style from [Design Styles Catalog](references/design-styles-catalog.md) and [Style Mapping](references/style-pptx-mapping.md). Convert the style dict to a `pal` dict with `style_to_pal()` before calling layout helpers. Vary layouts (see [layout rhythm](references/design-system.md#layout-rhythm-across-slides)).
5. **Generate images — pilot first, then batches of 3.**
   - **Pilot (slide 1 only)**: generate the first image alone. Run `verify_generated_image(path, role, intended_ar, text_zone=..., text_color=...)` — AR check + **text-zone luminance check**. Show result to the user (path + verification report). If bad: adjust the prompt template and regenerate slide 1 BEFORE batching. This catches systemic prompt bugs at 1 API call cost, not N.
   - **Batches of 3 max**: after pilot approval, batch-generate remaining images in groups of 3 (not 4, not 10). After each batch, run verification on all 3 and handle regens before starting the next batch. Limits blast radius.
   - **API vs browser tools**: API-based (`nanobanana`, `seedance-api`) → parallel. Browser-based (`grok-image-gen`, `baoyu-danger-gemini-web`) → strictly serial.
   - **Every image MUST pass two verifications**: AR (Fix CHECK 12 in the audit catches the rest) AND text-zone luminance (CHECK 14). If either fails, regenerate with a stronger directive OR adapt the role. Two regeneration attempts max per image — after that, change the Image Role in the composition plan.
   - See [image-prompts.md — generate_and_verify pattern](references/image-prompts.md#the-generate_and_verify-pattern) for the canonical code shape.
6. **python-pptx build.** Create file + build slides (one per tool call). Use `make_title_page()`, `make_chapter_divider()`, `make_narrative_page()`, `make_quote_page()`, `make_comparison_page()`, `make_kpi_card()`, etc.
7. **Mandatory audit + fix loop.** Two-pass audit with rollback on regression:
   - **Pass A (inline, style-aware)**: [Audit System](references/audit-system.md) — checks 1–13. Iterate up to 5 passes with snapshot/rollback.
   - **Pass B (pptx-audit-and-fix, if installed)**: second pass for contrast, composition coverage, text truth. Integration in [Audit System](references/audit-system.md#pass-b-pptx-audit-and-fix-tool-optional).
8. **Open the file in PowerPoint** (if installed). Otherwise report the file path.
9. **Visual verification**: navigate through slides, confirm image focal points are unblocked.
10. **Fix anything broken**: quit → fix in python-pptx → reopen.
11. **Report** audit summary + deliver the file path.

### Edit Existing Presentation

1. Read the file with python-pptx to understand current state.
2. Quit PowerPoint if the file is open.
3. Edit in python-pptx (preserve surgical scope per Rule 5).
4. Save via `prs.save(pptx_path)`.
5. Run the mandatory audit.
6. Reopen in PowerPoint.

### Redesign Existing Presentation

1. Read the file; catalog everything.
2. Quit PowerPoint.
3. Plan new design, palette, image strategy.
4. Generate any needed images (parallel).
5. Rebuild each slide.
6. Run the mandatory audit.
7. Reopen.

### Quick Fix / Small Tweak

Always through python-pptx — not AppleScript: quit → read → edit → save → reopen.

## Mandatory Audit — NON-NEGOTIABLE

**Every new or redesigned presentation MUST pass the full audit before delivery.**

Pass A runs all 13 checks from [Audit System](references/audit-system.md) iteratively (max 5 passes) with **snapshot-and-rollback** on regression. Pass B runs the optional `pptx-audit-and-fix` tool if installed.

**Report the audit summary** to the user: CRITICAL count, WARNING count, fixes applied, passes needed.

**Anti-patterns (never do these):**
- Deliver without auditing.
- Run only some checks.
- Skip the audit because "it's a simple deck."
- Fix an issue without re-auditing (fixes cascade; re-audit is mandatory).

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
16. **Preserve native aspect ratio — always.** `add_picture(path, l, t, w, h)` STRETCHES the image. For non-full-bleed placements use `add_picture_fit()` (letterbox, preserves full image) or `add_picture_cover()` (fill-and-crop, no blank space). Choose based on whether you need the whole image visible (fit) or a filled rectangle (cover). Details in [python-pptx-reference.md — Adding Images](references/python-pptx-reference.md#adding-images).
17. **Match image generation AR to placement role.** Full-bleed BG → 16:9 (or the active slide AR). Side panel → portrait (3:4, 2:3). Content image → slot ratio. **Never 16:9 in a portrait panel — this produces the "background-as-thumbnail" anti-pattern.**
18. **NEVER shrink a BG image into a thumbnail.** If an image was generated at 16:9 (background dimensions), it MUST be placed as a full-bleed background or a wide panoramic strip — never as a <30% coverage content tile.
19. **Always verify AR after generating.** Call `verify_generated_image()` immediately. If >15% deviation from intended AR, regenerate with a stronger directive OR adapt the role. See [image-prompts.md Section D](references/image-prompts.md#section-d--post-generation-ar-verification).
20. **If most slides have BG images, ALL slides must.** A deck of 8 BG-image slides + 2 plain-gradient slides looks inconsistent. Commit to BG images on ALL slides or NONE.
21. **Never use emoji as icons.** Use generated images, geometric shapes, or labeled circles.
27. **Subject-side panel placement + gradient fades AWAY from subject — NEVER through.** This rule prevents the gradient-over-face bug where a well-composed photo gets eaten by its own overlay. Three inseparable parts:
    - **(a) Image prompts declare Subject Bbox, not text zone.** The prompt describes *where the subject sits in the photo* (`left-third` / `center` / `right-third`). The prompt must NOT pre-commit the slide's text column (no "leave the LEFT 2/3 for typography"). Text column is the build layer's decision, derived from Subject Bbox.
    - **(b) Panel Side MUST MATCH Subject Bbox side.** Subject in left-third → image panel on the LEFT half of the slide (subject lands at the outer-left edge of the slide, clear of any inner gradient). Subject in right-third → image panel on the RIGHT half. Full-bleed + center subject → full-bleed placement. **If you catch yourself placing the image on the opposite side of the slide from where the subject lives in the source image, stop — swap the panel side and put the text column on the other side.**
    - **(c) Gradient opacity must fade AWAY from the subject.** The opaque end of the overlay gradient meets the text column on the INNER edge; the transparent end is on the OUTER edge where the subject sits. In practice: for a left-half image panel with a left-third subject, the gradient sits on the inner-right edge fading from transparent-at-outer-left to opaque-at-inner-right. Never the reverse.
    - **(d) Sanity check before declaring a slide done.** After building any image + gradient pair, mentally overlay the two: if the gradient's high-opacity region overlaps the subject's bbox by >10%, the design is broken — flip panel side OR flip gradient direction. Do not ship it. This is the exact bug that produced the slide-2/slide-4 rework; the rule exists to make it impossible to repeat.
    - Full rationale and worked examples in [image-prompts.md — subject-side placement](references/image-prompts.md#bg-image-contrast-strategy) and [design-system.md — composition planning](references/design-system.md#composition-planning).

### Process
22. **Always save** at end of every Python script: `prs.save(pptx_path)`.
23. **Escape special characters** in XML: `&` → `&amp;`, `<` → `&lt;`, `>` → `&gt;`.
24. **Build incrementally.** One slide per tool call. Announce progress.
25. **AppleScript is not an editor — it's a remote control.** All content/design changes go through python-pptx. Edit cycle: check presence → quit → wait for exit → rebuild → reopen.
26. **Unit difference.** AppleScript reads positions in points (72/inch). python-pptx uses EMUs (914400/inch). Convert: `EMU = points × 12700`.

## References

Detailed reference documentation lives in focused files. Read the relevant file when the task requires it:

- **[python-pptx Reference](references/python-pptx-reference.md)** — Complete API reference: imports, opening/saving, shapes, text boxes, tables, charts, images, gradients, transparency, rounded corners, helper functions (`make_title_page()`, `make_kpi_card()`, etc.), `pal` dict contract, `style_to_pal()` adapter, `check_overlaps()`, `add_gradient_shape()`, `add_picture_fit()`, `add_picture_cover()`, `verify_generated_image()`. **Read before writing any python-pptx code.**
- **[AppleScript Reference](references/applescript-patterns.md)** — App lifecycle and navigation: PowerPoint presence check (graceful fallback for Keynote-only machines), the reload pattern, navigation, slideshow control, screenshot triggers, unit system. **Read ONLY for app control — never for editing.**
- **[Design System](references/design-system.md)** — Typography rules, color palettes, layout catalog (11 types), composition patterns (10 patterns), layout rhythm, theme pairing, EMU conversions. **Read when planning a new deck's visual design.**
- **[Design Styles Catalog](references/design-styles-catalog.md)** — 12 curated styles (STYLE-01 through STYLE-12) with full layout, typography, color, and graphic treatment specs. **Read when the user requests a specific style.**
- **[Style → python-pptx Mapping](references/style-pptx-mapping.md)** — Concrete RGBColor values, font configs, accent bar settings, card parameters for each style + required-key schema. **Read alongside the Design Styles Catalog.**
- **[Image Prompt Engineering](references/image-prompts.md)** — How to write AI image prompts: Section A (full-bleed BG), Section A2 (side panels), Section B (content images), Section C (prompt quality checklist), Section D (post-gen AR verification). **Read before generating any image.**
- **[Audit System](references/audit-system.md)** — Post-generation quality audit: 13 checks, iterative fix loop with rollback, cascading fix strategies, word-wrap simulation, bullet layout algorithm, false positive avoidance. **Read before running the mandatory audit.**
