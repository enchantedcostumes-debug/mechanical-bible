#!/usr/bin/env python3
"""
Generate Greek Mechanical Translations - Mechanical Bible
==========================================================
Generates Benner-style mechanical translations for every verse
in the Greek New Testament using TAGNT morphology data + TBESG lexicon.

Reads from SQLite: greek_words (morphology), greek_vocab (definitions)
Outputs to: data/mechanical/<book>.json

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import sqlite3
import re
from collections import defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
from greek_engine import render_greek_word

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'database' / 'mechanical-bible.db'
MECH_DIR = BASE_DIR / 'data' / 'mechanical'


def clean_gloss(gloss):
    """Clean up TBESG/TAGNT gloss for mechanical rendering.

    Strips brackets, articles, and normalizes for ALL CAPS format.
    """
    if not gloss:
        return ''

    # Remove brackets from TAGNT: "[The] book" -> "book", "<the>" -> ""
    gloss = re.sub(r'\[.*?\]', '', gloss)
    gloss = re.sub(r'<.*?>', '', gloss)

    # Strip leading/trailing whitespace and punctuation
    gloss = gloss.strip(' .,;:!?')

    # Remove "of " prefix from genitives (grammar engine adds ~of)
    if gloss.startswith('of '):
        gloss = gloss[3:]

    # Remove common prefixes that the engine handles
    for prefix in ('the ', 'a ', 'an ', 'to '):
        if gloss.startswith(prefix):
            gloss = gloss[len(prefix):]

    return gloss.strip()


def main():
    print('=' * 60)
    print('GENERATE GREEK MECHANICAL TRANSLATIONS')
    print('  TAGNT morphology + TBESG lexicon')
    print('=' * 60)

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    # Load greek_vocab
    c.execute('SELECT strongs, mechanical, gloss FROM greek_vocab')
    vocab = {}
    for row in c.fetchall():
        vocab[row['strongs']] = {
            'mechanical': row['mechanical'],
            'gloss': row['gloss'],
        }
    print(f'Loaded {len(vocab):,} vocab entries')

    # Get all books in canonical order
    c.execute('''
        SELECT book, MIN(id) as first_id FROM greek_words
        GROUP BY book ORDER BY first_id
    ''')
    books = [row['book'] for row in c.fetchall()]
    print(f'Processing {len(books)} books...')

    total_verses = 0
    total_words = 0
    matched_vocab = 0
    matched_tagnt = 0
    unmatched = 0

    MECH_DIR.mkdir(parents=True, exist_ok=True)

    for book in books:
        # Get all words for this book, ordered by chapter, verse, word_pos
        c.execute('''
            SELECT chapter, verse, word_pos, greek, lemma, strongs, morph, gloss
            FROM greek_words
            WHERE book = ?
            ORDER BY chapter, verse, word_pos
        ''', (book,))

        # Group by chapter and verse
        book_data = defaultdict(lambda: defaultdict(list))
        for row in c.fetchall():
            ch = str(row['chapter'])
            vs = str(row['verse'])
            book_data[ch][vs].append(dict(row))

        # Generate mechanical text per verse
        output = {}
        book_verses = 0

        for ch in sorted(book_data.keys(), key=int):
            output[ch] = {}
            for vs in sorted(book_data[ch].keys(), key=int):
                words = book_data[ch][vs]
                mech_parts = []

                for w in words:
                    strongs = w['strongs'] or ''
                    morph = w['morph'] or ''

                    # Get root name: prefer vocab mechanical, then TAGNT gloss
                    root = ''
                    source = ''

                    if strongs and strongs in vocab:
                        root = vocab[strongs]['mechanical']
                        source = 'vocab'
                    elif w['gloss']:
                        cleaned = clean_gloss(w['gloss'])
                        if cleaned:
                            root = cleaned.upper().replace(' ', '.')
                            source = 'tagnt'

                    if not root:
                        # Last resort: use lemma transliterated
                        root = '?'
                        source = 'none'

                    mech = render_greek_word(morph, root, w['lemma'], strongs)
                    mech_parts.append(mech)

                    total_words += 1
                    if source == 'vocab':
                        matched_vocab += 1
                    elif source == 'tagnt':
                        matched_tagnt += 1
                    else:
                        unmatched += 1

                mech_text = ' '.join(mech_parts)
                output[ch][vs] = {'text': mech_text}
                book_verses += 1

        # Write JSON
        json_path = MECH_DIR / f'{book}.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=None)

        chapters = len(output)
        total_verses += book_verses
        print(f'  {book}: {chapters} chapters, {book_verses} verses')

    print(f'\n[DONE] Generated {total_verses:,} verses across {len(books)} books')
    print(f'  Total words: {total_words:,}')
    print(f'  TBESG vocab: {matched_vocab:,} ({matched_vocab/total_words*100:.1f}%)')
    print(f'  TAGNT gloss: {matched_tagnt:,} ({matched_tagnt/total_words*100:.1f}%)')
    print(f'  Unmatched: {unmatched:,} ({unmatched/total_words*100:.1f}%)')

    conn.close()


if __name__ == '__main__':
    main()
