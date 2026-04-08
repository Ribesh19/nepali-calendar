# Nepali Calendar for Outlook / Google Calendar / Apple Calendar

Subscribable .ics calendar files covering Nepali public holidays, festivals, and international days observed in Nepal — sourced from [nepalipatro.com.np](https://nepalipatro.com.np).

## Subscribe

Add these URLs in your calendar app (Outlook: Add calendar → Subscribe from web):

| Calendar | URL |
|---|---|
| Public holidays only | `https://Ribesh19.github.io/nepali-calendar/public-holidays.ics` |
| Holidays + Festivals | `https://Ribesh19.github.io/nepali-calendar/primary-events.ics` |
| Everything | `https://Ribesh19.github.io/nepali-calendar/all.ics` |

## Event Categories

- **public-holidays.ics** — Official Nepal government public holidays (सार्वजनिक बिदाहरू)
- **primary-events.ics** — Above + Nepali festivals (चाडपर्व) including Dashain, Tihar, Teej, Mother's Day, Father's Day
- **all.ics** — Above + international days observed in Nepal (अन्तराष्ट्रिय दिवस)

## Updating for a New BS Year (run in April each year)

Requirements: Python 3.11+, Playwright Chromium

```bash
# Install dependencies (first time only)
pip install -r requirements.txt
playwright install chromium

# 1. Scrape the new BS year (replace 2084 with the current year)
python -m scraper.scrape 2084

# 2. Review data/2084.json — edit manually if anything looks wrong

# 3. Generate .ics files
python -m generator.generate 2084

# 4. Commit and push — GitHub Pages auto-serves the updated files
git add data/2084.json docs/
git commit -m "data: add BS 2084 events"
git push
```

## How It Works

1. **Scraper** (`scraper/scrape.py`) — Uses Playwright to render the nepalipatro.com.np calendar pages, parses event data with BeautifulSoup
2. **Generator** (`generator/generate.py`) — Reads the JSON data and produces RFC 5545-compliant .ics files
3. **GitHub Pages** — Serves the `.ics` files from the `/docs` folder for easy calendar subscription

## Data Source

[nepalipatro.com.np](https://nepalipatro.com.np) — scraped once per BS year around Baisakh 1 (mid April).
