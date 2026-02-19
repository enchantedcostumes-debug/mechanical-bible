#!/usr/bin/env python3
"""
TRANSLATE FROM PATTERNS - Mechanical Bible
=============================================
Translates the remaining 48,000+ words that Benner's AHLB doesn't
directly cover, by using Hebrew grammar patterns + his root definitions.

Categories handled:
1. PRONOUNS (אני, הוא, היא, אתה, אנחנו, etc.)
2. VERB CONJUGATIONS (ויאמרו, ויבא, ותאמר, etc. → root verb + tense)
3. PREPOSITION+SUFFIX (לו, להם, אתו, בו, עליו, etc.)
4. PROPER NAMES (יהודה, ירושלם, יעקב, דויד, etc.)
5. CONSTRUCT FORMS (בני, אלהי, etc.)
6. COMMON PARTICLES (כה, או, כי, אם, גם, etc.)

Uses Benner's methodology: concrete meanings, no theological abstractions.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'

# ============================================================
# 1. PRONOUNS
# ============================================================
PRONOUNS = {
    'אני': ('I', 'pronoun'),
    'אנכי': ('I', 'pronoun'),
    'אתה': ('you (m.sg.)', 'pronoun'),
    'את': None,  # Skip - already handled as object marker
    'הוא': ('he', 'pronoun'),
    'היא': ('she', 'pronoun'),
    'אנחנו': ('we', 'pronoun'),
    'אנו': ('we', 'pronoun'),
    'אתם': ('you (m.pl.)', 'pronoun'),
    'אתן': ('you (f.pl.)', 'pronoun'),
    'הם': ('they (m.)', 'pronoun'),
    'המה': ('they (m.)', 'pronoun'),
    'הנה': ('they (f.)', 'pronoun'),
    'הן': ('they (f.)', 'pronoun'),
    'זה': ('this (m.)', 'pronoun'),
    'זאת': ('this (f.)', 'pronoun'),
    'זו': ('this (f.)', 'pronoun'),
    'אלה': ('these', 'pronoun'),
    'אלו': ('these', 'pronoun'),
    'ההוא': ('that (m.)', 'pronoun'),
    'ההיא': ('that (f.)', 'pronoun'),
    'האלה': ('these', 'pronoun'),
    'מי': ('who', 'pronoun'),
    'מה': ('what', 'pronoun'),
    'אשר': ('which/that', 'relative'),
    'כל': ('all/every', 'adjective'),
    'עוד': ('still/again', 'adverb'),
    'שם': ('there', 'adverb'),
    'פה': ('here', 'adverb'),
    'הנה': ('behold', 'interjection'),
    'עתה': ('now', 'adverb'),
    'מאד': ('exceedingly', 'adverb'),
    'גם': ('also', 'conjunction'),
    'או': ('or', 'conjunction'),
    'אם': ('if', 'conjunction'),
    'כן': ('so/thus', 'adverb'),
    'לא': ('not', 'adverb'),
    'אין': ('there is not', 'adverb'),
    'לכן': ('therefore', 'conjunction'),
    'כה': ('thus/so', 'adverb'),
    'אל': ('to/toward', 'preposition'),
    'על': ('upon/over', 'preposition'),
    'עד': ('until/unto', 'preposition'),
    'אחרי': ('after/behind', 'preposition'),
    'לפני': ('before/in front of', 'preposition'),
    'תחת': ('under/instead of', 'preposition'),
    'בתוך': ('in the midst of', 'preposition'),
    'אצל': ('beside/near', 'preposition'),
    'סביב': ('around/surrounding', 'preposition'),
    'למען': ('for the sake of', 'preposition'),
    'עם': ('with', 'preposition'),
    'את': None,  # Skip
}

# ============================================================
# 2. PRONOMINAL SUFFIXES ON PREPOSITIONS
# ============================================================
PREP_SUFFIX = {
    # ל (to) + suffixes
    'לו': 'to him',
    'לה': 'to her',
    'לי': 'to me',
    'לך': 'to you (m.)',
    'לנו': 'to us',
    'להם': 'to them (m.)',
    'להן': 'to them (f.)',
    'לכם': 'to you (m.pl.)',
    'לכן': 'to you (f.pl.)',
    # ב (in) + suffixes
    'בו': 'in him/it',
    'בה': 'in her/it',
    'בי': 'in me',
    'בך': 'in you (m.)',
    'בם': 'in them',
    'בנו': 'in us',
    # על (upon) + suffixes
    'עלי': 'upon me',
    'עליו': 'upon him',
    'עליה': 'upon her',
    'עליך': 'upon you',
    'עלינו': 'upon us',
    'עליהם': 'upon them',
    # אל (to) + suffixes
    'אלי': 'to me',
    'אליו': 'to him',
    'אליה': 'to her',
    'אליך': 'to you',
    'אלינו': 'to us',
    'אליהם': 'to them',
    # עם (with) + suffixes
    'עמו': 'with him',
    'עמי': 'with me',
    'עמך': 'with you',
    'עמנו': 'with us',
    'עמהם': 'with them',
    # את (with/object) + suffixes
    'אתו': 'him (object)',
    'אתי': 'me (object)',
    'אתך': 'you (object)',
    'אתנו': 'us (object)',
    'אתכם': 'you all (object)',
    # מן (from) + suffixes
    'ממנו': 'from him/it',
    'ממני': 'from me',
    'ממך': 'from you',
    'מהם': 'from them',
    # כ (like) + suffixes
    'כמו': 'like him',
    'כמוך': 'like you',
}

# ============================================================
# 3. PROPER NAMES (transliterated, not translated)
# ============================================================
PROPER_NAMES = {
    'יהודה': 'Yehudah',
    'ירושלם': 'Yerushalem',
    'ירושלים': 'Yerushalem',
    'יעקב': 'Ya\'aqov',
    'דויד': 'David',
    'דוד': 'David',
    'משה': 'Mosheh',
    'אברהם': 'Avraham',
    'יצחק': 'Yits\'hhaq',
    'שמואל': 'Shemu\'el',
    'שלמה': 'Shelomoh',
    'יוסף': 'Yoseph',
    'אהרן': 'Aharon',
    'בנימן': 'Binyamin',
    'ראובן': 'Re\'uven',
    'שמעון': 'Shim\'on',
    'לוי': 'Lewi',
    'יששכר': 'Yissaskar',
    'זבולן': 'Zevulun',
    'דן': 'Dan',
    'נפתלי': 'Naphtali',
    'גד': 'Gad',
    'אשר': None,  # Skip - also means "which/that"
    'מנשה': 'Menashsheh',
    'אפרים': 'Ephrayim',
    'שאול': 'Sha\'ul',
    'פרעה': 'Par\'oh',
    'יהושע': 'Yehoshu\'a',
    'ישראל': 'Yisra\'el',
    'מצרים': 'Mitsrayim',
    'בבל': 'Bavel',
    'אדום': 'Edom',
    'מואב': 'Mo\'av',
    'אשור': 'Ashshur',
    'כנען': 'Kena\'an',
    'צור': 'Tsor',
    'צידון': 'Tsidon',
    'עמון': 'Ammon',
    'פלשתים': 'Pelishtim',
    'ארם': 'Aram',
    'סיני': 'Sinay',
    'ציון': 'Tsiyyon',
    'לבנון': 'Levanon',
    'ירדן': 'Yarden',
    'שכם': 'Shekhem',
    'חברון': 'Hhevron',
    'בית': 'Beyt',
    'גלעד': 'Gil\'ad',
    'נח': 'No\'ahh',
    'אדם': None,  # Skip - also means "man/human"
    'אליהו': 'Eliyahu',
    'ישעיהו': 'Yesha\'yahu',
    'ירמיהו': 'Yirmeyahu',
    'יחזקאל': 'Yehhezeq\'el',
    'עזרא': 'Ezra',
    'נחמיה': 'Nehhemyah',
    'איוב': 'Iyyov',
    'רות': 'Rut',
    'אסתר': 'Ester',
    'דניאל': 'Daniy\'el',
}

# ============================================================
# 4. COMMON VERB ROOTS (for conjugation extraction)
# ============================================================
# Format: root_letters -> (benner_mechanical, benner_rmt_base)
VERB_ROOTS = {
    'אמר': ('SAY', 'said'),
    'בוא': ('COME', 'came'),
    'נתן': ('GIVE', 'gave'),
    'עשה': ('DO', 'made'),
    'הלך': ('WALK', 'walked'),
    'ראה': ('SEE', 'saw'),
    'ידע': ('KNOW', 'knew'),
    'שמע': ('HEAR', 'heard'),
    'דבר': ('SPEAK', 'spoke'),
    'לקח': ('TAKE', 'took'),
    'ישב': ('SIT', 'sat/dwelt'),
    'שלח': ('SEND', 'sent'),
    'שוב': ('TURN', 'turned'),
    'קרא': ('CALL', 'called'),
    'עלה': ('GO.UP', 'went up'),
    'ירד': ('GO.DOWN', 'went down'),
    'יצא': ('GO.OUT', 'went out'),
    'מות': ('DIE', 'died'),
    'עמד': ('STAND', 'stood'),
    'שים': ('SET', 'set'),
    'אכל': ('EAT', 'ate'),
    'נפל': ('FALL', 'fell'),
    'נשא': ('LIFT', 'lifted'),
    'כתב': ('WRITE', 'wrote'),
    'ילד': ('BIRTH', 'birthed'),
    'בנה': ('BUILD', 'built'),
    'שמר': ('GUARD', 'guarded'),
    'עבד': ('SERVE', 'served'),
    'מצא': ('FIND', 'found'),
    'קום': ('RISE', 'rose'),
    'מלך': ('REIGN', 'reigned'),
    'נכה': ('STRIKE', 'struck'),
    'זרע': ('SOW', 'sowed'),
    'חיה': ('LIVE', 'lived'),
    'ברך': ('KNEEL', 'knelt/blessed'),
    'שפט': ('JUDGE', 'judged'),
    'צוה': ('CHARGE', 'charged'),
    'פנה': ('FACE', 'faced'),
    'סור': ('TURN.ASIDE', 'turned aside'),
    'ברח': ('FLEE', 'fled'),
    'חטא': ('ERR', 'erred'),
    'רדף': ('PURSUE', 'pursued'),
    'שבע': ('SWEAR', 'swore'),
    'כרת': ('CUT', 'cut'),
    'אסף': ('GATHER', 'gathered'),
    'חנה': ('CAMP', 'camped'),
    'סבב': ('SURROUND', 'surrounded'),
    'פקד': ('VISIT', 'visited/appointed'),
    'גלה': ('UNCOVER', 'uncovered/exiled'),
    'קבר': ('BURY', 'buried'),
    'קדש': ('SET.APART', 'set apart'),
    'ברא': ('SHAPE', 'shaped'),
    'היה': ('EXIST', 'existed'),
    'בדל': ('SEPARATE', 'separated'),
}

# Verb prefix patterns (imperfect/vav-consecutive)
VERB_PREFIXES = {
    'וי': ('and he', 'past'),      # vav-consecutive imperfect 3ms
    'ות': ('and she', 'past'),     # vav-consecutive imperfect 3fs
    'ויי': ('and they', 'past'),   # rare
    'ויא': ('and he', 'past'),     # with aleph
    'יי': ('he will', 'future'),
    'תי': ('she will', 'future'),
    'אי': ('I will', 'future'),
    'ני': ('we will', 'future'),
    'י': ('he will', 'future'),     # imperfect 3ms
    'ת': ('she will', 'future'),    # imperfect 3fs or 2ms
    'א': ('I will', 'future'),     # imperfect 1cs
    'נ': ('we will', 'future'),    # imperfect 1cp
}

# Verb suffix patterns
VERB_SUFFIXES = {
    'ו': ('they', 'plural'),
    'ת': ('you (m.)', 'subject'),
    'תי': ('I', 'subject'),
    'נו': ('we/us', 'subject/object'),
    'ני': ('me', 'object'),
    'הו': ('him', 'object'),
    'ה': ('her', 'object'),
    'ם': ('them', 'object'),
}


def try_verb_parse(hebrew, words):
    """Try to parse a word as a verb conjugation."""
    # Try vav-consecutive forms (ויXXX)
    if hebrew.startswith('וי') and len(hebrew) >= 4:
        # Strip וי prefix
        root_candidate = hebrew[2:]
        # Try to find the root (may need to strip suffix too)
        for root_letters, (mech, rmt_base) in VERB_ROOTS.items():
            # Check if root_candidate starts with or matches the root
            if root_candidate.startswith(root_letters[:2]) or root_letters in root_candidate:
                # Check for plural suffix
                if root_candidate.endswith('ו') and len(root_candidate) > len(root_letters):
                    return f'and they {rmt_base}', f'and~they~will~{mech}(V)'
                return f'and he {rmt_base}', f'and~he~will~{mech}(V)'

    # Try ות prefix (and she)
    if hebrew.startswith('ות') and len(hebrew) >= 4:
        root_candidate = hebrew[2:]
        for root_letters, (mech, rmt_base) in VERB_ROOTS.items():
            if root_candidate.startswith(root_letters[:2]) or root_letters in root_candidate:
                return f'and she {rmt_base}', f'and~she~will~{mech}(V)'

    # Try imperfect without vav (יXXX)
    if hebrew.startswith('י') and len(hebrew) >= 3:
        root_candidate = hebrew[1:]
        for root_letters, (mech, rmt_base) in VERB_ROOTS.items():
            if root_candidate.startswith(root_letters[:2]):
                if root_candidate.endswith('ו'):
                    return f'they will {rmt_base.replace("ed","").replace("ew","ow").replace("oke","eak").strip()}', f'they~will~{mech}(V)'
                return f'he will {rmt_base.replace("ed","").replace("ew","ow").replace("oke","eak").strip()}', f'he~will~{mech}(V)'

    return None, None


def translate_word(hebrew, entry, words):
    """Try to translate a single word using patterns."""
    # 1. Check pronouns
    if hebrew in PRONOUNS:
        result = PRONOUNS[hebrew]
        if result is not None:
            return result[0], result[1]

    # 2. Check preposition+suffix combos
    if hebrew in PREP_SUFFIX:
        return PREP_SUFFIX[hebrew], 'preposition'

    # 3. Check proper names
    if hebrew in PROPER_NAMES:
        result = PROPER_NAMES[hebrew]
        if result is not None:
            return result, 'proper_name'

    # 4. Try verb conjugation parsing
    rmt, mech = try_verb_parse(hebrew, words)
    if rmt:
        return rmt, 'verb'

    # 5. Check for prefix + known pronoun/prep
    for prefix in ['ו', 'וה', 'ב', 'ל', 'כ', 'מ', 'ה', 'ש']:
        if hebrew.startswith(prefix) and len(hebrew) > len(prefix):
            rest = hebrew[len(prefix):]
            # Check if rest is a proper name
            if rest in PROPER_NAMES and PROPER_NAMES[rest]:
                prefix_eng = {'ו': 'and', 'וה': 'and the', 'ב': 'in', 'ל': 'to',
                              'כ': 'like', 'מ': 'from', 'ה': 'the', 'ש': 'that'}.get(prefix, '')
                return f'{prefix_eng} {PROPER_NAMES[rest]}', 'proper_name'
            # Check if rest is a pronoun
            if rest in PRONOUNS and PRONOUNS[rest]:
                prefix_eng = {'ו': 'and', 'ב': 'in', 'ל': 'to', 'כ': 'like', 'מ': 'from', 'ה': 'the'}.get(prefix, '')
                return f'{prefix_eng} {PRONOUNS[rest][0]}', PRONOUNS[rest][1]

    # 6. Construct forms — words ending in י that are "X of"
    if hebrew.endswith('י') and len(hebrew) >= 3:
        base = hebrew[:-1]
        if base in words:
            base_def = words[base].get('definition', '')
            if base_def and not any(base_def.startswith(p) for p in ['Strength', 'Hand', 'Nail', 'Mark', 'Staff', 'Window']):
                short = base_def.split(':')[0].strip()
                if short.startswith('I. '): short = short[3:]
                return f'{short.lower()} of', 'noun'

    # 7. Plural forms — words ending in ים or ות
    if hebrew.endswith('ים') and len(hebrew) >= 4:
        base = hebrew[:-2]
        if base in words:
            base_def = words[base].get('definition', '')
            if base_def and not any(base_def.startswith(p) for p in ['Strength', 'Hand', 'Nail', 'Mark', 'Staff', 'Window']):
                short = base_def.split(':')[0].strip()
                if short.startswith('I. '): short = short[3:]
                return f'{short.lower()}s', 'noun'

    # 8. Common number words
    numbers = {
        'אחד': 'one', 'שנים': 'two', 'שלש': 'three', 'שלשה': 'three',
        'ארבע': 'four', 'ארבעה': 'four', 'חמש': 'five', 'חמשה': 'five',
        'שש': 'six', 'ששה': 'six', 'שבע': 'seven', 'שבעה': 'seven',
        'שמנה': 'eight', 'תשע': 'nine', 'תשעה': 'nine', 'עשר': 'ten',
        'עשרה': 'ten', 'עשרים': 'twenty', 'שלשים': 'thirty',
        'ארבעים': 'forty', 'חמשים': 'fifty', 'ששים': 'sixty',
        'שבעים': 'seventy', 'שמנים': 'eighty', 'מאה': 'hundred',
        'מאות': 'hundreds', 'אלף': 'thousand', 'אלפים': 'thousands',
        'רבבה': 'ten thousand',
    }
    if hebrew in numbers:
        return numbers[hebrew], 'number'

    return None, None


def main():
    print('=' * 60)
    print('TRANSLATE FROM PATTERNS - Mechanical Bible')
    print('Extrapolating from Benner\'s methodology')
    print('=' * 60)

    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'[OK] Loaded {len(words)} words')

    stats = defaultdict(int)
    translated = 0

    for hw, entry in words.items():
        d = entry.get('definition', '')
        has_mech = bool(entry.get('mechanical_translation'))

        # Skip words that already have good definitions
        if has_mech:
            continue
        # Check if definition is pictographic garbage
        is_pic = False
        if d:
            first_token = d.split(',')[0].split(' ')[0].lower().strip()
            letter_pics = {'strength','hand','nail','mark','staff','window','house','teeth',
                          'water','head','eye','mouth','seed','palm','fence','door','basket',
                          'ox','foot','sun','cross','side','thorn','snake'}
            if first_token in letter_pics and ',' in d[:40]:
                is_pic = True
            # Also check after prefix
            if d.startswith(('And ', 'In ', 'To ', 'From ', 'Like ', 'The ', 'That ')):
                rest = re.sub(r'^(And|In|To|From|Like|The|That)\s+', '', d)
                rest_token = rest.split(',')[0].split(' ')[0].lower().strip()
                if rest_token in letter_pics and ',' in rest[:40]:
                    is_pic = True

        if not is_pic:
            continue

        # Try pattern-based translation
        result, pos = translate_word(hw, entry, words)
        if result:
            entry['definition'] = result
            if pos:
                entry['part_of_speech'] = pos
            entry['rmt_translation'] = result.lower()
            translated += 1
            stats[pos] += 1

    print(f'\n[DONE] Translated {translated} words by pattern matching')
    print(f'\nBreakdown:')
    for pos, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f'  {pos:>15}: {count}')

    # Save
    with open(WORDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)
    print(f'\n[SAVED] {WORDS_JSON}')

    # Show remaining untranslated count
    still_pic = 0
    for entry in words.values():
        d = entry.get('definition', '')
        if d:
            first_token = d.split(',')[0].split(' ')[0].lower().strip()
            letter_pics = {'strength','hand','nail','mark','staff','window','house','teeth',
                          'water','head','eye','mouth','seed','palm','fence','door','basket',
                          'ox','foot','sun','cross','side','thorn','snake'}
            if first_token in letter_pics and ',' in d[:40]:
                still_pic += 1
            elif d.startswith(('And ', 'In ', 'To ', 'From ', 'Like ', 'The ', 'That ')):
                rest = re.sub(r'^(And|In|To|From|Like|The|That)\s+', '', d)
                rest_token = rest.split(',')[0].split(' ')[0].lower().strip()
                if rest_token in letter_pics and ',' in rest[:40]:
                    still_pic += 1

    print(f'\nStill pictographic-only: {still_pic} ({still_pic/len(words)*100:.1f}%)')


if __name__ == '__main__':
    main()
