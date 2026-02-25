---
name: pptx-design-agent
description: "Expert PowerPoint design agent for macOS using python-pptx and AppleScript. Creates and edits stunning, professional presentations with premium design quality. Use when: (1) Creating new PowerPoint presentations from scratch with python-pptx, (2) Editing or redesigning existing .pptx files, (3) Building slide decks with custom design (gradients, cards, KPI panels, charts, tables), (4) Live editing presentations via AppleScript IPC (text, fonts, positions, fills, z-order, visibility, rotation, shadows, speaker notes), (5) Refreshing/previewing presentations live in PowerPoint on macOS, (6) Generating AI images for slide backgrounds and content, (7) Any task requiring python-pptx code generation with design best practices."
---

# PowerPoint Design Agent

Expert PowerPoint design agent on macOS. Creates and edits professional presentations using `python-pptx` + `lxml` for slide building, AppleScript for **live IPC editing**, and AI image generation for visual content.

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
  • See the full list of all 13 styles with descriptions?
  • Pick a different style by name or number?
```

**Wait for user response. Do not silently default.**

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
| Narrative (tech showcase, premium dark) | STYLE-13 (Premium Dark Editorial) |
| Generic / unclear | STYLE-02 (default) |

**If NONE of the 13 styles fit the user's content**, generate a **custom style** on the fly:

1. Analyze the content's tone, audience, and subject matter.
2. Design a bespoke style dict with: `slide_bg`, `fonts` (title, body, optional extras), `palette` (5-8 colors), `accent_bar` (optional), and `design_notes`.
3. Present it to the user:
```
None of the 13 preset styles are a great fit for your content. I've designed a custom style:

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

#### Default Behavior (user says "yes" to images or "add images" without specifying)

**Default to full-bleed background images.** Do NOT ask — just proceed with backgrounds unless the user explicitly says otherwise.

```
I'll use AI-generated full-bleed background images for key slides.
Here's my image composition plan:
[present plan]
```

#### When User Explicitly Requests Content Images

If the user says "in-slide illustrations", "content images", "images inside cards", "not backgrounds" — switch to content image mode. See **Content Image Prompt Rules** below.

#### When to Ask

Only ask if the user's intent is genuinely ambiguous:

```
Would you like AI-generated images for the slides?

  • Yes, full backgrounds (Recommended) — HD images as full-bleed slide
    backgrounds with text overlaid on composed negative space zones.
  • Yes, as content images — In-slide illustrations placed alongside text,
    inside cards, or as visual elements within the layout.
  • Yes, mixed — Some slides get backgrounds, others get content images.
  • No — Solid color / gradient backgrounds from the style palette only.
```

If the user says **yes** (any mode), you MUST complete a **Global Image Strategy** and a **Per-Slide Composition Plan** before generating any image.

#### Step 3a: Global Image Strategy

```
Image Mode: [full-bleed backgrounds (default) | content images | mixed]
Primary image style: [photorealistic | illustrated | abstract | etc.]
Deck palette integration: [dark images + light text | light images + dark overlay | etc.]
Layout rhythm pattern: [alternating | progressive | content-driven | grouped]
BG tone consistency: [dark moody | light airy | warm earth | cool tech | vibrant neon]
Text zone strategy: [image-level negative space | PPTX gradient overlay | mixed]
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
| # | Layout Type | Image Role | Composition Pattern | Image Concept | Focal Point | Text Zone | Image Dimensions |
|---|-------------|------------|---------------------|---------------|-------------|-----------|------------------|
| 1 | Title Page | Full-bleed BG | Bleed + Gradient Fade | [scene] | Center | Bottom 30% gradient | 16:9 full-slide |
| 2 | Narrative | Side panel | Split Left-Right | [scene] | Right 55% | Left 45% | 7:5 right-half |
| 3 | Quote Page | Full-bleed BG | Center Stage | [scene] | Center | Side panels 20% each | 16:9 full-slide |
| 4 | Comparison | No image | — | — | — | — | — |
| ... | ... | ... | ... | ... | ... | ... | ... |
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
   - For dark styles (STYLE-13): "Dark moody tones, deep shadows, warm undertones matching #0C0C0E background"
   - For light styles (STYLE-01): "Bright, clean, high-key lighting, white/grey negative space"
   - For warm styles (STYLE-02): "Warm cream and earth tones, soft editorial lighting"
   - **Explicitly name 2-3 colors from the active palette** that the image should harmonize with.

4. **Visual style matching.** The image style must match the deck's design language:
   - STYLE-01 (Strategy): Clean, corporate photography, minimal, geometric
   - STYLE-04 (Kawaii): Soft pastel illustration, cute, rounded shapes
   - STYLE-06 (Anime): Dramatic cinematic anime art, rich detail
   - STYLE-13 (Premium Dark): Moody, luxurious, editorial photography with warm gold highlights

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

8. **Text zone strategy — image negative space vs PPTX gradient overlay.** Two equally valid approaches for creating readable text zones. Choose based on the image:

   **Option A: Image-level negative space** (default for abstract/gradient BGs)
   - The AI generates the image WITH built-in dark/quiet zones matching text placement
   - Best when: abstract backgrounds, simple scenes, controllable compositions
   - Prompt includes: "Bottom 30% fades to near-black for text overlay"

   **Option B: PPTX gradient overlay shapes** (preferred for rich/detailed BGs)
   - Generate a full, visually rich image WITHOUT worrying about text zones
   - Add a PPTX shape (rectangle) with a gradient fill over the text zone:
     - Gradient from `style_bg_color` at 70-85% opacity → fully transparent
     - This creates a smooth dark-to-clear fade that makes text readable without destroying the image
   - Best when: photorealistic scenes, busy compositions, images where you want the FULL visual impact
   - **The gradient overlay can be colored** — use the style's primary bg color for the opaque end

   **Option C: Combined** (best results for cinematic/dramatic slides)
   - Generate the image with SOME negative space tendency (not as extreme as Option A)
   - Add a subtle PPTX gradient overlay (30-50% opacity) for extra text contrast
   - The image does 60% of the work, the overlay does 40%

   **Declare your choice in the Global Image Strategy** (Step 3a) and apply it consistently across the deck. Don't mix Option A on some slides and Option B on others without a clear reason.

**Example prompt for a STYLE-13 title slide:**
```
Moody aerial view of a city at night with warm golden lights reflecting on water.
Dark atmospheric tones, deep blacks matching #0C0C0E. Warm gold highlights
complementing #D4A853 accent color. Subject in upper-center third. Bottom 30% fades
to near-black darkness for text overlay. No text, no words, no letters, no typography.
16:9 aspect ratio, high resolution, cinematic editorial photography style.
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

**Example prompt for a STYLE-13 side panel (right side, 55% width):**
```
Close-up portrait of a professional in a modern office, warm golden lighting.
Dark moody tones matching #0C0C0E, warm highlights complementing #D4A853.
Subject centered-right in frame, left edge fades to deep shadow for clean
transition to text zone. 3:4 portrait aspect ratio, high resolution.
No text, no words, no letters, no typography. Cinematic editorial photography.
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

**Example prompt for a content image in a STYLE-13 agent card:**
```
Minimalist icon illustration of a robot assistant. Flat design style with muted gold
(#D4A853) and warm grey (#9A9AA0) tones on a dark background (#1A1A1E). Clean,
geometric, no text. 1:1 square aspect ratio. Simple and elegant, matching premium
dark editorial aesthetic.
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

## Dual-Engine Architecture

Two engines for manipulating PowerPoint — choose the right one:

- **python-pptx** (file-based): Bulk creation, complex formatting (gradients, corner radius, letter spacing via lxml), images, charts, tables, font colors.
- **AppleScript IPC** (live editing): Text edits, font properties, positions, fills, z-order, visibility, rotation, shadows, speaker notes, slide management — all instant, no reload.

**Golden Rule:** Build with python-pptx, tweak with AppleScript. For edit-only tasks on an open presentation, use AppleScript alone (no python-pptx, no file reload).

See the full decision matrix and all live IPC operations in [AppleScript patterns](references/applescript-patterns.md).

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
7. **Mandatory audit + fix loop** — read [Audit System](references/audit-system.md) and run all checks (1-12) iteratively. Fix cascading issues. Do NOT skip this step. CHECK 12 (image AR distortion) is CRITICAL — it catches stretched/squeezed images.
8. **AppleScript**: Open the file in PowerPoint.
9. **AppleScript**: Navigate through slides to verify visually — check that image focal points are unblocked and text sits in the planned zones.
10. **AppleScript**: Make any live tweaks (text, positions).
11. **AppleScript**: Save.
12. **Report** audit summary to user, then deliver the file path.

### Edit Existing Presentation (Live IPC)

1. AppleScript: Read all slides/shapes/text (enumerate).
2. Decide: minor text edits -> AppleScript. Major redesign -> python-pptx.
3. AppleScript: Make targeted live edits.
4. AppleScript: Save.

### Redesign Existing Presentation

1. AppleScript: Catalog everything (read all shapes/text).
2. Plan new design, palette, image strategy.
3. Generate needed images.
4. python-pptx: Rebuild each slide (clear old, add new).
5. AppleScript: Close and reopen the file.
6. AppleScript: Verify each slide visually.
7. AppleScript: Make live tweaks if needed.
8. AppleScript: Save.

### Quick Fix / Tweak (IPC-Only)

1. AppleScript: Read the target slide/shape.
2. AppleScript: Make the change live.
3. AppleScript: Save.

No python-pptx needed!

## Mandatory Audit — NON-NEGOTIABLE

**Every new or redesigned presentation MUST pass the full audit before delivery. No exceptions.**

The audit is **not optional**, **not skippable**, and **not deferrable**. It runs after all slides are built and before the file is shown to the user.

### What the audit does
Run all 12 checks from [Audit System](references/audit-system.md): bounds, text clipping, word-wrap, container sync, bullet alignment, overlap, z-order, font compliance, spacing, color/fill integrity, style compliance, **image aspect ratio distortion**. Iterate up to 5 passes — fix issues, re-audit, repeat until clean.

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
- **Background-as-thumbnail**: Generating a 16:9 background image but placing it as a small 5"x3" content image covering <20% of the slide. This is the #1 composition failure. If the image is 16:9, it MUST be full-bleed.
- **Monotonous layout**: Using the exact same layout (e.g., text-left + image-right) for all content slides. Vary layout types across slides — use at least 4 different layouts in a 10+ slide deck.
- **Disconnected image-text relationship**: Generating an image without considering where text will be overlaid. Every image prompt must include composition directives specifying negative space zones that match text placement.
- **Copy-paste layout syndrome**: Every slide having text at (0.8", 0.5") and image at (7.8", 2.4"). This screams "no planning." Each slide's layout should be chosen based on its content type, not copy-pasted from a template.
- **Image aspect ratio distortion**: Using `add_picture(path, l, t, w, h)` with both width and height that don't match the image's native AR. A 16:9 image placed in a 3:5 portrait panel gets horizontally compressed — visually obvious and unprofessional. **Prevention:** use `add_picture_fit()` for ALL non-full-bleed placements, and run CHECK 12 in the audit. **Root cause:** `add_picture()` silently stretches to fit the given dimensions without any warning.
- **Inconsistent BG tone across slides**: Generating slide 2's background as a dark moody abstract and slide 5's as a bright airy photo. This makes the deck look like a collage of unrelated slides, not a cohesive presentation. **ALL background images must share the same color temperature, visual style, and complexity level.** Define the global BG identity ONCE in Step 3a and enforce it on every image prompt. If you notice tone drift mid-generation, stop and regenerate the outlier.
- **Generic negative space instead of content-aware composition**: Asking the AI for "dark area on the left for text" without connecting the image's CONTENT to the slide's MESSAGE. The image should visually support what the text says — subjects positioned to create meaning with the overlay, not just blank space for text to sit on. The image and text are ONE composition telling ONE story.

---

## 22 Critical Rules

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
13. **Use AppleScript IPC for quick edits.** Don't rebuild an entire deck when you only need to change one text box. Read -> edit -> save, all live.
14. **Remember the unit difference.** AppleScript uses points (72/inch). python-pptx uses EMUs (914400/inch). Convert: `EMU = points * 12700`.
15. **Always calculate text frame dimensions.** Never guess frame sizes. For each paragraph, sum the widths of ALL runs to get the paragraph width, then compute `ceil(para_width / frame_width)` to get the wrapped line count, then derive height from total lines. Use `word_wrap=False` for single-line elements. See the [Text Frame Sizing](#text-frame-sizing) section in python-pptx Reference.
16. **Surgical fixes only.** When fixing a bug (e.g., text overflow, overlap), change ONLY what's needed to fix that bug. Preserve all existing design decisions — border colors, accent bar direction, radius, opacity, card style, font sizes, spacing. Never redesign an element while fixing it. A fix that introduces a new visual inconsistency is not a fix.
17. **Separate decorative elements from content.** Decorative elements (slide numbers, icons, accent shapes) must have clear spatial separation from content text (titles, body). Never place a decorative element in the same quadrant at a similar position to a title — they will visually crowd each other. Ensure no horizontal or vertical overlap between decorative and content elements.
18. **Use moderate corner radius on content cards.** Rounded rectangle `adj` values: 3000 = barely visible, 10000 = moderate/pleasant, 16667 = default, 50000 = pill shape. Use `adj=10000` as the default for content cards. Pill shape (50000) is almost always too extreme for rectangular content cards.
19. **NEVER shrink a background image into a content thumbnail.** If an image was generated at 16:9 ratio (background dimensions), it MUST be placed as a full-bleed background covering the entire slide, or as a wide panoramic strip. Placing a 16:9 image as a small 5"x3" content image is a **composition failure** — it wastes the image, looks awkward, and defeats the purpose of composition planning. Match image generation dimensions to placement dimensions: full-bleed backgrounds get 16:9, side panels get portrait/square ratios, content thumbnails get ratios matching their actual slot size. **If you catch yourself placing any image at <30% slide coverage, stop and ask: was this image generated for this role?**
20. **ALL background images must be visually consistent across the deck.** Same color temperature (all dark OR all light OR all warm — never mixed), same visual style (all photo OR all abstract OR all illustrated — never mixed), same complexity level, same palette range. Define a "Global BG identity" sentence in Step 3a and include it verbatim in EVERY image generation prompt. If a generated image breaks the consistency (e.g., comes out bright when the deck is dark), regenerate it — do NOT proceed with a mismatched BG.
21. **BG images must be content-aware, not just "leave blank space."** The image's subjects and composition should reflect what the slide's text is about. A comparison slide needs a visually split image. A growth slide needs upward energy. A competition slide needs two subjects facing off with a gradient zone between them for overlay text. The image and the text overlay are ONE design telling ONE story — design them together, not independently. When the image can't create natural text zones through content arrangement alone, use PPTX gradient overlay shapes (rectangle with gradient fill from style bg color at 70-85% opacity to transparent) as an equally valid alternative.
22. **NEVER distort images — always preserve native aspect ratio.** `slide.shapes.add_picture(path, left, top, width, height)` STRETCHES the image to fit the given W×H regardless of native AR. If the image's native aspect ratio doesn't match the target box, the image gets visually compressed/stretched — this is immediately obvious and unprofessional. **Rules:** (a) For **full-bleed backgrounds only** (16:9 image → 16:9 slide), specifying both W and H is safe because ARs match. (b) For **ALL other placements** (side panels, content images, card images), you MUST use `add_picture_fit()` from the [python-pptx Reference](references/python-pptx-reference.md) — it fits the image within a bounding box while preserving native AR. (c) Before placing ANY non-background image, verify AR compatibility with `check_image_ar(path, target_w, target_h)`. (d) The audit (CHECK 12) catches distortion post-build, but prevention at code-writing time is mandatory — do not rely on the audit as the only safeguard. (e) If an image was generated at 16:9 and the target placement is a portrait panel, do NOT force it into the panel — either use it as a full-bleed background or regenerate at the correct ratio.

## References

Detailed reference documentation is split into focused files. Read the relevant file when needed:

- **[python-pptx Reference](references/python-pptx-reference.md)**: Complete API reference — imports, opening/saving, shapes, text boxes, tables, charts, images, gradients, transparency, rounded corners, helper functions (`make_title_page()`, `make_chapter_divider()`, `make_narrative_page()`, `make_quote_page()`, `make_comparison_page()`, `make_kpi_card()`), overlap checker, audit code. **Read this before writing any python-pptx code.**
- **[AppleScript Patterns](references/applescript-patterns.md)**: Full live IPC capability reference — dual-engine architecture, presentation management, slide operations, live text/font/position/fill/z-order/visibility/rotation/shadow editing, speaker notes, comprehensive slide reader, known limitations, unit system, decision matrix. **Read this before any PowerPoint automation or live editing.**
- **[Design System](references/design-system.md)**: Typography rules, color palettes (dark premium, light clean, warm earth, bold vibrant, tropical dark), layout rules, decorative elements, image generation capability (prompts, workflow, strategy, layering), **Layout Type Catalog** (11 layout types: Title Page, Chapter Divider, Narrative Page, Quote Page, Full-Bleed Image, KPI Cards, Comparison, Timeline, Data Table, Diagram, Grid/Mosaic), **Layout Type Matching Guide** (decision tree + anti-patterns), **Image Composition Patterns** (10 patterns for image-overlay coordination), layout rhythm, theme pairing, composition prompt engineering, EMU conversions. **Read this when planning a new deck's visual design — especially the Layout Type Catalog for choosing the right layout per slide.**
- **[Design Styles Catalog](references/design-styles-catalog.md)**: 12 curated design styles (STYLE-01 through STYLE-12) with full layout, typography, color palette, and graphic treatment specs for each. Styles range from Strategy Consulting (McKinsey) to Retro Risograph. **Read this when the user requests a specific style or you're recommending one.**
- **[Style → python-pptx Mapping](references/style-pptx-mapping.md)**: Concrete RGBColor values, font configs, accent bar settings, card/tile parameters, and design notes for each of the 13 styles. **Read this alongside the Design Styles Catalog to get implementation-ready values.**
- **[Audit System](references/audit-system.md)**: Mandatory post-generation quality audit — 12 checks (bounds, text clipping, word-wrap, container sync, bullet alignment, overlap, z-order, font compliance, spacing, color integrity, style compliance, **image AR distortion**), iterative fix loop (max 5 passes), cascading fix strategies, word-wrap simulation, bullet layout algorithm, false positive avoidance. **Read this before running the mandatory audit after building slides.**
