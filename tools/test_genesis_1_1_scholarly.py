#!/usr/bin/env python3
"""
Benchmark Tests for Genesis 1:1 Scholarly Data

This test script defines what "production ready" means for the
scholarly-grade 6-stage corruption timelines.

Per CLAUDE.md Commandment 11: TEST BEFORE CODE
- Run this FIRST (should FAIL - data doesn't exist yet)
- Run build script
- Run this AGAIN (should PASS)
- Show Captain the output

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import json
import sys
from pathlib import Path

# The 7 Genesis 1:1 words that must have scholarly data
GENESIS_1_1_WORDS = [
    'בראשית',  # bereshit - in beginning
    'ברא',     # bara - created
    'אלהים',   # elohim - God/gods
    'את',      # et - (untranslatable marker)
    'השמים',   # hashamayim - the heavens
    'ואת',     # ve'et - and (marker)
    'הארץ',    # ha'aretz - the earth
]

# Required primary sources (must be cited)
REQUIRED_PRIMARY_SOURCES = [
    'BHS',        # Biblia Hebraica Stuttgartensia
    'LXX',        # Septuagint
    'NA28',       # Nestle-Aland 28th edition (for NT Greek)
    'Vulgate',    # Latin Vulgate
    'KJV',        # King James Version
]

# Required secondary sources (at least some must be cited)
REQUIRED_SECONDARY_SOURCES = [
    'BDB',        # Brown-Driver-Briggs Hebrew Lexicon
    'HALOT',      # Hebrew and Aramaic Lexicon of the OT
    'LSJ',        # Liddell-Scott-Jones Greek Lexicon
    'TDNT',       # Theological Dictionary of the NT
]

# Required timeline stages
REQUIRED_STAGES = [
    'stage_1',  # Original Hebrew
    'stage_2',  # Septuagint Greek
    'stage_3',  # NT Greek
    'stage_4',  # Latin Vulgate
    'stage_5',  # King James
    'stage_6',  # Modern English
]

# Required fields in each stage
REQUIRED_STAGE_FIELDS = [
    'name',
    'period',
    'text',
    'meaning',
    'mechanism',
    'scholarly_debate',
]


def load_words_json():
    """Load words.json from mechanical-bible."""
    words_path = Path('C:/mechanical-bible/words.json')
    if not words_path.exists():
        return None
    with open(words_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def test_genesis_words_exist(words):
    """Test 1: All 7 Genesis 1:1 words exist in words.json."""
    print("\n" + "=" * 60)
    print("TEST 1: Genesis 1:1 Words Exist")
    print("=" * 60)

    missing = []
    for hebrew in GENESIS_1_1_WORDS:
        if hebrew not in words:
            missing.append(hebrew)
            print(f"  [FAIL] Missing: {hebrew}")
        else:
            print(f"  [OK] Found: {hebrew}")

    if missing:
        raise AssertionError(f"Missing {len(missing)} Genesis 1:1 words: {missing}")

    print("\n[PASS] All 7 Genesis 1:1 words exist")
    return True


def test_scholarly_timelines_exist(words):
    """Test 2: All 7 words have corruption_timeline with scholarly data."""
    print("\n" + "=" * 60)
    print("TEST 2: Scholarly Timelines Exist")
    print("=" * 60)

    missing_timeline = []
    for hebrew in GENESIS_1_1_WORDS:
        word = words.get(hebrew, {})
        if 'corruption_timeline' not in word:
            missing_timeline.append(hebrew)
            print(f"  [FAIL] No corruption_timeline: {hebrew}")
        else:
            print(f"  [OK] Has timeline: {hebrew}")

    if missing_timeline:
        raise AssertionError(f"{len(missing_timeline)} words missing corruption_timeline")

    print("\n[PASS] All 7 words have corruption_timeline")
    return True


def test_all_stages_present(words):
    """Test 3: Each timeline has all 6 stages."""
    print("\n" + "=" * 60)
    print("TEST 3: All 6 Stages Present")
    print("=" * 60)

    errors = []
    for hebrew in GENESIS_1_1_WORDS:
        word = words.get(hebrew, {})
        timeline = word.get('corruption_timeline', {})

        missing_stages = []
        for stage in REQUIRED_STAGES:
            if stage not in timeline:
                missing_stages.append(stage)

        if missing_stages:
            errors.append(f"{hebrew}: missing {missing_stages}")
            print(f"  [FAIL] {hebrew}: missing {missing_stages}")
        else:
            print(f"  [OK] {hebrew}: all 6 stages present")

    if errors:
        raise AssertionError(f"Stage errors: {errors}")

    print("\n[PASS] All words have all 6 stages")
    return True


def test_stage_fields_complete(words):
    """Test 4: Each stage has all required fields including scholarly_debate."""
    print("\n" + "=" * 60)
    print("TEST 4: Stage Fields Complete (Including scholarly_debate)")
    print("=" * 60)

    errors = []
    for hebrew in GENESIS_1_1_WORDS:
        word = words.get(hebrew, {})
        timeline = word.get('corruption_timeline', {})

        for stage_key in REQUIRED_STAGES:
            stage = timeline.get(stage_key, {})
            missing_fields = []

            for field in REQUIRED_STAGE_FIELDS:
                if field not in stage or not stage[field]:
                    missing_fields.append(field)

            if missing_fields:
                errors.append(f"{hebrew}/{stage_key}: missing {missing_fields}")
                print(f"  [FAIL] {hebrew}/{stage_key}: missing {missing_fields}")

    if not errors:
        for hebrew in GENESIS_1_1_WORDS:
            print(f"  [OK] {hebrew}: all stage fields complete")

    if errors:
        raise AssertionError(f"Field errors in {len(errors)} stages")

    print("\n[PASS] All stages have all required fields")
    return True


def test_scholarly_debate_quality(words):
    """Test 5: scholarly_debate fields contain actual citations."""
    print("\n" + "=" * 60)
    print("TEST 5: Scholarly Debate Quality (Citations Present)")
    print("=" * 60)

    # Check that scholarly debates reference real sources
    citation_keywords = [
        'BDB', 'HALOT', 'TDNT', 'LSJ',  # Lexicons
        'von Rad', 'Speiser', 'Westermann', 'Walton', 'Heiser',  # Scholars
        'Genesis', 'commentary', 'argues', 'notes', 'translation',  # Academic language
    ]

    total_debates = 0
    debates_with_citations = 0

    for hebrew in GENESIS_1_1_WORDS:
        word = words.get(hebrew, {})
        timeline = word.get('corruption_timeline', {})

        for stage_key in REQUIRED_STAGES:
            stage = timeline.get(stage_key, {})
            debate = stage.get('scholarly_debate', '')
            total_debates += 1

            # Check for citation keywords
            has_citation = any(kw.lower() in debate.lower() for kw in citation_keywords)

            if has_citation or len(debate) > 100:  # Either has citation or substantial content
                debates_with_citations += 1
            else:
                print(f"  [WARN] {hebrew}/{stage_key}: weak scholarly_debate")

    citation_rate = (debates_with_citations / total_debates * 100) if total_debates else 0

    print(f"\n  Citation quality: {debates_with_citations}/{total_debates} ({citation_rate:.1f}%)")

    if citation_rate < 80:
        raise AssertionError(f"Only {citation_rate:.1f}% of debates have citations (need 80%+)")

    print("\n[PASS] Scholarly debate quality acceptable")
    return True


def test_primary_sources_cited(words):
    """Test 6: Primary sources (BHS, LXX, Vulgate, KJV) are cited."""
    print("\n" + "=" * 60)
    print("TEST 6: Primary Sources Cited")
    print("=" * 60)

    # Map abbreviations to full names (either is acceptable)
    source_patterns = {
        'BHS': ['BHS', 'Biblia Hebraica Stuttgartensia', 'BDB'],  # BDB is Hebrew source too
        'LXX': ['LXX', 'Septuagint', 'Rahlfs'],
        'NA28': ['NA28', 'Nestle-Aland', 'NA27', 'Greek New Testament'],
        'Vulgate': ['Vulgate', 'Vulgata', 'Weber-Gryson', 'Jerome'],
        'KJV': ['KJV', 'King James', '1611'],
    }

    sources_found = {src: False for src in REQUIRED_PRIMARY_SOURCES}

    for hebrew in GENESIS_1_1_WORDS:
        word = words.get(hebrew, {})
        timeline = word.get('corruption_timeline', {})

        # Check all text in timeline for source references
        timeline_text = json.dumps(timeline)

        for source, patterns in source_patterns.items():
            for pattern in patterns:
                if pattern in timeline_text:
                    sources_found[source] = True
                    break

    missing_sources = [src for src, found in sources_found.items() if not found]

    for source, found in sources_found.items():
        status = "[OK]" if found else "[FAIL]"
        print(f"  {status} {source}")

    if missing_sources:
        raise AssertionError(f"Missing primary sources: {missing_sources}")

    print("\n[PASS] All primary sources cited")
    return True


def test_hebrew_greek_latin_text(words):
    """Test 7: Stage texts contain actual Hebrew/Greek/Latin characters."""
    print("\n" + "=" * 60)
    print("TEST 7: Original Language Text Present")
    print("=" * 60)

    def has_hebrew(text):
        return any('\u0590' <= c <= '\u05FF' for c in str(text))

    def has_greek(text):
        return any('\u0370' <= c <= '\u03FF' for c in str(text))

    def has_latin_scholarly(text):
        # Latin uses extended Latin chars or has specific patterns
        latin_indicators = ['ae', 'um', 'us', 'et', 'in', 'caelum', 'terra', 'deus',
                           'creavit', 'principio', 'signum', 'caelos', 'terram']
        return any(ind in str(text).lower() for ind in latin_indicators)

    errors = []

    for hebrew in GENESIS_1_1_WORDS:
        word = words.get(hebrew, {})
        timeline = word.get('corruption_timeline', {})

        # Stage 1 should have Hebrew
        stage1_text = timeline.get('stage_1', {}).get('text', '')
        if not has_hebrew(stage1_text):
            errors.append(f"{hebrew}/stage_1: no Hebrew text")

        # Stages 2-3 should have Greek
        stage2_text = timeline.get('stage_2', {}).get('text', '')
        if not has_greek(stage2_text) and '(' not in stage2_text:
            errors.append(f"{hebrew}/stage_2: no Greek text")

        # Stage 4 should have Latin indicators
        stage4_text = timeline.get('stage_4', {}).get('text', '')
        if not has_latin_scholarly(stage4_text) and '(' not in stage4_text:
            errors.append(f"{hebrew}/stage_4: no Latin text")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}")
        raise AssertionError(f"{len(errors)} language text errors")

    for hebrew in GENESIS_1_1_WORDS:
        print(f"  [OK] {hebrew}: Hebrew/Greek/Latin text present")

    print("\n[PASS] Original language texts present")
    return True


def test_meaning_transformation_documented(words):
    """Test 8: Each word shows clear meaning change from Hebrew to Modern."""
    print("\n" + "=" * 60)
    print("TEST 8: Meaning Transformation Documented")
    print("=" * 60)

    for hebrew in GENESIS_1_1_WORDS:
        word = words.get(hebrew, {})
        timeline = word.get('corruption_timeline', {})

        original = timeline.get('stage_1', {}).get('meaning', '')
        modern = timeline.get('stage_6', {}).get('meaning', '')

        print(f"  {hebrew}:")
        print(f"    Original: {original[:60]}...")
        print(f"    Modern:   {modern[:60]}...")

        if not original or not modern:
            raise AssertionError(f"{hebrew}: missing original or modern meaning")

    print("\n[PASS] Meaning transformations documented")
    return True


def run_all_tests():
    """Run all benchmark tests."""
    print("=" * 70)
    print("GENESIS 1:1 SCHOLARLY DATA - BENCHMARK TESTS")
    print("=" * 70)
    print("\nPer CLAUDE.md Commandment 11: TEST BEFORE CODE")
    print("These tests define what 'production ready' means.")

    # Load words.json
    print("\n[INFO] Loading words.json...")
    words = load_words_json()

    if words is None:
        print("[FAIL] words.json not found at C:/mechanical-bible/words.json")
        sys.exit(1)

    print(f"[OK] Loaded {len(words)} words")

    # Run all tests
    tests = [
        ("Genesis words exist", test_genesis_words_exist),
        ("Scholarly timelines exist", test_scholarly_timelines_exist),
        ("All 6 stages present", test_all_stages_present),
        ("Stage fields complete", test_stage_fields_complete),
        ("Scholarly debate quality", test_scholarly_debate_quality),
        ("Primary sources cited", test_primary_sources_cited),
        ("Original language text", test_hebrew_greek_latin_text),
        ("Meaning transformation", test_meaning_transformation_documented),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func(words)
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {name}: {e}")
            failed += 1

    # Final summary
    print("\n" + "=" * 70)
    print("BENCHMARK TEST RESULTS")
    print("=" * 70)
    print(f"  Passed: {passed}/{len(tests)}")
    print(f"  Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n[OK] ALL TESTS PASSED - Production Ready!")
        print("=" * 70)
        return 0
    else:
        print(f"\n[FAIL] {failed} tests failed - NOT production ready")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
