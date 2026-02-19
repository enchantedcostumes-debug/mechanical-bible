#!/usr/bin/env python3
"""
Fix words.json definitions using AHLB Strong's dictionary.
Applies proper definitions from ahlb_strongs.json with manual overrides
for common words where AHLB I./II. ordering doesn't match Strong's numbers.
"""
import json
import re
import csv
from pathlib import Path

BASE = Path(__file__).parent.parent
WORDS_JSON = BASE / 'words.json'
AHLB_JSON = BASE / 'tools' / 'ahlb_strongs.json'
VERSES_CSV = Path(r'C:\flask-structural-api\services\rosetta_stone\data\tanakh_COMPLETE_verses.csv')

# Manual overrides for common words where AHLB I./II. ordering is wrong
OVERRIDES = {
    'H853': 'Direct object marker: Indicator of the direct object. Also: with.',
    'H834': 'Which: Or who, what or that.',
    'H835': 'Happy: One who is happy is one whose life is lived straightly.',
    'H3808': 'Not: A lacking or absence.',
    'H3863': 'If: To have what you are without.',
    'H4994': 'Please: A pleading or request for something.',
    'H4995': 'Raw: Meat that is not fit for consumption.',
    'H8064': 'Skies: The upper region above.',
    'H3068': 'YHWH: The proper name of the God of Israel.',
    'H559': 'Say: To bring forth sayings.',
    'H1696': 'Speak: A careful arrangement of words or commands.',
    'H6547': 'Pharaoh: Title of the king of Egypt.',
    'H5680': 'Hebrew: One who has crossed over.',
    'H2719': 'Sword: A weapon used to lay waste a city.',
    'H2717': 'Waste: A dry wasteland, desolate.',
    'H3117': 'Day: A day unit, from sunset to sunset.',
    'H3220': 'Sea: A large body of water.',
    'H413': 'Toward: A moving toward a goal.',
    'H430': 'Power: The power or might of one who rules or teaches. One who yokes with another.',
    'H5921': 'Upon: To be on or above.',
    'H3478': 'He will rule as God: The name of Jacob and his descendants.',
    'H1980': 'Walk: To walk or go.',
    'H935': 'Come: To fill a void by entering it. To come or go.',
    'H7200': 'See: To see, perceive, look.',
    'H8085': 'Hear: To listen, perceive by the ear.',
    'H3045': 'Know: To have an intimate relationship with another person, idea or experience.',
    'H5414': 'Give: To give or place.',
    'H3947': 'Take: To receive something given or to take something.',
    'H7971': 'Send: To send or stretch out.',
    'H5975': 'Stand: To stand upright, be established.',
    'H7725': 'Turn back: To return to a previous place or state.',
    'H3318': 'Go out: To go or come out.',
    'H5927': 'Go up: To ascend, go up, climb.',
    'H3381': 'Go down: To descend, go down.',
    'H6440': 'Face: The face of a person.',
    'H3027': 'Hand: The hand of man.',
    'H5869': 'Eye: The eye of man.',
    'H1121': 'Son: One who continues the family line.',
    'H1004': 'House: The house or tent as focus of the family.',
    'H376': 'Man: The male gender.',
    'H802': 'Woman: The female gender. Also: fire.',
    'H1': 'Father: The switching father.',
    'H517': 'Mother: One who binds the family.',
    'H251': 'Brother: One who is united to another.',
    'H776': 'Land: The whole of the earth or a region.',
    'H4325': 'Water: The liquid of flowing water.',
    'H1697': 'Word: An arrangement of words. Also: thing, matter.',
    'H4057': 'Wilderness: A place of order, an open area. Also: speech.',
    'H6963': 'Voice: The sound of the voice.',
}


def shorten_def(definition):
    if not definition:
        return '?'
    if ':' in definition:
        short = definition.split(':')[0].strip()
        if short:
            short = re.sub(r'^\[(.+)\]$', r'\\1', short)
            return short
    d = re.sub(r'\s*\(.*?\)', '', definition)
    parts = re.split(r'[;,.]', d)
    return parts[0].strip() or '?'


def main():
    # Load AHLB dictionary
    with open(AHLB_JSON, 'r', encoding='utf-8') as f:
        ahlb = json.load(f)

    # Apply overrides
    for snum, definition in OVERRIDES.items():
        ahlb[snum] = definition

    # Load words.json
    with open(WORDS_JSON, 'r', encoding='utf-8') as f:
        words = json.load(f)

    # Apply AHLB definitions to words.json
    updated = 0
    for w, entry in words.items():
        strongs = entry.get('strongs', '')
        if not strongs:
            continue
        base = re.sub(r'_.*$', '', strongs)
        if base in ahlb:
            ahlb_def = ahlb[base]
            if ahlb_def and len(ahlb_def) > 3:
                entry['definition'] = ahlb_def
                updated += 1

    # Fix compound words with "in, with, by X" prefix descriptions
    for w, entry in words.items():
        d = entry.get('definition', '')
        if d.startswith('in, with, by '):
            root_name = d[13:].strip()
            entry['definition'] = root_name

    print(f'Updated {updated} words from AHLB')

    # Save
    with open(WORDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, separators=(',', ':'))
    print('Saved words.json')

    # Preview
    with open(VERSES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['book'] == 'Genesis' and row['chapter'] == '1' and row['verse'] == '1':
                heb_words = row['hebrew'].split()
                pairs = []
                for hw in heb_words:
                    e = words.get(hw)
                    if e and e.get('definition'):
                        eng = shorten_def(e['definition'])
                        pairs.append(f'{hw}({eng})')
                    else:
                        pairs.append(f'{hw}(?)')
                print(f'\nGenesis 1:1: {" ".join(pairs)}')
                break

    with open(VERSES_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['book'] == 'Exodus' and row['chapter'] == '5' and row['verse'] in ['1', '2', '3']:
                heb_words = row['hebrew'].split()
                pairs = []
                for hw in heb_words:
                    e = words.get(hw)
                    if e and e.get('definition'):
                        eng = shorten_def(e['definition'])
                        pairs.append(f'{hw}({eng})')
                    else:
                        pairs.append(f'{hw}(?)')
                print(f'Exodus 5:{row["verse"]}: {" ".join(pairs)}')

    # Save updated AHLB too
    with open(AHLB_JSON, 'w', encoding='utf-8') as f:
        json.dump(ahlb, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()
