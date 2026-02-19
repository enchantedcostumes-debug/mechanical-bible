#!/usr/bin/env python3
"""
RECONCILE LEXICONS - Mechanical Bible
=======================================
Merges AHLB (Jeff Benner) definitions into words.json, replacing
Strong's concordance glosses with Benner's concrete Hebrew definitions.

Also adds:
- Root information (parent root, root action/concrete/abstract)
- KJV translation field from AHLB
- Verb form data
- Part of speech from grammatical form codes

Priority:
1. AHLB definition (concrete Hebrew meaning) - PRIMARY
2. Existing definition if no AHLB match
3. Pictographic placeholder as last resort

SAFE: Only modifies definition-related fields. Does NOT touch
gematria, letters, pictographic, timeline, frequency, or first_occurrence.

Usage: python reconcile_lexicons.py

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent

# Input files
WORDS_JSON = BASE_DIR / 'words.json'
AHLB_BY_STRONGS = BASE_DIR / 'data' / 'ahlb_by_strongs.json'
AHLB_COMPLETE = BASE_DIR / 'data' / 'ahlb_complete.json'

# Part of speech mapping from AHLB grammatical form codes
GRAM_TO_POS = {
    'V': 'verb',
    'Nm': 'noun',
    'Nf': 'noun',
    'Nf1': 'noun',
    'Nf2': 'noun',
    'Nf3': 'noun',
    'Nf4': 'noun',
}
# All lowercase letter forms are noun derivatives
for c in 'abcdefghijklmnopqrst':
    GRAM_TO_POS[c + 'm'] = 'noun'
    GRAM_TO_POS[c + 'f'] = 'noun'
    GRAM_TO_POS[c + 'f1'] = 'noun'
    GRAM_TO_POS[c + 'f2'] = 'noun'
    GRAM_TO_POS[c + 'f3'] = 'noun'
    GRAM_TO_POS[c + 'f4'] = 'noun'
    GRAM_TO_POS[c] = 'noun'  # bare letter = noun derivative


def load_ahlb():
    """Load parsed AHLB data."""
    if not AHLB_BY_STRONGS.exists():
        print(f'[ERROR] {AHLB_BY_STRONGS} not found. Run parse_ahlb_complete.py first.')
        return None, None

    with open(AHLB_BY_STRONGS, 'r', encoding='utf-8') as f:
        by_strongs = json.load(f)

    ahlb_roots = None
    if AHLB_COMPLETE.exists():
        with open(AHLB_COMPLETE, 'r', encoding='utf-8') as f:
            complete = json.load(f)
        ahlb_roots = complete.get('roots', [])

    print(f'[OK] Loaded AHLB: {len(by_strongs)} Strong\'s entries')
    if ahlb_roots:
        print(f'[OK] Loaded AHLB: {len(ahlb_roots)} root entries')

    return by_strongs, ahlb_roots


def load_words():
    """Load words.json."""
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'[OK] Loaded words.json: {len(words)} entries')
    return words


def reconcile(words, ahlb_strongs, ahlb_roots):
    """Merge AHLB data into words.json entries."""
    stats = {
        'ahlb_matched': 0,
        'definition_upgraded': 0,
        'pos_added': 0,
        'root_added': 0,
        'kjv_added': 0,
        'already_had_def': 0,
        'no_strongs': 0,
        'no_ahlb_match': 0,
        'pictograph_only': 0,
    }

    for hebrew_word, entry in words.items():
        strongs = entry.get('strongs', '')

        # Clean up Strong's number format
        if strongs:
            # Handle formats like "H1471_ל" -> "H1471"
            clean_strongs = re.sub(r'_.*$', '', strongs)
            # Also handle multiple numbers
            clean_strongs = clean_strongs.strip()
        else:
            clean_strongs = ''

        if not clean_strongs:
            stats['no_strongs'] += 1
            if entry.get('definition', '').startswith('[From pictographs'):
                stats['pictograph_only'] += 1
            continue

        # Look up in AHLB
        ahlb_entry = ahlb_strongs.get(clean_strongs)
        if not ahlb_entry:
            stats['no_ahlb_match'] += 1
            continue

        stats['ahlb_matched'] += 1

        # Get AHLB definition
        ahlb_def = ahlb_entry.get('definition', '')

        # Clean the AHLB definition — remove leading grammatical markers
        if ahlb_def:
            # Remove patterns like "ASh) —" or "ShP) —" at the start
            ahlb_def = re.sub(r'^[A-Za-z]{1,4}\)\s*[—–\-]+\s*', '', ahlb_def)
            ahlb_def = ahlb_def.strip()

        # UPGRADE DEFINITION
        current_def = entry.get('definition', '')
        is_placeholder = current_def.startswith('[From pictographs')

        if ahlb_def:
            # Always prefer AHLB concrete definition
            old_def = current_def
            entry['definition'] = ahlb_def

            # Store old definition as fallback reference
            if old_def and not is_placeholder and old_def != ahlb_def:
                entry['strongs_definition'] = old_def

            stats['definition_upgraded'] += 1
        elif not is_placeholder:
            stats['already_had_def'] += 1

        # ADD ROOT INFORMATION
        root = ahlb_entry.get('root', '')
        root_num = ahlb_entry.get('root_number', 0)
        if root or root_num:
            entry['ahlb_root'] = root
            entry['ahlb_root_number'] = root_num
            entry['root_action'] = ahlb_entry.get('root_action', '')
            entry['root_concrete'] = ahlb_entry.get('root_concrete', '')
            entry['root_abstract'] = ahlb_entry.get('root_abstract', '')
            stats['root_added'] += 1

        # ADD PART OF SPEECH
        gram_form = ahlb_entry.get('grammatical_form', '')
        if gram_form:
            pos = GRAM_TO_POS.get(gram_form, '')
            if not pos and ahlb_entry.get('is_verb'):
                pos = 'verb'
            if pos:
                entry['part_of_speech'] = pos
                stats['pos_added'] += 1

        # ADD KJV TRANSLATIONS
        kjv = ahlb_entry.get('kjv_translations', [])
        if kjv:
            entry['kjv_translations'] = kjv
            # Also set the timeline.kjv field
            if 'timeline' in entry and isinstance(entry['timeline'], dict):
                entry['timeline']['kjv'] = ', '.join(kjv[:5])
            stats['kjv_added'] += 1

        # ADD VERB FORMS
        verb_forms = ahlb_entry.get('verb_forms', [])
        if verb_forms:
            entry['verb_forms'] = verb_forms

        # ADD FREQUENCY FROM AHLB (more accurate than our count)
        ahlb_freq = ahlb_entry.get('frequency', 0)
        if ahlb_freq > 0:
            entry['ahlb_frequency'] = ahlb_freq

    return stats


def save_words(words):
    """Save updated words.json."""
    # Backup current file
    backup = WORDS_JSON.with_suffix('.json.bak')
    import shutil
    shutil.copy2(WORDS_JSON, backup)
    print(f'[OK] Backup saved to {backup}')

    with open(WORDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)
    print(f'[OK] Saved updated words.json ({WORDS_JSON.stat().st_size:,} bytes)')

    # Also update words-priority.json if it exists
    priority_path = BASE_DIR / 'words-priority.json'
    if priority_path.exists():
        with open(priority_path, 'r', encoding='utf-8') as f:
            priority = json.load(f)

        updated = 0
        for key in priority:
            if key in words:
                # Copy AHLB fields
                for field in ['definition', 'strongs_definition', 'part_of_speech',
                              'ahlb_root', 'ahlb_root_number', 'root_action',
                              'root_concrete', 'root_abstract', 'kjv_translations',
                              'verb_forms', 'ahlb_frequency']:
                    if field in words[key]:
                        priority[key][field] = words[key][field]
                        updated += 1

        with open(priority_path, 'w', encoding='utf-8') as f:
            json.dump(priority, f, ensure_ascii=False)
        print(f'[OK] Updated words-priority.json ({updated} field updates)')


def main():
    print('=' * 60)
    print('RECONCILE LEXICONS - Mechanical Bible')
    print('Merging AHLB (Jeff Benner) into words.json')
    print('=' * 60)

    ahlb_strongs, ahlb_roots = load_ahlb()
    if ahlb_strongs is None:
        return

    words = load_words()
    stats = reconcile(words, ahlb_strongs, ahlb_roots)

    print('\n' + '=' * 60)
    print('RECONCILIATION RESULTS')
    print('=' * 60)
    print(f'  Words matched to AHLB:     {stats["ahlb_matched"]:>6}')
    print(f'  Definitions upgraded:       {stats["definition_upgraded"]:>6}')
    print(f'  Part of speech added:       {stats["pos_added"]:>6}')
    print(f'  Root info added:            {stats["root_added"]:>6}')
    print(f'  KJV translations added:     {stats["kjv_added"]:>6}')
    print(f'  Already had definition:     {stats["already_had_def"]:>6}')
    print(f'  No Strong\'s number:         {stats["no_strongs"]:>6}')
    print(f'  No AHLB match:              {stats["no_ahlb_match"]:>6}')
    print(f'  Pictograph-only (no match): {stats["pictograph_only"]:>6}')

    # Show sample upgraded entries
    print('\n' + '=' * 60)
    print('SAMPLE UPGRADED ENTRIES')
    print('=' * 60)

    test_words_hebrew = {}
    for hw, entry in words.items():
        sn = entry.get('strongs', '')
        if sn in ('H7225', 'H1254', 'H430', 'H776', 'H120', 'H8451',
                   'H7965', 'H2617', 'H7307', 'H5315', 'H410', 'H1285', 'H571'):
            test_words_hebrew[sn] = (hw, entry)

    for sn in ('H7225', 'H1254', 'H430', 'H776', 'H120', 'H8451',
               'H7965', 'H2617', 'H7307', 'H5315', 'H410', 'H1285', 'H571'):
        if sn in test_words_hebrew:
            hw, entry = test_words_hebrew[sn]
            print(f'\n  {sn} ({hw}):')
            print(f'    AHLB Definition: {entry.get("definition", "")[:100]}')
            old = entry.get('strongs_definition', '')
            if old:
                print(f'    Old (Strong\'s):  {old[:100]}')
            pos = entry.get('part_of_speech', '')
            if pos:
                print(f'    Part of Speech:  {pos}')
            root = entry.get('ahlb_root', '')
            if root:
                print(f'    Root: {root} (ac:{entry.get("root_action","")}, co:{entry.get("root_concrete","")}, ab:{entry.get("root_abstract","")})')

    save_words(words)

    print('\n' + '=' * 60)
    print('[DONE] Lexicon reconciliation complete')
    print('=' * 60)


if __name__ == '__main__':
    main()
