# Research Workflow

A step-by-step recipe Claude follows when asked to research any topic.

---

## Step 0 — Check the Indie Game Database (Always First)

Before running any web searches, check the living database for prior knowledge:

1. Open `output/indie-game-conference-database-summary.md` — scan for games matching the research topic's genre or region
2. If access to the Google Sheet is available, query it for:
   - Games from the target genre that appeared at conferences
   - Developers whose prior games have conference history
   - Which conferences are producing breakout hits in the relevant region

Use any matches as **seed entries** for deeper research — these are pre-validated games with known conference history and performance data.

If no matches are found, proceed directly to Step 1.

---

## Step 1 — Ask Clarifying Questions

Before doing any research, ask the user these questions (use AskUserQuestion with up to 4 questions at once):

1. **Angle** — What specific angle matters most?
   - Options: market size & revenue, key players & companies, technology & trends, consumer behavior, history & origins, competitive landscape, **emerging indie games & convention showcases**
   - Allow the user to pick multiple or type their own

2. **Use case** — What will this research be used for?
   - Options: competitive analysis, pitch deck, game design inspiration, investment research, general learning
   - Allow the user to type their own

3. **Recency** — How time-sensitive does the data need to be?
   - Options: Latest 6 months only, Last 2 years, Any timeframe (historical OK)

4. **Exclusions** — Is there anything to explicitly skip or avoid?
   - Free text — leave blank if nothing to exclude

Do not start researching until these answers are received.

---

## Step 2 — State the Research Plan

Before executing, briefly tell the user:
- The topic and the confirmed scope (angles + use case)
- Which sections the report will include
- Roughly how many sources you'll target (aim for 10+)

Example:
> "Researching [topic] with a focus on [angles]. I'll cover [sections] across ~12 sources. Starting now."

---

## Step 3 — Execute Research

Search using WebSearch. Target 10 or more sources total.

**Source priority — Emerging / Indie Game Research (highest to lowest):**

When the topic involves emerging, pre-viral, or indie games, use this priority order. Mainstream press covers trends *after* they break — indie showcases surface them *before*.

1. **Indie convention showcases & exhibitor lists** *(highest signal for pre-viral discovery)*
   - GDC (Game Developers Conference) — Independent Games Summit, GDC Play exhibitor list, GDC Vault talks
   - Triple-I Initiative — dedicated indie publisher showcase (digital, runs multiple times per year)
   - PAX (East / West / Aus / Online) — PAX Rising indie showcase floor
   - IndieCade — indie game festival & competition finalists
   - Day of the Devs — curated indie showcase (Double Fine / iam8bit)
   - BitSummit — Japanese indie games showcase (Kyoto)
   - Tokyo Game Show — Indie Game Area exhibitor list
   - Gamescom / Devcom — indie dev conference track and indie arena
   - PGC Connects (Pocket Gamer Connects) — mobile/indie pitch competition finalists
   - Steam Next Fest — upcoming indie demos; check wishlist counts and download numbers

2. **Indie-specialist press & community signals**
   - GamesIndustry.biz indie coverage
   - Pocket Gamer Biz (mobile indie)
   - IndieGames.com and itch.io featured / staff picks
   - GameDiscover.co newsletter (Simon Carless — Steam data-driven indie analysis)
   - Reddit: r/indiegaming, r/gamedev breakout threads
   - Indie Twitter/X community signals (developer announcements, wishlist milestones)

3. **Official company / publisher data and press releases**

4. **Industry analyst reports** (Newzoo, Sensor Tower, App Annie, IDC, Accio, Naavik)

5. **Reputable financial or business news** (Reuters, Bloomberg, Forbes)

6. **Mainstream gaming press** (IGN, Kotaku, Eurogamer) — use for confirmation, not discovery

---

**Indie research search strategy:**

When the topic involves emerging or pre-viral games, always run at least one search explicitly targeting convention showcase coverage or exhibitor lists. Examples:
- `GDC 2025 indie showcase participants new games`
- `Triple-I Initiative 2025 2026 lineup`
- `PAX Rising 2025 notable games`
- `Steam Next Fest [month year] standout demos wishlist`
- `BitSummit 2025 highlights new developers`
- `[game title] GDC 2025 demo` (if following up on a specific title)

This catches titles that haven't yet received mainstream press coverage.

---

For each source, record:
- The URL
- The key finding(s) extracted from it
- The date of publication (if available)

---

## Step 4 — Organize Findings

Before writing the report, mentally group all findings into these buckets:
- Executive summary bullets (the 3-5 most important takeaways)
- Key data & stats (numbers, percentages, revenue, user counts, growth rates)
- Key players & companies (who matters in this space)
- Dynamic sections (determined by the angles the user selected)
- Source list

---

## Step 5 — Write the Report

Use this exact structure:

```
# [Topic] — Research Report
*Date: YYYY-MM-DD*
*Prepared for: [use case the user stated]*

---

## Executive Summary
- [Finding 1]
- [Finding 2]
- [Finding 3]
- [Finding 4 — optional]
- [Finding 5 — optional]

---

## Key Data & Stats
- [Stat with source number, e.g. "Market size: $4.2B in 2024 [3]"]
- [...]

---

## Key Players & Companies
- **[Company/Studio Name]** — [One-line description of what they do and why they matter]
- [...]

---

## [Dynamic Section 1 — based on user's selected angle]
[Bullet points or short paragraphs]

## [Dynamic Section 2 — if applicable]
[Bullet points or short paragraphs]

---

## Sources & Citations
[1] [Title or description] — [URL] ([Date if known])
[2] ...
```

Rules:
- Use bullet points over paragraphs wherever possible
- Keep each bullet to 1-2 lines
- Cite sources inline with bracketed numbers [1], [2], etc.
- Do not editorialize — report what sources say
- If data conflicts between sources, note both and flag the discrepancy

---

## Step 6 — Save Output

Save two files to the `output/` folder:

1. `output/YYYY-MM-DD_[topic-slug].md` — the full markdown report
2. `output/YYYY-MM-DD_[topic-slug].txt` — plain text version (strip markdown formatting)

The topic slug should be lowercase, hyphen-separated, no special characters.
Example: topic "Mobile Battle Royale in SEA" → slug `mobile-battle-royale-sea`

After saving, confirm the file paths to the user:
> "Report saved to:
> - output/2026-05-26_mobile-battle-royale-sea.md
> - output/2026-05-26_mobile-battle-royale-sea.txt"

---

## Quality Checklist (before finishing)

- [ ] 10+ sources used and cited
- [ ] All mandatory sections present: Executive Summary, Key Data & Stats, Key Players, Sources
- [ ] Every stat has an inline citation
- [ ] Both .md and .txt files saved to output/
- [ ] File names follow the YYYY-MM-DD_slug convention
