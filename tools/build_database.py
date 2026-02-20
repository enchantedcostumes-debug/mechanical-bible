#!/usr/bin/env python3
"""
BUILD MECHANICAL BIBLE DATABASE
=================================
Creates ONE SQLite database from all scattered data sources.

Sources:
  - tanakh_COMPLETE_verses.csv (23,341 verses - Hebrew, English, gematria)
  - tanakh_COMPLETE_level2_words.csv (263,117 words per verse)
  - tanakh_COMPLETE_level1_letters.csv (every letter)
  - tanakh_COMPLETE_mathematical.csv (factors, divine patterns)
  - data/mechanical/<book>.json (mechanical translations per verse)
  - data/tsk/<book>.json (cross-references)
  - words.json (58,443 word definitions, pictographics, strongs)
  - data/bible_names.json (2,338 names)
  - data/ahlb_complete.json (Ancient Hebrew Lexicon)
  - data/hebrew_strongs.json (Strong's concordance)

Output: database/mechanical_bible.db

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import csv
import json
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
FLASK_DIR = Path('C:/flask-structural-api')
ROSETTA_DATA = FLASK_DIR / 'services' / 'rosetta_stone' / 'data'
DB_PATH = BASE_DIR / 'database' / 'mechanical_bible.db'
DATA_DIR = BASE_DIR / 'data'

# Increase CSV field size limit
csv.field_size_limit(2**31 - 1)


def create_schema(conn):
    """Create all tables."""
    c = conn.cursor()

    c.executescript('''
        -- Books of the Bible
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            hebrew_name TEXT,
            volume TEXT,
            chapter_count INTEGER,
            folder_name TEXT
        );

        -- Verses (the core - every verse of every chapter)
        CREATE TABLE IF NOT EXISTS verses (
            verse_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            hebrew_text TEXT,
            jps_text TEXT,
            rmt_text TEXT,
            mechanical_text TEXT,
            oracle_text TEXT,
            gematria INTEGER,
            digital_root INTEGER,
            word_count INTEGER,
            letter_count INTEGER,
            factors TEXT,
            divine_patterns TEXT,
            word_gematrias TEXT,
            FOREIGN KEY (book_id) REFERENCES books(book_id),
            UNIQUE(book_id, chapter, verse)
        );

        -- Words in each verse (positional)
        CREATE TABLE IF NOT EXISTS verse_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verse_id INTEGER NOT NULL,
            word_pos INTEGER NOT NULL,
            hebrew TEXT NOT NULL,
            gematria INTEGER,
            breakdown TEXT,
            significance TEXT,
            FOREIGN KEY (verse_id) REFERENCES verses(verse_id)
        );

        -- Master word dictionary (from words.json)
        CREATE TABLE IF NOT EXISTS dictionary (
            word_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hebrew TEXT NOT NULL UNIQUE,
            transliteration TEXT,
            strongs TEXT,
            gematria INTEGER,
            digital_root INTEGER,
            definition TEXT,
            pictographic TEXT,
            mechanical_translation TEXT,
            rmt_translation TEXT,
            part_of_speech TEXT,
            frequency INTEGER,
            first_occurrence TEXT,
            is_name INTEGER DEFAULT 0,
            is_control_word INTEGER DEFAULT 0,
            control_mechanism TEXT,
            scholarly_notes TEXT,
            ahlb_root TEXT,
            ahlb_root_number INTEGER,
            root_action TEXT,
            root_concrete TEXT,
            benner_note TEXT,
            kjv_translations TEXT,
            letters_json TEXT,
            timeline_json TEXT,
            corruption_timeline_json TEXT
        );

        -- Letters per word per verse
        CREATE TABLE IF NOT EXISTS verse_letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verse_id INTEGER NOT NULL,
            word_pos INTEGER NOT NULL,
            letter_pos INTEGER NOT NULL,
            letter TEXT NOT NULL,
            letter_name TEXT,
            gematria INTEGER,
            FOREIGN KEY (verse_id) REFERENCES verses(verse_id)
        );

        -- Biblical names
        CREATE TABLE IF NOT EXISTS names (
            name_id INTEGER PRIMARY KEY AUTOINCREMENT,
            hebrew TEXT,
            english TEXT,
            meaning TEXT,
            gematria INTEGER,
            frequency INTEGER,
            first_book TEXT,
            first_chapter INTEGER,
            first_verse INTEGER,
            strongs TEXT,
            type TEXT
        );

        -- Cross-references (TSK)
        CREATE TABLE IF NOT EXISTS cross_references (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_book TEXT NOT NULL,
            from_chapter INTEGER NOT NULL,
            from_verse INTEGER NOT NULL,
            ref_text TEXT NOT NULL
        );

        -- Indexes for fast lookups
        CREATE INDEX IF NOT EXISTS idx_verses_book_ch ON verses(book_id, chapter);
        CREATE INDEX IF NOT EXISTS idx_verses_book_ch_v ON verses(book_id, chapter, verse);
        CREATE INDEX IF NOT EXISTS idx_verse_words_vid ON verse_words(verse_id);
        CREATE INDEX IF NOT EXISTS idx_verse_letters_vid ON verse_letters(verse_id);
        CREATE INDEX IF NOT EXISTS idx_dict_hebrew ON dictionary(hebrew);
        CREATE INDEX IF NOT EXISTS idx_dict_strongs ON dictionary(strongs);
        CREATE INDEX IF NOT EXISTS idx_names_english ON names(english);
        CREATE INDEX IF NOT EXISTS idx_xref_from ON cross_references(from_book, from_chapter, from_verse);
    ''')

    conn.commit()
    print('[OK] Schema created')


# Book folder mapping
BOOK_FOLDERS = {
    'Genesis': 'genesis', 'Exodus': 'exodus', 'Leviticus': 'leviticus',
    'Numbers': 'numbers', 'Deuteronomy': 'deuteronomy', 'Joshua': 'joshua',
    'Judges': 'judges', 'Ruth': 'ruth',
    '1 Samuel': 'i_samuel', '2 Samuel': 'ii_samuel',
    '1 Kings': 'i_kings', '2 Kings': 'ii_kings',
    '1 Chronicles': 'i_chronicles', '2 Chronicles': 'ii_chronicles',
    'Ezra': 'ezra', 'Nehemiah': 'nehemiah', 'Esther': 'esther',
    'Job': 'job', 'Psalms': 'psalms', 'Proverbs': 'proverbs',
    'Ecclesiastes': 'ecclesiastes', 'Song of Songs': 'song_of_songs',
    'Isaiah': 'isaiah', 'Jeremiah': 'jeremiah', 'Lamentations': 'lamentations',
    'Ezekiel': 'ezekiel', 'Daniel': 'daniel', 'Hosea': 'hosea',
    'Joel': 'joel', 'Amos': 'amos', 'Obadiah': 'obadiah',
    'Jonah': 'jonah', 'Micah': 'micah', 'Nahum': 'nahum',
    'Habakkuk': 'habakkuk', 'Zephaniah': 'zephaniah', 'Haggai': 'haggai',
    'Zechariah': 'zechariah', 'Malachi': 'malachi',
    'Matthew': 'matthew', 'Mark': 'mark', 'Luke': 'luke', 'John': 'john',
    'Acts': 'acts', 'Romans': 'romans',
    '1 Corinthians': '1_corinthians', '2 Corinthians': '2_corinthians',
    'Galatians': 'galatians', 'Ephesians': 'ephesians',
    'Philippians': 'philippians', 'Colossians': 'colossians',
    '1 Thessalonians': '1_thessalonians', '2 Thessalonians': '2_thessalonians',
    '1 Timothy': '1_timothy', '2 Timothy': '2_timothy',
    'Titus': 'titus', 'Philemon': 'philemon', 'Hebrews': 'hebrews',
    'James': 'james', '1 Peter': '1_peter', '2 Peter': '2_peter',
    '1 John': '1_john', '2 John': '2_john', '3 John': '3_john',
    'Jude': 'jude', 'Revelation': 'revelation'
}

# JSON book name mapping (mechanical/*.json uses these)
JSON_BOOK_MAP = {
    'Genesis': 'genesis', 'Exodus': 'exodus', 'Leviticus': 'leviticus',
    'Numbers': 'numbers', 'Deuteronomy': 'deuteronomy', 'Joshua': 'joshua',
    'Judges': 'judges', 'Ruth': 'ruth',
    '1 Samuel': '1_samuel', '2 Samuel': '2_samuel',
    '1 Kings': '1_kings', '2 Kings': '2_kings',
    '1 Chronicles': '1_chronicles', '2 Chronicles': '2_chronicles',
    'Ezra': 'ezra', 'Nehemiah': 'nehemiah', 'Esther': 'esther',
    'Job': 'job', 'Psalms': 'psalms', 'Proverbs': 'proverbs',
    'Ecclesiastes': 'ecclesiastes', 'Song of Songs': 'song_of_songs',
    'Isaiah': 'isaiah', 'Jeremiah': 'jeremiah', 'Lamentations': 'lamentations',
    'Ezekiel': 'ezekiel', 'Daniel': 'daniel', 'Hosea': 'hosea',
    'Joel': 'joel', 'Amos': 'amos', 'Obadiah': 'obadiah',
    'Jonah': 'jonah', 'Micah': 'micah', 'Nahum': 'nahum',
    'Habakkuk': 'habakkuk', 'Zephaniah': 'zephaniah', 'Haggai': 'haggai',
    'Zechariah': 'zechariah', 'Malachi': 'malachi',
    'Matthew': 'matthew', 'Mark': 'mark', 'Luke': 'luke', 'John': 'john',
    'Acts': 'acts', 'Romans': 'romans',
    '1 Corinthians': '1_corinthians', '2 Corinthians': '2_corinthians',
    'Galatians': 'galatians', 'Ephesians': 'ephesians',
    'Philippians': 'philippians', 'Colossians': 'colossians',
    '1 Thessalonians': '1_thessalonians', '2 Thessalonians': '2_thessalonians',
    '1 Timothy': '1_timothy', '2 Timothy': '2_timothy',
    'Titus': 'titus', 'Philemon': 'philemon', 'Hebrews': 'hebrews',
    'James': 'james', '1 Peter': '1_peter', '2 Peter': '2_peter',
    '1 John': '1_john', '2 John': '2_john', '3 John': '3_john',
    'Jude': 'jude', 'Revelation': 'revelation'
}


def import_verses(conn):
    """Import verses from tanakh_COMPLETE_verses.csv."""
    c = conn.cursor()
    book_ids = {}
    verse_count = 0

    # First pass: collect books
    csv_path = ROSETTA_DATA / 'tanakh_COMPLETE_verses.csv'
    if not csv_path.exists():
        print(f'[WARN] {csv_path} not found, skipping')
        return book_ids

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        books_seen = {}
        rows = list(reader)

    # Insert books
    for row in rows:
        book = row['book']
        if book not in books_seen:
            volume = row.get('volume', '')
            hebrew_name = row.get('hebrew_name', '')
            folder = BOOK_FOLDERS.get(book, book.lower().replace(' ', '_'))
            c.execute('''INSERT OR IGNORE INTO books (name, hebrew_name, volume, folder_name)
                        VALUES (?, ?, ?, ?)''', (book, hebrew_name, volume, folder))
            books_seen[book] = True

    conn.commit()

    # Get book IDs
    c.execute('SELECT book_id, name FROM books')
    for row in c.fetchall():
        book_ids[row[1]] = row[0]

    # Insert verses
    for row in rows:
        book = row['book']
        bid = book_ids.get(book)
        if not bid:
            continue

        ch = int(row['chapter'])
        v = int(row['verse'])
        hebrew = row.get('hebrew', '')
        english = row.get('english', '')
        gematria = int(row['gematria']) if row.get('gematria', '').strip() else 0
        wc = int(row['word_count']) if row.get('word_count', '').strip() else 0
        lc = int(row['letter_count']) if row.get('letter_count', '').strip() else 0
        word_gematrias = row.get('word_gematrias', '')
        divine = row.get('divine_patterns', '')

        # Digital root
        dr = gematria
        while dr > 9 and dr != 0:
            dr = sum(int(d) for d in str(dr))

        c.execute('''INSERT OR IGNORE INTO verses
                    (book_id, chapter, verse, hebrew_text, jps_text, gematria, digital_root,
                     word_count, letter_count, word_gematrias, divine_patterns)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (bid, ch, v, hebrew, english, gematria, dr, wc, lc, word_gematrias, divine))
        verse_count += 1

    conn.commit()

    # Update chapter counts
    c.execute('''UPDATE books SET chapter_count = (
                    SELECT MAX(chapter) FROM verses WHERE verses.book_id = books.book_id
                 )''')
    conn.commit()

    print(f'[OK] Imported {verse_count} verses, {len(book_ids)} books')
    return book_ids


def import_verse_words(conn):
    """Import word positions from tanakh_COMPLETE_level2_words.csv."""
    c = conn.cursor()
    csv_path = ROSETTA_DATA / 'tanakh_COMPLETE_level2_words.csv'
    if not csv_path.exists():
        print(f'[WARN] {csv_path} not found, skipping')
        return

    # Build verse_id lookup
    c.execute('SELECT verse_id, b.name, v.chapter, v.verse FROM verses v JOIN books b ON v.book_id = b.book_id')
    verse_lookup = {}
    for row in c.fetchall():
        key = (row[1], row[2], row[3])
        verse_lookup[key] = row[0]

    count = 0
    batch = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book = row['book']
            ch = int(row['chapter'])
            v = int(row['verse'])
            vid = verse_lookup.get((book, ch, v))
            if not vid:
                continue

            wp = int(row['word_pos'])
            hebrew = row.get('word', '')
            gem = int(row['gematria']) if row.get('gematria', '').strip() else 0
            breakdown = row.get('breakdown', '')
            sig = row.get('significance', '')

            batch.append((vid, wp, hebrew, gem, breakdown, sig))
            count += 1

            if len(batch) >= 5000:
                c.executemany('''INSERT INTO verse_words (verse_id, word_pos, hebrew, gematria, breakdown, significance)
                                VALUES (?, ?, ?, ?, ?, ?)''', batch)
                batch = []

    if batch:
        c.executemany('''INSERT INTO verse_words (verse_id, word_pos, hebrew, gematria, breakdown, significance)
                        VALUES (?, ?, ?, ?, ?, ?)''', batch)

    conn.commit()
    print(f'[OK] Imported {count} verse-words')


def import_mechanical(conn, book_ids):
    """Import mechanical translations from data/mechanical/*.json."""
    c = conn.cursor()
    mech_dir = DATA_DIR / 'mechanical'
    if not mech_dir.exists():
        print('[WARN] data/mechanical/ not found, skipping')
        return

    count = 0
    for book_name, json_name in JSON_BOOK_MAP.items():
        json_path = mech_dir / f'{json_name}.json'
        if not json_path.exists():
            continue

        bid = book_ids.get(book_name)
        if not bid:
            continue

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for ch_str, verses in data.items():
            ch = int(ch_str)
            for v_str, vdata in verses.items():
                v = int(v_str)
                mech_text = vdata.get('text', '') if isinstance(vdata, dict) else str(vdata)

                c.execute('''UPDATE verses SET mechanical_text = ?
                            WHERE book_id = ? AND chapter = ? AND verse = ?''',
                         (mech_text, bid, ch, v))
                count += 1

    conn.commit()
    print(f'[OK] Updated {count} mechanical translations')


def import_dictionary(conn):
    """Import word definitions from words.json."""
    c = conn.cursor()
    words_path = BASE_DIR / 'words.json'
    if not words_path.exists():
        print('[WARN] words.json not found, skipping')
        return

    with open(words_path, 'r', encoding='utf-8') as f:
        words = json.load(f)

    count = 0
    for hebrew, w in words.items():
        c.execute('''INSERT OR IGNORE INTO dictionary
                    (hebrew, transliteration, strongs, gematria, digital_root,
                     definition, pictographic, mechanical_translation, rmt_translation,
                     part_of_speech, frequency, first_occurrence, is_name, is_control_word,
                     control_mechanism, scholarly_notes, ahlb_root, ahlb_root_number,
                     root_action, root_concrete, benner_note, kjv_translations,
                     letters_json, timeline_json, corruption_timeline_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (
                     hebrew,
                     w.get('transliteration', ''),
                     w.get('strongs', ''),
                     w.get('gematria', 0),
                     w.get('digital_root', 0),
                     w.get('definition', ''),
                     w.get('pictographic', ''),
                     w.get('mechanical_translation', ''),
                     w.get('rmt_translation', ''),
                     w.get('part_of_speech', ''),
                     w.get('frequency', 0),
                     w.get('first_occurrence', ''),
                     1 if w.get('is_name') else 0,
                     1 if w.get('is_control_word') else 0,
                     w.get('control_mechanism', ''),
                     w.get('scholarly_notes', ''),
                     w.get('ahlb_root', ''),
                     w.get('ahlb_root_number', 0),
                     w.get('root_action', ''),
                     w.get('root_concrete', ''),
                     w.get('benner_note', ''),
                     json.dumps(w.get('kjv_translations', []), ensure_ascii=False),
                     json.dumps(w.get('letters', []), ensure_ascii=False),
                     json.dumps(w.get('timeline', {}), ensure_ascii=False),
                     json.dumps(w.get('corruption_timeline', {}), ensure_ascii=False),
                 ))
        count += 1

    conn.commit()
    print(f'[OK] Imported {count} dictionary words')


def import_names(conn):
    """Import biblical names from data/bible_names.json."""
    c = conn.cursor()
    names_path = DATA_DIR / 'bible_names.json'
    if not names_path.exists():
        print('[WARN] data/bible_names.json not found, skipping')
        return

    with open(names_path, 'r', encoding='utf-8') as f:
        names = json.load(f)

    count = 0
    if isinstance(names, dict):
        items = names.values() if all(isinstance(v, dict) for v in names.values()) else [names]
    elif isinstance(names, list):
        items = names
    else:
        print('[WARN] Unexpected names format')
        return

    for n in items:
        if not isinstance(n, dict):
            continue
        c.execute('''INSERT OR IGNORE INTO names
                    (hebrew, english, meaning, gematria, frequency, first_book, first_chapter, first_verse, strongs, type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (
                     n.get('hebrew', ''),
                     n.get('english', n.get('name', '')),
                     n.get('meaning', n.get('definition', '')),
                     n.get('gematria', 0),
                     n.get('frequency', 0),
                     n.get('first_book', ''),
                     n.get('first_chapter', 0),
                     n.get('first_verse', 0),
                     n.get('strongs', ''),
                     n.get('type', ''),
                 ))
        count += 1

    conn.commit()
    print(f'[OK] Imported {count} names')


def import_tsk(conn):
    """Import cross-references from data/tsk/*.json."""
    c = conn.cursor()
    tsk_dir = DATA_DIR / 'tsk'
    if not tsk_dir.exists():
        print('[WARN] data/tsk/ not found, skipping')
        return

    count = 0
    for json_path in tsk_dir.glob('*.json'):
        if json_path.name.startswith('_'):
            continue

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        book_name = json_path.stem.replace('_', ' ').title()
        # Handle numbered books
        for prefix in ['I ', 'Ii ']:
            if book_name.startswith(prefix):
                num = '1' if prefix == 'I ' else '2'
                book_name = num + ' ' + book_name[len(prefix):]

        if isinstance(data, dict):
            for ch_str, ch_data in data.items():
                if not ch_str.isdigit():
                    continue
                ch = int(ch_str)
                if isinstance(ch_data, dict):
                    for v_str, refs in ch_data.items():
                        if not v_str.isdigit():
                            continue
                        v = int(v_str)
                        ref_text = json.dumps(refs, ensure_ascii=False) if isinstance(refs, (list, dict)) else str(refs)
                        c.execute('''INSERT INTO cross_references (from_book, from_chapter, from_verse, ref_text)
                                    VALUES (?, ?, ?, ?)''', (book_name, ch, v, ref_text))
                        count += 1

    conn.commit()
    print(f'[OK] Imported {count} cross-references')


def import_mathematical(conn, book_ids):
    """Import mathematical data (factors, patterns) from tanakh_COMPLETE_mathematical.csv."""
    c = conn.cursor()
    csv_path = ROSETTA_DATA / 'tanakh_COMPLETE_mathematical.csv'
    if not csv_path.exists():
        print(f'[WARN] {csv_path} not found, skipping')
        return

    count = 0
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            book = row.get('book', '')
            bid = book_ids.get(book)
            if not bid:
                continue

            ch = int(row['chapter'])
            v = int(row['verse'])
            factors = row.get('factors', '')

            c.execute('''UPDATE verses SET factors = ?
                        WHERE book_id = ? AND chapter = ? AND verse = ?''',
                     (factors, bid, ch, v))
            count += 1

    conn.commit()
    print(f'[OK] Updated {count} verse factors')


def print_stats(conn):
    """Print database statistics."""
    c = conn.cursor()

    c.execute('SELECT COUNT(*) FROM books')
    print(f'  Books:            {c.fetchone()[0]}')

    c.execute('SELECT COUNT(*) FROM verses')
    print(f'  Verses:           {c.fetchone()[0]}')

    c.execute('SELECT COUNT(*) FROM verse_words')
    print(f'  Verse-words:      {c.fetchone()[0]}')

    c.execute('SELECT COUNT(*) FROM dictionary')
    print(f'  Dictionary:       {c.fetchone()[0]}')

    c.execute('SELECT COUNT(*) FROM names')
    print(f'  Names:            {c.fetchone()[0]}')

    c.execute('SELECT COUNT(*) FROM cross_references')
    print(f'  Cross-refs:       {c.fetchone()[0]}')

    c.execute("SELECT COUNT(*) FROM verses WHERE mechanical_text IS NOT NULL AND mechanical_text != ''")
    print(f'  With mechanical:  {c.fetchone()[0]}')

    # Database file size
    db_size = DB_PATH.stat().st_size / (1024 * 1024)
    print(f'  Database size:    {db_size:.1f} MB')


def main():
    print('=' * 60)
    print('BUILDING MECHANICAL BIBLE DATABASE')
    print('=' * 60)

    # Create database directory
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Remove old database if exists
    if DB_PATH.exists():
        DB_PATH.unlink()
        print('[OK] Removed old database')

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')

    try:
        create_schema(conn)

        book_ids = import_verses(conn)
        import_verse_words(conn)
        import_mechanical(conn, book_ids)
        import_mathematical(conn, book_ids)
        import_dictionary(conn)
        import_names(conn)
        import_tsk(conn)

        print()
        print('DATABASE STATISTICS:')
        print('-' * 40)
        print_stats(conn)

        print()
        print(f'[OK] Database created: {DB_PATH}')

    finally:
        conn.close()


if __name__ == '__main__':
    main()
