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
    # Uses name_en as summary
    assert any("Nepali New Year" in s for s in summaries)
    assert not any("Eid" in s for s in summaries)
    assert not any("Mother" in s for s in summaries)
    assert not any("Heritage" in s for s in summaries)


def test_generate_ics_festival_holidays():
    """Festival holidays = public holidays + Wikipedia festival events (Eid etc.)."""
    ics = generate_ics(DATA["events"], categories=["public_holiday", "festival"])
    cal = _parse_cal(ics)
    summaries = [str(c.get("SUMMARY")) for c in cal.walk() if c.name == "VEVENT"]
    assert any("Nepali New Year" in s for s in summaries)
    assert any("Eid" in s for s in summaries)
    # optional_holiday and international_day not included
    assert not any("Mother" in s for s in summaries)
    assert not any("Heritage" in s for s in summaries)


def test_generate_ics_all_events():
    ics = generate_ics(
        DATA["events"],
        categories=["public_holiday", "festival", "optional_holiday", "international_day"],
    )
    cal = _parse_cal(ics)
    summaries = [str(c.get("SUMMARY")) for c in cal.walk() if c.name == "VEVENT"]
    assert any("Nepali New Year" in s for s in summaries)
    assert any("Eid" in s for s in summaries)
    assert any("Mother" in s for s in summaries)
    assert any("Heritage" in s for s in summaries)


def test_events_are_all_day():
    ics = generate_ics(DATA["events"], categories=["public_holiday"])
    cal = _parse_cal(ics)
    for component in cal.walk():
        if component.name == "VEVENT":
            dtstart = component.get("DTSTART")
            assert dtstart.params.get("VALUE") == "DATE"


def test_uids_are_unique():
    ics = generate_ics(
        DATA["events"],
        categories=["public_holiday", "festival", "optional_holiday", "international_day"],
    )
    cal = _parse_cal(ics)
    uids = [str(c.get("UID")) for c in cal.walk() if c.name == "VEVENT"]
    assert len(uids) == len(set(uids))


def test_write_ics_files_creates_three_files(tmp_path):
    write_ics_files(DATA, docs_dir=str(tmp_path))
    assert (tmp_path / "public-holidays.ics").exists()
    assert (tmp_path / "festival-holidays.ics").exists()
    assert (tmp_path / "all.ics").exists()


def test_summary_uses_english_name():
    """SUMMARY field in .ics should be name_en, not name_ne."""
    ics = generate_ics(DATA["events"], categories=["public_holiday"])
    cal = _parse_cal(ics)
    summaries = [str(c.get("SUMMARY")) for c in cal.walk() if c.name == "VEVENT"]
    # English name should be present
    assert any("Nepali New Year" in s for s in summaries)
    # Nepali script should NOT be in summaries (since name_en is provided)
    assert not any("\u0928\u0935 \u0935\u0930\u094d\u0937" in s for s in summaries)
