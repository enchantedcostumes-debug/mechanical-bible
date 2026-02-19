#!/usr/bin/env python3
"""
Generate Mechanical Translations - Mechanical Bible
=====================================================
Generates Benner-method mechanical translations for every verse in the Tanakh.

Uses:
  1. OSHB morphology codes for grammatical form
  2. benner_vocab table for Benner's specific word choices
  3. AHLB definitions as fallback
  4. mechanical_engine.py for rendering morph codes to Benner format

Output: Updates the mechanical spans in the HTML files.
        Also generates data/mechanical/<book>.json for API/dynamic use.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent))
from mechanical_engine import render_word

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'database' / 'mechanical-bible.db'
OUTPUT_DIR = BASE_DIR / 'data' / 'mechanical'


def digital_root(n):
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def shorten_def(definition):
    """Extract short label from definition for fallback."""
    if not definition:
        return '?'
    if ':' in definition:
        short = definition.split(':')[0].strip()
        if short:
            return re.sub(r'^\[(.+)\]$', r'\1', short)
    d = re.sub(r'\s*\(.*?\)', '', definition)
    parts = re.split(r'[;,.]', d)
    return parts[0].strip() or '?'


def strip_points(text):
    """Strip vowels and cantillation from Hebrew text."""
    text = text.replace('/', '')
    return ''.join(ch for ch in text
                   if unicodedata.category(ch) not in ('Mn', 'Cf'))


def match_oshb_to_verse_words(verse_words, oshb_words):
    """Match OSHB words to our unpointed verse words.
    Returns list of (verse_word, [oshb_rows]) pairs."""
    result = []
    oi = 0

    for vw in verse_words:
        matched_oshb = []
        consumed = ''

        while oi < len(oshb_words):
            oshb_stripped = strip_points(oshb_words[oi]['hebrew'])
            consumed += oshb_stripped
            matched_oshb.append(oshb_words[oi])
            oi += 1

            if consumed == vw:
                break
            elif len(consumed) >= len(vw):
                break

        result.append((vw, matched_oshb))

    return result


def main():
    if not DB_PATH.exists():
        print(f'ERROR: Database not found at {DB_PATH}')
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Load Benner vocabulary (priority lookup)
    print('Loading Benner vocabulary...')
    c.execute('SELECT strongs, mechanical FROM benner_vocab')
    benner_vocab = {r['strongs']: r['mechanical'] for r in c.fetchall()}
    print(f'  {len(benner_vocab)} Benner vocab entries')

    # Load AHLB definitions as fallback
    print('Loading AHLB fallback definitions...')
    c.execute('SELECT strongs, definition FROM ahlb')
    ahlb_lookup = {r['strongs']: r['definition'] for r in c.fetchall()}
    print(f'  {len(ahlb_lookup)} AHLB entries')

    # Load words table as second fallback
    c.execute("SELECT strongs, definition FROM words WHERE strongs IS NOT NULL AND strongs != ''")
    words_lookup = {}
    for r in c.fetchall():
        s = r['strongs'].split('_')[0].split(',')[0].strip()
        if s and s not in words_lookup:
            words_lookup[s] = r['definition']
    print(f'  {len(words_lookup)} words entries')

    def get_root(strongs):
        """Get the mechanical root word for a Strong's number.
        Priority: benner_vocab > AHLB short > words short"""
        if strongs in benner_vocab:
            return benner_vocab[strongs]
        defn = ahlb_lookup.get(strongs, '') or words_lookup.get(strongs, '')
        if defn:
            short = shorten_def(defn)
            if short and short != '?':
                return short.upper().replace(' ', '.')
        return '?'

    # Get all verses from verses table (has gematria)
    print('Loading verse metadata...')
    c.execute('SELECT book, chapter, verse, hebrew_text, gematria FROM verses')
    verse_meta = {}
    for r in c.fetchall():
        key = (r['book'], r['chapter'], r['verse'])
        verse_meta[key] = {
            'hebrew_text': r['hebrew_text'],
            'gematria': r['gematria'] or 0,
        }
    print(f'  {len(verse_meta)} verses')

    # Get all OSHB books
    c.execute('SELECT DISTINCT book FROM oshb_words ORDER BY book')
    oshb_books = [r['book'] for r in c.fetchall()]

    # Process each book
    books_data = defaultdict(lambda: defaultdict(dict))
    total_verses = 0
    total_words = 0
    matched_benner = 0
    matched_ahlb = 0
    unmatched = 0

    for book in oshb_books:
        # Get all OSHB words for this book
        c.execute('''
            SELECT chapter, verse, position, hebrew, lemma, morph, strongs_parts
            FROM oshb_words
            WHERE book = ?
            ORDER BY chapter, verse, position
        ''', (book,))

        verse_oshb = defaultdict(list)
        for r in c.fetchall():
            key = (r['chapter'], r['verse'])
            verse_oshb[key].append({
                'position': r['position'],
                'hebrew': r['hebrew'],
                'lemma': r['lemma'] or '',
                'morph': r['morph'] or '',
                'strongs': r['strongs_parts'] or '',
            })

        for (chapter, verse), oshb_words in sorted(verse_oshb.items()):
            meta_key = (book, chapter, verse)
            meta = verse_meta.get(meta_key)

            if meta:
                hebrew_text = meta['hebrew_text']
                gematria = meta['gematria']
            else:
                hebrew_text = ' '.join(strip_points(w['hebrew']) for w in oshb_words)
                gematria = 0

            dr = digital_root(gematria) if gematria else 0
            verse_words = hebrew_text.split()

            # Match OSHB to verse words
            matches = match_oshb_to_verse_words(verse_words, oshb_words)

            # Build mechanical translation
            mech_parts = []
            for vw, oshb_rows in matches:
                if not oshb_rows:
                    mech_parts.append('?')
                    unmatched += 1
                elif len(oshb_rows) == 1:
                    orow = oshb_rows[0]
                    strongs = orow['strongs']
                    root = get_root(strongs) if strongs else '?'
                    if root == '?':
                        # Try words table direct lookup for the Hebrew word
                        unpointed = strip_points(orow['hebrew'])
                        c.execute('SELECT definition FROM words WHERE hebrew = ?', (unpointed,))
                        wrow = c.fetchone()
                        if wrow and wrow['definition']:
                            root = shorten_def(wrow['definition']).upper().replace(' ', '.')

                    mech = render_word(orow['morph'], root, orow['lemma'], strongs)
                    mech_parts.append(mech)

                    if strongs and strongs in benner_vocab:
                        matched_benner += 1
                    elif strongs:
                        matched_ahlb += 1
                    else:
                        unmatched += 1
                else:
                    # Multiple OSHB words for one verse word
                    parts = []
                    for orow in oshb_rows:
                        strongs = orow['strongs']
                        root = get_root(strongs) if strongs else '?'
                        mech = render_word(orow['morph'], root, orow['lemma'], strongs)
                        parts.append(mech)
                    mech_parts.append(' '.join(parts))
                    matched_ahlb += 1

                total_words += 1

            mech_text = ' '.join(mech_parts)

            books_data[book][str(chapter)][str(verse)] = {
                'text': mech_text,
                'g': gematria,
                'dr': dr,
            }
            total_verses += 1

    # Write per-book JSON files
    print(f'\nWriting JSON files...')
    for folder, chapters in sorted(books_data.items()):
        outpath = OUTPUT_DIR / f'{folder}.json'
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(chapters, f, ensure_ascii=False, separators=(',', ':'))
        verse_count = sum(len(vs) for vs in chapters.values())
        print(f'  {folder}: {len(chapters)} chapters, {verse_count} verses')

    pct_b = (matched_benner / total_words * 100) if total_words else 0
    pct_a = (matched_ahlb / total_words * 100) if total_words else 0
    pct_u = (unmatched / total_words * 100) if total_words else 0

    print(f'\n[DONE] Generated {total_verses} verses across {len(books_data)} books')
    print(f'  Total words: {total_words}')
    print(f'  Benner vocab: {matched_benner} ({pct_b:.1f}%)')
    print(f'  AHLB fallback: {matched_ahlb} ({pct_a:.1f}%)')
    print(f'  Unmatched: {unmatched} ({pct_u:.1f}%)')

    conn.close()


if __name__ == '__main__':
    print('=' * 60)
    print('GENERATE MECHANICAL TRANSLATIONS - Mechanical Bible')
    print('  Benner-method verse-by-verse generation')
    print('  OSHB morphology + Benner vocabulary + AHLB fallback')
    print('=' * 60)
    main()
