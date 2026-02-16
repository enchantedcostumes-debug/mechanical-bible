"""
BUILD NAMES DATABASE
Uses the Oracle platform's mechanical Bible data to extract EVERY proper name.

STRATEGY (Two-Pass Capitalization Analysis):
1. PASS 1: Scan ALL 39 books, count how often each word appears capitalized vs lowercase
2. FILTER: Proper names ONLY appear capitalized. Common English words appear both ways.
   - Words that ONLY appear capitalized -> almost certainly proper names
   - Words that appear >50% capitalized -> likely proper names (e.g. "Adam")
   - Words that appear <50% capitalized -> common English words at sentence start
3. PASS 2: Extract the filtered names with first-appearance tracking
4. ENRICH: Map to Hebrew using 58,400-entry lexicon, calculate gematria
5. CATEGORIZE: persons, places, peoples/nations, events, titles

This script uses the EXISTING Oracle infrastructure:
- data/mechanical_bible/books/*.json (39 books)
- data/lexicon/hebrew_lexicon_complete.json (58,400 Hebrew words)
- words.json (58,400 Hebrew words with definitions)

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import os
import re
import sys
from collections import Counter

# Path to the Oracle platform data
ORACLE_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           '..', 'flask-structural-api', '.claude', 'worktrees', 'jovial-merkle')

# Also try direct path
if not os.path.exists(ORACLE_BASE):
    ORACLE_BASE = r'C:\flask-structural-api\.claude\worktrees\jovial-merkle'

BOOKS_DIR = os.path.join(ORACLE_BASE, 'data', 'mechanical_bible', 'books')
LEXICON_PATH = os.path.join(ORACLE_BASE, 'data', 'lexicon', 'hebrew_lexicon_complete.json')

# Output in mechanical-bible repo
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPT_DIR)
OUTPUT_PATH = os.path.join(REPO_DIR, 'data', 'bible_names.json')

# Also load local words.json for Hebrew lookup
WORDS_PATH = os.path.join(REPO_DIR, 'words.json')

# Hebrew letter values for gematria
HEBREW_VALUES = {
    '\u05d0': 1,   # aleph
    '\u05d1': 2,   # bet
    '\u05d2': 3,   # gimel
    '\u05d3': 4,   # dalet
    '\u05d4': 5,   # he
    '\u05d5': 6,   # vav
    '\u05d6': 7,   # zayin
    '\u05d7': 8,   # chet
    '\u05d8': 9,   # tet
    '\u05d9': 10,  # yod
    '\u05db': 20,  # kaf
    '\u05da': 20,  # final kaf
    '\u05dc': 30,  # lamed
    '\u05de': 40,  # mem
    '\u05dd': 40,  # final mem
    '\u05e0': 50,  # nun
    '\u05df': 50,  # final nun
    '\u05e1': 60,  # samekh
    '\u05e2': 70,  # ayin
    '\u05e4': 80,  # pe
    '\u05e3': 80,  # final pe
    '\u05e6': 90,  # tsade
    '\u05e5': 90,  # final tsade
    '\u05e7': 100, # qof
    '\u05e8': 200, # resh
    '\u05e9': 300, # shin
    '\u05ea': 400, # tav
}


def calc_gematria(hebrew_text):
    """Calculate standard Hebrew gematria."""
    return sum(HEBREW_VALUES.get(c, 0) for c in hebrew_text)


def digital_root(n):
    """Calculate digital root."""
    if n == 0:
        return 0
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n


# Book order and display names
BOOK_ORDER = [
    'genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy',
    'joshua', 'judges', 'ruth',
    'i_samuel', 'ii_samuel', 'i_kings', 'ii_kings',
    'i_chronicles', 'ii_chronicles',
    'ezra', 'nehemiah', 'esther',
    'job', 'psalms', 'proverbs', 'ecclesiastes', 'song_of_songs',
    'isaiah', 'jeremiah', 'lamentations', 'ezekiel', 'daniel',
    'hosea', 'joel', 'amos', 'obadiah', 'jonah',
    'micah', 'nahum', 'habakkuk', 'zephaniah', 'haggai',
    'zechariah', 'malachi'
]

BOOK_DISPLAY = {
    'genesis': 'Genesis', 'exodus': 'Exodus', 'leviticus': 'Leviticus',
    'numbers': 'Numbers', 'deuteronomy': 'Deuteronomy',
    'joshua': 'Joshua', 'judges': 'Judges', 'ruth': 'Ruth',
    'i_samuel': '1 Samuel', 'ii_samuel': '2 Samuel',
    'i_kings': '1 Kings', 'ii_kings': '2 Kings',
    'i_chronicles': '1 Chronicles', 'ii_chronicles': '2 Chronicles',
    'ezra': 'Ezra', 'nehemiah': 'Nehemiah', 'esther': 'Esther',
    'job': 'Job', 'psalms': 'Psalms', 'proverbs': 'Proverbs',
    'ecclesiastes': 'Ecclesiastes', 'song_of_songs': 'Song of Songs',
    'isaiah': 'Isaiah', 'jeremiah': 'Jeremiah',
    'lamentations': 'Lamentations', 'ezekiel': 'Ezekiel', 'daniel': 'Daniel',
    'hosea': 'Hosea', 'joel': 'Joel', 'amos': 'Amos',
    'obadiah': 'Obadiah', 'jonah': 'Jonah', 'micah': 'Micah',
    'nahum': 'Nahum', 'habakkuk': 'Habakkuk', 'zephaniah': 'Zephaniah',
    'haggai': 'Haggai', 'zechariah': 'Zechariah', 'malachi': 'Malachi'
}

# ============================================================================
# TWO-PASS CAPITALIZATION ANALYSIS
# ============================================================================
# Instead of maintaining a massive exclude list, we use a data-driven approach:
# Proper names ONLY appear capitalized. Common English words appear both ways.
# A word that appears 50%+ of the time capitalized is likely a proper name.
# A word that appears mostly lowercase is a common English word at sentence start.
#
# ADDITIONAL SAFETY: Hard-coded exclusions for known non-name terms that happen
# to only appear capitalized in Bible text (titles, terms, abbreviations)
ALWAYS_EXCLUDE = {
    # Translation/editorial abbreviations
    'Heb', 'Lit', 'Cf', 'Exod', 'Num', 'Deut', 'Lev', 'Chron', 'Eccl',
    'Prov', 'Isa', 'Mic', 'Zech', 'Ezek', 'Neh', 'Gen', 'Judg', 'Jer',
    'Josh', 'Sam', 'Ps', 'Hos',
    # Divine titles (not personal names in the traditional sense)
    'Lord', 'God', 'Almighty', 'Sovereign',
    # Textual/scholarly terms
    'Septuagint', 'Targum', 'Vulgate', 'Masoretic', 'Samaritan',
    'Akkadian', 'Sumerian', 'Ugaritic', 'Symmachus', 'Jerome',
    'Decalogue', 'Torah', 'Midrash', 'Mishnah', 'Abodah',
    'Bible', 'Dictionary', 'English', 'Hebrew', 'Rashbam', 'Ramban',
    'Tabernacle', 'Sabbath', 'Passover', 'Sanhedrin', 'Josephus',
    'Ecclesiastes',
    # Liturgical terms
    'Selah', 'Amen', 'Hosanna', 'Hallelujah', 'Maranatha', 'Hallel',
    # Single letters and ultra-short non-names
    'Ah', 'Oh', 'Lo', 'Ha',
    # Common English words that only appear capitalized in mechanical translation
    'Nevertheless', 'Moreover', 'Therefore', 'Whereby', 'Herein', 'Thereof',
    'Hitherto', 'Whence', 'Wherein', 'Behold', 'Hark', 'Creator',
    'Seedtime', 'Precise', 'Verily', 'Indeed', 'Synonym', 'Presumably',
    'Henceforth', 'Infinitives', 'Figurines', 'Coax', 'Suspend',
    'Furthermore', 'Impulsively', 'Thoughtlessly', 'Despondency',
    'Deprives', 'Brandished', 'Extolled', 'Nestled', 'Growls',
    'Forthwith', 'Assuredly', 'Restlessly', 'Conscientiously',
    'Mediterranean', 'Phoenicians', 'Braggart', 'Lowland',
    'Transjordan', 'Grammar', 'Luxury', 'Preeminent', 'Repairer',
    'Watchers', 'Assembler', 'Dweller', 'Flints', 'Wildcats',
    'Pleiades', 'Stillbirths',
    # Divine titles that aren't personal names
    'Adonai', 'Elyon', 'Shaddai', 'Ehyeh-Asher-Ehyeh',
    # Descriptive phrases used as names in some translations
    'Not-My-People', 'Ever-Living', 'Unity', 'Jewish', 'Twas', 'Wasn',
    # Text artifacts - concatenated word fragments from mechanical translation
    'Godefire', 'Zionand', 'Zionfall', 'Goddthat', 'Bizzaron', 'Seadthe',
    # Demonyms (adjective forms, not proper names themselves)
    'Egyptian', 'Assyrian', 'Hittites',
}

# English word suffixes that Hebrew names NEVER use
# Used to filter out mechanical translation vocabulary words
NON_NAME_SUFFIXES = (
    'ing', 'tion', 'ness', 'ment', 'ous', 'ive', 'able', 'ible',
    'less', 'ful', 'ally', 'erly', 'ily', 'ory', 'ary', 'ery',
    'ise', 'ize', 'ure', 'ude', 'ance', 'ence', 'ism',
    'ths', 'nts', 'wls',  # plural/verb endings for "Stillbirths", "Flints", "Growls"
)

# Names that the ratio analysis might miss because they also appear lowercase
# in some Bible translations - force include these known biblical names
FORCE_INCLUDE = {
    'Adam', 'Eve', 'God', 'Israel', 'Judah', 'Joseph', 'David', 'Moses',
    'Aaron', 'Abraham', 'Isaac', 'Jacob', 'Sarah', 'Rebekah', 'Rachel',
    'Leah', 'Ruth', 'Esther', 'Solomon', 'Saul', 'Samuel', 'Elijah',
    'Lot', 'Moab', 'Edom', 'Dan', 'Gad', 'Asher', 'Levi',
    'Haran', 'Ammon', 'Eden', 'Bethel', 'Zion', 'Shiloh',
    'Nod', 'Beer', 'Negeb', 'Gilead', 'Bashan',
    'Hur', 'Nun', 'Gog', 'Tob', 'Nob', 'Kir', 'Rab', 'Gur',
    'Uz', 'Hul', 'Reu', 'Buz', 'Luz', 'Zur', 'Ziv', 'Bul',
    'Kue', 'Pul', 'Pai', 'Koz', 'Iru', 'Zia', 'Ahi', 'Hod',
    'Cun', 'Ziz', 'Uel', 'Gob', 'Ner', 'Toi', 'Hor',
    'Ard', 'Ar', 'Er', 'Ir', 'Og', 'Ai',
    'Arad', 'Nebo', 'Beth', 'Ben', 'Bela', 'Gera',
}

# ============================================================================
# KNOWN HEBREW MAPPINGS - English name -> Hebrew text
# From the Oracle's genesis_names_data.py and Strong's concordance
# ============================================================================
ENGLISH_TO_HEBREW = {
    # Genesis patriarchs and key figures
    'Adam': '\u05d0\u05d3\u05dd',
    'Eve': '\u05d7\u05d5\u05d4',
    'Cain': '\u05e7\u05d9\u05df',
    'Abel': '\u05d4\u05d1\u05dc',
    'Seth': '\u05e9\u05ea',
    'Enosh': '\u05d0\u05e0\u05d5\u05e9',
    'Kenan': '\u05e7\u05d9\u05e0\u05df',
    'Mahalalel': '\u05de\u05d4\u05dc\u05dc\u05d0\u05dc',
    'Jared': '\u05d9\u05e8\u05d3',
    'Enoch': '\u05d7\u05e0\u05d5\u05da',
    'Methuselah': '\u05de\u05ea\u05d5\u05e9\u05dc\u05d7',
    'Lamech': '\u05dc\u05de\u05da',
    'Noah': '\u05e0\u05d7',
    'Shem': '\u05e9\u05dd',
    'Ham': '\u05d7\u05dd',
    'Japheth': '\u05d9\u05e4\u05ea',
    'Abram': '\u05d0\u05d1\u05e8\u05dd',
    'Abraham': '\u05d0\u05d1\u05e8\u05d4\u05dd',
    'Sarai': '\u05e9\u05e8\u05d9',
    'Sarah': '\u05e9\u05e8\u05d4',
    'Hagar': '\u05d4\u05d2\u05e8',
    'Ishmael': '\u05d9\u05e9\u05de\u05e2\u05d0\u05dc',
    'Isaac': '\u05d9\u05e6\u05d7\u05e7',
    'Rebekah': '\u05e8\u05d1\u05e7\u05d4',
    'Esau': '\u05e2\u05e9\u05d5',
    'Jacob': '\u05d9\u05e2\u05e7\u05d1',
    'Israel': '\u05d9\u05e9\u05e8\u05d0\u05dc',
    'Leah': '\u05dc\u05d0\u05d4',
    'Rachel': '\u05e8\u05d7\u05dc',
    'Reuben': '\u05e8\u05d0\u05d5\u05d1\u05df',
    'Simeon': '\u05e9\u05de\u05e2\u05d5\u05df',
    'Levi': '\u05dc\u05d5\u05d9',
    'Judah': '\u05d9\u05d4\u05d5\u05d3\u05d4',
    'Dan': '\u05d3\u05df',
    'Naphtali': '\u05e0\u05e4\u05ea\u05dc\u05d9',
    'Gad': '\u05d2\u05d3',
    'Asher': '\u05d0\u05e9\u05e8',
    'Issachar': '\u05d9\u05e9\u05e9\u05db\u05e8',
    'Zebulun': '\u05d6\u05d1\u05d5\u05dc\u05df',
    'Dinah': '\u05d3\u05d9\u05e0\u05d4',
    'Joseph': '\u05d9\u05d5\u05e1\u05e3',
    'Benjamin': '\u05d1\u05e0\u05d9\u05de\u05df',
    'Tamar': '\u05ea\u05de\u05e8',
    'Perez': '\u05e4\u05e8\u05e5',
    'Zerah': '\u05d6\u05e8\u05d7',
    'Potiphar': '\u05e4\u05d5\u05d8\u05d9\u05e4\u05e8',
    'Pharaoh': '\u05e4\u05e8\u05e2\u05d4',

    # Exodus - key figures
    'Moses': '\u05de\u05e9\u05d4',
    'Aaron': '\u05d0\u05d4\u05e8\u05df',
    'Miriam': '\u05de\u05e8\u05d9\u05dd',
    'Joshua': '\u05d9\u05d4\u05d5\u05e9\u05e2',
    'Caleb': '\u05db\u05dc\u05d1',
    'Bezalel': '\u05d1\u05e6\u05dc\u05d0\u05dc',
    'Jethro': '\u05d9\u05ea\u05e8\u05d5',
    'Zipporah': '\u05e6\u05e4\u05e8\u05d4',
    'Gershom': '\u05d2\u05e8\u05e9\u05dd',

    # Judges
    'Deborah': '\u05d3\u05d1\u05d5\u05e8\u05d4',
    'Gideon': '\u05d2\u05d3\u05e2\u05d5\u05df',
    'Samson': '\u05e9\u05de\u05e9\u05d5\u05df',
    'Delilah': '\u05d3\u05dc\u05d9\u05dc\u05d4',
    'Jephthah': '\u05d9\u05e4\u05ea\u05d7',

    # Ruth
    'Ruth': '\u05e8\u05d5\u05ea',
    'Boaz': '\u05d1\u05e2\u05d6',
    'Naomi': '\u05e0\u05e2\u05de\u05d9',
    'Obed': '\u05e2\u05d5\u05d1\u05d3',

    # Samuel/Kings
    'Samuel': '\u05e9\u05de\u05d5\u05d0\u05dc',
    'Saul': '\u05e9\u05d0\u05d5\u05dc',
    'David': '\u05d3\u05d5\u05d3',
    'Jonathan': '\u05d9\u05d4\u05d5\u05e0\u05ea\u05df',
    'Solomon': '\u05e9\u05dc\u05de\u05d4',
    'Bathsheba': '\u05d1\u05ea\u05e9\u05d1\u05e2',
    'Absalom': '\u05d0\u05d1\u05e9\u05dc\u05d5\u05dd',
    'Goliath': '\u05d2\u05dc\u05d9\u05ea',
    'Nathan': '\u05e0\u05ea\u05df',
    'Joab': '\u05d9\u05d5\u05d0\u05d1',
    'Abner': '\u05d0\u05d1\u05e0\u05e8',
    'Michal': '\u05de\u05d9\u05db\u05dc',
    'Abigail': '\u05d0\u05d1\u05d9\u05d2\u05d9\u05dc',
    'Elijah': '\u05d0\u05dc\u05d9\u05d4\u05d5',
    'Elisha': '\u05d0\u05dc\u05d9\u05e9\u05e2',
    'Jezebel': '\u05d0\u05d9\u05d6\u05d1\u05dc',
    'Ahab': '\u05d0\u05d7\u05d0\u05d1',
    'Jeroboam': '\u05d9\u05e8\u05d1\u05e2\u05dd',
    'Rehoboam': '\u05e8\u05d7\u05d1\u05e2\u05dd',
    'Hezekiah': '\u05d7\u05d6\u05e7\u05d9\u05d4\u05d5',
    'Josiah': '\u05d9\u05d0\u05e9\u05d9\u05d4\u05d5',

    # Prophets
    'Isaiah': '\u05d9\u05e9\u05e2\u05d9\u05d4\u05d5',
    'Jeremiah': '\u05d9\u05e8\u05de\u05d9\u05d4\u05d5',
    'Ezekiel': '\u05d9\u05d7\u05d6\u05e7\u05d0\u05dc',
    'Daniel': '\u05d3\u05e0\u05d9\u05d0\u05dc',
    'Hosea': '\u05d4\u05d5\u05e9\u05e2',
    'Joel': '\u05d9\u05d5\u05d0\u05dc',
    'Amos': '\u05e2\u05de\u05d5\u05e1',
    'Obadiah': '\u05e2\u05d1\u05d3\u05d9\u05d4',
    'Jonah': '\u05d9\u05d5\u05e0\u05d4',
    'Micah': '\u05de\u05d9\u05db\u05d4',
    'Nahum': '\u05e0\u05d7\u05d5\u05dd',
    'Habakkuk': '\u05d7\u05d1\u05e7\u05d5\u05e7',
    'Zephaniah': '\u05e6\u05e4\u05e0\u05d9\u05d4',
    'Haggai': '\u05d7\u05d2\u05d9',
    'Zechariah': '\u05d6\u05db\u05e8\u05d9\u05d4',
    'Malachi': '\u05de\u05dc\u05d0\u05db\u05d9',

    # Post-exile
    'Ezra': '\u05e2\u05d6\u05e8\u05d0',
    'Nehemiah': '\u05e0\u05d7\u05de\u05d9\u05d4',
    'Esther': '\u05d0\u05e1\u05ea\u05e8',
    'Mordecai': '\u05de\u05e8\u05d3\u05db\u05d9',
    'Job': '\u05d0\u05d9\u05d5\u05d1',

    # Places
    'Eden': '\u05e2\u05d3\u05df',
    'Babel': '\u05d1\u05d1\u05dc',
    'Canaan': '\u05db\u05e0\u05e2\u05df',
    'Egypt': '\u05de\u05e6\u05e8\u05d9\u05dd',
    'Sodom': '\u05e1\u05d3\u05dd',
    'Gomorrah': '\u05e2\u05de\u05e8\u05d4',
    'Bethel': '\u05d1\u05d9\u05ea\u05d0\u05dc',
    'Bethlehem': '\u05d1\u05d9\u05ea\u05dc\u05d7\u05dd',
    'Jerusalem': '\u05d9\u05e8\u05d5\u05e9\u05dc\u05dd',
    'Sinai': '\u05e1\u05d9\u05e0\u05d9',
    'Zion': '\u05e6\u05d9\u05d5\u05df',
    'Jordan': '\u05d9\u05e8\u05d3\u05df',
    'Hebron': '\u05d7\u05d1\u05e8\u05d5\u05df',
    'Jericho': '\u05d9\u05e8\u05d9\u05d7\u05d5',
    'Gilead': '\u05d2\u05dc\u05e2\u05d3',
    'Samaria': '\u05e9\u05de\u05e8\u05d5\u05df',
    'Nineveh': '\u05e0\u05d9\u05e0\u05d5\u05d4',
    'Babylon': '\u05d1\u05d1\u05dc',
    'Assyria': '\u05d0\u05e9\u05d5\u05e8',
    'Persia': '\u05e4\u05e8\u05e1',
    'Lebanon': '\u05dc\u05d1\u05e0\u05d5\u05df',
    'Edom': '\u05d0\u05d3\u05d5\u05dd',
    'Moab': '\u05de\u05d5\u05d0\u05d1',
    'Ammon': '\u05e2\u05de\u05d5\u05df',
    'Midian': '\u05de\u05d3\u05d9\u05df',
    'Shiloh': '\u05e9\u05d9\u05dc\u05d4',
    'Shechem': '\u05e9\u05db\u05dd',
    'Beersheba': '\u05d1\u05d0\u05e8\u05e9\u05d1\u05e2',
    'Ai': '\u05e2\u05d9',
    'Tyre': '\u05e6\u05e8',
    'Sidon': '\u05e6\u05d9\u05d3\u05d5\u05df',
    'Damascus': '\u05d3\u05de\u05e9\u05e7',
    'Carmel': '\u05db\u05e8\u05de\u05dc',
    'Tabor': '\u05ea\u05d1\u05d5\u05e8',
    'Hermon': '\u05d7\u05e8\u05de\u05d5\u05df',
    'Negev': '\u05e0\u05d2\u05d1',
    'Sharon': '\u05e9\u05e8\u05d5\u05df',
    'Ophir': '\u05d0\u05d5\u05e4\u05d9\u05e8',
    'Tarshish': '\u05ea\u05e8\u05e9\u05d9\u05e9',
    'Shinar': '\u05e9\u05e0\u05e2\u05e8',

    # Rivers
    'Euphrates': '\u05e4\u05e8\u05ea',
    'Tigris': '\u05d7\u05d3\u05e7\u05dc',
    'Pishon': '\u05e4\u05d9\u05e9\u05d5\u05df',
    'Gihon': '\u05d2\u05d9\u05d7\u05d5\u05df',

    # Genesis peoples/descendants
    'Cush': '\u05db\u05d5\u05e9',
    'Nimrod': '\u05e0\u05de\u05e8\u05d3',
    'Asshur': '\u05d0\u05e9\u05d5\u05e8',
    'Aram': '\u05d0\u05e8\u05dd',
    'Lot': '\u05dc\u05d5\u05d8',
    'Melchizedek': '\u05de\u05dc\u05db\u05d9\u05e6\u05d3\u05e7',
    'Laban': '\u05dc\u05d1\u05df',
    'Esau': '\u05e2\u05e9\u05d5',
    'Amalek': '\u05e2\u05de\u05dc\u05e7',

    # Table of Nations (Genesis 10)
    'Gomer': '\u05d2\u05de\u05e8',
    'Magog': '\u05de\u05d2\u05d5\u05d2',
    'Madai': '\u05de\u05d3\u05d9',
    'Javan': '\u05d9\u05d5\u05df',
    'Tubal': '\u05ea\u05d1\u05dc',
    'Meshech': '\u05de\u05e9\u05da',
    'Tiras': '\u05ea\u05d9\u05e8\u05e1',
    'Ashkenaz': '\u05d0\u05e9\u05db\u05e0\u05d6',
    'Riphath': '\u05e8\u05d9\u05e4\u05ea',
    'Togarmah': '\u05ea\u05d5\u05d2\u05e8\u05de\u05d4',
    'Elishah': '\u05d0\u05dc\u05d9\u05e9\u05d4',
    'Kittim': '\u05db\u05ea\u05d9\u05dd',
    'Dodanim': '\u05d3\u05d5\u05d3\u05e0\u05d9\u05dd',
    'Rodanim': '\u05e8\u05d5\u05d3\u05e0\u05d9\u05dd',
    'Mizraim': '\u05de\u05e6\u05e8\u05d9\u05dd',
    'Put': '\u05e4\u05d5\u05d8',
    'Seba': '\u05e1\u05d1\u05d0',
    'Sabtah': '\u05e1\u05d1\u05ea\u05d4',
    'Raamah': '\u05e8\u05e2\u05de\u05d4',
    'Sabteca': '\u05e1\u05d1\u05ea\u05db\u05d0',
    'Sheba': '\u05e9\u05d1\u05d0',
    'Dedan': '\u05d3\u05d3\u05df',
    'Nimrod': '\u05e0\u05de\u05e8\u05d3',
    'Erech': '\u05d0\u05e8\u05da',
    'Accad': '\u05d0\u05db\u05d3',
    'Calneh': '\u05db\u05dc\u05e0\u05d4',
    'Calah': '\u05db\u05dc\u05d7',
    'Rehoboth': '\u05e8\u05d7\u05d1\u05d5\u05ea',
    'Resen': '\u05e8\u05e1\u05df',
    'Heth': '\u05d7\u05ea',
    'Eber': '\u05e2\u05d1\u05e8',
    'Elam': '\u05e2\u05d9\u05dc\u05dd',
    'Lud': '\u05dc\u05d5\u05d3',
    'Peleg': '\u05e4\u05dc\u05d2',
    'Joktan': '\u05d9\u05e7\u05d8\u05df',
    'Almodad': '\u05d0\u05dc\u05de\u05d5\u05d3\u05d3',
    'Sheleph': '\u05e9\u05dc\u05e3',
    'Hazarmaveth': '\u05d7\u05e6\u05e8\u05de\u05d5\u05ea',
    'Jerah': '\u05d9\u05e8\u05d7',
    'Hadoram': '\u05d4\u05d3\u05d5\u05e8\u05dd',
    'Uzal': '\u05d0\u05d5\u05d6\u05dc',
    'Diklah': '\u05d3\u05e7\u05dc\u05d4',
    'Obal': '\u05e2\u05d5\u05d1\u05dc',
    'Abimael': '\u05d0\u05d1\u05d9\u05de\u05d0\u05dc',
    'Jobab': '\u05d9\u05d5\u05d1\u05d1',
    'Mesha': '\u05de\u05e9\u05d0',
    'Sephar': '\u05e1\u05e4\u05e8',

    # More Genesis names
    'Ararat': '\u05d0\u05e8\u05e8\u05d8',
    'Nod': '\u05e0\u05d5\u05d3',
    'Irad': '\u05e2\u05d9\u05e8\u05d3',
    'Mehujael': '\u05de\u05d7\u05d5\u05d9\u05d0\u05dc',
    'Methusael': '\u05de\u05ea\u05d5\u05e9\u05d0\u05dc',
    'Adah': '\u05e2\u05d3\u05d4',
    'Zillah': '\u05e6\u05dc\u05d4',
    'Jabal': '\u05d9\u05d1\u05dc',
    'Jubal': '\u05d9\u05d5\u05d1\u05dc',
    'Naamah': '\u05e0\u05e2\u05de\u05d4',
    'Havilah': '\u05d7\u05d5\u05d9\u05dc\u05d4',
    'Nahor': '\u05e0\u05d7\u05d5\u05e8',
    'Terah': '\u05ea\u05e8\u05d7',
    'Milcah': '\u05de\u05dc\u05db\u05d4',
    'Bethuel': '\u05d1\u05ea\u05d5\u05d0\u05dc',
    'Keturah': '\u05e7\u05d8\u05d5\u05e8\u05d4',
    'Zilpah': '\u05d6\u05dc\u05e4\u05d4',
    'Bilhah': '\u05d1\u05dc\u05d4\u05d4',
    'Ephraim': '\u05d0\u05e4\u05e8\u05d9\u05dd',
    'Manasseh': '\u05de\u05e0\u05e9\u05d4',

    # Numbers
    'Balaam': '\u05d1\u05dc\u05e2\u05dd',
    'Balak': '\u05d1\u05dc\u05e7',
    'Korah': '\u05e7\u05e8\u05d7',
    'Phinehas': '\u05e4\u05d9\u05e0\u05d7\u05e1',
    'Eleazar': '\u05d0\u05dc\u05e2\u05d6\u05e8',

    # More tribal/place names
    'Gilgal': '\u05d2\u05dc\u05d2\u05dc',
    'Hazor': '\u05d7\u05e6\u05d5\u05e8',
    'Megiddo': '\u05de\u05d2\u05d3\u05d5',
    'Bashan': '\u05d1\u05e9\u05df',
    'Horeb': '\u05d7\u05e8\u05d1',
    'Kadesh': '\u05e7\u05d3\u05e9',
    'Peniel': '\u05e4\u05e0\u05d9\u05d0\u05dc',
    'Moriah': '\u05de\u05e8\u05d9\u05d4',
    'Mamre': '\u05de\u05de\u05e8\u05d0',
    'Dothan': '\u05d3\u05ea\u05df',
    'Goshen': '\u05d2\u05e9\u05df',
    'Ramah': '\u05e8\u05de\u05d4',

    # Kings/Chronicles era
    'Haman': '\u05d4\u05de\u05df',
    'Vashti': '\u05d5\u05e9\u05ea\u05d9',
    'Cyrus': '\u05db\u05d5\u05e8\u05e9',
    'Nebuchadnezzar': '\u05e0\u05d1\u05d5\u05db\u05d3\u05e0\u05e6\u05e8',
    'Belshazzar': '\u05d1\u05dc\u05e9\u05d0\u05e6\u05e8',
    'Darius': '\u05d3\u05e8\u05d9\u05d5\u05e9',

    # J-names (English J = Hebrew Yod)
    'Jesse': '\u05d9\u05e9\u05d9',        # yod-shin-yod
    'Jael': '\u05d9\u05e2\u05dc',         # yod-ayin-lamed
    'Joash': '\u05d9\u05d5\u05d0\u05e9',  # yod-vav-aleph-shin
    'Jehu': '\u05d9\u05d4\u05d5\u05d0',   # yod-he-vav-aleph
    'Jair': '\u05d9\u05d0\u05d9\u05e8',   # yod-aleph-yod-resh
    'Jabin': '\u05d9\u05d1\u05d9\u05df',  # yod-bet-yod-nun
    'Jehoiada': '\u05d9\u05d4\u05d5\u05d9\u05d3\u05e2',  # yod-he-vav-yod-dalet-ayin
    'Jehoahaz': '\u05d9\u05d4\u05d5\u05d0\u05d7\u05d6',  # yod-he-vav-aleph-chet-zayin
    'Joram': '\u05d9\u05d5\u05e8\u05dd',  # yod-vav-resh-mem
    'Jonadab': '\u05d9\u05d5\u05e0\u05d3\u05d1',  # yod-vav-nun-dalet-bet
    'Joah': '\u05d9\u05d5\u05d0\u05d7',   # yod-vav-aleph-chet
    'Jabez': '\u05d9\u05e2\u05d1\u05e5',  # yod-ayin-bet-tsade
    'Jeroham': '\u05d9\u05e8\u05d7\u05dd', # yod-resh-chet-mem
    'Abijah': '\u05d0\u05d1\u05d9\u05d4',  # aleph-bet-yod-he
    'Ahijah': '\u05d0\u05d7\u05d9\u05d4',  # aleph-chet-yod-he
    'Jeshurun': '\u05d9\u05e9\u05e8\u05d5\u05df',  # yod-shin-resh-vav-nun
    'Jochebed': '\u05d9\u05d5\u05db\u05d1\u05d3',  # yod-vav-kaf-bet-dalet
    'Zippor': '\u05e6\u05e4\u05d5\u05e8',  # tsade-pe-vav-resh
    'Jemuel': '\u05d9\u05de\u05d5\u05d0\u05dc',  # yod-mem-vav-aleph-lamed
    'Jamin': '\u05d9\u05de\u05d9\u05df',  # yod-mem-yod-nun
    'Jezer': '\u05d9\u05e6\u05e8',        # yod-tsade-resh
    'Jetur': '\u05d9\u05d8\u05d5\u05e8',  # yod-tet-vav-resh
    'Sennacherib': '\u05e1\u05e0\u05d7\u05e8\u05d9\u05d1',  # samekh-nun-chet-resh-yod-bet
    'Artaxerxes': '\u05d0\u05e8\u05ea\u05d7\u05e9\u05e1\u05ea\u05d0',  # art-achshasta
    'Hephzibah': '\u05d7\u05e4\u05e6\u05d9\u05d1\u05d4',  # chet-pe-tsade-yod-bet-he
    'Jebus': '\u05d9\u05d1\u05d5\u05e1',  # yod-bet-vav-samekh
    'Jehonadab': '\u05d9\u05d4\u05d5\u05e0\u05d3\u05d1',  # yod-he-vav-nun-dalet-bet
    'Pedahzur': '\u05e4\u05d3\u05d4\u05e6\u05d5\u05e8',  # pe-dalet-he-tsade-vav-resh
    'Jophia': '\u05d9\u05e4\u05d9\u05e2',  # yod-pe-yod-ayin (Japhia)
    'Japhia': '\u05d9\u05e4\u05d9\u05e2',  # yod-pe-yod-ayin
    'Jarmuth': '\u05d9\u05e8\u05de\u05d5\u05ea',  # yod-resh-mem-vav-tav
    'Aijalon': '\u05d0\u05d9\u05dc\u05d5\u05df',  # aleph-yod-lamed-vav-nun
    'Joppa': '\u05d9\u05e4\u05d5',        # yod-pe-vav (Yafo)
    'Ziklag': '\u05e6\u05e7\u05dc\u05d2',  # tsade-qof-lamed-gimel
    'Kue': '\u05e7\u05d5\u05d4',          # qof-vav-he
    'Abijam': '\u05d0\u05d1\u05d9\u05dd', # aleph-bet-yod-mem
    'Ijon': '\u05e2\u05d9\u05d5\u05df',   # ayin-yod-vav-nun
    'Zelophehad': '\u05e6\u05dc\u05e4\u05d7\u05d3',  # tsade-lamed-pe-chet-dalet
    'Waheb': '\u05d5\u05d4\u05d1',        # vav-he-bet
    'Jahaz': '\u05d9\u05d4\u05e6',        # yod-he-tsade
    'Jazer': '\u05d9\u05e2\u05d6\u05e8',  # yod-ayin-zayin-resh
    'Jotbath': '\u05d9\u05d8\u05d1\u05ea',  # yod-tet-bet-tav
    'Jogli': '\u05d9\u05d2\u05dc\u05d9',  # yod-gimel-lamed-yod
    'Jeush': '\u05d9\u05e2\u05d5\u05e9',  # yod-ayin-vav-shin
    'Jalam': '\u05d9\u05e2\u05dc\u05dd',  # yod-ayin-lamed-mem
    'Jetheth': '\u05d9\u05ea\u05ea',      # yod-tav-tav
    'Zalmunna': '\u05e6\u05dc\u05de\u05e0\u05e2',  # tsade-lamed-mem-nun-ayin
    'Jerahmeel': '\u05d9\u05e8\u05d7\u05de\u05d0\u05dc',  # yod-resh-chet-mem-aleph-lamed
    'Chedorlaomer': '\u05db\u05d3\u05e8\u05dc\u05e2\u05de\u05e8',  # kedorla-omer
    'Chinnereth': '\u05db\u05e0\u05e8\u05ea',  # kaf-nun-resh-tav
    'Jokmeam': '\u05d9\u05e7\u05de\u05e2\u05dd',  # yod-qof-mem-ayin-mem
    'Huzzab': '\u05d4\u05e6\u05d1',       # he-tsade-bet
    'Aswan': '\u05e1\u05d5\u05df',        # samekh-vav-nun (Syene)
}


def load_oracle_books():
    """Load all 39 books from the Oracle's mechanical Bible database."""
    print('[>] Loading Oracle mechanical Bible books...')
    books = {}
    for book_file in BOOK_ORDER:
        filepath = os.path.join(BOOKS_DIR, f'{book_file}.json')
        if not os.path.exists(filepath):
            print(f'  [WARN] Missing: {book_file}')
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            books[book_file] = json.load(f)
    print(f'  Loaded {len(books)} books')
    return books


def load_words_json():
    """Load the mechanical-bible words.json for Hebrew lookup."""
    print('[>] Loading mechanical-bible words.json...')
    with open(WORDS_PATH, 'r', encoding='utf-8') as f:
        words = json.load(f)
    print(f'  Loaded {len(words)} Hebrew words')
    return words


def load_oracle_lexicon():
    """Load the Oracle's Hebrew lexicon for enrichment."""
    print('[>] Loading Oracle Hebrew lexicon...')
    with open(LEXICON_PATH, 'r', encoding='utf-8') as f:
        lex_data = json.load(f)
    entries = lex_data.get('entries', lex_data)
    print(f'  Loaded {len(entries)} lexicon entries')
    return entries


def extract_all_words_from_verse(english_text):
    """Extract ALL words from verse text, tracking capitalization."""
    # Remove translation notes
    text = re.sub(r'\*[^*]+\*', ' ', english_text)
    text = re.sub(r'\([^)]+\)', ' ', text)

    # Find ALL individual words
    words = re.findall(r'\b([A-Za-z][a-z]{1,}(?:-[A-Za-z][a-z]+)*)\b', text)
    return words


def extract_names_from_verse(english_text, accepted_names):
    """Extract proper names from English text using pre-computed accepted set."""
    text = re.sub(r'\*[^*]+\*', ' ', english_text)
    text = re.sub(r'\([^)]+\)', ' ', text)

    candidates = re.findall(r'\b([A-Z][a-z]{1,}(?:-[A-Z][a-z]+)*)\b', text)

    names = []
    for c in candidates:
        if c in accepted_names and len(c) > 1:
            names.append(c)
    return names


# Hebrew prefix characters that get attached to words
# These are: conjunction vav, article he, prepositions be/ke/le/me/she, accusative et
HEBREW_PREFIXES = [
    '\u05d5\u05d0\u05ea',  # ve-et (and+accusative)
    '\u05d0\u05ea',  # et (accusative marker)
    '\u05d5\u05d4',  # ve-ha (and+the)
    '\u05d5\u05d1',  # ve-be (and+in)
    '\u05d5\u05dc',  # ve-le (and+to)
    '\u05d5\u05de',  # ve-me (and+from)
    '\u05d5\u05e9',  # ve-she (and+that)
    '\u05d5',  # ve (and)
    '\u05d4',  # ha (the)
    '\u05d1',  # be (in)
    '\u05db',  # ke (like)
    '\u05dc',  # le (to)
    '\u05de',  # me (from)
    '\u05e9',  # she (that)
]


def strip_hebrew_prefix(hebrew_word):
    """Strip common Hebrew prefix characters from a word."""
    for prefix in HEBREW_PREFIXES:
        if hebrew_word.startswith(prefix) and len(hebrew_word) > len(prefix) + 1:
            return hebrew_word[len(prefix):]
    return hebrew_word


def consonant_skeleton(text):
    """Extract consonant skeleton from text (drop vowels for matching)."""
    vowels = set('aeiouAEIOU')
    result = ''
    i = 0
    t = text.lower()
    while i < len(t):
        # Handle digraphs
        if i + 1 < len(t) and t[i:i+2] in ('sh', 'th', 'ch', 'ts', 'tz', 'ph'):
            result += t[i:i+2]
            i += 2
        elif t[i] not in vowels and t[i].isalpha():
            result += t[i]
            i += 1
        else:
            i += 1
    return result


def normalize_consonants(cons):
    """Normalize consonant skeleton for cross-language matching."""
    s = cons
    s = s.replace('j', 'y')     # J -> Y (English J = Hebrew Yod)
    s = s.replace('c', 'k')     # C -> K (English C = Hebrew K/Q)
    s = s.replace('q', 'k')     # Q -> K
    s = s.replace('ph', 'p')    # PH -> P (English PH = Hebrew P)
    s = s.replace("'", '')      # Drop glottal stops
    s = s.replace('-', '')      # Drop hyphens
    s = s.replace('w', 'v')     # W -> V (English W = Hebrew Vav)
    return s


def consonant_match_score(english_name, hebrew_translit):
    """Score how well an English name matches a Hebrew transliteration."""
    eng = normalize_consonants(consonant_skeleton(english_name))
    heb = normalize_consonants(consonant_skeleton(hebrew_translit))

    if not eng or not heb:
        return 0.0

    # Exact match
    if eng == heb:
        return 1.0

    # One contains the other (prefix/suffix forms)
    if eng in heb:
        return 0.9 * len(eng) / len(heb)
    if heb in eng:
        return 0.9 * len(heb) / len(eng)

    # Ordered subsequence match
    matches = 0
    j = 0
    for c in eng:
        while j < len(heb):
            if heb[j] == c:
                matches += 1
                j += 1
                break
            j += 1

    if matches > 0:
        return matches / max(len(eng), len(heb))

    return 0.0


def find_hebrew_in_verse_words(english_name, verse_words, words_json):
    """Find Hebrew for a name by analyzing Hebrew words in the same verse."""
    if not verse_words:
        return ''

    best_match = ''
    best_score = 0.0

    name_lower = english_name.lower()

    for w in verse_words:
        hebrew_full = w['hebrew']

        # Try full form and prefix-stripped form
        forms_to_check = [hebrew_full, strip_hebrew_prefix(hebrew_full)]

        for hebrew in forms_to_check:
            if hebrew not in words_json:
                continue

            entry = words_json[hebrew]
            translit = entry.get('transliteration', '')
            freq = entry.get('frequency', 0)

            # Skip very common words (articles, conjunctions, prepositions)
            if freq > 500:
                continue

            if not translit:
                continue

            # Score this match
            score = consonant_match_score(english_name, translit)

            # Bonus: if frequency is low (rare word = likely a name)
            if freq <= 10 and score > 0.3:
                score += 0.1

            if score > best_score and score >= 0.5:
                best_match = hebrew
                best_score = score

    return best_match


def find_hebrew_for_name(english_name, words_json, lexicon, verse_words=None):
    """Find Hebrew text for an English name using multiple strategies.

    Strategies (in priority order):
    1. Hardcoded ENGLISH_TO_HEBREW mapping (most reliable)
    2. Verse-based extraction (Hebrew word in the same verse)
    3. Exact transliteration match in words.json
    4. Consonant skeleton matching across words.json
    5. Partial match on transliteration or definition
    """
    # 1. Check hardcoded mappings first (most reliable)
    if english_name in ENGLISH_TO_HEBREW:
        return ENGLISH_TO_HEBREW[english_name]

    # 2. Verse-based extraction (NEW - most powerful for unknown names)
    if verse_words:
        result = find_hebrew_in_verse_words(english_name, verse_words, words_json)
        if result:
            return result

    # 3. Search words.json by exact transliteration
    name_lower = english_name.lower()
    for hebrew, data in words_json.items():
        translit = data.get('transliteration', '').lower()
        if translit == name_lower:
            return hebrew

    # 4. Consonant skeleton matching across words.json
    best_match = ''
    best_score = 0.0
    for hebrew, data in words_json.items():
        translit = data.get('transliteration', '')
        if not translit:
            continue
        freq = data.get('frequency', 0)
        # Only consider low-frequency words (likely names)
        if freq > 100:
            continue
        score = consonant_match_score(english_name, translit)
        if score > best_score and score >= 0.65:
            best_match = hebrew
            best_score = score

    if best_match:
        return best_match

    # 5. Search lexicon by transliteration
    for hebrew, data in lexicon.items():
        translit = data.get('transliteration', '').lower()
        if translit == name_lower:
            return hebrew

    # 6. Partial match on transliteration (last resort)
    for hebrew, data in words_json.items():
        translit = data.get('transliteration', '').lower()
        if name_lower in translit and len(name_lower) >= 4:
            if len(hebrew) > 1:
                return hebrew

    return ''


def categorize_name(english_name, definition, hebrew):
    """Categorize a name as person, place, people, or other."""
    name_lower = english_name.lower()
    defn_lower = (definition or '').lower()

    # Known place names
    places = {
        'eden', 'babel', 'canaan', 'egypt', 'sodom', 'gomorrah', 'bethel',
        'bethlehem', 'jerusalem', 'sinai', 'zion', 'jordan', 'hebron',
        'jericho', 'gilead', 'samaria', 'nineveh', 'babylon', 'assyria',
        'persia', 'lebanon', 'edom', 'moab', 'ammon', 'midian', 'shiloh',
        'shechem', 'beersheba', 'ai', 'tyre', 'sidon', 'damascus',
        'carmel', 'tabor', 'hermon', 'negev', 'sharon', 'ophir',
        'tarshish', 'shinar', 'gilgal', 'hazor', 'megiddo', 'bashan',
        'horeb', 'kadesh', 'peniel', 'moriah', 'mamre', 'dothan',
        'goshen', 'ramah', 'pishon', 'gihon', 'euphrates', 'tigris',
        'ararat', 'paddan-aram', 'haran', 'ur', 'havilah',
        'nod', 'erech', 'accad', 'calneh', 'calah', 'rehoboth', 'resen',
        'mesha', 'sephar', 'sheba', 'dedan',
        'bethlehem', 'gibeah', 'gibeon', 'mizpah', 'mizpeh',
        'lachish', 'libnah', 'azekah', 'eglon', 'debir',
        'aroer', 'dibon', 'heshbon', 'jazer', 'succoth', 'mahanaim',
        'jabesh', 'jabesh-gilead', 'ramoth', 'ramoth-gilead',
        'tirzah', 'jezreel', 'dothan', 'zarephath', 'shunem',
        'anathoth', 'tekoa', 'gath', 'ekron', 'ashdod', 'ashkelon', 'gaza',
        'kedesh', 'hazor', 'aphek', 'beth-shan', 'endor',
        'gezer', 'aijalon', 'beth-horon', 'kiriath-jearim',
        'shittim', 'joppa', 'lydda', 'caesarea',
        'bethany', 'capernaum', 'nazareth', 'galilee', 'judea',
    }
    # Known peoples/nations
    peoples = {
        'cush', 'aram', 'amalek', 'philistia',
        'israelites', 'egyptians', 'canaanites', 'philistines', 'amorites',
        'hittites', 'hivites', 'jebusites', 'perizzites', 'girgashites',
        'midianites', 'moabites', 'ammonites', 'edomites', 'amalekites',
        'arameans', 'assyrians', 'babylonians', 'persians', 'greeks',
        'hebrews', 'jews', 'levites',
        'nephilim', 'rephaim', 'rephaites', 'anakim', 'anakites',
        'emim', 'zamzummim', 'horites', 'avvim', 'avvites',
        'kenites', 'kenizzites', 'kadmonites', 'rechabites',
        'nethinim', 'cherethites', 'pelethites',
        'arkites', 'sinites', 'arvadites', 'zemarites', 'hamathites',
        'ludim', 'anamim', 'lehabim', 'naphtuhim', 'pathrusim',
        'casluhim', 'caphtorim', 'cretans',
        'hittite', 'hivite', 'jebusite', 'perizzite', 'girgashite',
        'amorite', 'canaanite', 'midianite', 'moabite', 'ammonite',
        'edomite', 'amalekite', 'aramean', 'assyrian', 'babylonian',
        'ishmaelite', 'ishmaelites', 'philistine',
        'gomer', 'magog', 'madai', 'javan', 'tubal', 'meshech', 'tiras',
        'ashkenaz', 'riphath', 'togarmah', 'elishah', 'kittim',
        'dodanim', 'rodanim', 'mizraim', 'put',
    }

    if name_lower in places:
        return 'place'
    if name_lower in peoples:
        return 'people'
    if 'place' in defn_lower or 'city' in defn_lower or 'region' in defn_lower:
        return 'place'
    if 'nation' in defn_lower or 'people' in defn_lower:
        return 'people'
    return 'person'


def main():
    print('=' * 60)
    print('BIBLE NAMES DATABASE BUILDER')
    print('Two-Pass Capitalization Analysis')
    print('Using Oracle platform infrastructure')
    print('=' * 60)

    # Load data sources
    books = load_oracle_books()
    words_json = load_words_json()
    lexicon = load_oracle_lexicon()

    # ================================================================
    # PASS 1: Scan all books, count capitalized vs lowercase occurrences
    # ================================================================
    print('\n[>] PASS 1: Counting capitalization patterns across all 39 books...')

    cap_counts = Counter()   # word -> times it appears Capitalized
    low_counts = Counter()   # word -> times it appears lowercase

    for book_file in BOOK_ORDER:
        if book_file not in books:
            continue
        book_data = books[book_file]
        for verse in book_data.get('verses', []):
            english = verse.get('english_text', '')
            all_words = extract_all_words_from_verse(english)
            for word in all_words:
                if word[0].isupper():
                    cap_counts[word] += 1
                else:
                    low_counts[word.capitalize()] += 1

    # Determine which words are proper names
    # A word that ONLY appears capitalized -> almost certainly a proper name
    # A word that appears >80% capitalized -> very likely a proper name
    # A word that appears <50% capitalized -> common English word at sentence start
    accepted_names = set()
    rejected_words = set()

    all_cap_words = set(cap_counts.keys())
    print(f'  Total unique capitalized words: {len(all_cap_words)}')

    for word in all_cap_words:
        # Skip always-excluded terms
        if word in ALWAYS_EXCLUDE:
            rejected_words.add(word)
            continue

        # Force-include known biblical names
        if word in FORCE_INCLUDE:
            accepted_names.add(word)
            continue

        # Reject words with English suffixes that Hebrew names never use
        if word.lower().endswith(NON_NAME_SUFFIXES) and len(word) > 4:
            rejected_words.add(word)
            continue

        # Reject text artifacts: concatenated words (e.g., "Jesseothe", "Jordaneon")
        # These have lowercase runs of 3+ common English chars after the name portion
        # Real names with hyphens are already captured by the regex
        if len(word) > 8 and re.search(r'[a-z]{3,}[a-z]$', word):
            # Check for common artifact patterns: name + preposition/article
            artifact_suffixes = (
                'the', 'and', 'from', 'with', 'for', 'who', 'that', 'this',
                'people', 'inhabitants', 'ites', 'whole', 'bloody', 'fall',
                'neither', 'when', 'all', 'fire', 'through', 'compassionate',
            )
            word_lower = word.lower()
            is_artifact = False
            for suf in artifact_suffixes:
                if word_lower.endswith(suf) and len(word) > len(suf) + 3:
                    is_artifact = True
                    break
            # Also check for lowercase letter runs that look like English words
            # appended to names (e.g., "Egyptkfrom" has "kfrom")
            if not is_artifact and re.search(r'[a-z][a-z][a-z]{2,}$', word):
                # Count vowels in the suffix - English words have vowels
                suffix_match = re.search(r'([a-z]{4,})$', word)
                if suffix_match:
                    suffix = suffix_match.group(1)
                    vowel_count = sum(1 for c in suffix if c in 'aeiou')
                    if vowel_count >= 1 and len(suffix) >= 4:
                        is_artifact = True
            if is_artifact:
                rejected_words.add(word)
                continue

        cap = cap_counts[word]
        low = low_counts.get(word, 0)
        total = cap + low

        if low == 0:
            # ONLY appears capitalized -> proper name
            accepted_names.add(word)
        elif total >= 3 and cap / total > 0.8:
            # Appears >80% capitalized with enough samples -> likely name
            accepted_names.add(word)
        elif total >= 3 and cap / total <= 0.3:
            # Appears mostly lowercase -> common word
            rejected_words.add(word)
        elif total < 3 and low == 0:
            # Rare word, only capitalized -> accept
            accepted_names.add(word)
        else:
            # Ambiguous - skip (could add manual review later)
            rejected_words.add(word)

    print(f'  Accepted as names: {len(accepted_names)}')
    print(f'  Rejected as common words: {len(rejected_words)}')

    # ================================================================
    # PASS 2: Extract accepted names with first-appearance tracking
    # ================================================================
    print('\n[>] PASS 2: Extracting names with first-appearance tracking...')

    names_found = {}  # english -> {data}
    appearance_order = []

    for book_file in BOOK_ORDER:
        if book_file not in books:
            continue

        book_data = books[book_file]
        book_name = BOOK_DISPLAY.get(book_file, book_file)
        new_in_book = 0

        for verse in book_data.get('verses', []):
            english = verse.get('english_text', '')
            chapter = verse.get('chapter', 0)
            verse_num = verse.get('verse', 0)
            verse_words = verse.get('words', [])

            eng_names = extract_names_from_verse(english, accepted_names)

            for name in eng_names:
                if name not in names_found:
                    names_found[name] = {
                        'english': name,
                        'book': book_name,
                        'chapter': chapter,
                        'verse': verse_num,
                        'verse_words': verse_words,
                    }
                    appearance_order.append(name)
                    new_in_book += 1

        print(f'  {book_name}: {new_in_book} new names')

    print(f'\n  Total unique names: {len(names_found)}')

    # Map to Hebrew and enrich
    print('\n[>] Mapping names to Hebrew text (with verse-based extraction)...')
    hebrew_found = 0
    for name in appearance_order:
        data = names_found[name]
        verse_words = data.pop('verse_words', [])  # Remove from data, pass to lookup
        hebrew = find_hebrew_for_name(name, words_json, lexicon, verse_words=verse_words)
        if hebrew:
            data['hebrew'] = hebrew
            data['gematria'] = calc_gematria(hebrew)
            data['digital_root'] = digital_root(data['gematria'])

            # Get letter breakdown
            letters = []
            for ch in hebrew:
                if ch in HEBREW_VALUES:
                    letters.append({
                        'letter': ch,
                        'value': HEBREW_VALUES[ch]
                    })
            data['letters'] = letters
            hebrew_found += 1

            # Try to get definition from lexicon
            if hebrew in lexicon:
                lex_entry = lexicon[hebrew]
                data['definition'] = lex_entry.get('definition', '')
                data['strongs'] = lex_entry.get('strongs', '')
                data['transliteration'] = lex_entry.get('transliteration', '')
            elif hebrew in words_json:
                w_entry = words_json[hebrew]
                data['definition'] = w_entry.get('definition', '')
                data['strongs'] = w_entry.get('strongs', '')
                data['transliteration'] = w_entry.get('transliteration', '')
        else:
            data['hebrew'] = ''
            data['gematria'] = 0
            data['digital_root'] = 0
            data['letters'] = []

        # Categorize
        data['category'] = categorize_name(
            name, data.get('definition', ''), data.get('hebrew', ''))

    print(f'  Names with Hebrew: {hebrew_found}/{len(names_found)}')

    # Build output JSON matching names.html expected format
    print('\n[>] Building output JSON...')
    names_list = []
    for i, name in enumerate(appearance_order, 1):
        data = names_found[name]
        hebrew = data.get('hebrew', '')

        # Get pictographic meaning from words.json if available
        pictographic = ''
        if hebrew and hebrew in words_json:
            pictographic = words_json[hebrew].get('pictographic', '')

        entry = {
            'order': i,
            'english': data['english'],
            'hebrew': hebrew,
            'transliteration': data.get('transliteration', ''),
            'strongs': data.get('strongs', ''),
            'definition': data.get('definition', ''),
            'gematria': data.get('gematria', 0),
            'digital_root': data.get('digital_root', 0),
            'letters': data.get('letters', []),
            'category': data.get('category', 'person'),
            'first_occurrence': f"{data['book']} {data['chapter']}:{data['verse']}",
            'pictographic': pictographic,
        }
        names_list.append(entry)

    # Wrap in structure matching what names.html expects
    output = {
        'meta': {
            'total_names': len(names_list),
            'found_in_words_json': hebrew_found,
            'scope': '39 books of the Old Testament (Hebrew Bible)',
            'persons': sum(1 for e in names_list if e['category'] == 'person'),
            'places': sum(1 for e in names_list if e['category'] == 'place'),
            'peoples': sum(1 for e in names_list if e['category'] == 'people'),
        },
        'names': names_list,
    }

    # Write output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'\n{"=" * 60}')
    print(f'COMPLETE')
    print(f'{"=" * 60}')
    print(f'Total names: {len(names_list)}')
    print(f'With Hebrew: {hebrew_found}')
    print(f'Persons: {output["meta"]["persons"]}')
    print(f'Places: {output["meta"]["places"]}')
    print(f'Peoples: {output["meta"]["peoples"]}')
    print(f'Output: {OUTPUT_PATH}')

    # Show first 30
    print(f'\nFirst 30 names:')
    for entry in names_list[:30]:
        h = entry['hebrew'] or '?'
        g = entry['gematria']
        cat = entry['category'][:3]
        print(f"  {entry['order']:4d}. {entry['english']:20s} {h:>12s} g={g:5d} [{cat}] {entry['first_occurrence']}")


if __name__ == '__main__':
    main()
