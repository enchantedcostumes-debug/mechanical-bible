#!/usr/bin/env python3
"""
Fix compound Hebrew words in words.json.
Decomposes prefix+root combinations and builds readable definitions.
Uses the AHLB-sourced definitions already in words.json for root words.
"""
import json
import re
import csv
from pathlib import Path

BASE = Path(__file__).parent.parent
WORDS_JSON = BASE / 'words.json'

# Hebrew prepositions (multi-character, checked before single-letter)
PREPOSITIONS = [
    ('את', 'AT'),           # direct object marker
    ('אל', 'to'),           # toward
    ('על', 'upon'),          # upon/above
    ('עם', 'with'),          # with
    ('מן', 'from'),          # from
    ('אשר', 'which'),        # which/that
    ('פן', 'lest'),          # lest
    ('עד', 'until'),         # until
]

# Single-letter prefixes
PREFIXES = [
    ('ו', 'and'),
    ('ב', 'in'),
    ('ל', 'to'),
    ('מ', 'from'),
    ('ה', 'the'),
    ('כ', 'like'),
    ('ש', 'that'),
]

# Pronominal suffixes (most specific first)
SUFFIXES = [
    ('יהם', 'their'),
    ('יהן', 'their(f)'),
    ('ינו', 'our'),
    ('יכם', 'your(pl)'),
    ('הם', 'their'),
    ('הן', 'their(f)'),
    ('כם', 'your(pl)'),
    ('נו', 'us'),
    ('ני', 'me'),
    ('הו', 'him'),
    ('ך', 'your'),
    ('ו', 'his'),
    ('ה', 'her'),
    ('י', 'my'),
    ('ם', 'them'),
    ('ן', 'them(f)'),
]


def shorten_def(definition):
    if not definition:
        return '?'
    if ':' in definition:
        short = definition.split(':')[0].strip()
        if short:
            short = re.sub(r'^\[(.+)\]$', r'\1', short)
            return short
    d = re.sub(r'\s*\(.*?\)', '', definition)
    parts = re.split(r'[;,.]', d)
    return parts[0].strip() or '?'


def decompose(word, root_lookup):
    """Try to decompose a Hebrew compound word into prefix(es) + root + suffix.
    Returns (prefix_str, root_def) or None."""

    best_result = None
    best_root_len = 0

    # Try all combinations of prefix stripping
    def try_prefixes(remaining, prefix_parts):
        nonlocal best_result, best_root_len

        # Check if remaining is a known root
        if remaining in root_lookup and len(remaining) > best_root_len:
            root_def = shorten_def(root_lookup[remaining])
            prefix_str = ' '.join(prefix_parts) if prefix_parts else ''
            best_result = f'{prefix_str} {root_def}'.strip() if prefix_str else root_def
            best_root_len = len(remaining)

        if len(remaining) < 2:
            return

        # Try single-letter prefixes
        for prefix, eng in PREFIXES:
            if remaining.startswith(prefix) and len(remaining) > len(prefix) + 1:
                try_prefixes(remaining[len(prefix):], prefix_parts + [eng])

        # Try multi-character prepositions
        for prep, eng in PREPOSITIONS:
            if remaining.startswith(prep) and len(remaining) > len(prep):
                try_prefixes(remaining[len(prep):], prefix_parts + [eng])

    try_prefixes(word, [])
    return best_result


def main():
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)

    # Build root lookup: word -> definition (only words with Strong's numbers)
    root_lookup = {}
    for w, e in words.items():
        s = e.get('strongs', '')
        if s:
            d = e.get('definition', '')
            if d and len(d) > 3:
                root_lookup[w] = d

    print(f'Root words available: {len(root_lookup)}')

    # Fix compound words without Strong's numbers
    fixed = 0
    improved = 0
    still_bad = 0

    for w, entry in words.items():
        if entry.get('strongs'):
            continue  # already has Strong's, skip

        current_def = entry.get('definition', '')

        # Try decomposition
        new_def = decompose(w, root_lookup)
        if new_def:
            # Only update if it's actually better
            current_short = shorten_def(current_def)
            new_short = shorten_def(new_def) if ':' in new_def else new_def

            # Skip if current is already a good name
            if current_def and 'proper name' not in current_def.lower():
                entry['definition'] = new_def
                if current_def != new_def:
                    improved += 1
                fixed += 1
        else:
            still_bad += 1

    print(f'Fixed/confirmed: {fixed}')
    print(f'Improved: {improved}')
    print(f'Still unfixed: {still_bad}')

    # Save
    with open(WORDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, separators=(',', ':'))
    print('Saved words.json')

    # Preview
    VERSES_CSV = Path(r'C:\flask-structural-api\services\rosetta_stone\data\tanakh_COMPLETE_verses.csv')
    with open(VERSES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['book'] == 'Exodus' and row['chapter'] == '5' and row['verse'] in ['1', '2', '3']:
                heb_words = row['hebrew'].split()
                pairs = []
                for hw in heb_words:
                    e = words.get(hw)
                    if e and e.get('definition'):
                        eng = shorten_def(e['definition'])
                        pairs.append(f'{hw}({eng})')
                    else:
                        pairs.append(f'{hw}(?)')
                print(f'\nExodus 5:{row["verse"]}: {" ".join(pairs)}')

    with open(VERSES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['book'] == 'Genesis' and row['chapter'] == '1' and row['verse'] == '1':
                heb_words = row['hebrew'].split()
                pairs = []
                for hw in heb_words:
                    e = words.get(hw)
                    if e and e.get('definition'):
                        eng = shorten_def(e['definition'])
                        pairs.append(f'{hw}({eng})')
                    else:
                        pairs.append(f'{hw}(?)')
                print(f'\nGenesis 1:1: {" ".join(pairs)}')
                break


if __name__ == '__main__':
    main()
