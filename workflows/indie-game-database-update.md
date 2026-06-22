# Indie Game Conference Database — Update Workflow

A step-by-step recipe Claude follows to add new games to the database and refresh existing entries.

---

## When to Run This Workflow

- **Before any market research session** — check what games from your research target have prior conference appearances
- **After a major conference ends** — add newly showcased games while coverage is fresh
- **Quarterly refresh** — update performance metrics (Steam ratings, sales estimates) for existing entries

---

## Step 1 — Identify What to Update

Decide which conferences/years to add. Options:

1. **New year of an existing conference** — e.g., Nordic Game Conference 2026 just ended
2. **Gap-fill for a prior year** — e.g., BitSummit 2019 was never researched
3. **Entirely new conference** — a conference from the master list not yet in the database
4. **Performance refresh only** — no new entries, just update sales/ratings for launched games

State the target(s) clearly before proceeding.

---

## Step 2 — Research Indie Showcase Rosters

For each conference/year target, search ALL of the following source types (do not rely on just one):

### A. Official Sources

- **Conference website** — look for: Exhibitors, Showcase, Finalists, Award nominees, Indie Spotlight
  - Search: `"{Conference Name}" indie showcase {year} games`
  - Search: `"{Conference Name}" {year} exhibitors list`

- **Steam curator / collection page** — many conferences (Nordic Game, BitSummit, etc.) maintain a Steam page with curated game lists
  - Search: `"{Conference Name}" steam indie collection`
  - Search: `site:store.steampowered.com "{Conference Name}"`

- **Conference YouTube channel** — showcase trailers and highlight reels name games in titles and descriptions
  - Search: `"{Conference Name}" {year} indie showcase youtube`
  - Search: `"{Conference Name}" {year} games reveal trailer`

### B. Social & Community Sources

- **Reddit** — post-event threads often list all games shown
  - Search: `site:reddit.com "{Conference Name}" {year} indie games`
  - Check: r/indiegaming, r/gamedev, r/Games

- **Facebook** — official conference pages post showcase announcements; developer pages tag conferences
  - Search: `site:facebook.com "{Conference Name}" {year} indie showcase`
  - Search: `"{Conference Name}" {year} showcasing developer facebook`

- **Twitter/X** — conference hashtags; developer announcement tweets
  - Search: `"{Conference Name}" {year} indie developer "showcasing at"`
  - Search: `"#{ConferenceHashtag}" {year} indie game`

### C. Press Coverage

- **GamesIndustry.biz, Pocket Gamer Biz, IndieGames.com** — post-event roundups
  - Search: `"{Conference Name}" {year} indie games roundup site:gamesindustry.biz`

---

## Step 3 — For Each New Game Found, Collect Data

Populate all fields per game. Required fields marked with *.

| Field | How to Find |
|-------|-------------|
| **Game Name** * | From showcase list or press coverage |
| **Developer / Studio** * | Studio page, Steam store page, itch.io |
| **Studio Country** | Studio's About page or LinkedIn |
| **Conferences Showcased** * | Name(s) where the game appeared |
| **Years Showcased** * | Year(s) of those appearances |
| **Genre** | Steam tags, developer description |
| **Platform(s)** | Steam / App Store / console store page |
| **Launch Status** * | Launched / Early Access / In Development / Cancelled / Unknown |
| **Launch Year** | Steam release date |
| **Steam Rating** | Steam store page — e.g. "Very Positive (94%, 12,400 reviews)" |
| **Metacritic Score** | metacritic.com — e.g. "88" |
| **Estimated Sales** | SteamSpy, post-mortems, developer announcements |
| **Revenue Estimate** | Developer GDC talks, public filings, press estimates |
| **Awards & Recognition** | IGF nominations, GOTY lists, BAFTA nominations |
| **Significance** | One-line: why this game matters — breakout hit, cult classic, influential mechanic, regional success |
| **Sources** | List URLs used |

---

## Step 4 — Refresh Performance Data for Existing Games

For games already in the database that have launched:

1. Check Steam store page for updated rating and review count
2. Check for new sales milestones announced by developer
3. Check for new awards (IGF, BAFTA, GOTY nominations)
4. Update `Launch Status` if a game that was "In Development" has now launched

---

## Step 5 — Build the JSON Input File

Compile new/updated records into a JSON file at `output/db_update_YYYY-MM-DD.json`:

```json
[
  {
    "Game Name": "Example Game",
    "Developer / Studio": "Example Studio",
    "Studio Country": "Finland",
    "Conferences Showcased": "Nordic Game Conference; Gamescom",
    "Years Showcased": "2022; 2023",
    "Genre": "Puzzle Platformer",
    "Platform(s)": "PC, Nintendo Switch",
    "Launch Status": "Launched",
    "Launch Year": "2024",
    "Steam Rating": "Very Positive (91%, 3,200 reviews)",
    "Metacritic Score": "84",
    "Estimated Sales": "~500K copies",
    "Revenue Estimate": "",
    "Awards & Recognition": "IGF 2023 Excellence in Design nominee",
    "Significance": "Breakout Finnish indie; 500K copies without a publisher",
    "Sources": "https://... | https://..."
  }
]
```

Use semicolons to separate multiple values in a single cell (Conferences, Years).

---

## Step 6 — Push to Google Sheet

Run the sync script:

```bash
# Dry run first — preview changes without writing
python scripts/update_indie_db.py --data output/db_update_YYYY-MM-DD.json --dry-run

# Write for real
python scripts/update_indie_db.py --data output/db_update_YYYY-MM-DD.json
```

You'll receive a Google Sheets email notification when new rows are added.

---

## Step 7 — Full Refresh (Genre Research + Summary + Showcase Tracker Rebuild)

After adding new games, follow **`workflows/database-refresh.md`** to:

1. Re-run historical genres research if newly added games shift any genre cluster evidence
2. Re-run emerging genres research if newly added games are unreleased titles showcased in 2025–2026
3. Run `python scripts/update_indie_db.py` to push refreshed JSON to the Summary and Showcase Tracker tabs

> **Shortcut — skip the full research re-run if:**
> - Fewer than 5 games were added AND none fall within tracked genre clusters
> - In that case, just run `python scripts/update_indie_db.py` to rebuild computed tabs

---

## Step 8 — Update the Summary Report

If any newly added game qualifies as a **breakout hit or significant title**, add it to:
`output/indie-game-conference-database-summary.md`

Criteria for inclusion in the summary:
- Launched with Very Positive or above on Steam (85%+)
- Sold 500K+ copies, or
- Won a major award (IGF, BAFTA, GOTY category), or
- Demonstrated significant regional impact (top seller in an emerging market)

---

## Step 8 — Integration Rule for Research Sessions

> **Before running any web searches in a research session**, check the Google Sheet or the summary report for:
> - Games from the genre/region being researched that already have conference history
> - Developers whose prior games appeared at conferences
> - Patterns: which conferences are producing the most breakout hits in a given genre/region

Use the database as the first source, then supplement with live web searches.

---

## Master Conference List Reference

All 110+ conferences tracked in this database are sourced from the PDF:
`resources/Game Conferences List - Publisher Focused.pdf`

Tiers:
- **Tier 1** (highest data availability): GDC, PAX (East/West/Aus), Gamescom/Devcom, BitSummit, Tokyo Game Show, IndieCade, Nordic Game, Reboot Develop Blue, A Maze, Digital Dragons
- **Tier 2** (moderate): DevGAMM series, Develop Brighton, PGC Connects series, BIC Festival, Games Connect Asia Pacific, Gamescom Asia, IGDX, G2G Jakarta, GamesForum Hanoi, LevelUp KL
- **Tier 3** (limited public data): All remaining conferences — add entries as coverage is found
