#!/usr/bin/env python3
"""
PARSE AHLB COMPLETE - Mechanical Bible
========================================
Parses the FULL Ancient Hebrew Lexicon of the Bible (Jeff Benner) text file
into structured JSON data.

Input:  ahlb.txt (1.44 MB, 29,480 lines, ~1,526 roots, ~5,049 words)
Output: data/ahlb_complete.json - Full structured AHLB data
        data/ahlb_by_strongs.json - Indexed by Strong's number
        data/ahlb_roots.json - Root hierarchy (parent -> child -> adopted)

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re
import json
from pathlib import Path
from collections import defaultdict

# Paths
BASE_DIR = Path(__file__).parent.parent
AHLB_PATHS = [
    Path(r"C:\Users\Tammy Casey\Documents\AI PROJECTS\1 Website\EXTRACTED_FILES\raw_data\docs\ahlb.txt"),
    Path(r"C:\Users\Tammy Casey\Documents\AI PROJECTS\OLD STUFF\Rosetta Stone AHLB Gematria Analysis\ahlb.txt"),
    Path(r"G:\My Drive\PATREON\ARTICLES SERMONS\Evolution of Hebrew\ahlb.txt"),
]
OUTPUT_DIR = BASE_DIR / "data"


def find_ahlb_file():
    """Find the AHLB text file."""
    for p in AHLB_PATHS:
        if p.exists():
            print(f'[OK] Found AHLB at: {p}')
            return p
    print('[ERROR] Could not find ahlb.txt in any known location')
    return None


def parse_strongs(text):
    """Extract Strong's numbers from {str: NNNN} format."""
    match = re.search(r'\{str:\s*([\d,\s]+)\}', text)
    if not match:
        return []
    nums = [f'H{n.strip()}' for n in match.group(1).split(',') if n.strip()]
    return nums


def parse_frequency(text):
    """Extract frequency from [freq. N] format."""
    match = re.search(r'\[freq\.\s*(\d+)\]', text)
    return int(match.group(1)) if match else 0


def parse_kjv(text):
    """Extract KJV translations from |kjv: ...| format."""
    match = re.search(r'\|kjv:\s*([^|]+)\|', text)
    if not match:
        return []
    return [t.strip() for t in match.group(1).split(',') if t.strip()]


def parse_verb_forms(text):
    """Extract verb forms from (vf: ...) format."""
    match = re.search(r'\(vf:\s*([^)]+)\)', text)
    if not match:
        return []
    return [f.strip() for f in match.group(1).split(',') if f.strip()]


def parse_definition(text):
    """Extract the definition text — everything after the dash before metadata."""
    # Remove metadata markers
    cleaned = text
    # Remove [freq...], |kjv...|, {str...}, (vf...), [ms:...], [df:...], [ar:...]
    cleaned = re.sub(r'\[freq\.\s*\d+\]', '', cleaned)
    cleaned = re.sub(r'\|kjv:[^|]*\|', '', cleaned)
    cleaned = re.sub(r'\{str:[^}]*\}', '', cleaned)
    cleaned = re.sub(r'\(vf:[^)]*\)', '', cleaned)
    cleaned = re.sub(r'\[ms:[^\]]*\]', '', cleaned)
    cleaned = re.sub(r'\[df:[^\]]*\]', '', cleaned)
    cleaned = re.sub(r'\[ar:[^\]]*\]', '', cleaned)
    cleaned = re.sub(r'\[Hebrew and Aramaic\]', '', cleaned)
    cleaned = re.sub(r'\[Aramaic only\]', '', cleaned)
    cleaned = re.sub(r'\[Hebrew only\]', '', cleaned)
    # Clean up whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def parse_transliteration(text):
    """Extract transliteration from ( X-XX) format."""
    match = re.search(r'\(\s*([A-Za-z][A-Za-z\-]+)\s*\)', text)
    if match:
        return match.group(1).replace('-', '')
    return ''


def parse_root_header(line):
    """Parse a root header line like: 1002)  ( AB) ac: Stand co: Pole ab: ?"""
    match = re.match(r'(\d{4})\)\s+.*?\(\s*([A-Za-z]+)\s*\)\s*ac:\s*(.*?)\s*co:\s*(.*?)\s*ab:\s*(.*?)(?:$|~~)', line)
    if not match:
        # Try alternate format without the pictographic characters
        match = re.match(r'(\d{4})\)\s+\(\s*([A-Za-z]+)\s*\)\s*ac:\s*(.*?)\s*co:\s*(.*?)\s*ab:\s*(.*?)(?:$|~~)', line)
    if match:
        return {
            'root_number': int(match.group(1)),
            'root': match.group(2).strip(),
            'action': match.group(3).strip().rstrip(':').strip(),
            'concrete': match.group(4).strip().rstrip(':').strip(),
            'abstract': match.group(5).strip().rstrip(':').strip(),
        }
    return None


def classify_root_type(root_num):
    """Classify root by number range."""
    if 1001 <= root_num <= 1529:
        return 'parent'
    elif 2001 <= root_num <= 2999:
        return 'adopted_3letter'
    elif 3001 <= root_num <= 3099:
        return 'adopted_4letter'
    return 'unknown'


def parse_ahlb(filepath):
    """Parse the complete AHLB text file into structured data."""
    print(f'[INFO] Reading {filepath}...')
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    # Split into root sections by the separator
    # Each root section starts with a 4-digit number followed by )
    # Sections end with ~~~~~~~~~~

    roots = []
    words = []
    by_strongs = {}
    root_hierarchy = {}

    # Find the start of the actual lexicon (after "The Lexicon" header)
    lexicon_start = content.find('Parent and Child Roots')
    if lexicon_start == -1:
        lexicon_start = content.find('The Lexicon')
    if lexicon_start == -1:
        lexicon_start = 0

    lexicon_text = content[lexicon_start:]

    # Split by root separators
    sections = re.split(r'~~~~~~~~~~+', lexicon_text)
    print(f'[INFO] Found {len(sections)} sections to parse')

    current_root = None
    word_count = 0
    root_count = 0

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Check for root header (4-digit number at start of section)
        # Format: "1002)  ( AB) ac: Stand co: Pole ab: ?"
        # Note: there are Unicode pictographic characters between ) and (
        # Use a very permissive regex that just looks for the root number and transliteration
        root_match = re.search(r'^(\d{4})\)', section)
        if root_match:
            root_num = int(root_match.group(1))

            # Find the transliteration in parentheses: ( AB ) or ( ABG ) etc.
            translit_match = re.search(r'\(\s*([A-Z][A-Za-z]{1,3})\s*\)', section[:200])
            root_letters = translit_match.group(1) if translit_match else ''

            root_type = classify_root_type(root_num)

            # Parse ac:/co:/ab: from the header
            accoab = re.search(r'ac:\s*(.*?)\s+co:\s*(.*?)\s+ab:\s*(.*?)(?:\s*[~:.]|\s*The|\s*\(eng|\s*\[from)', section[:600])
            action = ''
            concrete_def = ''
            abstract_def = ''
            if accoab:
                action = accoab.group(1).strip().rstrip('?:').strip()
                concrete_def = accoab.group(2).strip().rstrip('?:').strip()
                abstract_def = accoab.group(3).strip().rstrip('?:').strip()
                # Clean up trailing garbage
                for field in ['action', 'concrete_def', 'abstract_def']:
                    val = locals()[field]
                    # Truncate at newline or very long text
                    if '\n' in val:
                        val = val.split('\n')[0].strip()
                    if len(val) > 80:
                        val = val[:80].strip()
                    locals()[field] = val

            # Extract full description text (after ab: line, before child roots)
            desc_match = re.search(r'ab:\s*[^:]*?:\s*(.*?)(?:\nA\)\s|\nB\)\s|\nC\)\s|\n[A-N]\)\s|$)', section[:1500], re.DOTALL)
            description = ''
            if desc_match:
                description = desc_match.group(1).strip()
                description = re.sub(r'\s+', ' ', description)

            # Check for [from: XX] for adopted roots
            parent_from = ''
            from_match = re.search(r'\[from:\s*([^\]]+)\]', section)
            if from_match:
                parent_from = from_match.group(1).strip()

            # Check for (eng: ...) English cognate
            eng_match = re.search(r'\(eng:\s*([^)]+)\)', section[:600])
            eng_cognate = eng_match.group(1).strip() if eng_match else ''

            current_root = {
                'root_number': root_num,
                'root': root_letters,
                'root_type': root_type,
                'action': action,
                'concrete': concrete_def,
                'abstract': abstract_def,
                'description': description[:500],
                'parent_from': parent_from,
                'eng_cognate': eng_cognate,
                'words': [],
            }
            roots.append(current_root)
            root_count += 1

            # Add to hierarchy
            root_hierarchy[root_letters] = {
                'number': root_num,
                'type': root_type,
                'action': action,
                'concrete': concrete_def,
                'abstract': abstract_def,
                'parent_from': parent_from,
                'eng_cognate': eng_cognate,
            }

        # Now parse all word entries in this section
        # Word entries have formats like:
        #   Nm) (TRANSLITERATION) — Definition [freq. N] |kjv: ...| {str: NNNN}
        #   V) (TRANSLITERATION) — Definition [freq. N] (vf: ...) |kjv: ...| {str: NNNN}
        #   Nf1) etc.

        # Find all word entries by looking for Strong's numbers
        strongs_pattern = r'\{str:\s*([\d,\s]+)\}'
        for strongs_match in re.finditer(strongs_pattern, section):
            strongs_nums = [f'H{n.strip()}' for n in strongs_match.group(1).split(',') if n.strip()]

            # Get the context: scan backwards from {str:} to find the nearest word entry marker
            pos = strongs_match.start()

            # Look backwards for the nearest grammatical form marker like "Nm)", "V)", "Nf1)", etc.
            # These mark the start of a word entry
            pre_text = section[:pos]
            # Find the last occurrence of a form marker before this {str:}
            form_markers = list(re.finditer(r'(?:^|\s)(V|Nm|Nf[0-9]?|[a-t]m?|[a-t]f[0-9]?|bm|cm|dm|em|fm|gm|hm|im|jm|km|lm|rm|bf[0-9]?|cf[0-9]?|df[0-9]?|ef[0-9]?|ff[0-9]?|gf[0-9]?|hf[0-9]?|if[0-9]?|jf[0-9]?|kf[0-9]?|lf[0-9]?|mf[0-9]?|nf[0-9]?|of[0-9]?|pf[0-9]?|qf[0-9]?|rf[0-9]?|sf[0-9]?|tf[0-9]?|afm|bfm)\)\s', pre_text))

            if form_markers:
                entry_start = form_markers[-1].start()
            else:
                entry_start = max(0, pos - 400)

            context = section[entry_start:strongs_match.end()]

            # Extract frequency
            freq = parse_frequency(context)

            # Extract KJV translations
            kjv = parse_kjv(context)

            # Extract verb forms
            verb_forms = parse_verb_forms(context)

            # Extract transliteration - look for ( X-XX ) pattern closest to the definition
            translit = ''
            translit_matches = list(re.finditer(r'\(\s*([A-Z][A-Za-z\-]+)\s*\)', context))
            if translit_matches:
                # Take the first transliteration in this word entry
                translit = translit_matches[0].group(1).replace('-', '').lower()

            # Extract the definition text after the — (em dash)
            definition = ''
            def_match = re.search(r'—\s*((?:I\.|II\.|III\.|IV\.)?\s*[A-Z].*?)(?:\[freq|\|kjv|\{str|\(vf:|\[ms:|\[df:|\[ar:|\[Hebrew|\[Aramaic)', context, re.DOTALL)
            if def_match:
                definition = def_match.group(1).strip()
                definition = re.sub(r'\s+', ' ', definition).strip()
                # Trim overly long definitions
                if len(definition) > 500:
                    definition = definition[:500].strip()

            # Determine grammatical form from the entry marker
            gram_form = ''
            if form_markers:
                gram_form = form_markers[-1].group(1).strip()

            # Determine if verb or noun
            is_verb = gram_form == 'V' or len(verb_forms) > 0

            word_entry = {
                'strongs': strongs_nums,
                'transliteration': translit,
                'definition': definition,
                'frequency': freq,
                'kjv_translations': kjv,
                'verb_forms': verb_forms,
                'grammatical_form': gram_form,
                'is_verb': is_verb,
                'root_number': current_root['root_number'] if current_root else 0,
                'root': current_root['root'] if current_root else '',
                'root_type': current_root['root_type'] if current_root else '',
                'root_action': current_root['action'] if current_root else '',
                'root_concrete': current_root['concrete'] if current_root else '',
                'root_abstract': current_root['abstract'] if current_root else '',
            }

            words.append(word_entry)
            word_count += 1

            # Index by Strong's number
            for sn in strongs_nums:
                by_strongs[sn] = word_entry

            # Add to current root's word list
            if current_root:
                current_root['words'].append({
                    'strongs': strongs_nums,
                    'transliteration': translit,
                    'definition': definition,
                    'frequency': freq,
                    'is_verb': is_verb,
                })

    print(f'[INFO] Parsed {root_count} roots')
    print(f'[INFO] Parsed {word_count} word entries')
    print(f'[INFO] Indexed {len(by_strongs)} Strong\'s numbers')

    return roots, words, by_strongs, root_hierarchy


def save_results(roots, words, by_strongs, root_hierarchy):
    """Save parsed data to JSON files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Complete AHLB data (roots with their words)
    ahlb_complete = {
        'metadata': {
            'title': 'Ancient Hebrew Lexicon of the Bible - Complete Parse',
            'author': 'Jeff A. Benner',
            'parsed_by': 'Mechanical Bible AHLB Parser',
            'total_roots': len(roots),
            'total_words': len(words),
            'total_strongs': len(by_strongs),
        },
        'roots': roots,
    }
    complete_path = OUTPUT_DIR / 'ahlb_complete.json'
    with open(complete_path, 'w', encoding='utf-8') as f:
        json.dump(ahlb_complete, f, ensure_ascii=False, indent=2)
    print(f'[SAVED] {complete_path} ({complete_path.stat().st_size:,} bytes)')

    # 2. By Strong's number (for easy lookup)
    strongs_path = OUTPUT_DIR / 'ahlb_by_strongs.json'
    with open(strongs_path, 'w', encoding='utf-8') as f:
        json.dump(by_strongs, f, ensure_ascii=False, indent=2)
    print(f'[SAVED] {strongs_path} ({strongs_path.stat().st_size:,} bytes)')

    # 3. Root hierarchy
    hierarchy_path = OUTPUT_DIR / 'ahlb_roots.json'
    with open(hierarchy_path, 'w', encoding='utf-8') as f:
        json.dump(root_hierarchy, f, ensure_ascii=False, indent=2)
    print(f'[SAVED] {hierarchy_path} ({hierarchy_path.stat().st_size:,} bytes)')


def print_sample(roots, by_strongs):
    """Print sample entries to verify parsing."""
    print('\n' + '=' * 60)
    print('SAMPLE ENTRIES')
    print('=' * 60)

    # Show some key words
    test_words = {
        'H7225': 'bereshit (Beginning)',
        'H1254': 'bara (Create/Shape)',
        'H430': 'elohim (God/Powers)',
        'H8064': 'shamayim (Sky)',
        'H776': 'erets (Land)',
        'H3068': 'YHWH',
        'H120': 'adam (Man)',
        'H8451': 'torah (Instruction)',
        'H7965': 'shalom (Peace)',
        'H2617': 'chesed (Kindness)',
        'H7307': 'ruach (Wind/Breath)',
        'H5315': 'nephesh (Being/Life)',
        'H3820': 'lev (Heart)',
        'H1285': 'berit (Covenant)',
        'H571': 'emeth (Truth)',
        'H410': 'el (Power/God)',
    }

    for sn, label in test_words.items():
        if sn in by_strongs:
            w = by_strongs[sn]
            print(f'\n  {sn} ({label}):')
            print(f'    Definition: {w["definition"][:120]}')
            print(f'    Root: {w["root"]} (#{w["root_number"]})')
            print(f'    Root meaning: ac:{w["root_action"]} co:{w["root_concrete"]} ab:{w["root_abstract"]}')
            print(f'    KJV: {", ".join(w["kjv_translations"][:8])}')
            print(f'    Frequency: {w["frequency"]}')
        else:
            print(f'\n  {sn} ({label}): NOT FOUND')

    # Stats
    print('\n' + '=' * 60)
    print('ROOT TYPE BREAKDOWN')
    print('=' * 60)
    types = defaultdict(int)
    for r in roots:
        types[r['root_type']] += 1
    for t, c in sorted(types.items()):
        print(f'  {t}: {c}')

    # Coverage stats
    print(f'\n  Total unique Strong\'s numbers indexed: {len(by_strongs)}')
    print(f'  Coverage of H1-H8674: {len(by_strongs)}/8674 = {len(by_strongs)/8674*100:.1f}%')


def main():
    print('=' * 60)
    print('PARSE AHLB COMPLETE - Mechanical Bible')
    print('Ancient Hebrew Lexicon of the Bible (Jeff A. Benner)')
    print('=' * 60)

    filepath = find_ahlb_file()
    if not filepath:
        return

    roots, words, by_strongs, root_hierarchy = parse_ahlb(filepath)

    if not roots:
        print('[ERROR] No roots parsed. Check file format.')
        return

    save_results(roots, words, by_strongs, root_hierarchy)
    print_sample(roots, by_strongs)

    print('\n' + '=' * 60)
    print(f'[DONE] Parsed {len(roots)} roots, {len(words)} words, {len(by_strongs)} Strong\'s entries')
    print('=' * 60)


if __name__ == '__main__':
    main()
