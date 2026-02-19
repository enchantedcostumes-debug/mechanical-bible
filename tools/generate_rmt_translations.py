#!/usr/bin/env python3
"""
GENERATE RMT TRANSLATIONS - Mechanical Bible
===============================================
Generates Benner-style multi-layer translations for every verse
in every chapter HTML file.

Three translation layers per verse:
1. MECHANICAL: Word-for-word with prefix notation (in~SUMMIT SHAPE(V) POWER~s)
2. RMT (Revised Mechanical Translation): Natural English preserving Hebrew names
3. STANDARD: More readable flowing English

Replaces the JPS translation text in <div class="translation"> with
all three layers.

Source methodology: Jeff Benner, The Mechanical Translation of the Torah

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'

# Hebrew prefix meanings for RMT layer
PREFIX_RMT = {
    'ו': 'and',
    'וה': 'and the',
    'וב': 'and in',
    'ול': 'and to',
    'וכ': 'and like',
    'ומ': 'and from',
    'ב': 'in',
    'בה': 'in the',
    'ל': 'to',
    'לה': 'to the',
    'כ': 'like',
    'כה': 'like the',
    'מ': 'from',
    'מה': 'from the',
    'ה': 'the',
    'ש': 'that',
    'שב': 'that in',
    'של': 'that to',
    'שה': 'that the',
}

# Mechanical prefix notation
PREFIX_MECH = {
    'ו': 'and~',
    'וה': 'and~the~',
    'וב': 'and~in~',
    'ול': 'and~to~',
    'וכ': 'and~like~',
    'ומ': 'and~from~',
    'ב': 'in~',
    'בה': 'in~the~',
    'ל': 'to~',
    'לה': 'to~the~',
    'כ': 'like~',
    'כה': 'like~the~',
    'מ': 'from~',
    'מה': 'from~the~',
    'ה': 'the~',
    'ש': 'which~',
    'שב': 'which~in~',
    'של': 'which~to~',
    'שה': 'which~the~',
}


def load_words():
    """Load words.json."""
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'[OK] Loaded {len(words)} words')
    return words


# Pictographic letter description words — if a definition starts with these
# followed by commas, it's letter-by-letter pictographic, not a real definition
LETTER_PIC_WORDS = {'strength', 'hand', 'nail', 'mark', 'staff', 'window', 'house',
                    'teeth', 'water', 'head', 'eye', 'mouth', 'seed', 'palm',
                    'fence', 'door', 'basket', 'ox', 'foot', 'sun', 'cross',
                    'side', 'thorn', 'snake'}


def is_pictographic(defn):
    """Check if a definition is just pictographic letter descriptions."""
    if not defn:
        return True
    first_word = defn.split(',')[0].split(' ')[0].lower().strip()
    return first_word in LETTER_PIC_WORDS and ', ' in defn[:40]


def has_real_definition(entry):
    """Check if a word entry has a real (non-pictographic) definition."""
    if not entry:
        return False
    if entry.get('mechanical_translation') or entry.get('rmt_translation'):
        return True
    defn = entry.get('definition', '')
    if not defn:
        return False
    if defn.startswith('[From pictographs'):
        return False
    if is_pictographic(defn):
        return False
    if '[Direct object marker]' in defn or '[Object marker]' in defn:
        return True  # AT marker is valid
    return True


def get_mechanical(word, entry):
    """Get mechanical translation for a word."""
    mech = entry.get('mechanical_translation', '')
    if mech:
        return mech

    defn = entry.get('definition', '')
    if not defn or is_pictographic(defn):
        return word

    short = defn.split(':')[0].strip()
    for prefix in ('I. ', 'II. ', 'III. '):
        if short.startswith(prefix):
            short = short[len(prefix):]
    if short.startswith(('And ', 'The ', 'In ', 'To ', 'From ', 'Like ')):
        parts = short.split(' ', 1)
        prefix = parts[0].lower()
        rest = parts[1] if len(parts) > 1 else ''
        return f'{prefix}~{rest.upper()}'

    return short.upper().replace(' ', '.')


def get_rmt(word, entry):
    """Get RMT (natural English) translation for a word."""
    rmt = entry.get('rmt_translation', '')
    if rmt and rmt != '~':
        return rmt
    if rmt == '~':
        return ''

    defn = entry.get('definition', '')
    if not defn:
        return ''

    if '[Direct object marker]' in defn or '[Object marker]' in defn:
        return ''

    if is_pictographic(defn):
        return ''

    # Handle prefix-composed definitions
    prefix_match = re.match(r'^(And the|And to|And in|And from|And|In the|In|To the|To|From the|From|Like|The|That)\s+(.+?)(?::|\.|\s*$)', defn)
    if prefix_match:
        prefix = prefix_match.group(1).lower()
        rest = prefix_match.group(2).strip()
        rest_word = rest.split(':')[0].split('.')[0].split(',')[0].strip().lower()
        if rest_word and rest_word not in LETTER_PIC_WORDS:
            return f'{prefix} {rest_word}'
        return prefix

    short = defn.split(':')[0].strip()
    for prefix in ('I. ', 'II. ', 'III. '):
        if short.startswith(prefix):
            short = short[len(prefix):]

    short = short.replace('[', '').replace(']', '').strip()
    if short and short.split(',')[0].split(' ')[0].lower() in LETTER_PIC_WORDS:
        return ''

    if len(short) > 30:
        short = short.split(' ')[0]

    return short.lower()


def decompose_compound(word, words_dict):
    """Decompose a compound Hebrew word into translatable parts.

    Hebrew tokens in the HTML can be compound words like:
    - אלהיםליבשה = אלהים + ל + יבשה (Elohiym + to + dry ground)
    - ויהיכן = ו + יהי + כן (and + existed + so)
    - אתהמים = את + ה + מים (AT + the + waters)

    Returns list of (hebrew_part, entry) tuples.
    """
    # Try known prefixes first (longest match first)
    prefixes_sorted = sorted(PREFIX_RMT.keys(), key=len, reverse=True)

    # Strategy 1: Try splitting at every position to find two known words
    for split_pos in range(1, len(word)):
        left = word[:split_pos]
        right = word[split_pos:]

        left_entry = words_dict.get(left, {})
        right_entry = words_dict.get(right, {})

        if has_real_definition(left_entry) and has_real_definition(right_entry):
            return [(left, left_entry), (right, right_entry)]

        # Try right side with prefix stripping
        if has_real_definition(left_entry):
            for pfx in prefixes_sorted:
                if right.startswith(pfx) and len(right) > len(pfx):
                    root = right[len(pfx):]
                    root_entry = words_dict.get(root, {})
                    if has_real_definition(root_entry):
                        return [(left, left_entry), (right, words_dict.get(right, root_entry))]

    # Strategy 2: Strip known prefix, then try to split remainder
    for pfx in prefixes_sorted:
        if word.startswith(pfx) and len(word) > len(pfx):
            remainder = word[len(pfx):]
            rem_entry = words_dict.get(remainder, {})
            if has_real_definition(rem_entry):
                return [('prefix:' + pfx, {}), (remainder, rem_entry)]

            # Try splitting the remainder
            for split_pos in range(1, len(remainder)):
                left = remainder[:split_pos]
                right = remainder[split_pos:]
                left_entry = words_dict.get(left, {})
                right_entry = words_dict.get(right, {})
                if has_real_definition(left_entry) and has_real_definition(right_entry):
                    return [('prefix:' + pfx, {}), (left, left_entry), (right, right_entry)]

    # Strategy 3: Try three-part split (word1 + word2 + word3)
    for i in range(1, len(word) - 1):
        for j in range(i + 1, len(word)):
            p1, p2, p3 = word[:i], word[i:j], word[j:]
            e1 = words_dict.get(p1, {})
            e2 = words_dict.get(p2, {})
            e3 = words_dict.get(p3, {})
            if has_real_definition(e1) and has_real_definition(e2) and has_real_definition(e3):
                return [(p1, e1), (p2, e2), (p3, e3)]

    return None  # Could not decompose


def translate_word(hw, words_dict):
    """Translate a single Hebrew word, decomposing compounds if needed.

    Returns (mechanical, rmt) tuple.
    """
    entry = words_dict.get(hw, {})

    # If we have a real definition, use it directly
    if has_real_definition(entry):
        return get_mechanical(hw, entry), get_rmt(hw, entry)

    # Try to decompose compound word
    parts = decompose_compound(hw, words_dict)
    if parts:
        mech_parts = []
        rmt_parts = []
        for part_hw, part_entry in parts:
            if part_hw.startswith('prefix:'):
                pfx = part_hw[7:]
                mech_parts.append(PREFIX_MECH.get(pfx, pfx + '~').rstrip('~'))
                rmt_parts.append(PREFIX_RMT.get(pfx, pfx))
            elif has_real_definition(part_entry):
                m = get_mechanical(part_hw, part_entry)
                r = get_rmt(part_hw, part_entry)
                mech_parts.append(m)
                if r:
                    rmt_parts.append(r)
            else:
                mech_parts.append(part_hw)
        return ' '.join(mech_parts), ' '.join(rmt_parts)

    # Last resort: if entry exists but is pictographic, return empty
    if entry:
        return hw, ''

    # Not in lexicon at all
    return hw, ''


def translate_verse(hebrew_words, words_dict):
    """Translate a list of Hebrew words into mechanical and RMT layers."""
    mech_parts = []
    rmt_parts = []

    for hw in hebrew_words:
        mech, rmt = translate_word(hw, words_dict)
        mech_parts.append(mech)
        if rmt:
            rmt_parts.append(rmt)

    mechanical = ' '.join(mech_parts)
    rmt_raw = ' '.join(rmt_parts)

    # Clean up RMT
    rmt_clean = rmt_raw.strip()
    if rmt_clean:
        rmt_clean = rmt_clean[0].upper() + rmt_clean[1:]
        rmt_clean = re.sub(r'\s+', ' ', rmt_clean)
        rmt_clean = re.sub(r'\band and\b', 'and', rmt_clean)
        if rmt_clean and rmt_clean[-1] not in '.!?,;':
            rmt_clean += '.'

    return mechanical, rmt_clean


def extract_hebrew_words(verse_html):
    """Extract Hebrew words from verse HTML."""
    # Find all <span class="word" ...>HEBREW</span>
    words = re.findall(r'<span[^>]*class="word"[^>]*>([^<]+)</span>', verse_html)
    return words


def process_html_file(filepath, words_dict, dry_run=False):
    """Process a single chapter HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    verses_translated = 0

    # Strategy: find each <div class="verse" id="..."> block and within it:
    # 1. Extract Hebrew words from the original-text div
    # 2. Generate mechanical + RMT translations
    # 3. Replace the <div class="translation">...</div> content

    # First, find all verse block boundaries
    verse_starts = [(m.start(), m.group(1)) for m in re.finditer(r'<div class="verse" id="([^"]*)">', content)]

    if not verse_starts:
        return 0

    # Process each verse block
    replacements = []  # (old_text, new_text) pairs

    for i, (start, verse_id) in enumerate(verse_starts):
        # Find the end of this verse block (start of next verse or end of content section)
        if i + 1 < len(verse_starts):
            end = verse_starts[i + 1][0]
        else:
            end = len(content)

        verse_block = content[start:end]

        # Extract Hebrew words
        hebrew_words = extract_hebrew_words(verse_block)
        if not hebrew_words:
            continue

        # Generate translations
        mechanical, rmt = translate_verse(hebrew_words, words_dict)
        if not rmt:
            continue

        # Find the translation div within this block
        trans_match = re.search(r'(<div class="translation">)(.*?)(</div>)', verse_block, re.DOTALL)
        if not trans_match:
            continue

        old_translation_div = trans_match.group(0)
        old_content = trans_match.group(2).strip()

        # Extract existing JPS text (the original translation)
        # If it already has <span class="rmt">, extract from jps span; otherwise use raw content
        jps_match = re.search(r'<span class="jps"[^>]*>(.*?)</span>', old_content, re.DOTALL)
        if jps_match:
            jps_text = jps_match.group(1).strip()
        else:
            # Strip any existing rmt/mechanical spans to get raw JPS
            jps_text = re.sub(r'<span class="(?:rmt|mechanical)"[^>]*>.*?</span>', '', old_content)
            # Strip sup note-ref tags from JPS for clean extraction
            jps_text = re.sub(r'<sup class="note-ref"[^>]*>.*?</sup>', '', jps_text)
            jps_text = jps_text.strip()
            # Clean ." artifacts
            jps_text = jps_text.replace(' ."', '').replace('."', '').strip()

        # Preserve any sup note-ref tags
        sup_match = re.search(r'(<sup class="note-ref"[^>]*>.*?</sup>)', old_content)
        sup_tag = sup_match.group(1) if sup_match else ''

        # Build new translation content with all three layers
        new_content = f'<span class="rmt">{rmt}</span>'
        new_content += f'<span class="mechanical" style="display:none">{mechanical}</span>'
        if jps_text:
            new_content += f'<span class="jps" style="display:none">{jps_text}</span>'
        if sup_tag:
            new_content += f' {sup_tag}'

        new_translation_div = f'<div class="translation">{new_content}</div>'

        replacements.append((old_translation_div, new_translation_div))
        verses_translated += 1

    # Apply all replacements
    if not dry_run and replacements:
        for old, new in replacements:
            content = content.replace(old, new, 1)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return verses_translated


def process_all_chapters(words_dict, dry_run=False):
    """Process all chapter HTML files."""
    # Get all book directories
    book_dirs = []
    for item in sorted(BASE_DIR.iterdir()):
        if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
            # Check if it contains HTML files
            html_files = list(item.glob('*.html'))
            if html_files:
                book_dirs.append(item)

    total_verses = 0
    total_files = 0

    for book_dir in book_dirs:
        html_files = sorted(book_dir.glob('*.html'))
        for hf in html_files:
            verses = process_html_file(hf, words_dict, dry_run=dry_run)
            if verses > 0:
                total_files += 1
                total_verses += verses

        if html_files:
            print(f'  {book_dir.name}: {len(html_files)} chapters')

    return total_files, total_verses


def main():
    import sys
    dry_run = '--dry-run' in sys.argv

    print('=' * 60)
    print('GENERATE RMT TRANSLATIONS - Mechanical Bible')
    print('Multi-layer translation for every verse')
    if dry_run:
        print('*** DRY RUN - no files will be modified ***')
    print('=' * 60)

    words = load_words()

    # Count how many words have mechanical/rmt translations
    has_mech = sum(1 for e in words.values() if e.get('mechanical_translation'))
    has_rmt = sum(1 for e in words.values() if e.get('rmt_translation'))
    print(f'[INFO] {has_mech} words have mechanical translations')
    print(f'[INFO] {has_rmt} words have RMT translations')

    # Test with Genesis 1 first
    print('\n=== TESTING GENESIS 1:1-5 ===')
    test_path = BASE_DIR / 'genesis' / '1.html'
    if test_path.exists():
        with open(test_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract first 5 verses
        verses = re.findall(r'<div class="verse" id="v1-(\d+)">(.*?)(?=<div class="verse"|<div class="chapter-nav")', content, re.DOTALL)
        for vnum, vhtml in verses[:5]:
            hebrew_words = extract_hebrew_words(vhtml)
            if hebrew_words:
                mech, rmt = translate_verse(hebrew_words, words)
                print(f'\n  Verse 1:{vnum}:')
                print(f'    Hebrew: {" ".join(hebrew_words)}')
                print(f'    Mechanical: {mech}')
                print(f'    RMT: {rmt}')

    # Process all files
    print('\n' + '=' * 60)
    print('PROCESSING ALL CHAPTER FILES')
    print('=' * 60)

    total_files, total_verses = process_all_chapters(words, dry_run=dry_run)

    print(f'\n[DONE] Translated {total_verses} verses across {total_files} files')
    if dry_run:
        print('[DRY RUN] No files were modified')

    print('=' * 60)


if __name__ == '__main__':
    main()
