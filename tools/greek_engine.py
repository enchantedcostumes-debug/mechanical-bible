#!/usr/bin/env python3
"""
Greek Mechanical Translation Engine - Mechanical Bible
========================================================
Generates mechanical translations from Robinson morphology codes
for the Greek New Testament.

Robinson morphology format:
  POS-TENSE/VOICE/MOOD-PERSON/NUMBER or POS-CASE/NUMBER/GENDER

  Verbs:  V-AAI-3S = Verb, Aorist Active Indicative, 3rd Singular
  Nouns:  N-NSF = Noun, Nominative Singular Feminine
  Articles: T-NSM = Article (The), Nominative Singular Masculine
  Pronouns: P-1NS = Pronoun, 1st person Nominative Singular
  Conjunctions: CONJ
  Prepositions: PREP
  Adverbs: ADV

Output follows the same tilde-connected format as Hebrew:
  and~he~did~BEGET(V) the~WORD BEGINNING~to

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re

# ============================================================
# Case suffixes for nouns/adjectives
# ============================================================
CASE_SUFFIX = {
    'N': '',      # Nominative — subject (bare)
    'G': '~of',   # Genitive — possession/source
    'D': '~to',   # Dative — indirect object
    'A': '',      # Accusative — direct object (bare)
    'V': '!',     # Vocative — address
}

# ============================================================
# Person map for verbs and pronouns
# ============================================================
PERSON_MAP = {
    '1S': 'I',
    '1P': 'we',
    '2S': 'you',
    '2P': 'you~all',
    '3S': 'he',
    '3P': 'they',
}

# ============================================================
# Pronoun accusative/object forms
# ============================================================
PRONOUN_OBJ = {
    '1S': 'me',
    '1P': 'us',
    '2S': 'you',
    '2P': 'you~all',
    '3S': 'him',    # default masc; fem handled separately
    '3P': 'them',
}


def parse_robinson(morph):
    """Parse a Robinson morphology code into components.

    Returns dict with keys: pos, tense, voice, mood, person, number,
                           case, gender, extra
    """
    if not morph:
        return None

    result = {
        'raw': morph,
        'pos': '',
        'tense': '',
        'voice': '',
        'mood': '',
        'person': '',
        'number': '',
        'case': '',
        'gender': '',
        'extra': '',
    }

    # Handle simple POS codes first
    if morph in ('CONJ', 'PREP', 'ADV', 'PRT', 'INJ', 'HEB', 'ARAM'):
        result['pos'] = morph
        return result

    parts = morph.split('-')
    pos = parts[0] if parts else ''
    result['pos'] = pos

    # Verb: V-TENSE/VOICE/MOOD-PERSON/NUMBER
    if pos == 'V' and len(parts) >= 2:
        tvm = parts[1]  # e.g. AAI, PAP, PAN, etc.
        if len(tvm) >= 1:
            result['tense'] = tvm[0]  # A=Aorist, P=Present, I=Imperfect, F=Future, R=peRfect, L=pLuperfect
        if len(tvm) >= 2:
            result['voice'] = tvm[1]  # A=Active, M=Middle, P=Passive, E=Either(mid/pass), D=Deponent
        if len(tvm) >= 3:
            result['mood'] = tvm[2]  # I=Indicative, S=Subjunctive, M=Imperative, P=Participle, N=Infinitive, O=Optative

        if len(parts) >= 3:
            pgn = parts[2]  # e.g. 3S, 1P, NSM (for participles)
            if len(pgn) >= 2 and pgn[0].isdigit():
                # Person+Number: 3S, 1P, etc.
                result['person'] = pgn[0]
                result['number'] = pgn[1]
            elif len(pgn) >= 3:
                # Participle case/number/gender: NSM, GSF, etc.
                result['case'] = pgn[0]
                result['number'] = pgn[1]
                result['gender'] = pgn[2] if len(pgn) > 2 else ''

        return result

    # Article: T-CASE/NUMBER/GENDER
    if pos == 'T' and len(parts) >= 2:
        cng = parts[1]
        if len(cng) >= 1:
            result['case'] = cng[0]
        if len(cng) >= 2:
            result['number'] = cng[1]
        if len(cng) >= 3:
            result['gender'] = cng[2]
        return result

    # Noun: N-CASE/NUMBER/GENDER[-P for proper, -T for title]
    if pos == 'N' and len(parts) >= 2:
        cng = parts[1]
        if len(cng) >= 1:
            result['case'] = cng[0]
        if len(cng) >= 2:
            result['number'] = cng[1]
        if len(cng) >= 3:
            result['gender'] = cng[2]
        if len(parts) >= 3:
            result['extra'] = parts[2]  # P=proper, T=title, LG=location gentilic
        return result

    # Adjective: A-CASE/NUMBER/GENDER
    if pos == 'A' and len(parts) >= 2:
        cng = parts[1]
        if len(cng) >= 1:
            result['case'] = cng[0]
        if len(cng) >= 2:
            result['number'] = cng[1]
        if len(cng) >= 3:
            result['gender'] = cng[2]
        return result

    # Pronoun types: P=personal, R=relative, D=demonstrative, X=interrogative/indefinite
    if pos in ('P', 'R', 'D', 'C', 'F', 'S', 'Q', 'I', 'X', 'K') and len(parts) >= 2:
        pgn = parts[1]
        # Could be person-first (P-1NS) or case-first (R-NSM)
        if len(pgn) >= 1 and pgn[0].isdigit():
            # Person-first: P-1NS, P-3ASM
            result['person'] = pgn[0]
            if len(pgn) >= 2:
                result['case'] = pgn[1]
            if len(pgn) >= 3:
                result['number'] = pgn[2]
            if len(pgn) >= 4:
                result['gender'] = pgn[3]
        else:
            # Case-first: R-NSM, D-GSF
            if len(pgn) >= 1:
                result['case'] = pgn[0]
            if len(pgn) >= 2:
                result['number'] = pgn[1]
            if len(pgn) >= 3:
                result['gender'] = pgn[2]
        return result

    return result


def render_greek_verb(parsed, root_upper):
    """Render a Greek verb in mechanical format."""
    tense = parsed['tense']
    voice = parsed['voice']
    mood = parsed['mood']
    person = parsed['person']
    number = parsed['number']

    person_key = f'{person}{number}' if person and number else ''
    person_label = PERSON_MAP.get(person_key, '')

    # Voice markers
    passive = voice in ('P',)         # Passive
    middle = voice in ('M', 'D')       # Middle or Deponent
    either_mp = voice in ('E',)        # Either middle or passive

    # Mood handling
    if mood == 'N':
        # Infinitive — no person
        if tense == 'P':
            # Present infinitive: DO(V)~ing
            return f'{root_upper}(V)~ing'
        elif tense == 'A':
            # Aorist infinitive: DO(V)
            if passive:
                return f'be~{root_upper}(V)~ed'
            if middle:
                return f'{root_upper}(V)~self'
            return f'{root_upper}(V)'
        elif tense == 'R':
            return f'have~{root_upper}(V)~ed'
        return f'{root_upper}(V)'

    if mood == 'M':
        # Imperative — command
        if passive:
            return f'be~{root_upper}(V)~ed!'
        if middle:
            return f'{root_upper}(V)~self!'
        return f'{root_upper}(V)!'

    if mood == 'P':
        # Participle — verbal adjective
        case_suffix = CASE_SUFFIX.get(parsed['case'], '')
        plural = '~s' if parsed['number'] == 'P' else ''
        if tense in ('P', 'I'):
            # Present/Imperfect participle → ~ing
            if passive or either_mp:
                return f'be~{root_upper}(V)~ed{plural}{case_suffix}'
            if middle:
                return f'{root_upper}(V)~ing~self{plural}{case_suffix}'
            return f'{root_upper}(V)~ing{plural}{case_suffix}'
        elif tense == 'A':
            # Aorist participle → having done
            if passive:
                return f'{root_upper}(V)~ed{plural}{case_suffix}'
            if middle:
                return f'{root_upper}(V)~ed~self{plural}{case_suffix}'
            return f'{root_upper}(V)~ed{plural}{case_suffix}'
        elif tense == 'R':
            # Perfect participle
            if passive:
                return f'be~{root_upper}(V)~ed{plural}{case_suffix}'
            return f'have~{root_upper}(V)~ed{plural}{case_suffix}'
        return f'{root_upper}(V)~ing{plural}{case_suffix}'

    if mood == 'O':
        # Optative — wish
        if person_label:
            return f'{person_label}~may~{root_upper}(V)'
        return f'may~{root_upper}(V)'

    if mood == 'S':
        # Subjunctive
        if person_label:
            if passive:
                return f'{person_label}~might~be~{root_upper}(V)~ed'
            if middle:
                return f'{person_label}~might~{root_upper}(V)~self'
            return f'{person_label}~might~{root_upper}(V)'
        return f'might~{root_upper}(V)'

    # Indicative (mood == 'I' or default)
    if tense == 'A':
        # Aorist — past/completed
        if passive:
            if person_label:
                return f'{person_label}~was~{root_upper}(V)~ed'
            return f'was~{root_upper}(V)~ed'
        if middle:
            if person_label:
                return f'{person_label}~did~{root_upper}(V)~self'
            return f'did~{root_upper}(V)~self'
        if person_label:
            return f'{person_label}~did~{root_upper}(V)'
        return f'did~{root_upper}(V)'

    elif tense == 'P':
        # Present — only 3rd person singular gets ~s
        third_s = person == '3' and number == 'S'
        verb_suffix = '~s' if third_s else ''
        if passive:
            if person_label:
                return f'{person_label}~is~{root_upper}(V)~ed'
            return f'is~{root_upper}(V)~ed'
        if middle:
            if person_label:
                return f'{person_label}~{root_upper}(V){verb_suffix}~self'
            return f'{root_upper}(V){verb_suffix}~self'
        if person_label:
            return f'{person_label}~{root_upper}(V){verb_suffix}'
        return f'{root_upper}(V){verb_suffix}'

    elif tense == 'I':
        # Imperfect — past continuous
        if passive:
            if person_label:
                return f'{person_label}~was~be~{root_upper}(V)~ed'
            return f'was~be~{root_upper}(V)~ed'
        if middle:
            if person_label:
                return f'{person_label}~was~{root_upper}(V)~ing~self'
            return f'was~{root_upper}(V)~ing~self'
        if person_label:
            return f'{person_label}~was~{root_upper}(V)~ing'
        return f'was~{root_upper}(V)~ing'

    elif tense == 'F':
        # Future
        if passive:
            if person_label:
                return f'{person_label}~will~be~{root_upper}(V)~ed'
            return f'will~be~{root_upper}(V)~ed'
        if middle:
            if person_label:
                return f'{person_label}~will~{root_upper}(V)~self'
            return f'will~{root_upper}(V)~self'
        if person_label:
            return f'{person_label}~will~{root_upper}(V)'
        return f'will~{root_upper}(V)'

    elif tense == 'R':
        # Perfect
        if passive:
            if person_label:
                return f'{person_label}~has~been~{root_upper}(V)~ed'
            return f'has~been~{root_upper}(V)~ed'
        if person_label:
            return f'{person_label}~has~{root_upper}(V)~ed'
        return f'has~{root_upper}(V)~ed'

    elif tense == 'L':
        # Pluperfect
        if person_label:
            return f'{person_label}~had~{root_upper}(V)~ed'
        return f'had~{root_upper}(V)~ed'

    # Fallback
    if person_label:
        return f'{person_label}~{root_upper}(V)'
    return f'{root_upper}(V)'


def render_greek_noun(parsed, root_upper):
    """Render a Greek noun in mechanical format."""
    case = parsed.get('case', '')
    number = parsed.get('number', '')

    plural = '~s' if number == 'P' else ''
    case_suffix = CASE_SUFFIX.get(case, '')

    return f'{root_upper}{plural}{case_suffix}'


def render_greek_article(parsed):
    """Render a Greek definite article."""
    case = parsed.get('case', '')
    case_suffix = CASE_SUFFIX.get(case, '')
    return f'the{case_suffix}'


def render_greek_pronoun(parsed, root_upper):
    """Render a Greek pronoun."""
    pos = parsed['pos']
    person = parsed.get('person', '')
    case = parsed.get('case', '')
    number = parsed.get('number', '')
    gender = parsed.get('gender', '')

    person_key = f'{person}{number}' if person and number else ''

    # Personal pronouns with case
    if pos == 'P' and person_key:
        if case in ('N', 'V'):
            # Nominative — subject form
            return PERSON_MAP.get(person_key, root_upper)
        elif case in ('A',):
            # Accusative — object form
            obj = PRONOUN_OBJ.get(person_key, root_upper.lower())
            return obj
        elif case == 'G':
            # Genitive — possessive
            obj = PRONOUN_OBJ.get(person_key, root_upper.lower())
            return f'{obj}~of'
        elif case == 'D':
            # Dative
            obj = PRONOUN_OBJ.get(person_key, root_upper.lower())
            return f'{obj}~to'
        return PERSON_MAP.get(person_key, root_upper)

    # Relative pronoun (R): who, which, that
    if pos == 'R':
        case_suffix = CASE_SUFFIX.get(case, '')
        return f'{root_upper.lower()}{case_suffix}'

    # Demonstrative pronoun (D): this, that
    if pos == 'D':
        case_suffix = CASE_SUFFIX.get(case, '')
        plural = '~s' if number == 'P' else ''
        return f'{root_upper.lower()}{plural}{case_suffix}'

    # Interrogative (X): who?, what?
    if pos == 'X':
        case_suffix = CASE_SUFFIX.get(case, '')
        return f'{root_upper.lower()}?{case_suffix}'

    # Reflexive, possessive, etc. — just use root
    case_suffix = CASE_SUFFIX.get(case, '')
    return f'{root_upper.lower()}{case_suffix}'


def render_greek_word(morph, root_name, lemma='', strongs=''):
    """Render a single Greek word in mechanical format.

    Args:
        morph: Robinson morphology code (e.g. 'V-AAI-3S', 'N-NSF')
        root_name: The root meaning in English (e.g. 'BEGET', 'BOOK')
        lemma: Greek lemma (dictionary form)
        strongs: Strong's G-number
    Returns:
        Mechanical translation string (e.g. 'he~did~BEGET(V)')
    """
    if not morph:
        return root_name.upper().replace(' ', '.') if root_name else '?'

    parsed = parse_robinson(morph)
    if not parsed:
        return root_name.upper().replace(' ', '.') if root_name else '?'

    root_upper = root_name.upper().replace(' ', '.') if root_name else '?'
    pos = parsed['pos']

    if pos == 'V':
        return render_greek_verb(parsed, root_upper)

    elif pos == 'N':
        return render_greek_noun(parsed, root_upper)

    elif pos == 'T':
        return render_greek_article(parsed)

    elif pos in ('CONJ',):
        return root_upper.lower()

    elif pos in ('PREP',):
        return root_upper.lower()

    elif pos in ('ADV',):
        return root_upper.lower()

    elif pos in ('PRT', 'INJ'):
        return root_upper.lower()

    elif pos in ('P', 'R', 'D', 'X', 'S', 'F', 'Q', 'I', 'K', 'C'):
        return render_greek_pronoun(parsed, root_upper)

    elif pos == 'A':
        # Adjective — similar to noun
        case = parsed.get('case', '')
        number = parsed.get('number', '')
        plural = '~s' if number == 'P' else ''
        case_suffix = CASE_SUFFIX.get(case, '')
        return f'{root_upper}{plural}{case_suffix}'

    # Fallback
    return root_upper
