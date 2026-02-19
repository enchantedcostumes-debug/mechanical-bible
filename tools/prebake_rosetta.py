#!/usr/bin/env python3
"""
PRE-BAKE ROSETTA DATA - Mechanical Bible
==========================================
Pairs each Hebrew word with its English definition from words.json
(58,443 entries with definitions, mechanical translations, Strong's numbers).

Source data:
  - words.json:  C:\mechanical-bible\words.json (the master word dictionary)
  - Verses CSV:  C:\flask-structural-api\...\tanakh_COMPLETE_verses.csv

Output: data/rosetta/<book>.json
  { "1": { "1": { "text": "בראשית(In the summit) ברא(Shape) ...", "g": 2701, "dr": 1 } } }

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'
FLASK_DIR = Path(r'C:\flask-structural-api')
VERSES_CSV = FLASK_DIR / 'services' / 'rosetta_stone' / 'data' / 'tanakh_COMPLETE_verses.csv'
OUTPUT_DIR = BASE_DIR / 'data' / 'rosetta'

# Map CSV book names to folder names
CSV_TO_FOLDER = {
    'Genesis': 'genesis', 'Exodus': 'exodus', 'Leviticus': 'leviticus',
    'Numbers': 'numbers', 'Deuteronomy': 'deuteronomy', 'Joshua': 'joshua',
    'Judges': 'judges', 'Ruth': 'ruth', '1 Samuel': '1_samuel',
    '2 Samuel': '2_samuel', '1 Kings': '1_kings', '2 Kings': '2_kings',
    '1 Chronicles': '1_chronicles', '2 Chronicles': '2_chronicles',
    'Ezra': 'ezra', 'Nehemiah': 'nehemiah', 'Esther': 'esther',
    'Job': 'job', 'Psalms': 'psalms', 'Proverbs': 'proverbs',
    'Ecclesiastes': 'ecclesiastes', 'Song of Songs': 'song_of_songs',
    'Isaiah': 'isaiah', 'Jeremiah': 'jeremiah', 'Lamentations': 'lamentations',
    'Ezekiel': 'ezekiel', 'Daniel': 'daniel', 'Hosea': 'hosea',
    'Joel': 'joel', 'Amos': 'amos', 'Obadiah': 'obadiah',
    'Jonah': 'jonah', 'Micah': 'micah', 'Nahum': 'nahum',
    'Habakkuk': 'habakkuk', 'Zephaniah': 'zephaniah', 'Haggai': 'haggai',
    'Zechariah': 'zechariah', 'Malachi': 'malachi'
}


def digital_root(n):
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def shorten_def(definition):
    """Extract the short label from a definition.
    'In the summit: At the head/beginning...' -> 'In the summit'
    'Shape: To fatten, fill up...' -> 'Shape'
    'The skies: The upper region above.' -> 'The skies'
    """
    if not definition:
        return '?'
    # Take text before the colon (that's the short label)
    if ':' in definition:
        short = definition.split(':')[0].strip()
        if short:
            # Strip leading [ ] brackets for markers like [Direct object marker]
            short = re.sub(r'^\[(.+)\]$', r'\1', short)
            return short
    # No colon — take first phrase
    d = re.sub(r'\s*\(.*?\)', '', definition)
    parts = re.split(r'[;,.]', d)
    return parts[0].strip() or '?'


def main():
    if not WORDS_JSON.exists():
        print(f'ERROR: words.json not found at {WORDS_JSON}')
        return
    if not VERSES_CSV.exists():
        print(f'ERROR: CSV not found at {VERSES_CSV}')
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load word dictionary
    print(f'Loading words.json...')
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'  {len(words)} word entries loaded')

    # Process verses
    books = defaultdict(lambda: defaultdict(dict))
    total = 0
    matched = 0
    unmatched = 0

    with open(VERSES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book = row['book']
            folder = CSV_TO_FOLDER.get(book)
            if not folder:
                continue

            ch = row['chapter']
            vs = row['verse']
            hebrew_text = row.get('hebrew', '')
            gematria = int(row.get('gematria', 0))
            dr = digital_root(gematria) if gematria else 0

            # Split Hebrew verse into words
            heb_words = hebrew_text.split()

            # Build rosetta pairs
            pairs = []
            for hw in heb_words:
                entry = words.get(hw)
                if entry and entry.get('definition'):
                    eng = shorten_def(entry['definition'])
                    pairs.append(f'{hw}({eng})')
                    matched += 1
                else:
                    pairs.append(f'{hw}(?)')
                    unmatched += 1

            books[folder][ch][vs] = {
                'text': ' '.join(pairs),
                'g': gematria,
                'dr': dr,
            }
            total += 1

    # Write per-book JSON files
    print(f'\nWriting JSON files...')
    for folder, chapters in sorted(books.items()):
        outpath = OUTPUT_DIR / f'{folder}.json'
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, ensure_ascii=False, separators=(',', ':'))
        verse_count = sum(len(vs) for vs in chapters.values())
        print(f'  {folder}: {len(chapters)} chapters, {verse_count} verses')

    total_words = matched + unmatched
    pct = (matched / total_words * 100) if total_words else 0
    print(f'\n[DONE] Pre-baked {total} verses across {len(books)} books')
    print(f'  Word matches: {matched}/{total_words} ({pct:.1f}%)')
    print(f'  Unmatched: {unmatched}')


if __name__ == '__main__':
    print('=' * 60)
    print('PRE-BAKE ROSETTA DATA - Mechanical Bible')
    print('=' * 60)
    main()
