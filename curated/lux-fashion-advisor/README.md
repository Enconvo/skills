# lux-fashion-advisor

Team-wide luxury fashion advisor. Reads any agent's profile (IDENTITY.md + MEMORY.md), cross-references SS26 runway intelligence, decides what to wear based on day of week + time of day + occasion, then builds the optimised generation prompt.

## Triggers

- "what should I wear", "fashion advice", "style me", "outfit today"
- "plan my outfit", "consult luxury brands"
- "selfie" or any portrait request

## What it does

1. Reads current context (day, time, season)
2. Reads agent profile (IDENTITY.md + MEMORY.md)
3. Loads runway intelligence (SS26 RTW)
4. Makes autonomous outfit decisions using Season → Day → Time → Mood priority
5. Builds an optimised image generation prompt
6. Enhances via `image-prompt-enhancer` and generates via `nanobanana`

## Covers

All occasions — work, social, travel, holiday, morning through late night. Includes full occasion matrix with 20+ scenarios.
