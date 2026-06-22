# Steam Watch — Daily Live Market Data Workflow

Maintains two Google Sheet tabs with live Steam market data, refreshed daily.

---

## What Each Tab Tracks

**Player Count Watch**
Top 100 games by peak concurrent players (24-hour peak). Reveals games with large organic followings that may have little press coverage. Each game shows genre and Indie/AAA classification. Indie games not yet in the Database that consistently exceed the 7-day indie average peak are flagged "→ Consider Adding."

**Cult Studio Watch**
Curated list of studios/developers with dedicated fan communities — from indie auteurs (Toby Fox, Lucas Pope, Team Cherry) to cult AAA-adjacent creators (Suda51, Kojima). Shows live Steam owner estimates for their tracked upcoming games.

---

## How to Run

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"

# Update both tabs:
python scripts/update_steam_watch.py

# Update a specific tab only:
python scripts/update_steam_watch.py --sheet players
python scripts/update_steam_watch.py --sheet studios

# Preview without writing (dry run):
python scripts/update_steam_watch.py --dry-run
```

---

## Daily Scheduling — Windows Task Scheduler

To run automatically every day at 09:00:

1. Open **Task Scheduler** (search in Start Menu)
2. Click **Create Basic Task...**
3. Name: `Steam Watch Daily Update`
4. Trigger: **Daily** → 09:00
5. Action: **Start a program**
   - Program: `C:\Users\IDG2601\Documents\Claude Agents\scripts\run_steam_watch.bat`
6. Finish

> If you previously had a "Steam Watch Weekly Update" task, delete it and create the new daily one.

Logs are saved to `output\steam_watch_log.txt` after each run.

Each run also appends a daily snapshot to `output\player_count_history.json` — used by the flag logic to determine 7-day consistency.

---

## Adding New Studios to Cult Studio Watch

Edit `resources/cult_studios.json`. Each entry has:

```json
{
  "studio": "Studio Name (Developer Name)",
  "known_for": "Game A, Game B",
  "category": "Indie Auteur | Indie Cult | Cult AAA-Adjacent | Cult Publisher",
  "tracked_games": [
    {
      "name": "Game Title",
      "appid": 123456,
      "status": "In Development | Announced | Launched"
    }
  ]
}
```

- `appid`: the Steam app ID (visible in the Steam store URL). Set to `null` if no Steam page exists yet.
- `tracked_games`: can be empty `[]` if the studio is being monitored but has no announced game yet.

After editing, run `python scripts/update_steam_watch.py --sheet studios` to refresh.

---

## Acting on "Consider Adding" Flags

When the Player Count Watch flags a game as "→ Consider Adding":

1. Open the game's Steam page to verify it's indie/relevant
2. Research the developer, conference history, and community signals
3. Follow `workflows/community-discovery-research.md` to create a proper DB entry
4. Run `python scripts/update_indie_db.py --data output/db_new_YYYY-MM-DD.json`
5. The flag will clear automatically on the next watch update

---

## Interpreting the Data

**Player Count Watch:**
- ▲ = rank improved vs previous day (trending up)
- ▼ = rank dropped vs previous day
- NEW = wasn't in top 100 yesterday
- `→ Consider Adding` = indie game, not in DB, above the 7-day indie average on 5+ of the last 7 days
- `(Monitoring — below avg)` = indie game, not in DB, but hasn't cleared the consistency threshold yet
- `(Monitoring — new)` = indie game seen for the first time today; check again tomorrow
- The indie average baseline is printed to the console on each run (also visible in dry-run output)

**Cult Studio Watch:**
- "No Steam page yet" = game is announced but no Steam listing — monitor the studio's social channels
- Steam Owners Est. comes from SteamSpy and is an approximation, not an exact figure

---

## Quality Checklist (after each run)

- [ ] Both tabs show today's date in the header row
- [ ] Player Count Watch has Genre and Indie/AAA columns populated for all games
- [ ] "In DB?" column shows ✓ YES for games known to be in the Database
- [ ] `output/player_count_history.json` updated with today's snapshot
- [ ] Cult Studio Watch shows updated owner estimates for tracked games (Silksong, Deltarune)
- [ ] Log file `output/steam_watch_log.txt` has no error lines
