"""
Steam Wishlist Tracker — Daily capture + Weekly AI report
----------------------------------------------------------
Modes:
  --mode daily   Fetch today's Top 500 wishlist chart and append to 'Wishlist History' sheet.
                 Flags significant movers (new entries or 20+ rank jump) and sends a Seatalk alert.
                 Run every day at 08:00 via Task Scheduler.

  --mode weekly  Analyse the previous Mon–Sun from 'Wishlist History', generate an AI
                 trend summary via Compass Claude API, write to 'Weekly Wishlist Summary',
                 and POST the formatted report to Seatalk via Pawon webhook.
                 Run every Monday at 09:00 via Task Scheduler.

  --dry-run      Print output without writing to Google Sheets or sending to Seatalk.

Config: scripts/watch_config.json
"""

import sys
import re
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import gspread
from google.oauth2.service_account import Credentials

# ── Paths & constants ─────────────────────────────────────────────────────────

BASE_DIR             = Path(__file__).parent.parent
CONFIG_FILE          = Path(__file__).parent / "watch_config.json"
SERVICE_ACCOUNT_FILE = Path(__file__).parent / "service_account.json"
LOG_FILE             = BASE_DIR / "output" / "wishlist_tracker_log.txt"

SPREADSHEET_ID = "1mfz9E63bc9Ea9rHf6O7CqVYgUw_zNMV6CWwi5jrX0Ac"

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HISTORY_SHEET  = "Wishlist History"
SUMMARY_SHEET  = "Weekly Wishlist Summary"
SNAPSHOT_SHEET = "Wishlist"  # live current-state view, overwritten daily

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IndieGameResearch/1.0)"}

TOP_N = 500  # fetched via 10 paginated requests (start=0,50,...,450, count=50 each)

VELOCITY_SHEET         = "Wishlist Velocity Tracker"
HIGH_VELOCITY_THRESHOLD = 15  # rank positions climbed in 7 days to trigger alert/section

AAA_PUBLISHERS = {
    "ubisoft", "electronic arts", "ea games", "capcom", "activision", "blizzard",
    "take-two", "rockstar games", "2k games", "square enix", "sega",
    "bandai namco", "konami", "bethesda", "xbox game studios", "microsoft",
    "playstation studios", "sony interactive", "warner bros", "cd projekt",
    "riot games", "epic games", "valve", "505 games", "deep silver",
    "thq nordic", "focus entertainment", "nacon", "4a games",
}

TIER_EMOJI = {"Indie": "🎮", "Triple A": "🏢", "AA": "🔷", "Early Access": "🧪"}

# Steam hardware/products that appear on the wishlist chart but are not games
EXCLUDED_NAMES = {
    "Steam Frame",
    "Steam Machine",
}

def classify_game(genre, publisher, developer):
    """Return 'Triple A', 'Indie', 'Early Access', or 'AA' (mid-tier)."""
    genre_l = (genre or "").lower()
    pub_l   = (publisher or "").lower()
    dev_l   = (developer or "").lower()
    if "early access" in genre_l:
        return "Early Access"
    for aaa in AAA_PUBLISHERS:
        if aaa in pub_l or aaa in dev_l:
            return "Triple A"
    if "indie" in genre_l:
        return "Indie"
    return "AA"

# ── Config loader ─────────────────────────────────────────────────────────────

def load_config():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

# ── Google Sheets helpers ─────────────────────────────────────────────────────

def get_spreadsheet():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    return client.open_by_key(SPREADSHEET_ID)


def get_or_create_worksheet(spreadsheet, name, rows=2000, cols=12):
    try:
        return spreadsheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = spreadsheet.add_worksheet(name, rows=rows, cols=cols)
        print(f"  Created worksheet '{name}'.")
        return ws

# ── Steam API helpers (reused from update_steam_watch.py) ────────────────────

def steam_search_wishlist(max_results=100):
    """Fetch up to max_results games via paginated calls (50 per page)."""
    url = "https://store.steampowered.com/search/results/"
    all_items = []
    batch = 50
    for start in range(0, max_results, batch):
        count = min(batch, max_results - start)
        params = {"filter": "popularwishlist", "json": 1, "count": count, "start": start}
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            for item in items:
                logo = item.get("logo", "")
                m = re.search(r"/apps/(\d+)/", logo)
                item["appid"] = m.group(1) if m else ""
            all_items.extend(items)
            if len(items) < count:
                break  # API returned fewer than requested — no more results
            time.sleep(0.3)  # polite pause between pages
        except Exception as e:
            print(f"  [Wishlist] API error at start={start}: {e}")
            break
    return all_items[:max_results]


def steam_appdetails(appid):
    url = f"https://store.steampowered.com/api/appdetails?appids={appid}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        app_data = data.get(str(appid), {})
        if not app_data.get("success"):
            return {}
        d = app_data.get("data", {})
        return {
            "developer":    ", ".join(d.get("developers", [])),
            "publisher":    ", ".join(d.get("publishers", [])),
            "genres":       ", ".join(g["description"] for g in d.get("genres", [])),
            "release_date": d.get("release_date", {}).get("date", ""),
        }
    except Exception:
        return {}


def steamspy_data(appid):
    """Return wishlist estimate and owners range from SteamSpy."""
    url = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        d = resp.json()
        return {
            "wishlists": d.get("wishlists", 0) or 0,
            "owners":    d.get("owners", "—") or "—",
        }
    except Exception:
        return {"wishlists": 0, "owners": "—"}


def compute_genre_distribution(rows):
    """Count genre occurrences across all rows; return top 5 as [(genre, count)]."""
    from collections import Counter
    counter = Counter()
    try:
        for row in rows:
            genre_str = row.get("Genre", "") or ""
            if genre_str and genre_str != "—":
                for g in genre_str.split(","):
                    g = g.strip()
                    if g:
                        counter[g] += 1
    except Exception:
        pass
    return counter.most_common(5)


def fetch_game_news(appid, game_name, count=3):
    """Fetch recent news articles for a game from Steam News API."""
    if not appid:
        return []
    url = (
        f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
        f"?appid={appid}&count={count}&maxlength=500&format=json"
    )
    try:
        time.sleep(0.3)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("appnews", {}).get("newsitems", [])
        clean = []
        for item in items:
            item["contents"] = re.sub(r"<[^>]+>", "", item.get("contents", "")).strip()
            clean.append(item)
        return clean
    except Exception as e:
        print(f"  [News] {game_name}: {e}")
        return []

# ── Mode: DAILY ───────────────────────────────────────────────────────────────

def run_daily(spreadsheet, dry_run=False):
    today = datetime.now().strftime("%Y-%m-%d")
    config = load_config()

    ws = get_or_create_worksheet(spreadsheet, HISTORY_SHEET, rows=50000, cols=12)
    ws.resize(rows=50000, cols=12)

    # Read existing sheet data: used for duplicate guard + prior rank/velocity comparison
    existing = ws.get_all_values()
    if not dry_run:
        if any(row and row[0] == today for row in existing[1:]):
            print(f"  Already captured data for {today}. Skipping duplicate run.")
            return

    # Build dict of yesterday's ranks {game_name: rank} from the most recent prior date
    prior_ranks = {}
    if len(existing) > 1:
        dates_seen = [row[0] for row in existing[1:] if row and row[0] and row[0] != today]
        if dates_seen:
            latest_prior = max(dates_seen)
            for row in existing[1:]:
                if row and len(row) >= 3 and row[0] == latest_prior:
                    try:
                        prior_ranks[row[2]] = int(row[1])
                    except (ValueError, IndexError):
                        pass

    # Build 7-day-ago ranks for rank-based velocity calculation
    prior_ranks_7d = {}
    if len(existing) > 1:
        target_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        dates_available = sorted(set(r[0] for r in existing[1:] if r and r[0] and r[0] != today))
        best_date = None
        for d in dates_available:
            try:
                diff = abs((datetime.strptime(d, "%Y-%m-%d") - datetime.strptime(target_date, "%Y-%m-%d")).days)
                if diff <= 2:
                    if best_date is None:
                        best_date = d
                    else:
                        cur_diff = abs((datetime.strptime(best_date, "%Y-%m-%d") - datetime.strptime(target_date, "%Y-%m-%d")).days)
                        if diff < cur_diff:
                            best_date = d
            except ValueError:
                pass
        if best_date:
            for row in existing[1:]:
                if row and row[0] == best_date and len(row) >= 3:
                    try:
                        prior_ranks_7d[row[2]] = int(row[1])
                    except (ValueError, IndexError):
                        pass
            print(f"  Velocity baseline: using {best_date} ({len(prior_ranks_7d)} games)")
        else:
            print("  Velocity baseline: no data from ~7 days ago yet — velocity will show 0")

    print(f"  Fetching Top {TOP_N} wishlist chart for {today}...")

    items = steam_search_wishlist(max_results=TOP_N)
    if not items:
        print("  ERROR: No data returned from Steam. Aborting.")
        return
    items = [i for i in items if i.get("name", "") not in EXCLUDED_NAMES]

    new_entries   = []   # (name, rank, tier, developer, publisher, genre, velocity_7d)
    big_climbers  = []   # (name, old_rank, new_rank, delta, tier, developer, publisher, genre, velocity_7d)
    high_velocity = []   # (name, rank, tier, developer, publisher, genre, velocity_7d)
    all_deltas    = []   # (name, old_rank, new_rank, delta, tier, developer, publisher, genre)
    rows = []

    for rank, item in enumerate(items, start=1):
        appid = item.get("appid", "")
        name  = item.get("name", "Unknown")

        details = {}
        if appid:
            details = steam_appdetails(appid)
            time.sleep(0.4)

        spy = {"wishlists": 0, "owners": "—"}
        if appid and rank <= 100:  # SteamSpy returns 0 for unreleased games above rank 100
            spy = steamspy_data(appid)
            time.sleep(0.5)

        tier = classify_game(
            details.get("genres", "—"),
            details.get("publisher", "—"),
            details.get("developer", "—"),
        )

        developer        = details.get("developer", "—")
        publisher        = details.get("publisher", "—")
        genre            = details.get("genres", "—")
        current_wishlists = spy["wishlists"]
        # Rank-based velocity: positions climbed vs 7 days ago (positive = improved)
        # Only computed for games that were actually tracked in the 7-day baseline
        if prior_ranks_7d and name in prior_ranks_7d:
            velocity_7d = prior_ranks_7d[name] - rank
        else:
            velocity_7d = 0

        if name not in prior_ranks:
            rank_change = "NEW"
            new_entries.append((name, rank, tier, developer, publisher, genre, velocity_7d))
        else:
            delta = prior_ranks[name] - rank  # positive = climbed
            rank_change = f"+{delta}" if delta > 0 else str(delta)
            if delta >= 10:
                big_climbers.append((name, prior_ranks[name], rank, delta, tier, developer, publisher, genre, velocity_7d))
            all_deltas.append((name, prior_ranks[name], rank, delta, tier, developer, publisher, genre))

        if velocity_7d >= HIGH_VELOCITY_THRESHOLD:
            high_velocity.append((name, rank, tier, developer, publisher, genre, velocity_7d))

        rows.append([
            today, rank, name, str(appid),
            developer, publisher, genre,
            details.get("release_date", item.get("release_date", "—")),
            current_wishlists,
            spy["owners"],
            rank_change,
            velocity_7d,
        ])
        vel_str = f" 🔥+{velocity_7d:,}/7d" if velocity_7d >= HIGH_VELOCITY_THRESHOLD else ""
        print(f"    #{rank:02d} [{tier[:3]}] {name}  [{rank_change}]{vel_str}")

    if dry_run:
        print(f"\n  [DRY RUN] Would append {len(rows)} rows to '{HISTORY_SHEET}'.")
        for r in rows[:3]:
            print(f"    {r}")
        today_names_dry = {row[2] for row in rows}
        exits_dry = sorted([n for n in prior_ranks if n not in today_names_dry], key=lambda n: prior_ranks[n])
        top_cl_dry = sorted([d for d in all_deltas if d[3] > 0], key=lambda x: x[3], reverse=True)[:10]
        top_fa_dry = sorted([d for d in all_deltas if d[3] < 0], key=lambda x: x[3])[:10]
        digest_dry = _build_daily_digest(today, top_cl_dry, top_fa_dry, new_entries, exits_dry, prior_exists=bool(prior_ranks))
        print(f"\n  [DRY RUN] Daily digest (would send to personal DM):\n")
        print(digest_dry)
        return

    # Ensure headers exist / are up to date
    if not existing:
        ws.append_row(
            ["Date", "Rank", "Game Name", "AppID", "Developer", "Publisher",
             "Genre", "Release Date", "Wishlist Est.", "Owners Est.", "Rank Change", "7d Rank Δ"],
            value_input_option="USER_ENTERED",
        )
    else:
        if len(existing[0]) < 11 or existing[0][10] != "Rank Change":
            ws.update_cell(1, 11, "Rank Change")
        if len(existing[0]) < 12:
            ws.update_cell(1, 12, "7d Rank Δ")

    ws.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"  Appended {len(rows)} rows to '{HISTORY_SHEET}'.")

    # Overwrite live snapshot tab with current Top 500 + Tier + Velocity columns
    ws_snap = get_or_create_worksheet(spreadsheet, SNAPSHOT_SHEET, rows=505, cols=13)
    ws_snap.resize(rows=505, cols=13)
    snap_rows = [[
        row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10],
        classify_game(row[6], row[5], row[4]),
        row[11],  # velocity_7d
        today,
    ] for row in rows]
    ws_snap.clear()
    ws_snap.append_row(
        ["Rank", "Game Name", "AppID", "Developer", "Publisher", "Genre",
         "Release Date", "Wishlist Est.", "Owners Est.", "Rank Change", "Tier",
         "7d Rank Δ", "Date Updated"],
        value_input_option="USER_ENTERED",
    )
    ws_snap.append_rows(snap_rows, value_input_option="USER_ENTERED")
    print(f"  Updated '{SNAPSHOT_SHEET}' snapshot tab ({len(snap_rows)} rows).")

    # Overwrite Velocity Tracker sheet: games with positive 7d rank improvement, sorted descending
    vel_tracker_rows = sorted(
        [
            [row[1], row[2], row[3], row[4], row[5], row[6],
             classify_game(row[6], row[5], row[4]), row[8], row[11]]
            for row in rows
            if isinstance(row[11], (int, float)) and row[11] > 0
        ],
        key=lambda r: r[8],  # r[8] = velocity_7d (rank positions climbed)
        reverse=True,
    )
    ws_vel = get_or_create_worksheet(spreadsheet, VELOCITY_SHEET, rows=505, cols=9)
    ws_vel.resize(rows=505, cols=9)
    ws_vel.clear()
    ws_vel.append_row(
        ["Rank", "Game Name", "AppID", "Developer", "Publisher", "Genre",
         "Tier", "Wishlist Est.", "7d Velocity"],
        value_input_option="USER_ENTERED",
    )
    if vel_tracker_rows:
        ws_vel.append_rows(vel_tracker_rows, value_input_option="USER_ENTERED")
    print(f"  Updated '{VELOCITY_SHEET}' tab ({len(vel_tracker_rows)} games with velocity data).")

    # Daily digest — always sent to personal DM
    today_names = {row[2] for row in rows}
    exits = sorted([n for n in prior_ranks if n not in today_names], key=lambda n: prior_ranks[n])
    top_climbers_digest = sorted([d for d in all_deltas if d[3] > 0], key=lambda x: x[3], reverse=True)[:10]
    top_fallers_digest  = sorted([d for d in all_deltas if d[3] < 0], key=lambda x: x[3])[:10]
    digest = _build_daily_digest(today, top_climbers_digest, top_fallers_digest, new_entries, exits, prior_exists=bool(prior_ranks))
    send_to_seatalk(config, digest, personal=True)
    send_to_seatalk(config, digest, personal=False)

# ── Mode: WEEKLY ──────────────────────────────────────────────────────────────

def get_week_range():
    """Return (week_start, week_end) for the most recently completed Mon–Sun week."""
    today = datetime.now().date()
    # Most recent Sunday
    days_since_sunday = today.weekday() + 1  # Monday=0 → +1
    if days_since_sunday == 7:
        days_since_sunday = 0
    week_end   = today - timedelta(days=days_since_sunday)
    week_start = week_end - timedelta(days=6)
    return week_start, week_end


def load_history_for_week(ws, week_start, week_end):
    """Return list of rows (as dicts) for the given week from Wishlist History."""
    all_rows = ws.get_all_records()
    result = []
    for row in all_rows:
        try:
            d = datetime.strptime(str(row.get("Date", "")), "%Y-%m-%d").date()
        except ValueError:
            continue
        if week_start <= d <= week_end:
            result.append(row)
    return result


def load_prior_week_history(ws, week_start):
    """Return rows for the 7 days before week_start (prior week), for comparison."""
    prior_end   = week_start - timedelta(days=1)
    prior_start = prior_end - timedelta(days=6)
    return load_history_for_week(ws, prior_start, prior_end)


def analyse_week(rows, prior_rows):
    """
    Given daily rows for a week, return a structured analysis dict:
      top5_stable: games in Top 5 on >= 5 of 7 days
      top10_stable: games in Top 10 on >= 5 of 7 days
      new_entrants: games not seen in prior week at all
      exits: games in prior week Top 15 but absent this week
      end_of_week_owners: {name: owners_string} from the latest date rows
      rank_by_name: {name: [rank per day list]}
      days_in_chart: {name: count_of_days}
      final_ranks: {name: rank on last day seen this week}
      prior_names: set of game names from prior week
    """
    from collections import defaultdict

    rank_by_name    = defaultdict(list)
    owners_by_name  = {}
    latest_date     = None

    for row in rows:
        name  = row.get("Game Name", "")
        rank  = row.get("Rank")
        date  = row.get("Date", "")
        owners = row.get("SteamSpy Owners Est.", "—")
        if not name or rank is None or name in EXCLUDED_NAMES:
            continue
        rank_by_name[name].append(int(rank))
        if date and (latest_date is None or date > latest_date):
            latest_date = date

    # Collect end-of-week owners from the latest date
    for row in rows:
        if row.get("Date") == latest_date:
            name = row.get("Game Name", "")
            if name:
                owners_by_name[name] = row.get("Owners Est.", "—")

    days_in_chart = {name: len(ranks) for name, ranks in rank_by_name.items()}
    final_ranks   = {name: ranks[-1] for name, ranks in rank_by_name.items()}

    top5_stable  = sorted(
        [n for n, ranks in rank_by_name.items() if sum(1 for r in ranks if r <= 5) >= 5],
        key=lambda n: sum(r for r in rank_by_name[n] if r <= 5) / max(1, sum(1 for r in rank_by_name[n] if r <= 5))
    )
    top10_stable = sorted(
        [n for n, ranks in rank_by_name.items() if sum(1 for r in ranks if r <= 10) >= 5],
        key=lambda n: sum(r for r in rank_by_name[n] if r <= 10) / max(1, sum(1 for r in rank_by_name[n] if r <= 10))
    )

    prior_names = {row.get("Game Name", "") for row in prior_rows if row.get("Game Name")}
    this_names  = set(rank_by_name.keys())

    new_entrants = sorted([n for n in this_names if n not in prior_names],
                          key=lambda n: final_ranks.get(n, 999))
    exits        = [n for n in prior_names if n not in this_names]

    genre_distribution = compute_genre_distribution(rows)

    appid_by_name     = {}
    genre_by_name     = {}
    publisher_by_name = {}
    for row in rows:
        name  = row.get("Game Name", "")
        appid = str(row.get("AppID", "")).strip()
        if name and appid and name not in appid_by_name:
            appid_by_name[name] = appid
        if name and name not in genre_by_name:
            genre_by_name[name]     = row.get("Genre", "—") or "—"
            publisher_by_name[name] = row.get("Publisher", "—") or "—"

    # Rank movers: compare first day rank vs last day rank within the week
    first_ranks = {}
    earliest_date = None
    for row in rows:
        date = row.get("Date", "")
        if date and (earliest_date is None or date < earliest_date):
            earliest_date = date
    for row in rows:
        if row.get("Date") == earliest_date:
            name = row.get("Game Name", "")
            try:
                first_ranks[name] = int(row.get("Rank", 0))
            except (ValueError, TypeError):
                pass

    # weekly_rank_delta: positive = improved (climbed), negative = fell
    weekly_rank_delta = {}
    for name in rank_by_name:
        if name in first_ranks and name in final_ranks:
            weekly_rank_delta[name] = first_ranks[name] - final_ranks[name]

    # Top climbers and fallers this week (min 3 days in chart)
    movers = [(name, delta) for name, delta in weekly_rank_delta.items()
              if days_in_chart.get(name, 0) >= 3]
    top_climbers = sorted(movers, key=lambda x: x[1], reverse=True)[:10]
    top_fallers  = sorted(movers, key=lambda x: x[1])[:5]

    # Tier classification per game
    tier_by_name = {}
    developer_by_name = {}
    for row in rows:
        name = row.get("Game Name", "")
        if name and name not in tier_by_name:
            genre     = row.get("Genre", "—") or "—"
            publisher = row.get("Publisher", "—") or "—"
            developer = row.get("Developer", "—") or "—"
            tier_by_name[name]      = classify_game(genre, publisher, developer)
            developer_by_name[name] = developer

    return {
        "top5_stable":        top5_stable,
        "top10_stable":       top10_stable,
        "new_entrants":       new_entrants,
        "exits":              exits,
        "end_of_week_owners": owners_by_name,
        "rank_by_name":       dict(rank_by_name),
        "days_in_chart":      days_in_chart,
        "final_ranks":        final_ranks,
        "prior_names":        prior_names,
        "latest_date":        latest_date,
        "genre_distribution": genre_distribution,
        "appid_by_name":      appid_by_name,
        "genre_by_name":      genre_by_name,
        "publisher_by_name":  publisher_by_name,
        "developer_by_name":  developer_by_name,
        "tier_by_name":       tier_by_name,
        "weekly_rank_delta":  weekly_rank_delta,
        "top_climbers":       top_climbers,
        "top_fallers":        top_fallers,
    }


def load_prior_weekly_summaries(ws):
    """Return all prior weekly summaries as a list of dicts."""
    try:
        return ws.get_all_records()
    except Exception:
        return []


def call_compass_api(config, prompt):
    """Call Compass Claude API and return the response text."""
    headers = {
        "Authorization": f"Bearer {config['compass']['api_key']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model":      config["compass"]["model"],
        "max_tokens": config["compass"]["max_tokens"],
        "messages": [
            {"role": "user", "content": prompt}
        ],
    }
    try:
        resp = requests.post(
            config["compass"]["base_url"],
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        # Standard Anthropic messages API response format
        return data["content"][0]["text"].strip()
    except Exception as e:
        print(f"  [Compass API] Error: {e}")
        return "Trend analysis unavailable this week."


def build_ai_prompt(week_start, week_end, analysis, prior_summaries, game_news=None):
    """Build the prompt for the Compass Claude API."""
    week_label = f"{week_start.strftime('%b %d')}–{week_end.strftime('%b %d, %Y')}"

    tier_by_name = analysis.get("tier_by_name", {})

    def tier_tag(name):
        t = tier_by_name.get(name, "AA")
        return "🎮 Indie" if t == "Indie" else ("🧪 EA" if t == "Early Access" else t)

    top5_lines = []
    for name in analysis["top5_stable"][:5]:
        days     = analysis["days_in_chart"].get(name, 0)
        ranks    = analysis["rank_by_name"].get(name, [])
        avg_rank = f"{sum(ranks)/len(ranks):.1f}" if ranks else "?"
        delta    = analysis.get("weekly_rank_delta", {}).get(name, 0)
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        top5_lines.append(
            f"  - {name} [{tier_tag(name)}]: {days}/7 days in Top 5, avg rank {avg_rank}, week Δ {delta_str}"
        )

    top10_others = [n for n in analysis["top10_stable"] if n not in analysis["top5_stable"]]
    top10_lines  = [f"  - {n} [{tier_tag(n)}]" for n in top10_others[:5]]

    # Rank movers block
    climber_lines = []
    for name, delta in analysis.get("top_climbers", []):
        if delta > 0:
            climber_lines.append(f"  - {name} [{tier_tag(name)}]: +{delta} positions")
    faller_lines = []
    for name, delta in analysis.get("top_fallers", []):
        if delta < 0:
            faller_lines.append(f"  - {name} [{tier_tag(name)}]: {delta} positions")

    new_lines  = [f"  - {n} [{tier_tag(n)}]" for n in analysis["new_entrants"][:8]]
    exit_lines = [f"  - {n}" for n in analysis["exits"][:5]]

    # Genre distribution block
    genre_dist = analysis.get("genre_distribution", [])
    if genre_dist:
        genre_lines = "\n".join(
            f"  {i+1}. {genre} ({count} chart appearances)"
            for i, (genre, count) in enumerate(genre_dist)
        )
        genre_block = f"Top 5 genres this week (all ranked games × days):\n{genre_lines}\n"
    else:
        genre_block = ""

    # Per-game news context — focus on top climbers + top 5 stable
    news_targets = [n for n, _ in analysis.get("top_climbers", [])[:5]] + \
                   [n for n in analysis["top5_stable"][:3] if n not in [x for x, _ in analysis.get("top_climbers", [])[:5]]]
    news_block = ""
    if game_news:
        sections = []
        for name in news_targets[:8]:
            items = game_news.get(name, [])
            if not items:
                continue
            snippets = [
                f'    • [{it.get("feedname", "")}] "{it.get("title", "")}" ({it.get("url", "")}) — {it.get("contents", "")[:300]}'
                for it in items
            ]
            sections.append(f"  [{name}]:\n" + "\n".join(snippets))
        if sections:
            news_block = "Recent news for top movers + stable top 5 (Steam News API):\n" + "\n".join(sections) + "\n"

    prior_context = ""
    if prior_summaries:
        last_n = prior_summaries[-6:]  # up to 6 prior weeks for context
        prior_context = "Prior weekly summaries (oldest to newest):\n"
        for s in last_n[:-1]:  # older weeks: structural only
            prior_context += (
                f"  Week {s.get('Week #', '?')} ({s.get('Week Start', '')}–{s.get('Week End', '')}): "
                f"Top 5 stable: {s.get('Top 5 Stable', '—')} | "
                f"New entrants: {s.get('New Entrants', '—')} | "
                f"Exits: {s.get('Exits', '—')}\n"
            )
        if last_n:  # most recent prior week: include full AI commentary
            last = last_n[-1]
            prior_context += (
                f"\nLast week — Week {last.get('Week #', '?')} "
                f"({last.get('Week Start', '')}–{last.get('Week End', '')}):\n"
                f"  Top 5 stable: {last.get('Top 5 Stable', '—')}\n"
                f"  New entrants: {last.get('New Entrants', '—')} | "
                f"Exits: {last.get('Exits', '—')}\n"
                f"  Last week's trend analysis:\n    {last.get('AI Commentary', '(none)')}\n"
            )
        prior_context += "\n"

    prompt = f"""You are a game market analyst writing a weekly Steam Wishlist chart briefing for an indie game research team.

Write 5–8 bullet points covering these areas in order:
1. vs last week: how rank movements compare — what's new, what reversed, is indie momentum building or cooling?
2. Notable rank climbers — WHY did they rise? Draw from news snippets. Label 🎮 Indie / 🧪 Early Access games explicitly.
3. Notable rank fallers — any pattern or cause?
4. New entrants and exits — what do they signal about player interest?
5. Biggest indie/EA signal of the week — any indie punching above its weight or a genre trend emerging?

Rules:
- Every insight that draws on news MUST cite the source as [Source Name](url)
- Max 20 words per bullet (not counting URLs)
- Use • as bullet character
- First bullet MUST start with "vs last week:"

**This week's data ({week_label}):**

Top rank climbers (Mon→Sun improvement):
{chr(10).join(climber_lines) if climber_lines else "  (chart stable — insufficient movement data)"}

Top rank fallers:
{chr(10).join(faller_lines) if faller_lines else "  none"}

New entrants to Top 500:
{chr(10).join(new_lines) if new_lines else "  none (or prior-week data insufficient for comparison)"}

Games that dropped out of Top 500:
{chr(10).join(exit_lines) if exit_lines else "  none"}

{genre_block}
{news_block}
{prior_context}"""

    return prompt


def format_seatalk_message(week_start, week_end, week_num, analysis, ai_commentary):
    """Build the Markdown message for Seatalk (format=1)."""
    week_label  = f"{week_start.strftime('%b %d')}–{week_end.strftime('%b %d, %Y')}"
    tier_by     = analysis.get("tier_by_name", {})
    final_ranks = analysis.get("final_ranks", {})

    def fmt_tier(name):
        t = tier_by.get(name, "AA")
        return TIER_EMOJI.get(t, "🔷")

    lines = [f"📊 **Steam Wishlist Chart — Week {week_num} ({week_label})**", ""]

    # (1) Biggest rank movers
    lines.append("**📈 Biggest Rank Movers This Week**")
    climbers = [(n, d) for n, d in analysis.get("top_climbers", []) if d > 0]
    fallers  = [(n, d) for n, d in analysis.get("top_fallers", []) if d < 0]
    if climbers:
        lines.append("↑ *Climbers:*")
        for name, delta in climbers[:8]:
            rank = final_ranks.get(name, "?")
            lines.append(f"  {fmt_tier(name)} **{name}** (now #{rank}, +{delta})")
    if fallers:
        lines.append("↓ *Fallers:*")
        for name, delta in fallers[:5]:
            rank = final_ranks.get(name, "?")
            lines.append(f"  {fmt_tier(name)} **{name}** (now #{rank}, {delta})")
    if not climbers and not fallers:
        lines.append("  _(chart was stable this week)_")

    # (2) New this week
    lines.append("")
    lines.append("**🆕 New This Week**")
    if analysis["new_entrants"]:
        for name in analysis["new_entrants"][:10]:
            rank = final_ranks.get(name, "?")
            lines.append(f"  {fmt_tier(name)} **{name}** (#{rank})")
    else:
        lines.append("  _(no new entries — or insufficient prior-week data for comparison)_")

    # (3) Dropped out
    lines.append("")
    lines.append("**📉 Dropped Out**")
    if analysis["exits"]:
        for name in analysis["exits"][:8]:
            lines.append(f"  • {name}")
    else:
        lines.append("  _(none)_")

    # (4) Top genres
    lines.append("")
    lines.append("**🎲 Top Genres**")
    genre_dist = analysis.get("genre_distribution", [])
    if genre_dist:
        for i, (genre, count) in enumerate(genre_dist[:8], start=1):
            lines.append(f"  {i}. {genre} ({count} appearances)")
    else:
        lines.append("  _(no genre data)_")

    # (5) AI analysis
    lines += ["", "**🤖 Analysis**", ai_commentary]

    return "\n".join(lines)


def _build_daily_digest(today, top_climbers, top_fallers, new_entries, exits, prior_exists=True):
    """Daily digest of top movers, new entries, and exits. Always sent to personal DM."""
    lines = [f"📊 **Steam Wishlist Daily — {today}**", ""]

    if not prior_exists:
        lines.append("_(First day of tracking — no prior data to compare)_")
        return "\n".join(lines)

    if top_climbers:
        lines.append("📈 **Top Climbers**")
        for name, old_rank, new_rank, delta, tier, developer, publisher, genre in top_climbers:
            lines.append(f"  {TIER_EMOJI.get(tier, '🎮')} {name}: #{old_rank} → #{new_rank} (+{delta})")
        lines.append("")

    if top_fallers:
        lines.append("📉 **Top Fallers**")
        for name, old_rank, new_rank, delta, tier, developer, publisher, genre in top_fallers:
            lines.append(f"  {TIER_EMOJI.get(tier, '🎮')} {name}: #{old_rank} → #{new_rank} ({delta})")
        lines.append("")

    if new_entries:
        cap = 15
        lines.append("🆕 **New to Top 500**")
        for name, rank, tier, developer, publisher, genre, velocity_7d in new_entries[:cap]:
            lines.append(f"  {TIER_EMOJI.get(tier, '🎮')} {name} (#{rank})")
        if len(new_entries) > cap:
            lines.append(f"  _(+ {len(new_entries) - cap} more)_")
        lines.append("")

    if exits:
        lines.append("📤 **Dropped Out**")
        for name in exits[:5]:
            lines.append(f"  • {name}")
        lines.append("")

    if not top_climbers and not top_fallers and not new_entries and not exits:
        lines.append("_(No rank changes today)_")

    return "\n".join(lines).rstrip()


def _build_movers_message(today, new_entries, big_climbers, high_velocity=None):
    """Build tier-grouped movers Seatalk message with optional velocity section."""
    high_velocity = high_velocity or []
    # Names already shown in new_entries/big_climbers — skip from high_velocity section
    already_shown = {e[0] for e in new_entries} | {e[0] for e in big_climbers}

    lines = [f"🚀 **Steam Wishlist Movers — {today}**", ""]
    if new_entries:
        lines.append("🆕 **New to Top 500:**")
        by_tier = {}
        for name, rank, tier, developer, publisher, genre, velocity_7d in new_entries:
            by_tier.setdefault(tier, []).append((name, rank, developer, publisher, genre, velocity_7d))
        for tier in ["Indie", "AA", "Triple A", "Early Access"]:
            if tier not in by_tier:
                continue
            lines.append(f"\n{TIER_EMOJI[tier]} **{tier}:**")
            for name, rank, developer, publisher, genre, velocity_7d in by_tier[tier]:
                meta = f"{developer}" if developer == publisher or publisher == "—" else f"{developer} / {publisher}"
                vel = f" | 🔥 +{velocity_7d} ranks/7d" if velocity_7d >= HIGH_VELOCITY_THRESHOLD else ""
                lines.append(f"• **{name}** (#{rank}) — {meta} | {genre}{vel}")
    if big_climbers:
        if new_entries:
            lines.append("")
        lines.append("⬆️ **Big Climbers (10+ positions):**")
        by_tier = {}
        for name, old, new_rank, delta, tier, developer, publisher, genre, velocity_7d in big_climbers:
            by_tier.setdefault(tier, []).append((name, old, new_rank, delta, developer, publisher, genre, velocity_7d))
        for tier in ["Indie", "AA", "Triple A", "Early Access"]:
            if tier not in by_tier:
                continue
            lines.append(f"\n{TIER_EMOJI[tier]} **{tier}:**")
            for name, old, new_rank, delta, developer, publisher, genre, velocity_7d in by_tier[tier]:
                meta = f"{developer}" if developer == publisher or publisher == "—" else f"{developer} / {publisher}"
                vel = f" | 🔥 +{velocity_7d} ranks/7d" if velocity_7d >= HIGH_VELOCITY_THRESHOLD else ""
                lines.append(f"• **{name}**: #{old} → #{new_rank} (+{delta}) — {meta} | {genre}{vel}")
    # High-velocity section: games not already listed above
    extra_vel = [(n, r, t, dev, pub, g, v) for n, r, t, dev, pub, g, v in high_velocity if n not in already_shown]
    if extra_vel:
        if new_entries or big_climbers:
            lines.append("")
        lines.append("🔥 **Trending (15+ rank climb in 7 days):**")
        by_tier = {}
        for name, rank, tier, developer, publisher, genre, velocity_7d in extra_vel:
            by_tier.setdefault(tier, []).append((name, rank, developer, publisher, genre, velocity_7d))
        for tier in ["Indie", "AA", "Triple A", "Early Access"]:
            if tier not in by_tier:
                continue
            lines.append(f"\n{TIER_EMOJI[tier]} **{tier}:**")
            for name, rank, developer, publisher, genre, velocity_7d in by_tier[tier]:
                meta = f"{developer}" if developer == publisher or publisher == "—" else f"{developer} / {publisher}"
                lines.append(f"• **{name}** (#{rank}) — climbed +{velocity_7d} ranks this week | {meta}")
    return "\n".join(lines)


def _get_seatalk_token(app_id, app_secret):
    """Exchange app_id + app_secret for a short-lived app_access_token."""
    resp = requests.post(
        "https://openapi.seatalk.io/auth/app_access_token",
        json={"app_id": app_id, "app_secret": app_secret},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise Exception(f"Seatalk auth error {data.get('code')}: {data.get('message', data)}")
    return data["app_access_token"]


def send_to_seatalk(config, message, dry_run=False, personal=False):
    """Send message via Seatalk OpenAPI (app_id + app_secret → token → send).
    personal=True → single_chat to seatalk_employee_code
    personal=False → group_chat to seatalk_group_id
    """
    sc = config["seatalk"]
    app_id     = sc.get("seatalk_app_id", "")
    app_secret = sc.get("seatalk_app_secret", "")

    if personal:
        employee_code = sc.get("seatalk_employee_code", "")
        if not employee_code:
            print("  [Seatalk] seatalk_employee_code not configured — skipping DM.")
            return False
        url          = "https://openapi.seatalk.io/messaging/v2/single_chat"
        payload      = {"employee_code": employee_code,
                        "message": {"tag": "text", "text": {"format": 1, "content": message}}}
        target_label = f"personal DM ({employee_code})"
    else:
        group_id = sc.get("seatalk_group_id", "")
        if not group_id:
            print("  [Seatalk] seatalk_group_id not configured — skipping group send.")
            return False
        url          = "https://openapi.seatalk.io/messaging/v2/group_chat"
        payload      = {"group_id": group_id,
                        "message": {"tag": "text", "text": {"format": 1, "content": message}}}
        target_label = "group chat"

    if dry_run:
        print(f"\n  [DRY RUN] Would send to Seatalk {target_label}:")
        print(f"    Payload preview:\n{message[:400]}...")
        return True

    if not app_id or not app_secret:
        print("  [Seatalk] seatalk_app_id or seatalk_app_secret not configured — skipping send.")
        return False

    try:
        token = _get_seatalk_token(app_id, app_secret)
    except Exception as e:
        print(f"  [Seatalk] Auth failed: {e}")
        return False

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        print(f"  Seatalk message sent to {target_label}. Status: {resp.status_code}")
        return True
    except Exception as e:
        print(f"  [Seatalk] Send error: {e}")
        return False


def run_weekly(spreadsheet, dry_run=False):
    config = load_config()

    week_start, week_end = get_week_range()
    week_num = week_start.isocalendar()[1]
    print(f"  Generating weekly report for Week {week_num}: "
          f"{week_start.strftime('%Y-%m-%d')} – {week_end.strftime('%Y-%m-%d')}")

    history_ws = get_or_create_worksheet(spreadsheet, HISTORY_SHEET, rows=5000, cols=8)
    summary_ws = get_or_create_worksheet(spreadsheet, SUMMARY_SHEET, rows=500, cols=10)

    # Load data
    week_rows   = load_history_for_week(history_ws, week_start, week_end)
    prior_rows  = load_prior_week_history(history_ws, week_start)
    prior_sums  = load_prior_weekly_summaries(summary_ws)

    if not week_rows:
        print(f"  WARNING: No history data found for Week {week_num}. "
              f"Has --mode daily been running this week?")

    analysis = analyse_week(week_rows, prior_rows)

    # Fetch news for top climbers + top 5 stable
    game_news = {}
    climber_names = [n for n, _ in analysis.get("top_climbers", [])[:5]]
    stable_names  = [n for n in analysis["top5_stable"][:3] if n not in climber_names]
    news_targets  = climber_names + stable_names
    if news_targets:
        print(f"  Fetching Steam news for {len(news_targets)} game(s) (top climbers + stable top 5)...")
        for name in news_targets:
            appid = analysis["appid_by_name"].get(name, "")
            news_items = fetch_game_news(appid, name, count=3)
            game_news[name] = news_items
            print(f"    {name}: {len(news_items)} article(s)")

    # AI commentary
    print("  Calling Compass Claude API for trend analysis...")
    prompt        = build_ai_prompt(week_start, week_end, analysis, prior_sums, game_news=game_news)
    ai_commentary = call_compass_api(config, prompt)
    print(f"  AI commentary received ({len(ai_commentary)} chars).")

    # Format Seatalk message
    message = format_seatalk_message(week_start, week_end, week_num, analysis, ai_commentary)

    # Write summary row
    top5_str   = ", ".join(analysis["top5_stable"][:5])
    top10_str  = ", ".join(analysis["top10_stable"][:10])
    new_str    = ", ".join(analysis["new_entrants"][:5])
    exits_str  = ", ".join(analysis["exits"][:5])
    owners_str = " | ".join(
        f"{n}: {analysis['end_of_week_owners'].get(n, '—')}"
        for n in analysis["top5_stable"][:5]
    )
    genre_dist = analysis.get("genre_distribution", [])
    genres_str = ", ".join(f"{g} ({c})" for g, c in genre_dist) if genre_dist else "—"

    summary_row = [
        week_num,
        week_start.strftime("%Y-%m-%d"),
        week_end.strftime("%Y-%m-%d"),
        top5_str,
        top10_str,
        new_str,
        exits_str,
        owners_str,
        genres_str,
        ai_commentary,
    ]

    if dry_run:
        print(f"\n  [DRY RUN] Would append summary row to '{SUMMARY_SHEET}':")
        print(f"    {summary_row[:4]}...")
        print(f"\n  [DRY RUN] Seatalk message:\n{'='*60}")
        print(message)
        print("="*60)
    else:
        # Write header if sheet is empty
        existing = summary_ws.get_all_values()
        if not existing:
            summary_ws.append_row(
                ["Week #", "Week Start", "Week End", "Top 5 Stable",
                 "Top 10 Stable", "New Entrants", "Exits",
                 "End-of-Week Owners", "Top Genres", "AI Commentary"],
                value_input_option="USER_ENTERED",
            )
        summary_ws.append_row(summary_row, value_input_option="USER_ENTERED")
        print(f"  Appended summary row to '{SUMMARY_SHEET}'.")

    # Send to Seatalk (personal DM if seatalk_mode=personal or --personal flag used)
    personal_mode = config["seatalk"].get("seatalk_mode", "group") == "personal"
    send_to_seatalk(config, message, dry_run=dry_run, personal=personal_mode)

# ── Main ──────────────────────────────────────────────────────────────────────

def resend_movers(spreadsheet, target_date=None, personal=True):
    """Re-compute and resend the movers alert from already-captured sheet data.
    Reads today's rows and the most recent prior date's rows — no new API calls, no writes.
    """
    today = target_date or datetime.now().strftime("%Y-%m-%d")
    config = load_config()

    ws = spreadsheet.worksheet(HISTORY_SHEET)
    existing = ws.get_all_values()
    if len(existing) < 2:
        print("  No history data found.")
        return

    # Gather today's rows (excluding non-games)
    today_rows = [r for r in existing[1:] if r and r[0] == today and r[2] not in EXCLUDED_NAMES]
    if not today_rows:
        print(f"  No rows found for {today} in '{HISTORY_SHEET}'.")
        return

    # Build prior ranks from the most recent date before today
    dates_before = sorted(set(r[0] for r in existing[1:] if r and r[0] < today))
    prior_ranks = {}
    prior_ranks_7d = {}
    if dates_before:
        latest_prior = dates_before[-1]
        for r in existing[1:]:
            if r and r[0] == latest_prior and len(r) >= 3:
                try:
                    prior_ranks[r[2]] = int(r[1])
                except (ValueError, IndexError):
                    pass

        target_7d = (datetime.strptime(today, "%Y-%m-%d") - timedelta(days=7)).strftime("%Y-%m-%d")
        best_date = None
        for d in dates_before:
            try:
                diff = abs((datetime.strptime(d, "%Y-%m-%d") - datetime.strptime(target_7d, "%Y-%m-%d")).days)
                if diff <= 2:
                    if best_date is None:
                        cur_diff = diff + 1
                    else:
                        cur_diff = abs((datetime.strptime(best_date, "%Y-%m-%d") - datetime.strptime(target_7d, "%Y-%m-%d")).days)
                    if diff < cur_diff:
                        best_date = d
            except ValueError:
                pass
        if best_date:
            for r in existing[1:]:
                if r and r[0] == best_date and len(r) >= 3:
                    try:
                        prior_ranks_7d[r[2]] = int(r[1])
                    except (ValueError, IndexError):
                        pass

    new_entries = []
    big_climbers = []
    high_velocity = []

    for row in today_rows:
        if len(row) < 11:
            continue
        try:
            rank      = int(row[1])
            name      = row[2]
            developer = row[4]
            publisher = row[5]
            genre     = row[6]
            tier      = classify_game(genre, publisher, developer)
        except (ValueError, IndexError):
            continue

        if name not in prior_ranks:
            rank_change = "NEW"
            velocity_7d = 0
            new_entries.append((name, rank, tier, developer, publisher, genre, velocity_7d))
        else:
            delta = prior_ranks[name] - rank
            rank_change = f"+{delta}" if delta > 0 else str(delta)
            velocity_7d = prior_ranks_7d[name] - rank if name in prior_ranks_7d else 0
            if delta >= 10:
                big_climbers.append((name, prior_ranks[name], rank, delta, tier, developer, publisher, genre, velocity_7d))

        velocity_7d = prior_ranks_7d.get(name, 0) and (prior_ranks_7d[name] - rank)
        if velocity_7d >= HIGH_VELOCITY_THRESHOLD:
            high_velocity.append((name, rank, tier, developer, publisher, genre, velocity_7d))

    if not (new_entries or big_climbers or high_velocity):
        print("  No significant movers today — nothing to send.")
        return

    msg = _build_movers_message(today, new_entries, big_climbers, high_velocity)
    print(msg)
    send_to_seatalk(config, msg, personal=personal)


def main():
    parser = argparse.ArgumentParser(description="Steam Wishlist Tracker")
    parser.add_argument(
        "--mode", choices=["daily", "weekly", "resend-movers"],
        required=True,
        help="'daily' = capture today's chart; 'weekly' = generate + send report; 'resend-movers' = resend today's movers alert from existing data",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print output without writing to Sheets or sending to Seatalk",
    )
    parser.add_argument(
        "--personal", action="store_true", default=None,
        help="Force personal DM mode for resend-movers (overrides config)",
    )
    args = parser.parse_args()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] Steam Wishlist Tracker — mode: {args.mode}")
    print("Connecting to Google Sheets...")
    spreadsheet = get_spreadsheet()
    print(f"Connected: {spreadsheet.title}\n")

    if args.mode == "daily":
        run_daily(spreadsheet, dry_run=args.dry_run)
    elif args.mode == "weekly":
        run_weekly(spreadsheet, dry_run=args.dry_run)
    elif args.mode == "resend-movers":
        personal = True if args.personal else load_config()["seatalk"].get("seatalk_mode", "group") == "personal"
        resend_movers(spreadsheet, personal=personal)

    print("\nDone.")


if __name__ == "__main__":
    main()
