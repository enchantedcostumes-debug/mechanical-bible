#!/usr/bin/env python3
"""
ENRICH BIBLICAL NAMES - Mechanical Bible
==========================================
Fills in missing definitions, transliterations, and pictographic
meanings for all 2,338 biblical names using:
1. words.json lexicon data
2. Known biblical name meanings (scholarly consensus)
3. Hebrew root analysis

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
NAMES_JSON = BASE_DIR / 'data' / 'bible_names.json'
WORDS_JSON = BASE_DIR / 'words.json'

# ============================================================================
# HEBREW TRANSLITERATION TABLE
# ============================================================================

HEBREW_TRANSLIT = {
    'א': '', 'ב': 'b', 'ג': 'g', 'ד': 'd', 'ה': 'h',
    'ו': 'v', 'ז': 'z', 'ח': 'hh', 'ט': 't', 'י': 'y',
    'כ': 'k', 'ך': 'k', 'ל': 'l', 'מ': 'm', 'ם': 'm',
    'נ': 'n', 'ן': 'n', 'ס': 's', 'ע': '', 'פ': 'p',
    'ף': 'p', 'צ': 'ts', 'ץ': 'ts', 'ק': 'q', 'ר': 'r',
    'ש': 'sh', 'ת': 't',
}

# ============================================================================
# WELL-KNOWN BIBLICAL NAME MEANINGS
# These are standard scholarly meanings, not interpretive
# ============================================================================

KNOWN_MEANINGS = {
    # Genesis names
    'Eden': 'Delight, pleasure',
    'Pishon': 'Dispersive, freely flowing',
    'Havilah': 'Circular, stretch of sand',
    'Gihon': 'Bursting forth, gushing',
    'Cush': 'Black, Ethiopia',
    'Tigris': 'Rapid, arrow-like',
    'Asshur': 'Level plain, Assyria',
    'Adam': 'Man, ground, red earth',
    'Eve': 'Life, living',
    'Cain': 'Acquired, possession',
    'Abel': 'Breath, vapor, vanity',
    'Nod': 'Wandering',
    'Enoch': 'Dedicated, initiated',
    'Irad': 'Wild donkey, fugitive',
    'Mehujael': 'Smitten by God',
    'Methushael': 'Man of God',
    'Lamech': 'Powerful, made low',
    'Adah': 'Ornament, adornment',
    'Zillah': 'Shadow, shade',
    'Jabal': 'Stream, to lead',
    'Jubal': 'Music, jubilee',
    'Tubal-cain': 'Worldly possession, smith',
    'Naamah': 'Pleasant, lovely',
    'Seth': 'Appointed, placed',
    'Enosh': 'Mortal man, frail',
    'Kenan': 'Possession, lamentation',
    'Mahalalel': 'Praise of God',
    'Jared': 'Descent, shall come down',
    'Methuselah': 'His death shall bring',
    'Noah': 'Rest, comfort',
    'Shem': 'Name, fame, renown',
    'Ham': 'Hot, warm, dark',
    'Japheth': 'Enlarged, opened',
    'Nimrod': 'Rebel, valiant, hunter',
    'Babel': 'Confusion, gate of God',
    'Nineveh': 'Offspring, dwelling',
    'Abram': 'Exalted father',
    'Abraham': 'Father of multitudes',
    'Sarai': 'Princess, noble woman',
    'Sarah': 'Princess, noble woman',
    'Lot': 'Covering, veil',
    'Hagar': 'Flight, stranger',
    'Ishmael': 'God hears',
    'Isaac': 'He laughs, laughter',
    'Rebekah': 'To tie, to bind, captivating',
    'Esau': 'Hairy, rough',
    'Jacob': 'Heel grasper, supplanter',
    'Israel': 'Prevails with God, wrestles with God',
    'Leah': 'Weary, wild cow',
    'Rachel': 'Ewe, lamb',
    'Reuben': 'Behold a son',
    'Simeon': 'Hearing, listened',
    'Levi': 'Joined, attached',
    'Judah': 'Praised, thanksgiving',
    'Dan': 'Judge, he judged',
    'Naphtali': 'My wrestling',
    'Gad': 'Fortune, troop',
    'Asher': 'Happy, blessed',
    'Issachar': 'He brings wages, reward',
    'Zebulun': 'Dwelling, habitation',
    'Dinah': 'Judged, vindicated',
    'Joseph': 'He will add, increase',
    'Benjamin': 'Son of the right hand',
    'Tamar': 'Palm tree, date palm',
    'Perez': 'Breach, break through',
    'Zerah': 'Rising, dawning, brightness',
    'Potiphar': 'Belonging to the sun',
    'Pharaoh': 'Great house, palace',
    'Manasseh': 'Causing to forget',
    'Ephraim': 'Doubly fruitful',
    'Goshen': 'Drawing near',

    # Exodus names
    'Moses': 'Drawn out of water',
    'Aaron': 'Enlightened, mountain of strength',
    'Miriam': 'Bitter sea, rebellion',
    'Jethro': 'Excellence, abundance',
    'Zipporah': 'Bird, sparrow',
    'Gershom': 'Stranger there',
    'Joshua': 'YHWH is salvation',
    'Bezalel': 'In the shadow of God',
    'Amalek': 'People that licks up, warlike',
    'Midian': 'Strife, judgment',
    'Sinai': 'Bush of thorns, clay',
    'Horeb': 'Desolate, waste',

    # Key prophets/leaders
    'Samuel': 'Heard by God, asked of God',
    'Saul': 'Asked for, demanded',
    'David': 'Beloved',
    'Solomon': 'Peace, peaceful',
    'Elijah': 'My God is YHWH',
    'Elisha': 'My God is salvation',
    'Isaiah': 'YHWH is salvation',
    'Jeremiah': 'YHWH will exalt',
    'Ezekiel': 'God strengthens',
    'Daniel': 'God is my judge',
    'Hosea': 'Salvation, deliverance',
    'Joel': 'YHWH is God',
    'Amos': 'Burden, burden bearer',
    'Obadiah': 'Servant of YHWH',
    'Jonah': 'Dove',
    'Micah': 'Who is like YHWH?',
    'Nahum': 'Comfort, consolation',
    'Habakkuk': 'Embrace, wrestler',
    'Zephaniah': 'YHWH has hidden',
    'Haggai': 'Festive, my feast',
    'Zechariah': 'YHWH remembers',
    'Malachi': 'My messenger, my angel',
    'Ezra': 'Help, helper',
    'Nehemiah': 'YHWH has comforted',

    # Ruth
    'Ruth': 'Friend, companion',
    'Boaz': 'Strength is in him, swiftness',
    'Naomi': 'Pleasant, my delight',
    'Orpah': 'Neck, back of neck',
    'Obed': 'Servant, worshipper',
    'Jesse': 'Gift, wealthy',

    # Key places
    'Jerusalem': 'Foundation of peace',
    'Bethlehem': 'House of bread',
    'Bethel': 'House of God',
    'Hebron': 'Alliance, association',
    'Jericho': 'Moon city, fragrant',
    'Shiloh': 'Place of rest, tranquil',
    'Zion': 'Parched place, monument',
    'Gilead': 'Rocky region, heap of witness',
    'Galilee': 'Circuit, region, rolling',
    'Jordan': 'Descender, flowing down',
    'Lebanon': 'White, whiteness',
    'Carmel': 'Garden land, vineyard of God',
    'Samaria': 'Watch mountain, guard',
    'Beersheba': 'Well of the oath',
    'Sodom': 'Burning, scorched',
    'Gomorrah': 'Submersion, bondage',
    'Egypt': 'Double straits, siege',
    'Mizraim': 'Double straits, Egypt',
    'Canaan': 'Lowland, merchant',
    'Moab': 'From the father',
    'Edom': 'Red',
    'Ammon': 'Tribal, people',
    'Philistia': 'Wanderers, immigrants',
    'Tyre': 'Rock, sharp stone',
    'Sidon': 'Fishing, fishery',
    'Damascus': 'Silent weaver, activity',
    'Shinar': 'Country of two rivers',
    'Paddan-aram': 'Field of Aram',
    'Ur': 'Light, flame',

    # Peoples
    'Hittite': 'Descendant of Heth, terror',
    'Amorite': 'Mountain dweller, talker',
    'Jebusite': 'Threshing place',
    'Perizzite': 'Village dweller',
    'Hivite': 'Villager, tent dweller',
    'Girgashite': 'Dwelling on clayey soil',

    # Judges period
    'Deborah': 'Bee, word, eloquent',
    'Gideon': 'Hewer, great warrior',
    'Samson': 'Sun-like, brightness',
    'Delilah': 'Feeble, languishing',
    'Jephthah': 'He opens',
    'Othniel': 'Force of God',
    'Ehud': 'United, strong',
    'Barak': 'Lightning, thunder',

    # United/Divided kingdom
    'Absalom': 'Father of peace',
    'Joab': 'YHWH is father',
    'Jonathan': 'YHWH has given',
    'Bathsheba': 'Daughter of the oath',
    'Nathan': 'He gave, gift',
    'Rehoboam': 'Enlarger of the people',
    'Jeroboam': 'The people contend',
    'Ahab': 'Uncle, father\'s brother',
    'Jezebel': 'Not exalted, chaste',
    'Hezekiah': 'YHWH is my strength',
    'Josiah': 'YHWH heals, supports',
    'Manasseh': 'Causing to forget',
    'Asa': 'Healer, physician',

    # Esther/Daniel era
    'Esther': 'Star, hidden',
    'Mordecai': 'Dedicated to Marduk, little man',
    'Haman': 'Magnificent, noise',
    'Vashti': 'Beautiful, best',
    'Nebuchadnezzar': 'Nebo protect the crown',
    'Cyrus': 'Sun, throne',
    'Darius': 'Maintainer, possessor',

    # Job
    'Job': 'Persecuted, hated',
    'Eliphaz': 'My God is gold',
    'Bildad': 'Son of contention',
    'Zophar': 'Sparrow, departing',
    'Elihu': 'He is my God',

    # Other important figures
    'Melchizedek': 'King of righteousness',
    'Balaam': 'Devourer of people',
    'Balak': 'Devastator, waster',
    'Caleb': 'Dog, whole-hearted',
    'Phinehas': 'Mouth of brass',
    'Eli': 'Ascension, elevated',
    'Hannah': 'Grace, favor, beautiful',
    'Abigail': 'Father\'s joy, source of joy',
    'Michal': 'Who is like God?',
    'Uriah': 'YHWH is my light',
}


def transliterate(hebrew):
    """Convert Hebrew text to basic transliteration."""
    result = []
    for ch in hebrew:
        t = HEBREW_TRANSLIT.get(ch, '')
        result.append(t)
    translit = ''.join(result)
    # Clean up double letters and format
    translit = re.sub(r'(.)\1+', r'\1\1', translit)
    return translit


def get_pictographic_from_words(hebrew, words):
    """Get pictographic description from words.json entry."""
    entry = words.get(hebrew, {})
    pic = entry.get('pictographic', '')
    if pic and pic != '[Pictographic]' and len(pic) < 200:
        return pic

    # Build from letters
    letters = entry.get('letters', [])
    if letters:
        parts = []
        for l in letters:
            char = l.get('char', l.get('letter', ''))
            name = l.get('name', '')
            pictograph = l.get('pictograph', '')
            if name and pictograph:
                parts.append(f"{char} ({name}: {pictograph})")
            elif name:
                parts.append(f"{char} ({name})")
        if parts:
            return ' + '.join(parts)

    return ''


def get_definition_from_words(hebrew, words):
    """Get a clean definition from words.json."""
    entry = words.get(hebrew, {})
    defn = entry.get('definition', '')
    if not defn or defn == '[Pictographic]':
        return ''
    # Clean up
    defn = defn.split(':')[0].strip()
    for prefix in ('I. ', 'II. ', 'III. '):
        if defn.startswith(prefix):
            defn = defn[len(prefix):]
    return defn[:100]


def enrich_names():
    """Enrich all biblical names with definitions and transliterations."""
    with open(NAMES_JSON, 'r', encoding='utf-8') as f:
        names_data = json.load(f)

    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)

    enriched_count = 0
    translit_count = 0
    pic_count = 0

    for name in names_data['names']:
        hebrew = name.get('hebrew', '')
        english = name.get('english', '')

        # Fill transliteration
        if not name.get('transliteration') and hebrew:
            translit = transliterate(hebrew)
            if translit:
                name['transliteration'] = translit
                translit_count += 1

        # Fill definition from known meanings first, then words.json
        if not name.get('definition'):
            # Check known meanings (case-insensitive match)
            known = KNOWN_MEANINGS.get(english, '')
            if not known:
                # Try variations
                for k, v in KNOWN_MEANINGS.items():
                    if k.lower() == english.lower():
                        known = v
                        break

            if known:
                name['definition'] = known
                enriched_count += 1
            else:
                # Try words.json
                defn = get_definition_from_words(hebrew, words)
                if defn:
                    name['definition'] = defn
                    enriched_count += 1

        # Fill pictographic
        if not name.get('pictographic') and hebrew:
            pic = get_pictographic_from_words(hebrew, words)
            if pic:
                name['pictographic'] = pic
                pic_count += 1

    # Save enriched data
    with open(NAMES_JSON, 'w', encoding='utf-8') as f:
        json.dump(names_data, f, ensure_ascii=False, indent=2)

    # Stats
    total = len(names_data['names'])
    with_def = sum(1 for n in names_data['names'] if n.get('definition', ''))
    with_translit = sum(1 for n in names_data['names'] if n.get('transliteration', ''))
    with_pic = sum(1 for n in names_data['names'] if n.get('pictographic', ''))

    print(f'\n[DONE] Enriched {total} names:')
    print(f'  Definitions added: {enriched_count} (total now: {with_def}/{total})')
    print(f'  Transliterations added: {translit_count} (total now: {with_translit}/{total})')
    print(f'  Pictographics added: {pic_count} (total now: {with_pic}/{total})')
    print(f'  Still missing definitions: {total - with_def}')


if __name__ == '__main__':
    print('=' * 60)
    print('ENRICH BIBLICAL NAMES - Mechanical Bible')
    print('=' * 60)
    enrich_names()
