#!/usr/bin/env python3
"""
One-time enrichment script for data/2083.json.

Adds name_en and re-categorises events based on Wikipedia's Nepal Public Holidays page:
  public_holiday    → unchanged (nepalipatro's "सार्वजनिक बिदाहरू")
  festival          → only events matching Wikipedia's Festival Holidays table
                      + 5 user-specified exceptions from Wikipedia's Optional list
  optional_holiday  → everything else formerly in "festival"
  international_day → unchanged

Run from repo root:
    python scripts/enrich_2083.py
"""

import json
from pathlib import Path

# ── Date-based overrides ──────────────────────────────────────────────────────
# Maps "YYYY-MM-DD" → (name_en, category)
# Priority: date overrides always win over keyword matching.
DATE_MAP: dict[str, tuple[str, str]] = {

    # ── PUBLIC HOLIDAYS (40 events – keep category, supply English name) ─────
    "2026-04-14": ("Nepali New Year 2083", "public_holiday"),
    "2026-05-01": ("Buddha Jayanti", "public_holiday"),
    "2026-05-29": ("Republic Day", "public_holiday"),
    "2026-08-28": ("Raksha Bandhan", "public_holiday"),
    "2026-08-29": ("Gai Jatra (Saparu)", "public_holiday"),
    "2026-09-04": ("Krishna Janmashtami", "public_holiday"),
    "2026-09-14": ("Teej (Haritalika Teej)", "public_holiday"),
    "2026-09-19": ("Constitution Day", "public_holiday"),
    "2026-10-04": ("Jitiya Parwa", "public_holiday"),
    "2026-10-11": ("Ghatasthapana (Dashain Begins)", "public_holiday"),
    "2026-10-17": ("Fulpati", "public_holiday"),
    "2026-10-18": ("Maha Asthami", "public_holiday"),
    "2026-10-19": ("Dashain Holiday", "public_holiday"),
    "2026-10-20": ("Maha Navami", "public_holiday"),
    "2026-10-21": ("Vijayadashami (Dashain Tika)", "public_holiday"),
    "2026-10-22": ("Dashain Holiday", "public_holiday"),
    "2026-10-23": ("Dashain Holiday", "public_holiday"),
    "2026-11-08": ("Laxmi Puja (Deepawali)", "public_holiday"),
    "2026-11-09": ("Gai Tihar", "public_holiday"),
    "2026-11-10": ("Goru Tihar & Govardhan Puja", "public_holiday"),
    "2026-11-11": ("Bhai Tika", "public_holiday"),
    "2026-11-12": ("Tihar Holiday", "public_holiday"),
    "2026-11-15": ("Chhath Parwa", "public_holiday"),
    "2026-11-24": ("Guru Nanak Jayanti", "public_holiday"),
    "2026-12-03": ("International Day of Persons with Disabilities", "public_holiday"),
    "2026-12-24": ("Udhauli Festival (Kirat)", "public_holiday"),
    "2026-12-25": ("Christmas Day", "public_holiday"),
    "2026-12-30": ("Tamu (Gurung) Lhosar", "public_holiday"),
    "2027-01-11": ("Prithvi Jayanti (National Unity Day)", "public_holiday"),
    "2027-01-15": ("Maghe Sankranti", "public_holiday"),
    "2027-01-30": ("Martyrs' Day", "public_holiday"),
    "2027-02-07": ("Sonam (Tamang) Lhosar", "public_holiday"),
    "2027-02-11": ("Saraswati Puja (Vasant Panchami)", "public_holiday"),
    "2027-02-19": ("Democracy Day", "public_holiday"),
    "2027-03-06": ("Maha Shivaratri", "public_holiday"),
    "2027-03-08": ("International Women's Day", "public_holiday"),
    "2027-03-09": ("Gyalpo Lhosar", "public_holiday"),
    "2027-03-21": ("Holi (Hills Region)", "public_holiday"),
    "2027-03-22": ("Holi (Terai Region)", "public_holiday"),
    "2027-04-06": ("Ghode Jatra", "public_holiday"),

    # ── FESTIVAL HOLIDAYS (Wikipedia Festival Holidays currently in "festival") ─
    "2026-05-20": ("Eid al-Adha (Bakr Eid)", "festival"),

    # ── USER EXCEPTIONS: Wikipedia Optional → keep as festival ───────────────
    # Gai Jatra, Teej, Saraswati Puja, Ghode Jatra are already public_holiday above.
    # Only Indra Jatra is currently "festival" and needs the exception treatment.
    "2026-09-25": ("Indra Jatra (Swanchhya)", "festival"),

    # ── OPTIONAL HOLIDAYS (festivals → reclassified) ─────────────────────────
    "2026-04-15": ("Tokha Chandeshwari Jatra", "optional_holiday"),
    "2026-04-16": ("Matati Chahre Puja", "optional_holiday"),
    "2026-04-17": ("Mother's Day (Mata Tirtha Aunsi)", "optional_holiday"),
    "2026-04-18": ("Bisket Jatra Ends (Bhaktapur)", "optional_holiday"),
    "2026-04-19": ("Parshuram Jayanti", "optional_holiday"),
    "2026-04-20": ("Akshay Tritiya", "optional_holiday"),
    "2026-04-21": ("Lalitpur Matsyendranath Rath Jatra Begins", "optional_holiday"),
    "2026-04-22": ("Adi Shankaracharya Jayanti", "optional_holiday"),
    "2026-04-23": ("Gangotpatti (Ganga Saptami)", "optional_holiday"),
    "2026-04-24": ("Democracy Day Anniversary", "optional_holiday"),
    "2026-04-25": ("Sita Jayanti", "optional_holiday"),
    "2026-04-27": ("Mohini Ekadashi Fast", "optional_holiday"),
    "2026-04-28": ("National Tea Day", "optional_holiday"),
    "2026-04-30": ("Nrusinha Jayanti", "optional_holiday"),
    "2026-05-05": ("Mangal Chauthi Fast", "optional_holiday"),
    "2026-05-07": ("Social Reform Day (Kirat)", "optional_holiday"),
    "2026-05-08": ("Red Cross Day", "optional_holiday"),
    "2026-05-09": ("Law Day", "optional_holiday"),
    "2026-05-11": ("Mahila Jyotis Sangh Foundation Day", "optional_holiday"),
    "2026-05-13": ("Apara Ekadashi Fast", "optional_holiday"),
    "2026-05-15": ("Sithinakha Puja", "optional_holiday"),
    "2026-05-16": ("Shani Jayanti", "optional_holiday"),
    "2026-05-17": ("Gosainkunda Bath Season Begins", "optional_holiday"),
    "2026-05-23": ("Siddhicharan Shrestha Birth Anniversary", "optional_holiday"),
    "2026-05-26": ("Gosainkunda Bath Season Ends", "optional_holiday"),
    "2026-05-30": ("Full Moon Fast (Purnima)", "optional_holiday"),
    "2026-06-01": ("Forest User Day", "optional_holiday"),
    "2026-06-04": ("Anti-Caste Discrimination Day", "optional_holiday"),
    "2026-06-07": ("Rabi Saptami Fast", "optional_holiday"),
    "2026-06-12": ("Anti-Child Labour Day", "optional_holiday"),
    "2026-06-15": ("New Moon Day (Somware Aunsi)", "optional_holiday"),
    "2026-06-20": ("Sithinakha Festival", "optional_holiday"),
    "2026-06-22": ("Wayu Asthami", "optional_holiday"),
    "2026-06-25": ("Nirjala Ekadashi Fast", "optional_holiday"),
    "2026-06-27": ("Shani Pradosh Fast", "optional_holiday"),
    "2026-06-29": ("Mastha Purnima", "optional_holiday"),
    "2026-07-08": ("Bhal-Bhal Asthami", "optional_holiday"),
    "2026-07-09": ("Nakwa Disi", "optional_holiday"),
    "2026-07-10": ("Yogini Ekadashi Fast", "optional_holiday"),
    "2026-07-11": ("Yogini Ekadashi Fast (Vaishnavas)", "optional_holiday"),
    "2026-07-13": ("Dila Chahre Puja", "optional_holiday"),
    "2026-07-16": ("Jagannath Rath Jatra", "optional_holiday"),
    "2026-07-17": ("Luto Phalne (New Year Cleansing)", "optional_holiday"),
    "2026-07-18": ("Kamaiya Liberation Day", "optional_holiday"),
    "2026-07-21": ("Surya Puja (Sun Worship)", "optional_holiday"),
    "2026-07-22": ("BP Koirala Memorial Day", "optional_holiday"),
    "2026-07-25": ("Tulsi Planting Day", "optional_holiday"),
    "2026-07-26": ("Tulsi Piye", "optional_holiday"),
    "2026-07-29": ("Guru Purnima", "optional_holiday"),
    "2026-07-31": ("Kheer Khane (Rice Pudding Day)", "optional_holiday"),
    "2026-08-09": ("Kamika Ekadashi Fast", "optional_holiday"),
    "2026-08-10": ("Som Pradosh Fast", "optional_holiday"),
    "2026-08-11": ("Gathemangal Puja", "optional_holiday"),
    "2026-08-13": ("Gunla Festival Begins (Buddhist)", "optional_holiday"),
    "2026-08-17": ("Nag Panchami", "optional_holiday"),
    "2026-08-19": ("Goswami Tulsidas Jayanti", "optional_holiday"),
    "2026-08-20": ("Yal Panchadaan", "optional_holiday"),
    "2026-08-23": ("Putrada Ekadashi Fast", "optional_holiday"),
    "2026-08-24": ("Bahidyabboye", "optional_holiday"),
    "2026-08-25": ("National Dharma Sabha Day", "optional_holiday"),
    "2026-08-27": ("Full Moon Fast (Purnima)", "optional_holiday"),
    "2026-08-30": ("Ropai Jatra", "optional_holiday"),
    "2026-09-01": ("Mangal Chauthi Fast", "optional_holiday"),
    "2026-09-02": ("Chandra Shashti Fast", "optional_holiday"),
    "2026-09-05": ("Gunga Navami", "optional_holiday"),
    "2026-09-07": ("Civil Service Day (Civil Servants Only)", "optional_holiday"),
    "2026-09-09": ("Jug Chahre Puja", "optional_holiday"),
    "2026-09-10": ("Nishi Barne", "optional_holiday"),
    "2026-09-11": ("Father's Day (Kushe Aunsi)", "optional_holiday"),
    "2026-09-12": ("Gunla Festival Ends", "optional_holiday"),
    "2026-09-13": ("Teej Eve Feast (Dar Khane)", "optional_holiday"),
    "2026-09-15": ("Rishi Panchami Fast", "optional_holiday"),
    "2026-09-16": ("Kokhaja Viye", "optional_holiday"),
    "2026-09-18": ("Mahalaxmi Vrat Begins", "optional_holiday"),
    "2026-09-20": ("Adukha Navami Fast", "optional_holiday"),
    "2026-09-22": ("Hariparivatini Ekadashi Fast", "optional_holiday"),
    "2026-09-27": ("Pitru Paksha Shraddha Begins (Ancestor Rites)", "optional_holiday"),
    "2026-09-28": ("Anti-Rabies Day", "optional_holiday"),
    "2026-09-30": ("Chauthi Shraddha", "optional_holiday"),
    "2026-10-01": ("Panchami Shraddha", "optional_holiday"),
    "2026-10-02": ("Saptami Shraddha", "optional_holiday"),
    "2026-10-03": ("Mahalaxmi Vrat Ends", "optional_holiday"),
    "2026-10-05": ("Dashami Shraddha", "optional_holiday"),
    "2026-10-06": ("Indira Ekadashi Fast", "optional_holiday"),
    "2026-10-07": ("Farping Harishankar Yatra", "optional_holiday"),
    "2026-10-08": ("Trayodashi Shraddha", "optional_holiday"),
    "2026-10-09": ("Chaturdashi Shraddha", "optional_holiday"),
    "2026-10-13": ("National Disaster Risk Reduction Day", "optional_holiday"),
    "2026-10-15": ("Rural Women's Day", "optional_holiday"),
    "2026-10-25": ("Kojagrat Fast (Full Moon)", "optional_holiday"),
    "2026-10-26": ("Kartik Bathing Season Begins", "optional_holiday"),
    "2026-11-01": ("Rabi Saptami Fast", "optional_holiday"),
    "2026-11-02": ("Radhastami", "optional_holiday"),
    "2026-11-04": ("UNESCO Day", "optional_holiday"),
    "2026-11-05": ("Rama Ekadashi Fast", "optional_holiday"),
    "2026-11-06": ("Dhanteras (Dhan Trayodashi)", "optional_holiday"),
    "2026-11-07": ("Dhanvantari Jayanti", "optional_holiday"),
    "2026-11-17": ("Gopastami", "optional_holiday"),
    "2026-11-18": ("Satya Yugadi", "optional_holiday"),
    "2026-11-20": ("Haribodini Ekadashi Fast", "optional_holiday"),
    "2026-11-21": ("Television Day", "optional_holiday"),
    "2026-11-25": ("Anti-Violence Against Women Day", "optional_holiday"),
    "2026-12-04": ("Utpatti Ekadashi Fast", "optional_holiday"),
    "2026-12-05": ("Volunteer Day", "optional_holiday"),
    "2026-12-06": ("Pashupatinath & Halesi Mahadev Fair", "optional_holiday"),
    "2026-12-07": ("Bala Chaturdashi (Seed Scattering)", "optional_holiday"),
    "2026-12-14": ("Vivahapanchami (Sita-Ram Wedding)", "optional_holiday"),
    "2026-12-16": ("National Flag Day", "optional_holiday"),
    "2026-12-17": ("Bakhuma", "optional_holiday"),
    "2026-12-19": ("Kirtipur Indrayani Jatra", "optional_holiday"),
    "2026-12-20": ("Mokshadha Ekadashi Fast", "optional_holiday"),
    "2026-12-21": ("Som Pradosh Fast", "optional_holiday"),
    "2026-12-23": ("Dattatreya Jayanti", "optional_holiday"),
    "2026-12-31": ("National Reconciliation Day", "optional_holiday"),
    "2027-01-01": ("New Year 2027", "optional_holiday"),
    "2027-01-03": ("Saphala Ekadashi Fast", "optional_holiday"),
    "2027-01-05": ("Guru Gobind Singh Jayanti", "optional_holiday"),
    "2027-01-07": ("Arniko Memorial Day", "optional_holiday"),
    "2027-01-08": ("Tol Lhosar", "optional_holiday"),
    "2027-01-12": ("Mangal Chauthi Fast", "optional_holiday"),
    "2027-01-13": ("National Bhakka Day", "optional_holiday"),
    "2027-01-16": ("Shwet Matsyendranath Bathing Ceremony", "optional_holiday"),
    "2027-01-18": ("Putrada Ekadashi Fast", "optional_holiday"),
    "2027-01-19": ("Musyaduli", "optional_holiday"),
    "2027-01-22": ("Magh Bathing Season Begins", "optional_holiday"),
    "2027-01-25": ("Kashi Ganesh Festival", "optional_holiday"),
    "2027-01-29": ("Nepal Nursing Day", "optional_holiday"),
    "2027-02-05": ("Lai Chahre Puja", "optional_holiday"),
    "2027-02-06": ("Pashupatinath Madhavnarayan Fair", "optional_holiday"),
    "2027-02-10": ("Tilakunda Chaturthi", "optional_holiday"),
    "2027-02-12": ("Skanda Sashti", "optional_holiday"),
    "2027-02-14": ("Valentine's Day", "optional_holiday"),
    "2027-02-16": ("Shalya Dashami", "optional_holiday"),
    "2027-02-17": ("Bhima Ekadashi Fast", "optional_holiday"),
    "2027-02-18": ("Magh Yatra (Vatu)", "optional_holiday"),
    "2027-02-20": ("Swasthani Vrat Ends", "optional_holiday"),
    "2027-02-27": ("National Magar Day", "optional_holiday"),
    "2027-03-02": ("Majhi Community Ladi Puja", "optional_holiday"),
    "2027-03-04": ("Vijaya Ekadashi Fast", "optional_holiday"),
    "2027-03-14": ("Pi Day", "optional_holiday"),
    "2027-03-15": ("Chaitra Sankranti", "optional_holiday"),
    "2027-03-16": ("Chir Sthapana (Chir Swaye)", "optional_holiday"),
    "2027-03-18": ("Amalaki Ekadashi", "optional_holiday"),
    "2027-03-19": ("Govinda Dwadashi", "optional_holiday"),
    "2027-03-20": ("Shani Pradosh Fast", "optional_holiday"),
    "2027-03-25": ("Nala Matsyendranath Rath Yatra", "optional_holiday"),
    "2027-03-27": ("Spiritual Journalist Society Foundation Day", "optional_holiday"),
    "2027-03-30": ("Shitalastami", "optional_holiday"),
    "2027-04-02": ("Papmochani Ekadashi Fast", "optional_holiday"),
    "2027-04-03": ("Devpatan Puja", "optional_holiday"),
    "2027-04-05": ("Pishach Chaturdashi (Pahan Chahre Puja)", "optional_holiday"),
    "2027-04-09": ("Matsyanarayana Fair", "optional_holiday"),
    "2027-04-11": ("Bisket Jatra Begins (Bhaktapur)", "optional_holiday"),

    # ── INTERNATIONAL DAYS ────────────────────────────────────────────────────
    "2026-04-26": ("World Intellectual Property Day", "international_day"),
    "2026-04-29": ("International Dance Day", "international_day"),
    "2026-05-03": ("World Press Freedom Day", "international_day"),
    "2026-05-12": ("World Nurses Day", "international_day"),
    "2026-05-21": ("World Culture Day", "international_day"),
    "2026-05-22": ("International Day for Biological Diversity", "international_day"),
    "2026-05-28": ("World Women's Health Day", "international_day"),
    "2026-05-31": ("World No Tobacco Day", "international_day"),
    "2026-06-03": ("World Bicycle Day", "international_day"),
    "2026-06-05": ("World Environment Day", "international_day"),
    "2026-06-08": ("World Oceans Day", "international_day"),
    "2026-06-14": ("World Blood Donor Day", "international_day"),
    "2026-06-17": ("World Day to Combat Desertification", "international_day"),
    "2026-06-21": ("International Yoga Day", "international_day"),
    "2026-06-23": ("International Olympic Day", "international_day"),
    "2026-06-26": ("International Day Against Drug Trafficking", "international_day"),
    "2026-07-02": ("World Sports Journalists Day", "international_day"),
    "2026-08-08": ("World Soil Conservation Day", "international_day"),
    "2026-08-12": ("International Youth Day", "international_day"),
    "2026-09-08": ("World Literacy Day", "international_day"),
    "2026-09-17": ("Vishwakarma Puja Day", "international_day"),
    "2026-09-21": ("International Day of Peace", "international_day"),
    "2026-09-23": ("International Sign Language Day", "international_day"),
    "2026-09-26": ("Int'l Day for Total Elimination of Nuclear Weapons", "international_day"),
    "2026-09-29": ("World Heart Day", "international_day"),
    "2026-10-10": ("World Mental Health Day", "international_day"),
    "2026-10-14": ("World Quality Day", "international_day"),
    "2026-10-16": ("World Food Day", "international_day"),
    "2026-10-24": ("World Development Information Day", "international_day"),
    "2026-10-31": ("World Cities Day", "international_day"),
    "2026-11-14": ("World Diabetes Day", "international_day"),
    "2026-11-16": ("World Tolerance Day", "international_day"),
    "2026-11-19": ("World Toilet Day", "international_day"),
    "2026-12-01": ("World AIDS Day", "international_day"),
    "2026-12-02": ("World Day for the Abolition of Slavery", "international_day"),
    "2026-12-09": ("International Anti-Corruption Day", "international_day"),
    "2026-12-10": ("World Human Rights Day", "international_day"),
    "2026-12-11": ("International Mountain Day", "international_day"),
    "2026-12-18": ("International Migrants Day", "international_day"),
    "2027-01-24": ("International Education Day", "international_day"),
    "2027-01-26": ("International Customs Day", "international_day"),
    "2027-02-02": ("World Wetlands Day", "international_day"),
    "2027-02-04": ("World Cancer Day", "international_day"),
    "2027-02-13": ("World Radio Day", "international_day"),
    "2027-02-15": ("International Childhood Cancer Day", "international_day"),
    "2027-02-21": ("World Mother Language Day", "international_day"),
    "2027-03-23": ("World Meteorological Day", "international_day"),
    "2027-03-24": ("World Tuberculosis Day", "international_day"),
    "2027-04-01": ("April Fools' Day (World Fool's Day)", "international_day"),
    "2027-04-07": ("World Health Day", "international_day"),
    "2027-04-12": ("World Astrology Federation Day", "international_day"),
    "2027-04-13": ("Bhaktapur Vishwadhwaj Festival", "international_day"),
}


def enrich(event: dict) -> dict:
    """Return event with name_en and corrected category."""
    date = event["date_ad"]
    if date in DATE_MAP:
        name_en, category = DATE_MAP[date]
        return {**event, "name_en": name_en, "category": category}

    # Fallback: keep existing category, mark name as needing translation
    # (should not be reached if DATE_MAP is complete)
    return {**event, "name_en": f"[{event['name_ne']}]"}


def main() -> None:
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    path = Path("data/2083.json")
    data = json.loads(path.read_text(encoding="utf-8"))

    enriched = [enrich(e) for e in data["events"]]

    # Report
    cats: dict[str, int] = {}
    unmapped: list[str] = []
    for e in enriched:
        cats[e["category"]] = cats.get(e["category"], 0) + 1
        if e["name_en"].startswith("["):
            unmapped.append(f"  {e['date_ad']}  {e['name_ne']}")

    data["events"] = enriched
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Enrichment complete")
    print(f"  Categories: {cats}")
    if unmapped:
        print(f"  WARNING: {len(unmapped)} unmapped events (name_en is still Nepali):")
        for u in unmapped:
            print(u)
    else:
        print("  All events have English names")


if __name__ == "__main__":
    main()
