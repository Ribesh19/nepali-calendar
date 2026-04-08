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
