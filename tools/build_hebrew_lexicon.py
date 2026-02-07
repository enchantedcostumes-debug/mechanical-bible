#!/usr/bin/env python3
"""
BUILD COMPLETE HEBREW LEXICON
==============================
Creates a master lexicon of EVERY Hebrew word with:
- Strong's number
- Pictographic breakdown
- Root analysis from AHLB
- Gematria
- All translation versions
- Control mechanism (if applicable)

This is the MASTER SOURCE for the Mechanical Bible.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "services" / "rosetta_stone" / "data"
CONCORDANCE_DIR = DATA_DIR / "concordance"
OUTPUT_DIR = BASE_DIR / "data" / "lexicon"
AHLB_PATH = Path("G:/My Drive/PATREON/ARTICLES SERMONS/Evolution of Hebrew/ahlb.txt")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Hebrew letter data
HEBREW_LETTERS = {
    'א': {'name': 'ALEPH', 'proto': '𐤀', 'pic': 'ox head', 'concrete': 'strength, power, leader', 'abstract': 'first, authority, beginning'},
    'ב': {'name': 'BET', 'proto': '𐤁', 'pic': 'house/tent', 'concrete': 'house, family, inside', 'abstract': 'within, by means of, in'},
    'ג': {'name': 'GIMEL', 'proto': '𐤂', 'pic': 'camel/foot', 'concrete': 'camel, foot, walk', 'abstract': 'lift up, pride, benefit'},
    'ד': {'name': 'DALET', 'proto': '𐤃', 'pic': 'door', 'concrete': 'door, pathway', 'abstract': 'movement, entrance, hang'},
    'ה': {'name': 'HEY', 'proto': '𐤄', 'pic': 'man with arms raised', 'concrete': 'behold, look, breath', 'abstract': 'reveal, the, presence'},
    'ו': {'name': 'VAV', 'proto': '𐤅', 'pic': 'tent peg/hook', 'concrete': 'nail, peg, hook', 'abstract': 'and, add, secure'},
    'ז': {'name': 'ZAYIN', 'proto': '𐤆', 'pic': 'weapon/plow', 'concrete': 'weapon, cut, food', 'abstract': 'nourish, cut, harvest'},
    'ח': {'name': 'CHET', 'proto': '𐤇', 'pic': 'fence/wall', 'concrete': 'wall, fence, divide', 'abstract': 'outside, protect, half'},
    'ט': {'name': 'TET', 'proto': '𐤈', 'pic': 'basket/snake', 'concrete': 'basket, surround, mud', 'abstract': 'contain, good, surround'},
    'י': {'name': 'YOD', 'proto': '𐤉', 'pic': 'hand/arm', 'concrete': 'hand, work, throw', 'abstract': 'deed, make, accomplish'},
    'כ': {'name': 'KAF', 'proto': '𐤊', 'pic': 'open palm', 'concrete': 'palm, open, tame', 'abstract': 'allow, cover, like'},
    'ך': {'name': 'KAF SOFIT', 'proto': '𐤊', 'pic': 'open palm', 'concrete': 'palm, open, tame', 'abstract': 'allow, cover, like'},
    'ל': {'name': 'LAMED', 'proto': '𐤋', 'pic': 'shepherd staff', 'concrete': 'staff, goad, teach', 'abstract': 'toward, authority, control'},
    'מ': {'name': 'MEM', 'proto': '𐤌', 'pic': 'water/waves', 'concrete': 'water, sea, liquid', 'abstract': 'chaos, mighty, from'},
    'ם': {'name': 'MEM SOFIT', 'proto': '𐤌', 'pic': 'water/waves', 'concrete': 'water, sea, liquid', 'abstract': 'chaos, mighty, from'},
    'נ': {'name': 'NUN', 'proto': '𐤍', 'pic': 'seed/fish', 'concrete': 'seed, fish, continue', 'abstract': 'heir, life, perpetuate'},
    'ן': {'name': 'NUN SOFIT', 'proto': '𐤍', 'pic': 'seed/fish', 'concrete': 'seed, fish, continue', 'abstract': 'heir, life, perpetuate'},
    'ס': {'name': 'SAMECH', 'proto': '𐤎', 'pic': 'prop/support', 'concrete': 'support, lean, grab', 'abstract': 'protect, turn, surround'},
    'ע': {'name': 'AYIN', 'proto': '𐤏', 'pic': 'eye', 'concrete': 'eye, see, watch', 'abstract': 'know, experience, shade'},
    'פ': {'name': 'PEY', 'proto': '𐤐', 'pic': 'mouth', 'concrete': 'mouth, blow, speak', 'abstract': 'word, open, scatter'},
    'ף': {'name': 'PEY SOFIT', 'proto': '𐤐', 'pic': 'mouth', 'concrete': 'mouth, blow, speak', 'abstract': 'word, open, scatter'},
    'צ': {'name': 'TSADE', 'proto': '𐤑', 'pic': 'man on side', 'concrete': 'side, chase, hunt', 'abstract': 'righteous, desire, wait'},
    'ץ': {'name': 'TSADE SOFIT', 'proto': '𐤑', 'pic': 'man on side', 'concrete': 'side, chase, hunt', 'abstract': 'righteous, desire, wait'},
    'ק': {'name': 'QOF', 'proto': '𐤒', 'pic': 'sun on horizon', 'concrete': 'horizon, behind, circle', 'abstract': 'time, cycle, condense'},
    'ר': {'name': 'RESH', 'proto': '𐤓', 'pic': 'head of man', 'concrete': 'head, top, chief', 'abstract': 'first, beginning, leader'},
    'ש': {'name': 'SHIN', 'proto': '𐤔', 'pic': 'two front teeth', 'concrete': 'sharp, press, consume', 'abstract': 'destroy, change, transform'},
    'ת': {'name': 'TAV', 'proto': '𐤕', 'pic': 'cross/mark', 'concrete': 'sign, mark, cross', 'abstract': 'covenant, complete, seal'},
}

GEMATRIA = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
    'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100,
    'ר': 200, 'ש': 300, 'ת': 400
}


@dataclass
class LexiconEntry:
    """Complete lexicon entry for a Hebrew word"""
    hebrew: str
    transliteration: str = ""
    strongs: str = ""
    definition: str = ""
    root: str = ""

    # Pictographic analysis
    letters: List[Dict] = field(default_factory=list)
    pictographic_meaning: str = ""

    # Numerical
    gematria: int = 0
    digital_root: int = 0

    # AHLB data
    ahlb_entry: str = ""
    parent_root: str = ""

    # Occurrences
    frequency: int = 0
    first_occurrence: str = ""

    # Translations (chain of evidence)
    kjv_translation: str = ""
    lxx_translation: str = ""
    vulgate_translation: str = ""

    # Control mechanism
    is_control_word: bool = False
    control_mechanism: str = ""


def get_digital_root(n: int) -> int:
    """Calculate digital root"""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def analyze_word(hebrew: str) -> Dict:
    """Analyze a Hebrew word pictographically"""
    letters = []
    meanings = []
    gematria = 0

    for char in hebrew:
        if char in HEBREW_LETTERS:
            data = HEBREW_LETTERS[char]
            letters.append({
                'letter': char,
                'name': data['name'],
                'proto_sinaitic': data['proto'],
                'pictograph': data['pic'],
                'concrete': data['concrete'],
                'abstract': data['abstract']
            })
            meanings.append(f"[{data['abstract']}]")
            gematria += GEMATRIA.get(char, 0)

    return {
        'letters': letters,
        'pictographic_meaning': ' '.join(meanings),
        'gematria': gematria,
        'digital_root': get_digital_root(gematria) if gematria > 0 else 0
    }


def load_strongs():
    """Load Strong's concordance data from ALL available sources"""
    print("[INFO] Loading Strong's Hebrew from ALL sources...")
    strongs_data = {}

    # Source 1: Main hebrew_strongs.json (has key words with high Strong's numbers)
    strongs_path = CONCORDANCE_DIR / "hebrew_strongs.json"
    if strongs_path.exists():
        with open(strongs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for word, info in data.items():
                if isinstance(info, dict):
                    strongs_num = info.get('strongs', '')
                    if strongs_num:
                        strongs_data[word] = info
                        # Also index by cleaned word (consonants only)
                        clean = ''.join(c for c in word if c in HEBREW_LETTERS)
                        if clean and clean != word:
                            strongs_data[clean] = info
        print(f"  [OK] Loaded {len(strongs_data)} entries from hebrew_strongs.json")

    # Source 2: Complete lexicon CSV (has many more entries with inflections)
    lexicon_csv = DATA_DIR / "hebrew_complete_lexicon.csv"
    if lexicon_csv.exists():
        csv_count = 0
        with open(lexicon_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row.get('word', '')
                strongs = row.get('strongs_number', '')

                if word and strongs:
                    # Only add if not already in strongs_data
                    if word not in strongs_data:
                        entry = {
                            'strongs': strongs,
                            'translit': row.get('transliteration', ''),
                            'definition': row.get('gloss', ''),
                            'gematria': row.get('gematria', ''),
                            'is_divine': row.get('is_divine', '') == 'True',
                            'divine_signature': row.get('divine_signature', ''),
                            'semantic_category': row.get('semantic_category', '')
                        }
                        strongs_data[word] = entry
                        csv_count += 1

                        # Also index by cleaned word (consonants only)
                        clean = ''.join(c for c in word if c in HEBREW_LETTERS)
                        if clean and clean not in strongs_data:
                            strongs_data[clean] = entry
                            csv_count += 1

        print(f"  [OK] Added {csv_count} entries from hebrew_complete_lexicon.csv")

    print(f"  [OK] Total: {len(strongs_data)} Strong's entries loaded")
    return strongs_data


def load_ahlb():
    """Load and parse AHLB data"""
    print("[INFO] Loading AHLB...")
    ahlb_data = {}

    if not AHLB_PATH.exists():
        print(f"  [WARN] AHLB not found at {AHLB_PATH}")
        return ahlb_data

    try:
        with open(AHLB_PATH, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        # Find all Strong's references with context
        pattern = r'([^\n]{0,500})\{str:\s*(\d+)\}'
        matches = re.finditer(pattern, content)

        for match in matches:
            context = match.group(1)
            strongs_num = f"H{match.group(2)}"
            ahlb_data[strongs_num] = context.strip()

        print(f"  [OK] Loaded {len(ahlb_data)} AHLB entries")
    except Exception as e:
        print(f"  [FAIL] AHLB error: {e}")

    return ahlb_data


def load_control_words():
    """Load top 100 control words"""
    print("[INFO] Loading control words...")
    control_words = {}

    control_path = BASE_DIR / "data" / "top_100_control_words.json"
    if control_path.exists():
        with open(control_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for word in data.get('control_words', []):
                strongs = word.get('strongs', '')
                if strongs:
                    control_words[strongs] = word
        print(f"  [OK] Loaded {len(control_words)} control words")

    return control_words


def extract_unique_words():
    """Extract all unique Hebrew words from Tanakh"""
    print("[INFO] Extracting unique Hebrew words from Tanakh...")

    words = defaultdict(lambda: {'count': 0, 'first_ref': ''})

    verses_path = DATA_DIR / "tanakh_COMPLETE_verses.csv"
    if not verses_path.exists():
        print(f"  [FAIL] Tanakh not found")
        return {}

    with open(verses_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            hebrew = row.get('hebrew', '')
            book = row.get('book', '')
            chapter = row.get('chapter', '')
            verse = row.get('verse', '')
            ref = f"{book} {chapter}:{verse}"

            for word in hebrew.split():
                # Clean word
                clean = ''.join(c for c in word if c in HEBREW_LETTERS)
                if clean:
                    if words[clean]['count'] == 0:
                        words[clean]['first_ref'] = ref
                    words[clean]['count'] += 1

    print(f"  [OK] Found {len(words)} unique Hebrew words")
    return words


def build_lexicon():
    """Build the complete lexicon"""
    print("=" * 60)
    print("BUILDING COMPLETE HEBREW LEXICON")
    print("=" * 60)
    print()

    # Load all source data
    strongs_data = load_strongs()
    ahlb_data = load_ahlb()
    control_words = load_control_words()
    unique_words = extract_unique_words()

    print()
    print("[INFO] Building lexicon entries...")

    lexicon = {}

    for hebrew, word_info in unique_words.items():
        # Analyze pictographically
        analysis = analyze_word(hebrew)

        # Create entry
        entry = LexiconEntry(
            hebrew=hebrew,
            letters=analysis['letters'],
            pictographic_meaning=analysis['pictographic_meaning'],
            gematria=analysis['gematria'],
            digital_root=analysis['digital_root'],
            frequency=word_info['count'],
            first_occurrence=word_info['first_ref']
        )

        # Add Strong's data if available
        if hebrew in strongs_data:
            sdata = strongs_data[hebrew]
            entry.strongs = sdata.get('strongs', '')
            entry.transliteration = sdata.get('translit', '')
            entry.definition = sdata.get('definition', '')
            entry.root = sdata.get('root', '')

            # Check AHLB
            if entry.strongs and entry.strongs in ahlb_data:
                entry.ahlb_entry = ahlb_data[entry.strongs]

            # Check control words
            if entry.strongs and entry.strongs in control_words:
                cw = control_words[entry.strongs]
                entry.is_control_word = True
                entry.control_mechanism = cw.get('control_mechanism', '')

        lexicon[hebrew] = entry

    print(f"[OK] Built {len(lexicon)} lexicon entries")

    # Count stats
    with_strongs = sum(1 for e in lexicon.values() if e.strongs)
    with_ahlb = sum(1 for e in lexicon.values() if e.ahlb_entry)
    control_count = sum(1 for e in lexicon.values() if e.is_control_word)

    print(f"  - With Strong's: {with_strongs}")
    print(f"  - With AHLB: {with_ahlb}")
    print(f"  - Control words: {control_count}")

    return lexicon


def save_lexicon(lexicon: Dict[str, LexiconEntry]):
    """Save the lexicon"""
    print()
    print("[INFO] Saving lexicon...")

    # Convert to dict
    lexicon_data = {
        'metadata': {
            'title': 'Complete Hebrew Lexicon',
            'description': 'Every Hebrew word with pictographic analysis',
            'generated': datetime.now().isoformat(),
            'total_words': len(lexicon),
            'sources': [
                "Strong's Concordance",
                "Ancient Hebrew Lexicon of the Bible (Jeff Benner)",
                "Proto-Sinaitic pictographic analysis",
                "Tanakh word frequency"
            ]
        },
        'entries': {k: asdict(v) for k, v in lexicon.items()}
    }

    # Save JSON
    json_path = OUTPUT_DIR / "hebrew_lexicon_complete.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(lexicon_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {json_path}")

    # Save by Strong's number
    strongs_index = {}
    for hebrew, entry in lexicon.items():
        if entry.strongs:
            strongs_index[entry.strongs] = asdict(entry)

    strongs_path = OUTPUT_DIR / "lexicon_by_strongs.json"
    with open(strongs_path, 'w', encoding='utf-8') as f:
        json.dump(strongs_index, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {strongs_path}")

    # Save by gematria
    gematria_index = defaultdict(list)
    for hebrew, entry in lexicon.items():
        if entry.gematria > 0:
            gematria_index[entry.gematria].append({
                'hebrew': hebrew,
                'meaning': entry.pictographic_meaning,
                'definition': entry.definition
            })

    gematria_path = OUTPUT_DIR / "lexicon_by_gematria.json"
    with open(gematria_path, 'w', encoding='utf-8') as f:
        json.dump(dict(gematria_index), f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {gematria_path}")

    # Save control words
    control_entries = {k: asdict(v) for k, v in lexicon.items() if v.is_control_word}
    control_path = OUTPUT_DIR / "control_words_lexicon.json"
    with open(control_path, 'w', encoding='utf-8') as f:
        json.dump(control_entries, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {control_path}")


def main():
    """Main entry point"""
    lexicon = build_lexicon()
    save_lexicon(lexicon)

    print()
    print("=" * 60)
    print("[OK] HEBREW LEXICON COMPLETE")
    print(f"Output: {OUTPUT_DIR}")
    print("=" * 60)

    # Show sample
    print()
    print("SAMPLE ENTRY - בראשית:")
    if 'בראשית' in lexicon:
        entry = lexicon['בראשית']
        print(f"  Hebrew: {entry.hebrew}")
        print(f"  Pictographic: {entry.pictographic_meaning}")
        print(f"  Gematria: {entry.gematria}")
        print(f"  Frequency: {entry.frequency}")
        print(f"  First: {entry.first_occurrence}")


if __name__ == '__main__':
    main()
