#!/usr/bin/env python3
"""
Build Hebrew Definitions Database
=================================

Converts lexicon_by_strongs.json (keyed by Strong's number) to
hebrew_definitions.json (keyed by Hebrew word) for the word modal.

This allows instant lookup of definitions when a user clicks any Hebrew word.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
from pathlib import Path


def build_hebrew_definitions():
    """Build hebrew_definitions.json from lexicon_by_strongs.json"""

    # Source file
    source_path = Path('C:/flask-structural-api/data/lexicon/lexicon_by_strongs.json')
    output_path = Path('C:/mechanical-bible/data/hebrew_definitions.json')

    print("=" * 70)
    print("BUILDING HEBREW DEFINITIONS DATABASE")
    print("=" * 70)

    # Load source
    print(f"\n[INFO] Loading {source_path}")
    with open(source_path, 'r', encoding='utf-8') as f:
        lexicon = json.load(f)

    print(f"[OK] Loaded {len(lexicon)} Strong's entries")

    # Build Hebrew-keyed dictionary
    hebrew_defs = {}

    for strongs_num, entry in lexicon.items():
        hebrew = entry.get('hebrew', '')
        if not hebrew:
            continue

        # Create lookup entry
        hebrew_defs[hebrew] = {
            'strongs': strongs_num,
            'transliteration': entry.get('transliteration', ''),
            'definition': entry.get('definition', ''),
            'root': entry.get('root', ''),
            'gematria': entry.get('gematria', 0),
            'digital_root': entry.get('digital_root', 0),
            'frequency': entry.get('frequency', 0),
            'first_occurrence': entry.get('first_occurrence', ''),
            'pictographic_meaning': entry.get('pictographic_meaning', ''),
            'letters': entry.get('letters', []),
            'kjv_translation': entry.get('kjv_translation', ''),
            'lxx_translation': entry.get('lxx_translation', ''),
            'vulgate_translation': entry.get('vulgate_translation', '')
        }

    print(f"[OK] Built {len(hebrew_defs)} Hebrew word entries")

    # Save output
    print(f"\n[INFO] Saving to {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(hebrew_defs, f, ensure_ascii=False, indent=2)

    # Calculate file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved {file_size_mb:.2f} MB")

    # Verify specific entries
    print("\n" + "-" * 70)
    print("VERIFICATION - Testing key lookups:")
    print("-" * 70)

    test_words = ['הארץ', 'בראשית', 'אלהים', 'ארץ', 'שמים']
    for word in test_words:
        if word in hebrew_defs:
            entry = hebrew_defs[word]
            print(f"  {word}: {entry['definition'][:50]}... (Strong's {entry['strongs']})")
        else:
            print(f"  {word}: NOT FOUND")

    print("\n" + "=" * 70)
    print(f"SUCCESS: {len(hebrew_defs)} Hebrew words with definitions")
    print("=" * 70)

    return hebrew_defs


if __name__ == '__main__':
    build_hebrew_definitions()
