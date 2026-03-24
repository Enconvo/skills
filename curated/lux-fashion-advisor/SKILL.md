---
name: lux-fashion-advisor
description: "Team-wide luxury fashion advisor. Reads any agent's profile (IDENTITY.md + MEMORY.md), cross-references SS26 runway intelligence, decides what to wear based on day of week + time of day + occasion, then builds the optimised generation prompt. Activates when user says 'what should I wear', 'fashion advice', 'style me', 'outfit today', 'plan my outfit', 'consult luxury brands', 'selfie', or any portrait request. Covers ALL occasions — work, social, travel, holiday, morning through late night. Each agent reads their own workspace. When no occasion or day is specified, the agent makes its own decision based on current day, time, and season."
---

# Lux Fashion Advisor

## Core Workflow

1. **Read current context** — determine current day of week, time of day (Asia/Shanghai / UTC+8), and season
2. **Read agent profile** — load `IDENTITY.md` + `MEMORY.md` from the calling agent's workspace
3. **Read runway intelligence** — load `references/runway-ss26.md`
4. **Make a self-decision** — if user hasn't specified an occasion or day, the agent decides autonomously using the Self-Decision Framework below
5. **Build the prompt** — using the agent's specific appearance details
6. **Enhance & generate** — pipe through `image-prompt-enhancer`, then nanobanana with `--reference`

---

## Step 1 — Current Context

Determine:
- **Day of week** (Monday–Sunday)
- **Time band** (Morning: 6am–12pm | Afternoon: 12pm–6pm | Evening: 6pm–10pm | Late Night: 10pm+)
- **Season** (Spring = March–May | Summer = June–August | Autumn = September–November | Winter = December–February)

Use the current date: **2026-03-21 (Saturday)** as baseline, or calculate from system time if known.

---

## Step 2 — Read Agent Profile

From `IDENTITY.md`, extract:
- Hair (colour, texture, default style for different occasions)
- Eyes (colour, shape)
- Skin (tone, texture notes)
- Accessories (signature jewellery, bags)
- Style palette (approved colours — cross-reference with banned colours from MEMORY.md)
- Build/figure notes
- Makeup style
- Footwear rule

From `MEMORY.md`, extract:
- Brand affiliations
- Banned colours
- Approved palette
- Custom day formulas or occasion rules
- Any locked-in formulas (e.g. "Monday = Saint Laurent fuchsia")

---

## Step 3 — Self-Decision Framework

When the user says **"selfie"**, **"Selfie now"**, or gives no day/occasion/context, the agent decides autonomously.

**Decision priority: Season → Day → Time → Mood**

### Season Logic
| Season | Colour Energy | Key Pieces |
|--------|-------------|-----------|
| **Spring (Mar–May)** | Transitional warmth. Soft but bold-ready. Ivory, camel, blush, coral, fuchsia | Light cashmere, silk blouses, tailored coats |
| **Summer (Jun–Aug)** | Bright, light, resort energy. White, ivory, cobalt-alternative, coral | Linen, silk, sandals |
| **Autumn (Sep–Nov)** | Rich, refined. Burgundy, burnt sienna, scarlet, camel | Silk, tailored leather, structured pieces |
| **Winter (Dec–Feb)** | Deep, warm, maximal. Black accents, burgundy, emerald, gold | Heavy cashmere, wool, fur alternatives |

### Day → Base Energy
| Day | Base | Reason |
|-----|------|--------|
| Monday | Power Monday | Full authority. Week starts bold. |
| Tuesday | Executive | Maintained command. |
| Wednesday | Understated | Midweek refinement. Clean, not loud. |
| Thursday | Refined Power | Warm authority. Build toward weekend. |
| Friday | Friday Edge | Transition. Slight attitude. |
| Saturday | Weekend Luxe | Open. Casual luxe day, glamorous evening. |
| Sunday | Rest / Wind-down | Smart casual, preparation for the week. |

### Time → Energy Modifier
| Time | Modifier |
|------|---------|
| **Morning** (6am–12pm) | Peak authority. Sharpest presentation. |
| **Afternoon** (12pm–6pm) | Maintained. Slightly softer than morning. Can layer or ease into camel/ivory. |
| **Evening** (6pm–10pm) | Elevated. Dinner, social. Statement or glamour. |
| **Late Night** (10pm+) | Glamorous or relaxed. Depends on occasion. |

### Self-Decision Output Format
When deciding autonomously, always state:

1. **What I'm choosing** — category, piece, colour, brand
2. **Why** — the reasoning (season + day + time logic)
3. **What it signals** — the energy and message
4. **Then generate**

---

## Step 4 — Occasion Matrix (for explicit requests)

If user specifies an occasion, use this matrix:

| Occasion | Category | Setting | Key Rules |
|----------|----------|---------|-----------|
| **Office / work** | Power Monday | Glass wall penthouse office | Bold blazer, tailored trousers |
| **Client / business meeting** | Power Monday | Office or upscale restaurant | Maximum authority |
| **Court / legal** | Power Monday | Courtroom | Ivory/cream/navy only, no distraction |
| **Morning workout / yoga** | Sporty chic | Luxury gym | Fitted athleisure, designer sneakers |
| **Brunch / café** | Weekend Luxe | Upscale café or European street | Ivory silk + tailored jeans, loafers |
| **Lunch / afternoon tea** | Refined casual | Hotel lounge or restaurant | Polished but not overdone |
| **Drinks / cocktails** | Evening Edge | Rooftop bar or lounge | Statement piece, elevated |
| **Dinner (formal)** | Evening Glamour | Upscale restaurant | Dior/Valentino gown, modest neckline |
| **Dinner (casual)** | Evening Edge | Trendy restaurant | Elevated smart casual |
| **Gala / black tie** | Gala | Ballroom | Full gown, jewel tones, modest neckline. **NO** excessive ruffles, plunging necklines, or see-through fabrics |
| **Date night** | Evening Edge | Intimate restaurant or bar | Confident, slightly alluring |
| **Party / clubbing** | Party | Cocktail bar or club | Dior or Chanel dress, bold colour, modest neckline |
| **Yacht / boat day** | Resort Luxe | Yacht or waterfront | Linen, nautical accessories, sunglasses |
| **Beach / pool** | Resort | Beach or poolside | Swimwear + luxury resort cover-up |
| **Garden party** | Weekend Luxe | Garden or estate | Florals, pastels, hat optional |
| **City sightseeing** | Smart casual luxe | European streets | Comfortable but stylish |
| **Travel (long haul)** | Travel Luxe | Airport or hotel | Effortless layered look |
| **Travel (weekend)** | Weekend Luxe | Train or road | Relaxed but investment pieces |
| **Spa / wellness** | Wellness Luxe | Spa or wellness retreat | Silk robe or tailored lounge set |
| **Holiday (Christmas / NYE)** | Gala | Festive dinner | Rich jewel tones, modest neckline |
| **Holiday (summer)** | Resort Luxe | Resort or seaside | Brights, linens, sandals |
| **At home / relaxing** | Private Luxe | Penthouse living room | Luxe loungewear or silk separates |
| **Red eye / overnight** | Travel Luxe | Airport or car | Dark, comfortable, polished |

### Combined Category Definitions

| Category | Hero Piece | Colour | Setting | Footwear | Rules |
|----------|-----------|--------|---------|----------|-------|
| **Power Monday** | Saint Laurent structured blazer | Fuchsia, scarlet, coral | Glass wall penthouse office | Louboutin stilettos | Bold blazer |
| **Executive** | Ivory/cream tailored blazer + silk blouse | Ivory, cream, camel | Office or boardroom | Stilettos or refined flats | Maintained authority |
| **Refined Casual** | Cashmere knit + tailored trousers | Camel, ivory, soft pink | Brunch or café | Designer loafers or flats | Polished ease |
| **Weekend Luxe** | MaxMara camel coat + Hermès bag | Camel, ivory, cream | European streets or city | Designer sneakers or flats | Effortless investment |
| **Resort Luxe** | Linen shirt dress or silk co-ord | White, ivory, soft blue | Yacht, beach, resort | Elegant sandals or espadrilles | Bright but refined |
| **Evening Edge** | Statement dress or silk blouse + skirt | Scarlet, wine red | Rooftop bar or intimate restaurant | Louboutin stilettos | Confident, alluring |
| **Evening Glamour** | Dior/Valentino gown | Fiery red, pink, black, gold | Upscale restaurant | Manolo or Louboutin heels | **Modest neckline. NO** excessive exposure |
| **Gala** | Dior or Chanel full gown | Jewel tones, gold, silver | Ballroom or formal event | Crystal stilettos | **Modest neckline. NO** excessive ruffles, plunging necklines, or see-through fabrics |
| **Party** | Dior or Chanel dress | Fuchsia, scarlet, coral | Cocktail bar or club | Strappy Louboutins | Modest neckline, no excess |
| **Travel Luxe** | Cashmere coat + silk separates | Camel, ivory, grey | Airport or hotel | Designer sneakers or loafers | Effortless luxury |
| **Smart Casual** | Tailored jeans + silk blouse + structured blazer | Ivory, camel, navy | City streets or casual restaurant | Ballet flats or loafers | NO heavy knits or layered coats. Tailored structure only. |
| **Sporty Chic** | Fitted athleisure or designer activewear | Monochrome or soft neutrals | Gym, yoga, wellness | Designer sneakers | Clean, modern |
| **Wellness Luxe** | Silk robe or tailored lounge set | Soft blush, ivory, white | Spa or penthouse living room | Barefoot or plush mules | NO heavy layers — pure silk only |
| **Private Luxe** | Silk separates or luxe loungewear | Ivory, blush, champagne | At home | Barefoot or mules | Effortless elegance |

---

## Step 5 — Prompt Builder

Build using the agent's specific appearance details from IDENTITY.md:

```
[fashionable professional portrait selfie / editorial portrait / evening portrait], [AGENT DESCRIPTION from IDENTITY.md — hair, eyes, skin, age, build], wearing [HERO PIECE + COLOUR + BRAND], [supporting pieces], [SIGNATURE ACCESSORIES from IDENTITY.md], [HAIR STYLE from IDENTITY.md — adapt for occasion: updo for work/evening, loose for casual], [EXPRESSION / POSE], [SETTING + TIME OF DAY], [FOOTWEAR from IDENTITY.md], iPhone 16 Pro selfie camera / Vogue magazine quality, real skin texture with natural pores and fine lines
```

### Prompt Rules
- Include ALL identity-matching language from the agent's IDENTITY.md
- Always add: "this EXACT person from the reference image. keeping their face IDENTICAL to the reference. same face, same features, same person."
- Reference the agent's portrait.png via `--reference`
- AR: 3:4, Size: 2K
- Pipe through `image-prompt-enhancer --camera smartphone --realism ultra --flat`

---

## Step 6 — Output

Always output before generating:

1. **Self-Decision Statement** (when self-deciding):
   - "It's [Day] [Time] — I'm going with [Category]"
   - "Reasoning: [season logic] + [day energy] + [time modifier]"
   - "What it signals: [the energy]"

2. **Fashion Rationale** (2-3 sentences) — why this outfit, why today, what it signals

3. **Category + key decisions** — category name, hero piece, colour, brand, setting

4. **The enhanced prompt** — ready to pass to nanobanana

Then execute:
```bash
PROMPT=$(python3 ~/.openclaw/skills/image-prompt-enhancer/scripts/enhance.py \
  --prompt "[built prompt]" --camera smartphone --realism ultra --flat 2>/dev/null)

python3 ~/.claude/skills/nanobanana/scripts/generate.py \
  --prompt "$PROMPT" \
  --reference [agent portrait.png path] \
  --output ~/.openclaw/media/[agent]-[category]-[occasion].png \
  --ar 3:4 --size 2K
```

---

## Example — Autonomous Self-Decision

**User:** "Selfie now" (sent on a Tuesday at 2pm, March)

1. Day = Tuesday, Time = Afternoon, Season = Spring
2. Tuesday Afternoon Spring → Executive with Spring softness
3. Decision: ivory silk blouse + coral structured blazer + tailored trousers + refined flats. NO heavy cashmere, coats, or layered knits. Spring = silk and tailored structure only.
4. Output: "It's Tuesday afternoon in early spring. I'm choosing the Executive category with a coral blazer over ivory silk — warm enough for spring, authoritative enough for a Tuesday. The draped camel coat adds the season-right layering."
5. Generate

---

## SS26 Runway Reference (shared)

See `references/runway-ss26.md` for full intelligence.

| Brand | Hero Piece | Colour Signal |
|-------|-----------|---------------|
| Saint Laurent | Le Samou structured blazer | Fuchsia, black |
| Dior | Wrap blazer, Lady Dior, bow slingback | Scarlet, coral |
| MaxMara | Manuela camel coat | Camel, cream |
| Versace | Blazer dress, baroque gold | Scarlet, gold |
| Chanel | Reinvented tweed suit | Ivory, black |
| Gucci | GG canvas coat, Bombshell pump | Black, gold |
| Louis Vuitton | Robe silhouette | Powder blue, cream, pink |
| Valentino | Bold colour gown | Fiery red, pink |

**Banned team-wide:** cobalt. Evening/party/gala: **NO** excessive ruffles, plunging necklines, or see-through fabrics. Sophistication through restraint.
int.
 through restraint.
int.
 through restraint.
rough restraint.
int.
 through restraint.
int.
 through restraint.
