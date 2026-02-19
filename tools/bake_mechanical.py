#!/usr/bin/env python3
"""
Bake Mechanical Translations into HTML - Mechanical Bible
============================================================
Updates the <span class="mechanical"> content in all chapter HTML files
with the generated Benner-method mechanical translations from JSON.

Reads: data/mechanical/<book>.json
Updates: <book>/<chapter>.html

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'mechanical'

# Map JSON book names to HTML folder names
BOOK_FOLDERS = {
    'genesis': 'genesis',
    'exodus': 'exodus',
    'leviticus': 'leviticus',
    'numbers': 'numbers',
    'deuteronomy': 'deuteronomy',
    'joshua': 'joshua',
    'judges': 'judges',
    'ruth': 'ruth',
    '1_samuel': 'i_samuel',
    '2_samuel': 'ii_samuel',
    '1_kings': 'i_kings',
    '2_kings': 'ii_kings',
    '1_chronicles': 'i_chronicles',
    '2_chronicles': 'ii_chronicles',
    'ezra': 'ezra',
    'nehemiah': 'nehemiah',
    'esther': 'esther',
    'job': 'job',
    'psalms': 'psalms',
    'proverbs': 'proverbs',
    'ecclesiastes': 'ecclesiastes',
    'song_of_songs': 'song_of_songs',
    'isaiah': 'isaiah',
    'jeremiah': 'jeremiah',
    'lamentations': 'lamentations',
    'ezekiel': 'ezekiel',
    'daniel': 'daniel',
    'hosea': 'hosea',
    'joel': 'joel',
    'amos': 'amos',
    'obadiah': 'obadiah',
    'jonah': 'jonah',
    'micah': 'micah',
    'nahum': 'nahum',
    'habakkuk': 'habakkuk',
    'zephaniah': 'zephaniah',
    'haggai': 'haggai',
    'zechariah': 'zechariah',
    'malachi': 'malachi',
}


def bake_chapter(html_path, chapter_data, book_name, chapter_num):
    """Replace mechanical span contents in one HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    updated = 0
    missing = 0

    for verse_num, verse_data in chapter_data.items():
        mech_text = verse_data['text']

        # Pattern: find the verse div and replace its mechanical span content
        # The verse id format is v{chapter}-{verse}
        verse_id = f'v{chapter_num}-{verse_num}'

        # Find the mechanical span within this verse's section
        # We need to find the span after the verse id marker
        pattern = (
            r'(id="' + re.escape(verse_id) + r'".*?'
            r'<span class="mechanical">)(.*?)(</span>)'
        )
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start(2)] + mech_text + content[match.end(2):]
            updated += 1
        else:
            missing += 1

    if content != original:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return updated, missing


def main():
    total_updated = 0
    total_missing = 0
    total_files = 0

    for book_key, folder_name in BOOK_FOLDERS.items():
        json_path = DATA_DIR / f'{book_key}.json'
        if not json_path.exists():
            print(f'  SKIP {book_key}: no JSON data')
            continue

        with open(json_path, 'r', encoding='utf-8') as f:
            book_data = json.load(f)

        book_folder = BASE_DIR / folder_name
        if not book_folder.exists():
            print(f'  SKIP {book_key}: no HTML folder at {book_folder}')
            continue

        book_updated = 0
        book_missing = 0

        for chapter_num, chapter_data in sorted(book_data.items(), key=lambda x: int(x[0])):
            html_path = book_folder / f'{chapter_num}.html'
            if not html_path.exists():
                continue

            u, m = bake_chapter(html_path, chapter_data, book_key, chapter_num)
            book_updated += u
            book_missing += m
            total_files += 1

        total_updated += book_updated
        total_missing += book_missing
        print(f'  {folder_name}: {book_updated} verses updated, {book_missing} missing spans')

    print(f'\n[DONE] Updated {total_updated} verses across {total_files} HTML files')
    if total_missing:
        print(f'  {total_missing} verses had no matching mechanical span in HTML')


if __name__ == '__main__':
    print('=' * 60)
    print('BAKE MECHANICAL TRANSLATIONS INTO HTML')
    print('  Updating <span class="mechanical"> in all chapter files')
    print('=' * 60)
    main()
