# Community Discovery Research Workflow

A step-by-step recipe Claude follows to find popular indie games from community platforms that aren't captured by conference-based research.

Run this workflow periodically (quarterly, or when you want to ensure the database reflects community favorites, not just conference-circuit games). After completing it, run `python scripts/update_indie_db.py --data output/db_community_YYYY-MM-DD.json` to push findings to the sheet.

---

## When to Run

- Quarterly refresh — community hits emerge faster than conferences surface them
- Before any SEA or mobile market research — community platforms often surface regional hits earlier
- When a "surprise breakout" game appears that wasn't at conferences
- After Steam Next Fest ends — top wishlisted games are now publicly known

---

## Step 0 — Seed Check (Avoid Duplicates)

Before searching, read `output/indie-game-conference-database-summary.md` to extract the full list of games already tracked. Keep this list in mind — if a game appears during research and is already in the database, **skip it** (no duplicate needed) unless it has a new community source worth adding to its record.

---

## Step 1 — Research Each Source Group

Search all 12 sources. Run agents in parallel across three groups for speed.

### Group A — Reddit & Community Forums

**r/IndieGaming, r/indiegames, r/gamedev, r/GamePlayTest, TIGSource**

Search targets:
```
site:reddit.com/r/indiegaming "I made this" indie game upvotes 2016..2026
site:reddit.com/r/gamedev "I made this" viral game 1000 upvotes
reddit.com r/IndieGaming "hidden gem" most upvoted games list
site:reddit.com/r/gameplaytest best reviewed demos 2022..2026
TIGSource forums notable devlog commercial release 2016..2026
reddit r/indiegaming most popular posts all time games
"r/indiegaming" top games year best of list
```

What to capture:
- Games that had viral "I made this" posts (10K+ upvotes)
- "Best of [year]" community lists
- Games consistently recommended in "hidden gem" threads
- TIGSource devlogs for games that became notable commercial releases

### Group B — itch.io / Ludum Dare / Global Game Jam / Alpha Beta Gamer

**itch.io New & Popular, game jams, Ludum Dare, Global Game Jam, Alpha Beta Gamer**

Search targets:
```
itch.io most downloaded games 2016..2026 indie
itch.io top rated games all time
"ludum dare" top rated games became commercial release
"global game jam" notable games commercial release 2016..2026
site:alphaBetagamer.com best indie games 2020..2026
itch.io game jam winners that became full games
ludum dare winners 2016 2017 2018 2019 2020 2021 2022 2023 2024 games
itch.io 1 million downloads free games indie
```

What to capture:
- itch.io games with 100K+ downloads or Overwhelmingly Positive ratings
- Ludum Dare entries (top 3 rated per jam) that became commercial releases
- Global Game Jam projects that got expanded (examples: Celeste started as a LD jam)
- Alpha Beta Gamer featured games with large pre-launch communities

### Group C — Steam Next Fest / GameDiscoverCo / Deconstructor of Fun / No Small Games / Best Indie Games (Clemmy)

**Steam Next Fest wishlists, newsletters, curated lists**

Search targets:
```
Steam Next Fest 2019 2020 2021 2022 2023 2024 2025 top wishlisted games
"Steam Next Fest" most wishlisted indie demos all time
site:gamediscover.co best indie games 2022..2026
site:gamediscover.co "top performers" steam indie
"deconstructor of fun" best indie games analysis 2020..2026
"no small games" recommended indie games 2020..2026
"best indie games" site:bestindiegames.com top list 2016..2026
clemmy best indie games list 2020..2026
gamesindustry.biz "surprise hit" OR "breakout indie" 2020..2026
```

What to capture:
- Steam Next Fest top ~10 wishlisted games per fest (2019–2025)
- Games featured in GameDiscoverCo as having unusual wishlist-to-sales conversion
- Games analyzed in Deconstructor of Fun for monetization/design innovation
- Games on No Small Games' recommended lists
- Clemmy's curated annual best-of lists

---

## Step 2 — For Each Game Found, Collect All Fields

Use the standard database schema. For community-discovered games:

| Field | What to fill |
|-------|-------------|
| `Game Name` | Official title |
| `Developer / Studio` | Studio/solo developer name |
| `Studio Country` | Country of origin |
| `Conferences Showcased` | The community platform where it was found: e.g., `"itch.io New & Popular"`, `"Steam Next Fest wishlists"`, `"r/IndieGaming"`, `"Ludum Dare"`, `"Alpha Beta Gamer"` |
| `Years Showcased` | Year of peak community attention or discovery |
| `Genre` | Game genre |
| `Platform(s)` | Where available |
| `Launch Status` | Launched / Early Access / In Development / Free (itch.io) |
| `Launch Year` | If released |
| `Steam Rating` | If on Steam |
| `Metacritic Score` | If available |
| `Estimated Sales` | If publicly known |
| `Revenue Estimate` | If publicly known |
| `Awards & Recognition` | Jam awards, community recognition, viral metrics |
| `Significance` | WHY the community noticed it — be specific: "1M+ itch.io downloads pre-Steam launch", "Viral Reddit post 45K upvotes led to publisher deal", "Steam Next Fest #1 wishlisted 2023", "Ludum Dare 48 winner expanded into commercial release" |
| `Sources` | URLs to the community posts/pages that confirmed the game's popularity |
| `Last Updated` | Today's date |

**Filter threshold** — only include games that meet at least one of:
- 50K+ Steam wishlists from Next Fest
- 100K+ itch.io downloads / plays
- Reddit post with 5K+ upvotes
- Top-rated Ludum Dare entry (top 10 overall in any jam)
- Featured by ≥2 of the curator sources (GameDiscoverCo, Clemmy, Alpha Beta Gamer, No Small Games)
- Clear viral community moment with documented evidence

---

## Step 3 — Exclude Already-Tracked Games

Before finalizing the JSON, compare against known database entries (from Step 0). Remove games already in the database. If a game is in the database but has a new community source worth noting, add an UPDATE record with just the updated `Conferences Showcased` and `Sources` fields.

---

## Step 4 — Save Output JSON

Save to: `output/db_community_YYYY-MM-DD.json`

Use exactly the standard schema field names from the database (`Game Name`, `Developer / Studio`, etc.)

---

## Step 5 — Save Research Report

Following `research.md` Step 6:
- `output/YYYY-MM-DD_community-indie-discovery.md`
- `output/YYYY-MM-DD_community-indie-discovery.txt`

---

## Step 6 — Push to Google Sheets

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"
python scripts/update_indie_db.py --data output/db_community_YYYY-MM-DD.json
```

The script deduplicates against existing records automatically.

---

## Quality Checklist

- [ ] All 12 sources checked (or noted as unavailable with reason)
- [ ] Filter threshold applied — no games added without evidence of community traction
- [ ] No games already in the database added as new entries
- [ ] `Significance` field explains the specific community signal for each game
- [ ] `Conferences Showcased` uses the exact platform name format (see Step 2)
- [ ] Output JSON is valid and uses exact field names
- [ ] Both .md and .txt report files saved
