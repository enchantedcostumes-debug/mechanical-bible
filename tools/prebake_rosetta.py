#!/usr/bin/env python3
"""
PRE-BAKE ROSETTA DATA - Mechanical Bible
==========================================
Extracts verse-level gematria/divine pattern data from
Flask's tanakh_COMPLETE_verses.csv into per-book JSON files
that the browser can fetch.

Output: data/rosetta/<book>.json
Each file: { "1": { "1": {...}, "2": {...} }, "2": { ... } }
           chapter -> verse -> {gematria, digital_root, divine_patterns, word_gematrias}

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import csv
import json
import os
from pathlib import Path
from collections import defaultdict

FLASK_DIR = Path(r'C:\flask-structural-api')
VERSES_CSV = FLASK_DIR / 'services' / 'rosetta_stone' / 'data' / 'tanakh_COMPLETE_verses.csv'
OUTPUT_DIR = Path(__file__).parent.parent / 'data' / 'rosetta'

# Map CSV book names to our folder names
BOOK_MAP = {
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


def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True


SACRED_NUMBERS = {3, 7, 12, 13, 26, 40, 72, 144, 153, 216, 288, 432, 888}


def build_rosetta_text(gematria, dr, word_gematrias, divine_patterns):
    """Build a compact Rosetta translation line from gematria data."""
    parts = []
    parts.append(f'[{gematria}]')
    if dr:
        parts.append(f'DR:{dr}')
    if is_prime(gematria):
        parts.append('PRIME')
    if gematria in SACRED_NUMBERS:
        parts.append('SACRED')
    if divine_patterns and divine_patterns != 'Standard':
        parts.append(divine_patterns)
    if word_gematrias:
        parts.append('(' + ' '.join(word_gematrias.split('|')) + ')')
    return ' '.join(parts)


def main():
    if not VERSES_CSV.exists():
        print(f'ERROR: CSV not found at {VERSES_CSV}')
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read all verses, grouped by book
    books = defaultdict(lambda: defaultdict(dict))
    total = 0

    with open(VERSES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book = row['book']
            ch = row['chapter']
            vs = row['verse']
            gematria = int(row.get('gematria', 0))
            dr = digital_root(gematria) if gematria else 0
            word_gematrias = row.get('word_gematrias', '')
            divine = row.get('divine_patterns', '')

            folder = BOOK_MAP.get(book)
            if not folder:
                continue

            books[folder][ch][vs] = {
                'g': gematria,
                'dr': dr,
                'wg': word_gematrias,
                'dp': divine,
                'text': build_rosetta_text(gematria, dr, word_gematrias, divine)
            }
            total += 1

    # Write per-book JSON files
    for folder, chapters in books.items():
        outpath = OUTPUT_DIR / f'{folder}.json'
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, ensure_ascii=False, separators=(',', ':'))
        verse_count = sum(len(vs) for vs in chapters.values())
        print(f'  {folder}: {len(chapters)} chapters, {verse_count} verses')

    print(f'\n[DONE] Pre-baked {total} verses across {len(books)} books into {OUTPUT_DIR}')


if __name__ == '__main__':
    print('=' * 60)
    print('PRE-BAKE ROSETTA DATA - Mechanical Bible')
    print('=' * 60)
    main()
