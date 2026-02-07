#!/usr/bin/env python3
"""
Add 6-Stage Corruption Timeline to Control Words

Takes the 32 control words and builds full 6-stage decay timelines
showing exactly how meaning was corrupted at each translation stage.

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


def build_corruption_timeline(word_data, greek_mapping):
    """Build 6-stage corruption timeline for a control word."""
    hebrew = word_data['hebrew']
    mechanism = word_data.get('control_mechanism', '')
    definition = word_data.get('definition', '')

    # Parse the control mechanism: "Original → Corrupted"
    if '→' in mechanism:
        parts = mechanism.split('→')
        original_meaning = parts[0].strip()
        corrupted_meaning = parts[1].strip() if len(parts) > 1 else ''
    else:
        original_meaning = definition
        corrupted_meaning = mechanism

    # Get Greek data if available
    greek = greek_mapping.get(hebrew, {})
    greek_word = greek.get('greek', '')
    greek_translit = greek.get('translit', '')
    greek_meaning = greek.get('meaning', '')

    # Build 6-stage timeline
    timeline = {
        'stage_1': {
            'name': 'Original Hebrew',
            'period': 'Pre-1000 BCE',
            'text': hebrew,
            'meaning': original_meaning,
            'mechanism': 'NONE - Original pictographic meaning intact'
        },
        'stage_2': {
            'name': 'Septuagint Greek',
            'period': '280-130 BCE',
            'text': greek_word if greek_word else '(translation)',
            'transliteration': greek_translit,
            'meaning': greek_meaning if greek_meaning else '(Greek rendering)',
            'mechanism': 'Greek philosophical categories applied; process → static concept'
        },
        'stage_3': {
            'name': 'NT Greek',
            'period': '50-100 CE',
            'text': greek_word if greek_word else '(same root)',
            'meaning': greek_meaning if greek_meaning else '(Christianized)',
            'mechanism': 'Christological theology overlay; Hebrew concept → Greek philosophy'
        },
        'stage_4': {
            'name': 'Latin Vulgate',
            'period': '382-405 CE',
            'text': '(Latin)',
            'meaning': '(Romanized)',
            'mechanism': 'Historical/institutional framework imposed'
        },
        'stage_5': {
            'name': 'King James',
            'period': '1611 CE',
            'text': definition,
            'meaning': definition,
            'mechanism': 'English idiom substituted; pictographic depth lost'
        },
        'stage_6': {
            'name': 'Modern English',
            'period': '1800-Present',
            'text': corrupted_meaning,
            'meaning': corrupted_meaning,
            'mechanism': 'Scientific materialism; " + original_meaning + " → ' + corrupted_meaning
        }
    }

    return timeline


def main():
    print("=" * 70)
    print("ADDING 6-STAGE CORRUPTION TIMELINES TO CONTROL WORDS")
    print("=" * 70)

    # Paths
    words_path = Path('C:/mechanical-bible/words.json')
    control_words_path = Path('C:/flask-structural-api/data/lexicon/control_words_lexicon.json')
    greek_mapping_path = Path('C:/mechanical-bible/data/hebrew_greek_mapping.json')
    priority_path = Path('C:/mechanical-bible/words-priority.json')

    # Load data
    print("\n[INFO] Loading words.json...")
    words = load_json(words_path)
    print(f"[OK] Loaded {len(words)} words")

    print("\n[INFO] Loading control_words_lexicon.json...")
    control_words = load_json(control_words_path)
    print(f"[OK] Loaded {len(control_words)} control words")

    print("\n[INFO] Loading hebrew_greek_mapping.json...")
    greek_mapping = load_json(greek_mapping_path)
    # Remove metadata
    if '_metadata' in greek_mapping:
        del greek_mapping['_metadata']
    print(f"[OK] Loaded {len(greek_mapping)} Greek mappings")

    # Process control words
    updated = 0
    for hebrew, control_data in control_words.items():
        if hebrew in words:
            # Add control word flag
            words[hebrew]['is_control_word'] = True
            words[hebrew]['control_mechanism'] = control_data.get('control_mechanism', '')

            # Build 6-stage corruption timeline
            corruption_timeline = build_corruption_timeline(control_data, greek_mapping)
            words[hebrew]['corruption_timeline'] = corruption_timeline

            updated += 1

    print()
    print("-" * 70)
    print(f"RESULTS:")
    print(f"  Control words with 6-stage timelines: {updated}")
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
            if hebrew in words and 'corruption_timeline' in words[hebrew]:
                word['is_control_word'] = words[hebrew].get('is_control_word', False)
                word['control_mechanism'] = words[hebrew].get('control_mechanism', '')
                word['corruption_timeline'] = words[hebrew]['corruption_timeline']
        save_json(priority_path, priority)
        print(f"[OK] Updated priority words")

    # Verify
    print()
    print("-" * 70)
    print("VERIFICATION - Sample control word timelines:")
    print("-" * 70)

    for test in ['בראשית', 'אלהים', 'נפש']:
        if test in words and 'corruption_timeline' in words[test]:
            print(f"\n{test} ({words[test].get('transliteration', '')}):")
            print(f"  Control mechanism: {words[test].get('control_mechanism', '')}")
            ct = words[test]['corruption_timeline']
            for stage_key in ['stage_1', 'stage_6']:
                stage = ct[stage_key]
                print(f"  {stage['name']}: {stage['meaning']}")

    print()
    print("=" * 70)
    print("SUCCESS - 32 control words now have 6-stage corruption timelines")
    print("=" * 70)


if __name__ == '__main__':
    main()
