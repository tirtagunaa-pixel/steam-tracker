"""
Steam Wishlist Tracker — Daily capture + Weekly AI report
----------------------------------------------------------
Modes:
  --mode daily   Fetch today's Top 15 wishlist chart and append to 'Wishlist History' sheet.
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

HISTORY_SHEET = "Wishlist History"
SUMMARY_SHEET = "Weekly Wishlist Summary"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IndieGameResearch/1.0)"}

TOP_N = 25  # Steam's popularwishlist endpoint returns 25 results regardless of count param

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

def steam_search_wishlist(max_results=15):
    url = "https://store.steampowered.com/search/results/"
    params = {"filter": "popularwishlist", "json": 1, "count": max_results, "start": 0}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        # Extract appid from logo URL: .../apps/<appid>/...
        for item in items:
            logo = item.get("logo", "")
            m = re.search(r"/apps/(\d+)/", logo)
            item["appid"] = m.group(1) if m else ""
        return items
    except Exception as e:
        print(f"  [Wishlist] API error: {e}")
        return []


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

    if not dry_run:
        ws_check = get_or_create_worksheet(spreadsheet, HISTORY_SHEET, rows=5000, cols=10)
        existing = ws_check.get_all_values()
        if any(row and row[0] == today for row in existing[1:]):
            print(f"  Already captured data for {today}. Skipping duplicate run.")
            return

    print(f"  Fetching Top {TOP_N} wishlist chart for {today}...")

    items = steam_search_wishlist(max_results=TOP_N)
    if not items:
        print("  ERROR: No data returned from Steam. Aborting.")
        return

    rows = []
    for rank, item in enumerate(items, start=1):
        appid = item.get("appid", "")
        name  = item.get("name", "Unknown")

        details = {}
        if appid:
            details = steam_appdetails(appid)
            time.sleep(0.4)

        spy = {"wishlists": 0, "owners": "—"}
        if appid:
            spy = steamspy_data(appid)
            time.sleep(0.5)

        rows.append([
            today,
            rank,
            name,
            str(appid),
            details.get("developer", "—"),
            details.get("publisher", "—"),
            details.get("genres", "—"),
            details.get("release_date", item.get("release_date", "—")),
            spy["wishlists"],
            spy["owners"],
        ])
        print(f"    #{rank:02d} {name}")

    if dry_run:
        print(f"\n  [DRY RUN] Would append {len(rows)} rows to '{HISTORY_SHEET}'.")
        for r in rows[:3]:
            print(f"    {r}")
        return

    ws = get_or_create_worksheet(spreadsheet, HISTORY_SHEET, rows=5000, cols=10)

    # Write header if sheet is empty
    existing = ws.get_all_values()
    if not existing:
        ws.append_row(
            ["Date", "Rank", "Game Name", "AppID", "Developer", "Publisher",
             "Genre", "Release Date", "Wishlist Est.", "Owners Est."],
            value_input_option="USER_ENTERED",
        )

    ws.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"  Appended {len(rows)} rows to '{HISTORY_SHEET}'.")

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
        if not name or rank is None:
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

    new_entrants = [n for n in this_names if n not in prior_names]
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

    top5_lines = []
    for name in analysis["top5_stable"][:5]:
        days    = analysis["days_in_chart"].get(name, 0)
        owners  = analysis["end_of_week_owners"].get(name, "—")
        ranks   = analysis["rank_by_name"].get(name, [])
        avg_rank = f"{sum(ranks)/len(ranks):.1f}" if ranks else "?"
        top5_lines.append(f"  - {name}: {days}/7 days in Top 5, avg rank {avg_rank}, owners est. {owners}")

    top10_others = [n for n in analysis["top10_stable"] if n not in analysis["top5_stable"]]
    top10_lines  = [f"  - {n}" for n in top10_others[:5]]

    new_lines  = [f"  - {n}" for n in analysis["new_entrants"][:5]]
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

    # Per-game news context block
    news_block = ""
    if game_news:
        sections = []
        for name in analysis["top5_stable"][:5]:
            items = game_news.get(name, [])
            if not items:
                sections.append(f"  [{name}]: no recent news found")
                continue
            snippets = [
                f'    • [{it.get("feedname", "")}] "{it.get("title", "")}" ({it.get("url", "")}) — {it.get("contents", "")[:300]}'
                for it in items
            ]
            sections.append(f"  [{name}]:\n" + "\n".join(snippets))
        if sections:
            news_block = "Recent news for Top 5 games (Steam News API):\n" + "\n".join(sections) + "\n"

    prior_context = ""
    if prior_summaries:
        last_n = prior_summaries[-6:]  # up to 6 prior weeks for context
        prior_context = "Prior weekly summaries (oldest to newest):\n"
        for s in last_n:
            prior_context += (
                f"  Week {s.get('Week #', '?')} ({s.get('Week Start', '')}–{s.get('Week End', '')}): "
                f"Top 5 stable: {s.get('Top 5 Stable', '—')} | "
                f"New entrants: {s.get('New Entrants', '—')} | "
                f"Exits: {s.get('Exits', '—')}\n"
            )
        prior_context += "\n"

    prompt = f"""You are a game market analyst. Analyse the Steam Wishlist chart data for the week of {week_label} and write a concise, insightful trend commentary for an indie game research team.

Focus on:
- For EACH of the top 5 games: explain WHY it is popular this week, drawing on the news snippets provided — cite specific announcements, upcoming features, or community events where available
- What genres or game types dominated the chart this week (use the genre frequency data provided)
- Significant new entrants or exits and what they might signal
- How this week's chart compares to prior weeks (look for evolving patterns)
- Any notable developer or publisher trends

**This week's data ({week_label}):**

Top 5 stable games (in Top 5 on 5+ of 7 days):
{chr(10).join(top5_lines) if top5_lines else "  (insufficient daily data)"}

Other Top 10 stable games:
{chr(10).join(top10_lines) if top10_lines else "  none"}

New entrants this week (not in prior week's Top 15):
{chr(10).join(new_lines) if new_lines else "  none"}

Games that dropped out of Top 15:
{chr(10).join(exit_lines) if exit_lines else "  none"}

{genre_block}
{news_block}
{prior_context}Write your analysis as bullet points only — one bullet per insight, each a single short sentence (max 20 words). Use • as the bullet character. For any cited news or article include the URL inline formatted as [Source](url). Write 5–8 bullets total."""

    return prompt


def format_seatalk_message(week_start, week_end, week_num, analysis, ai_commentary):
    """Build the Markdown message for Seatalk (format=1)."""
    week_label = f"{week_start.strftime('%b %d')}–{week_end.strftime('%b %d, %Y')}"

    lines = [
        f"📊 **Steam Wishlist Chart — Week {week_num} ({week_label})**",
        "",
        "**🏆 Top 5 (stable — appeared in Top 5 on 5+ days)**",
    ]

    def is_indie(name):
        genre_str = analysis.get("genre_by_name", {}).get(name, "")
        return "Indie" in genre_str.split(", ")

    top5 = analysis["top5_stable"][:5]
    if top5:
        for i, name in enumerate(top5, start=1):
            days_top5 = sum(1 for r in analysis["rank_by_name"].get(name, []) if r <= 5)
            genre     = analysis.get("genre_by_name", {}).get(name, "—")
            publisher = analysis.get("publisher_by_name", {}).get(name, "—")
            lines.append(f"{i}. **{name}** | {genre} | {publisher} | {days_top5}/7 days in Top 5")
        indie_count5 = sum(1 for n in top5 if is_indie(n))
        aaa_count5   = len(top5) - indie_count5
        lines.append(f"_Indie: {indie_count5} | AAA/Non-Indie: {aaa_count5}_")
    else:
        lines.append("_(insufficient daily data captured this week)_")

    lines += ["", "**📈 Top 10 Roundup**"]
    top10_others = [n for n in analysis["top10_stable"] if n not in analysis["top5_stable"]][:5]
    if top10_others:
        for i, name in enumerate(top10_others, start=len(top5) + 1):
            days_top10 = sum(1 for r in analysis["rank_by_name"].get(name, []) if r <= 10)
            genre      = analysis.get("genre_by_name", {}).get(name, "—")
            publisher  = analysis.get("publisher_by_name", {}).get(name, "—")
            lines.append(f"{i}. **{name}** | {genre} | {publisher} | {days_top10}/7 days in Top 10")
        all_top10 = analysis["top10_stable"][:10]
        indie_count10 = sum(1 for n in all_top10 if is_indie(n))
        aaa_count10   = len(all_top10) - indie_count10
        lines.append(f"_Indie: {indie_count10} | AAA/Non-Indie: {aaa_count10} (across full Top 10)_")
    else:
        lines.append("_(see Top 5 above)_")

    lines += [""]
    if analysis["new_entrants"]:
        lines.append("**🆕 New This Week**")
        for name in analysis["new_entrants"][:4]:
            rank = analysis["final_ranks"].get(name, "?")
            lines.append(f"• {name} (entered at #{rank})")

    if analysis["exits"]:
        lines.append("**📉 Dropped Out**")
        for name in analysis["exits"][:4]:
            lines.append(f"• {name}")

    genre_dist = analysis.get("genre_distribution", [])
    if genre_dist:
        lines.append("")
        lines.append("**🎮 Top Genres This Week**")
        for i, (genre, count) in enumerate(genre_dist, start=1):
            lines.append(f"{i}. {genre} ({count} chart appearances)")

    lines += [
        "",
        "**🤖 Trend Analysis**",
        ai_commentary,
    ]

    return "\n".join(lines)


def send_to_seatalk(config, message, dry_run=False):
    """POST the formatted message to Pawon webhook, which routes to Seatalk."""
    webhook_url = config["seatalk"].get("pawon_webhook_url", "")
    group_id    = config["seatalk"].get("seatalk_group_id", "")

    if not webhook_url or webhook_url.startswith("FILL_IN"):
        print("  [Seatalk] pawon_webhook_url not configured in watch_config.json — skipping send.")
        return False

    if dry_run:
        print("\n  [DRY RUN] Would POST to Pawon webhook:")
        print(f"    URL: {webhook_url}")
        print(f"    Payload preview:\n{message[:400]}...")
        return True

    headers = {
        "Authorization": f"Bearer {config['seatalk']['pawon_api_key']}",
        "Content-Type":  "application/json",
    }
    payload = {
        "message":  message,
        "group_id": group_id,
    }
    try:
        resp = requests.post(webhook_url, headers=headers, json=payload, timeout=15)
        resp.raise_for_status()
        print(f"  Seatalk message sent. Status: {resp.status_code}")
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

    # Fetch news for top 5 games
    game_news = {}
    top5_for_news = analysis["top5_stable"][:5]
    if top5_for_news:
        print(f"  Fetching Steam news for {len(top5_for_news)} top game(s)...")
        for name in top5_for_news:
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

    # Send to Seatalk
    send_to_seatalk(config, message, dry_run=dry_run)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Steam Wishlist Tracker")
    parser.add_argument(
        "--mode", choices=["daily", "weekly"], required=True,
        help="'daily' = capture today's chart; 'weekly' = generate + send report",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print output without writing to Sheets or sending to Seatalk",
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

    print("\nDone.")


if __name__ == "__main__":
    main()
