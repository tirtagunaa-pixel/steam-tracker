# Steam Western Marketing Research Workflow

A step-by-step recipe Claude follows when asked to research how to market a Steam game genre to western audiences. Produces a research report and a separate actionable marketing playbook.

---

## Step 0 — Pre-flight: Check the Indie Game Database

Before any web searches, check existing knowledge:

1. Open `output/indie-game-conference-database-summary.md` — scan for games matching the target genre
2. Note any games with known western market performance data (sales, ratings, awards, regional reception)
3. Flag any games from the database that could serve as case study candidates

Use matches as **seed entries** for the case study section. They come pre-validated with conference history.

If no matches found, proceed directly to Step 0.5.

---

## Step 0.5 — Genre Pre-loaded Knowledge Base

If the genre requested in Step 1 matches any of the 14 categories below, apply the pre-loaded context to all subsequent research steps. This knowledge was synthesized from 519+ tracked indie games across 110+ conferences (2016–2026) and deep marketing case study research (compiled in `output/2026-06-08_indie-genres-western-marketing-research.md`).

**How to use:**
1. Read the matching genre card before running any searches
2. Use the listed non-obvious insight as your primary hypothesis — confirm or challenge with research
3. Pre-fill the Discovery Channels section of Step 4 from the regional notes
4. Use the named cultural drivers to seed Step 4 (player behavior) searches

---

### Genre Quick Reference Cards

#### Action Roguelite
- **Stage:** Historical breakout (2016–2019). Still commercially viable — genre market $3.8B (2025).
- **Primary drivers:** Twitch/streaming culture (mastery = watchable), 'git gud' identity, adult time constraints (20–40 min runs), procedural content from small teams
- **Non-obvious insight:** Loop clarity > polish in trailers. Show full run arc (start → build → boss → die → restart) — showing death and restart outperforms showing victory.
- **Discovery:** Twitch/YouTube (Northernlion tier), r/roguelikes, mid-tier streamer seeding 3 months pre-launch
- **Wishlist benchmark:** 30K–50K = solid; 80K–100K = strong

#### Metroidvania
- **Stage:** Historical breakout (2017–2019). $2.8B market (2025), growing at 9.1% CAGR.
- **Primary drivers:** GBA/SNES nostalgia (now 30–40yo), YouTube secret-finding content culture, genre was dormant since 2006 (decade of suppressed demand)
- **Non-obvious insight:** The map screenshot is your best marketing asset — show incomplete map with visible unexplored rooms. This triggers purchase for the nostalgia demographic more than any action clip.
- **Discovery:** YouTube long-form (NOT TikTok), r/metroidvania (200K+ members), "Top Upcoming Metroidvanias" YouTube list-maker channels (pitch 6 months pre-launch)
- **Wishlist benchmark:** 20K–40K = respectable; strong long-tail sales pattern

#### Farming / Life Sim
- **Stage:** Historical breakout (2016–2022). Genre is now crowded — must have clear secondary hook to differentiate.
- **Primary drivers:** Cottagecore/slow-living aesthetic, COVID demographic expansion (non-gamer female audience), TikTok/Pinterest discovery (NOT Twitch)
- **Non-obvious insight:** The differentiation must be in the first sentence of Steam description AND the TikTok thumbnail. The secondary hook (e.g., Unpacking's narrative puzzle mechanic, Coffee Talk's barista management) is why the game exists beyond Stardew Valley. Never bury it in paragraph three.
- **Discovery:** TikTok (#cozygaming primary), Pinterest, YouTube lo-fi/cozy channels, Wholesome Games curator (submit to Wholesome Direct)
- **Wishlist benchmark:** 50K+ = strong; cozy game discovery converts poorly from general Steam browsing — TikTok-driven discovery needed

#### Deckbuilder Roguelite Hybrid
- **Stage:** Historical breakout (2019–2024). Market now saturated with imitators — differentiation is critical.
- **Primary drivers:** Board game renaissance (MTG/Dominion audience), adult time constraints (60–90 min runs), gambling psychology in safe solo context
- **Non-obvious insight:** Lead with *anticipation* of the peak combo moment, not system explanation. Balatro's marketing worked because viewers wanted to experience a score going from 100 to 10,000,000 — not because they understood the ruleset.
- **Caution:** Saturation risk is high. Without a clear one-sentence differentiator, genre median week-1 sales are ~700 units (GameDiscoverCo 2024 cautionary case study).
- **Discovery:** YouTube analytical/combo format, Northernlion orbit, BoardGameGeek (underused), German board game community (Spiel Essen adjacent)
- **Demo rule:** No session limit. Balatro's demo averaged 6–8 hours/player. A constrained demo kills conversion.

#### Cozy / Wholesome
- **Stage:** Historical breakout (2020–2022). Now the most crowded genre on Steam — cozy-tagged titles: 146 (2023) → 371 (2024).
- **Primary drivers:** COVID demographic expansion, cottagecore/self-care cultural movement, TikTok/Pinterest discovery, female/non-binary demographic normalization
- **Non-obvious insight:** The most effective marketing asset is a 15–30 second TikTok of ONE satisfying task loop with ambient audio — not a trailer. Unpacking's 120K TikTok followers came entirely from "satisfying tasks" videos built 5 months pre-launch.
- **UK note:** Strongest cozy market globally — 1 in 5 UK players play cozy games daily.
- **Discovery:** TikTok (5+ months pre-launch), Pinterest, Wholesome Direct (highest-ROI single placement), r/cozygamers (500K+ members)

#### Social / Co-op Multiplayer (Viral)
- **Stage:** Historical breakout (2018–2024). Still active — R.E.P.O. ($121M) and Peak (2025) prove the format continues to work.
- **Primary drivers:** COVID social substitute, Discord friend-group infrastructure, streaming 'moment culture' (reaction clips are the content), zero-skill-barrier accessibility
- **Non-obvious insight:** Marketing IS the game design. Audit "clip moment density" before any campaign — how many shareable moments does a 1-hour session produce? Lethal Company achieved 8M+ copies with zero press outreach. Among Us spent zero dollars. Clip moment density is the real product-market fit signal.
- **Discovery:** Twitch/YouTube (mid-tier streamers seeded 6–8 weeks pre-launch), Discord community launch before Steam, viral clip strategy primary

#### Cultural-Specific Narrative
- **Stage:** Historical breakout (2022–2024). No saturation risk — genre is supply-constrained by dev capacity, not market.
- **Primary drivers:** Post-Parasite/Squid Game Western appetite for non-Western content, festival circuit as discovery pipeline, diaspora communities as zero-cost advocates
- **Non-obvious insight:** Diaspora communities in Western markets are the most underused zero-cost channel. Venba's Tamil-Canadian audience in the US + Canada became unpaid advocates. Identify and directly engage diaspora community creators, Reddit communities, and cultural organizations in Western countries.
- **Sequence matters:** Regional festival → IGF nomination → mainstream culture press (NPR, BBC, The Guardian) → gaming press → Steam launch. Do NOT invert.
- **Discovery:** Culture/film journalism FIRST (The Guardian, NPR, CBC, The Atlantic), then gaming press. This demographic doesn't read Kotaku.

#### Absurdist / Viral Concept Game
- **Stage:** Historical breakout (2019–2023). Active format but requires exceptional concept clarity.
- **Primary drivers:** One-sentence pitch virality, premise-as-marketing (the honk IS the ad), meme culture, short play time + low price = zero purchase friction
- **Non-obvious insight:** Release MONTH matters more than most marketing campaigns. Untitled Goose Game launched September 2019 (quiet window before AAA season). A game ignored in November can define a September.
- **Failure mode:** Concept sounds good in text but produces poor gameplay footage. Without a viral clip within 72 hours of launch, the game becomes invisible.
- **Discovery:** Mainstream non-gaming media (Chrissy Teigen model), Twitter/X meme spread, mega-influencer for ignition (genre NEEDS high-reach channels for meme tipping point)

---

#### Autobiographical / Personal Narrative RPG *(Emerging)*
- **Stage:** Emerging — IGF 2025 triple win (Consume Me) established genre credibility. No saturation. 12–18 month window.
- **Primary drivers:** Mental health mainstreaming, games-as-therapy discourse, IGF legitimization, lived experience as irreplicable content differentiator
- **Non-obvious insight:** Mental Health Awareness Month (May) is a free annual marketing event that no game currently owns. Partnership with Safe In Our World (UK) or Games for Change (US) + May launch = press coverage no budget can buy.
- **Discovery:** Games-as-therapy press, Polygon/The Guardian cultural coverage, Safe In Our World partnership
- **Pricing sweet spot:** $9.99 with 20% launch discount

#### Psychological Horror (Narrative-First, No Jump Scares) *(Emerging)*
- **Stage:** Emerging — Mouthwashing (95% Steam, 23,854 reviews, Oct 2024) and Voices of the Void (5,441 ratings, 4.9/5) prove the market. 18–24 month window.
- **Primary drivers:** Jump scare fatigue in streamer communities, Gen Z liminal space/analog horror aesthetics, A24 film aesthetic normalization
- **Non-obvious insight:** Short play time (2–4 hrs) + low price ($9.99–$12.99) = the genre's unfair advantage over longer horror games. After completion, western players immediately tell friends to buy it. This conversion flywheel is faster than any campaign.
- **Mouthwashing discovery path:** Steam Next Fest Feb 2024 → horror YouTube/TikTok → 500K+ copies. Replicate: Feb Next Fest demo, low price, horror YouTubers as primary seeding.
- **Discovery:** Horror YouTube/TikTok (cold-key outreach to horror streamers), A24 aesthetic frame for film press

#### Rhythm Roguelite *(Emerging)*
- **Stage:** Emerging — Ratatan (BitSummit 2025 Grand Prize, 100K+ EA copies), Fresh Tracks (98% Steam). Zero competition in Western market. 12–18 month first-mover window.
- **Primary drivers:** Decade-long rhythm game drought (Guitar Hero collapsed 2011), roguelite solving "no content left" problem, Patapon nostalgia fanbase (15 years waiting)
- **Non-obvious insight:** VTubers (Hololive EN) are the single most effective underused channel for this genre. Emotional reactions and singing attempts are highly shareable clip content — Western mainstream gaming influencers are secondary targets, not primary.
- **Patapon community:** Actively waiting. r/Patapon, dedicated Discord servers — reaching them costs essentially nothing.

#### Cozy Horror / Dark Farming Hybrid *(Emerging)*
- **Stage:** Emerging — We Harvest Shadows (220K+ wishlists without marketing). Genre has 3–4 games total. 12–18 month first-mover window.
- **Primary drivers:** Cozy game saturation creating need for differentiation, cottagecore audience maturing (wanting tension), Gen Z #cozygaming + horror crossover TikTok community
- **Non-obvious insight:** We Harvest Shadows' formula: ONE high-visibility showcase event + same-day demo = 100K wishlists in 22 days → 220K in 3 months. No ongoing marketing. A single well-placed showcase + demo is higher ROI than any sustained campaign.
- **October timing advantage:** Cozy audience AND horror audience both peak in October. This is the single best launch window for this genre.

#### Cozy Management + Deckbuilder Hybrid *(Emerging)*
- **Stage:** Emerging — Balatro validated the market (5M+ copies, TGA 2024 GOTY), Dogpile's 96% Overwhelmingly Positive validates small-scale success. 18–24 month window.
- **Primary drivers:** Balatro's GOTY lowered publisher risk perception, board game renaissance crossover, adult time constraints + crunch-core cozy demand
- **Non-obvious insight:** "Crunch-core cozy" is an emerging self-identification in 30–45yo gamers that has no community hub yet. The first developer who creates that hub (Discord, subreddit, content series) will own the genre's community before any competing game exists.
- **German market:** Highest-ROI European market. German board game culture + Spiel Essen community = uncontested channel.

#### Physics Co-op Party *(Emerging)*
- **Stage:** Emerging — Fall Guys vacuum (5 years, no clear successor). Big Walk (House House) and Frog Sqwad (Fall Guys CD) are the two highest-pedigree entries in 2026. 12–18 month window.
- **Primary drivers:** Fall Guys vacuum (50M+ downloads month one, demand unmet for 5 years), TikTok physics chaos clips as organic marketing, COVID gaming-as-social-activity cohort seeking next co-op game
- **Non-obvious insight:** NEVER self-describe as "the next Fall Guys." Every game that did this failed. Successful 2025 games (Peak, R.E.P.O.) had distinct identities and let journalists make the comparison. Lead with your unique premise.
- **Discovery:** TikTok physics chaos clips (12–18 second format), Discord friend-group spread, mid-tier Twitch/YouTube variety streamers

---

## Step 1 — Ask Clarifying Questions

Before researching, ask the user these questions (use AskUserQuestion with up to 4 questions at once):

1. **Genre** — Which Steam game genre? (required if not already provided)
   - Examples: cozy / life sim, survival, roguelike, RPG, puzzle, horror, city builder, action platformer, visual novel, strategy
   - Allow the user to type their own if not listed

2. **Target markets** — Which western regions to cover?
   - US & Canada
   - UK
   - Germany
   - France
   - Australia & New Zealand
   - Nordic (Sweden, Norway, Denmark, Finland)
   - Default: all six if not specified

3. **Game scope** — What kind of games should the research focus on?
   - Indie only (under $10M budget)
   - All Steam games including AA/AAA
   - Free-to-play Steam games only

4. **Research angle** — What marketing moment is this for?
   - Pre-launch (building wishlist and awareness 6–12 months out)
   - Launch window (Day 0 to Day 30)
   - Post-launch (long-tail growth, DLC, updates)
   - Evergreen (genre strategy regardless of launch timing)

Do not start researching until answers are received.

---

## Step 2 — State the Research Plan

Before executing, tell the user:
- The genre and confirmed markets to cover
- Which case study games you'll target (seeds from database + will find more via research)
- The two output files you'll produce
- Roughly how many sources you'll target (aim for 15+)

Example:
> "Researching [genre] marketing for [markets]. I'll cover genre landscape, player behavior per region, 3+ case studies, and channel analysis — producing a research report and marketing playbook. Targeting ~15 sources. Starting now."

---

## Step 3 — Genre Landscape Research

Research the genre's current state on Steam and in western markets:

**Search targets:**
- `[genre] games Steam market size 2024 2025`
- `[genre] Steam top sellers player count`
- `[genre] games western market trends`
- `GameDiscover.co [genre] analysis`
- `SteamDB [genre] new releases`

**Capture:**
- Total Steam games in this genre (SteamDB or SteamSpy data)
- Top 10 best-performing titles by review count and rating
- Genre growth trend (growing / plateauing / shrinking)
- Key sub-genres and adjacent categories gaining traction
- Regional market share breakdown if available (Newzoo, GameAnalytics, or press estimates)
- Genre saturation signal: are there too many similar games launching?

---

## Step 4 — Player Behavior & Culture Deep Dive

Research each requested market. For **each region**, answer all six questions below.

**Search pattern per region:** `[genre] games [region] players community behavior`, `[genre] gaming culture [region] Steam`, plus any official market reports listed.

---

### US & Canada
- **Demographics:** age range, gender split, income/spending power (source: ESA annual report, Newzoo US data)
- **Discovery:** primary channels — TikTok, YouTube let's plays, Reddit, Steam discovery queue, Twitch, press
- **Community behavior:** key subreddits, Discord servers, streaming culture, what drives viral moments
- **Cultural touchstones:** themes and aesthetics that over-index (frontier/wilderness, dark humor, min-maxing culture, speedrunning community)
- **Spending habits:** price sensitivity, DLC appetite, early access tolerance, F2P vs premium attitude
- **Creator ecosystem:** top YouTubers and Twitch streamers for the genre; note follower counts and engagement style

### UK
- **Demographics:** source: UKIE annual report, YouGov gaming surveys
- **Discovery:** YouTube, press (RPS, PC Gamer UK, Eurogamer), Reddit, social
- **Community behavior:** strong press culture, word-of-mouth via forums and Discord, Steam reviews heavily read
- **Cultural touchstones:** dry humor, atmospheric world-building, management/strategy games resonate strongly
- **Spending habits:** slightly more price-sensitive than US; value for money matters; physical gaming culture still active
- **Creator ecosystem:** UK-based YouTubers and streamers for the genre

### Germany
- **Demographics:** source: game-Verband / BIU annual report, GfK gaming data
- **Discovery:** YouTube (highest per-capita gaming YouTube consumption in EU), press (4Players, GameStar, GamePro DE), Steam
- **Community behavior:** deliberate, research-heavy buying decisions; negative reactions to aggressive monetization; strong modding culture
- **Cultural touchstones:** simulation and management games over-index; historical themes resonate; quality over flash
- **Spending habits:** high willingness to pay for complete products; strong resistance to F2P, loot boxes, and paid DLC that feels like cut content
- **Creator ecosystem:** top German-language gaming YouTubers and streamers for the genre

### France
- **Demographics:** source: SELL annual report, Médiamétrie gaming data
- **Discovery:** YouTube, Twitch (strong Twitch culture vs other EU markets), press (Jeuxvideo.com, Canard PC, Gamekult)
- **Community behavior:** strong Twitch streaming community; JVC (Jeuxvideo.com) forums are influential; humor-driven viral content
- **Cultural touchstones:** narrative depth appreciated; artistic games and games-as-art discourse is strong; RPGs and story-heavy games well-received
- **Spending habits:** similar to UK; price-sensitive on indies; loyal to beloved series
- **Creator ecosystem:** top French-language streamers and YouTubers for the genre

### Australia & New Zealand
- **Demographics:** source: IGEA Digital Australia report
- **Discovery:** TikTok (high penetration), YouTube, Reddit (shares US-style culture), Discord
- **Community behavior:** mirrors US culture closely; timezone makes them late to viral waves but amplifies them; strong mobile crossover audience
- **Cultural touchstones:** humor-forward, action and survival games over-index, underdog indie roots appreciated
- **Spending habits:** higher prices due to AUD conversion (games feel more expensive); strong response to local dev representation
- **Creator ecosystem:** AU/NZ-based streamers and YouTubers; note that many follow US creators

### Nordic (Sweden, Norway, Denmark, Finland)
- **Demographics:** source: Nordic Game Conference reports, IGDA Nordic surveys
- **Discovery:** YouTube, Steam Discovery (high Steam usage per capita), Reddit, gaming press (Gamereactor, PC Gamer Nordic)
- **Community behavior:** heavy PC gaming culture; high average playtime; appreciation for systems depth and emergent gameplay
- **Cultural touchstones:** dark/minimalist aesthetics appreciated; nature and exploration themes resonate; mythology (Norse in particular) is sensitive — must be done respectfully
- **Spending habits:** high purchasing power; willing to pay full price for quality; lowest piracy rates in EU
- **Creator ecosystem:** Nordic-based YouTubers and streamers; note large English-language creator presence

---

## Step 5 — Case Study Research

Find and document **at least 3 games** in the target genre that launched on Steam and had notable western market outcomes (success or failure — both are instructive).

**Search strategy:**
- `[genre] indie game Steam success story western market`
- `[genre] game marketing postmortem`
- `[game title] Steam wishlist launch sales GDC talk`
- `GameDiscover.co [genre] breakout analysis`
- `[game title] developer interview marketing`
- GDC Vault talks on marketing for the genre

**For each case study, capture:**

```
### [Game Title] ([Year])
- **Developer:** [Studio name, country]
- **Genre tags:** [Primary + secondary Steam tags]
- **Marketing approach:** [Key tactics used — trailers, influencer outreach, Steam Next Fest, press kits, etc.]
- **Regional performance:** [Where it hit hardest, where it underperformed — use press coverage, review distribution, SteamSpy estimates if available]
- **What worked:** [Specific tactic + reason it landed]
- **What failed or was missed:** [Specific miss + lesson]
- **Key inflection moments:** [Trailer release, influencer peak, festival demo, viral moment — with dates if known]
- **Steam metrics (public data only):** [Peak concurrent players, review count, rating %, SteamSpy owners estimate]
- **Sources:** [inline citations]
```

Aim for a mix: at least one large success, one underdog success, and one cautionary tale or missed opportunity.

---

## Step 6 — Marketing Channel Analysis

For the target genre, assess each channel's effectiveness per region:

**Steam-specific tactics:**
- Steam Next Fest: timing, trailer requirements, demo conversion benchmarks for the genre
- Steam seasonal sales: which ones matter for the genre (Halloween, Summer, etc.)
- Steam Curator network: top curators for the genre (search `[genre] Steam curators`)
- Wishlist campaign benchmarks: what counts as a strong wishlist count for this genre pre-launch
- Steam page optimization: tag strategy, capsule art conventions that work in the genre

**Social channels by region:**

| Channel | US/CA | UK | DE | FR | AU/NZ | Nordic |
|---------|-------|----|----|-----|-------|--------|
| TikTok | High | Med | Low | Med | High | Low |
| YouTube let's play | High | High | High | Med | High | Med |
| Reddit | High | Med | Low | Low | Med | Med |
| Twitch | Med | Med | Low | High | Low | Low |
| Discord | High | High | High | High | Med | High |
| Twitter/X | Med | Med | Low | Low | Low | Low |

(Fill in actual effectiveness ratings based on research, not just the defaults above)

**Press & media by region:**
- US/CA: PC Gamer US, Kotaku, IGN, Rock Paper Shotgun
- UK: PC Gamer UK, Rock Paper Shotgun, Eurogamer, EDGE
- DE: 4Players, GameStar, GamePro DE
- FR: Jeuxvideo.com, Canard PC, Gamekult, IGN France
- AU/NZ: Kotaku AU, IGN AU, Press Start AU
- Nordic: Gamereactor, FZ.se, Pelit (FI)

**Influencer tier guidance:**
- Macro (1M+ subscribers): expensive, broad reach, poor genre targeting — best for launch-window awareness only
- Mid-tier (100K–1M): best ROI for most indie genres — passionate, niche audiences
- Micro (<100K): highest engagement rate, most authentic — ideal for pre-launch community building
- Note which tier works best for the specific genre (e.g., horror: micro + mid-tier; survival: mid-tier dominant)

---

## Step 7 — Regional Comparison Table

Synthesize all findings into a single reference table:

```
## Regional Comparison: [Genre] on Steam

| Market | Genre Audience Size | Primary Discovery | Cultural Notes | Price Sensitivity | Community Hub | Must-Target Outlets |
|--------|-------------------|-------------------|----------------|-------------------|---------------|-------------------|
| US/CA | [Est. size] | [Channel] | [1-line note] | Low/Med/High | [Platform] | [Outlet names] |
| UK | | | | | | |
| DE | | | | | | |
| FR | | | | | | |
| AU/NZ | | | | | | |
| Nordic | | | | | | |
```

---

## Step 8 — Synthesis

Write the synthesis section:

1. **Top 3 cross-regional insights** — patterns that held true across all or most markets
2. **Top regional surprise** — one finding per market that would not be obvious without research
3. **Regional priority ranking** — which markets to invest in first for this genre (1 = highest ROI)
4. **Go-to-market sequence** — which region to lead with and why, how others follow

---

## Step 9 — Write the Research Report

Save to `output/YYYY-MM-DD_[genre-slug]-western-marketing-research.md`

Use this structure:

```
# [Genre] — Steam Western Marketing Research Report
*Date: YYYY-MM-DD*
*Genre: [genre]*
*Markets covered: [list]*
*Game scope: [indie / all / F2P]*
*Research angle: [pre-launch / launch / post-launch / evergreen]*

---

## Executive Summary
- [Finding 1]
- [Finding 2]
- [Finding 3]
- [Finding 4]
- [Finding 5]

---

## Genre Landscape
[Findings from Step 3]

---

## Player Behavior & Culture

### US & Canada
[Findings]

### UK
[Findings]

### Germany
[Findings]

### France
[Findings]

### Australia & New Zealand
[Findings]

### Nordic
[Findings]

---

## Case Studies

### [Game 1]
[Template from Step 5]

### [Game 2]
[Template from Step 5]

### [Game 3]
[Template from Step 5]

---

## Marketing Channel Analysis
[Findings from Step 6]

---

## Regional Comparison Table
[Table from Step 7]

---

## Synthesis & Insights
[Findings from Step 8]

---

## Sources & Citations
[1] [Title] — [URL] (Date)
[2] ...
```

---

## Step 10 — Write the Marketing Playbook

Save to `output/YYYY-MM-DD_[genre-slug]-western-marketing-playbook.md`

Use this structure:

```
# [Genre] — Steam Western Marketing Playbook
*Date: YYYY-MM-DD*
*Based on: [research report filename]*
*Markets: [list]*

---

## Pre-Launch Phase (6–12 Months Before Release)

### Wishlist Strategy
- [Specific actions: when to open Steam page, wishlist targets by genre, Next Fest timing]

### Community Seeding
- [Which platforms to start communities on, per region]
- [Content type: dev logs, WIP screenshots, GIF loops — what works for this genre]

### Festival & Showcase Submissions
- [Which events to target: Steam Next Fest, PAX Rising, IndieCade, Triple-I, etc.]
- [Lead times required for each]

### Press Outreach
- [Outlets to pitch per region, timing, pitch format for this genre]

---

## Launch Window (Day 0 – Day 30)

### Steam Visibility
- [Launch trailer specs, timing relative to release, Steam page checklist]
- [Tag optimization for the genre]
- [Review solicitation strategy]

### Influencer Outreach
- [Which tier to target per region]
- [Key creators to approach for this genre]
- [Keys vs paid — guidance for this genre]

### Launch Day Checklist
- [ ] Steam page fully optimized (tags, capsule, trailer, screenshots)
- [ ] Press embargo lifted same day as launch
- [ ] Influencer coverage coordinated for Day 0–3
- [ ] Community channels (Discord, Reddit) monitored live

---

## Post-Launch (30+ Days)

### Community Management
- [How to sustain community per platform, per region]
- [Update cadence that works for this genre]

### DLC & Update Cycle
- [Timing guidance based on case studies]
- [What kind of content drives re-engagement for this genre]

### Discount Strategy
- [Which Steam sales to participate in, when first discount is appropriate]
- [Regional pricing — does the genre benefit from regional price adjustments?]

### Long-Tail Growth
- [Bundle strategy, Humble Bundle, Fanatical]
- [Content creator re-engagement: patches, updates, anniversary events]

---

## Budget Allocation Guide

| Channel | US/CA | UK | DE | FR | AU/NZ | Nordic | Notes |
|---------|-------|----|----|-----|-------|--------|-------|
| Influencer outreach | | | | | | | |
| Press / media | | | | | | | |
| Paid social (TikTok/Meta) | | | | | | | |
| Steam promotions | | | | | | | |
| Festival fees | | | | | | | |

(Express as % of total marketing budget)

---

## Campaign Timeline

| Milestone | Timing | Owner | Target Markets |
|-----------|--------|-------|----------------|
| Steam page live | 12 months before | Dev | All |
| First Steam Next Fest | [dates based on genre + launch window] | Dev | All |
| Press preview build | 3 months before | Dev | US, UK, DE |
| Influencer keys sent | 4 weeks before | Dev/PR | Priority markets |
| Launch day | Day 0 | All | All |
| First major update | 30–60 days post | Dev | All |
| First discount | 90 days post | Dev | All |

---

## KPIs to Track

**Pre-launch:**
- Wishlist count at 6 months, 3 months, 1 month before launch
- Steam Next Fest demo downloads and wishlist conversion rate
- Influencer video views and wishlist-click attribution

**Launch window:**
- Day-1, Day-7, Day-30 concurrent players (SteamDB)
- Review count and positive % at Day-7 and Day-30
- Regional review breakdown (Steam shows regional review counts)
- Wishlist-to-purchase conversion rate

**Post-launch:**
- Monthly active players trend
- DLC attach rate
- Organic discovery share (new reviews from non-day-1 players)
- Refund rate (Steam developer dashboard)
```

After saving both files, confirm file paths to the user.

---

## Step 11 — Sync to Google Doc

After both output files are saved, rebuild and upload the full research doc by running:

```
python scripts/sync_to_research_gdoc.py
```

The script scans `output/` for **all** `*-western-marketing-research.md` + `*-western-marketing-playbook.md` pairs, converts them to formatted HTML, and replaces the Google Doc with the complete up-to-date document. No arguments needed.

**First run only:** If the script prints "Re-authorizing with expanded scopes", a browser window will open. Sign in and approve — token is saved automatically for all future runs.

After the script runs, confirm it printed:
> `Google Doc updated: https://docs.google.com/document/d/1miOctTSb2IHlfwRolEF1vQ3hDwiTJ1cMmyuKcDLXCZU/edit`

---

## Quality Checklist (Before Finishing)

- [ ] 3+ named case studies with specific marketing tactics, not just descriptions
- [ ] All requested markets covered with cultural specifics (not generic global observations)
- [ ] Regional comparison table present and fully filled in
- [ ] Marketing playbook has concrete action items with timing — not just categories
- [ ] Inline citations `[#]` on all data points and stats
- [ ] Both output files saved with `YYYY-MM-DD_[genre-slug]-western-marketing-[research|playbook].md`
- [ ] Genre slug is lowercase, hyphenated, no special characters
- [ ] Numbered sources list present in research report
- [ ] Pre-flight database check completed and findings noted (or noted as no match)
- [ ] 15+ sources cited total across both files
- [ ] Google Doc sync confirmed — Step 11 output shows the doc URL
