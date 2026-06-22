# Emerging Genres Research Workflow (Database-First)

A step-by-step recipe Claude follows when asked to research and refresh the "Emerging Genres to Watch" section of the indie game database.

Every genre listed must be backed by games already in the database. No genre can be justified solely by a press article.

Run this workflow whenever you want to update the emerging genres data in the Summary tab. After completing it, run `python scripts/update_indie_db.py` to push the findings live.

---

## When to Re-run

- After each major conference season (post-GDC in March, post-Gamescom in August, post-TGS in October)
- When a new genre appears to break out commercially (e.g., a new surprise hit like Balatro)
- Before any market research or pitch deck work — ensures emerging genres section is current

---

## Step 0 — Extract Unreleased Recently Showcased Games from Database

Read `output/indie-game-conference-database-summary.md`. Filter for all games where:
- Launch Status = "In Development", "Upcoming", "Announced", "Early Access", or "Demo"
- Years Showcased includes **2025 or 2026**

Build a working list of these games with their Genre, Awards & Recognition, Conferences Showcased, and Years Showcased. This is your **primary source** — all emerging genres must come from here.

---

## Step 1 — Cluster by Genre

Group the filtered games by genre. Count games per cluster:
- **3+ games** = Strong signal
- **2 games** = Moderate signal
- **1 game** = Weak / speculative (only include if it has exceptional community or award evidence)

Rank clusters by count. These clusters are your genre candidates. Write down 5–8 top candidates before moving on.

---

## Step 2 — Community Evidence (direct player quotes required)

For each genre cluster (top 5–8), search for **player reactions** to the specific games in that cluster — not press coverage:

```
"[game name]" site:reddit.com demo OR "first impressions" OR "played the demo"
"[game name]" site:steamcommunity.com review OR "wishlist" OR "demo"
"[game name]" r/indiegaming OR r/indiegames reaction OR "I played"
"[game name]" steam next fest wishlists most wishlisted 2025
```

For each game: **copy the actual player comment verbatim** (top-voted Reddit comment or a representative Steam review). Record the direct URL to that specific comment/post.

**Format for the JSON field:**
`"[exact quoted comment]" — u/username, r/indiegaming, N upvotes (https://reddit.com/r/...)` or
`"[steam review quote]" — Steam username (https://store.steampowered.com/app/...)`

Skip generic articles, press previews, or developer posts. Only player voices count.

---

## Step 3 — Award Evidence

For each genre cluster:
1. Check the "Awards & Recognition" column in the DB for all games in the cluster — this is already populated
2. Run targeted searches for gaps:
   ```
   "[game name]" IGF 2025 OR "Day of the Devs" OR "PAX Rising" award OR nominee OR finalist
   "[game name]" IndieCade 2025 OR BAFTA 2025 nominee
   ```
3. Record only **verified awards**: IGF nominee/winner, IndieCade Official Selection, Day of the Devs selection, BAFTA Games nomination, etc.

---

## Step 4 — Score and Assign Confidence

### Community Signal Weighting (75 / 25 split)

**Primary signals — 75% weight (highest evidence bar). ONE of these alone is sufficient:**
- Reddit: 5,000+ upvotes on a single game post (direct URL required)
- Steam wishlists: 50,000+ wishlists (direct Steam store page URL required)

**Secondary signals — 25% weight (supplementary). Two or more required to substitute for a weak primary signal):**
- TikTok: 100K+ hashtag views for the specific game title
- Discord: Active server with 1,000+ members
- YouTube: First-impressions or demo video with 50K+ views
- Twitch: Featured during Next Fest window with notable concurrent viewers
- itch.io: 10,000+ downloads (free/demo games only)
- Twitter/X: Viral announcement thread with 1,000+ quote tweets

**Sufficient community signal** = either:
- ONE primary signal cleared (5K+ Reddit upvotes OR 50K+ Steam wishlists), OR
- A lower primary threshold (3K+ upvotes / 30K+ wishlists) PLUS 2+ secondary signals documented

For each genre cluster, assign a Confidence level:
- **High**: 3+ unreleased DB games + sufficient community signal (per above weighting) + award evidence
- **Medium**: 2+ unreleased DB games + at least one of: community signal OR award evidence
- **Speculative**: 1–2 DB games + strong community signal only (must be exceptional — e.g. viral post, #1 wishlisted on Steam Next Fest)

Only include Speculative genres if the community signal is exceptional and documented with a direct link.

---

## Step 5 — Identify 5–8 Emerging Genres

Order from highest to lowest confidence.

For each genre, collect:

| Field | What to fill |
|-------|-------------|
| `genre` | Genre name — be specific ("cozy horror" not "horror") |
| `db_unreleased_games` | Games from our DB: name (Conference Year · Developer); semicolon-separated |
| `community_signals` | Verbatim player quote + username + URL; or Steam wishlist count + URL |
| `award_evidence` | Verified award/nomination names and game; or "None found" |
| `game_market_fit` | For each listed game: one sentence explaining HOW that specific game addresses the market gap, followed by one citeable community/player quote or quantified signal that validates it. Format: "Game: [gap claim]. Community validation: \"[exact quote]\" — [username], [source] ([URL])." OR "Game: [gap claim]. Community signal: [stat + URL]." Pipe-separate multiple games. |
| `confidence` | High / Medium / Speculative |
| `research_date` | Today's date (YYYY-MM-DD) |
| `sources` | Pipe-separated direct URLs to player threads, Steam pages, award pages only — no articles |

---

## Step 6 — Save Output JSON

Save to `output/emerging-genres-latest.json` (overwrites previous version):

```json
[
  {
    "genre": "Genre Name",
    "db_unreleased_games": "Game A (PAX Rising 2025 · Dev Studio A); Game B (GDC 2026 · Dev Studio B); Game C (BitSummit 2025 · Dev Studio C)",
    "community_signals": "\"This demo blew me away, the controls feel incredible\" — u/PlayerName, r/indiegaming, 8.2K upvotes (https://reddit.com/r/indiegaming/...); Game B Steam Next Fest Feb 2025 top-10 wishlisted (~220K wishlists, https://store.steampowered.com/app/...)",
    "award_evidence": "Game A: IGF 2025 Nominee — Excellence in Design; Game C: Day of the Devs 2025 Official Selection",
    "game_market_fit": "Game A: [how it addresses the market gap]. Community validation: \"[exact player quote]\" — [username], [source] ([URL]). | Game B: [how it addresses the gap]. Community signal: [stat] ([URL]).",
    "confidence": "High",
    "research_date": "YYYY-MM-DD",
    "sources": "https://reddit.com/r/indiegaming/... | https://store.steampowered.com/app/... | https://igf.com/2025/..."
  }
]
```

---

## Step 7 — Save Human-Readable Report

Following `research.md` Step 6, also save:

- `output/YYYY-MM-DD_emerging-indie-genres.md` — full markdown report with methodology notes, all findings, and sources
- `output/YYYY-MM-DD_emerging-indie-genres.txt` — plain text version

The markdown report should include:
- Executive summary (3–5 bullets: top findings, confidence levels)
- The full genre table with explanations
- Database cross-reference notes (which games from the DB drove each genre's inclusion)
- Full source list with dates

---

## Step 8 — Push to Google Sheets

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"
python scripts/update_indie_db.py
```

The script auto-reads `output/emerging-genres-latest.json` and writes it into the Summary tab's "EMERGING GENRES TO WATCH" section.

---

## Quality Checklist

- [ ] Every genre has at least one game from the database (unreleased, showcased 2025–2026)
- [ ] Community evidence contains verbatim player quotes with direct URLs — no articles
- [ ] Award evidence drawn from DB "Awards & Recognition" field or verified award page links
- [ ] Confidence levels assigned and justified
- [ ] `emerging-genres-latest.json` is valid JSON with new schema fields (`db_unreleased_games`, `community_signals`, `award_evidence`, `game_market_fit`, `confidence`)
- [ ] Every game in `game_market_fit` has a citeable community/player source (direct quote with URL, or quantified signal with URL)
- [ ] Citations in `game_market_fit` are specific to the gap-fulfillment claim — not generic praise
- [ ] Both .md and .txt output files saved
- [ ] Script run confirms `[Emerging genres] Using live research from emerging-genres-latest.json`
