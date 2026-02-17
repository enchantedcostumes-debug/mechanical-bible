#!/usr/bin/env python3
"""
Fix verse anchors - the original regex ate the verse-ref div.
This script restores the verse-ref text by parsing the id attribute.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')


def find_all_chapters():
    """Find all chapter HTML files."""
    chapters = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        skip_dirs = {'tools', 'css', 'js', 'data', '.git', 'node_modules', 'img', 'images'}
        rel = os.path.relpath(root, PROJECT_ROOT)
        if any(part in skip_dirs for part in rel.split(os.sep)):
            continue
        for f in files:
            if re.match(r'^\d+\.html$', f):
                chapters.append(os.path.join(root, f))
    return sorted(chapters)


def get_book_name(filepath):
    """Extract book name from directory name."""
    rel = os.path.relpath(filepath, PROJECT_ROOT)
    book_dir = rel.split(os.sep)[0]
    # Convert directory name to proper book name
    name_map = {
        'genesis': 'Genesis', 'exodus': 'Exodus', 'leviticus': 'Leviticus',
        'numbers': 'Numbers', 'deuteronomy': 'Deuteronomy',
        'joshua': 'Joshua', 'judges': 'Judges', 'ruth': 'Ruth',
        'i_samuel': '1 Samuel', 'ii_samuel': '2 Samuel',
        'i_kings': '1 Kings', 'ii_kings': '2 Kings',
        'i_chronicles': '1 Chronicles', 'ii_chronicles': '2 Chronicles',
        'ezra': 'Ezra', 'nehemiah': 'Nehemiah', 'esther': 'Esther',
        'job': 'Job', 'psalms': 'Psalms', 'proverbs': 'Proverbs',
        'ecclesiastes': 'Ecclesiastes', 'song_of_solomon': 'Song of Solomon',
        'isaiah': 'Isaiah', 'jeremiah': 'Jeremiah', 'lamentations': 'Lamentations',
        'ezekiel': 'Ezekiel', 'daniel': 'Daniel',
        'hosea': 'Hosea', 'joel': 'Joel', 'amos': 'Amos',
        'obadiah': 'Obadiah', 'jonah': 'Jonah', 'micah': 'Micah',
        'nahum': 'Nahum', 'habakkuk': 'Habakkuk', 'zephaniah': 'Zephaniah',
        'haggai': 'Haggai', 'zechariah': 'Zechariah', 'malachi': 'Malachi',
        'matthew': 'Matthew', 'mark': 'Mark', 'luke': 'Luke', 'john': 'John',
        'acts': 'Acts', 'romans': 'Romans',
        '1_corinthians': '1 Corinthians', '2_corinthians': '2 Corinthians',
        'galatians': 'Galatians', 'ephesians': 'Ephesians',
        'philippians': 'Philippians', 'colossians': 'Colossians',
        '1_thessalonians': '1 Thessalonians', '2_thessalonians': '2 Thessalonians',
        '1_timothy': '1 Timothy', '2_timothy': '2 Timothy',
        'titus': 'Titus', 'philemon': 'Philemon',
        'hebrews': 'Hebrews', 'james': 'James',
        '1_peter': '1 Peter', '2_peter': '2 Peter',
        '1_john': '1 John', '2_john': '2 John', '3_john': '3 John',
        'jude': 'Jude', 'revelation': 'Revelation',
    }
    return name_map.get(book_dir, book_dir.replace('_', ' ').title())


def fix_chapter(filepath):
    """Fix verse anchors that lost their verse-ref divs."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    book_name = get_book_name(filepath)
    modified = False

    # Find broken pattern: <div class="verse" id="vX-Y"><span class="verse-gematria">
    # Should be: <div class="verse" id="vX-Y">\n<div class="verse-ref">Book X:Y\n<span class="verse-gematria">
    pattern = r'<div class="verse" id="v(\d+)-(\d+)"><span class="verse-gematria">'

    def restore_verse_ref(match):
        chapter = match.group(1)
        verse = match.group(2)
        return (
            f'<div class="verse" id="v{chapter}-{verse}">\n'
            f'                <div class="verse-ref">{book_name} {chapter}:{verse}\n'
            f'                    <span class="verse-gematria">'
        )

    new_content = re.sub(pattern, restore_verse_ref, content)
    if new_content != content:
        modified = True
        content = new_content

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return modified


def main():
    chapters = find_all_chapters()
    print(f'[OK] Found {len(chapters)} chapter files')

    fixed = 0
    ok = 0

    for filepath in chapters:
        rel = os.path.relpath(filepath, PROJECT_ROOT)
        try:
            if fix_chapter(filepath):
                fixed += 1
                if fixed <= 5 or fixed % 100 == 0:
                    print(f'  [FIX] {rel}')
            else:
                ok += 1
        except Exception as e:
            print(f'  [FAIL] {rel}: {e}')

    print()
    print('=' * 60)
    print(f'[OK] Fixed: {fixed}')
    print(f'[--] Already OK: {ok}')
    print(f'[OK] Total: {len(chapters)}')
    print('=' * 60)


if __name__ == '__main__':
    main()
