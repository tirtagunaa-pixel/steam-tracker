"""
Rising Stars Retroactive Analysis
----------------------------------
Reads Wishlist History, finds games ranked 101-500 in the most recent Top-500 data,
computes rank change from first appearance vs latest, and sends a summary to personal DM.
"""

import sys
import re
import json
import time
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
    """Rank-based wishlist estimate.
    Calibrated from two confirmed data points (Jul 2026):
      - rank ~90  ≈ 600K  (GDC Pro chart data)
      - rank ~366 > 100K  (Sandcastle Steam community post)
    Fit: ~170M × rank^-1.28. Ranges are ±40% around the central estimate.
    Caveat: Steam ranks by velocity (recent adds), not total count.
    Older games accumulate wishlists over time and may sit higher than
    their rank implies; newer games at the same rank may have fewer.
    """
    if rank <= 10:  return "~1.5M-4M+"
    if rank <= 25:  return "~900K-1.8M"
    if rank <= 50:  return "~600K-1.1M"
    if rank <= 80:  return "~430K-760K"
    if rank <= 100: return "~340K-600K"
    if rank <= 130: return "~270K-480K"
    if rank <= 160: return "~215K-385K"
    if rank <= 200: return "~170K-305K"
    if rank <= 250: return "~135K-240K"
    if rank <= 300: return "~105K-190K"
    if rank <= 350: return "~90K-160K"
    if rank <= 400: return "~75K-140K"
    if rank <= 450: return "~65K-120K"
    return "~55K-100K"

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; IndieGameResearch/1.0)"}

def find_appid_by_name(name):
    """Search Steam for a game by name; return appid string or ''."""
    try:
        resp = requests.get(
            "https://store.steampowered.com/api/storesearch/",
            params={"term": name, "l": "english", "cc": "US"},
            headers=HEADERS, timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        name_lower = name.lower()
        for item in items:
            if item.get("name", "").lower() == name_lower:
                return str(item["id"])
        # Accept closest match if first result is very similar
        if items:
            first = items[0]
            if name_lower in first.get("name", "").lower() or first.get("name", "").lower() in name_lower:
                return str(first["id"])
    except Exception:
        pass
    return ""

def _clean(text):
    return (text or "").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&#39;", "'").strip()

def steam_enrich(appid):
    """Return {developer, publisher, genres, tags} for an appid via appdetails + store page.
    Falls back to short description when no user-defined tags exist."""
    result = {"developer": "—", "publisher": "—", "genres": "—", "tags": "—"}
    if not appid:
        return result
    try:
        resp = requests.get(
            f"https://store.steampowered.com/api/appdetails?appids={appid}",
            headers=HEADERS, timeout=10,
        )
        resp.raise_for_status()
        data = resp.json().get(str(appid), {})
        if data.get("success"):
            d = data.get("data", {})
            result["developer"] = ", ".join(d.get("developers", [])) or "—"
            result["publisher"]  = ", ".join(d.get("publishers", [])) or "—"
            result["genres"]     = ", ".join(g["description"] for g in d.get("genres", [])) or "—"
    except Exception:
        pass

    # User-defined tags via store page HTML (official API doesn't expose these)
    try:
        time.sleep(0.3)
        resp = requests.get(
            f"https://store.steampowered.com/app/{appid}/",
            headers=HEADERS, timeout=10,
        )
        html = resp.text
        tags = re.findall(r'class="app_tag"[^>]*>\s*([^<\n]+?)\s*<', html)
        tags = [_clean(t) for t in tags if _clean(t) and _clean(t) != "+"]
        if tags:
            result["tags"] = ", ".join(tags[:8])
        else:
            # Fallback: short description from store page
            m = re.search(r'class="game_description_snippet"[^>]*>\s*([^<\n]+?)\s*<', html)
            if m:
                result["tags"] = _clean(m.group(1))[:160]
    except Exception:
        pass

    return result


def web_search_description(name):
    """DuckDuckGo instant answer API — last-resort fallback for game description/tags."""
    try:
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": f"{name} steam game", "format": "json",
                    "no_redirect": "1", "no_html": "1", "skip_disambig": "1"},
            headers=HEADERS, timeout=10,
        )
        data = resp.json()
        text = (data.get("AbstractText") or "").strip()
        if len(text) > 20:
            return text[:160]
        for topic in data.get("RelatedTopics", [])[:4]:
            if isinstance(topic, dict):
                text = (topic.get("Text") or "").strip()
                if len(text) > 20:
                    return text[:160]
    except Exception:
        pass
    return "—"


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

    # Build rank lookup per date per game; also store appid and metadata from sheet
    rank_on_date = defaultdict(dict)  # {name: {date: rank}}
    appid_lookup = {}                 # {name: appid_str}
    meta_lookup  = {}                 # {name: {tier, developer, publisher, genre, tags}}
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
            appid     = row[3] if len(row) > 3 else ""
            developer = (row[4] if len(row) > 4 else "") or ""
            publisher = (row[5] if len(row) > 5 else "") or ""
            genre     = (row[6] if len(row) > 6 else "") or ""
            appid_lookup[name] = appid
            meta_lookup[name] = {
                "tier":      classify_game(genre, publisher, developer),
                "developer": developer or "—",
                "publisher": publisher or "—",
                "genre":     genre or "—",
                "tags":      "—",
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
        if delta <= 0:
            continue  # only keep climbers, skip now to avoid enriching fallers/stable

        results.append({
            "name":          name,
            "delta":         delta,
            "first_rank":    first_rank,
            "latest_rank":   latest_rank,
            "days":          days_tracked,
            "est_wishlists": estimate_wishlists(latest_rank),
        })

    climbers = sorted(results, key=lambda x: x["delta"], reverse=True)

    # Count stable/fallers for footer
    all_ranks_101plus = [
        name for name, date_ranks in rank_on_date.items()
        if date_ranks.get(latest_date, 0) > 100
    ]
    stable_ct = sum(1 for name in all_ranks_101plus
                    if name not in {r["name"] for r in climbers}
                    and rank_on_date[name].get(latest_date) == rank_on_date[name].get(
                        sorted([d for d in rank_on_date[name] if d in top500_dates])[0]
                        if sorted([d for d in rank_on_date[name] if d in top500_dates]) else latest_date
                    ))
    faller_ct = len(all_ranks_101plus) - len(climbers) - stable_ct

    print(f"  Games 101-500 on {latest_date}: {len(all_ranks_101plus)} total "
          f"({len(climbers)} climbers)")

    TIER_LABEL = {"Indie": "Indie", "Triple A": "AAA", "AA": "AA", "Early Access": "Early Access"}

    # ── Phase 1: enrich games with missing developer data (no appid captured) ──
    missing = [r for r in climbers if meta_lookup.get(r["name"], {}).get("developer", "—") == "—"]
    if missing:
        print(f"  Phase 1: enriching {len(missing)} games with no metadata...")
    for i, r in enumerate(missing):
        name  = r["name"]
        appid = appid_lookup.get(name, "")
        if not appid:
            appid = find_appid_by_name(name)
            if appid:
                appid_lookup[name] = appid
            time.sleep(0.4)
        if appid:
            enriched = steam_enrich(appid)
            meta_lookup[name].update({
                "developer": enriched["developer"],
                "publisher":  enriched["publisher"],
                "genre":      enriched["genres"],
                "tags":       enriched["tags"],
                "tier":       classify_game(enriched["genres"],
                                            enriched["publisher"],
                                            enriched["developer"]),
            })
            time.sleep(0.4)
        else:
            # DuckDuckGo fallback when no Steam page found
            desc = web_search_description(name)
            if desc != "—":
                meta_lookup[name]["tags"] = f"[web] {desc}"
            time.sleep(0.5)
        if (i + 1) % 20 == 0:
            print(f"    {i+1}/{len(missing)} done")

    # ── Phase 2: fetch store page tags for games that have dev data but no tags ──
    no_tags = [r for r in climbers
               if meta_lookup.get(r["name"], {}).get("tags", "—") == "—"
               and appid_lookup.get(r["name"], "")]
    if no_tags:
        print(f"  Phase 2: fetching store tags/descriptions for {len(no_tags)} games...")
    for i, r in enumerate(no_tags):
        name  = r["name"]
        appid = appid_lookup.get(name, "")
        try:
            time.sleep(0.3)
            resp = requests.get(f"https://store.steampowered.com/app/{appid}/",
                                headers=HEADERS, timeout=10)
            html = resp.text
            tags = re.findall(r'class="app_tag"[^>]*>\s*([^<\n]+?)\s*<', html)
            tags = [_clean(t) for t in tags if _clean(t) and _clean(t) != "+"]
            if tags:
                meta_lookup[name]["tags"] = ", ".join(tags[:8])
            else:
                # Short description fallback
                m = re.search(r'class="game_description_snippet"[^>]*>\s*([^<\n]+?)\s*<', html)
                if m:
                    meta_lookup[name]["tags"] = _clean(m.group(1))[:160]
        except Exception:
            pass
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(no_tags)} done")

    # ── Phase 3: DuckDuckGo for anything still blank ──
    still_blank = [r for r in climbers if meta_lookup.get(r["name"], {}).get("tags", "—") == "—"]
    if still_blank:
        print(f"  Phase 3: web search fallback for {len(still_blank)} remaining games...")
    for r in still_blank:
        name = r["name"]
        desc = web_search_description(name)
        if desc != "—":
            meta_lookup[name]["tags"] = f"[web] {desc}"
        time.sleep(0.5)

    print(f"  Enrichment complete. Writing {len(climbers)} climbers to Google Sheet...")

    # ── Write ALL climbers to a Google Sheet tab ──
    def get_or_create_ws(ss, name, rows=1000, cols=10):
        try:
            return ss.worksheet(name)
        except Exception:
            return ss.add_worksheet(name, rows=rows, cols=cols)

    snap_ws = get_or_create_ws(spreadsheet, "Rising Stars Snapshot", rows=1000, cols=10)
    snap_ws.clear()
    snap_ws.append_row(
        ["Date", "Rank (latest)", "Game Name", "Tier", "Developer", "Publisher",
         "Tags / Description", "Rank Change", "Span (days)", "Est. Wishlists"],
        value_input_option="USER_ENTERED",
    )
    sheet_rows = []
    for r in climbers:
        name = r["name"]
        meta = meta_lookup.get(name, {})
        dev  = meta.get("developer", "—")
        pub  = meta.get("publisher", "—")
        tags = meta.get("tags", "—") if meta.get("tags", "—") != "—" else meta.get("genre", "—")
        sheet_rows.append([
            latest_date,
            r["latest_rank"],
            name,
            TIER_LABEL.get(meta.get("tier", "AA"), "AA"),
            dev,
            pub,
            tags,
            f"+{r['delta']}",
            r["days"],
            r["est_wishlists"],
        ])
    if sheet_rows:
        snap_ws.append_rows(sheet_rows, value_input_option="USER_ENTERED")
    print(f"  Written {len(sheet_rows)} rows to 'Rising Stars Snapshot'.")

    # ── Build Seatalk DM: top 30 climbers summary ──
    top30 = climbers[:30]
    lines = [
        f"🌱 **Rising Stars ({earliest_date} → {latest_date}, {span_days}d)**",
        f"Rank 101-500 climbers — top 30 of {len(climbers)} | full list in 'Rising Stars Snapshot' sheet",
        "",
        "📈 **Climbers**",
        "",
    ]

    for r in top30:
        name       = r["name"]
        meta       = meta_lookup.get(name, {})
        tier_label = TIER_LABEL.get(meta.get("tier", "AA"), meta.get("tier", "AA"))
        days_str   = f"{r['days']}d" if r["days"] > 0 else "today"
        dev        = meta.get("developer", "—")
        pub        = meta.get("publisher", "—")
        credit     = dev if (dev == pub or pub in ("—", "")) else f"{dev} / {pub}"
        tags_str   = meta.get("tags", "—")
        if tags_str == "—":
            tags_str = meta.get("genre", "—")
        lines.append(
            f"**{name}** [{tier_label}] — #{r['first_rank']} → #{r['latest_rank']} "
            f"(+{r['delta']} in {days_str}) | {r['est_wishlists']}"
        )
        lines.append(f"  _{credit} | {tags_str}_")
        lines.append("")

    if not top30:
        lines.append("_(No rank climbers in rank 101-500 yet — check back after more days of data)_")

    lines.append(f"_Data from {len(top500_dates)} captured day(s) · {len(climbers)} climbers / {stable_ct} stable / {faller_ct} fallers_")

    message = "\n".join(lines).rstrip()
    print("\n" + "="*60)
    print(message)
    print("="*60 + "\n")

    send_personal_dm(config, message)

if __name__ == "__main__":
    main()
