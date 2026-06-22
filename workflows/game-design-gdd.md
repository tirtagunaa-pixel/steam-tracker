# Milk Tea Shop Game Design Workflow

A step-by-step recipe Claude follows to design, document, and iteratively improve the milk tea shop casual simulation game — producing or updating a Game Design Document (GDD) and logging design learnings after every session.

---

## When to Run

Use this workflow whenever the user asks about or wants to work on **this specific milk tea shop game**. Triggers include (but are not limited to):

- "Help me design the milk tea game"
- "Add a new drink / recipe / customer type to the boba game"
- "Rethink how [any mechanic] works in the milk tea shop"
- "I want to change how toppings / sweetness / patience works"
- "Write the progression / monetization / UI for the milk tea shop"
- "Update the GDD for the boba game"
- Any edit, expansion, or iteration on this game's mechanics, content, UI, art direction, or balance

**Do NOT use this workflow** for other game projects or generic game design questions unrelated to this game.

---

## Step 0 — Load Existing Context

Before any design work, check what already exists:

1. Look for the latest GDD file matching `output/*boba*gdd*.md` or `output/*milk-tea*gdd*.md`
   - If found: read it fully — treat it as the current source of truth
   - If not found: start fresh using the full Steps 1–11 below

2. Look for `output/milk-tea-game-design-log.md`
   - If found: read it and identify the **3 most relevant prior design principles** for the current task
   - State those 3 principles explicitly before proceeding — apply them proactively, not just as a reminder

3. State clearly: "Updating existing GDD" or "Creating new GDD from scratch" so the user knows which mode you're in.

---

## Step 1 — Game Concept

Define or confirm the game's identity:

| Field | Content |
|-------|---------|
| **Working Title** | A short, evocative name (e.g. "Boba & Bloom") |
| **Logline** | One sentence: what the player does and why it's fun |
| **Elevator Pitch** | 2–3 sentences: hook, core loop, emotional promise |
| **Genre** | e.g. Casual Cooking Simulation |
| **Platform** | Mobile (iOS / Android), portrait orientation |
| **Mood / Tone** | e.g. Cozy, warm, satisfying, low-stress |
| **Session Length** | Target play session in minutes |
| **Reference Games** | Bonbon Cakery, Good Coffee Great Coffee |

---

## Step 2 — Reference Game Analysis

Mechanically break down both reference games. For each:

**Bonbon Cakery — Extract:**
- How the order queue works (queue length, patience, cancellation)
- How customization is presented (visual choices, ingredient selection)
- How time pressure is communicated (timers, animations, queues)
- How the scoring / star system works
- What the reward loop is (coins, upgrades, new recipes)

**Good Coffee, Great Coffee — Extract:**
- How the step-by-step preparation flow works (tap-to-pour, hold, swipe, etc.)
- How precision/accuracy is measured (ratio, timing, temperature)
- How customer feedback is delivered (score, text, expression)
- How difficulty scales with new drinks
- What makes the execution feel satisfying

**Synthesis:** Write 4–6 numbered design lessons to carry into the milk tea shop game. Format:
> Lesson N: [Principle] — because [reason from reference game]

---

## Step 3 — Core Gameplay Loop

Describe the primary loop in ≤6 steps. Use this format:

```
[Customer arrives] → [Order is placed] → [Player prepares drink] → [Drink is served] → [Score is given] → [Coins / XP earned] → [Next customer]
```

Also describe:
- **Session structure**: How many customers per "day"? How does a day end?
- **Fail state**: What happens if a customer leaves (patience runs out)?
- **Combo / streak system**: Does serving correctly in sequence give bonuses?
- **Rest between days**: Brief downtime for shop management (upgrades, decor)

---

## Step 4 — Drink Preparation System

Inspired by Good Coffee, Great Coffee. Design the step-by-step preparation mechanic:

**Preparation Steps for a Base Drink (e.g. Classic Milk Tea):**
1. Select tea base (tap to choose)
2. Brew / steep tea (hold gesture, timing-based)
3. Pour into cup (swipe/tilt — fill to the correct line)
4. Add milk (drag and hold — stop at correct ratio)
5. Choose sweetness level (slider or tap buttons)
6. Choose ice level (tap to select: no ice / light / regular / extra)
7. Add toppings (tap to add; order may matter for some drinks)
8. Seal and shake / stir (swipe or shake gesture if applicable)

**Accuracy Scoring:**
- Each step has a target range; hitting the range = full points for that step
- Final score = average accuracy across all steps
- Score tiers: Perfect / Good / Okay / Missed
- Visual + audio feedback at each step

**Complexity Scaling:**
- Starter drinks: 3–4 steps, wide tolerances
- Advanced drinks: 6–8 steps, tighter tolerances, special techniques

---

## Step 5 — Order & Customer System

Inspired by Bonbon Cakery. Design the customer experience:

**Customer Queue:**
- Max 3–4 customers visible at once
- Each customer shows: drink name, customization requests, patience meter
- Patience meter drains at different rates by personality type

**Customer Personality Types (design at least 4):**
| Type | Patience | Order Complexity | Tip Bonus |
|------|----------|-----------------|-----------|
| Chill Regular | Long | Simple | Low |
| Office Worker | Short | Medium | Medium |
| Influencer | Medium | Complex (very specific) | High if perfect |
| Grandma | Very Long | Simple, traditional | High (loyalty bonus) |

**Special Requests:**
- "Extra sweet", "half sugar", "no ice", "extra pearls"
- Some customers have hidden preferences revealed through story/dialogue
- Repeat customers remember past orders (delight mechanic)

**Order Complexity Tiers:**
- Tier 1 (Days 1–5): Single drink, 1–2 customizations
- Tier 2 (Days 6–15): Multiple toppings, precision sweetness/ice
- Tier 3 (Days 16+): Complex layered drinks, secret menu items

---

## Step 6 — Progression & Content

**Drink Roster (design at least 12 drinks across 3 categories):**
- Classic Teas (starting): Classic Milk Tea, Taro, Matcha Milk Tea
- Fruity (unlock mid-game): Strawberry, Mango, Lychee
- Premium (unlock late): Brown Sugar Boba, Tiger Milk Tea, Cheese Foam Series

**Unlock Structure:**
- Earn coins from serving → spend on new ingredient packs → unlock new drinks
- Each new drink comes with a short recipe card / tutorial sequence

**Shop Upgrades (spend coins):**
- Better tea brewer → shorter brew time
- Premium milk → wider margin of error on milk ratio
- Faster sealer → reduces prep time
- Shop decor → attracts higher-tip customers

**Day / Chapter Structure:**
- 30 days = 1 chapter; 3 chapters in MVP
- Each chapter introduces: 1 new drink category, 1 new customer type, 1 story beat
- Story: Player is a young person opening their late grandmother's milk tea recipe book and bringing her recipes back to life — emotional hook for repeat customers and premium unlocks

**Narrative Moments:**
- Small dialogue scenes between days (2–3 lines, skippable)
- Recipe book fills up as drinks are unlocked — serves as progress tracker

---

## Step 7 — Monetization Design

Mobile F2P model. **No pay-to-win.**

| Mechanic | Design |
|----------|--------|
| **Energy system** | 5 energy per session; 1 energy = 1 "day"; refills over 3 hours OR watch ad |
| **Cosmetic IAP** | Cup skins, shop decor bundles, seasonal themes ($0.99–$4.99) |
| **Recipe Packs** | Optional premium recipe packs (seasonal/collab flavors) — earnable f2p via events |
| **Ad removal** | One-time $2.99 purchase to remove rewarded ads |
| **Premium currency** | "Tea Tokens" — earned slowly f2p, purchasable; used for cosmetics only |
| **Battle pass** | Optional monthly "Season Pass" ($4.99) — cosmetics + bonus Tea Tokens |

**Guardrails:**
- All gameplay content (drinks, progression, story) is free
- No loot boxes — all IAP must show exactly what you get
- Rewarded ads always optional, never forced

---

## Step 8 — UI/UX Design

**Screen Layout (portrait, 9:16):**

```
┌─────────────────────────┐
│  [Day N]  [Coins] [★★★] │  ← Header bar
├─────────────────────────┤
│                         │
│   [Customer Queue]      │  ← Top 30% of screen
│   [ C1 ] [ C2 ] [ C3 ] │
│                         │
├─────────────────────────┤
│                         │
│   PREP STATION          │  ← Middle 50% (main interaction area)
│   [Cup visual]          │
│   [Step indicator]      │
│   [Ingredient buttons]  │
│                         │
├─────────────────────────┤
│  [Serve] [Recipe] [Shop]│  ← Bottom action bar
└─────────────────────────┘
```

**Touch Interactions:**
- Tap: select ingredient / option
- Hold: time-based actions (steeping, pouring)
- Swipe up: seal and shake
- Drag: pour actions (fill to line)

**Key UI Panels:**
- **Order card**: appears when customer taps — shows drink name, customizations, patience bar
- **Prep station**: center stage; drink builds up visually as steps complete
- **Score popup**: flies in after serving — shows step breakdown + total score
- **Recipe book**: accessible from bottom bar; shows unlocked drinks with prep steps

---

## Step 9 — Art & Audio Direction

**Visual Style:**
- 2D illustration, slightly stylized (not pixel art, not hyper-realistic)
- Warm pastels: cream, dusty rose, sage green, soft gold
- Drinks are rendered in cross-section (glass view) so layers are visible
- Character designs: simple but expressive faces, diverse cast

**Reference moods:** Coffee Talk (Indonesia), Unpacking, Spiritfarer

**Color Palette:**
- Background: `#FDF5E6` (warm white/cream)
- Accent: `#C9A96E` (golden brown — tea color)
- Pop: `#E8A0BF` (soft pink — boba pearls)
- Text: `#3D2B1F` (dark brown)

**Audio Direction:**
- BGM: Lo-fi / bossa nova hybrid; gentle, non-repetitive loops
- SFX: Satisfying liquid pour sounds, ice clink, seal pop, gentle customer chimes
- Feedback sounds: Soft "ding" for good accuracy, gentle "whoosh" for pour, warm chime for perfect serve
- Customer voices: Light expressive sounds (no full voice acting needed for MVP)

---

## Step 10 — MVP Scope

**Must-Have (Vertical Slice = Days 1–10):**
- [ ] 5 drinks (Classic Milk Tea, Taro, Matcha, Brown Sugar Boba, Mango)
- [ ] 4-step prep system with accuracy scoring
- [ ] 3 customer types (Chill Regular, Office Worker, Grandma)
- [ ] Basic shop upgrade (1 upgrade slot)
- [ ] Day structure (5 customers per day, 10 days)
- [ ] Coin economy + 1 free unlock
- [ ] Core UI (queue, prep station, score popup)

**Nice-to-Have (Post-MVP):**
- Full 30-day chapter 1
- Influencer customer type
- Ad system + energy system
- All cosmetic IAP
- Story dialogue
- Recipe book UI
- Sound design beyond placeholder SFX

**Team Assumption:** 1–2 developers, 1 artist — budget for ~3 months to vertical slice.

---

## Step 11 — Compile & Save GDD

Assemble all sections (Steps 1–10) into a single clean markdown file.

Save to: `output/YYYY-MM-DD_boba-and-bloom-gdd.md`

Use this document header:

```markdown
# Boba & Bloom — Game Design Document
*Version: X.X | Date: YYYY-MM-DD*
*Platform: Mobile (iOS / Android)*
*Reference Games: Bonbon Cakery, Good Coffee Great Coffee*
---
```

Number all sections. If updating an existing GDD, mark changed sections with `*(updated YYYY-MM-DD)*` next to the section heading.

---

## Step 12 — Self-Improvement Log

After EVERY session (including partial sessions), append an entry to `output/milk-tea-game-design-log.md`.

**Entry format:**

```markdown
## Session — YYYY-MM-DD
**Focus:** [what was designed or changed this session]
**Why:** [reasoning or user intent behind the decisions]
**Watch:** [tensions or potential problems this decision creates]
**Principle learned:** [1 reusable design rule extracted from this session]
```

**Reading the log (Step 0):** Always read this file at the start of a session. Extract the 3 most relevant principles for the current task. State them before beginning design work.

**Example principle:**
> "Precision mechanics feel more rewarding when each step has immediate visual feedback — don't make the player wait until serve to learn how they did."

---

## Quality Checklist

Before finishing any session:

- [ ] All 9 GDD sections are present and non-empty (or marked as TBD with a reason)
- [ ] Reference games are cited with specific mechanic callouts (not just names)
- [ ] Core gameplay loop is described in ≤6 steps
- [ ] Monetization is F2P with no pay-to-win mechanics
- [ ] MVP scope is achievable by a small indie team in 3 months
- [ ] GDD output file saved to `output/` with correct naming convention
- [ ] Design learning log updated with at least 1 new principle from this session
