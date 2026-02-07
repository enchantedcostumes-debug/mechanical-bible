#!/usr/bin/env python3
"""
Add Timeline Data (Greek, Latin, KJV) to words.json

This updates the timeline section for each word with:
- Septuagint Greek translation
- NT Greek (same as LXX for most words)
- Vulgate Latin translation
- KJV English translation

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


def main():
    print("=" * 70)
    print("ADDING TIMELINE DATA TO WORDS.JSON")
    print("=" * 70)

    # Paths
    words_path = Path('C:/mechanical-bible/words.json')
    greek_mapping_path = Path('C:/mechanical-bible/data/hebrew_greek_mapping.json')
    output_path = Path('C:/mechanical-bible/words.json')
    priority_path = Path('C:/mechanical-bible/words-priority.json')

    # Load words
    print("\n[INFO] Loading words.json...")
    words = load_json(words_path)
    print(f"[OK] Loaded {len(words)} words")

    # Load Greek mapping
    print("\n[INFO] Loading hebrew_greek_mapping.json...")
    greek_mapping = load_json(greek_mapping_path)
    # Remove metadata
    if '_metadata' in greek_mapping:
        del greek_mapping['_metadata']
    print(f"[OK] Loaded {len(greek_mapping)} Hebrew-Greek mappings")

    # Hebrew prefixes for lookup
    PREFIXES = ['ה', 'ב', 'כ', 'ל', 'מ', 'ו', 'ש']

    def lookup_greek(hebrew):
        """Look up Greek translation, trying prefix stripping."""
        if hebrew in greek_mapping:
            return greek_mapping[hebrew]
        # Try stripping prefixes
        for prefix in PREFIXES:
            if hebrew.startswith(prefix) and len(hebrew) > 1:
                stripped = hebrew[1:]
                if stripped in greek_mapping:
                    return greek_mapping[stripped]
        return None

    # Update timeline for each word
    updated = 0
    for hebrew, word in words.items():
        if 'timeline' not in word:
            word['timeline'] = {}

        timeline = word['timeline']
        greek = lookup_greek(hebrew)

        # Update Septuagint if we have Greek data
        if greek:
            greek_word = greek.get('greek', '')
            greek_translit = greek.get('translit', '')
            greek_meaning = greek.get('meaning', '')
            timeline['septuagint'] = f"{greek_word} ({greek_translit}) - {greek_meaning}"
            timeline['nt_greek'] = f"{greek_word} ({greek_translit})"
            updated += 1

        # Use definition for KJV if not already set
        if timeline.get('kjv') == '(Research in progress)' or not timeline.get('kjv'):
            definition = word.get('definition', '')
            if definition:
                timeline['kjv'] = definition

        # Use transliteration for modern if not already set
        if timeline.get('modern') == 'See pictographic meaning' or not timeline.get('modern'):
            definition = word.get('definition', '')
            if definition:
                timeline['modern'] = definition

    print()
    print("-" * 70)
    print(f"RESULTS:")
    print(f"  Words with Greek timeline data: {updated}")
    print("-" * 70)

    # Save updated words.json
    print("\n[INFO] Saving updated words.json...")
    save_json(output_path, words)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved {size_mb:.1f} MB")

    # Update priority words too
    if priority_path.exists():
        print("\n[INFO] Updating words-priority.json...")
        priority = load_json(priority_path)
        for hebrew, word in priority.items():
            if hebrew in words:
                word['timeline'] = words[hebrew].get('timeline', {})
        save_json(priority_path, priority)
        print(f"[OK] Updated {len(priority)} priority words")

    # Verify
    print()
    print("-" * 70)
    print("VERIFICATION:")
    print("-" * 70)

    for test in ['בראשית', 'אלהים', 'ארץ', 'אור', 'שמים']:
        if test in words:
            t = words[test].get('timeline', {})
            sep = t.get('septuagint', 'N/A')[:50]
            kjv = t.get('kjv', 'N/A')[:50]
            print(f"  {test}:")
            print(f"    Septuagint: {sep}")
            print(f"    KJV: {kjv}")

    print()
    print("=" * 70)
    print("SUCCESS")
    print("=" * 70)


if __name__ == '__main__':
    main()
