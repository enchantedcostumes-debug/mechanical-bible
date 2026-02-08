#!/usr/bin/env python3
"""
Generate Definitions from Letter Pictographs
=============================================

For words missing definitions, create a definition from
the pictographic meanings of the constituent letters.

Also generates transliteration from letter names.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
from pathlib import Path


def load_json(filepath):
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save data to JSON file (compact format)."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=None, separators=(',', ':'))


# Letter transliteration map
LETTER_TRANSLIT = {
    'ALEPH': "'",
    'BET': 'b',
    'GIMEL': 'g',
    'DALET': 'd',
    'HEY': 'h',
    'VAV': 'v',
    'ZAYIN': 'z',
    'CHET': 'ch',
    'TET': 't',
    'YOD': 'y',
    'KAF': 'k',
    'LAMED': 'l',
    'MEM': 'm',
    'NUN': 'n',
    'SAMEKH': 's',
    'AYIN': "'",
    'PEY': 'p',
    'TSADE': 'ts',
    'QOF': 'q',
    'RESH': 'r',
    'SHIN': 'sh',
    'TAV': 't',
    # Final forms
    'FINAL_KAF': 'k',
    'FINAL_MEM': 'm',
    'FINAL_NUN': 'n',
    'FINAL_PEY': 'p',
    'FINAL_TSADE': 'ts',
}


def generate_transliteration(letters):
    """Generate transliteration from letter names."""
    if not letters:
        return ''

    translit_parts = []
    for letter in letters:
        name = letter.get('name', '').upper()
        if name in LETTER_TRANSLIT:
            translit_parts.append(LETTER_TRANSLIT[name])
        elif name:
            # Fallback: first char of name lowercase
            translit_parts.append(name[0].lower())

    return ''.join(translit_parts)


def generate_pictographic_definition(letters):
    """Generate definition from letter pictographs."""
    if not letters:
        return ''

    # Get pictograph or concrete meaning for each letter
    parts = []
    for letter in letters:
        pic = letter.get('pictograph', '')
        concrete = letter.get('concrete', '')
        abstract = letter.get('abstract', '')

        # Prefer concrete over pictograph for definition
        meaning = concrete or pic or abstract
        if meaning:
            # Take first meaning if comma-separated
            meaning = meaning.split(',')[0].strip()
            parts.append(meaning)

    if parts:
        return ' + '.join(parts)
    return ''


def main():
    print("=" * 70)
    print("GENERATING DEFINITIONS FROM LETTER PICTOGRAPHS")
    print("=" * 70)

    # Paths
    words_path = Path('C:/mechanical-bible/words.json')
    priority_path = Path('C:/mechanical-bible/words-priority.json')

    # Load data
    print("\n[INFO] Loading words.json...")
    words = load_json(words_path)
    print(f"[OK] Loaded {len(words)} words")

    # Track progress
    generated_translit = 0
    generated_def = 0
    already_had_def = 0

    for hebrew, word in words.items():
        letters = word.get('letters', [])

        # Generate transliteration if missing
        if not word.get('transliteration') and letters:
            translit = generate_transliteration(letters)
            if translit:
                word['transliteration'] = translit
                generated_translit += 1

        # Generate definition if missing
        if not word.get('definition'):
            if letters:
                pic_def = generate_pictographic_definition(letters)
                if pic_def:
                    word['definition'] = f"[From pictographs: {pic_def}]"
                    generated_def += 1
        else:
            already_had_def += 1

    print()
    print("-" * 70)
    print("RESULTS:")
    print(f"  Already had definition: {already_had_def}")
    print(f"  Generated transliteration: {generated_translit}")
    print(f"  Generated definition from pictographs: {generated_def}")
    print(f"  Total words with definition now: {already_had_def + generated_def}")
    print("-" * 70)

    # Save updated words.json
    print("\n[INFO] Saving updated words.json...")
    save_json(words_path, words)
    size_mb = words_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved {size_mb:.1f} MB")

    # Update priority words too
    if priority_path.exists():
        print("\n[INFO] Updating words-priority.json...")
        priority = load_json(priority_path)
        for hebrew, word in priority.items():
            if hebrew in words:
                word['transliteration'] = words[hebrew].get('transliteration', '')
                word['definition'] = words[hebrew].get('definition', '')
        save_json(priority_path, priority)
        print("[OK] Updated priority words")

    # Verification
    print()
    print("-" * 70)
    print("VERIFICATION - Sample generated entries:")
    print("-" * 70)

    samples = ['תהיה', 'וכלצבאם', 'ויברכהו', 'להחיתכם']
    for s in samples:
        if s in words:
            w = words[s]
            print(f"\n{s}:")
            print(f"  Transliteration: {w.get('transliteration', 'N/A')}")
            print(f"  Definition: {w.get('definition', 'N/A')[:60]}...")

    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
