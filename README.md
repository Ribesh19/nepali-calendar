# Nepali Calendar for Outlook / Google Calendar / Apple Calendar

Subscribable .ics calendar files for Nepali public holidays, festivals, and cultural events — sourced from [nepalipatro.com.np](https://nepalipatro.com.np) and cross-referenced with [Wikipedia's Nepal public holidays list](https://en.wikipedia.org/wiki/Public_holidays_in_Nepal).

All event names are in **English**. Covers BS 2083 in full: **14 April 2026 – 13 April 2027**.

---

## Subscription URLs

| Calendar | URL | Events |
|---|---|---|
| Public Holidays | `https://Ribesh19.github.io/nepali-calendar/public-holidays.ics` | 40 |
| Festival Holidays | `https://Ribesh19.github.io/nepali-calendar/festival-holidays.ics` | 47 |
| Everything | `https://Ribesh19.github.io/nepali-calendar/all.ics` | 247 |

---

## How to Subscribe

### Outlook (Desktop — recommended for full year view)

1. Open Calendar → click **Add Calendar** (left sidebar)
2. Select **Subscribe from web**
3. Paste the URL → click **Import**
4. The full year of events loads immediately

> **If Outlook only shows events for a few months:** Right-click the subscribed calendar in the left panel → **Calendar Properties** → increase the "Download appointments for the past/future" range, or switch to **Outlook Desktop** (classic) which handles subscriptions better than the web version.

### Google Calendar

1. On the left sidebar, click **+** next to "Other calendars"
2. Select **From URL**
3. Paste the URL → click **Add calendar**

> **Note:** Google Calendar re-fetches subscribed calendars roughly every **24 hours**. You cannot force an immediate refresh. All events for the full year (Apr 2026 – Apr 2027) are in the file and will appear once synced.

### Apple Calendar (iPhone / iPad)

1. Open **Settings** → **Calendar** → **Accounts**
2. Tap **Add Account** → **Other**
3. Tap **Add Subscribed Calendar**
4. Paste the URL → tap **Next** → **Save**

### Apple Calendar (Mac)

1. Open Calendar → **File** → **New Calendar Subscription**
2. Paste the URL → click **Subscribe**
3. Set **Auto-refresh** to "Every day" → click **OK**

---

## What's in each file?

### public-holidays.ics — 40 events
Official Nepali government public holidays (सार्वजनिक बिदाहरू) — days when government offices, banks, and schools are closed. Includes:
- Major festivals: Dashain (8 days), Tihar (5 days), Holi, Maha Shivaratri, Buddha Jayanti, Raksha Bandhan, Krishna Janmashtami, Teej, Chhath Parwa
- National days: Republic Day, Constitution Day, Democracy Day, Martyrs' Day, International Women's Day
- Community holidays: Lhosar (Tamang, Gurung, Gyalpo), Udhauli/Ubhauli (Kirat), Christmas, Guru Nanak Jayanti

### festival-holidays.ics — 47 events
Everything in public-holidays.ics **plus** major festivals from Wikipedia's Nepal Festival Holidays list and notable community celebrations:
- Eid al-Adha (Bakr Eid)
- Indra Jatra (Swanchhya) — Kathmandu Valley chariot festival
- Additional festivals from the Newari, Kirat, and other community calendars

### all.ics — 247 events
Everything above **plus**:
- **Optional cultural events:** Mother's Day (Mata Tirtha Aunsi), Father's Day (Kushe Aunsi), Nag Panchami, Guru Purnima, Teej Eve feast, Dhanteras, Gopastami, and many more
- **Local jatras and fairs:** Bisket Jatra, Indrayani Jatra, Matsyendranath Rath Jatra, Jagannath Rath Jatra, and others
- **Fasting days (vrats):** Ekadashi, Pradosh, and other observance days
- **International days observed in Nepal:** World Health Day, World Environment Day, World Human Rights Day, and 49 others

---

## Category Reference

| Category | What it means | Files |
|---|---|---|
| `public_holiday` | Official government public holidays | All three |
| `festival` | Wikipedia Festival Holidays (non-official) + notable exceptions | festival-holidays.ics, all.ics |
| `optional_holiday` | Cultural observances, local jatras, fasting days, civic days | all.ics only |
| `international_day` | International days observed in Nepal | all.ics only |

---

## Updating for a New BS Year (run in April each year)

Requirements: Python 3.11+, Playwright Chromium

```bash
# Install dependencies (first time only)
pip install -r requirements.txt
playwright install chromium

# 1. Scrape the new BS year
python -m scraper.scrape 2084

# 2. Copy and adapt the enrichment script for the new year, then run it
#    to add English names and fix categories
python scripts/enrich_2083.py   # adapt year references inside the script

# 3. Review data/2084.json — edit manually if anything looks wrong

# 4. Generate .ics files
python -m generator.generate 2084

# 5. Commit and push — GitHub Pages serves the updated files automatically
git add data/2084.json docs/
git commit -m "data: add BS 2084 events"
git push
```

---

## How It Works

1. **Scraper** (`scraper/scrape.py`) — Playwright renders nepalipatro.com.np calendar pages (a JavaScript SPA), BeautifulSoup extracts all events with both BS and AD dates
2. **Enrichment** (`scripts/enrich_2083.py`) — Adds English names and re-categorises events using Wikipedia's Nepal public holidays classification
3. **Generator** (`generator/generate.py`) — Reads `data/YYYY.json` and produces RFC 5545-compliant .ics files with a 24-hour refresh hint
4. **GitHub Pages** — Serves `.ics` files from `/docs` at `Ribesh19.github.io/nepali-calendar/`

## Data Source

[nepalipatro.com.np](https://nepalipatro.com.np) — scraped once per BS year around Baisakh 1 (mid April). Categorisation cross-referenced with [Wikipedia](https://en.wikipedia.org/wiki/Public_holidays_in_Nepal).
