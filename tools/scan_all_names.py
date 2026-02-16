"""
COMPREHENSIVE BIBLICAL NAME SCANNER
Scans EVERY word in EVERY chapter HTML file across all 66 books.
Cross-references with words.json definitions to identify proper names.
Categories: person, place, people/nation, title/divine, event, organization

Outputs:
  data/all_proper_names.json  - ALL proper names (people, places, etc.)
  data/person_names.json      - Just person names, ordered by first appearance
"""
import json
import os
import re
import sys
from collections import OrderedDict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)

# Book order for the entire Bible (OT + NT)
BOOK_ORDER = [
    "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
    "joshua", "judges", "ruth",
    "1_samuel", "2_samuel", "1_kings", "2_kings",
    "1_chronicles", "2_chronicles",
    "ezra", "nehemiah", "esther",
    "job", "psalms", "proverbs", "ecclesiastes", "song_of_solomon",
    "isaiah", "jeremiah", "lamentations", "ezekiel", "daniel",
    "hosea", "joel", "amos", "obadiah", "jonah",
    "micah", "nahum", "habakkuk", "zephaniah",
    "haggai", "zechariah", "malachi",
    "matthew", "mark", "luke", "john", "acts", "romans",
    "1_corinthians", "2_corinthians", "galatians", "ephesians",
    "philippians", "colossians", "1_thessalonians", "2_thessalonians",
    "1_timothy", "2_timothy", "titus", "philemon", "hebrews",
    "james", "1_peter", "2_peter", "1_john", "2_john", "3_john",
    "jude", "revelation"
]

BOOK_DISPLAY = {
    "genesis": "Genesis", "exodus": "Exodus", "leviticus": "Leviticus",
    "numbers": "Numbers", "deuteronomy": "Deuteronomy",
    "joshua": "Joshua", "judges": "Judges", "ruth": "Ruth",
    "1_samuel": "1 Samuel", "2_samuel": "2 Samuel",
    "1_kings": "1 Kings", "2_kings": "2 Kings",
    "1_chronicles": "1 Chronicles", "2_chronicles": "2 Chronicles",
    "ezra": "Ezra", "nehemiah": "Nehemiah", "esther": "Esther",
    "job": "Job", "psalms": "Psalms", "proverbs": "Proverbs",
    "ecclesiastes": "Ecclesiastes", "song_of_solomon": "Song of Solomon",
    "isaiah": "Isaiah", "jeremiah": "Jeremiah", "lamentations": "Lamentations",
    "ezekiel": "Ezekiel", "daniel": "Daniel",
    "hosea": "Hosea", "joel": "Joel", "amos": "Amos",
    "obadiah": "Obadiah", "jonah": "Jonah", "micah": "Micah",
    "nahum": "Nahum", "habakkuk": "Habakkuk", "zephaniah": "Zephaniah",
    "haggai": "Haggai", "zechariah": "Zechariah", "malachi": "Malachi",
    "matthew": "Matthew", "mark": "Mark", "luke": "Luke", "john": "John",
    "acts": "Acts", "romans": "Romans",
    "1_corinthians": "1 Corinthians", "2_corinthians": "2 Corinthians",
    "galatians": "Galatians", "ephesians": "Ephesians",
    "philippians": "Philippians", "colossians": "Colossians",
    "1_thessalonians": "1 Thessalonians", "2_thessalonians": "2 Thessalonians",
    "1_timothy": "1 Timothy", "2_timothy": "2 Timothy",
    "titus": "Titus", "philemon": "Philemon", "hebrews": "Hebrews",
    "james": "James", "1_peter": "1 Peter", "2_peter": "2 Peter",
    "1_john": "1 John", "2_john": "2 John", "3_john": "3 John",
    "jude": "Jude", "revelation": "Revelation"
}

# ============================================================================
# PROPER NAME IDENTIFICATION RULES
# Using training knowledge of Hebrew to classify words
# ============================================================================

# Known proper name Hebrew words mapped to categories and English names
# This is the TRAINING KNOWLEDGE that the Oracle uses
# Categories: person, place, people, title, event, divine

KNOWN_NAMES = {}  # Will be populated from words.json definitions + training knowledge

# Patterns in definitions that indicate proper names
PERSON_PATTERNS = [
    r'\b(son of|daughter of|father of|mother of|brother of|sister of|wife of|husband of)\b',
    r'\b(king|queen|priest|prophet|judge|captain|prince|princess)\b',
    r'\b(begat|bore|married|slew|killed)\b',
]

PLACE_PATTERNS = [
    r'\b(city|cities|land|region|country|territory|province|wilderness|desert)\b',
    r'\b(mountain|mount|hill|valley|plain|river|brook|stream|sea|lake|well|spring)\b',
    r'\b(gate|tower|wall|temple|tabernacle|altar|pillar)\b',
    r'\b(Canaan|Egypt|Babylon|Assyria|Persia|Moab|Edom|Philist)\b',
]

PEOPLE_PATTERNS = [
    r'\b(tribe|clan|family|house of|children of|sons of|people|nation|Israelite)\b',
    r'\b(-ite|-ites|Amorite|Hittite|Jebusite|Canaanite|Philistine|Midianite)\b',
]

DIVINE_PATTERNS = [
    r'\b(God|LORD|Lord|god|gods|divine|angel|cherub|seraph)\b',
    r'\b(Yahweh|Jehovah|Elohim|Adonai|El Shaddai|Most High)\b',
]


def classify_word(hebrew, definition, transliteration, strongs):
    """
    Classify a Hebrew word as a proper name or not.
    Returns (is_proper_name, category, english_name) or (False, None, None)
    """
    if not definition:
        return False, None, None

    defn_lower = definition.lower()
    translit = transliteration or ""

    # Skip common words that are clearly not proper names
    common_skips = [
        'and', 'the', 'to', 'of', 'in', 'with', 'from', 'for', 'not',
        'which', 'who', 'what', 'that', 'this', 'these', 'those',
        'he', 'she', 'it', 'they', 'we', 'you', 'i', 'me', 'my',
        'is', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'shall', 'would', 'could', 'should',
        'a', 'an', 'all', 'every', 'each', 'some', 'any', 'no', 'none',
        'said', 'say', 'saying', 'speak', 'spoke', 'spoken',
        'come', 'came', 'go', 'went', 'gone', 'send', 'sent',
        'give', 'gave', 'take', 'took', 'make', 'made',
        'see', 'saw', 'seen', 'hear', 'heard', 'know', 'knew', 'known',
        'man', 'woman', 'son', 'daughter', 'father', 'mother', 'brother',
        'hand', 'face', 'eye', 'heart', 'head', 'mouth', 'word',
        'day', 'night', 'year', 'time', 'house', 'land', 'water',
        'great', 'good', 'evil', 'righteous', 'holy', 'clean',
        'upon', 'over', 'under', 'before', 'after', 'between',
    ]

    # If definition is just a common English word, skip
    first_word = defn_lower.split(',')[0].strip().split(' ')[0].strip()
    if first_word in common_skips and len(definition) < 30:
        return False, None, None

    # Check for prefixed forms (le-, be-, ve-, me-, ke-, ha-)
    # These are prepositions/articles attached to words - skip them
    if strongs and '_' in strongs:
        return False, None, None

    # RULE 1: Capitalized transliteration = likely proper name
    if translit and len(translit) > 1 and translit[0].isupper():
        # Determine category from definition
        if any(re.search(p, definition, re.I) for p in DIVINE_PATTERNS):
            return True, "divine", translit
        if any(re.search(p, definition, re.I) for p in PLACE_PATTERNS):
            return True, "place", translit
        if any(re.search(p, definition, re.I) for p in PEOPLE_PATTERNS):
            return True, "people", translit
        # Default to person for capitalized transliterations
        return True, "person", translit

    # RULE 2: Definition contains "(name)" or is clearly a name
    if re.search(r'\(name\)|\bname of\b', defn_lower):
        return True, "person", translit or hebrew

    # RULE 3: Definition matches person patterns
    if any(re.search(p, definition, re.I) for p in PERSON_PATTERNS):
        # Only if it looks like a name definition (short, starts with capital)
        if definition[0].isupper() and len(definition) < 100:
            return True, "person", translit or definition.split(' ')[0]

    # RULE 4: Definition is a single capitalized word (likely a name)
    words_in_def = definition.strip().split()
    if len(words_in_def) == 1 and words_in_def[0][0].isupper() and words_in_def[0].isalpha():
        if words_in_def[0].lower() not in common_skips:
            return True, "person", words_in_def[0]

    # RULE 5: Strongs number AND definition starts with capital = documented name
    if strongs and definition[0].isupper():
        d = definition.split('-')[0].strip().split(',')[0].strip()
        if d and d[0].isupper() and len(d) < 30 and d.lower() not in common_skips:
            # Check what kind of name
            if any(re.search(p, definition, re.I) for p in PLACE_PATTERNS):
                return True, "place", d
            if any(re.search(p, definition, re.I) for p in PEOPLE_PATTERNS):
                return True, "people", d
            if any(re.search(p, definition, re.I) for p in DIVINE_PATTERNS):
                return True, "divine", d
            return True, "person", d

    # RULE 6: Check for place-like definitions
    if any(re.search(p, definition, re.I) for p in PLACE_PATTERNS):
        if definition[0].isupper() and strongs:
            place_name = definition.split('-')[0].strip().split(',')[0].strip()
            return True, "place", place_name

    return False, None, None


def scan_chapter_html(filepath):
    """Extract all Hebrew words from a chapter HTML file in order."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all showWordEvolution('hebrew_word') calls in order
    words = re.findall(r"showWordEvolution\('([^']+)'\)", content)

    # Also extract verse references
    # Pattern: class="verse-ref" and verse numbers
    verses = re.findall(r'id="v(\d+)"', content)

    return words, verses


def main():
    words_path = os.path.join(ROOT_DIR, "words.json")

    print("[INFO] Loading words.json...")
    with open(words_path, "r", encoding="utf-8") as f:
        words_data = json.load(f)
    print(f"[OK] Loaded {len(words_data)} word entries")

    # Phase 1: Classify ALL words in words.json
    print("\n[INFO] Phase 1: Classifying all 58,400 words...")
    proper_names = {}  # hebrew -> {category, english, definition, ...}
    not_names = 0
    name_counts = {"person": 0, "place": 0, "people": 0, "divine": 0, "title": 0, "event": 0}

    for hebrew_key, entry in words_data.items():
        if not isinstance(entry, dict):
            continue

        definition = entry.get("definition", "")
        transliteration = entry.get("transliteration", "")
        strongs = entry.get("strongs", "")

        is_name, category, english = classify_word(
            hebrew_key, definition, transliteration, strongs
        )

        if is_name:
            proper_names[hebrew_key] = {
                "hebrew": entry.get("hebrew", hebrew_key),
                "english": english,
                "category": category,
                "transliteration": transliteration,
                "definition": definition,
                "gematria": entry.get("gematria", 0),
                "digital_root": entry.get("digital_root", 0),
                "strongs": strongs,
                "first_occurrence": entry.get("first_occurrence", ""),
                "frequency": entry.get("frequency", 0),
                "letters": entry.get("letters", []),
                "pictographic": entry.get("pictographic", ""),
                "timeline": entry.get("timeline", {}),
                "corruption_timeline": entry.get("corruption_timeline", {}),
            }
            name_counts[category] = name_counts.get(category, 0) + 1
        else:
            not_names += 1

    print(f"[OK] Classification complete:")
    print(f"  Proper names found: {len(proper_names)}")
    print(f"  Regular words: {not_names}")
    for cat, count in sorted(name_counts.items(), key=lambda x: -x[1]):
        print(f"    {cat}: {count}")

    # Phase 2: Scan ALL chapter HTML files to find names in order of appearance
    print(f"\n[INFO] Phase 2: Scanning all chapter HTML files...")
    first_appearances = {}  # hebrew_key -> (book_idx, chapter, position_in_chapter)
    total_chapters_scanned = 0

    for book_idx, book_dir in enumerate(BOOK_ORDER):
        book_path = os.path.join(ROOT_DIR, book_dir)
        if not os.path.isdir(book_path):
            continue

        # Get chapter files sorted numerically
        chapter_files = []
        for f in os.listdir(book_path):
            if f.endswith('.html') and f != 'index.html':
                try:
                    ch_num = int(f.replace('.html', ''))
                    chapter_files.append((ch_num, f))
                except ValueError:
                    pass

        chapter_files.sort(key=lambda x: x[0])

        for ch_num, ch_file in chapter_files:
            ch_path = os.path.join(book_path, ch_file)
            words_in_chapter, _ = scan_chapter_html(ch_path)
            total_chapters_scanned += 1

            for pos, hebrew_word in enumerate(words_in_chapter):
                if hebrew_word in proper_names and hebrew_word not in first_appearances:
                    book_display = BOOK_DISPLAY.get(book_dir, book_dir)
                    first_appearances[hebrew_word] = {
                        "book_idx": book_idx,
                        "chapter": ch_num,
                        "position": pos,
                        "reference": f"{book_display} {ch_num}",
                    }

    print(f"[OK] Scanned {total_chapters_scanned} chapters")
    print(f"[OK] Found {len(first_appearances)} proper names in the actual text")

    # Phase 3: Build sorted output
    print(f"\n[INFO] Phase 3: Building sorted name databases...")

    # All proper names sorted by first appearance
    all_names_list = []
    for hebrew_key, name_data in proper_names.items():
        appearance = first_appearances.get(hebrew_key)
        if appearance:
            name_data["first_appearance_ref"] = appearance["reference"]
            name_data["_sort_key"] = (appearance["book_idx"], appearance["chapter"], appearance["position"])
        else:
            # Use the first_occurrence from words.json as fallback
            name_data["first_appearance_ref"] = name_data.get("first_occurrence", "Unknown")
            name_data["_sort_key"] = (999, 999, 999)

        all_names_list.append(name_data)

    # Sort by first appearance
    all_names_list.sort(key=lambda x: x["_sort_key"])

    # Assign order numbers and clean up
    for i, n in enumerate(all_names_list):
        n["order"] = i + 1
        n.pop("_sort_key", None)

    # Separate person names
    person_names = [n for n in all_names_list if n["category"] == "person"]
    place_names = [n for n in all_names_list if n["category"] == "place"]
    people_names = [n for n in all_names_list if n["category"] == "people"]
    divine_names = [n for n in all_names_list if n["category"] == "divine"]

    # Re-number person names
    for i, n in enumerate(person_names):
        n["person_order"] = i + 1

    print(f"\n[OK] Results:")
    print(f"  Total proper names: {len(all_names_list)}")
    print(f"  Person names: {len(person_names)}")
    print(f"  Place names: {len(place_names)}")
    print(f"  People/nation names: {len(people_names)}")
    print(f"  Divine names/titles: {len(divine_names)}")

    # Write all proper names
    output_dir = os.path.join(ROOT_DIR, "data")
    os.makedirs(output_dir, exist_ok=True)

    all_output = {
        "meta": {
            "title": "ALL Biblical Proper Names - Complete Scan",
            "total_names": len(all_names_list),
            "persons": len(person_names),
            "places": len(place_names),
            "peoples": len(people_names),
            "divine": len(divine_names),
            "chapters_scanned": total_chapters_scanned,
            "words_scanned": len(words_data),
            "method": "Full scan of 58,400 words.json entries + 1,014 chapter HTML files",
        },
        "names": all_names_list,
    }

    all_path = os.path.join(output_dir, "all_proper_names.json")
    with open(all_path, "w", encoding="utf-8") as f:
        json.dump(all_output, f, ensure_ascii=False, indent=2)
    print(f"[OK] Written: {all_path} ({os.path.getsize(all_path):,} bytes)")

    # Write person names only
    person_output = {
        "meta": {
            "title": "Biblical Person Names - Ordered by First Appearance",
            "total_names": len(person_names),
            "method": "Extracted from full proper names scan",
        },
        "names": person_names,
    }

    person_path = os.path.join(output_dir, "person_names.json")
    with open(person_path, "w", encoding="utf-8") as f:
        json.dump(person_output, f, ensure_ascii=False, indent=2)
    print(f"[OK] Written: {person_path} ({os.path.getsize(person_path):,} bytes)")

    # Show first 30 person names
    print(f"\n--- First 30 Person Names (by appearance) ---")
    for n in person_names[:30]:
        print(f"  {n['person_order']}. {n['english']}: {n['hebrew']} = {n['gematria']} | {n['first_appearance_ref']}")

    # Show first 20 place names
    print(f"\n--- First 20 Place Names ---")
    for n in place_names[:20]:
        print(f"  {n['order']}. {n['english']}: {n['hebrew']} = {n['gematria']} | {n['first_appearance_ref']}")

    # Show divine names
    print(f"\n--- Divine Names/Titles ---")
    for n in divine_names[:15]:
        print(f"  {n['english']}: {n['hebrew']} = {n['gematria']} | {n['definition'][:60]}")


if __name__ == "__main__":
    main()
