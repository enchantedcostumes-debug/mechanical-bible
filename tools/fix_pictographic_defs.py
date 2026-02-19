#!/usr/bin/env python3
"""
FIX DEFINITIONS + POPULATE STRONG'S — Mechanical Bible
========================================================
1. Parse OSHB (Open Scriptures Hebrew Bible) XML files to get
   Hebrew word → Strong's number mappings
2. Map Strong's → AHLB definitions
3. Update words.json with:
   - Strong's numbers for all words that can be mapped
   - Real AHLB definitions replacing all garbage
4. Morphological decomposition as fallback

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
import unicodedata
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'
AHLB_STRONGS = BASE_DIR / 'data' / 'ahlb_by_strongs.json'
AHLB_COMPLETE = BASE_DIR / 'data' / 'ahlb_complete.json'
HEBREW_DEFS = BASE_DIR / 'data' / 'hebrew_definitions.json'
LEXICON_STRONGS = BASE_DIR / 'data' / 'lexicon' / 'lexicon_by_strongs.json'
OSHB_DIR = Path(r'C:\Users\Tammy Casey\Documents\AI PROJECTS\PEER\morphhb-master\wlc')
BIBLE_NAMES = BASE_DIR / 'data' / 'bible_names.json'


def is_good_definition(d):
    """Return True if this definition is genuine, not garbage."""
    if not d or d == '?' or d == '[Pictographic]':
        return False
    if 'From pictograph' in d or 'From the pictograph' in d:
        return False
    if 'parent root' in d or 'Hebrew root' in d:
        return False
    # Letter-meaning concatenation garbage
    if re.search(r'[A-Z][a-z]+, [a-z]+(?:, [a-z]+)? [A-Z][a-z]+, [a-z]+', d):
        return False
    if re.search(r'^(?:To |And |The |From |In )?[A-Z][a-z]+, [a-z]', d):
        return False
    return True


def shorten_def(definition):
    """Extract short label."""
    if not definition:
        return '?'
    if ':' in definition:
        short = definition.split(':')[0].strip()
        short = re.sub(r'^\[(.+)\]$', r'\1', short)
        if short:
            return short
    d = re.sub(r'\s*\(.*?\)', '', definition)
    parts = re.split(r'[;,.]', d)
    return parts[0].strip() or '?'


def parse_oshb():
    """Parse OSHB XML files to build Hebrew→Strong's mapping."""
    print('Parsing OSHB XML files...')
    hebrew_to_strongs = {}
    total = 0

    for fname in sorted(os.listdir(OSHB_DIR)):
        if not fname.endswith('.xml') or fname == 'VerseMap.xml':
            continue
        fpath = OSHB_DIR / fname
        try:
            tree = ET.parse(fpath)
            root = tree.getroot()
        except Exception:
            continue

        ns = 'http://www.bibletechnologies.net/2003/OSIS/namespace'
        for w in root.iter(f'{{{ns}}}w'):
            lemma = w.get('lemma', '')
            text = w.text or ''

            # Clean: remove cantillation/vowel marks
            clean = ''.join(c for c in text
                           if unicodedata.category(c) not in ('Mn', 'Cf'))
            clean_full = clean.replace('/', '')

            if not lemma or not clean_full:
                continue

            # Extract Strong's numbers
            nums = re.findall(r'\b(\d+)\b', lemma)
            for num in nums:
                snum = f'H{num}'
                # Store full form
                if clean_full not in hebrew_to_strongs:
                    hebrew_to_strongs[clean_full] = snum

                # Store root (after prefix slash)
                parts = clean.split('/')
                if len(parts) > 1:
                    root_word = parts[-1]
                    if root_word not in hebrew_to_strongs:
                        hebrew_to_strongs[root_word] = snum

            total += 1

    print(f'  Parsed {total} word tokens')
    print(f'  Hebrew→Strong\'s mappings: {len(hebrew_to_strongs)}')
    return hebrew_to_strongs


def main():
    print('=' * 60)
    print('FIX DEFINITIONS + POPULATE STRONG\'S')
    print('=' * 60)

    # ─── Load data ───
    print('\nLoading data...')
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'  words.json: {len(words)} entries')

    with open(AHLB_STRONGS, 'r', encoding='utf-8') as f:
        ahlb_strongs = json.load(f)
    print(f'  ahlb_by_strongs.json: {len(ahlb_strongs)} entries')

    with open(HEBREW_DEFS, 'r', encoding='utf-8') as f:
        hebrew_defs = json.load(f)

    with open(LEXICON_STRONGS, 'r', encoding='utf-8') as f:
        lexicon = json.load(f)

    # Load biblical names
    with open(BIBLE_NAMES, 'r', encoding='utf-8') as f:
        names_data = json.load(f)
    bible_names = names_data.get('names', [])
    print(f'  bible_names.json: {len(bible_names)} names')

    # Build Hebrew → name definition lookup (names take priority!)
    name_defs = {}
    for n in bible_names:
        heb = n.get('hebrew', '')
        eng = n.get('english', '')
        defn = n.get('definition', '')
        if heb:
            if defn:
                name_defs[heb] = f'{eng}: {defn}'
            elif eng:
                name_defs[heb] = f'{eng}: A proper name.'
    print(f'  Name definitions: {len(name_defs)}')

    # ─── Phase 1: Parse OSHB for Strong's mappings ───
    heb_to_strongs = parse_oshb()

    # ─── Phase 2: Build AHLB definition lookup ───
    print('\n── Phase 2: Building AHLB definition lookup ──')

    # AHLB Strong's → definition
    strongs_defs = {}
    for snum, entry in ahlb_strongs.items():
        if isinstance(entry, dict):
            d = entry.get('definition', '')
        else:
            d = str(entry)
        if d:
            strongs_defs[snum] = d

    # Also add from lexicon
    for snum, entry in lexicon.items():
        base = snum.split('_')[0]
        if base not in strongs_defs:
            d = entry.get('definition', '')
            if d:
                strongs_defs[base] = d

    print(f'  Strong\'s definitions: {len(strongs_defs)}')

    # Build Hebrew → AHLB definition via Strong's
    ahlb_defs = {}
    for heb, snum in heb_to_strongs.items():
        if snum in strongs_defs:
            ahlb_defs[heb] = strongs_defs[snum]

    print(f'  Hebrew words with AHLB defs: {len(ahlb_defs)}')

    # ─── Phase 3: Build good definition pool ───
    print('\n── Phase 3: Building definition pool ──')

    good_pool = {}

    # Add genuinely good existing definitions
    for hw, entry in words.items():
        d = entry.get('definition', '')
        if is_good_definition(d):
            good_pool[hw] = d

    # Add from hebrew_definitions.json
    for hw, entry in hebrew_defs.items():
        d = entry.get('definition', '')
        if d and hw not in good_pool:
            good_pool[hw] = d

    # Add AHLB definitions (these are the new ones!)
    for hw, d in ahlb_defs.items():
        if hw not in good_pool:
            good_pool[hw] = d

    # Add biblical name definitions — these OVERRIDE everything else
    # because names should show their meaning, not generic AHLB verb defs
    for hw, d in name_defs.items():
        good_pool[hw] = d  # Override even existing AHLB defs for names

    # Override common words that AHLB maps to wrong Strong's,
    # or that got corrupted by name overrides in previous runs
    OVERRIDES = {
        # Fix words corrupted by name overrides (verb roots that share Hebrew with names)
        'ברא': 'Shape: To create by filling and fashioning.',
        'רדה': 'Rule: To have dominion, to tread down.',
        'אדם': 'Man: Humanity, mankind. From the red earth.',
        'שרה': 'Princess: A noble woman. Also: to struggle.',
        'נח': 'Rest: Comfort, to settle.',
        'גד': 'Fortune: A troop, good fortune.',
        'דן': 'Judge: To judge, to govern.',
        'חם': 'Hot: Warm, dark. Father-in-law.',
        # Grammar particles with wrong AHLB mappings
        'אשר': 'Which: A relative particle — who, which, what, that.',
        'אל': 'To: Toward, unto. Also: God, power.',
        'לא': 'Not: A negative particle.',
        'את': '[Direct object marker]: Indicator of the direct object. Also: with.',
        'כי': 'Given that: Because, for, when, that.',
        'גם': 'Also: Even, moreover.',
        'כן': 'So: Thus, in this manner.',
        'פן': 'Lest: For fear that.',
        'אם': 'If: A conditional particle.',
        'עד': 'Until: Up to, as far as.',
        'מן': 'From: Out of, away from, more than.',
        'אך': 'Only: Surely, but, however.',
        'הנה': 'Behold: Look, see, here.',
        'נא': 'Please: A particle of entreaty.',
        'אף': 'Also: Even, indeed. Nose when plural.',
        'לו': 'To him: Or: if only, would that.',
        'בו': 'In him: In it.',
        'לי': 'To me: For me.',
        'לך': 'To you: For you. Also: Walk, go.',
        'בי': 'In me: Please, I pray.',
        'אליו': 'To him: Unto him.',
        'אלי': 'To me: Unto me.',
        'עליו': 'Upon him: Over him, concerning him.',
        'אליהם': 'To them: Unto them.',
        'עליהם': 'Upon them: Over them.',
        'להם': 'To them: For them.',
        'לכם': 'To you: For you (plural).',
        'בהם': 'In them: Among them.',
        'מהם': 'From them: Of them.',
        'אתם': 'You: Second person plural. Also: them (with object marker).',
        'לפני': 'Before: In the presence of, in front of.',
        'אחרי': 'After: Behind, following.',
        'ביום': 'In the day: On the day.',
        'בני': 'Sons of: Children of.',
        'אבי': 'Father of: My father.',
        'אביך': 'Your father: Father of you.',
        'אביו': 'His father: Father of him.',
        'אמו': 'His mother: Mother of him.',
        'בית': 'House: A household, temple, family.',
        'כל': 'All: The whole, every, each.',
        'ויהי': 'And it was: And it came to pass.',
        'ויאמר': 'And he said: And he spoke.',
        'לאמר': 'Saying: To say.',
        'אני': 'I: First person singular.',
        'אנכי': 'I: First person singular (emphatic).',
        'אתה': 'You: Second person masculine singular.',
        'היא': 'She: Third person feminine singular.',
        'הוא': 'He: Third person masculine singular.',
        'זה': 'This: Demonstrative pronoun.',
        'הזה': 'This: The one being pointed to.',
        'אדני': 'My lord: Master.',
    }
    for hw, d in OVERRIDES.items():
        good_pool[hw] = d

    print(f'  Good definition pool: {len(good_pool)}')

    # ─── Phase 4: Populate Strong's numbers ───
    print('\n── Phase 4: Populating Strong\'s numbers ──')
    strongs_added = 0
    for hw, entry in words.items():
        existing_strongs = entry.get('strongs', '')
        if not existing_strongs and hw in heb_to_strongs:
            words[hw]['strongs'] = heb_to_strongs[hw]
            strongs_added += 1

    print(f'  Strong\'s numbers added: {strongs_added}')
    total_strongs = sum(1 for v in words.values() if v.get('strongs'))
    print(f'  Total words with Strong\'s: {total_strongs}')

    # ─── Phase 5: Fix definitions ───
    print('\n── Phase 5: Fixing definitions ──')

    # First reset all garbage definitions
    needs_fix = 0
    for hw, entry in words.items():
        d = entry.get('definition', '')
        if not is_good_definition(d):
            needs_fix += 1

    print(f'  Words needing definitions: {needs_fix}')

    # Prefixes for morphological decomposition
    PREFIXES = [
        ('ובה', 'and in the'), ('ולה', 'and to the'),
        ('ומה', 'and from the'), ('וכה', 'and as the'),
        ('וב', 'and in'), ('וה', 'and the'), ('וכ', 'and as'),
        ('ול', 'and to'), ('ומ', 'and from'), ('וש', 'and which'),
        ('בה', 'in the'), ('כה', 'as the'), ('לה', 'to the'),
        ('מה', 'from the'), ('שה', 'which the'),
        ('ו', 'and'), ('ה', 'the'), ('ב', 'in'), ('כ', 'as'),
        ('ל', 'to'), ('מ', 'from'), ('ש', 'which'),
    ]

    SUFFIXES = [
        ('ותיהם', ''), ('ותיהן', ''), ('ותינו', ''),
        ('יהם', ''), ('יהן', ''), ('ותם', ''), ('ותי', ''),
        ('ינו', ''), ('תיך', ''), ('ותיו', ''),
        ('יכם', ''), ('כם', ''), ('הם', ''), ('הן', ''),
        ('נו', ''), ('ות', ''), ('ים', ''), ('ין', ''),
        ('תי', ''), ('יו', ''), ('יה', ''), ('יך', ''),
        ('ני', ''), ('תו', ''), ('תם', ''), ('הו', ''),
        ('ך', ''), ('ם', ''), ('ן', ''), ('ה', ''), ('י', ''),
    ]

    def find_definition(hw):
        """Try to find a definition for a Hebrew word."""
        # Direct pool match
        if hw in good_pool:
            return good_pool[hw], 'direct'

        # Try Strong's → AHLB directly
        snum = words[hw].get('strongs', '') or heb_to_strongs.get(hw, '')
        if snum:
            base_s = snum.split('_')[0]
            if base_s in strongs_defs:
                return strongs_defs[base_s], 'strongs'

        candidates = []

        # Morphological decomposition
        for pfx, pfx_m in [('', '')] + PREFIXES:
            if pfx and not hw.startswith(pfx):
                continue
            if pfx and len(hw) <= len(pfx):
                continue

            rest = hw[len(pfx):] if pfx else hw

            for sfx, sfx_m in [('', '')] + SUFFIXES:
                if sfx and not rest.endswith(sfx):
                    continue
                if sfx and len(rest) <= len(sfx) + 1:
                    continue

                bare = rest[:-len(sfx)] if sfx else rest
                if not bare or (not pfx and not sfx):
                    continue  # Skip no-strip case (already checked direct)

                # Check in good_pool
                if bare in good_pool:
                    candidates.append((bare, pfx_m, good_pool[bare], len(bare)))
                    continue

                # Try restore common endings
                for restore in ['ה', 'י', 'ת', 'א', 'ו']:
                    candidate = bare + restore
                    if candidate in good_pool:
                        candidates.append((candidate, pfx_m, good_pool[candidate], len(candidate)))
                        break

        if candidates:
            # Pick longest bare root (most specific)
            candidates.sort(key=lambda x: -x[3])
            best = candidates[0]
            bare_word, prefix_meaning, definition, _ = best
            short = shorten_def(definition)
            if prefix_meaning:
                new_def = f'{prefix_meaning.capitalize()} {short.lower()}'
            else:
                new_def = definition
            method = 'morph_prefix' if prefix_meaning else 'morph_suffix'
            return new_def, method

        # Compound word splitting: try splitting into 2 known sub-words
        for i in range(1, len(hw)):
            left = hw[:i]
            right = hw[i:]
            if left in good_pool and right in good_pool:
                left_short = shorten_def(good_pool[left])
                right_short = shorten_def(good_pool[right])
                return f'{left_short} + {right_short}', 'compound'

        # Proper nouns: use transliteration as definition
        entry = words.get(hw, {})
        translit = entry.get('transliteration', '')
        if translit and len(translit) > 1:
            # Capitalize as proper noun
            return f'{translit.title()}: A proper name.', 'proper_noun'

        return None, 'unresolved'

    # Apply fixes
    stats = defaultdict(int)
    for hw, entry in words.items():
        # Grammar overrides ALWAYS apply (these fix AHLB Strong's ambiguity)
        if hw in OVERRIDES:
            words[hw]['definition'] = OVERRIDES[hw]
            stats['grammar_override'] += 1
            continue

        d = entry.get('definition', '')
        if is_good_definition(d):
            stats['already_good'] += 1
            continue

        # Name definitions: only apply if no good definition exists
        if hw in name_defs:
            words[hw]['definition'] = name_defs[hw]
            stats['name_def'] += 1
            continue

        defn, method = find_definition(hw)
        if defn:
            words[hw]['definition'] = defn
            stats[method] += 1
        else:
            words[hw]['definition'] = '?'
            stats['unresolved'] += 1

    # ─── Report ───
    print('\n── Results ──')
    for method, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'    {method}: {count}')

    good_count = sum(1 for v in words.values()
                     if v.get('definition', '') and v['definition'] != '?')
    unknown_count = sum(1 for v in words.values()
                        if v.get('definition', '') == '?' or not v.get('definition', ''))
    print(f'\n  Final: {good_count} defined ({good_count/len(words)*100:.1f}%), {unknown_count} unknown')

    # Verify key words
    print('\n── Verification ──')
    test_words = [
        ('בראשית', 'In the summit'),
        ('ברא', 'Shape'),
        ('אלהים', 'Power'),
        ('הים', 'the + sea'),
        ('ורדו', 'and + rule'),
        ('מלאכתו', 'work'),
        ('השביעי', 'the + seven'),
        ('תולדות', 'bear/generations'),
        ('הכוכבים', 'the stars'),
        ('עשות', 'do'),
        ('מים', 'Waters'),
        ('ים', 'Sea'),
        ('רדה', 'rule'),
        ('מלאכה', 'work'),
        ('שבע', 'seven/swear'),
    ]
    for hw, expected in test_words:
        d = words.get(hw, {}).get('definition', '?')
        short = shorten_def(d) if d != '?' else '?'
        s = words.get(hw, {}).get('strongs', '')
        print(f'  {hw}: "{short}" strongs={s} (expected ~{expected})')

    # ─── Save ───
    print('\nSaving words.json...')
    with open(WORDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print('Done!')


if __name__ == '__main__':
    main()
