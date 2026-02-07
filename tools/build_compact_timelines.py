#!/usr/bin/env python3
"""
Build COMPACT 6-Stage Timelines for ALL Words
==============================================

Creates a separate timelines.json file to keep words.json under 100MB.
The modal JavaScript will load timelines separately.

This keeps:
- words.json: Core word data (~75MB)
- timelines.json: Timeline data for all words (~100MB)

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
from pathlib import Path


def load_json(filepath):
    """Load a JSON file."""
    if not Path(filepath).exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(filepath, data):
    """Save data to JSON file (compact format)."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=None, separators=(',', ':'))


def build_compact_timeline(word_data, greek_data):
    """Build compact 6-stage timeline for a word."""
    hebrew = word_data.get('hebrew', '')
    definition = word_data.get('definition', '')
    strongs = word_data.get('strongs', '')

    # Get pictographic meaning from letters
    letters = word_data.get('letters', [])
    if letters:
        pics = [l.get('pictograph', l.get('concrete', ''))[:20] for l in letters if l.get('pictograph') or l.get('concrete')]
        pictographic = ' + '.join(pics) if pics else definition
    else:
        pictographic = definition

    # Get Greek data
    greek = greek_data.get(hebrew, {})
    greek_word = greek.get('greek', '')
    greek_translit = greek.get('translit', '')

    # COMPACT timeline - only essential fields
    return {
        's1': {'t': hebrew, 'm': pictographic[:100] if pictographic else ''},
        's2': {'t': greek_word, 'tr': greek_translit, 'm': greek.get('meaning', '')[:80]},
        's3': {'t': greek_word, 'm': ''},  # NT Greek
        's4': {'t': '', 'm': ''},  # Vulgate
        's5': {'t': definition.split(',')[0][:40] if definition else '', 'm': definition[:60] if definition else ''},
        's6': {'m': definition[:80] if definition else ''},
        'str': strongs  # Strong's reference
    }


def main():
    print("=" * 70)
    print("BUILDING COMPACT TIMELINES (SEPARATE FILE)")
    print("=" * 70)

    # Paths
    words_path = Path('C:/mechanical-bible/words.json')
    greek_path = Path('C:/mechanical-bible/data/hebrew_greek_mapping.json')
    timelines_path = Path('C:/mechanical-bible/timelines.json')

    # Load data
    print("\n[INFO] Loading words.json...")
    words = load_json(words_path)
    print(f"[OK] Loaded {len(words)} words")

    print("\n[INFO] Loading hebrew_greek_mapping.json...")
    greek_mapping = load_json(greek_path)
    if '_metadata' in greek_mapping:
        del greek_mapping['_metadata']
    print(f"[OK] Loaded {len(greek_mapping)} Greek mappings")

    # Build compact timelines
    print("\n[INFO] Building compact timelines...")
    timelines = {}

    for hebrew, word_data in words.items():
        # Skip words that have full scholarly timelines in words.json
        # (Genesis 1:1 words will stay in words.json)
        existing = word_data.get('corruption_timeline', {})
        if existing.get('stage_1', {}).get('scholarly_debate', ''):
            # Has scholarly data - keep in words.json, skip compact
            continue

        # Remove timeline from words.json (will be in separate file)
        if 'corruption_timeline' in word_data:
            del word_data['corruption_timeline']

        # Build compact timeline
        timelines[hebrew] = build_compact_timeline(word_data, greek_mapping)

    print(f"[OK] Built {len(timelines)} compact timelines")

    # Save compact timelines
    print("\n[INFO] Saving timelines.json...")
    save_json(timelines_path, timelines)
    size_mb = timelines_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved timelines.json ({size_mb:.1f} MB)")

    # Save updated words.json (without embedded timelines)
    print("\n[INFO] Saving updated words.json (without redundant timelines)...")
    save_json(words_path, words)
    words_size = words_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved words.json ({words_size:.1f} MB)")

    print()
    print("=" * 70)
    print(f"SUCCESS - Split into two files:")
    print(f"  words.json:     {words_size:.1f} MB (core data + 7 scholarly timelines)")
    print(f"  timelines.json: {size_mb:.1f} MB (compact timelines for {len(timelines)} words)")
    print("=" * 70)


if __name__ == '__main__':
    main()
