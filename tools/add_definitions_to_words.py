#!/usr/bin/env python3
"""
Add Transliteration and Definitions to words.json

This script enriches the words.json file by adding:
- transliteration (how to pronounce the Hebrew)
- definition (what the word means in English)
- strongs (Strong's number for reference)

Uses hebrew_lexicon_complete.json which has 58,400 entries.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
from pathlib import Path


def load_json(filepath):
    """Load a JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save data to JSON file (compact format for words.json)."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=None, separators=(',', ':'))


def main():
    print("=" * 70)
    print("ADDING DEFINITIONS TO WORDS.JSON FROM COMPLETE LEXICON")
    print("=" * 70)

    # Paths
    words_path = Path('C:/mechanical-bible/words.json')
    complete_lexicon_path = Path('C:/flask-structural-api/data/lexicon/hebrew_lexicon_complete.json')
    output_path = Path('C:/mechanical-bible/words.json')
    priority_path = Path('C:/mechanical-bible/words-priority.json')

    # Load data
    print("\n[INFO] Loading words.json...")
    words = load_json(words_path)
    print(f"[OK] Loaded {len(words)} words")

    print("\n[INFO] Loading hebrew_lexicon_complete.json (122 MB)...")
    complete = load_json(complete_lexicon_path)
    entries = complete.get('entries', {})
    print(f"[OK] Loaded {len(entries)} complete lexicon entries")

    # Enrich words with data from complete lexicon
    enriched = 0
    not_found = 0

    for hebrew, word in words.items():
        if hebrew in entries:
            entry = entries[hebrew]
            # Add transliteration and definition
            word['transliteration'] = entry.get('transliteration', '')
            word['definition'] = entry.get('definition', '')
            word['strongs'] = entry.get('strongs', '')

            # Add KJV translation if available
            if entry.get('kjv_translation'):
                word['timeline']['kjv'] = entry['kjv_translation']

            # Add Vulgate translation if available
            if entry.get('vulgate_translation'):
                word['timeline']['vulgate'] = entry['vulgate_translation']

            # Add LXX translation if available
            if entry.get('lxx_translation'):
                word['timeline']['septuagint'] = entry['lxx_translation']

            enriched += 1
        else:
            # Not found in complete lexicon
            if not word.get('transliteration'):
                word['transliteration'] = ''
            if not word.get('definition'):
                word['definition'] = ''
            not_found += 1

    print()
    print("-" * 70)
    print(f"ENRICHMENT RESULTS:")
    print(f"  Total words: {len(words)}")
    print(f"  Enriched with definitions: {enriched}")
    print(f"  Not found in complete lexicon: {not_found}")
    print("-" * 70)

    # Save updated words.json
    print("\n[INFO] Saving updated words.json...")
    save_json(output_path, words)
    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved {size_mb:.1f} MB")

    # Also update words-priority.json if it exists
    if priority_path.exists():
        print("\n[INFO] Updating words-priority.json...")
        priority = load_json(priority_path)
        for hebrew, word in priority.items():
            if hebrew in words:
                word['transliteration'] = words[hebrew].get('transliteration', '')
                word['definition'] = words[hebrew].get('definition', '')
                word['strongs'] = words[hebrew].get('strongs', '')
                if 'timeline' in words[hebrew]:
                    word['timeline'] = words[hebrew]['timeline']
        save_json(priority_path, priority)
        psize = priority_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Updated {len(priority)} priority words ({psize:.1f} MB)")

    # Verify a few entries
    print()
    print("-" * 70)
    print("VERIFICATION - Sample entries:")
    print("-" * 70)

    test_words = ['בראשית', 'אלהים', 'ארץ', 'השמים', 'הארץ', 'ברא', 'את', 'יום', 'אור', 'טוב']
    for test in test_words:
        if test in words:
            w = words[test]
            translit = w.get('transliteration', 'N/A') or 'N/A'
            defn = (w.get('definition', 'N/A') or 'N/A')[:60]
            print(f"  {test}: {translit} = {defn}")

    print()
    print("=" * 70)
    print(f"SUCCESS: {enriched} words now have transliteration and definitions")
    print("=" * 70)


if __name__ == '__main__':
    main()
