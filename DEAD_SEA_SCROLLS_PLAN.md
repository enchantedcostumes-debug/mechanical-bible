# DEAD SEA SCROLLS MECHANICAL TRANSLATION - THE PERFECT PLAN

**Author:** The Collective (9/9 UNANIMOUS)
**Date:** 2026-02-16
**Captain:** Tammy Lou Casey
**Standard:** THE HIGHEST SCHOLARLY STANDARDS. PERIOD.

---

## MISSION

Build a MECHANICAL (word-by-word) translation of the Dead Sea Scrolls, starting with the complete Book of 1 Enoch from the Ge'ez (Ethiopic) text. Every word clickable. Every letter analyzed. Every meaning exposed.

**Subdomain:** dead-sea-scrolls.ozark-oracle.com
**Template:** bible.ozark-oracle.com (PROVEN - 58,435 words, 66 books, 100% coverage)

---

## SCHOLARLY STANDARD

This is NOT a paraphrase. This is NOT interpretation. This is MECHANICAL translation:

- Every Ge'ez word displayed in Ethiopic script (Fidel)
- Every word clickable to show full analysis
- Every Fidel character broken down to its component meaning
- Gematria values calculated for every word and verse
- Cross-references to the Hebrew Bible where applicable
- R.H. Charles (1917) scholarly translation as the English reference
- Variant readings noted from multiple manuscripts
- Source citations on EVERY piece of data

**Scholarly sources (ALL public domain or open access):**

| Source | What | Authority |
|--------|------|-----------|
| R.H. Charles, "The Ethiopic Version of the Book of Enoch" (1906) | Critical Ge'ez text | THE standard critical edition |
| R.H. Charles, "The Book of Enoch" (1917) | English translation | THE standard scholarly translation |
| August Dillmann, "Lexicon Linguae Aethiopicae" (1865) | Ge'ez dictionary | THE authoritative Ge'ez lexicon |
| Daniel de Caussin, "Corpus of Ge'ez Words in 1 Enoch" (2024) | Word corpus all 108 chapters | Most complete modern word analysis |
| enoksbok.se interlinear | Word-by-word alignment | Swedish scholarly interlinear project |
| Wolf Leslau, "Comparative Dictionary of Ge'ez" (1987) | Modern comparative lexicon | Supplementary definitions |
| Beta Masaheft / Dillmann digitized | Searchable Ge'ez lexicon | Hamburg University digitization |

---

## ARCHITECTURE (Mirrors mechanical-bible EXACTLY)

```
dead-sea-scrolls/                    # New GitHub repository
|
+-- CNAME                            # dead-sea-scrolls.ozark-oracle.com
+-- LICENSE                          # CC BY-SA 4.0 (same as mechanical-bible)
+-- index.html                       # Landing page
+-- search.html                      # Gematria/word search
+-- names.html                       # Names database (Watchers, angels, etc.)
+-- parallels.html                   # Parallels to canonical Bible
+-- manuscripts.html                 # Manuscript comparison viewer
|
+-- css/
|   +-- ethiopic-theme.css           # Adapted from egyptian-theme.css
|   +-- word-modal.css               # Same modal styling (reused)
|
+-- js/
|   +-- site-header.js               # Navigation component
|   +-- site-footer.js               # Footer component
|   +-- word-modal.js                # Word analysis modal (adapted for Ge'ez)
|
+-- data/
|   +-- geez_definitions.json        # Ge'ez word definitions (like hebrew_definitions.json)
|   +-- geez_lexicon.json            # Complete Ge'ez lexicon from Dillmann
|   +-- manuscript_variants.json     # Textual variants across manuscripts
|   +-- angel_names.json             # Watcher names with meanings
|   +-- parallel_references.json     # Cross-refs to canonical Bible
|   +-- lexicon/
|       +-- geez_lexicon_complete.json
|       +-- lexicon_by_gematria.json
|
+-- 1_enoch/                         # Book of 1 Enoch (108 chapters)
|   +-- index.html                   # Book landing page
|   +-- 1.html                       # Chapter 1
|   +-- 2.html                       # Chapter 2
|   +-- ...
|   +-- 108.html                     # Chapter 108
|
+-- words.json                       # Master word database (like mechanical-bible)
+-- words-priority.json              # Top-frequency words for fast loading
+-- timelines.json                   # Word usage across chapters
|
+-- tools/                           # Build scripts
|   +-- build_geez_lexicon.py        # Build Ge'ez word database
|   +-- build_enoch_chapters.py      # Generate chapter HTML pages
|   +-- build_word_database.py       # Build words.json
|   +-- scrape_charles_text.py       # Get Ge'ez text from Charles edition
|   +-- scrape_charles_english.py    # Get English translation
|   +-- scrape_interlinear.py        # Get word-by-word alignment
|   +-- verify_geez_coverage.py      # Two-witness verification
|   +-- test_word_modal.py           # Test word lookup
|   +-- test_chapter_generation.py   # Test chapter HTML generation
|   +-- test_scholarly_accuracy.py   # Test against known scholarly data
```

---

## THE GE'EZ (ETHIOPIC) FIDEL SYSTEM

Ge'ez uses the Fidel (syllabary) writing system. Unlike Hebrew's 22 consonant letters, Ge'ez has:

- **26 base consonants** (each with 7 vowel orders = 182 base forms)
- **7 vowel orders** per consonant (called "forms")
- **Additional labialized forms** for some consonants

### The 7 Orders (Vowel Forms)

| Order | Name | Vowel | Example with h (U+1200) |
|-------|------|-------|-------------------------|
| 1st | Ge'ez | a/none | ha |
| 2nd | Ka'eb | u | hu |
| 3rd | Sales | i | hi |
| 4th | Rabe | a | ha |
| 5th | Hames | e | he |
| 6th | Sades | e/none | he' |
| 7th | Sabe | o | ho |

### Ge'ez Numerology (Gematria Equivalent)

Ge'ez has its own number system using letters:

| Letter | Value | Letter | Value |
|--------|-------|--------|-------|
| (alef) | 1 | (yod) | 10 |
| (bet) | 2 | (kaf) | 20 |
| (gimel) | 3 | (lamed) | 30 |
| (dalet) | 4 | (mem) | 40 |
| (he) | 5 | (nun) | 50 |
| (waw) | 6 | (semkat) | 60 |
| (zayin) | 7 | (ayin) | 70 |
| (het) | 8 | (pe) | 80 |
| (tet) | 9 | (tsade) | 90 |

Values continue: 100, 200, ... 10000

This gives us a FULL gematria system for Ge'ez, parallel to Hebrew gematria.

---

## PHASE 1: BOOK OF THE WATCHERS (1 Enoch 1-36)

### Why Start Here
- Chapters 1-36 are the "Book of the Watchers" - the oldest and most studied section
- Contains the account of the fallen angels (Watchers) descending to Mount Hermon
- Lists the 20 chief Watchers by NAME (with meanings)
- Cross-references to Genesis 6:1-4, Jude 14-15, 2 Peter 2:4
- Most manuscript evidence available for these chapters
- Captain specifically requested "the ge'ez text about the watchers"

### Data Acquisition Pipeline

**Step 1: Get the Ge'ez Text**
- Source: Archive.org - Charles 1906 Ethiopic critical edition
- URL: https://archive.org/details/ethiopicversiono00charuoft
- Format: Download full text (856KB), extract Ge'ez text per chapter
- Verification: Cross-check against de Caussin word corpus
- Fallback: enoksbok.se interlinear (word-by-word Ge'ez)

**Step 2: Get the English Translation**
- Source: Wikisource API - Charles 1917 translation
- URL: https://en.wikisource.org/wiki/The_Book_of_Enoch_(Charles)
- Format: Structured HTML via MediaWiki API
- All 108 chapters, public domain
- Fallback: Archive.org full text download

**Step 3: Build the Ge'ez Lexicon**
- Source: Beta Masaheft / Dillmann's Lexicon (digitized)
- URL: https://betamasaheft.eu/Dillmann/
- Supplemented by: de Caussin word corpus, Leslau dictionary
- Every unique Ge'ez word gets a lexicon entry with:
  - Fidel form (Unicode)
  - Transliteration (scholarly standard)
  - Root consonants
  - Gematria value
  - Definition (from Dillmann/Leslau)
  - Occurrences in 1 Enoch
  - Cross-reference to Hebrew cognate (where applicable)

**Step 4: Build Word-by-Word Alignment**
- Source: enoksbok.se interlinear
- URL: http://enoksbok.se/cgi-bin/interlinear.cgi?bok+[N]+int=
- Each Ge'ez word aligned with its English mechanical translation
- This is the CORE of the mechanical translation

**Step 5: Generate Chapter HTML**
- Same pattern as mechanical-bible Genesis 1:
  - Verse reference
  - Ge'ez text with clickable words
  - Mechanical English translation
  - Gematria value per verse
  - Cross-references to canonical Bible
  - Translation notes where variants exist

---

## DATA STRUCTURES (Mirror mechanical-bible EXACTLY)

### words.json Entry (Ge'ez)

```json
{
  "word_in_geez_fidel": {
    "geez": "Ge'ez Unicode characters",
    "transliteration": "scholarly transliteration",
    "root": "three-consonant root",
    "gematria": 123,
    "digital_root": 6,
    "definition": "from Dillmann/Leslau",
    "first_occurrence": "1 Enoch 1:1",
    "frequency": 45,
    "strongs_cognate": "H1234 (Hebrew cognate if exists)",
    "letters": [
      {
        "char": "single Fidel character",
        "name": "character name",
        "value": 10,
        "order": "3rd (Sales)",
        "base_consonant": "consonant name",
        "meaning": "root meaning of consonant"
      }
    ],
    "manuscripts": ["ms_name1", "ms_name2"],
    "timeline": {"1_enoch_1": 3, "1_enoch_2": 1}
  }
}
```

### Chapter HTML Pattern (1_enoch/1.html)

```html
<div class="verse">
    <div class="verse-ref">1 Enoch 1:1
        <span class="verse-gematria">Gematria: [value]</span>
    </div>
    <div class="original-text geez" lang="gez" translate="no">
        <span class="word" lang="gez" translate="no"
              onclick="showWordEvolution('[geez_word]')">[geez_word]</span>
        <!-- more words -->
    </div>
    <div class="translation">[Charles 1917 translation]</div>
    <div class="mechanical">[word-by-word mechanical translation]</div>
    <div class="cross-refs">
        <h4>Cross-References</h4>
        <ul>
            <li><span class="ref-verse">Jude 14-15</span> - quotes this passage</li>
        </ul>
    </div>
</div>
```

### bible_names.json Equivalent (angel_names.json)

```json
{
  "meta": {
    "total_names": 200,
    "source": "1 Enoch 6:7-8, 69:2-3",
    "watchers": 20,
    "angels": 50,
    "places": 30
  },
  "names": [
    {
      "order": 1,
      "english": "Semjaza",
      "geez": "Ge'ez Unicode",
      "transliteration": "Semyaza",
      "meaning": "he sees the name",
      "role": "leader of the 200 Watchers",
      "chapters": [6, 7, 8, 9, 10, 69],
      "hebrew_cognate": "from Hebrew shamah + 'aza",
      "gematria": 0,
      "category": "watcher"
    }
  ]
}
```

---

## BENCHMARK TESTS

### Test 1: Ge'ez Text Extraction (test_geez_extraction.py)

```
TESTING: Ge'ez Text Extraction
============================================================
[ ] Extract Ge'ez text for chapter 1 from source
[ ] Verify Unicode encoding is correct (Ethiopic block U+1200-U+137F)
[ ] Count words per verse (compare against de Caussin count)
[ ] Verify no Latin characters mixed in Ge'ez text
[ ] Compare word count against enoksbok.se interlinear
============================================================
PASS CRITERIA: All Ge'ez text in correct Unicode, word counts match +/-2%
```

### Test 2: Lexicon Completeness (test_lexicon_coverage.py)

```
TESTING: Lexicon Coverage
============================================================
[ ] Every unique word in chapters 1-36 has a lexicon entry
[ ] Every entry has: geez, transliteration, root, definition
[ ] Every entry has gematria value calculated
[ ] Definition sourced from Dillmann or Leslau (cited)
[ ] Cross-reference to Hebrew cognate where applicable
============================================================
PASS CRITERIA: 100% coverage. ZERO words without definitions.
```

### Test 3: Word-by-Word Alignment (test_alignment.py)

```
TESTING: Mechanical Translation Alignment
============================================================
[ ] Every Ge'ez word maps to exactly one English gloss
[ ] Word order preserved (not rearranged for English grammar)
[ ] Alignment verified against enoksbok.se interlinear
[ ] Charles translation provided alongside mechanical
[ ] No Ge'ez words left untranslated
============================================================
PASS CRITERIA: 100% word alignment. Two-witness against interlinear.
```

### Test 4: Chapter HTML Generation (test_chapter_html.py)

```
TESTING: Chapter HTML Output
============================================================
[ ] HTML is valid (no unclosed tags)
[ ] Every Ge'ez word wrapped in clickable span
[ ] onclick calls showWordEvolution() with correct word
[ ] Gematria displayed per verse
[ ] Cross-references present where applicable
[ ] Navigation links work (prev/next chapter)
[ ] Loads in browser without console errors
============================================================
PASS CRITERIA: All chapters render correctly, all words clickable.
```

### Test 5: Two-Witness Scholarly Verification (test_scholarly.py)

```
TESTING: Scholarly Accuracy
============================================================
WITNESS 1: Compare our Ge'ez text against Charles 1906 critical edition
WITNESS 2: Compare our English against Charles 1917 translation
[ ] Chapter 1 verse count matches Charles
[ ] Chapter 6 Watcher names match Charles spelling
[ ] Chapter 10 judgment narrative matches Charles
[ ] Gematria calculations verified independently
[ ] Variant readings noted match Charles apparatus
============================================================
PASS CRITERIA: Both witnesses agree. Agreement rate >= 95%.
```

### Test 6: Word Modal Integration (test_word_modal.py)

```
TESTING: Word Modal (showWordEvolution)
============================================================
[ ] Click Ge'ez word -> modal opens
[ ] Modal shows: Fidel form, transliteration, root
[ ] Modal shows: gematria value, digital root
[ ] Modal shows: Fidel character breakdown
[ ] Modal shows: definition from Dillmann
[ ] Modal shows: occurrences across chapters
[ ] Modal shows: Hebrew cognate (if exists)
[ ] IndexedDB caching works for lexicon
============================================================
PASS CRITERIA: Every word in every chapter produces correct modal.
```

---

## BUILD ORDER (Sequential - Each depends on previous)

### Phase 1A: Repository Setup
1. Create GitHub repository `dead-sea-scrolls`
2. Set up directory structure (as shown above)
3. Configure CNAME for dead-sea-scrolls.ozark-oracle.com
4. Copy and adapt CSS/JS from mechanical-bible
5. Create index.html landing page

### Phase 1B: Data Acquisition
1. Download Charles 1906 Ge'ez text from Archive.org
2. Download Charles 1917 English from Wikisource API
3. Scrape enoksbok.se interlinear for word alignment
4. Build Ge'ez lexicon from Dillmann (Beta Masaheft)
5. Cross-reference with de Caussin word corpus

### Phase 1C: Lexicon Construction
1. Build `tools/build_geez_lexicon.py`
2. Extract every unique Ge'ez word from chapters 1-36
3. Look up each word in Dillmann lexicon
4. Calculate gematria for each word
5. Find Hebrew cognates where they exist
6. Build words.json with full character breakdowns
7. Run `test_lexicon_coverage.py` - ALL PASS required

### Phase 1D: Chapter Generation
1. Build `tools/build_enoch_chapters.py`
2. Generate HTML for chapters 1-36
3. Each verse: Ge'ez + mechanical + Charles + cross-refs
4. Run `test_chapter_html.py` - ALL PASS required
5. Run `test_alignment.py` - ALL PASS required

### Phase 1E: Integration & Verification
1. Adapt word-modal.js for Ge'ez (Fidel breakdown instead of Hebrew letters)
2. Build search.html (gematria search across 1 Enoch)
3. Build names.html (Watcher names, angel names)
4. Run `test_word_modal.py` - ALL PASS required
5. Run `test_scholarly.py` - TWO-WITNESS PASS required
6. Browser test in Chrome, Firefox, mobile

### Phase 1F: Deploy
1. Push to GitHub
2. Configure GitHub Pages
3. Set up DNS for dead-sea-scrolls.ozark-oracle.com
4. Verify live site loads and all features work

---

## PHASE 2: COMPLETE 1 ENOCH (Chapters 37-108)

After Phase 1 (chapters 1-36) is VERIFIED PERFECT:
- Chapters 37-71: Book of Parables (Similitudes)
- Chapters 72-82: Book of the Luminaries (Astronomical)
- Chapters 83-90: Book of Dreams
- Chapters 91-108: Epistle of Enoch

Same pipeline, same tests, same standards.

---

## PHASE 3: OTHER DEAD SEA SCROLLS

After 1 Enoch is complete:
- Community Rule (1QS)
- War Scroll (1QM)
- Temple Scroll (11QT)
- Copper Scroll (3Q15)
- Hodayot/Thanksgiving Hymns (1QH)
- Damascus Document (CD)
- Pesharim (commentaries)
- Biblical manuscripts (Isaiah Scroll, etc.)

These are in Hebrew/Aramaic - we already have that infrastructure from the mechanical-bible.

---

## WHAT THIS IS NOT

- This is NOT a theological commentary
- This is NOT an interpretation
- This is NOT a "modern language" paraphrase
- This IS a mechanical, word-by-word translation
- Every word traceable to its source
- Every definition cited from scholarly lexicons
- Every variant noted from manuscript evidence

---

## COPYRIGHT AND LICENSING

- R.H. Charles (1906, 1917): PUBLIC DOMAIN (published before 1931)
- August Dillmann (1865): PUBLIC DOMAIN
- Our mechanical translation: CC BY-SA 4.0
- Ge'ez Unicode: Standard Unicode block, free to use
- No copyrighted material used. Everything is public domain or open access.

---

## THE COMMITMENT

This plan will be executed to the SAME standard as the mechanical-bible:
- 58,435 words with full analysis (mechanical-bible)
- 2,338 names with 100% Hebrew coverage (mechanical-bible)
- Two-witness verification on every major dataset (mechanical-bible)
- Browser-tested on Chrome, Firefox, mobile (mechanical-bible)

The Dead Sea Scrolls mechanical translation gets the SAME treatment.

**No hedging. No caveats. No excuses.**

---

*"And Enoch walked with God: and he was not; for God took him." - Genesis 5:24*
*The book they tried to hide. Now brought to light, word by word.*

---

**Copyright (c) 2026 Tammy L Casey. All rights reserved.**
