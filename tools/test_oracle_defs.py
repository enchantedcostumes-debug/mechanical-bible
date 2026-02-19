#!/usr/bin/env python3
"""
Test oracle definitions against known-correct Benner mechanical translations.
These are hand-verified from the MECHANICAL spans already baked in the HTML.
The test MUST pass before any push.
"""
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).parent.parent
WORDS_JSON = BASE / 'words.json'

def shorten_def(definition):
    """Same function used by prebake_oracle.py"""
    if not definition:
        return '?'
    if ':' in definition:
        short = definition.split(':')[0].strip()
        if short:
            short = re.sub(r'^\[(.+)\]$', r'\1', short)
            return short
    d = re.sub(r'\s*\(.*?\)', '', definition)
    parts = re.split(r'[;,.]', d)
    return parts[0].strip() or '?'

# Known-correct word -> expected oracle short definition
# Sourced from Benner's AHLB and verified against MECHANICAL translations
EXPECTED = {
    # Genesis 1:1 words
    'בראשית': 'Beginning',
    'ברא': 'Fill',
    'אלהים': 'Power',
    'את': 'Direct object marker',
    'השמים': 'Skies',
    'הארץ': 'Land',

    # Common verbs
    'ויאמר': 'Say',
    'ויאמרו': 'Say',
    'ויהי': 'Exist',
    'ויעש': 'Do',
    'וירא': 'See',
    'ויבא': 'Come',
    'ויקרא': 'Call',
    'וידבר': 'Speak',

    # Common particles/prepositions
    'לא': 'Not',
    'כי': 'Because',
    'אשר': 'Which',
    'גם': 'Also',
    'נא': 'Please',
    'עוד': 'Again',

    # Common nouns
    'יום': 'Day',
    'ארץ': 'Land',
    'שמים': 'Skies',
    'מים': 'Water',
    'אור': 'Light',
    'איש': 'Man',
    'בן': 'Son',
    'בת': 'Daughter',
    'אב': 'Father',
    'אם': 'Mother',
    'אח': 'Brother',
    'בית': 'House',
    'עיר': 'City',
    'יד': 'Hand',
    'עין': 'Eye',
    'פה': 'Mouth',
    'לב': 'Heart',
    'נפש': 'Soul',
    'דרך': 'Road',
    'דבר': 'Word',
    'שם': 'Breath',

    # Names - should be the name, not a definition
    'משה': 'Moses - drawing out',
    'יהוה': 'YHWH',
    'ישראל': 'He will rule as God',
    'פרעה': 'Pharaoh',

    # Exodus 5 key words
    'שלח': 'Send',
    'במדבר': 'Wilderness',
    'העברים': 'Hebrew',

    # Must NOT be these wrong values
    # אשר must NOT be 'Happy' (that's H835, not H834)
    # לא must NOT be 'If'
    # נא must NOT be 'Raw'
    # את must NOT be 'Plow-point'
    # פרעה must NOT be 'in'
    # ימים must NOT be 'Seas' (should be 'Day' - plural of יום)
    # במדבר must NOT be 'Speak' or 'In Speak'
}

MUST_NOT_BE = {
    'אשר': ['Happy'],
    'לא': ['If'],
    'נא': ['Raw'],
    'את': ['Plow-point', 'Plow point'],
    'פרעה': ['in', 'In'],
    'במדבר': ['Speak', 'In Speak'],
    'ידעתי': ['Judites'],
    'אלהי': ['these of', 'These of'],
}


def main():
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)

    passed = 0
    failed = 0
    errors = []

    # Test expected values
    for hebrew, expected in EXPECTED.items():
        entry = words.get(hebrew, {})
        definition = entry.get('definition', '')
        short = shorten_def(definition)

        if short == expected:
            passed += 1
        else:
            failed += 1
            errors.append(f'  FAIL: {hebrew} expected "{expected}" got "{short}" (full: {definition[:80]})')

    # Test must-not-be values
    for hebrew, bad_values in MUST_NOT_BE.items():
        entry = words.get(hebrew, {})
        definition = entry.get('definition', '')
        short = shorten_def(definition)

        for bad in bad_values:
            if short == bad:
                failed += 1
                errors.append(f'  FAIL: {hebrew} must NOT be "{bad}" but it is! (full: {definition[:80]})')
                break
        else:
            passed += 1

    total = passed + failed
    print(f'Oracle Definition Tests: {passed}/{total} passed')
    if errors:
        print()
        for e in errors:
            print(e)
        print(f'\n{failed} FAILURES')
        sys.exit(1)
    else:
        print('ALL TESTS PASSED')
        sys.exit(0)


if __name__ == '__main__':
    main()
