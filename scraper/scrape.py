from __future__ import annotations
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


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
    # lxml parser: faster than html.parser, handles malformed HTML better
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
