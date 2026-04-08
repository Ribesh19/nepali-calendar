# Nepali Calendar for Outlook / Google Calendar / Apple Calendar

Subscribable .ics calendar files for Nepali public holidays, festivals, and cultural events — sourced from [nepalipatro.com.np](https://nepalipatro.com.np) and cross-referenced with [Wikipedia's Nepal public holidays list](https://en.wikipedia.org/wiki/Public_holidays_in_Nepal).

All event names are in **English**. Covers one Bikram Sambat year at a time (currently BS 2083: April 2026 – April 2027).

---

## Subscribe

Add one of these URLs in your calendar app:

- **Outlook:** Add Calendar → Subscribe from web → paste URL
- **Google Calendar:** Other calendars (+) → From URL → paste URL
- **Apple Calendar:** File → New Calendar Subscription → paste URL

| Calendar | URL | Events |
|---|---|---|
| Public Holidays | `https://Ribesh19.github.io/nepali-calendar/public-holidays.ics` | 40 |
| Festival Holidays | `https://Ribesh19.github.io/nepali-calendar/festival-holidays.ics` | 42 |
| Everything | `https://Ribesh19.github.io/nepali-calendar/all.ics` | 247 |

---

## What's in each file?

### public-holidays.ics — 40 events
Official Nepali government public holidays (सार्वजनिक बिदाहरू) — days when government offices, banks, and schools are closed. Includes:
- Major festivals: Dashain, Tihar, Holi, Maha Shivaratri, Buddha Jayanti
- National days: Republic Day, Constitution Day, Democracy Day, Martyrs' Day, Women's Day
- Community-specific holidays: Lhosar (Tamang, Gurung, Gyalpo), Chhath Parwa, Udhauli/Ubhauli, Christmas

### festival-holidays.ics — 42 events
Everything in public-holidays.ics **plus** festival holidays recognised by Wikipedia's Nepal public holidays list that are not already official public holidays:
- **Eid al-Adha (Bakr Eid)** — observed by Muslim community
- **Indra Jatra (Swanchhya)** — Kathmandu Valley's major chariot festival

### all.ics — 247 events
Everything above **plus** optional/cultural observances and international days:
- Optional cultural events: Mother's Day (Mata Tirtha Aunsi), Father's Day (Kushe Aunsi), Nag Panchami, Guru Purnima, Teej Eve (Dar Khane), Gai Tihar eve events, Dhanteras, and many more
- Jatras and local festivals: Bisket Jatra, Indrayani Jatra, Matsyendranath Rath Jatra, and others
- International days observed in Nepal: World Health Day, World Environment Day, World Human Rights Day, etc.

---

## Updating for a New BS Year (run in April each year)

Requirements: Python 3.11+, Playwright Chromium

```bash
# Install dependencies (first time only)
pip install -r requirements.txt
playwright install chromium

# 1. Scrape the new BS year (replace 2084 with the current BS year)
python -m scraper.scrape 2084

# 2. Run the enrichment script to add English names and fix categories
#    (update the year in the script filename/path as needed)
python scripts/enrich_2083.py   # copy and adapt for the new year

# 3. Review data/2084.json — edit manually if anything looks wrong

# 4. Generate .ics files
python -m generator.generate 2084

# 5. Commit and push — GitHub Pages auto-serves the updated files
git add data/2084.json docs/
git commit -m "data: add BS 2084 events"
git push
```

---

## How It Works

1. **Scraper** (`scraper/scrape.py`) — Playwright renders nepalipatro.com.np calendar pages (JavaScript SPA), BeautifulSoup extracts events with both BS and AD dates
2. **Enrichment** (`scripts/enrich_2083.py`) — Adds English event names and re-categorises events using Wikipedia's Nepal public holidays classification
3. **Generator** (`generator/generate.py`) — Reads `data/YYYY.json` and produces RFC 5545-compliant .ics files
4. **GitHub Pages** — Serves `.ics` files from the `/docs` folder at `Ribesh19.github.io/nepali-calendar/`

## Category Reference

| Category | Wikipedia term | In which .ics |
|---|---|---|
| `public_holiday` | Public Holidays + Festival Holidays (official) | All three files |
| `festival` | Festival Holidays (non-official) + key Optional holidays | festival-holidays.ics, all.ics |
| `optional_holiday` | Optional Holidays + cultural observances | all.ics only |
| `international_day` | International days observed in Nepal | all.ics only |

## Data Source

[nepalipatro.com.np](https://nepalipatro.com.np) — scraped once per BS year around Baisakh 1 (mid April). Event categorisation cross-referenced with [Wikipedia](https://en.wikipedia.org/wiki/Public_holidays_in_Nepal).
