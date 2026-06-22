# Western Player Behavior & Cultural Drivers Research Workflow

A step-by-step recipe Claude follows to research the cultural and behavioral forces that drove (or are driving) indie genre breakouts in the Western gaming market.

Run this workflow when you want to update or refresh the "WESTERN PLAYER BEHAVIOR & CULTURAL DRIVERS" section of the Summary tab. After completing it, run `python scripts/update_indie_db.py` to push findings live.

---

## When to Re-run

- Annually — player behavior data changes meaningfully year-over-year
- After a major cultural shift (new platform launch, another pandemic-scale event, major demographic survey release)
- Before any market research or pitch deck work — ensures the behavioral context is current
- After adding new genres to the Historical or Emerging genre sections (new genres may introduce new drivers)

---

## Step 0 — Seed from Genre Reasoning

Read `output/historical-genres-latest.json` and `output/emerging-genres-latest.json`. For each entry, scan the `breakout_reasoning` field and extract every player behavior / cultural factor mentioned.

Group by frequency:
- **Tier 1**: appears in 3+ genres = major driver (primary research target)
- **Tier 2**: appears in 2 genres = moderate driver (secondary research target)
- **Tier 3**: appears in 1 genre = minor driver (mention only if data is readily available)

The current Tier 1 drivers (13 total) are:
1. COVID-19 / Pandemic Gaming Boom
2. Twitch / Livestreaming as Discovery Engine
3. Nostalgia / Returning Adult Gamers
4. Accessibility / Non-Traditional Gamer Demographics
5. Mental Health Mainstreaming & Gaming as Therapy
6. 'Cottagecore' / Slow Living / Self-Care Cultural Movement
7. Adult Gamer Time Constraints (short-session demand)
8. Content Creator / Influencer Ecosystem (TikTok, YouTube)
9. Female / Non-Binary Gamer Demographic Growth
10. Discord / Social Gaming Infrastructure
11. Mastery Culture / 'Git Gud' Identity
12. Gen Z Liminal Space & Analog Horror Aesthetics
13. Global Streaming & Non-Western Cultural Acceptance

---

## Step 1 — Research Each Driver (Run 3 Agents in Parallel)

### Priority Sources (use these before general web search)
```
Newzoo global gaming market reports: newzoo.com/resources/blog
GDC State of the Game Industry: gdconf.com/state-of-game-industry
ESA (Entertainment Software Association) annual reports: theesa.com/resources
Nielsen SuperData gaming surveys: neilsen.com/solutions/gaming
StreamElements / Stream Hatchet: streamelements.com/blog
Axios / Quartz gaming coverage: axios.com/technology/gaming
Variety / Hollywood Reporter gaming market coverage
GameDiscoverCo newsletter (gamediscover.co)
Statista gaming statistics: statista.com/topics/gaming
NPD Group gaming data
```

### Search Queries Per Driver

**Driver 1 — COVID-19 Gaming Boom**
```
"new gamers 2020" Newzoo OR ESA OR Nielsen statistics pandemic
"gaming demographics" 2020 COVID report new players
steam concurrent users 2020 growth record
"casual gamers" 2020 increase statistics report
gaming revenue growth 2020 lockdown statistics
```

**Driver 2 — Twitch / Livestreaming Discovery**
```
"game discovery" Twitch 2019 2020 2021 statistics streaming impact
"how players discover games" survey 2020 2022 streaming
Twitch hours watched 2016 2020 2024 statistics growth
"streaming influence" game sales statistics report
streamelements gaming 2020 2021 top games viewed
```

**Driver 3 — Nostalgia / Returning Adult Gamers**
```
"millennial gamers" nostalgia gaming behavior survey statistics
"returning gamers" 2020 demographics report
"nostalgia gaming" retro revival statistics market
GDC survey "player age" demographics 2020 2024
"lapsed gamers" 2020 COVID returning statistics
```

**Driver 4 — Accessibility / Non-Traditional Demographics**
```
"casual gamers" market growth 2016 2025 statistics
"non-gamer" audience games 2020 statistics survey
gaming audience "first time" 2020 demographics
mobile to PC gaming migration statistics
"puzzle games" "narrative games" accessibility growth statistics
```

**Driver 5 — Mental Health & Gaming as Therapy**
```
"gaming mental health" therapy statistics survey 2020 2025
"games for mental health" growth report statistics
"anxiety depression" gaming coping statistics 2020 2024
"games as therapy" mainstream acceptance statistics
"gaming wellbeing" survey ESA OR APA statistics
```

**Driver 6 — Cottagecore / Slow Living Movement**
```
"cozy games" market growth Steam statistics 2020 2025
"cottagecore" Google Trends statistics 2020 2022
"farming sim" genre growth statistics Steam 2020 2024
"cozy gaming" search trends statistics TikTok 2021 2023
"slow living" gaming crossover statistics
```

**Driver 7 — Adult Gamer Time Constraints**
```
"gaming session length" statistics adults 2020 2025
"average gaming time" adults demographics survey 2022 2024
"time-limited" gamers statistics behavior survey
GDC survey "gaming time" adults statistics
"short session" game design demand statistics
```

**Driver 8 — Content Creator / Influencer Ecosystem**
```
"TikTok game discovery" statistics 2022 2025 gaming
"YouTube gaming" discovery statistics survey 2020 2024
"influencer" game discovery statistics report
"how people discover games" survey 2022 2024 content creator
BookTok "BookTok effect" gaming equivalent statistics
```

**Driver 9 — Female / Non-Binary Demographic Growth**
```
"women gamers" percentage 2016 2025 statistics ESA
"female gamers" growth demographics survey report
ESA "women" gaming statistics 2020 2024
"non-binary" gaming demographics survey statistics
"cozy games" gender demographic statistics survey
```

**Driver 10 — Discord / Social Gaming Infrastructure**
```
Discord users statistics 2020 2025 growth gaming
"Discord" gaming community statistics growth
"social gaming" infrastructure Discord statistics 2019 2024
Discord gaming servers statistics 2020 2024
"voice chat" gaming social adoption statistics
```

**Driver 11 — Mastery Culture / 'Git Gud'**
```
"souls-like" genre growth statistics 2017 2024
"roguelike" mastery culture statistics community growth
"git gud" gaming culture statistics 2016 2022
"challenging games" player preference survey statistics
Twitch "mastery" gaming content statistics
```

**Driver 12 — Gen Z Aesthetics (Liminal Space / Analog Horror)**
```
"analog horror" YouTube views statistics 2021 2025
"liminal space" Google Trends statistics 2020 2024
"Gen Z gaming" aesthetics survey behavior statistics
"horror content" Gen Z consumption statistics 2022 2025
"nosleep" reddit growth statistics 2020 2024
```

**Driver 13 — Global Streaming / Non-Western Acceptance**
```
Netflix "international content" viewership statistics 2019 2024
Parasite "global film" mainstream acceptance statistics data
"Squid Game" viewership statistics Netflix impact gaming
"international games" Western acceptance survey statistics
"non-Western games" sales statistics growth 2020 2025
```

---

## Step 2 — For Each Driver, Collect All Fields

| Field | What to fill |
|-------|-------------|
| `driver` | Short descriptive name (e.g., "COVID-19 Gaming Boom") |
| `peak_period` | Year range when most impactful (e.g., "2020–2022") |
| `genres_impacted` | Comma-separated list of genre names from our DB this explains |
| `key_statistics` | 1–3 specific cited data points with numbers and source name. Format: "Stat (Source, Year)" |
| `behavioral_shift` | Concrete description of how this changed player discovery, purchasing, or play patterns |
| `current_status` | One of: "Active", "Fading", "Transformed" — plus 1–2 sentence description of 2025–2026 state |
| `research_date` | Today's date (YYYY-MM-DD) |
| `sources` | Pipe-separated direct URLs to the reports/surveys/articles used |

**Data quality rules:**
- `key_statistics` must contain at least ONE number (percentage, count, revenue figure, etc.) with a named source
- `sources` must be direct links to the actual report/article page, not homepages
- If data is unavailable for a driver, note "No industry survey data available — qualitative signal only" in `key_statistics`
- Do NOT invent statistics — if you cannot find cited data, say so explicitly

---

## Step 3 — Save Output JSON

Save to `output/player-behavior-research-latest.json`:

```json
[
  {
    "driver": "COVID-19 Gaming Boom",
    "peak_period": "2020–2022",
    "genres_impacted": "Farming/Life Sim, Cozy/Wholesome, Social Co-op Multiplayer, Physics Co-op Party",
    "key_statistics": "26% of gamers started or resumed gaming during COVID lockdowns (Newzoo 2021); US game spending rose 27% in 2020 to $56.9B (NPD Group 2021); Steam peak concurrent users hit 24M in April 2020 vs. 18M in 2019 (Valve 2020)",
    "behavioral_shift": "Millions of non-gamers entered the market for the first time through accessible, low-barrier genres (farming sims, cozy games). Friend groups that had never played together began gaming as a social substitute for in-person gatherings. Gaming session frequency increased across all demographics as other leisure activities were unavailable.",
    "current_status": "Fading — the acute pandemic-era gaming spike reversed 2022–2024 as in-person social activities resumed. However, the demographic expansion (millions of new players who discovered gaming) is permanent; the new players did not fully exit the market.",
    "research_date": "YYYY-MM-DD",
    "sources": "https://newzoo.com/resources/blog/... | https://www.statista.com/..."
  }
]
```

Order entries from most genres impacted to least.

---

## Step 4 — Save Human-Readable Report

Save:
- `output/YYYY-MM-DD_player-behavior-research.md` — full report with methodology, findings per driver, and source list
- `output/YYYY-MM-DD_player-behavior-research.txt` — plain text version

---

## Step 5 — Push to Google Sheets

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"
python scripts/update_indie_db.py
```

The script auto-reads `output/player-behavior-research-latest.json` and writes a new "WESTERN PLAYER BEHAVIOR & CULTURAL DRIVERS" section into the Summary tab, placed above the Historical Genre Breakout section.

---

## Quality Checklist

- [ ] All 13 Tier 1 drivers covered
- [ ] Every driver has at least 1 cited statistic with a number and source name
- [ ] `sources` field contains direct article/report URLs (not homepages)
- [ ] `genres_impacted` uses exact genre names from our DB
- [ ] `current_status` reflects 2025–2026 state (not just historical peak)
- [ ] Any absent data noted explicitly ("No industry survey available — qualitative only")
- [ ] JSON is valid and contains exactly 13 entries (or more if Tier 2 drivers added)
- [ ] Script run confirms `[Player behavior] Using live research from player-behavior-research-latest.json`
