"""
Add 35 missing Bible name entries to words.json
Each entry gets REAL letter breakdowns, gematria, pictographic analysis
Strong's numbers verified from biblehub.com / blueletterbible.org
"""
import json
import os

# Hebrew letter data for building REAL pictographic breakdowns
LETTER_DATA = {
    '\u05d0': {'name': 'ALEPH', 'value': 1, 'pictograph': 'Ox head', 'concrete': 'Strength, power, leader', 'abstract': 'Authority, beginning'},
    '\u05d1': {'name': 'BET', 'value': 2, 'pictograph': 'Tent/House', 'concrete': 'House, tent, dwelling', 'abstract': 'Family, inside'},
    '\u05d2': {'name': 'GIMEL', 'value': 3, 'pictograph': 'Camel/Foot', 'concrete': 'Camel, foot, walk', 'abstract': 'Journey, gathering, pride'},
    '\u05d3': {'name': 'DALET', 'value': 4, 'pictograph': 'Door', 'concrete': 'Door, pathway, entrance', 'abstract': 'Opening, access'},
    '\u05d4': {'name': 'HE', 'value': 5, 'pictograph': 'Window/Man with arms raised', 'concrete': 'Window, look, behold', 'abstract': 'Revelation, breath'},
    '\u05d5': {'name': 'VAV', 'value': 6, 'pictograph': 'Tent peg/Hook', 'concrete': 'Nail, hook, peg', 'abstract': 'Connection, binding, and'},
    '\u05d6': {'name': 'ZAYIN', 'value': 7, 'pictograph': 'Plow/Weapon', 'concrete': 'Weapon, plow, cut', 'abstract': 'Sustenance, nourishment'},
    '\u05d7': {'name': 'CHET', 'value': 8, 'pictograph': 'Tent wall/Fence', 'concrete': 'Wall, fence, enclosure', 'abstract': 'Protection, separation'},
    '\u05d8': {'name': 'TET', 'value': 9, 'pictograph': 'Snake/Basket', 'concrete': 'Snake, basket, surround', 'abstract': 'Encompass, contain'},
    '\u05d9': {'name': 'YOD', 'value': 10, 'pictograph': 'Hand/Arm', 'concrete': 'Hand, arm, work', 'abstract': 'Deed, power, worship'},
    '\u05db': {'name': 'KAF', 'value': 20, 'pictograph': 'Open palm', 'concrete': 'Palm, open hand, cover', 'abstract': 'Bending, submission'},
    '\u05dc': {'name': 'LAMED', 'value': 30, 'pictograph': 'Shepherd staff', 'concrete': 'Staff, goad, teach', 'abstract': 'Authority, learning, toward'},
    '\u05de': {'name': 'MEM', 'value': 40, 'pictograph': 'Water waves', 'concrete': 'Water, sea', 'abstract': 'Chaos, mighty'},
    '\u05e0': {'name': 'NUN', 'value': 50, 'pictograph': 'Sprouting seed', 'concrete': 'Seed, fish, offspring', 'abstract': 'Continue, perpetuate, heir'},
    '\u05e1': {'name': 'SAMEKH', 'value': 60, 'pictograph': 'Thorn/Shield', 'concrete': 'Thorn, shield, prop', 'abstract': 'Support, protect, surround'},
    '\u05e2': {'name': 'AYIN', 'value': 70, 'pictograph': 'Eye', 'concrete': 'Eye, see, watch', 'abstract': 'Experience, knowledge, sight'},
    '\u05e4': {'name': 'PE', 'value': 80, 'pictograph': 'Mouth', 'concrete': 'Mouth, speak, word', 'abstract': 'Expression, command'},
    '\u05e6': {'name': 'TSADE', 'value': 90, 'pictograph': 'Fish hook/Man on side', 'concrete': 'Hook, catch, righteous', 'abstract': 'Righteousness, hunting'},
    '\u05e7': {'name': 'QOF', 'value': 100, 'pictograph': 'Back of head/Needle eye', 'concrete': 'Back of head, monkey', 'abstract': 'Cycle, behind, horizon'},
    '\u05e8': {'name': 'RESH', 'value': 200, 'pictograph': 'Head of man', 'concrete': 'Head, person, chief', 'abstract': 'First, top, beginning'},
    '\u05e9': {'name': 'SHIN', 'value': 300, 'pictograph': 'Two teeth/Flame', 'concrete': 'Teeth, fire, consume', 'abstract': 'Destroy, sharp, divine presence'},
    '\u05ea': {'name': 'TAV', 'value': 400, 'pictograph': 'Cross mark/Signature', 'concrete': 'Mark, sign, cross', 'abstract': 'Covenant, seal, truth'},
    # Final forms
    '\u05da': {'name': 'KAF (final)', 'value': 500, 'pictograph': 'Open palm', 'concrete': 'Palm, open hand, cover', 'abstract': 'Bending, submission'},
    '\u05dd': {'name': 'MEM (final)', 'value': 600, 'pictograph': 'Water waves', 'concrete': 'Water, sea', 'abstract': 'Chaos, mighty'},
    '\u05df': {'name': 'NUN (final)', 'value': 700, 'pictograph': 'Sprouting seed', 'concrete': 'Seed, fish, offspring', 'abstract': 'Continue, perpetuate, heir'},
    '\u05e3': {'name': 'PE (final)', 'value': 800, 'pictograph': 'Mouth', 'concrete': 'Mouth, speak, word', 'abstract': 'Expression, command'},
    '\u05e5': {'name': 'TSADE (final)', 'value': 900, 'pictograph': 'Fish hook/Man on side', 'concrete': 'Hook, catch, righteous', 'abstract': 'Righteousness, hunting'},
}

# Strong's data for all 35 missing names (researched from biblehub.com, blueletterbible.org)
MISSING_NAMES = {
    # Genesis genealogy names
    '\u05d7\u05d5\u05d9\u05dc\u05d4': {  # Havilah
        'english': 'Havilah', 'strongs': 'H2341',
        'transliteration': 'Chavilah',
        'definition': 'Circular; a land of gold, bdellium and onyx (Gen 2:11); also a son of Cush and of Joktan',
        'first_occurrence': 'Genesis 2:11', 'frequency': 7
    },
    '\u05e0\u05d5\u05d3': {  # Nod
        'english': 'Nod', 'strongs': 'H5113',
        'transliteration': 'Nowd',
        'definition': 'Wandering; the land east of Eden where Cain dwelt',
        'first_occurrence': 'Genesis 4:16', 'frequency': 1
    },
    '\u05e2\u05d9\u05e8\u05d3': {  # Irad
        'english': 'Irad', 'strongs': 'H5897',
        'transliteration': 'Iyrad',
        'definition': 'Fugitive; a descendant of Cain',
        'first_occurrence': 'Genesis 4:18', 'frequency': 2
    },
    '\u05de\u05d7\u05d5\u05d9\u05d0\u05dc': {  # Mehujael
        'english': 'Mehujael', 'strongs': 'H4232',
        'transliteration': 'Mechuwya\'el',
        'definition': 'Smitten of God; a descendant of Cain',
        'first_occurrence': 'Genesis 4:18', 'frequency': 2
    },
    '\u05d9\u05d1\u05dc': {  # Jabal
        'english': 'Jabal', 'strongs': 'H2989',
        'transliteration': 'Yabal',
        'definition': 'Stream, flowing; father of tent-dwellers and livestock keepers',
        'first_occurrence': 'Genesis 4:20', 'frequency': 1
    },
    # Table of Nations (Genesis 10)
    '\u05de\u05d2\u05d5\u05d2': {  # Magog
        'english': 'Magog', 'strongs': 'H4031',
        'transliteration': 'Magowg',
        'definition': 'Land of Gog; a son of Japheth, and the region of his descendants',
        'first_occurrence': 'Genesis 10:2', 'frequency': 4
    },
    '\u05ea\u05d9\u05e8\u05e1': {  # Tiras
        'english': 'Tiras', 'strongs': 'H8494',
        'transliteration': 'Tiyrac',
        'definition': 'Desire; a son of Japheth',
        'first_occurrence': 'Genesis 10:2', 'frequency': 2
    },
    '\u05e8\u05d9\u05e4\u05ea': {  # Riphath
        'english': 'Riphath', 'strongs': 'H7384',
        'transliteration': 'Riyphath',
        'definition': 'Spoken word; a son of Gomer',
        'first_occurrence': 'Genesis 10:3', 'frequency': 2
    },
    '\u05d3\u05d5\u05d3\u05e0\u05d9\u05dd': {  # Dodanim
        'english': 'Dodanim', 'strongs': 'H1721',
        'transliteration': 'Dodaniym',
        'definition': 'Leaders; descendants of Javan (Greeks)',
        'first_occurrence': 'Genesis 10:4', 'frequency': 1
    },
    '\u05e8\u05d5\u05d3\u05e0\u05d9\u05dd': {  # Rodanim
        'english': 'Rodanim', 'strongs': 'H1721',
        'transliteration': 'Rodaniym',
        'definition': 'Leaders; variant of Dodanim, descendants of Javan',
        'first_occurrence': '1 Chronicles 1:7', 'frequency': 1
    },
    '\u05e1\u05d1\u05ea\u05d4': {  # Sabtah
        'english': 'Sabtah', 'strongs': 'H5454',
        'transliteration': 'Cabta\'',
        'definition': 'Striking; a son of Cush',
        'first_occurrence': 'Genesis 10:7', 'frequency': 2
    },
    '\u05e1\u05d1\u05ea\u05db\u05d0': {  # Sabteca
        'english': 'Sabteca', 'strongs': 'H5455',
        'transliteration': 'Cabteka\'',
        'definition': 'Striking; a son of Cush',
        'first_occurrence': 'Genesis 10:7', 'frequency': 2
    },
    '\u05d0\u05db\u05d3': {  # Accad
        'english': 'Accad', 'strongs': 'H390',
        'transliteration': 'Akkad',
        'definition': 'Fortress; a city in Shinar founded by Nimrod',
        'first_occurrence': 'Genesis 10:10', 'frequency': 1
    },
    '\u05e8\u05e1\u05df': {  # Resen
        'english': 'Resen', 'strongs': 'H7449',
        'transliteration': 'Recen',
        'definition': 'Bridle, halter; a city between Nineveh and Calah',
        'first_occurrence': 'Genesis 10:12', 'frequency': 1
    },
    '\u05dc\u05d5\u05d3': {  # Lud
        'english': 'Lud', 'strongs': 'H3865',
        'transliteration': 'Luwd',
        'definition': 'Strife; a son of Shem, ancestor of the Lydians',
        'first_occurrence': 'Genesis 10:22', 'frequency': 4
    },
    '\u05d0\u05dc\u05de\u05d5\u05d3\u05d3': {  # Almodad
        'english': 'Almodad', 'strongs': 'H486',
        'transliteration': 'Almowdad',
        'definition': 'Not measured, immeasurable; a son of Joktan',
        'first_occurrence': 'Genesis 10:26', 'frequency': 2
    },
    '\u05d4\u05d3\u05d5\u05e8\u05dd': {  # Hadoram
        'english': 'Hadoram', 'strongs': 'H1913',
        'transliteration': 'Hadowram',
        'definition': 'Noble honor; a son of Joktan',
        'first_occurrence': 'Genesis 10:27', 'frequency': 4
    },
    '\u05d0\u05d5\u05d6\u05dc': {  # Uzal
        'english': 'Uzal', 'strongs': 'H187',
        'transliteration': 'Uwzal',
        'definition': 'To go away, wander; a son of Joktan',
        'first_occurrence': 'Genesis 10:27', 'frequency': 2
    },
    '\u05d3\u05e7\u05dc\u05d4': {  # Diklah
        'english': 'Diklah', 'strongs': 'H1853',
        'transliteration': 'Diqlah',
        'definition': 'Palm grove; a son of Joktan',
        'first_occurrence': 'Genesis 10:27', 'frequency': 2
    },
    '\u05e2\u05d5\u05d1\u05dc': {  # Obal
        'english': 'Obal', 'strongs': 'H5745',
        'transliteration': 'Owbal',
        'definition': 'Stripped bare; a son of Joktan',
        'first_occurrence': 'Genesis 10:28', 'frequency': 1
    },
    '\u05d0\u05d1\u05d9\u05de\u05d0\u05dc': {  # Abimael
        'english': 'Abimael', 'strongs': 'H39',
        'transliteration': 'Abiyma\'el',
        'definition': 'Father of Mael (my father is God); a son of Joktan',
        'first_occurrence': 'Genesis 10:28', 'frequency': 2
    },
    # Other missing names
    '\u05e2\u05d9': {  # Ai
        'english': 'Ai', 'strongs': 'H5857',
        'transliteration': 'Ay',
        'definition': 'Heap of ruins; a Canaanite city near Bethel',
        'first_occurrence': 'Genesis 12:8', 'frequency': 36
    },
    '\u05e4\u05d3\u05d4\u05e6\u05d5\u05e8': {  # Pedahzur
        'english': 'Pedahzur', 'strongs': 'H6301',
        'transliteration': 'Pedahtsur',
        'definition': 'The Rock has ransomed; father of Gamaliel of Manasseh',
        'first_occurrence': 'Numbers 1:10', 'frequency': 5
    },
    '\u05d5\u05d4\u05d1': {  # Waheb
        'english': 'Waheb', 'strongs': 'H2052',
        'transliteration': 'Vaheb',
        'definition': 'A place in Moab mentioned in the Book of the Wars of YHWH',
        'first_occurrence': 'Numbers 21:14', 'frequency': 1
    },
    '\u05d9\u05d4\u05e6': {  # Jahaz
        'english': 'Jahaz', 'strongs': 'H3096',
        'transliteration': 'Yahats',
        'definition': 'Trodden down; a place in Moab where Israel defeated Sihon',
        'first_occurrence': 'Numbers 21:23', 'frequency': 8
    },
    '\u05d9\u05d8\u05d1\u05ea': {  # Jotbath
        'english': 'Jotbath', 'strongs': 'H3193',
        'transliteration': 'Yotbathah',
        'definition': 'Pleasantness; a station in the wilderness wandering',
        'first_occurrence': 'Deuteronomy 10:7', 'frequency': 2
    },
    '\u05d9\u05d2\u05dc\u05d9': {  # Jogli
        'english': 'Jogli', 'strongs': 'H3020',
        'transliteration': 'Yogli',
        'definition': 'Exiled; father of Bukki of Dan',
        'first_occurrence': 'Numbers 34:22', 'frequency': 1
    },
    '\u05e6\u05dc\u05de\u05e0\u05e2': {  # Zalmunna
        'english': 'Zalmunna', 'strongs': 'H6759',
        'transliteration': 'Tsalmunna',
        'definition': 'Shade withheld; a king of Midian slain by Gideon',
        'first_occurrence': 'Judges 8:5', 'frequency': 12
    },
    '\u05e2\u05d9\u05d5\u05df': {  # Ijon
        'english': 'Ijon', 'strongs': 'H5859',
        'transliteration': 'Iyyown',
        'definition': 'Ruin; a city in northern Israel (Naphtali)',
        'first_occurrence': '1 Kings 15:20', 'frequency': 3
    },
    # The 4 we manually fixed earlier
    '\u05de\u05b4\u05e7\u05b0\u05d5\u05b5\u05d4': {  # Que/Kue (with vowels)
        'english': 'Que (Kue)', 'strongs': 'H4723',
        'transliteration': 'Miqveh',
        'definition': 'Collection, drove; a place in Cilicia where Solomon imported horses',
        'first_occurrence': '2 Chronicles 1:16', 'frequency': 2
    },
    '\u05d1\u05b7\u05bc\u05e6\u05b0\u05dc\u05d5\u05bc\u05ea': {  # Bazluth (with vowels)
        'english': 'Bazluth', 'strongs': 'H1213',
        'transliteration': 'Batsluwth',
        'definition': 'Stripping, peeling; head of a family of exiles returning with Zerubbabel',
        'first_occurrence': 'Ezra 2:52', 'frequency': 1
    },
    '\u05d1\u05b7\u05bc\u05e6\u05b0\u05dc\u05b4\u05d9\u05ea': {  # Bazlith (with vowels)
        'english': 'Bazlith', 'strongs': 'H1213',
        'transliteration': 'Batsliyth',
        'definition': 'Stripping, peeling; variant of Bazluth',
        'first_occurrence': 'Nehemiah 7:54', 'frequency': 1
    },
    '\u05e7\u05d5\u05b9\u05e2\u05b7': {  # Koa (with vowels)
        'english': 'Koa', 'strongs': 'H6970',
        'transliteration': 'Qowa',
        'definition': 'Cutting off; a people east of the Tigris allied with Babylon',
        'first_occurrence': 'Ezekiel 23:23', 'frequency': 1
    },
    '\u05e1\u05d5\u05df': {  # Aswan / Syene
        'english': 'Aswan', 'strongs': 'H5482',
        'transliteration': 'Ceveneh',
        'definition': 'Opening; a city on the southern border of Egypt (modern Aswan)',
        'first_occurrence': 'Ezekiel 29:10', 'frequency': 2
    },
    '\u05d4\u05e6\u05d1': {  # Huzzab
        'english': 'Huzzab', 'strongs': 'H5324',
        'transliteration': 'Hutstsab',
        'definition': 'It is decreed/established; possibly the queen of Nineveh',
        'first_occurrence': 'Nahum 2:7', 'frequency': 1
    },
}


def strip_vowels(hebrew):
    """Remove Hebrew vowel points to get consonant-only form"""
    consonants = []
    for ch in hebrew:
        # Keep only consonant code points (0x05D0-0x05EA)
        if '\u05d0' <= ch <= '\u05ea':
            consonants.append(ch)
    return ''.join(consonants)


def build_letters(hebrew_consonants):
    """Build letter breakdown array from consonant-only Hebrew"""
    letters = []
    for ch in hebrew_consonants:
        if ch in LETTER_DATA:
            ld = LETTER_DATA[ch]
            letters.append({
                'char': ch,
                'name': ld['name'],
                'value': ld['value'],
                'pictograph': ld['pictograph'],
                'concrete': ld['concrete'],
                'abstract': ld['abstract']
            })
    return letters


def calc_gematria(letters):
    """Calculate gematria from letter breakdown"""
    return sum(l['value'] for l in letters)


def digital_root(n):
    """Calculate digital root (repeated digit sum until single digit)"""
    while n > 9:
        n = sum(int(d) for d in str(n))
    return n


def build_pictographic(letters):
    """Build pictographic string"""
    return ' + '.join(f'[{l["pictograph"]}]' for l in letters)


def main():
    # Load words.json
    words_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'words.json')
    with open(words_path, 'r', encoding='utf-8') as f:
        words = json.load(f)

    added = 0
    for hebrew_key, info in MISSING_NAMES.items():
        if hebrew_key in words:
            print(f'[SKIP] {info["english"]} already in words.json')
            continue

        # Get consonants for letter analysis
        consonants = strip_vowels(hebrew_key)
        if not consonants:
            consonants = hebrew_key  # already consonant-only

        # Build letter breakdown
        letters = build_letters(consonants)
        gematria = calc_gematria(letters)
        dr = digital_root(gematria)
        pictographic = build_pictographic(letters)

        entry = {
            'hebrew': hebrew_key,
            'gematria': gematria,
            'digital_root': dr,
            'first_occurrence': info['first_occurrence'],
            'frequency': info['frequency'],
            'strongs': info['strongs'],
            'letters': letters,
            'pictographic': pictographic,
            'timeline': {
                'hebrew': pictographic,
                'septuagint': '(Research in progress)',
                'nt_greek': '(Research in progress)',
                'vulgate': '(Research in progress)',
                'kjv': info['english'],
                'modern': info['english']
            },
            'transliteration': info['transliteration'],
            'definition': info['definition'],
        }

        words[hebrew_key] = entry
        added += 1
        print(f'[OK] Added {info["english"]} ({hebrew_key}) - gematria={gematria}, dr={dr}, {len(letters)} letters')

    # Save
    with open(words_path, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

    print(f'\n[OK] Added {added} entries to words.json')
    print(f'[OK] Total words.json entries: {len(words)}')


if __name__ == '__main__':
    main()
