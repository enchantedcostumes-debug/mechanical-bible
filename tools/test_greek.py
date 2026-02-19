#!/usr/bin/env python3
"""
Test Greek mechanical translation engine against known grammar patterns.
Tests MUST pass before any generation or push.
Derived from TAGNT morphology codes + known Greek grammar.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from greek_engine import render_greek_word

# ============================================================
# Tests derived from Matthew 1:1-2 and John 1:1-3 TAGNT data
# Format: (morph_code, root_name, expected_output)
# ============================================================
TESTS = [
    # ===================== NOUNS =====================

    # Βίβλος (N-NSF) = Nominative Singular Feminine → bare root
    ('N-NSF', 'BOOK', 'BOOK'),

    # γενέσεως (N-GSF) = Genitive Singular Feminine → ~of
    ('N-GSF', 'ORIGIN', 'ORIGIN~of'),

    # Ἰησοῦ (N-GSM-P) = Genitive Singular Masculine Proper → ~of (name)
    ('N-GSM-P', 'YESHUA', 'YESHUA~of'),

    # Χριστοῦ (N-GSM-T) = Genitive Singular Masculine Title → ~of
    ('N-GSM-T', 'ANOINTED', 'ANOINTED~of'),

    # υἱοῦ (N-GSM) = Genitive Singular Masculine → ~of
    ('N-GSM', 'SON', 'SON~of'),

    # Nominative Plural Masculine
    ('N-NPM', 'BROTHER', 'BROTHER~s'),

    # Accusative Singular Masculine → bare (direct object)
    ('N-ASM', 'SON', 'SON'),

    # Dative Singular Masculine → ~to
    ('N-DSM', 'MASTER', 'MASTER~to'),

    # Dative Singular Feminine (John 1:1 — ἀρχῇ)
    ('N-DSF', 'BEGINNING', 'BEGINNING~to'),

    # Nominative Singular Masculine (John 1:1 — λόγος)
    ('N-NSM', 'WORD', 'WORD'),

    # Accusative Singular Masculine Title (John 1:1 — θεόν)
    ('N-ASM-T', 'GOD', 'GOD'),

    # Accusative Plural Masculine
    ('N-APM', 'BROTHER', 'BROTHER~s'),

    # Genitive Plural Masculine
    ('N-GPM', 'DISCIPLE', 'DISCIPLE~s~of'),

    # Dative Plural Masculine
    ('N-DPM', 'DISCIPLE', 'DISCIPLE~s~to'),

    # Vocative Singular Masculine
    ('N-VSM', 'MASTER', 'MASTER!'),

    # ===================== VERBS =====================

    # Aorist Active Indicative 3S (Matt 1:2 — ἐγέννησεν)
    ('V-AAI-3S', 'BEGET', 'he~did~BEGET(V)'),

    # Imperfect Active Indicative 3S (John 1:1 — ἦν)
    ('V-IAI-3S', 'EXIST', 'he~was~EXIST(V)~ing'),

    # Present Active Indicative 3S
    ('V-PAI-3S', 'SAY', 'he~SAY(V)~s'),

    # Present Active Indicative 1S
    ('V-PAI-1S', 'SAY', 'I~SAY(V)'),

    # Future Active Indicative 3S
    ('V-FAI-3S', 'SAY', 'he~will~SAY(V)'),

    # Aorist Active Indicative 3P (plural)
    ('V-AAI-3P', 'SAY', 'they~did~SAY(V)'),

    # Aorist Active Indicative 1S
    ('V-AAI-1S', 'SEE', 'I~did~SEE(V)'),

    # Present Active Participle Nominative Singular Masculine
    ('V-PAP-NSM', 'SAY', 'SAY(V)~ing'),

    # Aorist Passive Indicative 3S
    ('V-API-3S', 'RAISE', 'he~was~RAISE(V)~ed'),

    # Perfect Active Indicative 3S
    ('V-RAI-3S', 'WRITE', 'he~has~WRITE(V)~ed'),

    # Aorist Middle Indicative 3S
    ('V-AMI-3S', 'ANSWER', 'he~did~ANSWER(V)~self'),

    # Aorist Active Subjunctive 3S
    ('V-AAS-3S', 'GIVE', 'he~might~GIVE(V)'),

    # Present Active Imperative 2S
    ('V-PAM-2S', 'FOLLOW', 'FOLLOW(V)!'),

    # Aorist Active Imperative 2S
    ('V-AAM-2S', 'COME', 'COME(V)!'),

    # Aorist Active Infinitive
    ('V-AAN', 'DO', 'DO(V)'),

    # Present Active Infinitive
    ('V-PAN', 'DO', 'DO(V)~ing'),

    # Present Middle/Passive Indicative 3S
    ('V-PMI-3S', 'COME', 'he~COME(V)~s~self'),

    # Present Passive Indicative 3S
    ('V-PPI-3S', 'CALL', 'he~is~CALL(V)~ed'),

    # ===================== ARTICLES =====================

    # Definite article — Nominative Singular Masculine
    ('T-NSM', 'THE', 'the'),

    # Definite article — Accusative Singular Masculine
    ('T-ASM', 'THE', 'the'),

    # Definite article — Genitive Singular Feminine
    ('T-GSF', 'THE', 'the~of'),

    # ===================== CONJUNCTIONS =====================

    # καί
    ('CONJ', 'AND', 'and'),

    # δέ
    ('CONJ', 'BUT', 'but'),

    # ===================== PREPOSITIONS =====================

    # ἐν (John 1:1)
    ('PREP', 'IN', 'in'),

    # πρός (John 1:1)
    ('PREP', 'TOWARD', 'toward'),

    # ἐκ
    ('PREP', 'FROM', 'from'),

    # ===================== ADVERBS =====================

    ('ADV', 'NOT', 'not'),

    # ===================== PRONOUNS =====================

    # Personal pronoun — Nominative Singular 1st person
    ('P-1NS', 'I', 'I'),

    # Personal pronoun — Accusative Singular 3rd person masculine
    ('P-3ASM', 'HE', 'him'),

    # Personal pronoun — Genitive Singular 3rd person masculine
    ('P-3GSM', 'HE', 'him~of'),

    # Demonstrative pronoun
    ('D-NSM', 'THIS', 'this'),

    # Relative pronoun — Nominative Singular Masculine
    ('R-NSM', 'WHO', 'who'),

    # Interrogative pronoun
    ('X-NSM', 'WHO', 'who?'),
]


def main():
    passed = 0
    failed = 0
    errors = []

    for morph, root, expected in TESTS:
        result = render_greek_word(morph, root)
        if result == expected:
            passed += 1
        else:
            failed += 1
            errors.append(f'  FAIL: morph={morph} root={root} -> got "{result}" expected "{expected}"')

    total = passed + failed
    print(f'Greek Mechanical Translation Tests: {passed}/{total} passed')
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
