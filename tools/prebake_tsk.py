#!/usr/bin/env python3
"""
PRE-BAKE TSK CROSS-REFERENCES - Mechanical Bible
==================================================
Converts the OpenBible.info TSK dataset (344,800 cross-references)
into per-book JSON files the browser can fetch.

Source: data/tsk_raw.txt (tab-separated: FromVerse  ToVerse  Votes)
Format: Gen.1.1  Prov.8.22-Prov.8.30  59

Output: data/tsk/<book>.json
  { "1": { "1": [ {"ref": "Proverbs 8:22-30", "votes": 59}, ... ] } }

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
RAW_FILE = BASE_DIR / 'data' / 'tsk_raw.txt'
OUTPUT_DIR = BASE_DIR / 'data' / 'tsk'

# Abbreviation -> full name + folder
BOOK_ABBREV = {
    'Gen': ('Genesis', 'genesis'), 'Exod': ('Exodus', 'exodus'),
    'Lev': ('Leviticus', 'leviticus'), 'Num': ('Numbers', 'numbers'),
    'Deut': ('Deuteronomy', 'deuteronomy'), 'Josh': ('Joshua', 'joshua'),
    'Judg': ('Judges', 'judges'), 'Ruth': ('Ruth', 'ruth'),
    '1Sam': ('1 Samuel', 'i_samuel'), '2Sam': ('2 Samuel', 'ii_samuel'),
    '1Kgs': ('1 Kings', 'i_kings'), '2Kgs': ('2 Kings', 'ii_kings'),
    '1Chr': ('1 Chronicles', 'i_chronicles'), '2Chr': ('2 Chronicles', 'ii_chronicles'),
    'Ezra': ('Ezra', 'ezra'), 'Neh': ('Nehemiah', 'nehemiah'),
    'Esth': ('Esther', 'esther'), 'Job': ('Job', 'job'),
    'Ps': ('Psalms', 'psalms'), 'Prov': ('Proverbs', 'proverbs'),
    'Eccl': ('Ecclesiastes', 'ecclesiastes'), 'Song': ('Song of Songs', 'song_of_songs'),
    'Isa': ('Isaiah', 'isaiah'), 'Jer': ('Jeremiah', 'jeremiah'),
    'Lam': ('Lamentations', 'lamentations'), 'Ezek': ('Ezekiel', 'ezekiel'),
    'Dan': ('Daniel', 'daniel'), 'Hos': ('Hosea', 'hosea'),
    'Joel': ('Joel', 'joel'), 'Amos': ('Amos', 'amos'),
    'Obad': ('Obadiah', 'obadiah'), 'Jonah': ('Jonah', 'jonah'),
    'Mic': ('Micah', 'micah'), 'Nah': ('Nahum', 'nahum'),
    'Hab': ('Habakkuk', 'habakkuk'), 'Zeph': ('Zephaniah', 'zephaniah'),
    'Hag': ('Haggai', 'haggai'), 'Zech': ('Zechariah', 'zechariah'),
    'Mal': ('Malachi', 'malachi'),
    'Matt': ('Matthew', 'matthew'), 'Mark': ('Mark', 'mark'),
    'Luke': ('Luke', 'luke'), 'John': ('John', 'john'),
    'Acts': ('Acts', 'acts'), 'Rom': ('Romans', 'romans'),
    '1Cor': ('1 Corinthians', '1_corinthians'), '2Cor': ('2 Corinthians', '2_corinthians'),
    'Gal': ('Galatians', 'galatians'), 'Eph': ('Ephesians', 'ephesians'),
    'Phil': ('Philippians', 'philippians'), 'Col': ('Colossians', 'colossians'),
    '1Thess': ('1 Thessalonians', '1_thessalonians'), '2Thess': ('2 Thessalonians', '2_thessalonians'),
    '1Tim': ('1 Timothy', '1_timothy'), '2Tim': ('2 Timothy', '2_timothy'),
    'Titus': ('Titus', 'titus'), 'Phlm': ('Philemon', 'philemon'),
    'Heb': ('Hebrews', 'hebrews'), 'Jas': ('James', 'james'),
    '1Pet': ('1 Peter', '1_peter'), '2Pet': ('2 Peter', '2_peter'),
    '1John': ('1 John', '1_john'), '2John': ('2 John', '2_john'),
    '3John': ('3 John', '3_john'), 'Jude': ('Jude', 'jude'),
    'Rev': ('Revelation', 'revelation'),
}


def parse_ref(ref_str):
    """Parse 'Gen.1.1' or 'Prov.8.22-Prov.8.30' into readable form.

    Returns (book_abbrev, chapter, verse_str, readable) or None.
    """
    # Handle ranges like Prov.8.22-Prov.8.30
    if '-' in ref_str:
        parts = ref_str.split('-')
        start = parse_single_ref(parts[0])
        end = parse_single_ref(parts[-1])
        if start and end:
            s_book, s_ch, s_vs, s_full_name = start
            e_book, e_ch, e_vs, _ = end
            if s_book == e_book and s_ch == e_ch:
                readable = f'{s_full_name} {s_ch}:{s_vs}-{e_vs}'
            elif s_book == e_book:
                readable = f'{s_full_name} {s_ch}:{s_vs}-{e_ch}:{e_vs}'
            else:
                readable = f'{s_full_name} {s_ch}:{s_vs}'
            return (s_book, s_ch, s_vs, readable)
        return None
    return parse_single_ref(ref_str)


def parse_single_ref(ref_str):
    """Parse 'Gen.1.1' into (abbrev, chapter, verse, 'Genesis 1:1')."""
    parts = ref_str.split('.')
    if len(parts) < 3:
        return None
    abbrev = parts[0]
    info = BOOK_ABBREV.get(abbrev)
    if not info:
        return None
    full_name, folder = info
    ch = parts[1]
    vs = parts[2]
    return (abbrev, ch, vs, f'{full_name} {ch}:{vs}')


def main():
    if not RAW_FILE.exists():
        print(f'ERROR: Raw TSK file not found at {RAW_FILE}')
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parse raw data: group by source book/chapter/verse
    # books[folder][chapter][verse] = [ {ref, votes}, ... ]
    books = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    total_refs = 0
    skipped = 0

    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('From'):
                continue

            parts = line.split('\t')
            if len(parts) < 3:
                continue

            from_ref = parts[0]
            to_ref = parts[1]
            try:
                votes = int(parts[2])
            except ValueError:
                votes = 0

            # Skip negative votes (low quality)
            if votes < 0:
                skipped += 1
                continue

            # Parse source
            from_parsed = parse_single_ref(from_ref)
            if not from_parsed:
                skipped += 1
                continue

            from_abbrev, from_ch, from_vs, _ = from_parsed
            from_info = BOOK_ABBREV.get(from_abbrev)
            if not from_info:
                skipped += 1
                continue
            _, from_folder = from_info

            # Parse target
            to_parsed = parse_ref(to_ref)
            if not to_parsed:
                skipped += 1
                continue

            _, _, _, to_readable = to_parsed

            books[from_folder][from_ch][from_vs].append({
                'ref': to_readable,
                'v': votes,
            })
            total_refs += 1

    # Sort each verse's refs by vote count (highest first)
    for folder in books:
        for ch in books[folder]:
            for vs in books[folder][ch]:
                books[folder][ch][vs].sort(key=lambda x: -x['v'])

    # Write per-book JSON files
    print(f'Writing JSON files...')
    book_count = 0
    for folder in sorted(books.keys()):
        chapters = books[folder]
        outpath = OUTPUT_DIR / f'{folder}.json'
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, ensure_ascii=False, separators=(',', ':'))
        verse_count = sum(len(vs) for vs in chapters.values())
        ref_count = sum(
            len(refs) for ch in chapters.values() for refs in ch.values()
        )
        print(f'  {folder}: {len(chapters)} ch, {verse_count} vs, {ref_count} refs')
        book_count += 1

    # Write summary stats
    stats = {
        'total_books': book_count,
        'total_references': total_refs,
        'skipped': skipped,
        'source': 'OpenBible.info TSK (CC-BY)',
    }
    stats_path = OUTPUT_DIR / '_stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    print(f'\n[DONE] {total_refs} cross-references across {book_count} books')
    print(f'  Skipped: {skipped} (negative votes or parse errors)')


if __name__ == '__main__':
    print('=' * 60)
    print('PRE-BAKE TSK CROSS-REFERENCES - Mechanical Bible')
    print('=' * 60)
    main()
