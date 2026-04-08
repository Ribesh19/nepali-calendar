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
    assert any("नव वर्ष" in s for s in summaries)
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
            assert dtstart.params.get("VALUE") == "DATE"


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
