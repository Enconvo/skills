# Scene Patterns — 7 Reusable Archetypes

Scenes are not snowflakes. Nearly every scene in every explainer maps to one of 7 archetypes. Pick the archetype first, then fill in content.

## 1. Title Card

**Job:** Set the tone, name the thing, establish the visual identity.

**Duration:** 4–8s.

**Must contain:**
- The title (one line, display size).
- A kicker or subtitle (one line).
- An anchor decoration (mission patch, brand mark, large numeral, or thematic SVG).
- A metadata stamp (date, location, source, or mission code in mono font).

**Motion:** Anchor decoration scales in. Title slams up. Subtitle slides in. Stamp pulses once. No character-by-character typewriter (feels slow).

**Common mistakes:** cramming a paragraph; using bouncy easing on the title; centering with nothing to give the scene depth.

## 2. Launch / Intro

**Job:** Kick the narrative into motion. Show the first real moment.

**Duration:** 8–14s.

**Must contain:**
- Phase label ("PHASE 01 ·…" or "ACT I ·…" in mono).
- One clear headline (6–10 words max).
- One body line of context.
- A hero visual element (rocket SVG, product shot, map, human subject).
- Live data: counters, timers, status readouts.

**Motion:** Hero visual is continuously animating (counter rolling, rocket rising, map zooming). Label slides in first; headline follows; data ticker materialises last. Element movement is LINEAR while present; do not ease-in-out a position that's meant to keep drifting off-screen.

**Common mistakes:** static hero during a dynamic story moment; counters without `tabular-nums`; too many data points competing with the headline.

## 3. Data / Stat Reveal

**Job:** Deliver a single memorable number or fact.

**Duration:** 5–10s.

**Must contain:**
- A label in small-caps (12–16px, mono, 0.28em tracking).
- The number itself at a display size (90–140px).
- A unit line (km/s, USD, %, tons, seconds).
- A context line ("— the farthest humans have traveled").
- ONE supporting decorative: a curved line, a sparkline, a progress bar, a pulsing marker.

**Motion:** Label appears first, number counts up from 0 (`power2.out`, 1.5–3s), unit materialises, context fades last. Number must end EXACTLY at final value — no bounce, no overshoot.

**Common mistakes:** multiple stats competing in one scene (cut to separate Data Reveal scenes instead); counter without tabular-nums causing digit jitter; number animating past target and settling back.

## 4. Hero Moment

**Job:** The one shot the viewer will remember. Usually halfway through or at 60–70% in.

**Duration:** 8–14s.

**Must contain:**
- Full-frame hero visual (moon, product macro, building, portrait, etc.).
- One hero stat or hero phrase overlaid.
- A secondary supporting element that reinforces scale ("— farthest humans have ever traveled" / "— over 2 million users").
- A clearly distinct visual rhythm vs neighboring scenes (longer hold, slower motion, larger type).

**Motion:** Slow zoom or parallax on hero visual across the full scene (`power1.inOut`). Stat text enters with gravity (slow, weighted). Support text fades last. Optional pulsing marker.

**Common mistakes:** Hero Moment without enough airtime (4s is not a hero); competing overlays obscuring the hero; using the same scene duration as all neighbors — viewer misses the emphasis.

## 5. Figure-Eight / Circular Return

**Job:** Show completion, return, closing a loop.

**Duration:** 8–12s.

**Must contain:**
- A visual that mirrors or reverses Scene 3 or 4 (return trajectory, before/after image, reversed progress bar).
- A headline that names the return ("Gravity brings them home" / "Back where we started, but different").
- A climbing or culminating counter (re-entry velocity, total distance, elapsed time).

**Motion:** Trajectory path draws in the reverse direction from an earlier scene. Counter climbs. Camera or hero element moves toward the frame it started from.

**Common mistakes:** Skipping this archetype for short videos (fine). Using it decoratively without narrative payoff (not fine — if nothing returns, this scene shouldn't exist).

## 6. Split-Screen / Contrast

**Job:** Before vs after, us vs them, problem vs solution.

**Duration:** 6–10s.

**Must contain:**
- A clear 50/50 or 40/60 division of the frame (vertical is more common than horizontal for 16:9).
- Label for each side (top-left of each half, mono, small-caps).
- One visual + one stat per side.

**Motion:** Each side animates in on a stagger (0.4s apart). Hero stats count up in sync. A dividing rule draws in place.

**Common mistakes:** three or more divisions (ok for 16:9 landscape at most; otherwise visuals become too small); un-labeled sides; contrast that isn't actually a contrast.

## 7. Outro / CTA / Closing Stat Block

**Job:** Wrap it up. Tell the viewer what to do or what it meant.

**Duration:** 6–12s.

**Must contain:**
- A closing summary line ("10 days · 1 flyby · 4 astronauts · ∞ ambition").
- A "what's next" call-out (next mission, CTA button mock, date, URL).
- Final fade-to-canvas at the end (the ONLY scene where exit animations are allowed per HyperFrames rules).

**Motion:** Final stats stagger in. Hero closing line holds for 1.5–2s at full opacity. Fade to canvas over 1.0–1.2s `power2.in`.

**Common mistakes:** no clear closing stat block; CTA buried; cutting to black without a fade.

---

## Composition rules

1. **Typical 60s video = 7 scenes:** Title → Intro → Data → Hero → Support/Contrast → Return → Outro.
2. **Typical 30s video = 4 scenes:** Title → Main beat → Hero → Outro.
3. **Typical 90s video = 9 scenes:** Title → Intro → 3× Act beats → Hero → Contrast → Return → Outro.
4. **Keep scene durations varied.** Same length for every scene feels robotic. Let the Hero Moment breathe longer (+30% vs neighbors).
5. **Every scene needs entrance animations on every element.** Per HyperFrames rules, elements must NEVER appear fully-formed.
6. **Only the final scene may use exit animations.** All intermediate scenes rely on the root-level transition to handle their exit.
