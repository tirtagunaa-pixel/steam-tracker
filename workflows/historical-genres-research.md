# Historical Genre Breakout Research Workflow (Database-First)

A step-by-step recipe Claude follows when asked to research and refresh the "Historical Genre Breakout Analysis" section of the indie game database.

Every genre listed must be grounded in launched games already in the database with documented performance data. No genre can be justified solely by a press article.

Run this workflow when you want to update or verify the historical genre section in the Summary tab. After completing it, run `python scripts/update_indie_db.py` to push the findings live.

---

## When to Re-run

- When the database adds a significant batch of new games (e.g., 50+ new entries)
- Annually — historical patterns shift as more games launch and data matures
- When a genre that was "emerging" has now fully broken out (move it from emerging to historical)

---

## Step 0 — Extract Launched Games from Database

Read `output/indie-game-conference-database-summary.md`. Filter for games where:
- Launch Status = "Launched" (or equivalent — released, fully launched)

Collect for each game: Game Name, Developer/Studio, Studio Country, Genre, Steam Rating, Estimated Sales, Revenue Estimate, Awards & Recognition, Conferences Showcased, Years Showcased.

This is your primary data source. All historical genres must trace back to games in this list.

---

## Step 1 — Cluster by Genre and Era

Group launched games by genre. For each genre cluster:
- Count how many games are in the cluster
- Find the **earliest** conference year any game in the cluster appeared (from Years Showcased)
- Find the **peak activity years** — the range when most games in the cluster were being showcased
- Assign an **Era** label (e.g., "2017–2019") based on conference peak activity

**Signal thresholds:**
- **Strong**: 4+ launched games in the cluster
- **Moderate**: 2–3 launched games with good performance data
- **Weak**: 1 game only — exclude unless it has exceptional awards + community signal

Rank clusters by game count. Aim to identify 6–10 historical genre breakouts.

---

## Step 2 — DB Performance Evidence

For each genre cluster, pull directly from the game records:

1. **Top-performing games** — filter for Steam Rating ≥ 90% OR Estimated Sales ≥ 500K copies
2. **Award-winning games** — check the "Awards & Recognition" field; note IGF wins, BAFTA nominations, GDC Awards, etc.
3. **Conference debut** — the earliest Year Showcased across the cluster, and which conference

These are your **Defining Games** — pick the 3–5 most representative, prioritizing high performers and award winners.

**DB Performance Evidence format:**
`Average Steam Rating across cluster: X%. Total estimated sales: Y. Awards: Z IGF nominations, N BAFTA nominations.`

---

## Step 3 — Community Validation Search (direct quotes required)

For each genre cluster, search for **player community reactions** — not critic reviews or press articles:

```
"[top game from cluster]" site:reddit.com OR site:steamcommunity.com "best game" OR "can't stop playing" OR "hidden gem"
"[genre name]" indie reddit 2016..2024 "best of" OR "recommendations"
"[top game]" steam reviews community response after launch
```

For each search: **copy the actual player comment verbatim** (top-voted Reddit comment or a representative Steam review). Record the direct URL to that specific comment/review.

**Format:**
`"[exact quoted comment]" — u/username, r/indiegaming, N upvotes (https://reddit.com/r/...)` or
`"[steam review quote]" — Steam username (https://store.steampowered.com/app/...)`

At least one direct quote per genre is required. No generic articles.

---

## Step 4 — Why It Broke Out (DB-justified)

Write 2–4 sentences explaining the genre's breakout using only DB-derived facts and community evidence:
- Reference the conference pattern: "Genre cluster appeared at GDC, PAX, and BitSummit simultaneously in 2018–2019 (X games in DB)"
- Reference the performance data: "Average Steam Rating across cluster: 93%. Combined estimated sales: 8M+ copies."
- Reference award patterns: "3 IGF nominations across the cluster 2018–2020"
- Include one direct player quote as evidence of community resonance
- Add one structural reason (low dev cost, streaming appeal, underserved audience, etc.) — but only if supportable by the data

Do **not** write "this genre broke out because articles said so." Every claim must trace to DB data or a direct community quote.

---

## Step 4a — X Axis Scoring: Skill Barrier / Difficulty

When scoring how hard a game is to access for the Mapping tab X axis (1 = Very Accessible → 10 = Punishing/Hardcore), use these three factors:

---

### Factor 1 — Design Intent (~40% weight)

What to look for: did the developer *intentionally* design for accessibility or for challenge as a core identity?

**Sources to check:**
- Developer GDC talks, postmortems, and interviews (e.g. "we wanted players to feel progression even when dying")
- How the game frames failure in its UI and narrative — does dying advance something (Hades: story progresses, mirror upgrades persist) or reset everything (Dead Cells: full permadeath, no persistent narrative)?
- Whether the progression system reduces punishment over time vs. keeps it constant
- Whether the game's marketing and description leads with difficulty ("prepare to die") or accessibility ("no fail state")

**Scoring guide:**
- 1–3: Failure is explicitly optional or consequence-free by design (auto-attacks, God Mode from the start, narrative continues on death)
- 4–6: Mixed intent — challenging but with meaningful onboarding or optional modifiers
- 7–10: Difficulty is the core identity; developer explicitly designed around skill gates with no softening

**Worked examples:**
- Hades (3.0): God Mode offered at game start, narrative progresses on every death — accessibility is a first-class design value
- Dead Cells (6.0): No narrative progression on death, no built-in softening — difficulty is intentional and marketed as such
- Nine Sols (8.5): Soulslike parry-timing philosophy explicitly stated by developer; game designed around mastery gates

---

### Factor 2 — Community-Documented Difficulty (~30% weight)

What to look for: how does the player community describe the challenge curve in their own words?

**Sources to check:**
- Metacritic user reviews — search for "difficult," "hard," "took me X hours to get past," "frustrating," "punishing," "impossible"
- Reddit communities (r/roguelikes, r/[game name]) — look for new player help threads, "how do I beat X" posts, "is this supposed to be this hard?" posts
- Community wiki complexity — a large, detailed wiki with in-depth guides (Hollow Knight wiki) indicates community perceived the game as requiring external help; a sparse wiki indicates accessibility
- Steam reviews sorted by "Funny" — often contain the most candid difficulty descriptions
- "Hours to first boss kill" or "hours to first win" patterns in community discussions

**Scoring guide:**
- 1–3: Community primarily describes it as "easy to pick up," "relaxing," "anyone can play this"
- 4–6: Community describes moderate challenge — "takes some getting used to," "fair difficulty," "punishing but fair"
- 7–10: Community broadly describes it as hard — "brutal early game," "died hundreds of times," "this destroyed me," multiple dedicated new-player help threads

**Worked examples:**
- Vampire Survivors (1.5): Community almost universally describes it as "impossible to fail early," "chill," "auto-play"
- Celeste (7.0): Community consistently notes hundreds of expected deaths — "Celeste is designed around failing repeatedly" is a common framing
- Hollow Knight (6.5): Large community wiki, extensive boss guides, multiple "is this game too hard?" Reddit threads

---

### Factor 3 — Accessibility Features (~30% weight)

What to look for: does the game provide built-in options that genuinely lower the skill barrier, and how prominently are they surfaced?

**Sources to check:**
- In-game settings menus and pause menus (does a difficulty slider or accessibility mode exist?)
- How early and prominently the option is shown — Hades surfaces God Mode within the first few deaths; Celeste's Assist Mode requires navigating into a submenu
- Whether the feature is presented as "intended" or "not the real experience" (Celeste's Assist Mode includes explicit text saying "this is not the intended experience")
- Whether the accessibility feature meaningfully changes the core challenge mechanic or is cosmetic
- Developer statements about the accessibility feature's design intent

**Scoring guide:**
- 1–3: Multiple built-in accessibility options, prominently surfaced early, designed without stigma (God Mode-style)
- 4–6: Accessibility options exist but require seeking out, or come with friction (hidden in menus, developer framing suggests "real mode" is harder)
- 7–10: Essentially no built-in accessibility options; difficulty is fixed and the only path forward is skill improvement

**Worked examples:**
- Hades (3.0): God Mode reduces damage taken by 2% per death, cumulative — surfaced prominently, designed as a first-class option
- Celeste (6.5): Assist Mode exists but is buried in menus with text noting it's not the "intended experience" — partial credit
- Nine Sols (8.5): No meaningful accessibility options; one difficulty setting that is very hard

---

### Final X Score

**X = (Design Intent score × 0.4) + (Community Difficulty score × 0.3) + (Accessibility Features score × 0.3)**

Score to one decimal place. The three factors should be assessed independently before combining — a game can have hard community perception (factor 2 = 8) but strong accessibility features (factor 3 = 2) that bring the total down.

---

## Step 4b — Y Axis Scoring: Commercial Mainstream Reach

When scoring how "mainstream" a historical genre's breakout was (for the Mapping tab Y axis), use this two-factor method:

**Copies Sold — 50% of Y axis score**
Use the game's estimated lifetime sales (from DB `Estimated Sales` field or public records):
- 30M+: 10
- 10M+: 9
- 5M+: 8.5
- 3M+: 8
- 1M+: 7
- 500K+: 6
- 100K–500K: 4–5
- Under 100K: 1–3

Where exact figures aren't available, use Steam review count, SteamSpy estimates, or developer-confirmed milestones as proxies.

**Community / Social Listening — 50% of Y axis score**
This bucket combines two signals:

*Mainstream cultural recognition (half of this 50% = 25% total):*
- Non-gaming press coverage: The Guardian, NPR, BBC Culture, The Atlantic, mainstream magazines
- The Game Awards Best Game / Best Indie win (mainstream gaming audience, not industry-facing)
- Clear meme / viral cultural moment (the game is referenced by people who don't play games)
- Known by non-gamers in your social circle (qualitative but useful proxy)

*Steam review language analysis (half of this 50% = 25% total):*
Search the top 20–30 Steam reviews for the genre's defining games. Look for phrases indicating the game reached audiences outside the core genre:
- "I don't normally play [genre] but..."
- "My [partner / friend / parent] got me into this"
- "First game I've played in years"
- "I'm not a gamer but..."
- "Bought this because I saw it on TikTok / YouTube / my feed"

High frequency of these phrases = strong crossover signal. Their absence = genre stayed within its core audience.

**Final Y score = (Copies Sold score × 0.5) + (Cultural Recognition score × 0.25) + (Steam Review Language score × 0.25)**

**Y axis scale:**
- 9–10: All three components clearly met — Stardew Valley (30M+), Balatro (5M+ + TGA GOTY) tier
- 7–8: Strong sales + one community signal strongly met — Hollow Knight, Dead Cells tier
- 5–6: Solid sales within the genre, limited mainstream crossover
- 3–4: Niche/specialist success, low sales scale
- 1–2: Underground, freeware, or community-only

**Note:** A game can have lower sales but high cultural recognition and still score well (e.g. Untitled Goose Game: 1M+ copies but global meme = ~7). Conversely, a game can have huge sales from niche repeat-buyers without mainstream crossover (e.g. modded Minecraft community sales vs. mainstream Minecraft brand recognition).

---

## Step 5 — Identify 6–10 Historical Breakout Genres

Order chronologically by era (earliest first).

For each genre, collect:

| Field | What to fill |
|-------|-------------|
| `era` | Era label e.g. "2017–2019" |
| `genre` | Genre name |
| `db_defining_games` | Top 3–5 games from DB with key stats: "Game (Developer, Steam%, Sales, Awards)" |
| `db_performance_evidence` | Aggregate stats from DB: average rating, total sales, award count |
| `why_it_broke_out` | DB-justified explanation + one direct player quote with URL |
| `game_market_fit` | For each defining game: one sentence explaining HOW that specific game addressed the market gap, followed by one citeable community/player quote or quantified signal that validates it. Format: "Game: [gap claim]. Community validation: \"[exact quote]\" — [username], [source] ([URL])." OR "Game: [gap claim]. Community signal: [stat + URL]." Pipe-separate multiple games. |
| `peak_years` | When genre was most active in the DB (conference peak) |
| `research_date` | Today's date (YYYY-MM-DD) |
| `sources` | Pipe-separated direct URLs to player threads, Steam pages, award pages only |

---

## Step 6 — Save Output JSON

Save to `output/historical-genres-latest.json`:

```json
[
  {
    "era": "2017–2019",
    "genre": "Metroidvania",
    "db_defining_games": "Hollow Knight (Team Cherry, 95% Steam, 2M+ copies, IGF Excellence in Visual Art Nominee 2018); Dead Cells (Motion Twin, 97% Steam, 5M+ copies, GDC Award 2019); Ori and the Will of the Wisps (Moon Studios, 98% Steam, 2M+ copies)",
    "db_performance_evidence": "5 games in DB in this genre. Average Steam Rating: 95.7%. Combined estimated sales: 10M+. Awards: 3 IGF nominations, 1 GDC Award, 2 BAFTA nominations across cluster.",
    "why_it_broke_out": "Conference cluster: Hollow Knight, Dead Cells and Ori appeared at PAX, GDC, and BitSummit simultaneously 2017–2018 (DB: 5 games, earliest showcase 2016). Performance: highest average Steam Rating of any genre in the DB. Community quote: \"Hollow Knight reignited my love for gaming. It's the best metroidvania ever made and it costs $15.\" — u/CaveKnight99, r/metroidvania, 12.4K upvotes (https://reddit.com/r/metroidvania/...). Structural reason: low asset cost (2D pixel/hand-drawn) + deep map exploration = high replay value + accessible to small teams.",
    "game_market_fit": "Hollow Knight: [how it addresses the gap]. Community validation: \"[exact player quote]\" — [username], Metacritic [score]/10 (https://...). | Dead Cells: [how it addresses the gap]. Community validation: \"[exact player quote]\" — [username], Steam (https://...).",
    "peak_years": "2017–2019",
    "research_date": "YYYY-MM-DD",
    "sources": "https://store.steampowered.com/app/367520/Hollow_Knight/ | https://reddit.com/r/metroidvania/... | https://igf.com/2018/..."
  }
]
```

---

## Step 7 — Save Human-Readable Report

Following `research.md` Step 6, also save:

- `output/YYYY-MM-DD_historical-indie-genres.md` — full markdown report with methodology, all genre tables, and sources
- `output/YYYY-MM-DD_historical-indie-genres.txt` — plain text version

The markdown report should include:
- Executive summary (3–5 bullets: most significant genre breakouts, patterns observed)
- Full genre table with explanations
- Database methodology notes (how games were filtered, thresholds used)
- Full source list with dates

---

## Step 8 — Push to Google Sheets

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"
python scripts/update_indie_db.py
```

The script auto-reads `output/historical-genres-latest.json` and writes it into the Summary tab's "HISTORICAL GENRE BREAKOUT ANALYSIS" section.

---

## Quality Checklist

- [ ] Every genre has 2+ launched games from the database
- [ ] Defining games include Steam Rating and/or Sales data from the DB
- [ ] DB Performance Evidence includes aggregate stats (average rating, total sales, award count)
- [ ] "Why It Broke Out" contains at least one verbatim player quote with a direct URL
- [ ] No generic press article used as the sole justification for any genre
- [ ] `historical-genres-latest.json` is valid JSON with schema fields (`era`, `genre`, `db_defining_games`, `game_market_fit`, `db_performance_evidence`, `why_it_broke_out`, `peak_years`, `research_date`, `sources`)
- [ ] Every game in `game_market_fit` has a citeable community/player source (direct quote with URL, or quantified signal with URL)
- [ ] Citations in `game_market_fit` are specific to the gap-fulfillment claim — not generic praise
- [ ] Both .md and .txt output files saved
- [ ] Script run confirms `[Historical genres] Using live research from historical-genres-latest.json`
