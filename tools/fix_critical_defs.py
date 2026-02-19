#!/usr/bin/env python3
"""
FIX CRITICAL DEFINITIONS - Mechanical Bible
=============================================
Corrects word definitions that were mis-indexed during AHLB parsing.
Uses Benner's actual Mechanical Translation conventions.

Also adds correct definitions for high-frequency words that had no
Strong's number (verb forms, inflections of common words).

Source: Jeff Benner, The Mechanical Translation of the Torah
        https://www.mechanical-translation.org/mtt/G1.html

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'

# === BENNER'S CORRECT DEFINITIONS ===
# These are the ACTUAL definitions from his Mechanical Translation,
# NOT the mis-indexed AHLB entries.

# Format: hebrew_word -> (correct_definition, correct_short, notes)
# correct_short is for the "mechanical" layer (1-2 words)
# correct_definition is the full Benner definition

CRITICAL_FIXES = {
    # === DIRECT OBJECT MARKER ===
    'את': {
        'definition': '[Direct object marker]: Indicator of the direct object in a sentence. Also: with, together with.',
        'mechanical': 'AT',
        'rmt': '~',  # invisible in RMT, just marks the object
        'strongs': 'H853',
        'part_of_speech': 'particle',
        'note': 'Benner: "AT" - a grammatical tool to identify the direct object. NOT "plow-point" (that is H855).',
    },
    'ואת': {
        'definition': 'And [direct object marker]',
        'mechanical': 'and~AT',
        'rmt': 'and',
        'part_of_speech': 'particle',
    },
    'אתהאור': {
        'definition': '[Object marker] the light',
        'mechanical': 'AT the~LIGHT',
        'rmt': 'the light',
    },
    'אתהרקיע': {
        'definition': '[Object marker] the sheet',
        'mechanical': 'AT the~SHEET',
        'rmt': 'the sheet',
    },
    'אתהמאור': {
        'definition': '[Object marker] the luminary',
        'mechanical': 'AT the~LUMINARY',
        'rmt': 'the luminary',
    },

    # === SKIES (not "breath/name") ===
    'שמים': {
        'definition': 'Skies: The upper region, the sky above.',
        'mechanical': 'SKY~s2',
        'rmt': 'skies',
        'strongs': 'H8064',
        'part_of_speech': 'noun',
        'note': 'Benner: "SKIES" - dual plural. NOT "heaven" (theological addition). NOT "breath/name" (that is H8034 shem).',
    },
    'השמים': {
        'definition': 'The skies: The upper region above.',
        'mechanical': 'the~SKY~s2',
        'rmt': 'the skies',
        'strongs': 'H8064_ה',
        'part_of_speech': 'noun',
    },

    # === SHAPE (verb form of bara, not "fill") ===
    'ברא': {
        'definition': 'Shape: To fatten, fill up or fashion. To shape something by filling it.',
        'mechanical': 'SHAPE(V)',
        'rmt': 'shaped',
        'strongs': 'H1254',
        'part_of_speech': 'verb',
        'note': 'Benner: "SHAPE" as verb (he~did~SHAPE). The filling of the earth with sun, moon, plants, animals. Originally meant "to fatten" (1 Samuel 2:29).',
    },

    # === WATERS (not "what") ===
    'מים': {
        'definition': 'Waters: A body of water, a flowing of water.',
        'mechanical': 'WATER~s2',
        'rmt': 'waters',
        'strongs': 'H4325',
        'part_of_speech': 'noun',
        'note': 'Benner: "WATERS" - dual plural. NOT "what" (that is H4100 mah).',
    },
    'המים': {
        'definition': 'The waters',
        'mechanical': 'the~WATER~s2',
        'rmt': 'the waters',
    },

    # === EXIST (hayah - high frequency verb) ===
    'היה': {
        'definition': 'Exist: To exist or have breath. That which exists has breath.',
        'mechanical': 'EXIST(V)',
        'rmt': 'existed',
        'strongs': 'H1961',
        'part_of_speech': 'verb',
        'note': 'Benner: "EXIST" - In Hebrew thought only that which has breath truly exists.',
    },
    'היתה': {
        'definition': 'She existed: Feminine past tense of exist.',
        'mechanical': 'she~did~EXIST(V)',
        'rmt': 'existed',
        'strongs': 'H1961',
        'part_of_speech': 'verb',
    },
    'ויהי': {
        'definition': 'And he existed: Consecutive imperfect of exist.',
        'mechanical': 'and~he~will~EXIST(V)',
        'rmt': 'and existed',
        'strongs': 'H1961',
        'part_of_speech': 'verb',
    },
    'יהי': {
        'definition': 'He will exist: Imperfect of exist.',
        'mechanical': 'he~will~EXIST(V)',
        'rmt': 'will exist',
        'strongs': 'H1961',
        'part_of_speech': 'verb',
    },
    'תהי': {
        'definition': 'She will exist',
        'mechanical': 'she~will~EXIST(V)',
        'rmt': 'will exist',
        'strongs': 'H1961',
        'part_of_speech': 'verb',
    },
    'יהיו': {
        'definition': 'They will exist',
        'mechanical': 'they~will~EXIST(V)',
        'rmt': 'will exist',
        'strongs': 'H1961',
        'part_of_speech': 'verb',
    },
    'והיו': {
        'definition': 'And they will exist',
        'mechanical': 'and~they~will~EXIST(V)',
        'rmt': 'and they existed',
        'strongs': 'H1961',
        'part_of_speech': 'verb',
    },

    # === SAY/SPEAK (amar) ===
    'ויאמר': {
        'definition': 'And he said: Consecutive imperfect of speak.',
        'mechanical': 'and~he~will~SAY(V)',
        'rmt': 'and said',
        'strongs': 'H559',
        'part_of_speech': 'verb',
    },
    'אמר': {
        'definition': 'Speak: To speak or say.',
        'mechanical': 'SAY(V)',
        'rmt': 'said',
        'strongs': 'H559',
        'part_of_speech': 'verb',
    },

    # === SEE (ra'ah) ===
    'וירא': {
        'definition': 'And he saw',
        'mechanical': 'and~he~will~SEE(V)',
        'rmt': 'and saw',
        'strongs': 'H7200',
        'part_of_speech': 'verb',
    },

    # === CALL OUT (qara) ===
    'ויקרא': {
        'definition': 'And he called out',
        'mechanical': 'and~he~will~CALL.OUT(V)',
        'rmt': 'and called out',
        'strongs': 'H7121',
        'part_of_speech': 'verb',
    },

    # === SEPARATE (badal) ===
    'ויבדל': {
        'definition': 'And he separated: To divide or make a distinction between.',
        'mechanical': 'and~he~will~SEPARATE(V)',
        'rmt': 'and separated',
        'strongs': 'H914',
        'part_of_speech': 'verb',
    },
    'מבדיל': {
        'definition': 'Making a separation',
        'mechanical': 'SEPARATE(V)~ing',
        'rmt': 'making a separation',
        'strongs': 'H914',
        'part_of_speech': 'verb',
    },
    'להבדיל': {
        'definition': 'To make a separation',
        'mechanical': 'to~SEPARATE(V)',
        'rmt': 'to make a separation',
    },

    # === MAKE (asah) ===
    'ויעש': {
        'definition': 'And he made: To do, to make, to act.',
        'mechanical': 'and~he~will~DO(V)',
        'rmt': 'and made',
        'strongs': 'H6213',
        'part_of_speech': 'verb',
    },
    'עשה': {
        'definition': 'Do: To do or make.',
        'mechanical': 'DO(V)',
        'rmt': 'made',
        'strongs': 'H6213',
        'part_of_speech': 'verb',
    },

    # === GOOD/FUNCTIONAL (tov) ===
    'טוב': {
        'definition': 'Functional: Something that functions properly, as it was intended.',
        'mechanical': 'FUNCTIONAL',
        'rmt': 'functional',
        'strongs': 'H2896',
        'part_of_speech': 'adjective',
        'note': 'Benner: "FUNCTIONAL" - not "good" in a moral sense, but functioning properly. A concrete Hebrew concept.',
    },
    'כיטוב': {
        'definition': 'That it was functional',
        'mechanical': 'GIVEN.THAT FUNCTIONAL',
        'rmt': 'that it was functional',
    },

    # === CONFUSION/WASTE (tohu) ===
    'תהו': {
        'definition': 'Confusion: A barren wasteland. A place of emptiness and disorder.',
        'mechanical': 'CONFUSION',
        'rmt': 'confusion',
        'strongs': 'H8414',
        'part_of_speech': 'noun',
    },

    # === EMPTY (bohu) ===
    'ובהו': {
        'definition': 'And unfilled: Empty, void.',
        'mechanical': 'and~UNFILLED',
        'rmt': 'and unfilled',
        'strongs': 'H922',
        'part_of_speech': 'noun',
    },

    # === DARKNESS ===
    'חשך': {
        'definition': 'Darkness: An absence of light.',
        'mechanical': 'DARKNESS',
        'rmt': 'darkness',
        'strongs': 'H2822',
        'part_of_speech': 'noun',
    },
    'ולחשך': {
        'definition': 'And to the darkness',
        'mechanical': 'and~to~the~DARKNESS',
        'rmt': 'and to the darkness',
    },

    # === FACE/PRESENCE ===
    'פני': {
        'definition': 'Face: The face or front, the presence of someone.',
        'mechanical': 'FACE~s',
        'rmt': 'face of',
        'strongs': 'H6440',
        'part_of_speech': 'noun',
    },
    'עלפני': {
        'definition': 'Upon the face of',
        'mechanical': 'UPON FACE~s',
        'rmt': 'upon the face of',
    },

    # === DEEP WATER ===
    'תהום': {
        'definition': 'Deep water: A great deep, the primordial deep.',
        'mechanical': 'DEEP.WATER',
        'rmt': 'the deep water',
        'strongs': 'H8415',
        'part_of_speech': 'noun',
    },

    # === WIND/BREATH ===
    'רוח': {
        'definition': 'Wind: The wind, also the breath or spirit of a man or god.',
        'mechanical': 'WIND',
        'rmt': 'wind',
        'strongs': 'H7307',
        'part_of_speech': 'noun',
    },

    # === FLUTTER (rachaph) ===
    'מרחפת': {
        'definition': 'Fluttering: A gentle hovering or trembling motion.',
        'mechanical': 'much~FLUTTER(V)~ing(fs)',
        'rmt': 'was fluttering',
        'strongs': 'H7363',
        'part_of_speech': 'verb',
    },

    # === LIGHT ===
    'אור': {
        'definition': 'Light: The light from the sun, moon, stars, fire or other source.',
        'mechanical': 'LIGHT',
        'rmt': 'light',
        'strongs': 'H216',
        'part_of_speech': 'noun',
    },

    # === DAY ===
    'יום': {
        'definition': 'Day: A day unit, from sunset to sunset.',
        'mechanical': 'DAY',
        'rmt': 'day',
        'strongs': 'H3117',
        'part_of_speech': 'noun',
    },

    # === NIGHT ===
    'לילה': {
        'definition': 'Night: The period of darkness.',
        'mechanical': 'NIGHT',
        'rmt': 'night',
        'strongs': 'H3915',
        'part_of_speech': 'noun',
    },

    # === SHEET/FIRMAMENT (raqia) ===
    'רקיע': {
        'definition': 'Sheet: A hammered out sheet of metal. The expanse of sky.',
        'mechanical': 'SHEET',
        'rmt': 'sheet',
        'strongs': 'H7549',
        'part_of_speech': 'noun',
        'note': 'Benner: "SHEET" - as hammered out flat. NOT "firmament" (Latin theological addition).',
    },
    'לרקיע': {
        'definition': 'To/for the sheet',
        'mechanical': 'to~SHEET',
        'rmt': 'for the sheet',
    },
    'ברקיע': {
        'definition': 'In the sheet',
        'mechanical': 'in~SHEET',
        'rmt': 'in the sheet',
    },

    # === EVENING ===
    'ערב': {
        'definition': 'Evening: The time of sunset and mixture of light and dark.',
        'mechanical': 'EVENING',
        'rmt': 'evening',
        'strongs': 'H6153',
        'part_of_speech': 'noun',
    },

    # === MORNING ===
    'בקר': {
        'definition': 'Morning: The breaking of daylight.',
        'mechanical': 'MORNING',
        'rmt': 'morning',
        'strongs': 'H1242',
        'part_of_speech': 'noun',
    },

    # === BEGINNING/SUMMIT ===
    'בראשית': {
        'definition': 'In the summit: At the head/beginning of time or events. The top, the first.',
        'mechanical': 'in~SUMMIT',
        'rmt': 'In the summit',
        'strongs': 'H7225',
        'part_of_speech': 'noun',
        'note': 'Benner: "in~SUMMIT" - resh=head, summit is the head of a mountain. Head of time = beginning.',
    },

    # === EARTH/LAND ===
    'הארץ': {
        'definition': 'The land: The ground, a region, territory.',
        'mechanical': 'the~LAND',
        'rmt': 'the land',
        'strongs': 'H776_ה',
        'part_of_speech': 'noun',
    },
    'והארץ': {
        'definition': 'And the land',
        'mechanical': 'and~the~LAND',
        'rmt': 'and the land',
    },

    # === BECAUSE/GIVEN THAT ===
    'כי': {
        'definition': 'Given that: Because, for, when, that.',
        'mechanical': 'GIVEN.THAT',
        'rmt': 'given that',
        'strongs': 'H3588',
        'part_of_speech': 'conjunction',
    },

    # === BETWEEN ===
    'בין': {
        'definition': 'Between: The interval or space separating two things.',
        'mechanical': 'BETWEEN',
        'rmt': 'between',
        'strongs': 'H996',
        'part_of_speech': 'preposition',
    },

    # === ONE ===
    'אחד': {
        'definition': 'Unit: A singular unit, one.',
        'mechanical': 'UNIT',
        'rmt': 'one',
        'strongs': 'H259',
        'part_of_speech': 'adjective',
    },

    # === SECOND ===
    'שני': {
        'definition': 'Second: The ordinal number two.',
        'mechanical': 'SECOND',
        'rmt': 'second',
        'strongs': 'H8145',
        'part_of_speech': 'adjective',
    },

    # === DRY GROUND ===
    'יבשה': {
        'definition': 'Dry ground: Ground that is dry, not covered by water.',
        'mechanical': 'DRY.GROUND',
        'rmt': 'dry ground',
        'strongs': 'H3004',
        'part_of_speech': 'noun',
    },

    # === GRASS ===
    'דשא': {
        'definition': 'Grass: Tender grass or herbs.',
        'mechanical': 'GRASS',
        'rmt': 'grass',
        'strongs': 'H1877',
        'part_of_speech': 'noun',
    },

    # === SEED ===
    'זרע': {
        'definition': 'Seed: The seed of plants. Also offspring, descendants.',
        'mechanical': 'SEED',
        'rmt': 'seed',
        'strongs': 'H2233',
        'part_of_speech': 'noun',
    },

    # === TREE ===
    'עץ': {
        'definition': 'Tree: A woody plant.',
        'mechanical': 'TREE',
        'rmt': 'tree',
        'strongs': 'H6086',
        'part_of_speech': 'noun',
    },

    # === PRODUCE/FRUIT ===
    'פרי': {
        'definition': 'Produce: The fruit or product of a plant or tree.',
        'mechanical': 'PRODUCE',
        'rmt': 'produce',
        'strongs': 'H6529',
        'part_of_speech': 'noun',
    },

    # === LUMINARY ===
    'מאור': {
        'definition': 'Luminary: A light-giver, a celestial body that gives light.',
        'mechanical': 'LUMINARY',
        'rmt': 'luminary',
        'strongs': 'H3974',
        'part_of_speech': 'noun',
    },

    # === STAR ===
    'כוכבים': {
        'definition': 'Stars: The stars of the sky.',
        'mechanical': 'STAR~s',
        'rmt': 'stars',
        'strongs': 'H3556',
        'part_of_speech': 'noun',
    },

    # === LIVING (chai) ===
    'חיה': {
        'definition': 'Living: Alive, having the breath of life.',
        'mechanical': 'LIVING',
        'rmt': 'living',
        'strongs': 'H2416',
        'part_of_speech': 'adjective',
    },

    # === SOUL/BEING ===
    'נפש': {
        'definition': 'Being: A breathing creature, the whole self, the appetite.',
        'mechanical': 'BEING',
        'rmt': 'being',
        'strongs': 'H5315',
        'part_of_speech': 'noun',
        'note': 'Benner: "BEING" - a breathing creature. The concrete meaning is the throat/neck (where breath passes).',
    },

    # === KIND/SPECIES ===
    'למינו': {
        'definition': 'To his kind: According to its species.',
        'mechanical': 'to~KIND~him',
        'rmt': 'to his kind',
    },
    'למינה': {
        'definition': 'To her kind',
        'mechanical': 'to~KIND~her',
        'rmt': 'to her kind',
    },
    'למינהם': {
        'definition': 'To their kind',
        'mechanical': 'to~KIND~them',
        'rmt': 'to their kind',
    },
}


def apply_fixes(words):
    """Apply critical definition fixes to words.json."""
    fixed = 0
    not_found = 0

    for hebrew, fix_data in CRITICAL_FIXES.items():
        if hebrew in words:
            entry = words[hebrew]

            # Save old definition for reference
            old_def = entry.get('definition', '')
            if old_def and 'strongs_definition' not in entry:
                entry['strongs_definition'] = old_def

            # Apply the fix
            entry['definition'] = fix_data['definition']

            if 'mechanical' in fix_data:
                entry['mechanical_translation'] = fix_data['mechanical']
            if 'rmt' in fix_data:
                entry['rmt_translation'] = fix_data['rmt']
            if 'strongs' in fix_data:
                entry['strongs'] = fix_data['strongs']
            if 'part_of_speech' in fix_data:
                entry['part_of_speech'] = fix_data['part_of_speech']
            if 'note' in fix_data:
                entry['benner_note'] = fix_data['note']

            fixed += 1
        else:
            not_found += 1
            # Only warn for important missing words, not compound forms
            if len(hebrew) <= 4:
                print(f'  [WARN] {hebrew} not found in words.json')

    return fixed, not_found


def propagate_to_compounds(words):
    """For words that have mechanical/rmt translations, propagate to prefix compounds."""
    # Build lookup of base words with mechanical translations
    base_lookup = {}
    for hw, entry in words.items():
        if 'mechanical_translation' in entry:
            base_lookup[hw] = entry

    propagated = 0
    for hw, entry in words.items():
        if 'mechanical_translation' in entry:
            continue  # Already has one

        # Try to find the base word by stripping prefixes
        for prefix_len in range(1, min(3, len(hw))):
            prefix = hw[:prefix_len]
            root = hw[prefix_len:]
            if root in base_lookup:
                root_entry = base_lookup[root]
                root_mech = root_entry['mechanical_translation']
                root_rmt = root_entry.get('rmt_translation', '')

                prefix_map = {
                    'ו': ('and~', 'and'),
                    'וה': ('and~the~', 'and the'),
                    'ב': ('in~', 'in'),
                    'בה': ('in~the~', 'in the'),
                    'ל': ('to~', 'to'),
                    'לה': ('to~the~', 'to the'),
                    'כ': ('like~', 'like'),
                    'מ': ('from~', 'from'),
                    'ה': ('the~', 'the'),
                }

                if prefix in prefix_map:
                    mech_prefix, rmt_prefix = prefix_map[prefix]
                    entry['mechanical_translation'] = f'{mech_prefix}{root_mech}'
                    entry['rmt_translation'] = f'{rmt_prefix} {root_rmt}'.strip()
                    propagated += 1
                    break

    return propagated


def main():
    print('=' * 60)
    print('FIX CRITICAL DEFINITIONS - Mechanical Bible')
    print('Correcting mis-indexed AHLB entries')
    print('=' * 60)

    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'[OK] Loaded {len(words)} words')

    fixed, not_found = apply_fixes(words)
    print(f'[OK] Fixed {fixed} critical definitions')
    print(f'[INFO] {not_found} compound forms not in lexicon (expected)')

    propagated = propagate_to_compounds(words)
    print(f'[OK] Propagated mechanical translations to {propagated} compound forms')

    # Verify Genesis 1:1
    print('\n=== GENESIS 1:1 VERIFICATION ===')
    gen1 = ['בראשית', 'ברא', 'אלהים', 'את', 'השמים', 'ואת', 'הארץ']
    mech_parts = []
    rmt_parts = []
    for hw in gen1:
        if hw in words:
            m = words[hw].get('mechanical_translation', '?')
            r = words[hw].get('rmt_translation', words[hw].get('definition','')[:20])
            mech_parts.append(m)
            if r != '~':  # Skip invisible AT marker
                rmt_parts.append(r)
            print(f'  {hw:>10}: mechanical={m:25s} rmt={r}')

    print(f'\n  Mechanical: {" ".join(mech_parts)}')
    print(f'  RMT:        {" ".join(rmt_parts)}')

    # Save
    with open(WORDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)
    print(f'\n[SAVED] {WORDS_JSON} ({WORDS_JSON.stat().st_size:,} bytes)')

    print('\n' + '=' * 60)
    print('[DONE] Critical definitions fixed')
    print('=' * 60)


if __name__ == '__main__':
    main()
