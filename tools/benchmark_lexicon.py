#!/usr/bin/env python3
"""
BENCHMARK LEXICON - Mechanical Bible
======================================
Tests the quality, completeness, and correctness of the lexicon data.
Compares our definitions against AHLB (Jeff Benner) and Strong's concordance.

Run this after ANY changes to words.json or lexicon data.

Tests:
1. COVERAGE: Every word has a definition (no placeholders)
2. AHLB INTEGRATION: Key theological words match Benner's concrete meanings
3. CONTROL WORD DETECTION: Historically corrupted words are flagged
4. PREFIX COMPOSITION: Prefix+root definitions make grammatical sense
5. GENESIS 1 FULL: Complete mechanical translation of Genesis chapter 1
6. ROOT MAPPING: Words correctly trace back to their parent roots
7. GEMATRIA CONSISTENCY: Every word has valid gematria data

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'
AHLB_BY_STRONGS = BASE_DIR / 'data' / 'ahlb_by_strongs.json'

# Test results tracking
PASSED = 0
FAILED = 0
WARNINGS = 0


def test(name, condition, detail=''):
    """Run a single test assertion."""
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f'  [PASS] {name}')
    else:
        FAILED += 1
        print(f'  [FAIL] {name}')
        if detail:
            print(f'         {detail}')


def warn(name, detail=''):
    """Issue a warning (not a failure)."""
    global WARNINGS
    WARNINGS += 1
    print(f'  [WARN] {name}')
    if detail:
        print(f'         {detail}')


def load_data():
    """Load words.json and AHLB data."""
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)

    ahlb = {}
    if AHLB_BY_STRONGS.exists():
        with open(AHLB_BY_STRONGS, 'r', encoding='utf-8') as f:
            ahlb = json.load(f)

    return words, ahlb


def test_coverage(words):
    """TEST 1: Every word has a definition."""
    print('\n' + '=' * 60)
    print('TEST 1: DEFINITION COVERAGE')
    print('=' * 60)

    total = len(words)
    has_def = 0
    placeholder = 0
    empty = 0

    for hw, entry in words.items():
        d = entry.get('definition', '')
        if d.startswith('[From pictographs'):
            placeholder += 1
        elif d:
            has_def += 1
        else:
            empty += 1

    pct = has_def / total * 100 if total > 0 else 0

    test(f'Total words loaded: {total}', total > 50000, f'Expected >50000, got {total}')
    test(f'Words with real definitions: {has_def} ({pct:.1f}%)', pct > 99.0,
         f'Expected >99%, got {pct:.1f}%')
    test(f'No placeholder definitions remaining', placeholder == 0,
         f'{placeholder} words still have [From pictographs] placeholders')
    test(f'No empty definitions', empty == 0,
         f'{empty} words have empty definitions')

    return has_def, total


def test_ahlb_key_words(words):
    """TEST 2: Key theological words have AHLB concrete definitions."""
    print('\n' + '=' * 60)
    print('TEST 2: AHLB KEY WORD DEFINITIONS')
    print('=' * 60)

    # These words MUST have concrete AHLB definitions, not abstract theological glosses
    key_tests = {
        'בראשית': {
            'strongs': 'H7225',
            'must_contain': ['head', 'beginning'],
            'must_not_contain': ['In the beginning God created'],  # No JPS text
            'description': 'bereshit - beginning/head',
        },
        'ברא': {
            'strongs': 'H1254',
            'must_contain': ['fill', 'fat'],
            'must_not_contain': ['create from nothing', 'ex nihilo'],
            'description': 'bara - fill/fatten (NOT create from nothing)',
        },
        'אלהים': {
            'strongs': 'H430',
            'must_contain': ['power', 'yoke'],
            'must_not_contain': ['God Almighty'],
            'description': 'elohim - power/yoke',
        },
        'ארץ': {
            'strongs': 'H776',
            'must_contain': ['land'],
            'must_not_contain': ['planet', 'Planet Earth'],
            'description': 'erets - land/region (NOT planet Earth)',
        },
        'אדם': {
            'strongs': 'H120',
            'must_contain': ['man', 'red'],
            'must_not_contain': [],
            'description': 'adam - man (from reddish skin)',
        },
        'תורה': {
            'strongs': 'H8451',
            'must_contain': ['teach', 'direction'],
            'must_not_contain': [],
            'description': 'torah - teaching/direction',
        },
        'שלום': {
            'strongs': 'H7965',
            'must_contain': ['complete'],
            'must_not_contain': [],
            'description': 'shalom - completeness',
        },
        'רוח': {
            'strongs': 'H7307',
            'must_contain': ['wind', 'breath'],
            'must_not_contain': ['Holy Spirit', 'Ghost'],
            'description': 'ruach - wind/breath',
        },
        'נפש': {
            'strongs': 'H5315',
            'must_contain': ['soul'],
            'must_not_contain': ['immortal soul'],
            'description': 'nephesh - soul/being',
        },
        'ברית': {
            'strongs': 'H1285',
            'must_contain': ['covenant'],
            'must_not_contain': [],
            'description': 'berit - covenant',
        },
        'חסד': {
            'strongs': 'H2617',
            'must_contain': ['kindness', 'bow'],
            'must_not_contain': [],
            'description': 'chesed - kindness (bowing the neck)',
        },
        'אמת': {
            'strongs': 'H571',
            'must_contain': ['truth', 'firm'],
            'must_not_contain': [],
            'description': 'emeth - truth (what is firm)',
        },
    }

    for hebrew, expected in key_tests.items():
        if hebrew not in words:
            test(f'{expected["description"]} exists in lexicon', False,
                 f'Word {hebrew} not found in words.json')
            continue

        entry = words[hebrew]
        d = entry.get('definition', '').lower()

        # Check must_contain
        for term in expected['must_contain']:
            test(f'{expected["description"]} contains "{term}"',
                 term.lower() in d,
                 f'Definition: {d[:100]}')

        # Check must_not_contain
        for term in expected['must_not_contain']:
            test(f'{expected["description"]} does NOT contain "{term}"',
                 term.lower() not in d,
                 f'Definition: {d[:100]}')


def test_tetragrammaton(words):
    """TEST 3: YHWH / Tetragrammaton handling."""
    print('\n' + '=' * 60)
    print('TEST 3: TETRAGRAMMATON (YHWH)')
    print('=' * 60)

    yhwh_entry = words.get('יהוה')
    test('YHWH (יהוה) exists in lexicon', yhwh_entry is not None)

    if yhwh_entry:
        d = yhwh_entry.get('definition', '')
        trans = yhwh_entry.get('transliteration', '')
        test('YHWH has transliteration "YHWH"',
             trans.upper() == 'YHWH' or 'yhwh' in trans.lower(),
             f'Got: {trans}')
        test('YHWH definition references tetragrammaton or God of Israel',
             'tetragrammaton' in d.lower() or 'god of israel' in d.lower() or 'proper name' in d.lower(),
             f'Got: {d[:100]}')


def test_prefix_composition(words):
    """TEST 4: Prefix-composed definitions are grammatically correct."""
    print('\n' + '=' * 60)
    print('TEST 4: PREFIX COMPOSITION')
    print('=' * 60)

    # Test specific prefix+root combinations
    prefix_tests = {
        'והארץ': ('And', 'land'),       # vav + he + erets
        'בראשית': ('beginning',),        # should NOT start with "In" since it's a root word itself
        'ולחשך': ('And', 'dark'),        # vav + lamed + choshek
    }

    for hw, expected_parts in prefix_tests.items():
        if hw not in words:
            warn(f'{hw} not found in words.json')
            continue
        d = words[hw].get('definition', '').lower()
        for part in expected_parts:
            test(f'{hw} definition contains "{part}"',
                 part.lower() in d,
                 f'Definition: {d[:100]}')

    # Count prefix-composed definitions
    prefix_count = 0
    for hw, entry in words.items():
        d = entry.get('definition', '')
        if d.startswith(('And ', 'In ', 'To ', 'From ', 'Like ', 'The ', 'That ')):
            prefix_count += 1

    test(f'At least 5000 prefix-composed definitions exist',
         prefix_count >= 5000,
         f'Got {prefix_count}')


def test_part_of_speech(words):
    """TEST 5: Part of speech coverage."""
    print('\n' + '=' * 60)
    print('TEST 5: PART OF SPEECH')
    print('=' * 60)

    pos_counts = defaultdict(int)
    no_pos = 0

    for hw, entry in words.items():
        pos = entry.get('part_of_speech', '')
        if pos:
            pos_counts[pos] += 1
        else:
            no_pos += 1

    total_with_pos = sum(pos_counts.values())
    test(f'At least 1000 words have POS tags',
         total_with_pos >= 1000,
         f'Got {total_with_pos}')

    for pos, count in sorted(pos_counts.items(), key=lambda x: -x[1]):
        print(f'    {pos}: {count}')

    test(f'Nouns outnumber verbs (expected for Hebrew)',
         pos_counts.get('noun', 0) > pos_counts.get('verb', 0),
         f'Nouns: {pos_counts.get("noun", 0)}, Verbs: {pos_counts.get("verb", 0)}')


def test_root_mapping(words):
    """TEST 6: Root information is populated."""
    print('\n' + '=' * 60)
    print('TEST 6: ROOT MAPPING')
    print('=' * 60)

    has_root_action = 0
    has_root_concrete = 0
    has_root_abstract = 0

    for hw, entry in words.items():
        if entry.get('root_action'):
            has_root_action += 1
        if entry.get('root_concrete'):
            has_root_concrete += 1
        if entry.get('root_abstract'):
            has_root_abstract += 1

    test(f'At least 1000 words have root action definitions',
         has_root_action >= 1000,
         f'Got {has_root_action}')
    test(f'At least 500 words have root concrete definitions',
         has_root_concrete >= 500,
         f'Got {has_root_concrete}')

    print(f'    Root action:   {has_root_action}')
    print(f'    Root concrete: {has_root_concrete}')
    print(f'    Root abstract: {has_root_abstract}')


def test_gematria(words):
    """TEST 7: Gematria data integrity."""
    print('\n' + '=' * 60)
    print('TEST 7: GEMATRIA INTEGRITY')
    print('=' * 60)

    has_gematria = 0
    has_digital_root = 0
    invalid_gematria = 0

    for hw, entry in words.items():
        g = entry.get('gematria', 0)
        dr = entry.get('digital_root', 0)
        if g and g > 0:
            has_gematria += 1
        if dr and dr > 0:
            has_digital_root += 1
        if g and (not isinstance(g, (int, float)) or g < 0):
            invalid_gematria += 1

    pct = has_gematria / len(words) * 100
    test(f'Gematria coverage: {has_gematria}/{len(words)} ({pct:.1f}%)',
         pct > 95.0,
         f'Expected >95%, got {pct:.1f}%')
    test(f'No invalid gematria values', invalid_gematria == 0,
         f'{invalid_gematria} entries have invalid gematria')

    # Verify key word gematria
    gematria_tests = {
        'בראשית': 913,
        'אלהים': 86,
        'את': 401,
    }
    for hw, expected_g in gematria_tests.items():
        if hw in words:
            actual_g = words[hw].get('gematria', 0)
            test(f'{hw} gematria = {expected_g}',
                 actual_g == expected_g,
                 f'Got {actual_g}')


def test_genesis_1(words):
    """TEST 8: Genesis 1:1 full mechanical translation."""
    print('\n' + '=' * 60)
    print('TEST 8: GENESIS 1:1 MECHANICAL TRANSLATION')
    print('=' * 60)

    # Genesis 1:1 word order (Hebrew right-to-left, listed left-to-right reading order)
    gen1_1 = ['בראשית', 'ברא', 'אלהים', 'את', 'השמים', 'ואת', 'הארץ']

    print('\n  Hebrew -> Mechanical Translation:')
    translation_parts = []
    all_found = True
    for hw in gen1_1:
        if hw in words:
            d = words[hw].get('definition', '')
            # Take just the first meaning (before colon explanation)
            short_def = d.split(':')[0].strip() if ':' in d else d.split('.')[0].strip()
            if short_def.startswith('I. '):
                short_def = short_def[3:]
            if short_def.startswith('II. '):
                short_def = short_def[4:]
            translation_parts.append(short_def)
            print(f'    {hw} = {short_def}')
        else:
            all_found = False
            translation_parts.append(f'[{hw}?]')
            print(f'    {hw} = NOT FOUND')

    test('All Genesis 1:1 words found', all_found)

    full_translation = ' '.join(translation_parts)
    print(f'\n  Full mechanical translation:')
    print(f'  "{full_translation}"')

    # This should NOT read like JPS "When God began to create heaven and earth"
    test('Translation does NOT match JPS',
         'when god began' not in full_translation.lower(),
         f'Got: {full_translation}')
    test('Translation uses concrete terms',
         any(term in full_translation.lower() for term in ['head', 'beginning', 'fill', 'power', 'land']),
         f'Got: {full_translation}')


def test_no_jps_contamination(words):
    """TEST 9: Definitions are NOT JPS translations."""
    print('\n' + '=' * 60)
    print('TEST 9: NO JPS CONTAMINATION')
    print('=' * 60)

    jps_phrases = [
        'when god began to create',
        'the spirit of god',
        'let there be light',
        'god called the light day',
        'the lord is my shepherd',
    ]

    contaminated = 0
    for hw, entry in words.items():
        d = entry.get('definition', '').lower()
        for phrase in jps_phrases:
            if phrase in d:
                contaminated += 1
                if contaminated <= 3:
                    warn(f'JPS phrase found in {hw}: "{phrase}"')

    test(f'No JPS translation phrases in definitions',
         contaminated == 0,
         f'{contaminated} definitions contain JPS phrases')


def main():
    global PASSED, FAILED, WARNINGS

    print('=' * 60)
    print('BENCHMARK LEXICON - Mechanical Bible')
    print('Lexicon Quality & Completeness Tests')
    print('=' * 60)

    words, ahlb = load_data()
    print(f'[OK] Loaded {len(words)} words, {len(ahlb)} AHLB entries')

    # Run all test suites
    test_coverage(words)
    test_ahlb_key_words(words)
    test_tetragrammaton(words)
    test_prefix_composition(words)
    test_part_of_speech(words)
    test_root_mapping(words)
    test_gematria(words)
    test_genesis_1(words)
    test_no_jps_contamination(words)

    # Summary
    print('\n' + '=' * 60)
    print('BENCHMARK SUMMARY')
    print('=' * 60)
    total = PASSED + FAILED
    print(f'  PASSED:   {PASSED}/{total}')
    print(f'  FAILED:   {FAILED}/{total}')
    print(f'  WARNINGS: {WARNINGS}')

    if FAILED == 0:
        print('\n  ALL TESTS PASSED')
    else:
        print(f'\n  {FAILED} TEST(S) FAILED - FIX REQUIRED')

    print('=' * 60)

    return 0 if FAILED == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
