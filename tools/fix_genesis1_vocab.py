#!/usr/bin/env python3
"""Fix critical vocabulary for Genesis 1 translations."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
WORDS_JSON = BASE_DIR / 'words.json'

with open(WORDS_JSON, 'r', encoding='utf-8') as f:
    words = json.load(f)

fixes = {
    # === FIX: ויברא is from ברא (shape), NOT ברך (kneel/bless) ===
    'ויברא': {'definition': 'And he shaped', 'mechanical_translation': 'and~he~will~SHAPE(V)', 'rmt_translation': 'and shaped'},

    # === ORDINAL NUMBERS (פ is paragraph/section marker) ===
    'שלישיפ': {'definition': 'Third', 'mechanical_translation': 'THIRD', 'rmt_translation': 'a third'},
    'רביעיפ': {'definition': 'Fourth', 'mechanical_translation': 'FOURTH', 'rmt_translation': 'a fourth'},
    'חמישיפ': {'definition': 'Fifth', 'mechanical_translation': 'FIFTH', 'rmt_translation': 'a fifth'},
    'ששיפ': {'definition': 'Sixth', 'mechanical_translation': 'SIXTH', 'rmt_translation': 'the sixth'},
    'שביעיפ': {'definition': 'Seventh', 'mechanical_translation': 'SEVENTH', 'rmt_translation': 'the seventh'},

    # === KEY VERBS ===
    'ויתן': {'definition': 'And he gave', 'mechanical_translation': 'and~he~will~GIVE(V)', 'rmt_translation': 'and gave'},
    'ישרצו': {'definition': 'They will swarm', 'mechanical_translation': 'they~will~SWARM(V)', 'rmt_translation': 'will swarm'},
    'שרצו': {'definition': 'They swarmed', 'mechanical_translation': 'SWARM(V)~ed', 'rmt_translation': 'swarmed'},
    'יעופף': {'definition': 'Will fly', 'mechanical_translation': 'he~will~FLY(V)', 'rmt_translation': 'will fly'},
    'תוצא': {'definition': 'She will bring forth', 'mechanical_translation': 'she~will~GO.OUT(V)', 'rmt_translation': 'will bring forth'},
    'ותוצא': {'definition': 'And she brought forth', 'mechanical_translation': 'and~she~will~GO.OUT(V)', 'rmt_translation': 'and brought forth'},
    'ירב': {'definition': 'He will increase', 'mechanical_translation': 'he~will~INCREASE(V)', 'rmt_translation': 'will increase'},
    'פרו': {'definition': 'Bear fruit', 'mechanical_translation': 'PRODUCE(V)~you(mp)', 'rmt_translation': 'bear fruit'},
    'ורבו': {'definition': 'And increase', 'mechanical_translation': 'and~INCREASE(V)~you(mp)', 'rmt_translation': 'and increase'},
    'ומלאו': {'definition': 'And fill', 'mechanical_translation': 'and~FILL(V)~you(mp)', 'rmt_translation': 'and fill'},
    'ירדו': {'definition': 'They will rule', 'mechanical_translation': 'they~will~DESCEND(V)', 'rmt_translation': 'and rule'},
    'נעשה': {'definition': 'We will make', 'mechanical_translation': 'we~will~DO(V)', 'rmt_translation': 'we will make'},
    'וכבשה': {'definition': 'And subdue her', 'mechanical_translation': 'and~SUBDUE(V)~her', 'rmt_translation': 'and subdue her'},

    # === KEY NOUNS ===
    'מארת': {'definition': 'Luminaries', 'mechanical_translation': 'LUMINARY~s', 'rmt_translation': 'luminaries'},
    'המארת': {'definition': 'The luminaries', 'mechanical_translation': 'the~LUMINARY~s', 'rmt_translation': 'the luminaries'},
    'למאורת': {'definition': 'For luminaries', 'mechanical_translation': 'to~LUMINARY~s', 'rmt_translation': 'for luminaries'},
    'לממשלת': {'definition': 'For ruling', 'mechanical_translation': 'to~RULE', 'rmt_translation': 'to rule'},
    'ממשלת': {'definition': 'Ruling, dominion', 'mechanical_translation': 'RULE', 'rmt_translation': 'ruling'},
    'משל': {'definition': 'Rule: To have dominion or authority over.', 'mechanical_translation': 'RULE(V)', 'rmt_translation': 'rule'},
    'ולמשל': {'definition': 'And to rule', 'mechanical_translation': 'and~to~RULE(V)', 'rmt_translation': 'and to rule'},
    'בהמה': {'definition': 'Beast: A mute animal.', 'mechanical_translation': 'BEAST', 'rmt_translation': 'beast'},
    'כנף': {'definition': 'Wing: The wing of a bird used for flight.', 'mechanical_translation': 'WING', 'rmt_translation': 'wing'},
    'כל': {'definition': 'All: The whole of something.', 'mechanical_translation': 'ALL', 'rmt_translation': 'every'},
    'תנין': {'definition': 'Serpent: A large sea creature.', 'mechanical_translation': 'SERPENT', 'rmt_translation': 'serpent'},
    'רמש': {'definition': 'Creep: To move slowly along the ground.', 'mechanical_translation': 'CREEP(V)', 'rmt_translation': 'creeping thing'},
    'ורמש': {'definition': 'And creeping thing', 'mechanical_translation': 'and~CREEP(V)', 'rmt_translation': 'and creeping thing'},
    'שרץ': {'definition': 'Swarm: To move or gather in large numbers.', 'mechanical_translation': 'SWARM(V)', 'rmt_translation': 'swarming thing'},
    'עוף': {'definition': 'Flyer: A flying creature with wings.', 'mechanical_translation': 'FLYER', 'rmt_translation': 'flyer'},
    'והעוף': {'definition': 'And the flyer', 'mechanical_translation': 'and~the~FLYER', 'rmt_translation': 'and the flyer'},
    'קטן': {'definition': 'Small: Something that is small or insignificant.', 'mechanical_translation': 'SMALL', 'rmt_translation': 'small'},
    'הקטן': {'definition': 'The small', 'mechanical_translation': 'the~SMALL', 'rmt_translation': 'the small'},
    'שנה': {'definition': 'Year: A period of repeating seasons.', 'mechanical_translation': 'YEAR', 'rmt_translation': 'year'},
    'ושנים': {'definition': 'And years', 'mechanical_translation': 'and~YEAR~s', 'rmt_translation': 'and years'},
    'מועד': {'definition': 'Appointment: A fixed time or season.', 'mechanical_translation': 'APPOINTMENT', 'rmt_translation': 'appointed time'},
    'אות': {'definition': 'Mark: A sign of an agreement.', 'mechanical_translation': 'MARK', 'rmt_translation': 'sign'},
    'לאתת': {'definition': 'For signs', 'mechanical_translation': 'to~MARK~s', 'rmt_translation': 'for signs'},
    'דמות': {'definition': 'Likeness: A pattern or image.', 'mechanical_translation': 'LIKENESS', 'rmt_translation': 'likeness'},
    'צלם': {'definition': 'Image: A representation.', 'mechanical_translation': 'IMAGE', 'rmt_translation': 'image'},
    'בצלמנו': {'definition': 'In our image', 'mechanical_translation': 'in~IMAGE~us', 'rmt_translation': 'in our image'},
    'כדמותנו': {'definition': 'Like our likeness', 'mechanical_translation': 'like~LIKENESS~us', 'rmt_translation': 'like our likeness'},
    'דגה': {'definition': 'Fish', 'mechanical_translation': 'FISH', 'rmt_translation': 'fish'},
    'דגת': {'definition': 'Fish of', 'mechanical_translation': 'FISH~of', 'rmt_translation': 'fish of'},
    'בדגת': {'definition': 'In the fish of', 'mechanical_translation': 'in~FISH~of', 'rmt_translation': 'over the fish of'},
    'ובבהמה': {'definition': 'And in the beast', 'mechanical_translation': 'and~in~BEAST', 'rmt_translation': 'and over the beast'},
    'ובכלהארץ': {'definition': 'And in all the land', 'mechanical_translation': 'and~in~ALL the~LAND', 'rmt_translation': 'and over all the land'},
    'ובכלהרמש': {'definition': 'And in all the creeping', 'mechanical_translation': 'and~in~ALL the~CREEP(V)', 'rmt_translation': 'and over every creeping thing'},
    'הרמש': {'definition': 'The creeping thing', 'mechanical_translation': 'the~CREEP(V)', 'rmt_translation': 'the creeping thing'},
    'הרמשת': {'definition': 'The creeping', 'mechanical_translation': 'the~CREEP(V)~ing', 'rmt_translation': 'the creeping'},

    # === COMPOUND WORDS ===
    'אתהתנינם': {'definition': 'The great serpents', 'mechanical_translation': 'AT the~SERPENT~s the~MAGNIFY~s', 'rmt_translation': 'the great serpents'},
    'החיההרמשת': {'definition': 'The living creeping thing', 'mechanical_translation': 'the~LIVING the~CREEP(V)~ing', 'rmt_translation': 'the living creeping thing'},
    'כלנפש': {'definition': 'Every being', 'mechanical_translation': 'ALL BEING', 'rmt_translation': 'every being'},
    'כלעוף': {'definition': 'Every flyer', 'mechanical_translation': 'ALL FLYER', 'rmt_translation': 'every flyer'},
    'כלרמש': {'definition': 'Every creeping thing', 'mechanical_translation': 'ALL CREEP(V)', 'rmt_translation': 'every creeping thing'},
    'להאיר': {'definition': 'To give light', 'mechanical_translation': 'to~LIGHT(V)', 'rmt_translation': 'to give light'},
    'ולמועדים': {'definition': 'And for appointed times', 'mechanical_translation': 'and~to~APPOINTMENT~s', 'rmt_translation': 'and for appointed times'},
    'ולימים': {'definition': 'And for days', 'mechanical_translation': 'and~to~DAY~s', 'rmt_translation': 'and for days'},
    'ובלילה': {'definition': 'And in the night', 'mechanical_translation': 'and~in~NIGHT', 'rmt_translation': 'and in the night'},
    'אתשני': {'definition': 'The two', 'mechanical_translation': 'AT TWO', 'rmt_translation': 'the two'},
    'וחיתוארץ': {'definition': 'And living thing of the land', 'mechanical_translation': 'and~LIVING~of LAND', 'rmt_translation': 'and living thing of the land'},
    'אתחית': {'definition': 'The living thing of', 'mechanical_translation': 'AT LIVING~of', 'rmt_translation': 'the living thing of'},
    'ואתהבהמה': {'definition': 'And the beast', 'mechanical_translation': 'and~AT the~BEAST', 'rmt_translation': 'and the beast'},
    'למינה': {'definition': 'To her kind', 'mechanical_translation': 'to~KIND~her', 'rmt_translation': 'to her kind'},
    'לאמר': {'definition': 'To say', 'mechanical_translation': 'to~SAY(V)', 'rmt_translation': 'saying'},
    'עשבמזריע': {'definition': 'Herb seeding', 'mechanical_translation': 'HERB SEED(V)~ing', 'rmt_translation': 'herb seeding'},

    # === PRONOUNS / PARTICLES ===
    'אתם': {'definition': 'Them (object marker + them)', 'mechanical_translation': 'AT~them', 'rmt_translation': 'them'},
    'בימים': {'definition': 'In the seas', 'mechanical_translation': 'in~SEA~s', 'rmt_translation': 'in the seas'},
    'הגדלים': {'definition': 'The great ones', 'mechanical_translation': 'the~MAGNIFY~s', 'rmt_translation': 'the great'},
    'למינהם': {'definition': 'To their kind', 'mechanical_translation': 'to~KIND~them', 'rmt_translation': 'to their kind'},

    # === Genesis 1:26-31 specific ===
    'אדם': {'definition': 'Man: A human being, from reddish soil.', 'mechanical_translation': 'MAN', 'rmt_translation': 'man'},
    'בצלמו': {'definition': 'In his image', 'mechanical_translation': 'in~IMAGE~him', 'rmt_translation': 'in his image'},
    'זכר': {'definition': 'Male: The male gender.', 'mechanical_translation': 'MALE', 'rmt_translation': 'male'},
    'ונקבה': {'definition': 'And female', 'mechanical_translation': 'and~FEMALE', 'rmt_translation': 'and female'},
    'נקבה': {'definition': 'Female: The female gender.', 'mechanical_translation': 'FEMALE', 'rmt_translation': 'female'},
    'ויברך': {'definition': 'And he knelt (blessed)', 'mechanical_translation': 'and~he~will~KNEEL(V)', 'rmt_translation': 'and blessed'},
    'עשב': {'definition': 'Herb: Green plant.', 'mechanical_translation': 'HERB', 'rmt_translation': 'herb'},
    'זרע': {'definition': 'Seed: A grain or seed.', 'mechanical_translation': 'SEED', 'rmt_translation': 'seed'},
    'עץ': {'definition': 'Tree: A woody plant.', 'mechanical_translation': 'TREE', 'rmt_translation': 'tree'},
    'פרי': {'definition': 'Produce: Fruit of a tree.', 'mechanical_translation': 'PRODUCE', 'rmt_translation': 'produce'},
    'לאכלה': {'definition': 'For food', 'mechanical_translation': 'to~EAT(V)~her', 'rmt_translation': 'for focus'},
    'ירק': {'definition': 'Green: Green vegetation.', 'mechanical_translation': 'GREEN', 'rmt_translation': 'green'},
    'כלעשב': {'definition': 'Every herb', 'mechanical_translation': 'ALL HERB', 'rmt_translation': 'every herb'},
    'כלעץ': {'definition': 'Every tree', 'mechanical_translation': 'ALL TREE', 'rmt_translation': 'every tree'},
    'אשרבו': {'definition': 'Which in him', 'mechanical_translation': 'WHICH in~him', 'rmt_translation': 'which has in it'},
    'פריעץ': {'definition': 'Produce of tree', 'mechanical_translation': 'PRODUCE TREE', 'rmt_translation': 'produce of tree'},
    'זרעזרע': {'definition': 'Seeding seed', 'mechanical_translation': 'SEED(V)~ing SEED', 'rmt_translation': 'seeding seed'},
    'לכלחית': {'definition': 'To every living thing', 'mechanical_translation': 'to~ALL LIVING~of', 'rmt_translation': 'to every living thing'},
    'ולכלעוף': {'definition': 'And to every flyer', 'mechanical_translation': 'and~to~ALL FLYER', 'rmt_translation': 'and to every flyer'},
    'ולכלרומש': {'definition': 'And to every creeping thing', 'mechanical_translation': 'and~to~ALL CREEP(V)', 'rmt_translation': 'and to every creeping thing'},
    'אשרבו': {'definition': 'Which is in him', 'mechanical_translation': 'WHICH in~him', 'rmt_translation': 'which has in it'},
    'נפשחיה': {'definition': 'Living being', 'mechanical_translation': 'BEING LIVING', 'rmt_translation': 'a living being'},
    'אתכלירק': {'definition': 'Every green thing', 'mechanical_translation': 'AT ALL GREEN', 'rmt_translation': 'every green thing'},
    'מאד': {'definition': 'Very, greatly.', 'mechanical_translation': 'MUCH', 'rmt_translation': 'very'},
    'והנה': {'definition': 'And look', 'mechanical_translation': 'and~BEHOLD', 'rmt_translation': 'and look'},
    'טוב': {'definition': 'Functional: Working well, good.', 'mechanical_translation': 'FUNCTIONAL', 'rmt_translation': 'functional'},
    'כלאשר': {'definition': 'All which', 'mechanical_translation': 'ALL WHICH', 'rmt_translation': 'all which'},
    'עשה': {'definition': 'Do: To make or do.', 'mechanical_translation': 'DO(V)', 'rmt_translation': 'he had made'},
}

# Also fix לאכלה properly
fixes['לאכלה'] = {'definition': 'For food', 'mechanical_translation': 'to~EAT(V)~her', 'rmt_translation': 'for food'}

fixed = 0
for hw, fix in fixes.items():
    if hw not in words:
        words[hw] = {'gematria': 0, 'digital_root': 0, 'letters': []}
    for key, val in fix.items():
        words[hw][key] = val
    fixed += 1

with open(WORDS_JSON, 'w', encoding='utf-8') as f:
    json.dump(words, f, ensure_ascii=False, indent=2)

print(f'Fixed {fixed} words in words.json')
