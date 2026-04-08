# Nepali Calendar (.ics) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Python scripts that scrape nepalipatro.com.np and generate three subscribable .ics files hosted on GitHub Pages, covering one Bikram Sambat year at a time.

**Architecture:** Playwright renders the 12 monthly calendar pages from nepalipatro.com.np → BeautifulSoup parses events from the DOM (all events are in the HTML, no JS interaction needed) → events are classified into three categories → saved as `data/YYYY.json` → a second script reads the JSON and generates three .ics files into `docs/` → `docs/` is served by GitHub Pages.

**Tech Stack:** Python 3.11+, `playwright` (chromium), `beautifulsoup4`, `icalendar`, `pytest`

---

## Key Facts (discovered during research)

- Site: `nepalipatro.com.np` — a React SPA. Pages require Playwright (JS rendering).
- Monthly calendar URL pattern: `https://nepalipatro.com.np/calendar/bs/YYYY-MM` (e.g. `2083-01` = Baisakh 2083)
- Each day cell in the HTML has `id="date-YYYY-MM-DD"` (BS date) and a nested `<time class="date-value" datetime="YYYY-MM-DD">` (AD date).
- Out-of-month "filler" cells have **no** `id` attribute on the inner div — safe to skip.
- Event `<p>` elements have class `event overflow-hidden np-holiday` (public holiday) or `event overflow-hidden normal-event` (everything else).
- Classification rule: if `'अन्तर्राष्ट्रिय'` or `'विश्व'` is in the name → `international_day`; otherwise → `festival`.
- BS 2083 runs approximately 14 April 2026 – 13 April 2027.

---

## File Map

```
nepali-calendar/
├── scraper/
│   └── scrape.py          # Playwright fetch + BS parse + classify → data/YYYY.json
├── generator/
│   └── generate.py        # data/YYYY.json → docs/*.ics
├── tests/
│   ├── fixtures/
│   │   └── nepalipatro-2082-01.html   # real HTML fixture for offline tests
│   ├── test_scraper.py
│   └── test_generator.py
├── data/                  # committed to repo, human-editable
│   └── .gitkeep
├── docs/                  # GitHub Pages source — serves *.ics files
│   └── .gitkeep
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Task 1: Project skeleton

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `scraper/__init__.py`, `generator/__init__.py`, `tests/__init__.py`
- Create: `tests/fixtures/` directory
- Copy: `.firecrawl/nepalipatro-2082-01.html` → `tests/fixtures/nepalipatro-2082-01.html`

- [ ] **Step 1: Create `requirements.txt`**

```
playwright==1.44.0
beautifulsoup4==4.12.3
icalendar==6.0.0
pytest==8.2.0
lxml==5.2.2
```

- [ ] **Step 2: Create `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.firecrawl/
*.egg-info/
.venv/
```

- [ ] **Step 3: Create empty `__init__.py` files and `data/` + `docs/` directories**

```bash
mkdir -p scraper generator tests/fixtures data docs
touch scraper/__init__.py generator/__init__.py tests/__init__.py data/.gitkeep docs/.gitkeep
```

- [ ] **Step 4: Copy the HTML fixture**

```bash
cp .firecrawl/nepalipatro-2082-01.html tests/fixtures/nepalipatro-2082-01.html
```

- [ ] **Step 5: Install dependencies and Playwright browser**

```bash
pip install -r requirements.txt
playwright install chromium
```

Expected: `playwright install chromium` downloads Chromium (~150 MB) and prints `Chromium ... downloaded`.

- [ ] **Step 6: Commit**

```bash
git init
git add requirements.txt .gitignore scraper/ generator/ tests/ data/.gitkeep docs/.gitkeep
git commit -m "chore: project skeleton"
```

---

## Task 2: `parse_month_html` — extract events from one month's HTML

**Files:**
- Create: `tests/test_scraper.py`
- Create: `scraper/scrape.py` (parse functions only — no network calls yet)

- [ ] **Step 1: Write failing tests**

Create `tests/test_scraper.py`:

```python
import json
import pytest
from pathlib import Path
from scraper.scrape import parse_month_html

FIXTURE = Path("tests/fixtures/nepalipatro-2082-01.html").read_text(encoding="utf-8")


def test_returns_list_of_dicts():
    events = parse_month_html(FIXTURE)
    assert isinstance(events, list)
    assert len(events) > 0
    assert all(isinstance(e, dict) for e in events)


def test_event_has_required_keys():
    events = parse_month_html(FIXTURE)
    required = {"name_ne", "date_ad", "date_bs", "category"}
    for e in events:
        assert required.issubset(e.keys()), f"Missing keys in {e}"


def test_public_holiday_detected():
    events = parse_month_html(FIXTURE)
    holidays = [e for e in events if e["category"] == "public_holiday"]
    names = [e["name_ne"] for e in holidays]
    assert any("नव वर्ष" in n for n in names), f"No New Year in holidays: {names}"


def test_ad_date_format():
    events = parse_month_html(FIXTURE)
    new_year = next(e for e in events if "नव वर्ष" in e["name_ne"])
    assert new_year["date_ad"] == "2025-04-14"


def test_bs_date_format():
    events = parse_month_html(FIXTURE)
    new_year = next(e for e in events if "नव वर्ष" in e["name_ne"])
    assert new_year["date_bs"] == "2082-01-01"


def test_no_empty_event_names():
    events = parse_month_html(FIXTURE)
    assert all(e["name_ne"].strip() for e in events)


def test_categories_are_valid():
    valid = {"public_holiday", "festival", "international_day"}
    events = parse_month_html(FIXTURE)
    for e in events:
        assert e["category"] in valid, f"Invalid category: {e['category']}"


def test_international_day_classified():
    events = parse_month_html(FIXTURE)
    intl = [e for e in events if e["category"] == "international_day"]
    names = [e["name_ne"] for e in intl]
    # "अन्तर्राष्ट्रिय पृथ्वी दिवस" is in month 01
    assert any("पृथ्वी" in n for n in names), f"Earth Day not classified as international: {names}"
```

- [ ] **Step 2: Run tests — verify they all FAIL**

```bash
pytest tests/test_scraper.py -v
```

Expected: `ImportError` or `AttributeError` — `scrape.py` doesn't exist yet.

- [ ] **Step 3: Implement `parse_month_html` and `classify_event` in `scraper/scrape.py`**

```python
from __future__ import annotations
from bs4 import BeautifulSoup


INTERNATIONAL_KEYWORDS = ["अन्तर्राष्ट्रिय", "विश्व"]


def classify_event(name: str) -> str:
    """Return 'international_day' if name contains international keywords, else 'festival'."""
    for kw in INTERNATIONAL_KEYWORDS:
        if kw in name:
            return "international_day"
    return "festival"


def parse_month_html(html: str) -> list[dict]:
    """
    Parse a rendered nepalipatro.com.np/calendar/bs/YYYY-MM page.

    Each day cell has id="date-YYYY-MM-DD" (BS date) and a nested
    <time class="date-value" datetime="YYYY-MM-DD"> (AD date).
    Event <p> elements have class "event overflow-hidden np-holiday"
    (public holidays) or "event overflow-hidden normal-event" (others).
    Out-of-month filler cells have no id on the inner div — skipped automatically.
    """
    soup = BeautifulSoup(html, "lxml")
    events: list[dict] = []

    for date_div in soup.find_all("div", id=lambda x: x and x.startswith("date-")):
        bs_date = date_div["id"].replace("date-", "")  # "2082-01-01"

        time_el = date_div.find("time", class_="date-value")
        if not time_el or not time_el.get("datetime"):
            continue
        ad_date: str = time_el["datetime"]  # "2025-04-14"

        cell = date_div.parent  # the outer .col.cell div
        for p in cell.find_all("p", class_="event"):
            name = p.get_text(strip=True)
            if not name:
                continue
            css_classes = p.get("class", [])
            if "np-holiday" in css_classes:
                category = "public_holiday"
            else:
                category = classify_event(name)
            events.append(
                {
                    "name_ne": name,
                    "date_ad": ad_date,
                    "date_bs": bs_date,
                    "category": category,
                }
            )

    return events
```

- [ ] **Step 4: Run tests — verify they all PASS**

```bash
pytest tests/test_scraper.py -v
```

Expected: `8 passed`.

- [ ] **Step 5: Commit**

```bash
git add scraper/scrape.py tests/test_scraper.py tests/fixtures/nepalipatro-2082-01.html
git commit -m "feat: parse_month_html extracts events from rendered calendar HTML"
```

---

## Task 3: `fetch_month_html` — Playwright fetcher

**Files:**
- Modify: `scraper/scrape.py` — add `fetch_month_html`

- [ ] **Step 1: Write failing test in `tests/test_scraper.py`** (append to file)

```python
from scraper.scrape import fetch_month_html

def test_fetch_month_html_returns_html_string():
    """Live network test — requires internet. Fetches Baisakh 2082 page."""
    html = fetch_month_html(2082, 1)
    assert isinstance(html, str)
    assert 'id="date-2082-01-' in html


def test_fetch_month_html_contains_events():
    html = fetch_month_html(2082, 1)
    events = parse_month_html(html)
    assert len(events) > 10
```

- [ ] **Step 2: Run these two new tests — verify FAIL**

```bash
pytest tests/test_scraper.py::test_fetch_month_html_returns_html_string -v
```

Expected: `ImportError` — `fetch_month_html` not defined yet.

- [ ] **Step 3: Implement `fetch_month_html` in `scraper/scrape.py`** (append to existing file)

```python
from playwright.sync_api import sync_playwright


def fetch_month_html(year: int, month: int) -> str:
    """
    Render https://nepalipatro.com.np/calendar/bs/YYYY-MM with a headless
    Chromium browser and return the page HTML after JS has run.
    """
    url = f"https://nepalipatro.com.np/calendar/bs/{year}-{month:02d}"
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30_000)
        html = page.content()
        browser.close()
    return html
```

- [ ] **Step 4: Run the two network tests**

```bash
pytest tests/test_scraper.py::test_fetch_month_html_returns_html_string tests/test_scraper.py::test_fetch_month_html_contains_events -v
```

Expected: Both PASS. Takes ~10 seconds (Playwright launch + render).

- [ ] **Step 5: Commit**

```bash
git add scraper/scrape.py tests/test_scraper.py
git commit -m "feat: fetch_month_html uses Playwright to render monthly calendar pages"
```

---

## Task 4: Main scraper script — scrape full year → `data/YYYY.json`

**Files:**
- Modify: `scraper/scrape.py` — add `scrape_year` and `__main__` block

- [ ] **Step 1: Write failing test** (append to `tests/test_scraper.py`)

```python
import json
from pathlib import Path
from scraper.scrape import scrape_year

def test_scrape_year_writes_json(tmp_path, monkeypatch):
    """Unit test — monkeypatches fetch_month_html to avoid network calls."""
    import scraper.scrape as m

    fixture_html = Path("tests/fixtures/nepalipatro-2082-01.html").read_text(encoding="utf-8")
    monkeypatch.setattr(m, "fetch_month_html", lambda year, month: fixture_html)

    out_path = tmp_path / "data" / "2082.json"
    out_path.parent.mkdir()
    scrape_year(2082, data_dir=str(tmp_path / "data"))

    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["bs_year"] == 2082
    assert isinstance(data["events"], list)
    assert len(data["events"]) > 0
```

- [ ] **Step 2: Run test — verify FAIL**

```bash
pytest tests/test_scraper.py::test_scrape_year_writes_json -v
```

Expected: `ImportError` — `scrape_year` not defined yet.

- [ ] **Step 3: Implement `scrape_year` and `__main__` block in `scraper/scrape.py`** (append)

```python
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def scrape_year(bs_year: int, data_dir: str = "data") -> None:
    """
    Fetch all 12 monthly pages for the given BS year, parse events,
    deduplicate, and write to data/YYYY.json.
    """
    all_events: list[dict] = []
    seen: set[tuple] = set()  # (date_bs, name_ne) pairs to avoid duplicates

    for month in range(1, 13):
        print(f"  Fetching {bs_year}-{month:02d}...", flush=True)
        html = fetch_month_html(bs_year, month)
        month_events = parse_month_html(html)
        for evt in month_events:
            key = (evt["date_bs"], evt["name_ne"])
            if key not in seen:
                seen.add(key)
                all_events.append(evt)

    # Sort by AD date
    all_events.sort(key=lambda e: e["date_ad"])

    payload = {
        "bs_year": bs_year,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://nepalipatro.com.np",
        "events": all_events,
    }

    out_path = Path(data_dir) / f"{bs_year}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(all_events)} events → {out_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m scraper.scrape <BS_YEAR>")
        sys.exit(1)
    year = int(sys.argv[1])
    print(f"Scraping BS year {year}...")
    scrape_year(year)
    print("Done.")
```

- [ ] **Step 4: Run test — verify PASS**

```bash
pytest tests/test_scraper.py::test_scrape_year_writes_json -v
```

Expected: `1 passed`.

- [ ] **Step 5: Run all scraper tests to make sure nothing regressed**

```bash
pytest tests/test_scraper.py -v -k "not fetch_month_html"
```

Expected: All non-network tests pass.

- [ ] **Step 6: Commit**

```bash
git add scraper/scrape.py tests/test_scraper.py
git commit -m "feat: scrape_year fetches all 12 months and writes data/YYYY.json"
```

---

## Task 5: ICS generator — `data/YYYY.json` → `docs/*.ics`

**Files:**
- Create: `tests/test_generator.py`
- Create: `tests/fixtures/sample-2083.json`
- Create: `generator/generate.py`

- [ ] **Step 1: Create fixture JSON `tests/fixtures/sample-2083.json`**

```json
{
  "bs_year": 2083,
  "generated_at": "2026-04-14T00:00:00+00:00",
  "source": "https://nepalipatro.com.np",
  "events": [
    {
      "name_ne": "नव वर्ष २०८३",
      "date_ad": "2026-04-14",
      "date_bs": "2083-01-01",
      "category": "public_holiday"
    },
    {
      "name_ne": "मातातीर्थ औंसी - आमाको मुख हेर्ने",
      "date_ad": "2026-04-17",
      "date_bs": "2083-01-04",
      "category": "festival"
    },
    {
      "name_ne": "विश्व सम्पदा दिवस",
      "date_ad": "2026-04-18",
      "date_bs": "2083-01-05",
      "category": "international_day"
    }
  ]
}
```

- [ ] **Step 2: Write failing tests in `tests/test_generator.py`**

```python
import json
from pathlib import Path
from icalendar import Calendar
from generator.generate import generate_ics, write_ics_files

FIXTURE_JSON = Path("tests/fixtures/sample-2083.json").read_text(encoding="utf-8")
DATA = json.loads(FIXTURE_JSON)


def _parse_cal(ics_bytes: bytes) -> Calendar:
    return Calendar.from_ical(ics_bytes)


def test_generate_ics_public_holidays_only():
    ics = generate_ics(DATA["events"], categories=["public_holiday"])
    cal = _parse_cal(ics)
    summaries = [str(c.get("SUMMARY")) for c in cal.walk() if c.name == "VEVENT"]
    assert "นว वर्ष २०८३" in summaries or any("नव वर्ष" in s for s in summaries)
    assert not any("मातातीर्थ" in s for s in summaries)
    assert not any("विश्व सम्पदा" in s for s in summaries)


def test_generate_ics_primary_events():
    ics = generate_ics(DATA["events"], categories=["public_holiday", "festival"])
    cal = _parse_cal(ics)
    summaries = [str(c.get("SUMMARY")) for c in cal.walk() if c.name == "VEVENT"]
    assert any("नव वर्ष" in s for s in summaries)
    assert any("मातातीर्थ" in s for s in summaries)
    assert not any("विश्व सम्पदा" in s for s in summaries)


def test_generate_ics_all_events():
    ics = generate_ics(DATA["events"], categories=["public_holiday", "festival", "international_day"])
    cal = _parse_cal(ics)
    summaries = [str(c.get("SUMMARY")) for c in cal.walk() if c.name == "VEVENT"]
    assert any("नव वर्ष" in s for s in summaries)
    assert any("मातातीर्थ" in s for s in summaries)
    assert any("विश्व सम्पदा" in s for s in summaries)


def test_events_are_all_day():
    ics = generate_ics(DATA["events"], categories=["public_holiday"])
    cal = _parse_cal(ics)
    for component in cal.walk():
        if component.name == "VEVENT":
            dtstart = component.get("DTSTART")
            # All-day events use DATE not DATETIME
            assert dtstart.params.get("VALUE") == "DATE" or hasattr(dtstart.dt, "date") and not hasattr(dtstart.dt, "hour")


def test_uids_are_unique():
    ics = generate_ics(DATA["events"], categories=["public_holiday", "festival", "international_day"])
    cal = _parse_cal(ics)
    uids = [str(c.get("UID")) for c in cal.walk() if c.name == "VEVENT"]
    assert len(uids) == len(set(uids))


def test_write_ics_files_creates_three_files(tmp_path):
    write_ics_files(DATA, docs_dir=str(tmp_path))
    assert (tmp_path / "public-holidays.ics").exists()
    assert (tmp_path / "primary-events.ics").exists()
    assert (tmp_path / "all.ics").exists()
```

- [ ] **Step 3: Run tests — verify FAIL**

```bash
pytest tests/test_generator.py -v
```

Expected: `ImportError` — `generate.py` not created yet.

- [ ] **Step 4: Implement `generator/generate.py`**

```python
from __future__ import annotations
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from icalendar import Calendar, Event


CALENDAR_NAMES = {
    ("public_holiday",): "Nepali Public Holidays",
    ("public_holiday", "festival"): "Nepali Public Holidays & Festivals",
    ("public_holiday", "festival", "international_day"): "Nepali Calendar - All Events",
}

OUTPUT_FILES = [
    ("public-holidays.ics", ["public_holiday"]),
    ("primary-events.ics", ["public_holiday", "festival"]),
    ("all.ics", ["public_holiday", "festival", "international_day"]),
]


def _make_uid(event: dict) -> str:
    h = hashlib.md5(event["name_ne"].encode()).hexdigest()[:8]
    return f"{event['date_ad']}-{h}@nepali-calendar"


def generate_ics(events: list[dict], categories: list[str]) -> bytes:
    """Return .ics bytes for events whose category is in `categories`."""
    cal = Calendar()
    cal.add("prodid", "-//Nepali Calendar//nepali-calendar//EN")
    cal.add("version", "2.0")
    cal_name = CALENDAR_NAMES.get(tuple(categories), "Nepali Calendar")
    cal.add("x-wr-calname", cal_name)
    cal.add("x-wr-caldesc", f"Nepali calendar events sourced from nepalipatro.com.np")

    category_set = set(categories)
    for evt in events:
        if evt["category"] not in category_set:
            continue
        year, month, day = map(int, evt["date_ad"].split("-"))
        vevent = Event()
        vevent.add("summary", evt["name_ne"])
        vevent.add("dtstart", date(year, month, day))
        vevent.add("uid", _make_uid(evt))
        vevent.add("dtstamp", datetime.now(timezone.utc))
        cal.add_component(vevent)

    return cal.to_ical()


def write_ics_files(data: dict, docs_dir: str = "docs") -> None:
    """Write the three .ics files into docs_dir."""
    out = Path(docs_dir)
    out.mkdir(parents=True, exist_ok=True)
    for filename, categories in OUTPUT_FILES:
        ics_bytes = generate_ics(data["events"], categories)
        (out / filename).write_bytes(ics_bytes)
        count = sum(1 for e in data["events"] if e["category"] in categories)
        print(f"  {filename}: {count} events")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m generator.generate <BS_YEAR>")
        sys.exit(1)
    year = int(sys.argv[1])
    json_path = Path("data") / f"{year}.json"
    if not json_path.exists():
        print(f"Error: {json_path} not found. Run scraper first.")
        sys.exit(1)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    print(f"Generating .ics files for BS {year}...")
    write_ics_files(data)
    print("Done. Files written to docs/")
```

- [ ] **Step 5: Run all generator tests — verify PASS**

```bash
pytest tests/test_generator.py -v
```

Expected: `6 passed`.

- [ ] **Step 6: Run the complete test suite**

```bash
pytest tests/ -v -k "not fetch_month_html"
```

Expected: All non-network tests pass.

- [ ] **Step 7: Commit**

```bash
git add generator/generate.py tests/test_generator.py tests/fixtures/sample-2083.json
git commit -m "feat: generate.py produces public-holidays.ics, primary-events.ics, all.ics"
```

---

## Task 6: End-to-end run for BS 2083 + verification

- [ ] **Step 1: Scrape BS 2083 (live run — takes ~2-3 minutes)**

```bash
python -m scraper.scrape 2083
```

Expected output:
```
Scraping BS year 2083...
  Fetching 2083-01...
  Fetching 2083-02...
  ...
  Fetching 2083-12...
Wrote NNN events → data/2083.json
Done.
```

- [ ] **Step 2: Spot-check `data/2083.json`**

```bash
python3 -c "
import json
data = json.load(open('data/2083.json', encoding='utf-8'))
print('Total events:', len(data['events']))
cats = {}
for e in data['events']:
    cats[e['category']] = cats.get(e['category'], 0) + 1
print('Categories:', cats)
print('First 5 events:')
for e in data['events'][:5]:
    print(f'  [{e[\"category\"]}] {e[\"date_ad\"]} — {e[\"name_ne\"]}')
"
```

Expected: 200–400 total events, `public_holiday` count 30–60, events start from ~2026-04-14.

- [ ] **Step 3: Generate .ics files**

```bash
python -m generator.generate 2083
```

Expected:
```
Generating .ics files for BS 2083...
  public-holidays.ics: NN events
  primary-events.ics: NNN events
  all.ics: NNN events
Done. Files written to docs/
```

- [ ] **Step 4: Validate each .ics file is parseable**

```bash
python3 -c "
from icalendar import Calendar
from pathlib import Path
for f in ['public-holidays.ics', 'primary-events.ics', 'all.ics']:
    cal = Calendar.from_ical((Path('docs') / f).read_bytes())
    events = [c for c in cal.walk() if c.name == 'VEVENT']
    print(f'{f}: {len(events)} events — OK')
"
```

- [ ] **Step 5: Manually import one .ics into a calendar app to verify it looks right**

Open Outlook/Google Calendar → Settings → Subscribe from URL → use a local file path or a temporary hosting. Verify event names show in Nepali, dates are correct, events are all-day.

- [ ] **Step 6: Commit data and output**

```bash
git add data/2083.json docs/
git commit -m "data: add BS 2083 scraped events and generated .ics files"
```

---

## Task 7: GitHub repo + Pages setup + README

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
# Nepali Calendar for Outlook / Google Calendar / Apple Calendar

Subscribable .ics calendar files covering Nepali public holidays, festivals, and
international days observed in Nepal — sourced from nepalipatro.com.np.

## Subscribe

Add these URLs in your calendar app (Outlook: Add calendar → Subscribe from web):

| Calendar | URL |
|---|---|
| Public Holidays only | `https://YOUR_USERNAME.github.io/nepali-calendar/public-holidays.ics` |
| Holidays + Festivals | `https://YOUR_USERNAME.github.io/nepali-calendar/primary-events.ics` |
| Everything | `https://YOUR_USERNAME.github.io/nepali-calendar/all.ics` |

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

# 4. Commit and push → GitHub Pages auto-serves the updated files
git add data/2084.json docs/
git commit -m "data: add BS 2084 events"
git push
```

## Data source

[nepalipatro.com.np](https://nepalipatro.com.np) — scraped once per BS year around Baisakh 1 (mid-April).
```

- [ ] **Step 2: Create a GitHub repository**

Go to github.com → New repository → name it `nepali-calendar` → public → no README (we have one).

- [ ] **Step 3: Push to GitHub**

```bash
git remote add origin https://github.com/YOUR_USERNAME/nepali-calendar.git
git branch -M main
git push -u origin main
```

- [ ] **Step 4: Enable GitHub Pages**

GitHub repo → Settings → Pages → Source: **Deploy from a branch** → Branch: `main` → Folder: `/docs` → Save.

Wait ~1 minute, then visit `https://YOUR_USERNAME.github.io/nepali-calendar/public-holidays.ics` — browser should download the file.

- [ ] **Step 5: Update README with real URLs (replace `YOUR_USERNAME`)**

Edit `README.md` — replace `YOUR_USERNAME` with your actual GitHub username.

```bash
git add README.md
git commit -m "docs: add real GitHub Pages URLs to README"
git push
```

- [ ] **Step 6: Test the live subscription URL in Outlook**

Outlook → Add Calendar → Subscribe from Web → paste the live URL → verify events appear.

---

## Self-Review

**Spec coverage:**
- ✅ Three .ics files (public-holidays, primary-events, all)
- ✅ Hosted on GitHub Pages
- ✅ Subscribable via URL in Outlook/Google/Apple Calendar
- ✅ Events sourced from nepalipatro.com.np with category grouping
- ✅ Manual run in April each year
- ✅ Human-editable intermediate JSON in `data/`
- ✅ README documents the annual update process

**Placeholder scan:** None found — all steps include actual code or commands.

**Type consistency:** `parse_month_html` → `list[dict]`, `scrape_year` → writes JSON, `generate_ics` → `bytes`, `write_ics_files` → writes files. Consistent throughout.

**Scope:** Appropriately sized for a single implementation session.
