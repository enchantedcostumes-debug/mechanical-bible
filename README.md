# THE MECHANICAL BIBLE

**Restoring the Original Meanings of Scripture Through Proto-Sinaitic Pictographic Analysis**

---

## What Is This?

The Mechanical Bible is a word-by-word analysis of Hebrew scripture that:

1. **Breaks down every Hebrew word** into its constituent letters
2. **Maps each letter** to its Proto-Sinaitic pictographic origin
3. **Reconstructs the original meaning** before 2,000 years of translation
4. **Tracks the 6-stage corruption** from Hebrew to Modern English
5. **Calculates gematria** (numerical values) and digital roots
6. **Identifies control words** - terms deliberately corrupted to manipulate populations

---

## The 6-Stage Corruption Timeline

| Stage | Period | What Happened |
|-------|--------|---------------|
| 1. Hebrew Original | Ancient | Proto-Sinaitic pictographs conveyed concrete meanings |
| 2. Septuagint (LXX) | 280 BCE | Greek translation introduced philosophical abstractions |
| 3. New Testament Greek | 100 CE | Hebrew concepts filtered through Hellenistic worldview |
| 4. Latin Vulgate | 400 CE | Jerome's Latin introduced Roman legal/religious framework |
| 5. King James | 1611 | English translation served political/ecclesiastical agenda |
| 6. Modern | Today | Original meanings almost completely obscured |

---

## Example: Genesis 1:1

**Hebrew:** בראשית ברא אלהים את השמים ואת הארץ

**Mechanical Breakdown:**

| Word | Hebrew | Gematria | Pictographic Meaning |
|------|--------|----------|---------------------|
| בראשית | B'reshit | 913 | "In the HEAD/CHIEF place" - not just "beginning" |
| ברא | Bara | 203 | "To fatten/fill" - creation as FILLING, not ex nihilo |
| אלהים | Elohim | 86 | "Mighty ones/powers" - plural form, singular verb |
| את | Et | 401 | Aleph-Tav - First and Last letters (Alpha-Omega) |
| השמים | HaShamayim | 395 | "The waters above" - שמ = "there" + מים = "waters" |
| ואת | V'et | 407 | "And the Aleph-Tav" |
| הארץ | HaAretz | 296 | "The firm/pressed land" - from רצץ "to press" |

**Total Verse Gematria:** 2701 = 37 x 73 (both prime numbers)

---

## Data Sources

- **Strong's Concordance** - H1 through H8674 (Hebrew)
- **Ancient Hebrew Lexicon of the Bible (AHLB)** - Jeff Benner
- **Proto-Sinaitic Pictographic Analysis** - Based on archaeological findings
- **Tanakh Complete** - 23,341 verses, 263,117 word occurrences
- **Rosetta Stone Project** - 356 language lexicons

---

## Repository Structure

```
mechanical-bible/
├── data/
│   ├── lexicon/           # 58,400 Hebrew word entries
│   ├── tanakh/            # Complete Tanakh verses
│   ├── concordance/       # Strong's mappings
│   └── evolution/         # 6-stage corruption data
├── tools/
│   ├── build_lexicon.py   # Build Hebrew lexicon
│   └── analyze_verse.py   # Analyze any verse
├── api/                   # Optional Flask API
├── docs/                  # Documentation
└── static/                # UI assets
```

---

## Usage

### Analyze a Verse

```python
from tools.analyze_verse import analyze

result = analyze("Genesis", 1, 1)
print(result)
```

### Look Up a Word

```python
from tools.lookup_word import lookup

word = lookup("H7225")  # or lookup("בראשית")
print(word.pictographic_meaning)
print(word.gematria)
print(word.letters)
```

---

## The 100 Control Words

These are the most corrupted words in scripture - terms whose meanings were deliberately altered to control populations:

| Hebrew | Modern Translation | Original Meaning | Control Mechanism |
|--------|-------------------|------------------|-------------------|
| יראה | "Fear" | "To see/perceive" | Makes God terrifying instead of perceivable |
| עבד | "Slave/servant" | "To work/serve" | Justifies human ownership |
| חטא | "Sin" | "To miss the mark" | Creates guilt industry |
| ... | ... | ... | ... |

See `data/control_words.json` for the complete list.

---

## Contributing

This is a living research project. Contributions welcome:

1. **LXX Greek mappings** - How was each Hebrew word translated in the Septuagint?
2. **Vulgate Latin mappings** - Jerome's Latin translations
3. **KJV analysis** - 1611 translation choices
4. **Additional pictographic research** - Proto-Sinaitic archaeology
5. **Corrections** - Found an error? Open an issue.

---

## License

**Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**

You are free to:
- **Share** - copy and redistribute in any medium or format
- **Adapt** - remix, transform, and build upon the material

Under these terms:
- **Attribution** - Give appropriate credit
- **ShareAlike** - Distribute under the same license

---

## The Mission

> *"The grass withers, the flower fades, but the Word of our God stands forever."*
> — Isaiah 40:8

This project exists to restore what was corrupted. The original Hebrew pictographs conveyed concrete, physical meanings that were systematically abstracted and spiritualized to serve institutional power.

**The truth is in the letters themselves.** We're just reading them correctly.

---

## Related Projects

- [Oracle Collective](https://github.com/enchantedcostumes-debug/flask-structural-api) - The platform hosting the live API
- [Ancient Hebrew Research Center](https://www.ancient-hebrew.org/) - Jeff Benner's work on AHLB

---

**Copyright (c) 2026 Tammy L Casey. All rights reserved.**

*"Known by our fruits, not our roots"*
