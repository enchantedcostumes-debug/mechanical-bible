#!/usr/bin/env python3
"""
TRANSLATE ALL WORDS - Mechanical Bible
========================================
Generates REAL definitions for ALL 58,435 words in words.json.

Strategy (in priority order):
1. Already has AHLB definition -> KEEP IT
2. Strip Hebrew prefixes -> find root with AHLB definition -> compose definition
3. Match to any known root word in words.json -> compose definition
4. Use AHLB by-strongs lookup for prefix+strongs combos
5. Generate mechanical definition from pictographic letter analysis

Hebrew Prefix Meanings:
  ו (vav)   = "and" / "then" (conjunction/consecutive)
  ב (bet)   = "in" / "with" / "by" (preposition)
  ל (lamed) = "to" / "for" (preposition)
  כ (kaf)   = "like" / "as" (comparison)
  מ (mem)   = "from" / "of" (preposition)
  ה (he)    = "the" (definite article) or interrogative
  ש (shin)  = "that" / "which" (relative)

Hebrew Suffix Meanings:
  ים (im)    = plural masculine
  ות (ot)    = plural feminine
  ה (ah)     = feminine / directional
  י (i/y)    = "my" or adjective
  ך (kha)    = "your" (m.sg.)
  ו (o/v)    = "his" or "him"
  ם (am/m)   = "them" / "their" (m.pl.)
  ן (an/n)   = "them" / "their" (f.pl.)

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'
AHLB_BY_STRONGS = BASE_DIR / 'data' / 'ahlb_by_strongs.json'

# Hebrew prefix definitions
PREFIXES = {
    'ו': 'And',
    'וה': 'And the',
    'וב': 'And in',
    'ול': 'And to',
    'וכ': 'And like',
    'ומ': 'And from',
    'ב': 'In',
    'בה': 'In the',
    'ל': 'To',
    'לה': 'To the',
    'כ': 'Like',
    'כה': 'Like the',
    'מ': 'From',
    'מה': 'From the',
    'ה': 'The',
    'ש': 'That',
    'שב': 'That in',
    'של': 'That to',
    'שה': 'That the',
}

# Pictograph meanings for each Hebrew letter
LETTER_PICTOGRAPHS = {
    'א': ('Ox-head', 'strength, leader, first'),
    'ב': ('House', 'family, inside, contain'),
    'ג': ('Foot', 'walk, gather, carry'),
    'ד': ('Door', 'move, open, pathway'),
    'ה': ('Window/Man', 'behold, reveal, breath'),
    'ו': ('Nail/Peg', 'secure, add, connect'),
    'ז': ('Mattock', 'cut, nourish, weapon'),
    'ח': ('Wall/Fence', 'outside, divide, protect'),
    'ט': ('Basket', 'surround, contain, clay'),
    'י': ('Hand', 'work, deed, make'),
    'כ': ('Palm', 'open, allow, cover'),
    'ל': ('Staff', 'authority, teach, toward'),
    'מ': ('Water', 'chaos, flow, mighty'),
    'נ': ('Seed', 'continue, heir, life'),
    'ס': ('Thorn', 'grab, protect, shield'),
    'ע': ('Eye', 'see, know, experience'),
    'פ': ('Mouth', 'speak, open, edge'),
    'צ': ('Man-on-side', 'hunt, journey, righteous'),
    'ק': ('Horizon', 'circle, time, condense'),
    'ר': ('Head', 'first, top, person'),
    'ש': ('Teeth', 'sharp, consume, repeat'),
    'ת': ('Cross-mark', 'sign, covenant, seal'),
    # Final forms
    'ך': ('Palm', 'open, allow, cover'),
    'ם': ('Water', 'chaos, flow, mighty'),
    'ן': ('Seed', 'continue, heir, life'),
    'ף': ('Mouth', 'speak, open, edge'),
    'ץ': ('Man-on-side', 'hunt, journey, righteous'),
}

# Two-letter root meaning combinations (Benner's parent roots)
# These are the concrete meanings of 2-letter parent roots
PARENT_ROOT_MEANINGS = {}


def load_data():
    """Load words.json and AHLB data."""
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)

    ahlb = {}
    if AHLB_BY_STRONGS.exists():
        with open(AHLB_BY_STRONGS, 'r', encoding='utf-8') as f:
            ahlb = json.load(f)

    return words, ahlb


def strip_prefixes(hebrew):
    """Strip Hebrew prefixes and return (prefix_text, root_word, prefixes_found)."""
    if not hebrew or len(hebrew) < 2:
        return '', hebrew, []

    original = hebrew
    prefixes_found = []
    prefix_text_parts = []

    # Try multi-char prefixes first, then single
    # Order matters: try longer prefixes first
    prefix_order = ['וה', 'וב', 'ול', 'וכ', 'ומ', 'בה', 'לה', 'כה', 'מה', 'שב', 'של', 'שה',
                     'ו', 'ב', 'ל', 'כ', 'מ', 'ה', 'ש']

    for prefix in prefix_order:
        if hebrew.startswith(prefix) and len(hebrew) > len(prefix) + 1:
            prefix_text_parts.append(PREFIXES[prefix])
            prefixes_found.append(prefix)
            hebrew = hebrew[len(prefix):]
            break  # Only strip one prefix layer

    prefix_text = ' '.join(prefix_text_parts)
    return prefix_text, hebrew, prefixes_found


def strip_suffixes(hebrew):
    """Strip Hebrew suffixes and return (root_word, suffix_text)."""
    if not hebrew or len(hebrew) < 3:
        return hebrew, ''

    suffix_text = ''

    # Common suffix patterns (check longest first)
    if hebrew.endswith('יהם') and len(hebrew) > 4:
        return hebrew[:-3], 'their'
    if hebrew.endswith('יהן') and len(hebrew) > 4:
        return hebrew[:-3], 'their (f)'
    if hebrew.endswith('ותם') and len(hebrew) > 4:
        return hebrew[:-3], 'their'
    if hebrew.endswith('ים') and len(hebrew) > 3:
        return hebrew[:-2], '(plural)'
    if hebrew.endswith('ות') and len(hebrew) > 3:
        return hebrew[:-2], '(plural f)'
    if hebrew.endswith('יו') and len(hebrew) > 3:
        return hebrew[:-2], 'his'
    if hebrew.endswith('יך') and len(hebrew) > 3:
        return hebrew[:-2], 'your'
    if hebrew.endswith('ני') and len(hebrew) > 3:
        return hebrew[:-2], 'me'
    if hebrew.endswith('נו') and len(hebrew) > 3:
        return hebrew[:-2], 'us/our'
    if hebrew.endswith('הם') and len(hebrew) > 3:
        return hebrew[:-2], 'them'
    if hebrew.endswith('כם') and len(hebrew) > 3:
        return hebrew[:-2], 'you (pl)'

    return hebrew, suffix_text


def build_pictographic_definition(hebrew, entry):
    """Build a mechanical definition from pictographic letter analysis."""
    letters_data = entry.get('letters', [])

    if not letters_data and hebrew:
        # Build from the letter pictographs
        parts = []
        for letter in hebrew:
            if letter in LETTER_PICTOGRAPHS:
                pic, meanings = LETTER_PICTOGRAPHS[letter]
                parts.append(f'{pic}({meanings})')
        if parts:
            return f"[{' + '.join(parts)}]"
        return ''

    # Use the existing letter analysis from words.json
    if letters_data:
        concrete_parts = []
        for ld in letters_data:
            concrete = ld.get('concrete', '')
            if concrete:
                concrete_parts.append(concrete)
            else:
                abstract = ld.get('abstract', '')
                if abstract:
                    concrete_parts.append(abstract)

        if concrete_parts:
            # Combine into a flowing definition
            return ' '.join(concrete_parts)

    return ''


def try_find_root(hebrew, words):
    """Try to find the root word in words.json by progressively stripping prefixes/suffixes."""
    # Direct lookup
    if hebrew in words and not words[hebrew].get('definition', '').startswith('[From'):
        return hebrew, words[hebrew].get('definition', '')

    # Try prefix stripping
    _, stripped, _ = strip_prefixes(hebrew)
    if stripped in words and not words[stripped].get('definition', '').startswith('[From'):
        return stripped, words[stripped].get('definition', '')

    # Try suffix stripping
    root, _ = strip_suffixes(hebrew)
    if root in words and not words[root].get('definition', '').startswith('[From'):
        return root, words[root].get('definition', '')

    # Try both prefix and suffix
    _, stripped, _ = strip_prefixes(hebrew)
    root, _ = strip_suffixes(stripped)
    if root in words and not words[root].get('definition', '').startswith('[From'):
        return root, words[root].get('definition', '')

    # Try adding ה back (some words lost definite article)
    if stripped and stripped[0] != 'ה':
        with_he = 'ה' + stripped
        if with_he in words and not words[with_he].get('definition', '').startswith('[From'):
            return with_he, words[with_he].get('definition', '')

    return None, None


def translate_all(words, ahlb):
    """Generate definitions for ALL words."""
    stats = {
        'already_has_ahlb': 0,
        'matched_by_prefix_strip': 0,
        'matched_by_strongs_prefix': 0,
        'pictographic_generated': 0,
        'total': len(words),
    }

    # First pass: build a lookup of words that have real definitions
    # (from AHLB reconciliation or manual entry)
    defined_words = {}
    for hw, entry in words.items():
        d = entry.get('definition', '')
        if d and not d.startswith('[From pictographs') and not d.startswith('['):
            defined_words[hw] = d

    print(f'[INFO] {len(defined_words)} words already have real definitions')

    # Also build Strong's lookup from words.json entries
    strongs_to_def = {}
    for hw, entry in words.items():
        sn = entry.get('strongs', '')
        d = entry.get('definition', '')
        if sn and d and not d.startswith('[From'):
            clean_sn = re.sub(r'_.*$', '', sn)
            if clean_sn not in strongs_to_def:
                strongs_to_def[clean_sn] = d

    # Add AHLB definitions to strongs lookup
    for sn, ahlb_entry in ahlb.items():
        d = ahlb_entry.get('definition', '')
        if d and sn not in strongs_to_def:
            strongs_to_def[sn] = d

    print(f'[INFO] {len(strongs_to_def)} Strong\'s numbers have definitions')

    # Second pass: translate all words
    for hw, entry in words.items():
        current_def = entry.get('definition', '')

        # Skip if already has a real definition
        if current_def and not current_def.startswith('[From pictographs') and not current_def.startswith('['):
            stats['already_has_ahlb'] += 1
            continue

        # Strategy 1: Strip prefixes and look up root
        prefix_text, root_word, prefixes = strip_prefixes(hw)

        # Try finding root with/without suffixes
        found_root, root_def = try_find_root(hw, words)

        if not root_def and root_word != hw:
            found_root, root_def = try_find_root(root_word, words)

        if root_def:
            if prefix_text:
                entry['definition'] = f'{prefix_text} {root_def}'
            else:
                entry['definition'] = root_def

            # Copy POS from root if available
            if found_root and found_root in words:
                root_entry = words[found_root]
                if 'part_of_speech' in root_entry and 'part_of_speech' not in entry:
                    entry['part_of_speech'] = root_entry['part_of_speech']
                if 'ahlb_root' in root_entry and 'ahlb_root' not in entry:
                    entry['ahlb_root'] = root_entry['ahlb_root']
                    entry['root_action'] = root_entry.get('root_action', '')
                    entry['root_concrete'] = root_entry.get('root_concrete', '')
                    entry['root_abstract'] = root_entry.get('root_abstract', '')

            stats['matched_by_prefix_strip'] += 1
            continue

        # Strategy 2: Check for Strong's number with prefix suffix
        sn = entry.get('strongs', '')
        if sn:
            clean_sn = re.sub(r'_.*$', '', sn)
            if clean_sn in strongs_to_def:
                # Get the prefix from the strongs notation (e.g. H3068_ל -> "to")
                prefix_part = ''
                if '_' in sn:
                    prefix_char = sn.split('_')[1]
                    prefix_part = PREFIXES.get(prefix_char, '')

                root_d = strongs_to_def[clean_sn]
                if prefix_part:
                    entry['definition'] = f'{prefix_part} {root_d}'
                else:
                    entry['definition'] = root_d
                stats['matched_by_strongs_prefix'] += 1
                continue

        # Strategy 3: Build from pictographic letter analysis
        pic_def = build_pictographic_definition(hw, entry)
        if pic_def:
            entry['definition'] = pic_def
            stats['pictographic_generated'] += 1
        else:
            # Last resort: better pictographic description
            parts = []
            for letter in hw:
                if letter in LETTER_PICTOGRAPHS:
                    pic, meanings = LETTER_PICTOGRAPHS[letter]
                    first_meaning = meanings.split(',')[0].strip()
                    parts.append(first_meaning)
            if parts:
                entry['definition'] = ' - '.join(parts)
                stats['pictographic_generated'] += 1

    return stats


def save_words(words):
    """Save the fully translated words.json."""
    with open(WORDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)
    print(f'[SAVED] {WORDS_JSON} ({WORDS_JSON.stat().st_size:,} bytes)')


def verify_results(words):
    """Show sample results and coverage stats."""
    total = len(words)
    has_real_def = 0
    still_placeholder = 0
    has_from_pic = 0

    samples_good = []
    samples_prefix = []

    for hw, entry in words.items():
        d = entry.get('definition', '')
        if d.startswith('[From pictographs'):
            still_placeholder += 1
        elif d.startswith('['):
            has_from_pic += 1
        elif d:
            has_real_def += 1
            if len(samples_good) < 5:
                samples_good.append((hw, d[:100]))

    print(f'\n  Total words:         {total}')
    print(f'  Real definitions:    {has_real_def} ({has_real_def/total*100:.1f}%)')
    print(f'  Pictographic (new):  {has_from_pic}')
    print(f'  Still placeholder:   {still_placeholder}')

    # Show Genesis 1:1 words
    print('\n=== GENESIS 1:1 WORDS ===')
    gen1_words = ['בראשית', 'ברא', 'אלהים', 'את', 'השמים', 'ואת', 'הארץ']
    for hw in gen1_words:
        if hw in words:
            d = words[hw].get('definition', '')[:80]
            print(f'  {hw} = {d}')
        else:
            # Try to find it
            for key in words:
                if key.replace('\u200d', '') == hw or hw in key:
                    d = words[key].get('definition', '')[:80]
                    print(f'  {key} = {d}')
                    break

    # Show some prefix-stripped examples
    print('\n=== SAMPLE PREFIX-COMPOSED DEFINITIONS ===')
    count = 0
    for hw, entry in words.items():
        d = entry.get('definition', '')
        if d and d.startswith(('And ', 'In ', 'To ', 'From ', 'Like ', 'The ', 'That ')):
            if count < 15:
                print(f'  {hw} = {d[:80]}')
                count += 1


def main():
    print('=' * 60)
    print('TRANSLATE ALL WORDS - Mechanical Bible')
    print('Every. Single. Word. Gets. A. Definition.')
    print('=' * 60)

    words, ahlb = load_data()
    print(f'[OK] Loaded {len(words)} words, {len(ahlb)} AHLB entries')

    stats = translate_all(words, ahlb)

    print('\n' + '=' * 60)
    print('TRANSLATION RESULTS')
    print('=' * 60)
    print(f'  Already had AHLB def:      {stats["already_has_ahlb"]:>6}')
    print(f'  Matched by prefix strip:   {stats["matched_by_prefix_strip"]:>6}')
    print(f'  Matched by Strong\'s+pfx:   {stats["matched_by_strongs_prefix"]:>6}')
    print(f'  Pictographic generated:    {stats["pictographic_generated"]:>6}')
    print(f'  TOTAL:                     {stats["total"]:>6}')

    print('\n' + '=' * 60)
    print('VERIFICATION')
    print('=' * 60)
    verify_results(words)

    save_words(words)

    print('\n' + '=' * 60)
    print('[DONE] ALL WORDS TRANSLATED')
    print('=' * 60)


if __name__ == '__main__':
    main()
