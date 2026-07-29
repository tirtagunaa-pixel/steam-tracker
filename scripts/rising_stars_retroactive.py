"""
Rising Stars Retroactive Analysis
----------------------------------
Reads Wishlist History, finds games ranked 101-500 in the most recent Top-500 data,
computes rank change from first appearance vs latest, and sends a summary to personal DM.
"""

import sys
import json
import requests
from datetime import datetime
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import gspread
from google.oauth2.service_account import Credentials

BASE_DIR             = Path(__file__).parent.parent
CONFIG_FILE          = Path(__file__).parent / "watch_config.json"
SERVICE_ACCOUNT_FILE = Path(__file__).parent / "service_account.json"

SPREADSHEET_ID = "1mfz9E63bc9Ea9rHf6O7CqVYgUw_zNMV6CWwi5jrX0Ac"
HISTORY_SHEET  = "Wishlist History"
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

EXCLUDED_NAMES = {"Steam Frame", "Steam Machine"}
TIER_EMOJI = {"Indie": "🎮", "Triple A": "🏢", "AA": "🔷", "Early Access": "🧪"}

AAA_PUBLISHERS = {
    "ubisoft", "electronic arts", "ea games", "capcom", "activision", "blizzard",
    "take-two", "rockstar games", "2k games", "square enix", "sega",
    "bandai namco", "konami", "bethesda", "xbox game studios", "microsoft",
    "playstation studios", "sony interactive", "warner bros", "cd projekt",
    "riot games", "epic games", "valve", "505 games", "deep silver",
    "thq nordic", "focus entertainment", "nacon", "4a games",
}

def classify_game(genre, publisher, developer):
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

def estimate_wishlists(rank):
    """Rough rank-based estimate using GDC Pro and public benchmark data."""
    if rank <= 10:  return "~1.5M-3M+"
    if rank <= 25:  return "~1M-1.5M"
    if rank <= 50:  return "~700K-1M"
    if rank <= 80:  return "~500K-800K"
    if rank <= 100: return "~350K-600K"
    if rank <= 130: return "~250K-400K"
    if rank <= 160: return "~170K-280K"
    if rank <= 200: return "~100K-200K"
    if rank <= 250: return "~70K-130K"
    if rank <= 300: return "~50K-90K"
    if rank <= 350: return "~35K-65K"
    if rank <= 400: return "~25K-50K"
    if rank <= 450: return "~18K-38K"
    return "~12K-28K"

def _get_seatalk_token(app_id, app_secret):
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

def send_personal_dm(config, message):
    sc = config["seatalk"]
    app_id        = sc.get("seatalk_app_id", "")
    app_secret    = sc.get("seatalk_app_secret", "")
    employee_code = sc.get("seatalk_employee_code", "")
    if not all([app_id, app_secret, employee_code]):
        print("  [Seatalk] Missing credentials — printing message only.\n")
        print(message)
        return
    token = _get_seatalk_token(app_id, app_secret)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "employee_code": employee_code,
        "message": {"tag": "text", "text": {"format": 1, "content": message}},
    }
    resp = requests.post(
        "https://openapi.seatalk.io/messaging/v2/single_chat",
        headers=headers, json=payload, timeout=15,
    )
    resp.raise_for_status()
    print(f"  Sent to personal DM. Status: {resp.status_code}")

def main():
    with open(CONFIG_FILE, encoding="utf-8") as f:
        config = json.load(f)

    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    ws = spreadsheet.worksheet(HISTORY_SHEET)

    print("  Reading Wishlist History...")
    all_rows = ws.get_all_values()
    if len(all_rows) < 2:
        print("  No data found.")
        return

    header = all_rows[0]
    data_rows = all_rows[1:]

    # Find dates where we have rank-101+ data (i.e. Top 500 was captured)
    date_max_rank = defaultdict(int)
    for row in data_rows:
        if len(row) < 3 or not row[0] or not row[1]:
            continue
        try:
            date_max_rank[row[0]] = max(date_max_rank[row[0]], int(row[1]))
        except ValueError:
            pass

    top500_dates = sorted([d for d, max_r in date_max_rank.items() if max_r > 100])
    print(f"  Dates with Top-500 data: {top500_dates}")

    if len(top500_dates) < 2:
        print("  Need at least 2 days of Top-500 data for comparison. Only have:", top500_dates)
        return

    earliest_date = top500_dates[0]
    latest_date   = top500_dates[-1]
    span_days = (datetime.strptime(latest_date, "%Y-%m-%d") -
                 datetime.strptime(earliest_date, "%Y-%m-%d")).days

    print(f"  Comparing: {earliest_date} → {latest_date} ({span_days} days)")

    # Build rank lookup per date per game; also store metadata
    rank_on_date = defaultdict(dict)  # {name: {date: rank}}
    meta_lookup  = {}                 # {name: {tier, developer, publisher, genre}}
    for row in data_rows:
        if len(row) < 7 or not row[0] or not row[1] or not row[2]:
            continue
        if row[2] in EXCLUDED_NAMES:
            continue
        try:
            rank = int(row[1])
        except ValueError:
            continue
        name = row[2]
        date = row[0]
        rank_on_date[name][date] = rank
        if name not in meta_lookup:
            developer = row[4] if len(row) > 4 else "—"
            publisher = row[5] if len(row) > 5 else "—"
            genre     = row[6] if len(row) > 6 else "—"
            meta_lookup[name] = {
                "tier":      classify_game(genre, publisher, developer),
                "developer": developer or "—",
                "publisher": publisher or "—",
                "genre":     genre or "—",
            }

    # Analyse games that appeared in the 101-500 range on the latest date
    results = []
    for name, date_ranks in rank_on_date.items():
        latest_rank = date_ranks.get(latest_date)
        if latest_rank is None or latest_rank <= 100:
            continue

        dates_in_window = sorted([d for d in date_ranks if d in top500_dates])
        if not dates_in_window:
            continue
        first_date = dates_in_window[0]
        first_rank = date_ranks[first_date]
        days_tracked = (datetime.strptime(latest_date, "%Y-%m-%d") -
                        datetime.strptime(first_date, "%Y-%m-%d")).days

        delta = first_rank - latest_rank  # positive = climbed
        meta  = meta_lookup.get(name, {})

        results.append({
            "name":          name,
            "tier":          meta.get("tier", "AA"),
            "developer":     meta.get("developer", "—"),
            "publisher":     meta.get("publisher", "—"),
            "genre":         meta.get("genre", "—"),
            "first_rank":    first_rank,
            "latest_rank":   latest_rank,
            "delta":         delta,
            "days":          days_tracked,
            "est_wishlists": estimate_wishlists(latest_rank),
        })

    climbers = sorted([r for r in results if r["delta"] > 0], key=lambda x: x["delta"], reverse=True)
    stable_ct = sum(1 for r in results if r["delta"] == 0)
    faller_ct = sum(1 for r in results if r["delta"] < 0)

    print(f"  Games 101-500 on {latest_date}: {len(results)} total "
          f"({len(climbers)} climbers, {stable_ct} stable, {faller_ct} fallers)")

    TIER_LABEL = {"Indie": "Indie", "Triple A": "AAA", "AA": "AA", "Early Access": "Early Access"}

    # Build message — climbers only
    lines = [
        f"🌱 **Rising Stars ({earliest_date} → {latest_date}, {span_days}d)**",
        f"Rank 101-500 games gaining ground — sorted by positions climbed",
        "",
        "📈 **Climbers**",
        "",
    ]

    for r in climbers[:30]:
        tier_label = TIER_LABEL.get(r["tier"], r["tier"])
        days_str   = f"{r['days']}d" if r["days"] > 0 else "today"
        dev        = r["developer"]
        pub        = r["publisher"]
        credit     = dev if (dev == pub or pub in ("—", "")) else f"{dev} / {pub}"
        genre      = r["genre"] if r["genre"] not in ("—", "") else "—"
        lines.append(
            f"**{r['name']}** [{tier_label}] — #{r['first_rank']} → #{r['latest_rank']} "
            f"(+{r['delta']} in {days_str}) | {r['est_wishlists']}"
        )
        lines.append(f"  _{credit} | {genre}_")
        lines.append("")

    if not climbers:
        lines.append("_(No rank climbers in rank 101-500 yet — check back after more days of data)_")

    lines.append(f"_Data from {len(top500_dates)} captured day(s) · {len(climbers)} climbers / {stable_ct} stable / {faller_ct} fallers_")

    message = "\n".join(lines).rstrip()
    print("\n" + "="*60)
    print(message)
    print("="*60 + "\n")

    send_personal_dm(config, message)

if __name__ == "__main__":
    main()
