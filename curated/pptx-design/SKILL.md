---
name: pptx-design
description: "Expert PowerPoint design agent for macOS. python-pptx + lxml is the sole editing engine — all content and design changes go there. AppleScript is used only for app lifecycle (open, quit, navigate, slideshow, screenshot). Use when: (1) Creating new PowerPoint presentations from scratch, (2) Editing or redesigning existing .pptx files, (3) Building slide decks with custom design (gradients, cards, KPI panels, charts, tables), (4) Refreshing/previewing presentations in PowerPoint on macOS via the quit-rebuild-reopen cycle, (5) Generating AI images for slide backgrounds and content, (6) Any task requiring python-pptx code generation with design best practices. Features 28 critical rules including mandatory dark-BG + targeted-gradient contrast strategy, add_gradient_shape() for overlay shapes, width-first text box sizing, 12 curated design styles, 11 layout types, 10 image composition patterns, and 3-phase pre-build workflow (content analysis → style selection → image strategy)."
---

# PowerPoint Design Agent

Expert PowerPoint design agent on macOS. Creates and edits professional presentations using `python-pptx` + `lxml` as the sole editing engine, AppleScript for **app lifecycle only** (open, close, quit, navigate, slideshow, screenshot), and AI image generation for visual content.

**Core doctrine:** python-pptx edits the file. AppleScript moves the window. Do not cross these streams.

## Core Behavior

- **Content-first, not layout-first.** Analyze the topic deeply before touching style or layout. Understand what each slide needs to communicate, then pick the layout type that fits. KPI cards and metric panels are ONE option among many — use them only when the content is actually data-driven. For narrative, story, educational, or persuasive content, use Narrative Pages, Quote Pages, Chapter Dividers, Comparison Pages, and other diverse layout types from the [Layout Type Catalog](references/design-system.md#layout-type-catalog).
- Determine if the request needs a plan. Complex (multi-slide deck, redesign) = plan first. Simple (edit one slide, change a font) = just do it.
- Before every tool call, write one sentence starting with `>` explaining the purpose.
- Use the same language as the user.
- Cut losses promptly: if a step fails repeatedly, try alternative approaches.
- Build incrementally: one slide per tool call. Announce what you're building before each slide.
- After completing all slides, **run the mandatory audit + fix loop** before delivering.
- Open/refresh the file in PowerPoint via AppleScript after audit is clean.

## Pre-Build Workflow (ALWAYS follow for new presentations)

**Before generating any new presentation, complete these 3 phases in order:**

### Phase 1: Content Analysis & Structure Planning (MANDATORY)

**This phase comes FIRST — before style, before images, before any code.** Analyze the topic to understand what the presentation needs to communicate.

1. **Analyze the topic:**
   - What is the subject?
   - What is the content type? (see classification table below)
   - Who is the audience?
   - What is the narrative arc? (e.g., setup → conflict → resolution, or intro → evidence → conclusion)

2. **Propose a slide structure table:**

```
| # | Purpose | Content Summary | Layout Type |
|---|---------|-----------------|-------------|
| 1 | Opening | Title + subtitle | Title Page |
| 2 | Setup | Background context | Narrative Page |
| 3 | Key moment | Dramatic quote | Quote Page |
| ... | ... | ... | ... |
```

3. **Validate layout diversity BEFORE presenting the table:**
   - Count consecutive slides with the same layout type. **If 3+ consecutive slides share a layout type, restructure.**
   - A 10-slide deck should use **at least 4 different layout types**.
   - Flag monotonous sequences to yourself and fix them. Do NOT present a table with 8 identical "Narrative Page" rows.
   - Use the [Layout Type Catalog](references/design-system.md#layout-type-catalog) (11 types) and [Layout Rhythm](references/design-system.md#layout-rhythm-across-slides) patterns to ensure variety.

4. **Wait for user approval before proceeding.** The user may want to add, remove, or reorder slides.

**Content Type Classification:**

| Content Type | Description | Typical Layout Mix |
|---|---|---|
| Narrative / Story | Fairy tales, case studies, biographies, journeys | Title Page, Chapter Dividers, Narrative Pages, Quote Pages, Full-Bleed Images |
| Educational | Lessons, tutorials, how-tos, explainers | Title Page, Narrative Pages, Diagram/Process, Comparison Pages, Data Tables |
| Data-Driven | Financial reports, KPI dashboards, analytics | Title Page, KPI Cards, Data Tables, Charts, Comparison Pages |
| Persuasive / Pitch | Investor decks, proposals, sales pitches | Title Page, Narrative Pages, KPI Cards, Comparison Pages, Quote Pages |
| Portfolio / Showcase | Galleries, product showcases, team intros | Title Page, Full-Bleed Images, Grid/Mosaic, Narrative Pages |
| Event / Agenda | Conference talks, meeting agendas, schedules | Title Page, Timeline, Data Tables, Narrative Pages |

### Phase 2: Style Selection

After the slide structure is approved, select the visual style.

If user specifies a style (e.g., "use STYLE-01", "McKinsey style") → confirm and proceed.

If user does NOT specify a style → recommend based on **content type** from Phase 1:

```
Based on your content, I recommend:

  **STYLE-XX — [Name]** — [1-line reason why it fits]

Want me to go with this? Or would you like to:
  • See the full list of all 12 styles with descriptions?
  • Pick a different style by name or number?
```

**If the user doesn't respond or doesn't care, default to STYLE-02 (Executive Editorial) and proceed.**

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

**If NONE of the 12 styles fit the user's content**, generate a **custom style** on the fly:

1. Analyze the content's tone, audience, and subject matter.
2. Design a bespoke style dict with: `slide_bg`, `fonts` (title, body, optional extras), `palette` (5-8 colors), `accent_bar` (optional), and `design_notes`.
3. Present it to the user:
```
None of the 12 preset styles are a great fit for your content. I've designed a custom style:

  **CUSTOM — [Name]**
  Palette: [2-3 key colors described]
  Fonts: [title font] + [body font]
  Vibe: [1-line description]

Want me to go with this? Or would you prefer to pick from the 13 presets?
```
4. Wait for user confirmation, then use the custom style dict throughout — same as any preset style. The audit (CHECK 11) uses whatever style dict is active, including custom ones.
5. The custom style dict must follow the same structure as the presets in [Style → python-pptx Mapping](references/style-pptx-mapping.md) so all audit checks work identically.

Style references: [Design Styles Catalog](references/design-styles-catalog.md) for full descriptions, [Style → python-pptx Mapping](references/style-pptx-mapping.md) for implementation values.

### Phase 3: Image Strategy & Composition Planning

After style is confirmed, determine the image approach.

#### Default Behavior — NO Background Images

**By default, do NOT use background images.** Use solid color / gradient backgrounds from the active style palette. Background images are powerful but add complexity (overlay management, contrast issues, image-text coordination) that isn't always needed.

**Only use BG images when the user explicitly requests them** — e.g., "with bg image", "add background images", "use photos", "cinematic slides", etc.

#### When User Requests Background Images

When the user explicitly asks for BG images, follow the **BG Image Contrast Strategy** (mandatory):

1. **Generate DARK / non-bright images.** All BG images must be dark, moody, atmospheric. Never generate bright, light, or airy backgrounds — they create text contrast nightmares.
2. **Add targeted gradient shapes** (NOT full-slide overlays) where text sits. Use `add_gradient_shape()` to create gradient fade zones that transition from dark (where text lives) to transparent (where the image should show through). These are narrow, targeted shapes — not full-slide tinted rectangles.
3. **Use light/white/cream text colors** for text overlaid on dark BG images.
4. **EXCEPTION — Opaque card/panel slides (KPI cards, data tables, etc.):** If the slide's content elements are opaque cards with solid fills, do NOT add ANY overlay — not even targeted gradients. The cards handle their own text contrast via their opaque fill. The BG image shows through in the gaps between cards, which is the whole point. Adding an overlay just washes out the BG for zero readability benefit.

```
# BG Image Contrast Decision Tree:
#
# Is the slide content in opaque cards/panels?
#   YES → No overlay. Cards handle contrast. BG image shows freely.
#   NO  → Text directly on BG image?
#     YES → Add targeted gradient shape(s) where text sits.
#           Gradient: dark end at text zone → transparent toward image focal point.
#     NO  → No overlay needed.
```

#### When User Explicitly Requests Content Images

If the user says "in-slide illustrations", "content images", "images inside cards", "not backgrounds" — switch to content image mode. See **Content Image Prompt Rules** below.

#### When to Ask

Only ask if the user's intent is genuinely ambiguous:

```
Would you like AI-generated images for the slides?

  • Yes, full backgrounds — Dark, atmospheric HD images as full-bleed slide
    backgrounds with targeted gradient overlays for text zones.
  • Yes, as content images — In-slide illustrations placed alongside text,
    inside cards, or as visual elements within the layout.
  • Yes, mixed — Some slides get backgrounds, others get content images.
  • No (Default) — Solid color / gradient backgrounds from the style palette only.
```

If the user says **yes** (any mode), you MUST complete a **Global Image Strategy** and a **Per-Slide Composition Plan** before generating any image.

#### Step 3a: Global Image Strategy

```
Image Mode: [full-bleed backgrounds | content images | mixed]
Primary image style: [photorealistic | illustrated | abstract | etc.]
Deck palette integration: dark images + light text (MANDATORY for BG images)
Layout rhythm pattern: [alternating | progressive | content-driven | grouped]
BG tone consistency: [dark moody | warm earth | cool tech | vibrant neon] (NEVER light/airy/bright)
Text contrast strategy: targeted gradient shapes where text sits + no overlay on opaque card slides
```

**CRITICAL — Cross-Slide BG Consistency Rule:**

All background images across the ENTIRE deck MUST share a consistent visual identity:
- **Same color temperature** — ALL dark, ALL light, ALL warm, etc. Mixing a bright sunny BG on slide 3 with a dark moody BG on slide 7 is a **composition failure**. Pick ONE tone and commit.
- **Same visual style** — ALL photorealistic, ALL abstract gradients, ALL illustrated, etc. Don't mix photo backgrounds with abstract shape backgrounds.
- **Same palette range** — Every BG image must harmonize with the same 2-3 hex colors from the active style. Include these colors in EVERY image prompt.
- **Same level of visual complexity** — Don't have a busy detailed scene on one slide and a minimal abstract wash on the next. Define the complexity level once and apply it uniformly.

**Anti-pattern examples (NEVER do these):**
- Slide 2: dark navy abstract gradient → Slide 4: bright white minimalist → Slide 6: warm sunset photo (**inconsistent tone**)
- Slide 1: photorealistic city → Slide 3: flat vector illustration → Slide 5: watercolor painting (**inconsistent style**)
- Slide 2: busy, detailed crowd scene → Slide 4: clean, empty gradient (**inconsistent complexity**)

When planning BG images, write ONE sentence defining the global visual identity, then enforce it on EVERY image prompt:
```
Global BG identity: "Dark moody abstract gradients with deep navy (#0A1628) to black,
subtle geometric mesh patterns, warm gold (#D4A853) accent glows. Minimal complexity,
no recognizable objects — pure atmosphere."
```

#### Step 3b: Per-Slide Composition Plan (MANDATORY)

Present a detailed composition plan table. **Every column is required — no shortcuts.**

```
| # | Layout Type | Image Role | Composition Pattern | Image Concept | Focal Point | Text Zone | Overlay Strategy | Image Dimensions |
|---|-------------|------------|---------------------|---------------|-------------|-----------|------------------|------------------|
| 1 | Title Page | Full-bleed BG | Bleed + Gradient Fade | [scene] | Center | Bottom 30% | Gradient shape bottom 35% | 16:9 full-slide |
| 2 | Narrative | Side panel | Split Left-Right | [scene] | Right 55% | Left 45% | Gradient shape left 45% | 7:5 right-half |
| 3 | Quote Page | Full-bleed BG | Center Stage | [scene] | Edges | Center | Gradient shape center band | 16:9 full-slide |
| 4 | KPI Cards | Full-bleed BG | Bleed + Even | [scene] | Even | Cards overlaid | NONE (opaque cards) | 16:9 full-slide |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
```

**Column definitions:**
- **Layout Type**: From Phase 1's approved slide structure (must match exactly)
- **Image Role**: How the image is physically placed on the slide:
  - `Full-bleed BG` — image covers entire slide (13.33" x 7.5"), text overlaid
  - `Side panel` — image fills one side (30-50% of slide width), content on the other
  - `Content image` — image as a discrete element within the layout, NOT a background
  - `Accent strip` — narrow panoramic image (full-width, 30-40% height)
  - `No image` — gradient/solid background only
- **Composition Pattern**: One of the 10 patterns from [Image Composition Patterns](references/design-system.md#image-composition-patterns), or "—" if no image
- **Image Concept**: Scene description for the AI image prompt
- **Focal Point**: Where the image's visual subject/interest lives
- **Text Zone**: Where text will be placed (must NOT overlap focal point)
- **Overlay Strategy**: How text contrast is handled on this slide:
  - `Gradient shape [zone]` — targeted `add_gradient_shape()` covering only the text zone, fading from dark to transparent
  - `NONE (opaque cards)` — slide has opaque card/panel fills; no overlay needed
  - `NONE (side panel)` — text is on the opposite side from the image; no overlay needed
- **Image Dimensions**: Aspect ratio and size relative to slide

#### Image Role ↔ Dimensions Binding Rules (CRITICAL)

**These rules are NON-NEGOTIABLE. Violating them produces the "background-as-thumbnail" anti-pattern.**

1. **Full-bleed BG images → MUST be placed at (0,0) covering the entire slide (13.33" x 7.5").** Never shrink a 16:9 background image to a small content area.

2. **Side panel images → generate at portrait or near-square ratio** (3:4, 2:3, 9:16) matching the panel's actual dimensions on the slide.

3. **Content images → generate at the exact aspect ratio of the target placement area.** If the image slot is 4"x3", generate at 4:3.

4. **If you generate a 16:9 image, the ONLY valid placements are:** full-bleed background or panoramic accent strip. **Anything else is a composition failure.**

5. **Image coverage validation:** Full-bleed = 100%, Side panel = 30-50%, Content image = 15-30%, Accent strip = 30-40%. **If a "background" image covers <30%, the plan is wrong.**

**Wait for user approval of the composition plan.** Then generate images one at a time during the build phase.

---

### Image Prompt Engineering Rules

**These rules govern how to write AI image generation prompts. The prompt must be fully aware of the PPTX design context — the image and the slide are ONE composition, not separate artifacts.**

#### A. Background Image Prompts (Full-Bleed BG) — DEFAULT MODE

Background images are the FOUNDATION of the slide. The PPTX overlay text will sit on top. The image must be designed to RECEIVE text, not compete with it.

**Mandatory prompt components:**

1. **NO TEXT IN THE IMAGE.** Always include: "No text, no words, no letters, no typography, no labels, no watermarks — purely visual."

2. **Negative space directives.** Specify WHERE on the image the PPTX text will be placed, and instruct the AI to leave that zone visually quiet:
   - "Leave the [bottom third / left 40% / center] dark and uncluttered for text overlay"
   - "Compose with negative space in [zone] — muted tones, soft gradients, or out-of-focus areas"
   - "The visual subject/focal point should be in [opposite zone from text]"

3. **Color/tone harmony with PPTX style.** The image's palette must complement the active style:
   - For dark styles: "Dark moody tones, deep shadows, warm undertones"
   - For light styles (STYLE-01): "Bright, clean, high-key lighting, white/grey negative space"
   - For warm styles (STYLE-02): "Warm cream and earth tones, soft editorial lighting"
   - **Explicitly name 2-3 colors from the active palette** that the image should harmonize with.

4. **Visual style matching.** The image style must match the deck's design language:
   - STYLE-01 (Strategy): Clean, corporate photography, minimal, geometric
   - STYLE-04 (Kawaii): Soft pastel illustration, cute, rounded shapes
   - STYLE-06 (Anime): Dramatic cinematic anime art, rich detail

5. **Composition pattern directive.** Based on the slide's text layout, specify the image's internal composition:
   - Title bottom-third text → "Subject centered or upper third, bottom fades to dark gradient"
   - Left-side text panel → "Visual interest concentrated on the right 60%, left side is atmospheric/blurred"
   - Center quote text → "Frame the center with visual elements at edges, center is moody open space"
   - Full overlay → "Even texture/pattern that works as a subtle backdrop — no strong focal point"

6. **Content-aware image composition.** The image's CONTENT must reflect the slide's message — not just leave generic blank space. The image and the overlay text tell ONE story together:
   - **Design the image subjects to SUPPORT the text message.** If the slide compares two things, the image should visually split into two zones. If the slide is about growth, the image should have upward visual energy.
   - **Place image subjects to CREATE natural text zones.** Don't rely solely on "leave blank space" — compose the image so its content arrangement naturally produces areas where text belongs.
   - **Example — NBA competition slide:** Two team stars split on opposite sides of the image, facing each other. The center zone between them grows darker with gradient — this is where the overlay text about the matchup goes. The image IS the story; the text completes it.
   - **Example — before/after slide:** Left half shows the "before" state (muted, desaturated), right half shows the "after" (vibrant, sharp). Overlay text labels each side. The image composition mirrors the slide's comparison structure.
   - **Example — abstract/shape backgrounds:** If using abstract gradients or geometric patterns, design the visual flow to guide the eye toward the text zone. Denser patterns at edges, opening up to quieter space where text lives.

7. **Aspect ratio and resolution.** Always specify: "16:9 aspect ratio, high resolution, widescreen composition"

8. **Text zone strategy — dark BG + targeted gradient shapes (the ONLY approach).**

   The strategy is simple and reliable:
   - **Generate dark, non-bright BG images.** Always prompt for dark, moody, atmospheric tones. Never generate bright/light BG images — they require heavy overlays that defeat the purpose.
   - **Add targeted gradient shapes where text sits** using `add_gradient_shape()`. These are narrow gradient rectangles that cover ONLY the text zone, fading from dark (opaque, where text lives) to transparent (where the image shows through). They are NOT full-slide overlays.
   - **Use light text colors** (white, cream, light gold) for all text on BG image slides.

   **EXCEPTION — Opaque card/panel slides:** If the slide's content is in opaque cards (KPI cards, data tables, etc.), do NOT add any gradient shapes. The cards have solid fills and handle their own text contrast. The BG image shows through the gaps between cards — covering it with overlays just washes out the geography/visual message of the image for zero benefit.

   **What NOT to do:**
   - Do NOT add full-slide semi-transparent overlay rectangles. They wash out the entire image uniformly, reducing visual impact. The old "Option A: image-level negative space" approach is insufficient alone — AI image generators can't reliably create precise dark zones. Targeted gradient shapes are more predictable.
   - Do NOT generate bright/airy BG images and try to fix contrast with heavy overlays. Start dark.
   - Do NOT add overlays on slides where all text is inside opaque cards/panels.

   Declare which slides need gradient shapes vs which are card-based (no overlay needed) in the Per-Slide Composition Plan (Step 3b) under the "Text Zone" column.

**Example prompt for a STYLE-02 title slide:**
```
Editorial overhead view of an elegant workspace with warm natural lighting.
Warm cream and earth tones matching #FAF7F2 palette. Rich amber highlights
complementing #C8A96E accent color. Subject in upper-center third. Bottom 30% fades
to soft warm tones for text overlay. No text, no words, no letters, no typography.
16:9 aspect ratio, high resolution, editorial photography style.
```

#### A2. Side Panel Image Prompts (30-50% of Slide)

Side panel images are a HYBRID — larger than content images, portrait-oriented, and they share a visual edge with the text zone. They need composition awareness like backgrounds (the edge adjacent to text must be visually quiet) but are sized like content images (portrait/square ratio, not 16:9).

**Mandatory prompt components:**

1. **NO TEXT IN THE IMAGE.** Same rule as backgrounds: "No text, no words, no letters, no typography, no labels, no watermarks — purely visual."

2. **Portrait or near-square aspect ratio.** Side panels are tall, not wide:
   - Right-side panel (55% width): "3:4 portrait aspect ratio" or "2:3 portrait"
   - Left-side panel (45% width): "3:4 portrait" or "4:5 near-square"
   - **NEVER 16:9** — that is backgrounds only. A 16:9 image forced into a portrait panel is the #1 distortion bug.

3. **Adjacent-edge negative space.** The edge of the image that borders the text zone must be visually quiet — NOT the focal point:
   - Right panel with text on left → "Subject on the right side of the frame, left edge fades to [dark/blurred/atmospheric] for clean transition to text zone"
   - Left panel with text on right → "Subject on the left, right edge fades to [dark/soft] for clean visual boundary"
   - **The focal point goes AWAY from the text edge, not toward it.**

4. **Color/tone harmony with slide background.** The image's overall tone should complement the slide's background color at the shared edge:
   - Dark slide bg (#0C0C0E) → "Dark atmospheric tones, image edge blends naturally with dark slide background"
   - Light slide bg (#FFFFFF) → "Clean, airy composition, image edge transitions smoothly to white"
   - **Name 2-3 hex colors from the active style palette.**

5. **Visual style matching.** Same as Section A — match the deck's design language.

6. **Subject composition for tall frames.** Portrait orientation changes composition rules:
   - "Subject centered vertically, filling 60-80% of the frame height"
   - Avoid wide landscape subjects (cities, panoramas) in portrait panels — they'll be tiny
   - Prefer subjects that work vertically: portraits, architecture, tall objects, abstract vertical compositions

**Example prompt for a STYLE-02 side panel (right side, 55% width):**
```
Close-up portrait of a professional in a modern office, warm natural lighting.
Warm cream tones matching #FAF7F2, amber highlights complementing #C8A96E.
Subject centered-right in frame, left edge fades to soft warm tones for clean
transition to text zone. 3:4 portrait aspect ratio, high resolution.
No text, no words, no letters, no typography. Editorial photography style.
```

#### B. Content Image Prompts (In-Slide Illustrations) — ONLY WHEN USER EXPLICITLY REQUESTS

Content images live INSIDE the layout as visual elements alongside text. They must be PPTX-design-aware.

**Mandatory prompt components:**

1. **Style/theme coherence.** The illustration style must match the deck's design system:
   - Use the active style's color palette as the image's primary palette
   - Match the design language: flat/minimal for corporate styles, illustrated for creative styles, photorealistic for editorial styles
   - "Color palette: [list 3-4 hex colors from active style]. Style: [style description]"

2. **Background handling.** Content images sit on colored card surfaces, not on white:
   - For dark themes: "Transparent background" or "Background color #1A1A1E to match card surface"
   - For light themes: "Clean white background" or "Background #FFFFFF"
   - **Never generate a content image with a busy background** — it will clash with the card/slide bg.

3. **Aspect ratio matches placement slot.** Generate at the EXACT ratio of the content area:
   - Card icon: "1:1 square, 400x400px"
   - Side illustration: "3:4 portrait, centered subject"
   - Wide feature image: "4:3 landscape"
   - **Never 16:9 for content images** (that's backgrounds only)

4. **Visual weight and scale.** Content images are subordinate to text — they support, not dominate:
   - "Clean, simple composition with clear subject and minimal surrounding detail"
   - "Icon-style illustration" or "Focused product shot" — not busy panoramic scenes
   - Ensure the subject fills 60-80% of the frame (no tiny subject in vast empty space)

5. **No text in image.** Same rule: "No text, no labels, no watermarks — purely visual."

6. **Consider adjacent PPTX elements.** If text wraps around the image or sits beside it:
   - "Subject facing [toward/away from] text side" (subjects should face toward the content, not away)
   - "Visual weight on [side closest to text]" to create visual connection

**Example prompt for a content image in a STYLE-05 product card:**
```
Minimalist icon illustration of a robot assistant. Flat design style with blue
(#2563EB) and slate grey (#64748B) tones on a white background (#FFFFFF). Clean,
geometric, no text. 1:1 square aspect ratio. Simple and modern, matching corporate
professional aesthetic.
```

#### C. Prompt Quality Checklist (Run Before Every Image Generation)

Before generating ANY image, verify your prompt includes:

- [ ] **No-text directive** ("No text, no words, no letters, no typography")
- [ ] **Aspect ratio** matching the image role (16:9 BG / portrait side panel / slot-ratio content)
- [ ] **Color harmony** — 2-3 hex colors from active style palette mentioned
- [ ] **Visual style** matching the deck's design language
- [ ] **For BG images:** Negative space zone specified matching text placement
- [ ] **For BG images:** Tone/darkness level matching slide background color
- [ ] **For side panels:** Portrait/near-square ratio (3:4, 2:3) — NEVER 16:9
- [ ] **For side panels:** Adjacent-edge negative space (edge near text zone is quiet/dark/blurred)
- [ ] **For side panels:** Subject composition works in portrait orientation (no wide panoramas)
- [ ] **For content images:** Background color matching card/slide surface
- [ ] **For content images:** Subject scale appropriate (fills 60-80% of frame)
- [ ] **Composition direction** — focal point placement specified

#### D. Post-Generation AR Verification (Run AFTER Every Image Generation)

**Many image gen tools have NO native aspect ratio parameter.** AR is requested via prompt text only, and the model may ignore it. You MUST verify every generated image before proceeding to placement.

After each image is generated, run `verify_generated_image()` from the [python-pptx Reference](references/python-pptx-reference.md):

```python
ok, ar, msg = verify_generated_image('generated.png', 'side-panel', intended_ar=0.75)
if not ok:
    print(f"⚠️ {msg}")  # → REGENERATE or adapt role
```

**Decision tree on mismatch:**
1. **Deviation <10%** → Accept. `add_picture_fit()` handles the slight difference gracefully.
2. **Deviation 10-25%** → Regenerate once with a more explicit AR directive: "IMPORTANT: This image MUST be taller than it is wide, 3:4 portrait ratio, approximately 768x1024 pixels."
3. **Deviation >25%** → The image is fundamentally the wrong shape. Either:
   - Regenerate with a completely reworded prompt emphasizing orientation
   - **Adapt the role**: if the model keeps producing 16:9, switch to full-bleed BG; if it keeps producing 1:1, use as a content image
4. **After 2 failed regenerations** → Stop trying to force the AR. Change the slide's Image Role in the composition plan to match what the model actually produces.

### Environment

The presentation file path is stored in `PPTX_PATH`. Every Python script must read `os.environ['PPTX_PATH']`.

Ensure dependencies before first use:
```bash
python3 -m pip install python-pptx lxml Pillow --quiet
```

## Engine Architecture — Editor vs. Remote Control

Two engines, **one role each** — do not confuse them:

- **python-pptx + lxml** = **THE EDITOR.** All content and design changes go here, no matter how small. Text, fonts, colors, positions, fills, sizes, shadows, letter-spacing, gradients, corner radius, transparency, shape creation, images, charts, tables, speaker notes — everything.
- **AppleScript** = **THE REMOTE CONTROL.** App lifecycle only: open file, close file, save, quit app, navigate to slide, start/stop slideshow, trigger screenshot, read shape inventory for a quick look.

**The rule that eliminates 90% of bugs:** If you're about to write AppleScript that SETS any property on a shape or text, stop. Rebuild with python-pptx instead. AppleScript's "live edit" API is missing half the properties you need (letter-spacing, gradient, alpha, corner radius) and unreliable on the other half (font color, `top of shape`). The rebuild-and-reload path is faster and more predictable.

**The standard edit cycle:**
```
1. Quit PowerPoint (if running):
   osascript -e 'tell application "Microsoft PowerPoint" to quit saving no'
2. Wait for the process to exit:
   while pgrep -x "Microsoft PowerPoint" > /dev/null; do sleep 0.2; done
3. Rebuild with python-pptx (creates or overwrites the .pptx file).
4. Reopen:
   open -a "Microsoft PowerPoint" /abs/path/file.pptx
```

**Why all four steps matter:** Skipping the quit step causes the #1 silent-failure bug — PowerPoint holds the file open, `open -a` just raises the stale window instead of re-reading from disk, and you see "my changes didn't appear." Always quit-wait-rebuild-reopen.

For in-place edits on a file the user has unsaved changes in, ask first — do not silently quit-discard their work.

See [AppleScript reference](references/applescript-patterns.md) for full lifecycle commands and deprecated live-edit patterns.

## Workflows

### New Presentation (Full Build)

1. **Content Analysis** (Phase 1) — Analyze the topic, classify content type, propose slide structure table with layout types. **Wait for user approval.**
2. **Style Selection** (Phase 2) — Recommend a style based on content type. **Wait for user approval.**
3. **Image Planning** (Phase 3) — Ask if user wants AI images. If yes, present image composition plan per slide. **Wait for user approval.**
4. **Plan** palette, fonts, and **composition strategy** — apply the chosen style from [Design Styles Catalog](references/design-styles-catalog.md) and [Style Mapping](references/style-pptx-mapping.md). For each slide, use the approved layout type (from the [Layout Type Catalog](references/design-system.md#layout-type-catalog)) and the approved composition pattern (from Phase 3's composition plan). Vary layouts across slides (see [layout rhythm](references/design-system.md#layout-rhythm-across-slides)). **Cross-check**: every slide's Image Role from the composition plan must match the python-pptx placement code you're about to write.
5. **Generate all needed images** (if user said yes) — use whichever AI image generation skill/MCP is available at the system level (the user may also explicitly specify one). **Browser-based tools (e.g., baoyu-danger-gemini-web, grok-image-gen) must generate one at a time, sequentially — NEVER in parallel. API-based image/video generation tools can run in parallel.** For each image:
   - **Check the approved Image Role** from Phase 3's composition plan
   - **Pick the correct prompt section**: Section A for full-bleed BG, Section A2 for side panels, Section B for content images. Run the Prompt Quality Checklist (Section C) before every generation call.
   - **Generate at the correct aspect ratio** for that role (16:9 for full-bleed BG, portrait 3:4/2:3 for side panels, slot-ratio for content images)
   - **POST-GENERATION VERIFICATION (MANDATORY):** After each image is generated, immediately run `verify_generated_image()` (see [python-pptx Reference](references/python-pptx-reference.md)) to check the actual pixel dimensions against the intended role. The image gen tool may have NO native AR parameter — it only honors AR requests in the prompt text, and models frequently ignore them. **If the actual AR doesn't match the intended role (>15% deviation), you MUST regenerate with a stronger AR directive or switch roles.** Common mismatches:
     - Intended "3:4 portrait" for side panel → model generated 16:9 landscape → **REGENERATE** with explicit "tall portrait composition, 3:4 ratio, taller than wide"
     - Intended "1:1 square" for card icon → model generated 4:3 → **REGENERATE** or accept if close enough (<10% off)
     - Intended "16:9 landscape" for background → model generated 1:1 square → **REGENERATE** or use as content image instead
   - **If regeneration fails twice**, adapt: change the Image Role to match what the model actually produced (e.g., if the model keeps producing 16:9, use it as full-bleed BG instead of forcing it into a side panel).
6. **python-pptx**: Create file + build all slides (one per tool call). Use the appropriate layout helpers for each slide's layout type: `make_title_page()`, `make_chapter_divider()`, `make_narrative_page()`, `make_quote_page()`, `make_comparison_page()`, `make_kpi_card()`, etc. Apply style colors, fonts, backgrounds.
7. **Mandatory audit + fix loop** — Two-pass audit:
   - **Pass A (inline, style-aware):** Read [Audit System](references/audit-system.md) and run all checks (1-12) iteratively. Fix cascading issues. CHECK 12 (image AR distortion) is CRITICAL.
   - **Pass B (pptx-audit-and-fix tool, if installed):** After Pass A is clean, run the standalone audit tool for additional checks (WCAG contrast, composition coverage, text truth estimation). This catches issues the inline audit misses — e.g., overlay shapes blocking >30% of a BG image. Chain it like this:
     ```python
     import os, importlib.util
     audit_path = os.path.expanduser("~/.claude/skills/pptx-audit-and-fix/references/pptx_audit.py")
     if os.path.exists(audit_path):
         spec = importlib.util.spec_from_file_location("pptx_audit", audit_path)
         mod = importlib.util.module_from_spec(spec)
         spec.loader.exec_module(mod)
         auditor = mod.PptxAuditor(pptx_path)
         report = auditor.run_full_audit()
         print(report)
         # Fix auto-fixable issues
         if any(i.severity.name == 'CRITICAL' for i in report.issues):
             auditor.fix_all(report)
             auditor.save(pptx_path)
     else:
         print("ℹ️ pptx-audit-and-fix skill not installed — skipping Pass B (contrast, composition coverage checks).")
     ```
   - **If pptx-audit-and-fix is not installed**, Pass A alone is sufficient. Pass B is an enhancement, not a requirement.
8. **AppleScript**: Open the file in PowerPoint (`open -a "Microsoft PowerPoint" "$PPTX_PATH"`).
9. **Visual verification**: Navigate through slides and visually confirm each slide — check that image focal points are unblocked and text sits in the planned zones. Use AppleScript `go to slide` for navigation.
10. **Fix anything broken**: If visual review finds issues, **quit PowerPoint, fix in python-pptx, reopen** (the standard edit cycle from the Engine Architecture section). Never reach for AppleScript to "just tweak this one thing."
11. **Report** audit summary to user, then deliver the file path.

### Edit Existing Presentation

1. **Read** the file with python-pptx to understand current state (shapes, text, positions, colors).
2. **Quit PowerPoint** if the file is currently open (to release the file lock).
3. **Edit** with python-pptx (modify existing shapes, add new ones, remove obsolete ones) — preserve surgical scope per Rule 16.
4. **Save** via `prs.save(pptx_path)`.
5. **Run the mandatory audit** (same as new presentations).
6. **Reopen** in PowerPoint for visual verification.

### Redesign Existing Presentation

1. **Read** the file with python-pptx to catalog everything.
2. **Quit PowerPoint** if open.
3. **Plan** new design, palette, image strategy.
4. **Generate** any needed images.
5. **Rebuild** each slide with python-pptx (clear old shapes, add new ones).
6. **Run the mandatory audit.**
7. **Reopen** in PowerPoint and visually verify.

### Quick Fix / Small Tweak

There is no "AppleScript-only" path. Even small tweaks — a font size, a color, a footer text — go through python-pptx:

1. Quit PowerPoint.
2. Open the file with python-pptx, locate the target shape, apply the change.
3. Save.
4. Reopen in PowerPoint.

This is faster than fighting AppleScript's missing/unreliable APIs for color, letter-spacing, gradient, radius, or alpha.

## Mandatory Audit — NON-NEGOTIABLE

**Every new or redesigned presentation MUST pass the full audit before delivery. No exceptions.**

The audit is **not optional**, **not skippable**, and **not deferrable**. It runs after all slides are built and before the file is shown to the user.

### What the audit does
**Pass A (inline, style-aware):** Run all 13 checks from [Audit System](references/audit-system.md): bounds, text clipping, word-wrap, container sync, bullet alignment, overlap, z-order, font compliance, spacing, color/fill integrity, style compliance, **image aspect ratio distortion**, **broken gradient fills (blue rectangle detection)**. Iterate up to 5 passes — fix issues, re-audit, repeat until clean.

**Pass B (pptx-audit-and-fix tool, optional):** If the `pptx-audit-and-fix` skill is installed at `~/.claude/skills/pptx-audit-and-fix/`, run it as a second pass for additional checks: WCAG contrast validation, composition coverage (overlay shapes blocking BG images), and text truth estimation via font metrics. This pass is **optional but recommended** — if the skill is not installed, Pass A alone is sufficient. See step 7 in the New Presentation workflow for the integration code.

### Enforcement rules
1. **Never deliver a .pptx without a clean audit.** If the audit finds CRITICAL issues, fix them. If fixes create new issues, re-audit.
2. **Always report the audit summary** to the user: CRITICAL count, WARNING count, fixes applied, passes needed.
3. **The audit runs on the saved file** — reload `Presentation(path)` after saving to get clean state.

### Anti-patterns (NEVER do these)
- Generating the .pptx and immediately saying "Here's your file!" without auditing — **this defeats the entire purpose of this skill.**
- Running only some checks — **all 12 checks must run every pass.**
- Skipping the audit because "it's a simple deck" — **simple decks still have font, bounds, and z-order issues.**
- Fixing an issue without re-auditing — **fixes cause cascading issues; re-audit is mandatory after every fix pass.**

### Composition Anti-patterns (ALSO NEVER do these)
- **Mixed BG consistency**: If >50% of slides use full-bleed background images, the remaining slides MUST also use background images. A deck with 8 image slides and 2 plain gradient slides looks inconsistent — the gradient slides stick out as obviously different. **Either commit to BG images on ALL slides or NONE.** When planning the composition table, if you mark any slide as "No image," ask yourself: will this slide look visually consistent with the image slides? If not, generate a BG image for it too.
- **Background-as-thumbnail**: Generating a 16:9 background image but placing it as a small 5"x3" content image covering <20% of the slide. This is the #1 composition failure. If the image is 16:9, it MUST be full-bleed.
- **Monotonous layout**: Using the exact same layout (e.g., text-left + image-right) for all content slides. Vary layout types across slides — use at least 4 different layouts in a 10+ slide deck.
- **Disconnected image-text relationship**: Generating an image without considering where text will be overlaid. Every image prompt must include composition directives specifying negative space zones that match text placement.
- **Copy-paste layout syndrome**: Every slide having text at (0.8", 0.5") and image at (7.8", 2.4"). This screams "no planning." Each slide's layout should be chosen based on its content type, not copy-pasted from a template.
- **Full-slide overlay on card slides**: Adding a semi-transparent full-slide rectangle over the BG image on a slide where ALL content is inside opaque cards (KPI panels, data tables). The cards already handle text contrast with their solid fills. The overlay just washes out the BG image — which IS the visual message (e.g., a satellite map showing the geography). If the slide has opaque cards, the overlay strategy is NONE.
- **Image aspect ratio distortion**: Using `add_picture(path, l, t, w, h)` with both width and height that don't match the image's native AR. A 16:9 image placed in a 3:5 portrait panel gets horizontally compressed — visually obvious and unprofessional. **Prevention:** use `add_picture_fit()` for ALL non-full-bleed placements, and run CHECK 12 in the audit. **Root cause:** `add_picture()` silently stretches to fit the given dimensions without any warning.
- **Inconsistent BG tone across slides**: Generating slide 2's background as a dark moody abstract and slide 5's as a bright airy photo. This makes the deck look like a collage of unrelated slides, not a cohesive presentation. **ALL background images must share the same color temperature, visual style, and complexity level.** Define the global BG identity ONCE in Step 3a and enforce it on every image prompt. If you notice tone drift mid-generation, stop and regenerate the outlier.
- **Generic negative space instead of content-aware composition**: Asking the AI for "dark area on the left for text" without connecting the image's CONTENT to the slide's MESSAGE. The image should visually support what the text says — subjects positioned to create meaning with the overlay, not just blank space for text to sit on. The image and text are ONE composition telling ONE story.

---

## 28 Critical Rules

1. **Never set any font below 14pt.** Not on labels, footnotes, axis text, or table cells.
2. **Always set explicit positions.** Every shape and image must have left, top, width, height.
3. **Always save** at end of every Python script: `prs.save(pptx_path)`.
4. **Escape special characters** in XML: `&` -> `&amp;`, `<` -> `&lt;`, `>` -> `&gt;`.
5. **Never use emoji as icons.** Use generated images, geometric shapes, or labeled circles.
6. **Use gradients for backgrounds**, not flat solid colors (unless image background is used).
7. **Add decorative accents** — thin bars, underlines, transparency shapes on every slide.
8. **Prefer more slides over dense slides.** Split content rather than shrinking fonts.
9. **Build incrementally.** One slide per tool call. Announce progress.
10. **Verify after building.** Check overlaps, overflow, and visual quality.
11. **Composition-first: plan image + overlay as ONE design.** Before generating any background image, decide where text/content zones go and where the image focal point lives. Generate images with intentional negative space (dark/empty/blurred areas) matching your content zones. The best slides need NO overlay because the image was composed for the layout. When overlays are needed, use targeted overlays (only where text sits), not full-bleed. Never overlay the image's focal point. See the Composition Planning section in [Design System](references/design-system.md#composition-planning) for the full layout catalog and coordination rules.
12. **Use lxml for gradients.** The python-pptx `fill.gradient()` API can fail; the lxml XML approach is bulletproof.
13. **AppleScript is not an editor — it's a remote control.** All content/design changes go through python-pptx, even one-line tweaks. When the file is open in PowerPoint, the edit cycle is: quit app → wait for process exit → rebuild with python-pptx → reopen. Do NOT use AppleScript to set fonts, colors, positions, fills, or any other shape property — half the properties you need aren't exposed and the rest are unreliable.
14. **Remember the unit difference.** AppleScript reads positions in points (72/inch). python-pptx uses EMUs (914400/inch). Convert: `EMU = points * 12700`. You'll mostly only need this when reading shape positions for debugging.
15. **Always calculate text frame dimensions.** **Width first, height second.** Before setting any text box dimensions, estimate the rendered width of the longest line: `rendered_width ≈ font_size_pt × 0.6 × char_count` (0.6 is average char width ratio for proportional fonts; use 0.7 for bold). If `rendered_width > box_width`, the text WILL wrap — causing unexpected extra lines, height overflow, and overlap with elements below. **Fix the width first** by widening the box to fit the text on the intended number of lines. Only then calculate the height based on `font_size × 1.3 × actual_line_count`. Common anti-pattern: a 472pt-wide box for a 44pt bold title "THE PERFECT BREW" — that's ~12 chars × 44 × 0.7 = 369pt (fits), but "THE PERFECT BREW EXPERIENCE" at 27 chars × 44 × 0.7 = 831pt (wraps). Always check. Never guess frame sizes. For each paragraph, sum the widths of ALL runs to get the paragraph width, then compute `ceil(para_width / frame_width)` to get the wrapped line count, then derive height from total lines. Use `word_wrap=False` for single-line elements. See the [Text Frame Sizing](#text-frame-sizing) section in python-pptx Reference.
16. **Surgical fixes only.** When fixing a bug (e.g., text overflow, overlap), change ONLY what's needed to fix that bug. Preserve all existing design decisions — border colors, accent bar direction, radius, opacity, card style, font sizes, spacing. Never redesign an element while fixing it. A fix that introduces a new visual inconsistency is not a fix.
17. **Separate decorative elements from content.** Decorative elements (slide numbers, icons, accent shapes) must have clear spatial separation from content text (titles, body). Never place a decorative element in the same quadrant at a similar position to a title — they will visually crowd each other. Ensure no horizontal or vertical overlap between decorative and content elements.
18. **Use moderate corner radius on content cards.** Rounded rectangle `adj` values: 3000 = barely visible, 10000 = moderate/pleasant, 16667 = default, 50000 = pill shape. Use `adj=10000` as the default for content cards. Pill shape (50000) is almost always too extreme for rectangular content cards.
19. **NEVER shrink a background image into a content thumbnail.** If an image was generated at 16:9 ratio (background dimensions), it MUST be placed as a full-bleed background covering the entire slide, or as a wide panoramic strip. Placing a 16:9 image as a small 5"x3" content image is a **composition failure** — it wastes the image, looks awkward, and defeats the purpose of composition planning. Match image generation dimensions to placement dimensions: full-bleed backgrounds get 16:9, side panels get portrait/square ratios, content thumbnails get ratios matching their actual slot size. **If you catch yourself placing any image at <30% slide coverage, stop and ask: was this image generated for this role?**
20. **ALL background images must be visually consistent across the deck.** Same color temperature (all dark OR all light OR all warm — never mixed), same visual style (all photo OR all abstract OR all illustrated — never mixed), same complexity level, same palette range. Define a "Global BG identity" sentence in Step 3a and include it verbatim in EVERY image generation prompt. If a generated image breaks the consistency (e.g., comes out bright when the deck is dark), regenerate it — do NOT proceed with a mismatched BG.
21. **BG images must be content-aware, not just "leave blank space."** The image's subjects and composition should reflect what the slide's text is about. A comparison slide needs a visually split image. A growth slide needs upward energy. A competition slide needs two subjects facing off with a gradient zone between them for overlay text. The image and the text overlay are ONE design telling ONE story — design them together, not independently. When the image can't create natural text zones through content arrangement alone, first try regenerating with stronger negative space directives. Only as a last resort, use a subtle PPTX gradient overlay (see Rule 25).
22. **NEVER distort images — always preserve native aspect ratio.** `slide.shapes.add_picture(path, left, top, width, height)` STRETCHES the image to fit the given W×H regardless of native AR. If the image's native aspect ratio doesn't match the target box, the image gets visually compressed/stretched — this is immediately obvious and unprofessional. **Rules:** (a) For **full-bleed backgrounds only** (16:9 image → 16:9 slide), specifying both W and H is safe because ARs match. (b) For **ALL other placements** (side panels, content images, card images), you MUST use `add_picture_fit()` from the [python-pptx Reference](references/python-pptx-reference.md) — it fits the image within a bounding box while preserving native AR. (c) Before placing ANY non-background image, verify AR compatibility with `check_image_ar(path, target_w, target_h)`. (d) The audit (CHECK 12) catches distortion post-build, but prevention at code-writing time is mandatory — do not rely on the audit as the only safeguard. (e) If an image was generated at 16:9 and the target placement is a portrait panel, do NOT force it into the panel — either use it as a full-bleed background or regenerate at the correct ratio.
23. **Card accent bars must be INSIDE the card boundary.** When adding a decorative accent bar to a card (top-bar, side-bar), position it inset within the card's bounding box — never floating above or detached from the card. A bar hovering 50px above a card looks like a layout bug. Place it flush at the card's top edge (inset by the corner radius if rounded) or as a thin strip inside the card's top/left padding area. The bar should visually belong to the card, not be a separate disconnected element.
24. **If most slides have BG images, ALL slides must.** When a deck uses full-bleed background images on >50% of slides, every remaining slide must also have a BG image. A deck mixing 8 rich image slides with 2 plain gradient slides looks visually inconsistent — the gradient slides stick out as obviously cheaper/different. Either commit to BG images on ALL slides or NONE. During the composition plan (Phase 3), if you mark any slide as "No image," validate that it won't break visual consistency with the image slides.
25. **NEVER use full-slide overlays. Use targeted gradient shapes OR no overlay.** Full-slide semi-transparent rectangles wash out the entire background image uniformly, blocking its visual message and defeating the purpose of using BG images. Instead:
   - **Text directly on BG image?** Add a targeted gradient shape (via `add_gradient_shape()`) covering ONLY the text zone — fading from dark (where text sits) to transparent (where the image shows). This preserves the image's focal point.
   - **Text inside opaque cards/panels (KPI, data tables)?** Add NO overlay at all. The cards have solid fills and handle their own contrast. The BG image shows through the gaps between cards — this is the whole point. Overlaying it provides zero readability benefit and just washes out the visual message (e.g., a satellite map of the Strait of Hormuz that IS the story).
   - **Bottom line:** the BG image's visual content is a design asset, not decoration. Protect it from unnecessary coverage.
26. **Pre-calculate text box width to prevent wrapping.** Before creating any text box, compute the rendered width of its longest text line using `font_size × 0.6 × char_count` (use 0.7 for bold fonts). If the rendered width exceeds the planned box width, widen the box — do NOT let text wrap unexpectedly. Unexpected wrapping is the #1 cause of cascading layout bugs: wrapped text increases height → overflows the box → overlaps elements below → triggers audit criticals. Prevention at creation time is 10× cheaper than fixing after the fact.

27. **NEVER write custom gradient fill code — use `add_gradient_shape()`.** Writing your own lxml code to add `<a:gradFill>` to shapes is the #1 cause of "mystery blue rectangles" in presentations. The bug: `etree.SubElement(spPr, ...)` can silently attach the element to the wrong XML parent (`<p:sp>` instead of `<p:spPr>`), and the shape's `<p:style>` theme reference (`accent1` = blue) takes over. **The ONLY correct way to add a gradient fill to a shape is `add_gradient_shape()` from [python-pptx Reference](references/python-pptx-reference.md).** It handles theme override (`shape.fill.solid()` first), element removal, and OOXML schema ordering. If you ever find yourself writing `etree.SubElement(..., 'gradFill')` or `etree.SubElement(..., qn('a:gradFill'))` outside of `add_gradient_shape()`, STOP — you are about to create a blue rectangle. Copy-paste `add_gradient_shape()` instead.

28. **BG images require dark tone + targeted gradient shapes for text contrast.** When using full-bleed background images, the contrast strategy is: (a) Generate dark/moody BG images — never bright or airy. (b) Add targeted `add_gradient_shape()` elements covering ONLY the text zones — fading from dark (opaque end at text) to transparent (toward image focal point). (c) Use light text colors (white, cream, gold). (d) EXCEPTION: skip all overlays on slides where content is inside opaque cards/panels (KPI cards, data tables) — the cards handle their own contrast and the BG image should show through freely. This rule replaces the old "generate images with built-in negative space" approach, which was unreliable because AI image generators can't precisely control dark zones.

## References

Detailed reference documentation is split into focused files. Read the relevant file when needed:

- **[python-pptx Reference](references/python-pptx-reference.md)**: Complete API reference — imports, opening/saving, shapes, text boxes, tables, charts, images, gradients, transparency, rounded corners, helper functions (`make_title_page()`, `make_chapter_divider()`, `make_narrative_page()`, `make_quote_page()`, `make_comparison_page()`, `make_kpi_card()`), overlap checker, audit code. **Read this before writing any python-pptx code.**
- **[AppleScript Reference](references/applescript-patterns.md)**: App lifecycle and navigation commands — the reload pattern (critical), presentation lifecycle, navigation, slideshow control, read-only inspection, screenshot triggers, unit system. Includes a deprecated "legacy live edit" section explaining why those patterns were demoted. **Read this ONLY for app control — never for editing. All editing goes through python-pptx.**
- **[Design System](references/design-system.md)**: Typography rules, color palettes (dark premium, light clean, warm earth, bold vibrant, tropical dark), layout rules, decorative elements, image generation capability (prompts, workflow, strategy, layering), **Layout Type Catalog** (11 layout types: Title Page, Chapter Divider, Narrative Page, Quote Page, Full-Bleed Image, KPI Cards, Comparison, Timeline, Data Table, Diagram, Grid/Mosaic), **Layout Type Matching Guide** (decision tree + anti-patterns), **Image Composition Patterns** (10 patterns for image-overlay coordination), layout rhythm, theme pairing, composition prompt engineering, EMU conversions. **Read this when planning a new deck's visual design — especially the Layout Type Catalog for choosing the right layout per slide.**
- **[Design Styles Catalog](references/design-styles-catalog.md)**: 12 curated design styles (STYLE-01 through STYLE-12) with full layout, typography, color palette, and graphic treatment specs for each. Styles range from Strategy Consulting (McKinsey) to Retro Risograph. **Read this when the user requests a specific style or you're recommending one.**
- **[Style → python-pptx Mapping](references/style-pptx-mapping.md)**: Concrete RGBColor values, font configs, accent bar settings, card/tile parameters, and design notes for each of the 12 styles. **Read this alongside the Design Styles Catalog to get implementation-ready values.**
- **[Audit System](references/audit-system.md)**: Mandatory post-generation quality audit — 12 checks (bounds, text clipping, word-wrap, container sync, bullet alignment, overlap, z-order, font compliance, spacing, color integrity, style compliance, **image AR distortion**), iterative fix loop (max 5 passes), cascading fix strategies, word-wrap simulation, bullet layout algorithm, false positive avoidance. **Read this before running the mandatory audit after building slides.**
