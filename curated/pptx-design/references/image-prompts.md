# Image Prompt Engineering

How to write AI image generation prompts for PPTX slides. The image and the PPTX overlay are ONE composition — design them together, not separately.

## Table of Contents

1. [Default: No Background Images](#default-no-background-images)
2. [BG Image Contrast Strategy](#bg-image-contrast-strategy)
3. [Subject-Side Placement — The Anti-Collision Rule](#subject-side-placement--the-anti-collision-rule) ← **READ if images have human/portrait subjects**
4. [Section A — Full-Bleed BG Prompts](#section-a--full-bleed-bg-prompts)
5. [Section A2 — Side Panel (30-50%) Prompts](#section-a2--side-panel-3050-prompts)
6. [Section B — Content Image Prompts](#section-b--content-image-prompts)
7. [Section C — Prompt Quality Checklist](#section-c--prompt-quality-checklist)
8. [Section D — Post-Generation AR Verification](#section-d--post-generation-ar-verification)
9. [The `generate_and_verify` Pattern](#the-generate_and_verify-pattern)

---

## Default: No Background Images

**By default, do NOT use background images.** Use solid color / gradient backgrounds from the active style palette. Background images add complexity (overlay management, contrast issues, image-text coordination) that isn't always needed.

**Only use BG images when the user explicitly requests them** — e.g., "with bg image", "add background images", "use photos", "cinematic slides", etc.

---

## BG Image Contrast Strategy

The mandatory approach when BG images are in use:

1. **Generate DARK / non-bright images.** All BG images must be dark, moody, atmospheric. Never generate bright, light, or airy backgrounds — they create text contrast nightmares.

2. **Add targeted gradient shapes** (NOT full-slide overlays) where text sits. Use `add_gradient_shape()` (or `add_bg_image(..., text_zone=...)` which wraps it) to create gradient fade zones that transition from dark (where text lives) to transparent (where the image should show through). These are narrow, targeted shapes — not full-slide tinted rectangles.

3. **Use light/white/cream text colors** for text overlaid on dark BG images.

4. **EXCEPTION — Opaque card/panel slides (KPI cards, data tables, etc.):** If the slide's content elements are opaque cards with solid fills, do NOT add ANY overlay — not even targeted gradients. The cards handle their own text contrast via their opaque fill. The BG image shows through in the gaps between cards, which is the whole point. Adding an overlay just washes out the BG for zero readability benefit.

```
BG Image Contrast Decision Tree:

Is the slide content in opaque cards/panels?
  YES → No overlay. Cards handle contrast. BG image shows freely.
  NO  → Text directly on BG image?
    YES → Add targeted gradient shape(s) where text sits.
          Gradient: dark end at text zone → transparent toward image focal point.
    NO  → No overlay needed.
```

**NEVER use full-slide semi-transparent overlay rectangles.** They wash out the entire image uniformly, reducing visual impact — defeats the purpose of using BG images at all.

---

## Subject-Side Placement — The Anti-Collision Rule

**This section enforces Rule 27 at the prompt layer.** It exists because of a real bug: slide 2 and slide 4 of Elena's personal bio deck had their gradient shapes fading *directly over her face/body*, because the image prompt declared a text zone, the build code declared a different text zone, and the two drifted apart. Rule 27 forbids this; this section tells you how to write prompts that make the bug impossible.

### Step 1 — Declare Subject Bbox, NOT text zone, in the prompt

When writing a side-panel or portrait-subject BG prompt, describe **where the subject sits inside the generated image frame**. Do NOT describe where the slide's text will go.

✅ **Correct:**
> "Subject positioned in the LEFT THIRD of the frame, sharp focus on her profile. Right two-thirds: out-of-focus warm bokeh of harbor lights."

❌ **Wrong (pre-commits text placement inside image prompt):**
> "Subject on left, leaving the RIGHT two-thirds as negative space for typography overlay."

The difference matters. The first is a fact about the photo — it remains true no matter which slide the image ends up on. The second bakes a slide-layout assumption into the image — and that assumption collides with whatever the build code decides.

### Step 2 — Panel Side is DERIVED from Subject Bbox

Once you know the Subject Bbox, the slide panel side is automatic:

| Subject Bbox in generated image | Slide panel side | Where subject ends up on slide | Where gradient sits |
|---|---|---|---|
| `left-third` | **LEFT** half of slide | Outer-left edge (clear, no overlay) | Inner-right edge of image panel, fading transparent→opaque going left-to-right |
| `right-third` | **RIGHT** half of slide | Outer-right edge (clear, no overlay) | Inner-left edge of image panel, fading opaque→transparent going left-to-right |
| `center` | Full-bleed | Center of slide | Corner gradients only, opposite any typography zone |
| `full-bleed` (no subject) | Full-bleed | n/a | Wherever the text zone sits, fading away from the (absent) focal point |

**The invariant:** the subject always lands at the *outer* edge of the slide; the gradient always sits on the *inner* edge where text meets image.

### Step 3 — Gradient fades AWAY from subject

For a side-panel layout, the gradient rectangle sits on the inner edge of the image panel. Its opacity stops are:

- **Opaque end (95-100%)** = the inner edge, meeting the text column cleanly
- **Transparent end (0%)** = the outer edge, where the subject lives

In python-pptx terms, for a LEFT-half image panel with a LEFT-third subject:

```python
add_gradient_shape(
    slide,
    left=image_panel_width - Emu(2000000),  # sit on INNER-RIGHT edge of panel
    top=0,
    width=Emu(2000000),
    height=SLIDE_H,
    colors=[(10, 10, 12), (10, 10, 12)],
    alphas=[0, 100000],   # transparent at outer, OPAQUE at inner — AWAY from subject
    angle=0,              # horizontal L→R fade
)
```

For a RIGHT-half image panel with a RIGHT-third subject, mirror it: gradient sits on the inner-LEFT edge of the panel, `alphas=[100000, 0]`.

### Step 4 — Pre-ship sanity check

Before declaring a BG-image slide done, mentally overlay the image panel and the gradient shape:

1. Where is the subject in the image? (left-third / center / right-third)
2. Where does the subject land on the slide? (outer-left / center / outer-right)
3. Where does the gradient's opaque region sit on the slide?

If the gradient's opaque region overlaps the subject's screen position by more than ~10%, the design is broken. The fix is ALWAYS one of two operations, never a regeneration:

- **Swap the panel side.** Move the image panel from left to right (or vice versa). Text column moves to the other side. Gradient direction flips. This is almost always the right fix.
- **Flip the gradient direction.** Less common — only if the panel side is constrained for other reasons.

This is exactly the fix that was applied to the Elena bio deck slides 2 and 4: image panels swapped sides, gradients flipped, zero image regeneration needed.

### Step 5 — Worked examples of correct prompt phrasing

**Side panel, subject on LEFT side of image → image panel on LEFT of slide:**
> "Editorial portrait, elegant woman in tailored Chanel tweed, Monte-Carlo harbor at golden hour. **Subject positioned in the LEFT THIRD of the frame in sharp focus, her body angled toward the right. Right two-thirds: out-of-focus warm bokeh of harbor lights.** 3:4 portrait aspect ratio. No text, no logos."

**Side panel, subject on RIGHT side of image → image panel on RIGHT of slide:**
> "Intimate candlelit restaurant scene, elegant woman in crimson Valentino silk, Michelin-star dining room. **Subject positioned in the RIGHT THIRD of the frame, seated at the table in warm key light. Left two-thirds: mahogany-paneled wall fading into dark candlelit shadow with soft bokeh of crystal glasses.** 3:4 portrait aspect ratio. No text, no logos."

**Full-bleed with center subject:**
> "Dramatic runway photograph, elegant woman seated front-row in black Dior couture. **Subject centered, theatrical spotlights overhead, runway extending into atmospheric darkness on both sides.** 16:9 widescreen. No text, no logos."

Notice what's absent from all three: no mention of "leave space for typography," no mention of "text zone," no slide-layout terminology. The prompts describe photographs. The build layer handles typography.

---

## Global Image Strategy (Before Generating Any Image)

When the user wants BG images, declare ONE global identity for the whole deck and enforce it on EVERY image prompt:

```
Global BG identity: "Dark moody abstract gradients with deep navy (#0A1628) to
black, subtle geometric mesh patterns, warm gold (#D4A853) accent glows. Minimal
complexity, no recognizable objects — pure atmosphere."
```

**Cross-slide consistency rule:** All BG images must share:
- **Same color temperature** (ALL dark, ALL warm, etc. — never mixed)
- **Same visual style** (ALL photo, ALL abstract, ALL illustrated)
- **Same palette range** (name 2-3 hex colors in every prompt)
- **Same complexity level**

Mixing a bright sunny BG on slide 3 with a dark moody BG on slide 7 is a composition failure. Commit to ONE tone and enforce it.

---

## Section A — Full-Bleed BG Prompts

Background images are the FOUNDATION of the slide. The PPTX overlay text will sit on top. The image must be designed to RECEIVE text, not compete with it.

### Mandatory Prompt Components

1. **NO TEXT IN THE IMAGE.** Always include: "No text, no words, no letters, no typography, no labels, no watermarks — purely visual."

2. **Negative space directives.** Specify WHERE on the image the PPTX text will be placed, and instruct the AI to leave that zone visually quiet:
   - "Leave the [bottom third / left 40% / center] dark and uncluttered for text overlay"
   - "Compose with negative space in [zone] — muted tones, soft gradients, or out-of-focus areas"
   - "The visual subject/focal point should be in [opposite zone from text]"

3. **Color/tone harmony with PPTX style.** Name 2-3 colors from the active palette:
   - Dark styles: "Dark moody tones, deep shadows, warm undertones"
   - Light styles (STYLE-01): "Bright, clean, high-key lighting, white/grey negative space"
   - Warm styles (STYLE-02): "Warm cream and earth tones, soft editorial lighting"

4. **Visual style matching** the deck's design language:
   - STYLE-01 (Strategy): Clean, corporate photography, minimal, geometric
   - STYLE-04 (Kawaii): Soft pastel illustration, cute, rounded shapes
   - STYLE-06 (Anime): Dramatic cinematic anime art, rich detail

5. **Composition pattern directive** based on the slide's text layout:
   - Title bottom-third text → "Subject centered or upper third, bottom fades to dark gradient"
   - Left-side text panel → "Visual interest concentrated on the right 60%, left side is atmospheric/blurred"
   - Center quote text → "Frame the center with visual elements at edges, center is moody open space"

6. **Content-aware image composition.** The image's CONTENT must reflect the slide's message — not just leave generic blank space. The image and the overlay text tell ONE story together:
   - If the slide compares two things, the image should visually split into two zones.
   - If the slide is about growth, the image should have upward visual energy.
   - Place image subjects to CREATE natural text zones.

7. **Aspect ratio and resolution.** Always specify: "16:9 aspect ratio, high resolution, widescreen composition"

8. **Dark tone directive.** "Dark, moody, atmospheric tones." Never request bright/airy backgrounds.

### Example Prompt (STYLE-02 Title Slide)

```
Editorial overhead view of an elegant workspace with warm natural lighting.
Warm cream and earth tones matching #FAF7F2 palette. Rich amber highlights
complementing #C8A96E accent color. Subject in upper-center third. Bottom 30%
fades to soft dark warm tones for text overlay. No text, no words, no letters,
no typography. 16:9 aspect ratio, high resolution, editorial photography style.
```

---

## Section A2 — Side Panel (30-50%) Prompts

Side panel images share a visual edge with the text zone. They need composition awareness like backgrounds but are sized like content images (portrait/square ratio, not 16:9).

### Mandatory Prompt Components

1. **NO TEXT IN THE IMAGE.** Same rule as backgrounds.

2. **Portrait or near-square aspect ratio.** Side panels are tall, not wide:
   - Right-side panel (55% width): "3:4 portrait aspect ratio" or "2:3 portrait"
   - Left-side panel (45% width): "3:4 portrait" or "4:5 near-square"
   - **NEVER 16:9** — that is backgrounds only. A 16:9 image forced into a portrait panel is the #1 distortion bug.

3. **Adjacent-edge negative space.** The edge of the image that borders the text zone must be visually quiet — NOT the focal point:
   - Right panel with text on left → "Subject on the right side of the frame, left edge fades to [dark/blurred/atmospheric] for clean transition to text zone"
   - Left panel with text on right → "Subject on the left, right edge fades to [dark/soft] for clean visual boundary"
   - **The focal point goes AWAY from the text edge, not toward it.**

4. **Color/tone harmony with slide background.** The image's overall tone should complement the slide's background color at the shared edge. Name 2-3 hex colors from the active palette.

5. **Visual style matching** — same as Section A.

6. **Subject composition for tall frames.** Portrait orientation changes composition rules:
   - "Subject centered vertically, filling 60-80% of the frame height"
   - Avoid wide landscape subjects (cities, panoramas) — they'll be tiny
   - Prefer subjects that work vertically: portraits, architecture, tall objects, abstract vertical compositions

### Example Prompt (STYLE-02 Right Panel, 55% Width)

```
Close-up portrait of a professional in a modern office, warm natural lighting.
Warm cream tones matching #FAF7F2, amber highlights complementing #C8A96E.
Subject centered-right in frame, left edge fades to soft warm tones for clean
transition to text zone. 3:4 portrait aspect ratio, high resolution.
No text, no words, no letters, no typography. Editorial photography style.
```

---

## Section B — Content Image Prompts

Content images live INSIDE the layout as visual elements alongside text. They must be PPTX-design-aware. Only use when the user explicitly requests "in-slide illustrations" / "content images" / "images inside cards".

### Mandatory Prompt Components

1. **Style/theme coherence.** The illustration style must match the deck's design system:
   - Use the active style's color palette
   - Match the design language: flat/minimal for corporate, illustrated for creative, photorealistic for editorial
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

4. **Visual weight and scale.** Content images are subordinate to text:
   - "Clean, simple composition with clear subject and minimal surrounding detail"
   - Subject fills 60-80% of the frame (no tiny subject in vast empty space)

5. **No text in image.** "No text, no labels, no watermarks — purely visual."

6. **Consider adjacent PPTX elements.** If text wraps around the image:
   - "Subject facing [toward/away from] text side" (subjects should face toward the content)
   - "Visual weight on [side closest to text]" to create visual connection

### Example Prompt (STYLE-05 Product Card)

```
Minimalist icon illustration of a robot assistant. Flat design style with blue
(#2563EB) and slate grey (#64748B) tones on a white background (#FFFFFF). Clean,
geometric, no text. 1:1 square aspect ratio. Simple and modern, matching corporate
professional aesthetic.
```

---

## Section C — Prompt Quality Checklist

Run this before EVERY image generation call:

- [ ] **No-text directive** ("No text, no words, no letters, no typography")
- [ ] **Aspect ratio** matching the image role (16:9 BG / portrait side panel / slot-ratio content)
- [ ] **Color harmony** — 2-3 hex colors from active style palette mentioned
- [ ] **Visual style** matching the deck's design language
- [ ] **Global BG identity** (if BG image) — verbatim inclusion from Step 3a
- [ ] **For BG images:** Dark/moody tone directive — never bright/airy
- [ ] **For BG images:** Negative space zone specified matching text placement
- [ ] **For side panels:** Portrait/near-square ratio (3:4, 2:3) — NEVER 16:9
- [ ] **For side panels:** Adjacent-edge negative space (edge near text zone is quiet/dark/blurred)
- [ ] **For side panels:** Subject composition works in portrait orientation (no wide panoramas)
- [ ] **For content images:** Background color matching card/slide surface
- [ ] **For content images:** Subject scale appropriate (fills 60-80% of frame)
- [ ] **Composition direction** — focal point placement specified
- [ ] **For prompts with a human/portrait subject:** Subject Bbox is declared (`left-third` / `center` / `right-third`) and the prompt does NOT pre-commit a slide text zone — see [Subject-Side Placement](#subject-side-placement--the-anti-collision-rule) and Rule 27
- [ ] **Panel Side matches Subject Bbox side** in the composition plan (side-panel layouts only)

---

## Section D — Post-Generation Verification (AR + Text Zone Luminance)

**Image gen tools lie about both AR and content.** AR may be ignored by the model. The "leave bottom 30% dark" directive may be partially followed but produce bright pixels where the text will sit. Two-stage verification — AR first, then **text-zone luminance** — catches both.

After each image is generated, run `verify_generated_image(..., text_zone=..., text_color=...)` from [python-pptx Reference](python-pptx-reference.md#embedded-helper-functions):

```python
from pptx_helpers import verify_generated_image

# For a full-bleed BG with white text in the bottom 35%:
ok, details, msg = verify_generated_image(
    'slide1_bg.png',
    intended_role='full-bleed',
    intended_ar=1.78,
    text_zone={'zone': 'bottom', 'size': 0.35},
    text_color='white',
)
if not ok:
    print(f"⚠️ {msg}")
    # Decision tree below → REGENERATE, adapt role, or add gradient shape
else:
    print(f"✅ {msg}")  # → proceed with placement
```

**Two stages of verification:**

1. **AR check** — does the image's pixel AR match the intended role? Mismatch >15% → regenerate.
2. **Text-zone luminance check** — if `text_zone` is provided, crop that region and verify mean luminance. For white/cream text, zone must be ≤140/255 grayscale. For dark text, ≥115/255.

**When to pass `text_zone`:**
- Full-bleed BG with text directly on the image → YES, always
- Side panel images (text lives on the opposite slide side, not on the image) → omit
- Content images inside opaque cards → omit (card handles contrast)
- Full-bleed BG with content in opaque cards → omit (cards handle contrast)

### Decision Tree on Failure

**AR mismatch:**
1. <10% deviation → Accept; `add_picture_fit()` handles it.
2. 10–25% → Regenerate once with a stronger AR directive in the prompt.
3. >25% → Regenerate with completely reworded orientation directive, OR adapt the Image Role.
4. After 2 failed regens → stop fighting the model; change the Image Role in the composition plan.

**Text-zone luminance fail (zone too bright for white text):**
1. **First try**: add a targeted gradient shape via `add_bg_image(..., text_zone=...)`. Zero API cost, usually sufficient. Proceed with placement.
2. **If gradient isn't enough** (image's focal-point bleed-through still washes text): regenerate with "CRITICAL: the [bottom|left|etc.] 35% MUST be dark, deep shadow, low luminance, suitable for white text overlay."
3. **After 2 failed regens**: swap the text zone to a darker part of the image (bottom → top, left → right), OR change text color to dark if the design allows.

---

## Pilot-First Then Batch-of-3 (Canonical Pattern)

**Do NOT batch-generate all images at once.** A systemic prompt bug (wrong palette hex, missing directive) will faithfully reproduce across all parallel calls, burning API cost and time. Instead: pilot-first with the template, then batches of 3 max.

### Workflow

```
Step 1: PROMPT PREVIEW (Phase 3c, BEFORE any API call)
  Show all N prompts to the user in a table with:
    # | Role | AR | Text Zone | Focal | Full Prompt Text
  Wait for approval/edits. Once approved, prompts are frozen.

Step 2: PILOT (slide 1 only, serial)
  - Generate slide 1's image with the approved prompt.
  - verify_generated_image(..., text_zone=..., text_color=...)
  - Show user the result (path + verification report).
  - If bad: adjust the prompt TEMPLATE (not just slide 1's prompt), regenerate slide 1.
  - If good: proceed to Step 3 with template frozen.

Step 3: BATCHES OF 3 (parallel for API tools, serial for browser tools)
  For each batch:
    - Launch 3 parallel API calls with the frozen template.
    - After all 3 return: verify ALL 3 (AR + text-zone luminance).
    - Handle regens for any failures before starting next batch.
    - Update the build's task list: mark batch completed, next batch in_progress.
  Repeat until all images done.
```

### Reference Implementation

```python
def generate_and_verify(prompt, intended_role, intended_ar, out_path,
                         text_zone=None, text_color='white', max_retries=2):
    """Generate one image with verify + retry loop.

    Pseudocode — `invoke_image_tool()` is whichever AI image skill is available
    (nanobanana, seedance-api, etc.). The verify-and-retry loop is what's
    important.
    """
    from pptx_helpers import verify_generated_image

    current_prompt = prompt
    for attempt in range(max_retries + 1):
        invoke_image_tool(current_prompt, out_path)  # external — nanobanana, etc.

        ok, details, msg = verify_generated_image(
            out_path, intended_role, intended_ar,
            text_zone=text_zone, text_color=text_color,
        )
        if ok:
            return out_path, details

        if attempt < max_retries:
            # Build a stronger directive based on WHICH verification failed
            strengthening = []
            if not details['ar_ok']:
                strengthening.append(orientation_directive(intended_ar))
            if details.get('zone_ok') is False:
                strengthening.append(
                    f"CRITICAL: The {text_zone['zone']} "
                    f"{int(text_zone['size']*100)}% of the image MUST be dark, "
                    f"deep shadow, low luminance — suitable for {text_color} text overlay."
                )
            current_prompt = f"{prompt}\n\n" + "\n".join(strengthening)
        else:
            raise RuntimeError(
                f"Verification still failing after {max_retries+1} tries: {msg}. "
                f"Consider: (a) add_bg_image(text_zone=...) to darken the zone with "
                f"a gradient shape, (b) swap text_zone to a darker image region, "
                f"(c) change text_color if design allows."
            )
    return out_path, details


def orientation_directive(intended_ar):
    if intended_ar > 1.4:
        return "The image MUST be WIDER than tall, 16:9 landscape, approximately 1920x1080px."
    elif intended_ar < 0.85:
        return "The image MUST be TALLER than wide, 3:4 portrait, approximately 768x1024px."
    else:
        return "The image MUST be approximately square, 1:1, approximately 1024x1024px."
```

### Why Batches of 3 (Not 4, Not 10)

- **3 is the blast-radius cap.** If a prompt template is systemically wrong, 3 wasted calls is acceptable; 10 is not.
- **3 fits comfortably in one verification pass** — Claude can inspect all 3 results, decide next steps, update tasks, and move on in a single response.
- **After-batch verification is non-negotiable.** Never launch batch N+1 without verifying batch N. If any image fails, regen it before the next batch launches.

### Parallel vs Serial

| Tool type | Strategy |
|---|---|
| API-based (`nanobanana`, `seedance-api`, `acestep`) | Parallel within each batch of 3 |
| Browser-based (`grok-image-gen`) | Strictly serial (one Chrome session) |

### Prompt Preview Gate (MANDATORY)

Phase 3c in SKILL.md requires showing all N prompts to the user BEFORE any image-gen tool call. Do not skip this. "Prompt approved by proxy via composition plan approval" is not sufficient — the user must see the full verbatim prompt strings.

---

## Image Prompt Anti-Patterns

- **Generic negative space** instead of content-aware composition. Asking for "dark area on the left for text" without connecting the image's CONTENT to the slide's MESSAGE. The image should visually support what the text says — subjects positioned to create meaning with the overlay.
- **Mixed BG tones across slides.** Dark abstract on slide 2, bright photo on slide 4. Breaks the deck's visual identity.
- **Bright/airy BG images with heavy overlays.** The old "fix it with overlay" approach. Start dark — never compensate with a full-slide wash.
- **16:9 image placed in a side panel.** Horizontally compresses the image. CHECK 12 catches this, but prevent at prompt time by specifying portrait ratio explicitly.
- **Content image with a busy background** that clashes with the card surface. Always request a solid or transparent background.
