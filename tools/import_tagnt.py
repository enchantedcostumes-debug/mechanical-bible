#!/usr/bin/env python3
"""
Import TAGNT + TBESG into SQLite - Mechanical Bible
=====================================================
Imports Greek NT word-by-word morphology data from STEPBible's TAGNT
and Greek lexicon definitions from TBESG into the mechanical-bible database.

Sources:
  - TAGNT (Translators Amalgamated Greek NT) — CC BY 4.0
  - TBESG (Translators Brief lexicon of Extended Strongs for Greek) — CC BY 4.0
  Both from https://github.com/STEPBible/STEPBible-Data

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'database' / 'mechanical-bible.db'
SOURCES_DIR = BASE_DIR / 'data' / 'sources'

# TAGNT book abbreviations → folder names
BOOK_MAP = {
    'Mat': 'matthew', 'Mrk': 'mark', 'Luk': 'luke', 'Jhn': 'john',
    'Act': 'acts', 'Rom': 'romans', '1Co': '1_corinthians', '2Co': '2_corinthians',
    'Gal': 'galatians', 'Eph': 'ephesians', 'Php': 'philippians', 'Col': 'colossians',
    '1Th': '1_thessalonians', '2Th': '2_thessalonians', '1Ti': '1_timothy', '2Ti': '2_timothy',
    'Tit': 'titus', 'Phm': 'philemon', 'Heb': 'hebrews', 'Jas': 'james',
    '1Pe': '1_peter', '2Pe': '2_peter', '1Jn': '1_john', '2Jn': '2_john',
    '3Jn': '3_john', 'Jud': 'jude', 'Rev': 'revelation',
}


def create_tables(conn):
    """Create greek_words and greek_vocab tables."""
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS greek_words')
    c.execute('DROP TABLE IF EXISTS greek_vocab')

    c.execute('''
        CREATE TABLE greek_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            word_pos INTEGER NOT NULL,
            greek TEXT,
            lemma TEXT,
            strongs TEXT,
            morph TEXT,
            gloss TEXT,
            editions TEXT
        )
    ''')
    c.execute('CREATE INDEX idx_gw_book_ch_vs ON greek_words(book, chapter, verse)')
    c.execute('CREATE INDEX idx_gw_strongs ON greek_words(strongs)')

    c.execute('''
        CREATE TABLE greek_vocab (
            strongs TEXT PRIMARY KEY,
            mechanical TEXT,
            gloss TEXT,
            pos TEXT
        )
    ''')
    conn.commit()


def parse_tagnt_ref(ref_field):
    """Parse TAGNT reference field like 'Mat.1.1#01=NKO'

    Returns: (book_abbr, chapter, verse, word_pos, word_type) or None
    """
    # Pattern: Book.Chapter.Verse#WordPos=Type
    # Can also have brackets for versification differences
    m = re.match(r'([A-Za-z0-9]+)\.(\d+)\.(\d+)(?:\[.*?\])?#(\d+)=(.+)', ref_field)
    if not m:
        return None
    return m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)), m.group(5)


def parse_strongs_morph(sm_field):
    """Parse the combined Strong's=Morph field like 'G0976=N-NSF' or 'G2424G=N-GSM-P'

    Returns: (strongs, morph)
    """
    if '=' not in sm_field:
        return '', sm_field
    parts = sm_field.split('=', 1)
    strongs_raw = parts[0].strip()
    morph = parts[1].strip()

    # Normalize Strong's: G0976 -> G976, G2424G -> G2424
    # Strip trailing letter disambiguation (G2424G -> G2424)
    m = re.match(r'(G\d+)', strongs_raw)
    strongs = m.group(1) if m else strongs_raw
    # Remove leading zeros: G0976 -> G976
    strongs = re.sub(r'G0+(\d)', r'G\1', strongs)

    return strongs, morph


def parse_greek_word(greek_field):
    """Parse Greek field like 'Βίβλος (Biblos)' -> 'Βίβλος'"""
    # Strip transliteration in parens and any trailing punctuation
    greek = re.sub(r'\s*\(.*?\)\s*', '', greek_field).strip()
    # Strip trailing periods, commas, semicolons, colons
    greek = greek.rstrip('.,;:·')
    return greek


def parse_lemma_gloss(lemma_field):
    """Parse lemma field like 'βίβλος=book' -> ('βίβλος', 'book')"""
    if '=' not in lemma_field:
        return lemma_field.strip(), ''
    parts = lemma_field.split('=', 1)
    lemma = parts[0].strip()
    # Clean up lemma: remove variant forms like 'Δαυείδ, Δαυίδ, Δαβίδ'
    if ',' in lemma:
        lemma = lemma.split(',')[0].strip()
    gloss = parts[1].strip()
    return lemma, gloss


def import_tagnt(conn, filepath):
    """Import one TAGNT file into greek_words table."""
    c = conn.cursor()
    count = 0
    skipped = 0

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('='):
                continue

            fields = line.split('\t')
            if len(fields) < 5:
                continue

            # Parse reference
            ref = parse_tagnt_ref(fields[0])
            if not ref:
                continue

            book_abbr, chapter, verse, word_pos, word_type = ref

            # Only import words found in major editions (N=Nestle-Aland, K=KJV tradition)
            # Skip 'O' only words (rare variants)
            if 'N' not in word_type and 'K' not in word_type:
                skipped += 1
                continue

            book = BOOK_MAP.get(book_abbr)
            if not book:
                continue

            # Parse fields
            greek = parse_greek_word(fields[1]) if len(fields) > 1 else ''
            english_gloss = fields[2].strip() if len(fields) > 2 else ''
            strongs, morph = parse_strongs_morph(fields[3]) if len(fields) > 3 else ('', '')
            lemma, lemma_gloss = parse_lemma_gloss(fields[4]) if len(fields) > 4 else ('', '')
            editions = fields[5].strip() if len(fields) > 5 else ''

            # Use English gloss from TAGNT col 2 as primary gloss
            gloss = english_gloss

            c.execute('''
                INSERT INTO greek_words (book, chapter, verse, word_pos, greek, lemma, strongs, morph, gloss, editions)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (book, chapter, verse, word_pos, greek, lemma, strongs, morph, gloss, editions))
            count += 1

    conn.commit()
    return count, skipped


def import_tbesg(conn, filepath):
    """Import TBESG lexicon into greek_vocab table."""
    c = conn.cursor()
    count = 0
    seen = set()

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            fields = line.split('\t')
            if len(fields) < 7:
                continue

            # First field should be G followed by digits
            strongs_raw = fields[0].strip()
            if not re.match(r'G\d+', strongs_raw):
                continue

            # Normalize Strong's
            strongs = re.sub(r'G0+(\d)', r'G\1', strongs_raw)

            # Skip if already seen (first entry wins for duplicates)
            if strongs in seen:
                continue
            seen.add(strongs)

            # Col 6 = brief gloss (what we use for mechanical rendering)
            gloss = fields[6].strip() if len(fields) > 6 else ''
            if not gloss:
                continue

            # Col 5 = morph type like G:N-F, G:V, etc.
            pos_field = fields[5].strip() if len(fields) > 5 else ''

            # Convert gloss to mechanical format: ALL CAPS, spaces → dots
            mechanical = gloss.upper().replace(' ', '.')

            c.execute('''
                INSERT OR IGNORE INTO greek_vocab (strongs, mechanical, gloss, pos)
                VALUES (?, ?, ?, ?)
            ''', (strongs, mechanical, gloss, pos_field))
            count += 1

    conn.commit()
    return count


def main():
    print('=' * 60)
    print('IMPORT GREEK NT DATA INTO DATABASE')
    print('  TAGNT morphology + TBESG lexicon')
    print('=' * 60)

    conn = sqlite3.connect(str(DB_PATH))

    # Create tables
    print('Creating tables...')
    create_tables(conn)

    # Import TAGNT
    tagnt_files = [
        SOURCES_DIR / 'TAGNT_Mat-Jhn.txt',
        SOURCES_DIR / 'TAGNT_Act-Rev.txt',
    ]
    total_words = 0
    total_skipped = 0
    for tf in tagnt_files:
        print(f'Importing {tf.name}...')
        count, skipped = import_tagnt(conn, tf)
        total_words += count
        total_skipped += skipped
        print(f'  {count:,} words imported, {skipped} variant-only words skipped')

    # Import TBESG lexicon
    tbesg_path = SOURCES_DIR / 'TBESG.txt'
    print(f'Importing {tbesg_path.name}...')
    vocab_count = import_tbesg(conn, tbesg_path)
    print(f'  {vocab_count:,} vocabulary entries imported')

    # Stats
    c = conn.cursor()
    c.execute('SELECT COUNT(DISTINCT book) FROM greek_words')
    books = c.fetchone()[0]
    c.execute('SELECT COUNT(DISTINCT book || chapter || verse) FROM greek_words')
    verses = c.fetchone()[0]
    c.execute('SELECT COUNT(DISTINCT strongs) FROM greek_words WHERE strongs != ""')
    unique_strongs = c.fetchone()[0]

    print(f'\n[DONE]')
    print(f'  greek_words: {total_words:,} words across {books} books, {verses:,} verses')
    print(f'  greek_vocab: {vocab_count:,} definitions')
    print(f'  Unique Strong\'s in text: {unique_strongs:,}')

    # Show book breakdown
    c.execute('''
        SELECT book, COUNT(*) as words, COUNT(DISTINCT chapter||'.'||verse) as verses
        FROM greek_words GROUP BY book ORDER BY MIN(id)
    ''')
    for row in c.fetchall():
        print(f'    {row[0]}: {row[1]:,} words, {row[2]} verses')

    conn.close()


if __name__ == '__main__':
    main()
