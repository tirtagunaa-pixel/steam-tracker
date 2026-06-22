# Wishlist Weekly Update Workflow

Tracks the Steam Wishlist chart daily, generates an AI-analysed weekly summary, and sends it to Seatalk every Monday.

---

## How It Works

**Daily (08:00 every day)**
- Fetches today's Top 15 most-wishlisted upcoming games on Steam
- Appends one row per game to the **Wishlist History** Google Sheet tab
- No notification sent — pure data capture

**Weekly (Monday 09:00)**
- Reads the previous Mon–Sun from Wishlist History
- Computes which games held Top 5 / Top 10 positions on 5+ of 7 days
- Identifies new entrants and games that dropped out
- Calls Compass Claude API to generate a trend commentary drawing on all prior weeks
- Appends a summary row to the **Weekly Wishlist Summary** tab
- Sends a formatted Markdown report to your Seatalk group via Pawon webhook

---

## One-time Setup

### 1. Fill in `scripts/watch_config.json`
Two fields need to be filled before first use:

```json
"pawon_webhook_url": "https://pawon.garena.co.id/webhook/<your-webhook-id>",
"seatalk_group_id":  "your_seatalk_group_id"
```

**Getting the Pawon webhook URL:**
1. Log in to `pawon.garena.co.id`
2. Create a new workflow with a **Webhook** trigger node
3. Add an **HTTP Request** node that POSTs to `https://openapi.seatalk.io/messaging/v2/group_chat`
   - Header: `Authorization: Bearer {{ $vars.SEATALK_ACCESS_TOKEN }}`
   - Body: `{ "group_id": "{{ $json.group_id }}", "message": { "tag": "text", "text": { "format": 1, "content": "{{ $json.message }}" } } }`
4. Copy the webhook URL from the Webhook node — paste it into `watch_config.json`

**Getting the Seatalk group_id:**
- Either check the `bot_added_to_group_chat` event payload after adding the bot to your group
- Or call `GET https://openapi.seatalk.io/messaging/v2/group_chat/joined` with your bot's access token

### 2. Set up Windows Task Scheduler

**Daily capture task:**
1. Open Task Scheduler → Create Basic Task
2. Name: `Steam Wishlist Daily Capture`
3. Trigger: **Daily** → 08:00
4. Action: Start a program → `C:\Users\IDG2601\Documents\Claude Agents\scripts\run_wishlist_daily.bat`

**Weekly report task:**
1. Open Task Scheduler → Create Basic Task
2. Name: `Steam Wishlist Weekly Report`
3. Trigger: **Weekly** → Monday → 09:00
4. Action: Start a program → `C:\Users\IDG2601\Documents\Claude Agents\scripts\run_wishlist_weekly.bat`

---

## Running Manually

```powershell
cd "C:\Users\IDG2601\Documents\Claude Agents"

# Capture today's chart (no Seatalk send):
python scripts\steam_wishlist_tracker.py --mode daily

# Generate weekly report and send to Seatalk:
python scripts\steam_wishlist_tracker.py --mode weekly

# Preview either mode without writing or sending:
python scripts\steam_wishlist_tracker.py --mode daily --dry-run
python scripts\steam_wishlist_tracker.py --mode weekly --dry-run
```

---

## Google Sheet Tabs

| Tab | Purpose |
|---|---|
| **Wishlist History** | Raw daily snapshots — one row per game per day |
| **Weekly Wishlist Summary** | One row per week with AI trend commentary |

**Wishlist History columns:**
`Date | Rank | Game Name | AppID | Developer | Genre | Release Date | SteamSpy Owners Est.`

**Weekly Wishlist Summary columns:**
`Week # | Week Start | Week End | Top 5 Stable | Top 10 Stable | New Entrants | Exits | End-of-Week Owners | AI Commentary`

---

## Seatalk Message Format

```
📊 Steam Wishlist Chart — Week XX (Jun 09–Jun 15, 2026)

🏆 Top 5 (stable — appeared in Top 5 on 5+ days)
1. Game A — ~500,000-1,000,000 owners — 7/7 days | #1→#1
2. Game B — ~200,000-500,000 owners — 6/7 days | #2→#3
...

📈 Top 10 Roundup
Game F, Game G, Game H

🆕 New This Week
• Game K (entered at #8)

📉 Dropped Out
• Game L

🤖 Trend Analysis
[AI-generated paragraph from Compass Claude API, drawing on all prior weeks]
```

---

## Notes on Wishlist Count Data

- Steam does not expose raw wishlist counts via public API
- **SteamSpy Owners Est.** is a range estimate of game *owners* (post-launch), not raw wishlists
- For unreleased upcoming games this field will often show `—` or `0-20,000`
- Rank position (1–15) is the primary reliable signal; owners est. is supplementary

---

## Quality Checklist (after weekly run)

- [ ] Wishlist History tab has today's date rows at bottom
- [ ] Weekly Wishlist Summary has a new row for the completed week
- [ ] Seatalk group received the formatted message
- [ ] `output/wishlist_tracker_log.txt` shows no error lines
- [ ] AI Commentary in Summary tab reads coherently and references prior weeks
