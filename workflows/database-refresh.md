# Database Refresh Workflow

Run this after **ANY** update to the Database tab to keep all computed tabs current and the Summary analysis fresh. This workflow ensures genre research is re-run against the updated game pool — not just re-rendered from stale cached JSON.

---

## When to Run

- After syncing new games via `python scripts/update_indie_db.py --data <file.json>`
- After manually editing rows in the Database Google Sheet
- After running deduplication, normalization, or repair operations
- After any conference research batch is added (community, tier3, 2025conferences, etc.)

---

## Step 1 — Immediate Rebuild (fast, no research needed)

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"
python scripts/update_indie_db.py
```

This immediately:
- Sorts the database by year + game name
- Rebuilds the **Showcase Tracker** tab (conference appearance matrix)
- Rebuilds the **Mapping** tab (quadrant charts)
- Re-renders the **Summary** tab from existing JSON files (may be stale — updated in Steps 2–4)

---

## Step 2 — Re-run Historical Genres Research

Follow `workflows/historical-genres-research.md`:

- Re-filter the database for **launched games** and re-cluster by genre
- Check whether any newly added games shift genre cluster sizes, add new breakout genres, or change the DB performance evidence for existing ones
- Update `output/historical-genres-latest.json` if evidence changed
- Key trigger: **pre-2016 additions** (Cave Story, Braid, Machinarium, Papers Please, etc.) may introduce new genre clusters or strengthen existing ones

**Skip this step if:** The update only added games from 2025–2026 (no new historical launched games).

---

## Step 3 — Re-run Emerging Genres Research

Follow `workflows/emerging-genres-research.md`:

- Re-filter the database for **unreleased games showcased in 2025–2026**
- Check if any newly added games strengthen or weaken existing confidence ratings
- Re-check community signals and award evidence for any genre clusters that gained new members
- Update `output/emerging-genres-latest.json` if confidence levels or signal games changed

**Skip this step if:** The update only added pre-2015 historical games (no new unreleased 2025–2026 entries).

---

## Step 4 — Push Refreshed Research to Summary Tab

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"
python scripts/update_indie_db.py
```

This re-reads the updated JSON files from Steps 2–3 and writes the fully refreshed **Summary** tab.

---

## Decision Guide: Full vs. Lightweight Refresh

| Database update type | Step 1 | Steps 2–3 | Step 4 |
|---|---|---|---|
| Pre-2016 historical games only | ✓ Required | Step 2 only | ✓ Required |
| 2025–2026 unreleased games only | ✓ Required | Step 3 only | ✓ Required |
| Mix of historical + recent | ✓ Required | Both | ✓ Required |
| Fewer than 5 games, no genre relevance | ✓ Required | Quick validation pass | ✓ Required |
| Community/launched games, no new genres | ✓ Required | Quick validation pass | ✓ Required |

A **quick validation pass** = open the relevant JSON file, check if cluster sizes or confidence levels changed, update only if material differences exist.

---

## Quality Checklist (after full refresh)

- [ ] Summary tab "Last updated" date is today
- [ ] Showcase Tracker row count matches Database row count
- [ ] Historical genres JSON `research_date` updated if re-run
- [ ] Emerging genres JSON `research_date` updated if re-run
- [ ] No stale "not yet in DB" text in emerging genres section
- [ ] Mapping tab still shows 3 charts (roguelike skill barrier, cozy feature depth, roguelike first-timer)
