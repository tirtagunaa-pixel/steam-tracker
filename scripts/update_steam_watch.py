"""
Steam Watch — Weekly Live Market Data
--------------------------------------
Populates two Google Sheet tabs with live Steam data:

  Player Count Watch — Top games by concurrent players (Steam Charts API)
  Cult Studio Watch  — Tracked studios/developers with cult followings

Usage:
  python scripts/update_steam_watch.py              # update both tabs
  python scripts/update_steam_watch.py --sheet players
  python scripts/update_steam_watch.py --sheet studios
  python scripts/update_steam_watch.py --dry-run   # print without writing

Scheduled via Windows Task Scheduler — see workflows/steam-watch-update.md
"""

import sys
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import gspread
from google.oauth2.service_account import Credentials

# ── Config ────────────────────────────────────────────────────────────────────

SPREADSHEET_ID       = "1mfz9E63bc9Ea9rHf6O7CqVYgUw_zNMV6CWwi5jrX0Ac"
SERVICE_ACCOUNT_FILE = Path(__file__).parent / "service_account.json"
CULT_STUDIOS_FILE    = Path(__file__).parent.parent / "resources" / "cult_studios.json"
PLAYER_HISTORY_FILE  = Path(__file__).parent.parent / "output" / "player_count_history.json"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

PLAYERS_SHEET   = "Player Count Watch"
STUDIOS_SHEET   = "Cult Studio Watch"
DATABASE_SHEET  = "Database"

BATCH_SIZE  = 50
BATCH_PAUSE = 15

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IndieGameResearch/1.0)"}

# ── Auth & Sheet helpers ──────────────────────────────────────────────────────

def get_client():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return gspread.authorize(creds)


def get_or_create_worksheet(spreadsheet, name, rows=200, cols=15):
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(name, rows=rows, cols=cols)
        print(f"  Created worksheet '{name}'.")
        return ws


def write_sheet(ws, rows, dry_run=False):
    if dry_run:
        print(f"  [DRY RUN] Would write {len(rows)} rows.")
        for r in rows[:5]:
            print(f"    {r}")
        return
    ws.clear()
    for i in range(0, len(rows), BATCH_SIZE):
        chunk = rows[i:i + BATCH_SIZE]
        ws.append_rows(chunk, value_input_option="USER_ENTERED")
        if i + BATCH_SIZE < len(rows):
            time.sleep(2)


def load_db_names(spreadsheet):
    """Return a set of lowercased game names already in the main Database tab."""
    try:
        ws = spreadsheet.worksheet(DATABASE_SHEET)
        records = ws.get_all_records()
        return {str(r.get("Game Name", "")).strip().lower() for r in records if r.get("Game Name")}
    except Exception:
        return set()


def in_db(name, db_names):
    return "✓ YES" if name.strip().lower() in db_names else "NO"


# ── Steam API helpers ─────────────────────────────────────────────────────────

def steam_appdetails(appid):
    """Fetch name, developer, genres for a single appid."""
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        app_data = data.get(str(appid), {})
        if not app_data.get("success"):
            return {}
        d = app_data.get("data", {})
        return {
            "name":         d.get("name", ""),
            "developer":    ", ".join(d.get("developers", [])),
            "publisher":    ", ".join(d.get("publishers", [])),
            "genres":       ", ".join(g["description"] for g in d.get("genres", [])),
            "release_date": d.get("release_date", {}).get("date", ""),
            "is_free":      d.get("is_free", False),
        }
    except Exception:
        return {}


def steam_top_players(max_results=100):
    """
    Fetch top games by current concurrent players.
    Returns list of {rank, appid, last_week_rank, peak_in_game}
    """
    url = "https://api.steampowered.com/ISteamChartsService/GetMostPlayedGames/v1/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        ranks = data.get("response", {}).get("ranks", [])
        return ranks[:max_results]
    except Exception as e:
        print(f"  [Players] API error: {e}")
        return []


def steam_wishlist_count(appid):
    """Estimate wishlist count via SteamSpy owners field (proxy)."""
    url = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        d = resp.json()
        owners = d.get("owners", "")
        return owners if owners else "—"
    except Exception:
        return "—"


# ── Player history helpers ────────────────────────────────────────────────────

def load_player_history():
    """Load {appid: {name, is_indie, genre, snapshots: [{date, rank, peak}]}} from disk."""
    if PLAYER_HISTORY_FILE.exists():
        with open(PLAYER_HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_player_history(history):
    """Persist history, keeping max 7 snapshots per game; prune entries older than 7 days."""
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    pruned = {}
    for appid, data in history.items():
        recent = [s for s in data.get("snapshots", []) if s["date"] >= cutoff]
        if recent:
            pruned[appid] = {**data, "snapshots": recent[-7:]}
    with open(PLAYER_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(pruned, f, indent=2, ensure_ascii=False)


def is_indie_game(genres_str):
    return "indie" in genres_str.lower()


def determine_flag(appid_str, history, indie_avg, db_names, name):
    """Return flag string for a game based on indie status, DB presence, and 7-day history."""
    data = history.get(appid_str, {})
    if not data.get("is_indie"):
        return ""
    if in_db(name, db_names) == "✓ YES":
        return ""
    snapshots = data.get("snapshots", [])
    if not snapshots:
        return "(Monitoring — new)"
    above = sum(1 for s in snapshots if s["peak"] > indie_avg)
    threshold = min(5, len(snapshots))
    if above >= threshold:
        return "→ Consider Adding"
    return "(Monitoring — below avg)"


# ── Sheet 1: Player Count Watch ───────────────────────────────────────────────

def sync_player_watch(spreadsheet, dry_run=False):
    print("  Fetching Steam top concurrent player charts...")
    db_names = load_db_names(spreadsheet)
    ranks    = steam_top_players(max_results=100)
    history  = load_player_history()
    today    = datetime.now().strftime("%Y-%m-%d")

    # ── Step 1: enrich each game with genre/indie classification ──────────────
    print("  Enriching game details (genre + indie/AAA)...")
    for entry in ranks:
        appid = str(entry.get("appid", ""))
        rank  = entry.get("rank", 0)
        peak  = entry.get("peak_in_game", 0)

        hist_entry = history.setdefault(appid, {"snapshots": []})

        # Reuse cached classification if available; otherwise fetch
        if "genre" not in hist_entry or "is_indie" not in hist_entry or "release_date" not in hist_entry:
            details = steam_appdetails(appid) if appid else {}
            time.sleep(0.4)
            hist_entry["name"]         = details.get("name", f"AppID {appid}")
            hist_entry["genre"]        = details.get("genres", "—")
            hist_entry["is_indie"]     = is_indie_game(hist_entry["genre"])
            hist_entry["developer"]    = details.get("developer", "—")
            hist_entry["release_date"] = details.get("release_date", "—") or "—"
        else:
            if "name" not in hist_entry:
                hist_entry["name"] = f"AppID {appid}"
            if "developer" not in hist_entry:
                hist_entry["developer"] = "—"

        # Record today's snapshot (replace if already exists for today)
        hist_entry["snapshots"] = [s for s in hist_entry["snapshots"] if s["date"] != today]
        hist_entry["snapshots"].append({"date": today, "rank": rank, "peak": peak})

    # ── Step 2: compute indie average baseline ────────────────────────────────
    all_indie_peaks = [
        s["peak"]
        for data in history.values()
        if data.get("is_indie")
        for s in data.get("snapshots", [])
        if isinstance(s.get("peak"), int)
    ]
    indie_avg = int(sum(all_indie_peaks) / len(all_indie_peaks)) if all_indie_peaks else 0
    print(f"  Indie average peak (7-day): {indie_avg:,}")

    # ── Step 3: build sheet rows ──────────────────────────────────────────────
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = [
        [f"PLAYER COUNT WATCH — Steam Top Games by Concurrent Players  ·  Last updated: {now}",
         "", "", "", "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", "", "", "", ""],
        ["Rank", "vs Last Week", "Game Name", "Developer", "Genre", "Indie/AAA",
         "Release Date", "Peak Players (24h)", "In DB?", "Steam Link", "Flag"],
    ]

    for entry in ranks:
        appid_int  = entry.get("appid", "")
        appid      = str(appid_int)
        rank       = entry.get("rank", "")
        last_rank  = entry.get("last_week_rank", 0)
        peak       = entry.get("peak_in_game", 0)

        if last_rank and rank:
            if rank < last_rank:
                movement = f"▲ {last_rank - rank}"
            elif rank > last_rank:
                movement = f"▼ {rank - last_rank}"
            else:
                movement = "—"
        else:
            movement = "NEW"

        hist_entry   = history.get(appid, {})
        name         = hist_entry.get("name", f"AppID {appid}")
        developer    = hist_entry.get("developer", "—")
        genre        = hist_entry.get("genre", "—")
        indie_label  = "Indie" if hist_entry.get("is_indie") else "AAA / Other"
        release_date = hist_entry.get("release_date", "—")
        steam_link   = f"https://store.steampowered.com/app/{appid_int}/" if appid_int else "—"
        in_database  = in_db(name, db_names)
        flag         = determine_flag(appid, history, indie_avg, db_names, name)
        peak_fmt     = f"{peak:,}" if isinstance(peak, int) else peak

        rows.append([rank, movement, name, developer, genre, indie_label,
                     release_date, peak_fmt, in_database, steam_link, flag])

    # ── Step 4: persist history and write sheet ───────────────────────────────
    if not dry_run:
        save_player_history(history)
        print(f"  History saved → {PLAYER_HISTORY_FILE.name}")

    ws = get_or_create_worksheet(spreadsheet, PLAYERS_SHEET, rows=150, cols=11)
    write_sheet(ws, rows, dry_run)
    indie_count = sum(1 for d in history.values() if d.get("is_indie"))
    print(f"  Player Count Watch written ({len(ranks)} games, {indie_count} indie).{' [DRY RUN]' if dry_run else ''}")


# ── Sheet 2: Cult Studio Watch ────────────────────────────────────────────────

def sync_studio_watch(spreadsheet, dry_run=False):
    print("  Building Cult Studio Watch...")

    if not CULT_STUDIOS_FILE.exists():
        print(f"  ERROR: {CULT_STUDIOS_FILE} not found.")
        return

    with open(CULT_STUDIOS_FILE, encoding="utf-8") as f:
        studios = json.load(f)

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    rows = [
        [f"CULT STUDIO WATCH — Studios & Developers with Dedicated Fan Communities  ·  Last updated: {now}",
         "", "", "", "", "", "", ""],
        ["", "", "", "", "", "", "", ""],
        ["Studio / Developer", "Category", "Known For", "Tracked Game", "Status",
         "Steam Owners Est.", "Steam Link", "Last Updated"],
    ]

    for studio in studios:
        name     = studio.get("studio", "")
        category = studio.get("category", "")
        known    = studio.get("known_for", "")
        games    = studio.get("tracked_games", [])

        if not games:
            # Studio with no tracked games — show as monitoring only
            rows.append([name, category, known, "— (no upcoming game tracked)", "", "", "", now])
            continue

        for game in games:
            game_name = game.get("name", "")
            appid     = game.get("appid")
            status    = game.get("status", "")

            if appid:
                owners     = steam_wishlist_count(appid)
                steam_link = f"https://store.steampowered.com/app/{appid}/"
                time.sleep(0.5)
            else:
                owners     = "No Steam page yet"
                steam_link = "—"

            rows.append([name, category, known, game_name, status, owners, steam_link, now])

    # Add a separator + legend section
    rows.append(["", "", "", "", "", "", "", ""])
    rows.append(["LEGEND", "", "", "", "", "", "", ""])
    rows.append(["Indie Auteur", "Solo or small-team developer whose creative identity IS the brand", "", "", "", "", "", ""])
    rows.append(["Indie Cult", "Studio with a fiercely dedicated niche audience", "", "", "", "", "", ""])
    rows.append(["Cult AAA-Adjacent", "Large-budget studio with cult-level director/auteur following", "", "", "", "", "", ""])
    rows.append(["Cult Publisher", "Publisher known for distinctive taste that fans follow", "", "", "", "", "", ""])

    ws = get_or_create_worksheet(spreadsheet, STUDIOS_SHEET, rows=150, cols=8)
    write_sheet(ws, rows, dry_run)
    print(f"  Cult Studio Watch written ({len(studios)} studios).{' [DRY RUN]' if dry_run else ''}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Steam Watch — Weekly Live Market Data")
    parser.add_argument("--sheet", choices=["players", "studios", "all"],
                        default="all", help="Which sheet to update (default: all)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print planned output without writing to Google Sheets")
    args = parser.parse_args()

    print("Connecting to Google Sheets...")
    client      = gspread.authorize(Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES))
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    print(f"Connected to: {spreadsheet.title}\n")

    if args.sheet in ("players", "all"):
        print("── Player Count Watch ──────────────────────────────────────")
        sync_player_watch(spreadsheet, dry_run=args.dry_run)

    if args.sheet in ("studios", "all"):
        print("\n── Cult Studio Watch ──────────────────────────────────────")
        sync_studio_watch(spreadsheet, dry_run=args.dry_run)

    print("\nDone.")


if __name__ == "__main__":
    main()
