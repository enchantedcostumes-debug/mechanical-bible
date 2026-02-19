#!/usr/bin/env python3
"""
Mechanical Translation Engine - Mechanical Bible
===================================================
Generates Benner-method mechanical translations from OSHB morphology codes.

Each Hebrew word is translated mechanically based on:
  1. The root word meaning (from AHLB)
  2. The grammatical form (from OSHB morph codes)
  3. Prefixes, suffixes, and particles

Format follows Jeff Benner's conventions:
  - Tildes (~) connect morphemes: and~he~will~SAY(V)
  - (V) marks verbs
  - ~s marks plurals, ~s2 marks duals
  - ~ing marks participles
  - Prefixes: in~, and~, the~, to~, from~, like~, that~
  - Person: he~, she~, I~, you~, we~, they~
  - Tense: will~ (imperfect/jussive/waw-consec), did~ (perfect)

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re

# ============================================================
# OSHB prefix codes → English
# ============================================================
PREFIX_MAP = {
    'b': 'in',
    'c': 'and',
    'd': 'the',
    'k': 'like',
    'l': 'to',
    'm': 'from',
    's': 'that',
    'i': 'by',
}

# ============================================================
# Morph prefix codes → English (from OSHB morph notation)
# ============================================================
MORPH_PREFIX_MAP = {
    'HC': 'and',      # Conjunction
    'HR': None,        # Preposition — handled by lemma prefix
    'HTd': 'the',      # Definite article
    'HRd': 'in~the',   # Preposition + article
    'HTr': None,        # Relative particle (אשר)
    'HTi': None,        # Interrogative
    'HTo': None,        # Object marker (את)
    'HTn': None,        # Negative
    'HTa': None,        # Affirmation
}

# ============================================================
# Verb stem labels for Benner-style output
# ============================================================
VERB_STEM_PREFIX = {
    'q': '',            # Qal — simple active (no prefix)
    'N': '',            # Niphal — Benner does NOT mark passive
    'p': 'much~',       # Piel — intensive active (Benner uses much~)
    'P': 'much~',       # Pual — intensive passive
    'h': '',            # Hiphil — Benner does NOT mark causative
    'H': '',            # Hophal — Benner does NOT mark causative passive
    't': 'self~',       # Hithpael — reflexive
    'o': 'much~',       # Polel — intensive (variant)
    'O': 'much~',       # Polal — intensive passive (variant)
    'r': 'self~',       # Hithpolel — reflexive (variant)
    'D': '',            # Nithpael
    'Q': 'much~',       # Pilpel
    'L': 'much~',       # Palal
    'f': 'self~',       # Hithpalpel
    'M': 'much~',       # Poal
    'K': 'much~',       # Pulal
}

# ============================================================
# Person prefixes for verbs
# ============================================================
PERSON_MAP = {
    '1cs': 'I',
    '1cp': 'we',
    '2ms': 'you',
    '2fs': 'you(f)',
    '2mp': 'you(mp)',
    '2fp': 'you(fp)',
    '3ms': 'he',
    '3fs': 'she',
    '3mp': 'they',
    '3fp': 'they(f)',
    '3cp': 'they',
    '2cp': 'you',
}

# ============================================================
# Suffix person map (pronominal suffixes)
# ============================================================
SUFFIX_MAP = {
    'Sp1cs': '~me',
    'Sp1cp': '~us',
    'Sp2ms': '~you',
    'Sp2fs': '~you(f)',
    'Sp2mp': '~you(mp)',
    'Sp2fp': '~you(fp)',
    'Sp3ms': '~him',
    'Sp3fs': '~her',
    'Sp3mp': '~them',
    'Sp3fp': '~them(f)',
    'Sp3cp': '~them',
}

# ============================================================
# Noun state/number markers
# ============================================================
# Gender: m=masc, f=fem, b=both/common
# Number: s=singular, p=plural, d=dual
# State: a=absolute, c=construct

# Words that are always dual in Hebrew despite OSHB coding as plural
ALWAYS_DUAL = {
    'H8064',  # שמים = SKY (always dual)
    'H4325',  # מים = WATER (always dual)
}


def is_prefix_morph(part):
    """Check if a morph part is a prefix (conjunction, article, preposition)
    vs a main word morph (verb, noun, adjective, etc.)."""
    # Prefix parts are short grammatical markers
    # C = conjunction, Td = definite article, R = preposition, Rd = prep+article
    # Ti = interrogative, Tn = negative, To = object marker, Ta = affirmation
    # Main parts: V... (verb 3+ chars), Nc... (noun), Np (proper noun),
    # Aa/Ac (adj), Pp/Pd (pronoun), D (adverb)
    if not part:
        return True
    # Conjunction is always a prefix
    if part == 'C':
        return True
    # Article
    if part in ('Td', 'Tr'):
        return True
    # Preposition as prefix (before a noun/verb)
    if part == 'R':
        return True
    if part == 'Rd':
        return True
    # Suffixes start with S
    if part.startswith('S'):
        return False  # suffix, not prefix
    # Verbs (V + stem + tense + pgn = 4+ chars typically)
    if part.startswith('V') and len(part) >= 3:
        return False
    # Nouns (Nc + gender + number + state = 4+ chars, Np = proper)
    if part.startswith('N') and len(part) >= 2:
        return False
    # Adjectives
    if part.startswith('A') and len(part) >= 2:
        return False
    # Pronouns
    if part.startswith('P') and len(part) >= 2:
        return False
    # Particles with detail (To = object marker, Td = article, etc.)
    if part.startswith('T') and len(part) >= 2:
        # To, Td, Ti, Tn, Ta, Tr are all particles that function as main words
        # when they're the last meaningful part
        return False
    # Adverb
    if part == 'D':
        return False
    # Short standalone conjunction
    if part == 'C' or part == 'Cj':
        return False  # standalone conjunction (like כי)
    return True


def parse_morph(morph):
    """Parse an OSHB morph code into its components.

    Example: HC/Vqw3ms → {prefixes: ['C'], pos: 'V', details: 'qw3ms', suffixes: []}
    Example: HNcmpa → {prefixes: [], pos: 'N', details: 'cmpa', suffixes: []}
    Example: HC/Td/Ncbsa → {prefixes: ['C', 'Td'], pos: 'N', details: 'cbsa', suffixes: []}
    Example: HR/Ncmsc/Sp3ms → {prefixes: ['R'], pos: 'N', details: 'cmsc', suffixes: ['Sp3ms']}
    """
    if not morph or not morph.startswith('H'):
        return None

    result = {
        'raw': morph,
        'prefixes': [],
        'suffixes': [],
        'pos': '',
        'details': '',
    }

    # Strip H prefix
    code = morph[1:]

    # Split on / to get all parts
    parts = code.split('/')

    # Find the main part — it's the first part that is NOT a prefix
    # and NOT a suffix (suffixes start with S)
    main_idx = -1
    for i, p in enumerate(parts):
        if not p:
            continue
        if p.startswith('S'):
            # This is a suffix — everything before it (that isn't prefix) is main
            continue
        if not is_prefix_morph(p):
            main_idx = i
            break

    if main_idx == -1:
        # No clear main part — the last non-S, non-prefix part is the main
        # Or it's all prefixes/particles (like standalone כי = HC)
        for i in range(len(parts) - 1, -1, -1):
            if parts[i] and not parts[i].startswith('S'):
                main_idx = i
                break

    if main_idx == -1:
        result['prefixes'] = parts
        return result

    result['prefixes'] = [p for p in parts[:main_idx] if p]
    main = parts[main_idx]

    # Collect suffixes
    for p in parts[main_idx + 1:]:
        if p:
            result['suffixes'].append(p)

    result['pos'] = main[0] if main else ''
    result['details'] = main[1:] if len(main) > 1 else ''

    return result


def render_verb(details, stem_prefix, root_upper, suffix_str):
    """Render a verb in Benner format based on morph details.

    details: the morph code after 'V' and stem letter, e.g. 'w3ms', 'p3fs', 'rmsa'
    """
    if not details:
        return f'{stem_prefix}{root_upper}(V){suffix_str}'

    tense = details[0] if details else ''
    pgn = details[1:]  # person-gender-number

    # Participle forms
    if tense in ('r', 's'):
        # Active/passive participle
        gender_num = ''
        if len(pgn) >= 2:
            g = pgn[0]  # m/f/b
            n = pgn[1]  # s/p
            # Only show gender/number marker for non-default (masc sing)
            # Benner shows: (f) for fem, (p) for plural, (fs) for fem sing, (fp) for fem plural
            if g == 'f' or n == 'p':
                parts = []
                if g == 'f':
                    parts.append('f')
                if n == 'p':
                    parts.append('p')
                elif n == 's' and g == 'f':
                    parts.append('s')  # Benner shows fs for feminine singular
                # Don't include state (a=absolute, c=construct) in the marker
                gender_num = f'({"".join(parts)})'

        if tense == 's':
            # Passive participle
            return f'{stem_prefix}{root_upper}(V)~ed{gender_num}{suffix_str}'
        else:
            # Active participle
            return f'{stem_prefix}{root_upper}(V)~ing{gender_num}{suffix_str}'

    # Infinitive forms
    if tense in ('c', 'a'):
        if tense == 'c':
            return f'{stem_prefix}{root_upper}(V){suffix_str}'  # Infinitive construct
        else:
            return f'{stem_prefix}{root_upper}(V){suffix_str}'  # Infinitive absolute

    # Imperative
    if tense == 'v':
        person_suffix = ''
        if pgn:
            if pgn.startswith('2mp') or pgn == '2mp':
                person_suffix = '~you(mp)'
            elif pgn.startswith('2fp') or pgn == '2fp':
                person_suffix = '~you(fp)'
            elif pgn.startswith('2ms') or pgn == '2ms':
                person_suffix = ''  # implied
            elif pgn.startswith('2fs') or pgn == '2fs':
                person_suffix = '~you(f)'
        return f'{stem_prefix}{root_upper}(V){person_suffix}{suffix_str}'

    # Perfect, imperfect, waw-consecutive, jussive, cohortative, sequential
    person_code = ''
    if len(pgn) >= 3:
        person_code = pgn[:3]
    elif len(pgn) >= 2:
        person_code = pgn[:2] + 's'  # default singular

    person = PERSON_MAP.get(person_code, '')

    if tense == 'p':
        # Perfect — completed action
        if person == 'he':
            # 3ms perfect = bare root in Benner
            return f'{stem_prefix}{root_upper}(V){suffix_str}'
        elif person in ('she', 'they', 'they(f)'):
            # 3fs/3p perfect gets "did" marker
            return f'{person}~did~{stem_prefix}{root_upper}(V){suffix_str}'
        elif person:
            return f'{person}~{stem_prefix}{root_upper}(V){suffix_str}'
        return f'{stem_prefix}{root_upper}(V){suffix_str}'

    elif tense in ('i', 'w', 'j', 'h', 'q'):
        # Imperfect/waw-consecutive/jussive/cohortative/sequential
        # Benner uses "will" for these (narrative imperfect)
        if person:
            return f'{person}~will~{stem_prefix}{root_upper}(V){suffix_str}'
        return f'{stem_prefix}{root_upper}(V){suffix_str}'

    # Fallback
    if person:
        return f'{person}~{stem_prefix}{root_upper}(V){suffix_str}'
    return f'{stem_prefix}{root_upper}(V){suffix_str}'


def render_noun(details, root_upper, suffix_str, strongs=''):
    """Render a noun in Benner format.

    details: morph code after 'N', e.g. 'cmpa' (common masc plural absolute)
    """
    if not details or len(details) < 2:
        return f'{root_upper}{suffix_str}'

    subtype = details[0]  # c=common, p=proper
    rest = details[1:]

    if subtype == 'p':
        # Proper noun — return as-is (name)
        return f'{root_upper}{suffix_str}'

    # Common noun — check gender, number, state
    gender = rest[0] if len(rest) >= 1 else ''
    number = rest[1] if len(rest) >= 2 else ''
    state = rest[2] if len(rest) >= 3 else ''

    plural = ''
    if number == 'p':
        # Check if this word is always dual in Hebrew
        if strongs in ALWAYS_DUAL:
            plural = '~s2'
        else:
            plural = '~s'
    elif number == 'd':
        plural = '~s2'  # dual

    return f'{root_upper}{plural}{suffix_str}'


def render_adjective(details, root_upper, suffix_str):
    """Render an adjective."""
    if not details:
        return f'{root_upper}{suffix_str}'

    # Similar to nouns
    gender = details[0] if len(details) >= 1 else ''
    number = details[1] if len(details) >= 2 else ''
    state = details[2] if len(details) >= 3 else ''

    plural = ''
    if number == 'p':
        plural = '~s'

    return f'{root_upper}{plural}{suffix_str}'


def render_word(morph, root_name, lemma='', strongs=''):
    """Render a single word in Benner mechanical format.

    Args:
        morph: OSHB morph code (e.g. 'HC/Vqw3ms')
        root_name: The AHLB root meaning in English (e.g. 'SAY')
        lemma: OSHB lemma for prefix detection (e.g. 'c/559')
        strongs: Strong's number (e.g. 'H8064') for special cases
    Returns:
        Mechanical translation string (e.g. 'and~he~will~SAY(V)')
    """
    parsed = parse_morph(morph)
    if not parsed:
        return root_name.upper().replace(' ', '.') if root_name else '?'

    root_upper = root_name.upper().replace(' ', '.') if root_name else '?'

    if root_upper == '?':
        return '?'

    # Build prefix string from morph prefixes
    # First, figure out which lemma prefixes correspond to which morph prefixes
    lemma_parts = lemma.split('/')[:-1] if lemma else []  # all except root
    lemma_idx = 0  # track which lemma prefix we've consumed

    prefix_parts = []
    for pfx in parsed['prefixes']:
        if pfx == 'C':
            prefix_parts.append('and')
            # Consume the matching 'c' in lemma
            if lemma_idx < len(lemma_parts) and lemma_parts[lemma_idx].strip() == 'c':
                lemma_idx += 1
        elif pfx == 'Td':
            prefix_parts.append('the')
            if lemma_idx < len(lemma_parts) and lemma_parts[lemma_idx].strip() == 'd':
                lemma_idx += 1
        elif pfx == 'Rd':
            # Preposition + article — get preposition from next lemma prefix
            prep = 'in'  # default
            while lemma_idx < len(lemma_parts):
                lp = lemma_parts[lemma_idx].strip()
                lemma_idx += 1
                if lp in PREFIX_MAP and lp not in ('c', 'd'):
                    # This is our preposition
                    prep = PREFIX_MAP[lp]
                    break
                elif lp == 'd':
                    # This is the article part of Rd, skip
                    continue
            prefix_parts.append(f'{prep}~the')
        elif pfx == 'R':
            # Preposition — get from lemma prefix
            prep_found = False
            while lemma_idx < len(lemma_parts):
                lp = lemma_parts[lemma_idx].strip()
                lemma_idx += 1
                if lp in PREFIX_MAP and lp != 'c':
                    prefix_parts.append(PREFIX_MAP[lp])
                    prep_found = True
                    break
            if not prep_found:
                prefix_parts.append('to')  # default preposition

    # Build suffix string from morph suffixes
    suffix_str = ''
    for sfx in parsed['suffixes']:
        if sfx in SUFFIX_MAP:
            suffix_str += SUFFIX_MAP[sfx]
        elif sfx.startswith('Sp'):
            # Match suffix person codes
            for k, v in SUFFIX_MAP.items():
                if sfx == k:
                    suffix_str += v
                    break
            else:
                # Try prefix match
                for k, v in SUFFIX_MAP.items():
                    if sfx.startswith(k[:5]):
                        suffix_str += v
                        break

    pos = parsed['pos']
    details = parsed['details']

    # Route by part of speech
    if pos == 'V':
        # Verb
        stem = details[0] if details else 'q'
        stem_prefix = VERB_STEM_PREFIX.get(stem, '')
        verb_details = details[1:] if len(details) > 1 else ''
        rendered = render_verb(verb_details, stem_prefix, root_upper, suffix_str)
    elif pos == 'N':
        rendered = render_noun(details, root_upper, suffix_str, strongs=strongs)
    elif pos == 'A':
        rendered = render_adjective(details, root_upper, suffix_str)
    elif pos == 'P':
        # Pronoun
        rendered = f'{root_upper}{suffix_str}'
    elif pos == 'T':
        # Particle (את, אשר, etc.)
        rendered = f'{root_upper}{suffix_str}'
    elif pos == 'R':
        # Standalone preposition
        rendered = f'{root_upper}{suffix_str}'
    elif pos == 'D':
        # Adverb
        rendered = f'{root_upper}{suffix_str}'
    elif pos == 'C':
        # Conjunction
        rendered = f'{root_upper}{suffix_str}'
    elif pos == 'S':
        # Suffix only
        if details and f'S{details}' in SUFFIX_MAP:
            rendered = SUFFIX_MAP[f'S{details}']
        else:
            rendered = suffix_str or '?'
    else:
        rendered = f'{root_upper}{suffix_str}'

    # Prepend prefix parts with tildes
    if prefix_parts:
        prefix_str = '~'.join(prefix_parts)
        return f'{prefix_str}~{rendered}'

    return rendered


# ============================================================
# Special handling for perfect 3ms verbs
# ============================================================
# Benner sometimes renders 3ms perfect as bare root (SHAPE),
# sometimes as "he~did~ROOT" — depends on narrative context.
# In waw-consecutive chains, the first verb often gets
# the person prefix. We'll follow the simpler convention:
# 3ms perfect in isolation = bare ROOT(V)
# 3ms perfect with other person = person prefix
# This matches what we see in Genesis 1.
