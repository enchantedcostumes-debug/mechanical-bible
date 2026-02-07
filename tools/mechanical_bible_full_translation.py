#!/usr/bin/env python3
"""
MECHANICAL BIBLE - FULL TRANSLATION
====================================
Translates the ENTIRE Tanakh mechanically using pictographic Hebrew analysis.

For EVERY Hebrew word:
1. Break into letters
2. Get pictographic meaning of each letter
3. Build the mechanical meaning
4. Track gematria

Output: Complete mechanical translation of every verse.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "services" / "rosetta_stone" / "data"
OUTPUT_DIR = BASE_DIR / "data" / "mechanical_bible"

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Hebrew letter pictographic meanings
HEBREW_LETTERS = {
    'א': {'name': 'ALEPH', 'pic': 'ox head', 'meaning': 'strength/leader/first'},
    'ב': {'name': 'BET', 'pic': 'house', 'meaning': 'house/within/by means of'},
    'ג': {'name': 'GIMEL', 'pic': 'camel', 'meaning': 'lift up/pride/benefit'},
    'ד': {'name': 'DALET', 'pic': 'door', 'meaning': 'door/pathway/movement'},
    'ה': {'name': 'HEY', 'pic': 'man with arms raised', 'meaning': 'behold/reveal/the'},
    'ו': {'name': 'VAV', 'pic': 'tent peg', 'meaning': 'hook/and/secure/add'},
    'ז': {'name': 'ZAYIN', 'pic': 'weapon', 'meaning': 'cut/nourish/weapon'},
    'ח': {'name': 'CHET', 'pic': 'fence', 'meaning': 'fence/protect/outside'},
    'ט': {'name': 'TET', 'pic': 'basket', 'meaning': 'surround/contain/good'},
    'י': {'name': 'YOD', 'pic': 'hand', 'meaning': 'hand/work/deed/make'},
    'כ': {'name': 'KAF', 'pic': 'palm', 'meaning': 'palm/open/allow/like'},
    'ך': {'name': 'KAF SOFIT', 'pic': 'palm', 'meaning': 'palm/open/allow/like'},
    'ל': {'name': 'LAMED', 'pic': 'staff', 'meaning': 'staff/teach/toward/authority'},
    'מ': {'name': 'MEM', 'pic': 'water', 'meaning': 'water/chaos/from/mighty'},
    'ם': {'name': 'MEM SOFIT', 'pic': 'water', 'meaning': 'water/chaos/from/mighty'},
    'נ': {'name': 'NUN', 'pic': 'seed', 'meaning': 'seed/continue/heir/life'},
    'ן': {'name': 'NUN SOFIT', 'pic': 'seed', 'meaning': 'seed/continue/heir/life'},
    'ס': {'name': 'SAMECH', 'pic': 'prop', 'meaning': 'support/turn/protect'},
    'ע': {'name': 'AYIN', 'pic': 'eye', 'meaning': 'eye/see/know/experience'},
    'פ': {'name': 'PEY', 'pic': 'mouth', 'meaning': 'mouth/speak/word/open'},
    'ף': {'name': 'PEY SOFIT', 'pic': 'mouth', 'meaning': 'mouth/speak/word/open'},
    'צ': {'name': 'TSADE', 'pic': 'man on side', 'meaning': 'righteous/desire/hunt'},
    'ץ': {'name': 'TSADE SOFIT', 'pic': 'man on side', 'meaning': 'righteous/desire/hunt'},
    'ק': {'name': 'QOF', 'pic': 'sun on horizon', 'meaning': 'behind/cycle/time/condense'},
    'ר': {'name': 'RESH', 'pic': 'head', 'meaning': 'head/first/beginning/top'},
    'ש': {'name': 'SHIN', 'pic': 'teeth', 'meaning': 'consume/destroy/sharp/change'},
    'ת': {'name': 'TAV', 'pic': 'cross/mark', 'meaning': 'mark/sign/covenant/complete'},
}

# Gematria values
GEMATRIA = {
    'א': 1, 'ב': 2, 'ג': 3, 'ד': 4, 'ה': 5, 'ו': 6, 'ז': 7, 'ח': 8, 'ט': 9,
    'י': 10, 'כ': 20, 'ך': 20, 'ל': 30, 'מ': 40, 'ם': 40, 'נ': 50, 'ן': 50,
    'ס': 60, 'ע': 70, 'פ': 80, 'ף': 80, 'צ': 90, 'ץ': 90, 'ק': 100,
    'ר': 200, 'ש': 300, 'ת': 400
}


@dataclass
class MechanicalWord:
    """A single Hebrew word with mechanical translation"""
    hebrew: str
    letters: List[Dict]
    mechanical_meaning: str
    gematria: int
    digital_root: int


@dataclass
class MechanicalVerse:
    """A complete verse with mechanical translation"""
    book: str
    chapter: int
    verse: int
    hebrew_text: str
    english_text: str
    words: List[MechanicalWord]
    mechanical_translation: str
    verse_gematria: int


def get_digital_root(n: int) -> int:
    """Calculate digital root of a number"""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def translate_word_mechanically(hebrew_word: str) -> MechanicalWord:
    """Translate a single Hebrew word mechanically"""
    letters = []
    meanings = []
    gematria = 0

    for char in hebrew_word:
        if char in HEBREW_LETTERS:
            letter_data = HEBREW_LETTERS[char]
            letters.append({
                'letter': char,
                'name': letter_data['name'],
                'pictograph': letter_data['pic'],
                'meaning': letter_data['meaning']
            })
            meanings.append(f"[{letter_data['meaning']}]")
            gematria += GEMATRIA.get(char, 0)

    mechanical_meaning = " ".join(meanings) if meanings else hebrew_word
    digital_root = get_digital_root(gematria) if gematria > 0 else 0

    return MechanicalWord(
        hebrew=hebrew_word,
        letters=letters,
        mechanical_meaning=mechanical_meaning,
        gematria=gematria,
        digital_root=digital_root
    )


def translate_verse_mechanically(book: str, chapter: int, verse: int,
                                  hebrew_text: str, english_text: str) -> MechanicalVerse:
    """Translate a complete verse mechanically"""
    # Split Hebrew text into words
    hebrew_words = hebrew_text.split()

    # Translate each word
    words = []
    mechanical_parts = []
    verse_gematria = 0

    for hw in hebrew_words:
        # Clean the word (remove punctuation)
        clean_word = ''.join(c for c in hw if c in HEBREW_LETTERS or c in GEMATRIA)
        if clean_word:
            mw = translate_word_mechanically(clean_word)
            words.append(mw)
            mechanical_parts.append(mw.mechanical_meaning)
            verse_gematria += mw.gematria

    mechanical_translation = " | ".join(mechanical_parts)

    return MechanicalVerse(
        book=book,
        chapter=chapter,
        verse=verse,
        hebrew_text=hebrew_text,
        english_text=english_text,
        words=words,
        mechanical_translation=mechanical_translation,
        verse_gematria=verse_gematria
    )


def process_tanakh():
    """Process the entire Tanakh"""
    print("[INFO] Loading Tanakh verses...")

    verses_file = DATA_DIR / "tanakh_COMPLETE_verses.csv"
    if not verses_file.exists():
        print(f"[FAIL] Tanakh file not found: {verses_file}")
        return

    results = []
    book_results = {}

    with open(verses_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        total = 0

        for row in reader:
            total += 1
            if total % 1000 == 0:
                print(f"  [INFO] Processed {total} verses...")

            book = row.get('book', '')
            chapter = int(row.get('chapter', 0))
            verse_num = int(row.get('verse', 0))
            hebrew = row.get('hebrew', '')
            english = row.get('english', '')

            if hebrew:
                mv = translate_verse_mechanically(book, chapter, verse_num, hebrew, english)
                results.append(mv)

                # Organize by book
                if book not in book_results:
                    book_results[book] = []
                book_results[book].append(mv)

    print(f"[OK] Processed {total} verses total")
    return results, book_results


def save_results(results: List[MechanicalVerse], book_results: Dict):
    """Save all results"""

    # Save complete JSON
    print("[INFO] Saving complete mechanical Bible...")
    complete_path = OUTPUT_DIR / "mechanical_bible_complete.json"

    # Convert to dict for JSON
    complete_data = {
        'metadata': {
            'title': 'Mechanical Bible - Complete Tanakh',
            'description': 'Every Hebrew word translated through pictographic letter analysis',
            'generated': datetime.now().isoformat(),
            'total_verses': len(results),
            'method': 'Proto-Sinaitic pictographic dissection'
        },
        'verses': [asdict(v) for v in results]
    }

    with open(complete_path, 'w', encoding='utf-8') as f:
        json.dump(complete_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved: {complete_path}")

    # Save by book
    print("[INFO] Saving individual books...")
    books_dir = OUTPUT_DIR / "books"
    books_dir.mkdir(exist_ok=True)

    for book, verses in book_results.items():
        book_file = books_dir / f"{book.lower().replace(' ', '_')}.json"
        book_data = {
            'book': book,
            'verses': [asdict(v) for v in verses],
            'total_verses': len(verses)
        }
        with open(book_file, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)

    print(f"[OK] Saved {len(book_results)} book files")

    # Save readable text version
    print("[INFO] Saving readable text version...")
    text_path = OUTPUT_DIR / "mechanical_bible_readable.txt"

    with open(text_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("THE MECHANICAL BIBLE\n")
        f.write("Complete Pictographic Translation of the Tanakh\n")
        f.write("=" * 80 + "\n\n")

        current_book = ""
        for v in results:
            if v.book != current_book:
                current_book = v.book
                f.write("\n" + "=" * 60 + "\n")
                f.write(f"BOOK: {current_book}\n")
                f.write("=" * 60 + "\n\n")

            f.write(f"{v.book} {v.chapter}:{v.verse}\n")
            f.write(f"HEBREW: {v.hebrew_text}\n")
            f.write(f"ENGLISH: {v.english_text}\n")
            f.write(f"MECHANICAL: {v.mechanical_translation}\n")
            f.write(f"GEMATRIA: {v.verse_gematria}\n")
            f.write("-" * 40 + "\n\n")

    print(f"[OK] Saved: {text_path}")


def main():
    """Main entry point"""
    print("=" * 60)
    print("MECHANICAL BIBLE - FULL TRANSLATION")
    print("Translating entire Tanakh through pictographic analysis")
    print("=" * 60)
    print()

    results, book_results = process_tanakh()

    if results:
        save_results(results, book_results)

        print()
        print("=" * 60)
        print("[OK] MECHANICAL BIBLE TRANSLATION COMPLETE")
        print(f"Total verses: {len(results)}")
        print(f"Total books: {len(book_results)}")
        print(f"Output: {OUTPUT_DIR}")
        print("=" * 60)

        # Show sample
        print()
        print("SAMPLE - Genesis 1:1:")
        print("-" * 40)
        sample = results[0]
        print(f"Hebrew: {sample.hebrew_text}")
        print(f"English: {sample.english_text}")
        print(f"Mechanical: {sample.mechanical_translation}")
        print(f"Gematria: {sample.verse_gematria}")
    else:
        print("[FAIL] No results generated")


if __name__ == '__main__':
    main()
