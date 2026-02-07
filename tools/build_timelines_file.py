#!/usr/bin/env python3
"""
Build Separate Timelines File for ALL 58,400 Words
===================================================

Creates timelines.json as a separate file loaded by word-modal.js.
This keeps words.json under GitHub's 100MB limit.

The modal will:
1. Load words.json (core data, ~78MB)
2. Load timelines.json (timeline data, ~30MB)
3. Merge on display

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


def build_timeline(word_data, greek_data):
    """Build 6-stage timeline for a word."""
    hebrew = word_data.get('hebrew', '')
    definition = word_data.get('definition', '')
    strongs = word_data.get('strongs', '')

    # Get pictographic from letters
    letters = word_data.get('letters', [])
    if letters:
        pics = []
        for l in letters:
            pic = l.get('pictograph', l.get('concrete', ''))
            if pic:
                pics.append(pic[:25])
        pictographic = ' + '.join(pics) if pics else definition
    else:
        pictographic = definition

    # Get Greek
    greek = greek_data.get(hebrew, {})

    return {
        '1': {  # Hebrew Original
            'n': 'Original Hebrew',
            'p': 'c. 1000-500 BCE',
            't': hebrew,
            'm': (pictographic or definition or '')[:120],
            'd': f"BDB/HALOT: '{definition}'. {f'Strongs {strongs}.' if strongs else ''}"
        },
        '2': {  # Septuagint
            'n': 'Septuagint Greek',
            'p': '280-130 BCE',
            't': greek.get('greek', ''),
            'tr': greek.get('translit', ''),
            'm': greek.get('meaning', '(LXX translation)')[:80],
            'd': 'Greek philosophical categories applied to Hebrew concrete thinking.'
        },
        '3': {  # NT Greek
            'n': 'NT Greek',
            'p': '50-100 CE',
            't': greek.get('greek', ''),
            'm': '(NT usage)',
            'd': 'Christological reinterpretation; see TDNT/Kittel.'
        },
        '4': {  # Vulgate
            'n': 'Latin Vulgate',
            'p': '382-405 CE',
            't': '',
            'm': '(Latin)',
            'd': 'Jerome translated for Western church; Latin legal/institutional connotations.'
        },
        '5': {  # KJV
            'n': 'King James',
            'p': '1611 CE',
            't': (definition.split(',')[0] if definition else '')[:40],
            'm': definition[:80] if definition else '',
            'd': 'KJV established English biblical vocabulary.'
        },
        '6': {  # Modern
            'n': 'Modern English',
            'p': 'Today',
            't': (definition.split(',')[0] if definition else ''),
            'm': definition[:100] if definition else 'See Hebrew pictographic meaning',
            'd': 'Modern interpretation; original Hebrew nuance often invisible.'
        }
    }


def main():
    print("=" * 70)
    print("BUILDING SEPARATE TIMELINES FILE")
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

    # Build timelines for ALL words
    print("\n[INFO] Building timelines for all words...")
    timelines = {}
    preserved = 0

    for hebrew, word_data in words.items():
        # Preserve scholarly timelines (Genesis 1:1 words)
        existing = word_data.get('corruption_timeline', {})
        if existing.get('stage_1', {}).get('scholarly_debate', ''):
            # Keep full scholarly timeline in timelines.json too
            timelines[hebrew] = existing
            preserved += 1
        else:
            # Build new compact timeline
            timelines[hebrew] = build_timeline(word_data, greek_mapping)

    print(f"[OK] Built {len(timelines)} timelines ({preserved} scholarly preserved)")

    # Save timelines.json
    print("\n[INFO] Saving timelines.json...")
    save_json(timelines_path, timelines)
    size_mb = timelines_path.stat().st_size / (1024 * 1024)
    print(f"[OK] Saved timelines.json ({size_mb:.1f} MB)")

    # Verify
    print()
    print("-" * 70)
    print("VERIFICATION - Sample timelines:")
    print("-" * 70)

    samples = ['בראשית', 'אדם', 'שלום', 'אהבה', 'תורה']
    for s in samples:
        if s in timelines:
            t = timelines[s]
            stage1 = t.get('1', t.get('stage_1', {}))
            stage6 = t.get('6', t.get('stage_6', {}))
            m1 = stage1.get('m', stage1.get('meaning', ''))[:50]
            m6 = stage6.get('m', stage6.get('meaning', ''))[:50]
            print(f"\n{s}:")
            print(f"  Stage 1: {m1}...")
            print(f"  Stage 6: {m6}...")

    print()
    print("=" * 70)
    print(f"SUCCESS - Created timelines.json ({size_mb:.1f} MB)")
    print("Now update word-modal.js to load this file")
    print("=" * 70)


if __name__ == '__main__':
    main()
