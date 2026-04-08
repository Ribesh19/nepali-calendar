from __future__ import annotations
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

from icalendar import Calendar, Event


CALENDAR_NAMES = {
    ("public_holiday",): "Nepali Public Holidays",
    ("public_holiday", "festival"): "Nepali Public Holidays & Festival Holidays",
    ("public_holiday", "festival", "optional_holiday", "international_day"): "Nepali Calendar - All Events",
}

OUTPUT_FILES = [
    ("public-holidays.ics", ["public_holiday"]),
    ("festival-holidays.ics", ["public_holiday", "festival"]),
    ("all.ics", ["public_holiday", "festival", "optional_holiday", "international_day"]),
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
    cal.add("x-wr-caldesc", "Nepali calendar events sourced from nepalipatro.com.np")

    # Hint to calendar clients: refresh once per day, deliver full file
    cal.add("refresh-interval;value=duration", "P1D")
    cal.add("x-published-ttl", "P1D")

    category_set = set(categories)
    for event in events:
        if event["category"] not in category_set:
            continue
        year, month, day = map(int, event["date_ad"].split("-"))
        vevent = Event()
        vevent.add("summary", event.get("name_en") or event["name_ne"])
        vevent.add("dtstart", date(year, month, day))
        vevent.add("uid", _make_uid(event))
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

    try:
        year = int(sys.argv[1])
    except ValueError:
        print(f"Error: BS year must be an integer. Got: {sys.argv[1]}")
        sys.exit(1)

    json_path = Path("data") / f"{year}.json"
    if not json_path.exists():
        print(f"Error: {json_path} not found. Run scraper first.")
        sys.exit(1)
    data = json.loads(json_path.read_text(encoding="utf-8"))
    print(f"Generating .ics files for BS {year}...")
    write_ics_files(data)
    print("Done. Files written to docs/")
