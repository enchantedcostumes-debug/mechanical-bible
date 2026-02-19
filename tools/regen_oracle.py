#!/usr/bin/env python3
"""
REGENERATE ORACLE DATA — Mechanical Bible
==========================================
Re-looks up every Hebrew word in the existing oracle JSON files
using the updated words.json definitions.

Preserves gematria and digital root values.
Only changes the definition text in parentheses.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'
ORACLE_DIR = BASE_DIR / 'data' / 'oracle'


def shorten_def(definition):
    """Extract short label from a definition."""
    if not definition or definition == '?':
        return '?'
    if ':' in definition:
        short = definition.split(':')[0].strip()
        short = re.sub(r'^\[(.+)\]$', r'\1', short)
        if short:
            return short
    d = re.sub(r'\s*\(.*?\)', '', definition)
    parts = re.split(r'[;,.]', d)
    return parts[0].strip() or '?'


def main():
    print('Loading words.json...')
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'  {len(words)} entries')

    oracle_files = sorted(f for f in os.listdir(ORACLE_DIR) if f.endswith('.json'))
    print(f'\nRegenerating {len(oracle_files)} oracle files...')

    total_verses = 0
    total_words = 0
    matched = 0
    unmatched = 0

    for fname in oracle_files:
        fpath = ORACLE_DIR / fname
        with open(fpath, 'r', encoding='utf-8') as f:
            book = json.load(f)

        for ch_num, chapter in book.items():
            for vs_num, verse in chapter.items():
                old_text = verse.get('text', '')
                # Parse: "בראשית(In the summit) ברא(Shape) ..."
                # Extract Hebrew words
                pairs = re.findall(r'([^\s(]+)\(([^)]*)\)', old_text)

                new_pairs = []
                for heb, old_eng in pairs:
                    total_words += 1
                    entry = words.get(heb)
                    if entry and entry.get('definition'):
                        eng = shorten_def(entry['definition'])
                        new_pairs.append(f'{heb}({eng})')
                        matched += 1
                    else:
                        # Keep old definition
                        new_pairs.append(f'{heb}({old_eng})')
                        unmatched += 1

                verse['text'] = ' '.join(new_pairs)
                total_verses += 1

        # Write back
        with open(fpath, 'w', encoding='utf-8') as f:
            json.dump(book, f, ensure_ascii=False, separators=(',', ':'))

        vc = sum(len(vs) for vs in book.values())
        print(f'  {fname}: {len(book)} chapters, {vc} verses')

    pct = (matched / total_words * 100) if total_words else 0
    print(f'\n[DONE] Regenerated {total_verses} verses across {len(oracle_files)} books')
    print(f'  Words: {matched}/{total_words} matched ({pct:.1f}%)')
    print(f'  Kept old: {unmatched}')


if __name__ == '__main__':
    print('=' * 60)
    print('REGENERATE ORACLE DATA - Mechanical Bible')
    print('=' * 60)
    main()
