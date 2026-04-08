from pathlib import Path
from scraper.scrape import parse_month_html, classify_event

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


def test_classify_event_returns_festival_by_default():
    """By default, classify_event returns 'festival'."""
    assert classify_event("कोई सामान्य घटना") == "festival"


def test_classify_event_identifies_international_with_aantrik():
    """Detects 'अन्तर्राष्ट्रिय' keyword as international_day."""
    assert classify_event("अन्तर्राष्ट्रिय महिला दिवस") == "international_day"


def test_classify_event_identifies_international_with_world():
    """Detects 'विश्व' keyword as international_day."""
    assert classify_event("विश्व स्वास्थ्य दिवस") == "international_day"


def test_classify_event_handles_both_keywords():
    """Should match if EITHER keyword exists."""
    assert classify_event("some विश्व text") == "international_day"


def test_parse_month_html_with_empty_html():
    """Empty or minimal HTML should return empty list, not crash."""
    empty_result = parse_month_html("")
    assert empty_result == []


def test_parse_month_html_with_missing_structure():
    """HTML missing expected elements should gracefully skip them."""
    minimal = '<html><body><div id="date-2082-01-01"></div></body></html>'
    result = parse_month_html(minimal)
    # Should not crash; behavior is OK if empty or partial
    assert isinstance(result, list)


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
