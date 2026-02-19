#!/usr/bin/env python3
"""
DEEP NAME ANALYSIS - Mechanical Bible
======================================
Analyzes every biblical name using HebrewStrong.xml (8,674 entries),
AHLB root data, and OSHB morphological data to produce the most
comprehensive name definitions possible.

For each name produces:
  - Strong's number
  - Pointed Hebrew with vowels
  - Pronunciation (phonetic)
  - Transliteration (academic)
  - Part of speech (person/place/people)
  - Etymology (source text from Strong's)
  - Root components (each root word with meaning)
  - Mechanical meaning (root-based meaning extraction)
  - Full definition

Matching strategy:
  1. Existing Strong's number -> direct lookup
  2. Hebrew text (unpointed) -> Strong's proper noun lookup
  3. English name -> Strong's usage field lookup
  4. Remaining unmatched flagged for review

Output: data/names_enriched_preview.json (DRY RUN)
  Does NOT overwrite bible_names.json without permission.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).parent.parent
NAMES_JSON = BASE_DIR / 'data' / 'bible_names.json'
AHLB_STRONGS = BASE_DIR / 'data' / 'ahlb_by_strongs.json'
AHLB_COMPLETE = BASE_DIR / 'data' / 'ahlb_complete.json'
STRONG_XML = Path(r'C:\Users\Tammy Casey\Documents\AI PROJECTS\PEER\morphhb-master\HebrewStrong.xml')

NS = 'http://openscriptures.github.com/morphhb/namespace'


def full_text(elem):
    """Get full text content of an XML element including children."""
    if elem is None:
        return ''
    parts = [elem.text or '']
    for c in elem:
        parts.append(c.text or '')
        parts.append(c.tail or '')
    return re.sub(r'\s+', ' ', ' '.join(parts)).strip()


def parse_strongs_xml():
    """Parse HebrewStrong.xml into a complete dictionary."""
    print(f'Loading {STRONG_XML.name}...')
    tree = ET.parse(str(STRONG_XML))
    root = tree.getroot()

    strongs = {}
    for entry in root:
        sid = entry.attrib.get('id', '')
        if not sid:
            continue

        w = entry.find(f'{{{NS}}}w')
        source = entry.find(f'{{{NS}}}source')
        meaning = entry.find(f'{{{NS}}}meaning')
        usage = entry.find(f'{{{NS}}}usage')

        source_refs = []
        if source is not None:
            for ref in source.findall(f'{{{NS}}}w'):
                src = ref.attrib.get('src', '')
                if src:
                    source_refs.append(f'H{src}')

        strongs[sid] = {
            'hebrew': (w.text or '').strip() if w is not None else '',
            'pron': w.attrib.get('pron', '') if w is not None else '',
            'xlit': w.attrib.get('xlit', '') if w is not None else '',
            'pos': w.attrib.get('pos', '') if w is not None else '',
            'source_text': full_text(source),
            'source_refs': source_refs,
            'meaning': full_text(meaning),
            'usage': full_text(usage),
        }

    print(f'  {len(strongs)} entries loaded')
    return strongs


def build_lookups(strongs):
    """Build multiple lookup tables for matching names to Strong's."""
    # Hebrew (unpointed) -> Strong's for proper nouns
    by_hebrew = {}
    for sid, e in strongs.items():
        if 'n-pr' in e.get('pos', ''):
            clean = re.sub(r'[\u0591-\u05C7]', '', e['hebrew'])
            if clean and clean not in by_hebrew:
                by_hebrew[clean] = sid

    # English name -> Strong's (from usage field)
    by_english = {}
    for sid, e in strongs.items():
        if 'n-pr' not in e.get('pos', ''):
            continue
        usage = e.get('usage', '')
        for eng_name in re.findall(r'([A-Z][a-z]+)', usage):
            if eng_name not in by_english:
                by_english[eng_name] = sid
        # Also check meaning field
        meaning = e.get('meaning', '')
        for eng_name in re.findall(r'([A-Z][a-z]+)', meaning):
            if eng_name not in by_english:
                by_english[eng_name] = sid

    return by_hebrew, by_english


def extract_mechanical_meaning(se):
    """Extract the root-based mechanical meaning from source text."""
    src = se.get('source_text', '')

    # Look for meaning phrases after semicolons
    meaning_phrases = []
    parts = src.split(';')
    for p in parts[1:]:
        p = p.strip().rstrip(';').strip()
        if p and not p.startswith('from') and not p.startswith('or ') and not p.startswith('the same'):
            clean = re.sub(r'\(.*?\)', '', p).strip()
            if clean and len(clean) > 1:
                meaning_phrases.append(clean)

    if meaning_phrases:
        return '; '.join(meaning_phrases)

    # Fall back to meaning field minus the name itself
    m = se.get('meaning', '')
    m = re.sub(r'^[^,]+,\s*', '', m).strip()
    return m


def resolve_etymology(se, strongs, ahlb, strongs_to_root):
    """Build etymology chain from source references."""
    parts = []
    for ref in se.get('source_refs', []):
        entry = {}
        if ref in strongs:
            r = strongs[ref]
            root_meaning = r['meaning'] or r['usage']
            root_meaning = re.sub(r'\s+', ' ', root_meaning).strip().rstrip('.')

            entry = {
                'strongs': ref,
                'hebrew': r['hebrew'],
                'meaning': root_meaning,
            }

            if ref in ahlb:
                ahlb_def = ahlb[ref].get('definition', '')
                if ahlb_def and ':' in ahlb_def:
                    entry['ahlb'] = ahlb_def.split(':')[0].strip()
                elif ahlb_def:
                    entry['ahlb'] = ahlb_def.split('.')[0].strip()

            root_data = strongs_to_root.get(ref, {})
            if root_data.get('action'):
                entry['root_action'] = root_data['action']
            if root_data.get('concrete'):
                entry['root_concrete'] = root_data['concrete']

        elif ref in ahlb:
            a = ahlb[ref]
            d = a.get('definition', '')
            short = d.split(':')[0].strip() if ':' in d else d
            entry = {'strongs': ref, 'meaning': short}

        if entry:
            parts.append(entry)
    return parts


def build_definition(english, se, etymology, ahlb):
    """Build the comprehensive definition string."""
    mech = extract_mechanical_meaning(se)

    # Start with mechanical meaning
    if mech:
        defn = mech.rstrip('.').strip()
    else:
        defn = ''

    # Add etymology info if no mechanical meaning
    if not defn and etymology:
        root_meanings = []
        for e in etymology:
            m = e.get('ahlb') or e.get('meaning', '')
            if m:
                m = re.sub(r'^[^,]+,\s*', '', m) if ',' in m and len(m) > 50 else m
                m = m.split('.')[0].strip() if len(m) > 60 else m
                root_meanings.append(m)
        if root_meanings:
            defn = ' + '.join(root_meanings)

    # If we still have nothing, use the Strong's meaning field
    if not defn:
        m = se.get('meaning', '')
        m = re.sub(r'^[^,]+,\s*', '', m).strip()
        if m:
            defn = m

    # Capitalize first letter
    if defn:
        defn = defn[0].upper() + defn[1:] if len(defn) > 1 else defn.upper()

    return defn


def is_garbage_name(english):
    """Detect entries that are NOT actual biblical names."""
    garbage_words = {
        'Robbers', 'Undoes', 'Thrusts', 'Brazenly', 'Ants', 'Canal', 'Burnish',
        'Equip', 'Mined', 'Shelves', 'Fleeter', 'Blackest', 'Tracked', 'Bid',
        'Leveled', 'Lender', 'Laity', 'Lighters', 'Wrack', 'Achieves', 'Restorer',
        'Adders', 'Vapors', 'Mow', 'Gestures', 'Inlaid', 'Gleams', 'Magnate',
        'Loosed', 'Hostsis', 'Highhe', 'Ho', 'Curd', 'Hitch', 'Hey',
        'Someday', 'Sometime', 'Caller', 'Hosts', 'Sober', 'Talmud', 'Brace',
        'Saadia', 'Trani', 'Lehazkir', 'Clauses',
        'Jacoband', 'Godwho', 'Godwith', 'Godwhose', 'Highand',
        'Youto', 'Youwhen', 'Yahnow', 'Zionthat', 'Horeband',
        'Higgaion', 'Koheleth', 'Esth', 'Baba', 'Kamma',
        'Amirethe', 'Amir', 'Kedemite', 'Luzzatto',
        'Peshitta', 'Kimhi', 'Malbim', 'Davidic', 'Kasdim',
        'Onkelos', 'Tiberian', 'Empire', 'Middoth',
        'Deck', 'Rough', 'Torrid', 'Aye', 'Robbers',
        'Syntax', 'Absolve', 'Park', 'Marginal', 'Punic', 'Lam',
        'Loosed', 'Thrusts', 'Janah', 'Hush',
        'Seiraand', 'Darom', 'Gateaat', 'Ramahiin', 'Shaon',
        'Obad', 'Lashed', 'Citycthe', 'Imhow', 'Seagthe',
        'Edomihe', 'Hilldthe', 'Onioth', 'Canaanas',
        'Greek', 'Arabic', 'Syriac', 'Aramaic',
        'Yea', 'Az', 'Isn',
    }
    return english in garbage_words


def main():
    print('=' * 60)
    print('DEEP NAME ANALYSIS - Mechanical Bible')
    print('=' * 60)

    # Load all data sources
    strongs = parse_strongs_xml()
    by_hebrew, by_english = build_lookups(strongs)
    print(f'  Hebrew lookup: {len(by_hebrew)} proper nouns')
    print(f'  English lookup: {len(by_english)} name mappings')

    print(f'Loading AHLB data...')
    with open(AHLB_STRONGS, 'r', encoding='utf-8') as f:
        ahlb = json.load(f)
    print(f'  {len(ahlb)} AHLB entries')

    with open(AHLB_COMPLETE, 'r', encoding='utf-8') as f:
        ahlb_c = json.load(f)

    # Build root lookup
    strongs_to_root = {}
    for rt in ahlb_c.get('roots', []):
        for word in rt.get('words', []):
            for s in word.get('strongs', []):
                strongs_to_root[f'H{s}'] = {
                    'root': rt.get('root', ''),
                    'action': rt.get('action', ''),
                    'concrete': rt.get('concrete', ''),
                    'abstract': rt.get('abstract', ''),
                    'description': rt.get('description', ''),
                }

    # Load names
    print(f'Loading bible_names.json...')
    with open(NAMES_JSON, 'r', encoding='utf-8') as f:
        names_data = json.load(f)
    names = names_data.get('names', [])
    print(f'  {len(names)} names')

    # Process every name
    print(f'\n{"="*60}')
    print(f'ANALYZING ALL {len(names)} NAMES')
    print(f'{"="*60}')

    matched = 0
    unmatched = []
    enriched_count = 0
    garbage_count = 0
    match_methods = Counter()

    for i, n in enumerate(names):
        heb = n.get('hebrew', '')
        english = n.get('english', '')
        existing_strongs = n.get('strongs', '')
        existing_def = n.get('definition', '')

        # Flag garbage entries
        if is_garbage_name(english):
            names[i]['_garbage'] = True
            garbage_count += 1
            continue

        # Find Strong's number - try 3 methods
        sid = None
        method = None

        # Method 1: Existing Strong's
        if existing_strongs and existing_strongs in strongs:
            sid = existing_strongs
            method = 'existing_strongs'

        # Method 2: Hebrew text lookup
        if not sid and heb in by_hebrew:
            sid = by_hebrew[heb]
            method = 'hebrew_match'

        # Method 3: English name lookup
        if not sid and english in by_english:
            sid = by_english[english]
            method = 'english_match'

        if not sid or sid not in strongs:
            unmatched.append(english)
            continue

        matched += 1
        match_methods[method] += 1
        se = strongs[sid]

        # Build etymology
        etymology = resolve_etymology(se, strongs, ahlb, strongs_to_root)

        # Build comprehensive definition
        new_def = build_definition(english, se, etymology, ahlb)

        # Enrich the name entry with ALL available data
        names[i]['strongs'] = sid
        if se['xlit']:
            names[i]['transliteration'] = se['xlit']
        if se['pron']:
            names[i]['pronunciation'] = se['pron']
        if se['hebrew']:
            names[i]['pointed_hebrew'] = se['hebrew']
        if se['pos']:
            names[i]['pos'] = se['pos']
        if se['source_text']:
            names[i]['etymology'] = se['source_text']

        mech = extract_mechanical_meaning(se)
        if mech:
            names[i]['mechanical_meaning'] = mech

        if se['usage']:
            names[i]['usage'] = se['usage']

        if etymology:
            names[i]['root_components'] = etymology

        # Update definition if we have something better
        if new_def and (not existing_def or existing_def == '?'):
            names[i]['definition'] = new_def
            enriched_count += 1

    # Stats
    has_def = sum(1 for n in names if n.get('definition') and not n.get('_garbage'))
    has_strongs = sum(1 for n in names if n.get('strongs') and not n.get('_garbage'))
    has_pron = sum(1 for n in names if n.get('pronunciation') and not n.get('_garbage'))
    has_etymology = sum(1 for n in names if n.get('etymology') and not n.get('_garbage'))
    has_mech = sum(1 for n in names if n.get('mechanical_meaning') and not n.get('_garbage'))
    has_roots = sum(1 for n in names if n.get('root_components') and not n.get('_garbage'))
    real_names = sum(1 for n in names if not n.get('_garbage'))

    print(f'\n{"="*60}')
    print(f'RESULTS')
    print(f'{"="*60}')
    print(f'Total entries: {len(names)}')
    print(f'Garbage flagged: {garbage_count}')
    print(f'Real names: {real_names}')
    print(f'Matched to Strong\'s: {matched}')
    print(f'  by existing strongs: {match_methods["existing_strongs"]}')
    print(f'  by hebrew text: {match_methods["hebrew_match"]}')
    print(f'  by english name: {match_methods["english_match"]}')
    print(f'Unmatched: {len(unmatched)}')
    print(f'New definitions added: {enriched_count}')
    print(f'\nField population (real names only):')
    print(f'  definition: {has_def}/{real_names} ({has_def/real_names*100:.1f}%)')
    print(f'  strongs: {has_strongs}/{real_names} ({has_strongs/real_names*100:.1f}%)')
    print(f'  pronunciation: {has_pron}/{real_names} ({has_pron/real_names*100:.1f}%)')
    print(f'  etymology: {has_etymology}/{real_names} ({has_etymology/real_names*100:.1f}%)')
    print(f'  mechanical_meaning: {has_mech}/{real_names} ({has_mech/real_names*100:.1f}%)')
    print(f'  root_components: {has_roots}/{real_names} ({has_roots/real_names*100:.1f}%)')

    if unmatched:
        print(f'\nUnmatched names ({len(unmatched)}):')
        for u in sorted(unmatched):
            print(f'  {u}')

    # Show 20 sample enriched names
    print(f'\n{"="*60}')
    print(f'SAMPLE ENRICHED NAMES')
    print(f'{"="*60}')
    shown = 0
    for n in names:
        if n.get('mechanical_meaning') and not n.get('_garbage') and shown < 20:
            print(f'\n{n["english"]} ({n["hebrew"]}) [{n.get("strongs","")}]')
            print(f'  Pointed: {n.get("pointed_hebrew","")}')
            print(f'  Pronunciation: {n.get("pronunciation","")}')
            print(f'  Transliteration: {n.get("transliteration","")}')
            print(f'  Definition: {n.get("definition","")}')
            print(f'  Mechanical: {n.get("mechanical_meaning","")}')
            print(f'  Etymology: {n.get("etymology","")[:150]}')
            if n.get('root_components'):
                print(f'  Roots:')
                for r in n['root_components']:
                    ahlb_note = f' [AHLB: {r["ahlb"]}]' if r.get('ahlb') else ''
                    print(f'    {r.get("strongs","")}: {r.get("hebrew","")} = {r.get("meaning","")[:80]}{ahlb_note}')
            shown += 1

    # Save enriched data (DRY RUN)
    preview_path = BASE_DIR / 'data' / 'names_enriched_preview.json'
    names_data['names'] = names
    with open(preview_path, 'w', encoding='utf-8') as f:
        json.dump(names_data, f, ensure_ascii=False, indent=2)
    print(f'\n[DRY RUN] Enriched data saved to: {preview_path}')
    print(f'Review before applying to bible_names.json!')


if __name__ == '__main__':
    main()
