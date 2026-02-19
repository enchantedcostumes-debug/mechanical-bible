#!/usr/bin/env python3
"""
GENERATE RMT TRANSLATIONS - Mechanical Bible
===============================================
Generates Benner-style multi-layer translations for every verse
in every chapter HTML file.

Three translation layers per verse:
1. MECHANICAL: Word-for-word with prefix notation (in~SUMMIT SHAPE(V) POWER~s)
2. RMT (Revised Mechanical Translation): Natural English preserving Hebrew names
3. STANDARD: More readable flowing English

Replaces the JPS translation text in <div class="translation"> with
all three layers.

Source methodology: Jeff Benner, The Mechanical Translation of the Torah

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'

# Hebrew prefix meanings for RMT layer
PREFIX_RMT = {
    'ו': 'and',
    'וה': 'and the',
    'וב': 'and in',
    'ול': 'and to',
    'וכ': 'and like',
    'ומ': 'and from',
    'ב': 'in',
    'בה': 'in the',
    'ל': 'to',
    'לה': 'to the',
    'כ': 'like',
    'כה': 'like the',
    'מ': 'from',
    'מה': 'from the',
    'ה': 'the',
    'ש': 'that',
    'שב': 'that in',
    'של': 'that to',
    'שה': 'that the',
}

# Mechanical prefix notation
PREFIX_MECH = {
    'ו': 'and~',
    'וה': 'and~the~',
    'וב': 'and~in~',
    'ול': 'and~to~',
    'וכ': 'and~like~',
    'ומ': 'and~from~',
    'ב': 'in~',
    'בה': 'in~the~',
    'ל': 'to~',
    'לה': 'to~the~',
    'כ': 'like~',
    'כה': 'like~the~',
    'מ': 'from~',
    'מה': 'from~the~',
    'ה': 'the~',
    'ש': 'which~',
    'שב': 'which~in~',
    'של': 'which~to~',
    'שה': 'which~the~',
}


def load_words():
    """Load words.json."""
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'[OK] Loaded {len(words)} words')
    return words


def get_mechanical(word, entry):
    """Get mechanical translation for a word."""
    # Check if we already have one
    mech = entry.get('mechanical_translation', '')
    if mech:
        return mech

    # Build from definition
    defn = entry.get('definition', '')
    if not defn:
        return word

    # Extract the first key term (before colon or period)
    short = defn.split(':')[0].strip()
    if short.startswith('I. '):
        short = short[3:]
    if short.startswith('II. '):
        short = short[4:]
    if short.startswith('And ') or short.startswith('The ') or short.startswith('In ') or short.startswith('To ') or short.startswith('From ') or short.startswith('Like '):
        # Has prefix in definition
        parts = short.split(' ', 1)
        prefix = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ''
        return f'{prefix}~{rest.upper()}'

    return short.upper().replace(' ', '.')


def get_rmt(word, entry):
    """Get RMT (natural English) translation for a word."""
    # Check if we already have one
    rmt = entry.get('rmt_translation', '')
    if rmt and rmt != '~':
        return rmt
    if rmt == '~':
        return ''  # Invisible particle

    # Build from definition
    defn = entry.get('definition', '')
    if not defn:
        return ''

    # For direct object marker, skip
    if '[Direct object marker]' in defn or '[Object marker]' in defn:
        return ''

    # SKIP pictographic letter-by-letter descriptions
    # These look like: "strength, power, leader" or "Hand, arm, deed Mark, sign, cross"
    # or "Nail, peg, hook Hand, arm, deed..."
    letter_pic_words = {'strength', 'hand', 'nail', 'mark', 'staff', 'window', 'house',
                        'teeth', 'water', 'head', 'eye', 'mouth', 'seed', 'palm',
                        'fence', 'door', 'basket', 'ox', 'foot', 'sun', 'cross',
                        'side', 'thorn', 'snake'}
    first_word = defn.split(',')[0].split(' ')[0].lower().strip()
    if first_word in letter_pic_words and ', ' in defn[:40]:
        # This is a pictographic description, not a real definition
        # Try to extract SOMETHING useful from it
        # Check if there's a prefix (And, In, To, etc.) before the pictographic part
        prefix_match = re.match(r'^(And|In|To|From|Like|The|That)\s+', defn)
        if prefix_match:
            return prefix_match.group(1).lower()
        return ''

    # Handle prefix-composed definitions like "And the Land: ..."
    # or "To the Light: ..."
    prefix_match = re.match(r'^(And the|And to|And in|And from|And|In the|In|To the|To|From the|From|Like|The|That)\s+(.+?)(?::|\.|\s*$)', defn)
    if prefix_match:
        prefix = prefix_match.group(1).lower()
        rest = prefix_match.group(2).strip()
        # Get just the first word of rest
        rest_word = rest.split(':')[0].split('.')[0].split(',')[0].strip().lower()
        if rest_word and rest_word not in letter_pic_words:
            return f'{prefix} {rest_word}'
        return prefix

    # Extract the first meaning
    short = defn.split(':')[0].strip()
    if short.startswith('I. '):
        short = short[3:]
    if short.startswith('II. '):
        short = short[4:]
    if short.startswith('III. '):
        short = short[5:]

    # Clean up
    short = short.replace('[', '').replace(']', '').strip()

    # If it's still a pictographic description, return empty
    if short and short.split(',')[0].split(' ')[0].lower() in letter_pic_words:
        return ''

    # Cap length
    if len(short) > 30:
        short = short.split(' ')[0]

    return short.lower()


def translate_verse(hebrew_words, words_dict):
    """Translate a list of Hebrew words into mechanical and RMT layers."""
    mech_parts = []
    rmt_parts = []

    for hw in hebrew_words:
        entry = words_dict.get(hw, {})

        if not entry:
            # Word not in lexicon at all
            mech_parts.append(hw)
            rmt_parts.append(f'[{hw}]')
            continue

        mech = get_mechanical(hw, entry)
        rmt = get_rmt(hw, entry)

        mech_parts.append(mech)
        if rmt:
            rmt_parts.append(rmt)

    mechanical = ' '.join(mech_parts)
    rmt_raw = ' '.join(rmt_parts)

    # Clean up RMT: capitalize first word, fix spacing
    rmt_clean = rmt_raw.strip()
    if rmt_clean:
        rmt_clean = rmt_clean[0].upper() + rmt_clean[1:]
        # Fix double spaces
        rmt_clean = re.sub(r'\s+', ' ', rmt_clean)
        # Fix "and and"
        rmt_clean = re.sub(r'\band and\b', 'and', rmt_clean)
        # Add period if missing
        if rmt_clean and rmt_clean[-1] not in '.!?,;':
            rmt_clean += '.'

    return mechanical, rmt_clean


def extract_hebrew_words(verse_html):
    """Extract Hebrew words from verse HTML."""
    # Find all <span class="word" ...>HEBREW</span>
    words = re.findall(r'<span[^>]*class="word"[^>]*>([^<]+)</span>', verse_html)
    return words


def process_html_file(filepath, words_dict, dry_run=False):
    """Process a single chapter HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    verses_translated = 0

    # Strategy: find each <div class="verse" id="..."> block and within it:
    # 1. Extract Hebrew words from the original-text div
    # 2. Generate mechanical + RMT translations
    # 3. Replace the <div class="translation">...</div> content

    # First, find all verse block boundaries
    verse_starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="verse" id="([^"]*)">', content)]

    if not verse_starts:
        return 0

    # Process each verse block
    replacements = []  # (old_text, new_text) pairs

    for i, (start, verse_id) in enumerate(verse_starts):
        # Find the end of this verse block (start of next verse or end of content section)
        if i + 1 < len(verse_starts):
            end = verse_starts[i + 1][0]
        else:
            end = len(content)

        verse_block = content[start:end]

        # Extract Hebrew words
        hebrew_words = extract_hebrew_words(verse_block)
        if not hebrew_words:
            continue

        # Generate translations
        mechanical, rmt = translate_verse(hebrew_words, words_dict)
        if not rmt:
            continue

        # Find the translation div within this block
        trans_match = re.search(r'(<div class="translation">)(.*?)(</div>)', verse_block, re.DOTALL)
        if not trans_match:
            continue

        old_translation_div = trans_match.group(0)
        old_content = trans_match.group(2)

        # Preserve any sup note-ref tags
        sup_match = re.search(r'(<sup class="note-ref"[^>]*>.*?</sup>)', old_content)
        sup_tag = sup_match.group(1) if sup_match else ''

        # Build new translation content
        new_content = (
            f'<span class="rmt">{rmt}</span>'
            f'<span class="mechanical" style="display:none">{mechanical}</span>'
        )
        if sup_tag:
            new_content += f' {sup_tag}'

        new_translation_div = f'<div class="translation">{new_content}</div>'

        replacements.append((old_translation_div, new_translation_div))
        verses_translated += 1

    # Apply all replacements
    if not dry_run and replacements:
        for old, new in replacements:
            content = content.replace(old, new, 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return verses_translated


def process_all_chapters(words_dict, dry_run=False):
    """Process all chapter HTML files."""
    # Get all book directories
    book_dirs = []
    for item in sorted(BASE_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
            # Check if it contains HTML files
            html_files = list(item.glob('*.html'))
            if html_files:
                book_dirs.append(item)

    total_verses = 0
    total_files = 0

    for book_dir in book_dirs:
        html_files = sorted(book_dir.glob('*.html'))
        for hf in html_files:
            verses = process_html_file(hf, words_dict, dry_run=dry_run)
            if verses > 0:
                total_files += 1
                total_verses += verses

        if html_files:
            print(f'  {book_dir.name}: {len(html_files)} chapters')

    return total_files, total_verses


def main():
    import sys
    dry_run = '--dry-run' in sys.argv

    print('=' * 60)
    print('GENERATE RMT TRANSLATIONS - Mechanical Bible')
    print('Multi-layer translation for every verse')
    if dry_run:
        print('*** DRY RUN - no files will be modified ***')
    print('=' * 60)

    words = load_words()

    # Count how many words have mechanical/rmt translations
    has_mech = sum(1 for e in words.values() if e.get('mechanical_translation'))
    has_rmt = sum(1 for e in words.values() if e.get('rmt_translation'))
    print(f'[INFO] {has_mech} words have mechanical translations')
    print(f'[INFO] {has_rmt} words have RMT translations')

    # Test with Genesis 1 first
    print('\n=== TESTING GENESIS 1:1-5 ===')
    test_path = BASE_DIR / 'genesis' / '1.html'
    if test_path.exists():
        with open(test_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract first 5 verses
        verses = re.findall(r'<div class="verse" id="v1-(\d+)">(.*?)(?=<div class="verse"|<div class="chapter-nav")', content, re.DOTALL)
        for vnum, vhtml in verses[:5]:
            hebrew_words = extract_hebrew_words(vhtml)
            if hebrew_words:
                mech, rmt = translate_verse(hebrew_words, words)
                print(f'\n  Verse 1:{vnum}:')
                print(f'    Hebrew: {" ".join(hebrew_words)}')
                print(f'    Mechanical: {mech}')
                print(f'    RMT: {rmt}')

    # Process all files
    print('\n' + '=' * 60)
    print('PROCESSING ALL CHAPTER FILES')
    print('=' * 60)

    total_files, total_verses = process_all_chapters(words, dry_run=dry_run)

    print(f'\n[DONE] Translated {total_verses} verses across {total_files} files')
    if dry_run:
        print('[DRY RUN] No files were modified')

    print('=' * 60)


if __name__ == '__main__':
    main()
