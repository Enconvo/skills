# AI-Slop Fingerprints

If a generated site has any of these, it reads as "another generic AI-built page" and the user notices instantly. Redesign before shipping.

## Color

- Cyan-on-dark with glowing borders. The 2024–2025 SaaS template default.
- Purple-to-blue gradient text on a heading. Decorative-not-meaningful.
- Neon accents on a dark background. Looks "cool" without requiring decisions.
- Pure black `#000` or pure white `#fff`. Always tint toward your brand hue.
- Gray text on a colored background. Use a tinted shade of the background instead.
- Default dark mode with glowing accents.

## Layout

- Centered everything. Left-aligned + asymmetric reads more designed.
- Identical card grids — same-sized cards with icon + heading + text, repeated.
- Hero metric layout template — big number, small label, supporting stats, gradient accent.
- Wrapping every content block in a card (cards inside cards).
- Same padding everywhere — no spatial rhythm.
- Three-column "what we do" with three identical icons.

## Typography

- Inter, Roboto, Arial, Open Sans, or system-ui fonts. Free, distinctive alternatives: Fraunces, Inter Tight (yes, the variable version is fine), Authentic Sans, GT Alpina (paid), Sohne (paid), JetBrains Mono.
- Monospace as a lazy "technical" / "developer" signal. Use it intentionally (data, code, captions) or not at all.
- Gradient text on a metric or heading. Decorative.

## Decorative elements

- Glassmorphism applied decoratively to every card (blur + glass + glow border).
- Rounded rectangles with generic drop shadows — could be any AI output.
- Sparklines as decoration — tiny charts that look sophisticated but convey nothing.
- Rounded elements with thick colored border on one side — almost never looks intentional.
- Large icons with rounded corners above every heading. Templated.

## Interaction

- Modals as a default UI pattern. Use only when there's truly no alternative.
- Every button as a primary button. Hierarchy matters.
- Hover effects on everything (whole-card lifts, big shadow growth). Pick a few moments.

## Motion

- Bounce / elastic easing. Real objects decelerate smoothly; bounce reads as "I tried."
- Animating layout properties (width, height, padding). Use `transform` and `opacity` only.
- Confetti / spring physics on every interaction.

## Hero

- "Hero metric layout" — big number, small label, supporting stats, gradient accent. The 2024 fintech template.
- Background video with no audio that loops a generic abstract animation.
- Three.js demo cube spinning that has nothing to do with the brand.
- Stock photo of a smiling team in a glass office.
- AI-generated "futuristic city" or "abstract neural network" hero image.

## Copy

- "Welcome to ___" / "Discover ___" / "Empower your ___" / "Streamline your ___". Verb-and-vague.
- Five bullet points all starting with the same verb.
- Hero subtitle that just restates the hero title in different words.
- "Built with React, TypeScript, Tailwind" anywhere on a marketing page.

## The AI-Slop Test

Before shipping, ask: **If you showed this to a designer and said "AI made this," would they believe you immediately?** If yes, redesign. A distinctive interface should make someone ask "how was this made?" not "which AI made this?"

Adapted from the principles in the `frontend-design` skill.
