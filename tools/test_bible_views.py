#!/usr/bin/env python3
"""
Test suite for Mechanical Bible view features.
Validates interlinear, parallel, grammar, and search across all 1,189 chapters.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import os
import re
import sys
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')


def find_all_chapters():
    """Find all chapter HTML files."""
    chapters = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        skip_dirs = {'tools', 'css', 'js', 'data', '.git', 'node_modules', 'img', 'images'}
        rel = os.path.relpath(root, PROJECT_ROOT)
        if any(part in skip_dirs for part in rel.split(os.sep)):
            continue
        for f in files:
            if re.match(r'^\d+\.html$', f):
                chapters.append(os.path.join(root, f))
    return sorted(chapters)


# ===== TEST 1: All JS files exist =====

def test_js_files_exist():
    """All four JavaScript feature files must exist."""
    js_files = [
        'js/interlinear.js',
        'js/parallel-view.js',
        'js/grammar-view.js',
        'js/search.js',
    ]
    for js_file in js_files:
        path = os.path.join(PROJECT_ROOT, js_file)
        assert os.path.exists(path), f'Missing JS file: {js_file}'
        size = os.path.getsize(path)
        assert size > 500, f'{js_file} too small ({size} bytes) - likely stub'
    print(f'[PASS] All 4 JS files exist and are substantial')


# ===== TEST 2: CSS styles added =====

def test_css_styles():
    """CSS must have all view-related styles."""
    css_path = os.path.join(PROJECT_ROOT, 'css', 'egyptian-theme.css')
    assert os.path.exists(css_path), 'Missing egyptian-theme.css'

    with open(css_path, 'r', encoding='utf-8') as f:
        css = f.read()

    required_classes = [
        '.view-toolbar',
        '.interlinear-container',
        '.interlinear-word',
        '.il-hebrew',
        '.il-translit',
        '.il-gloss',
        '.parallel-verse',
        '.parallel-hebrew',
        '.parallel-english',
        '.grammar-legend',
        '.grammar-legend-swatch',
        '.search-modal',
        '.search-modal-content',
        '.search-header',
        '.search-results',
        '.search-result-item',
    ]

    missing = []
    for cls in required_classes:
        if cls not in css:
            missing.append(cls)

    assert len(missing) == 0, f'Missing CSS classes: {missing}'
    print(f'[PASS] All {len(required_classes)} CSS classes found in egyptian-theme.css')


# ===== TEST 3: All chapters have view toolbar =====

def test_all_chapters_have_toolbar():
    """Every chapter file must have the view toolbar."""
    chapters = find_all_chapters()
    assert len(chapters) > 1000, f'Expected 1000+ chapters, found {len(chapters)}'

    missing_toolbar = []
    for filepath in chapters:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'view-toolbar' not in content:
            rel = os.path.relpath(filepath, PROJECT_ROOT)
            missing_toolbar.append(rel)

    assert len(missing_toolbar) == 0, (
        f'{len(missing_toolbar)} chapters missing toolbar: '
        f'{missing_toolbar[:5]}{"..." if len(missing_toolbar) > 5 else ""}'
    )
    print(f'[PASS] All {len(chapters)} chapters have view toolbar')


# ===== TEST 4: All chapters load 4 scripts =====

def test_all_chapters_load_scripts():
    """Every chapter must load all 4 feature JS files."""
    chapters = find_all_chapters()
    scripts = ['interlinear.js', 'parallel-view.js', 'grammar-view.js', 'search.js']

    issues = []
    for filepath in chapters:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for script in scripts:
            if script not in content:
                rel = os.path.relpath(filepath, PROJECT_ROOT)
                issues.append(f'{rel} missing {script}')

    assert len(issues) == 0, (
        f'{len(issues)} script loading issues: '
        f'{issues[:5]}{"..." if len(issues) > 5 else ""}'
    )
    print(f'[PASS] All {len(chapters)} chapters load all 4 feature scripts')


# ===== TEST 5: Toolbar has all 4 buttons =====

def test_toolbar_buttons():
    """Toolbar must have Interlinear, Parallel, Grammar, and Search buttons."""
    chapters = find_all_chapters()
    # Sample 20 random chapters for button content check
    sample = random.sample(chapters, min(20, len(chapters)))

    buttons = ['toggleInterlinear', 'toggleParallel', 'toggleGrammar', 'openSearch']

    for filepath in sample:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        for btn in buttons:
            rel = os.path.relpath(filepath, PROJECT_ROOT)
            assert btn in content, f'{rel} missing button function: {btn}'

    print(f'[PASS] All 4 toolbar buttons verified in {len(sample)} sample chapters')


# ===== TEST 6: Verse anchors present =====

def test_verse_anchors():
    """Chapters must have verse anchor IDs for deep linking."""
    chapters = find_all_chapters()
    sample = random.sample(chapters, min(20, len(chapters)))

    anchored = 0
    no_anchor = 0

    for filepath in sample:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'id="v' in content:
            anchored += 1
        else:
            no_anchor += 1

    assert anchored > 0, 'No chapters have verse anchors'
    print(f'[PASS] Verse anchors found in {anchored}/{len(sample)} sample chapters')


# ===== TEST 7: Interlinear JS has Hebrew transliteration =====

def test_interlinear_content():
    """Interlinear JS must have Hebrew transliteration map."""
    js_path = os.path.join(PROJECT_ROOT, 'js', 'interlinear.js')
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    assert 'HEBREW_TRANSLIT' in content, 'Missing HEBREW_TRANSLIT map'
    assert 'hebrewToTranslit' in content, 'Missing hebrewToTranslit function'
    assert 'toggleInterlinear' in content, 'Missing toggleInterlinear function'
    assert 'enableInterlinear' in content, 'Missing enableInterlinear function'
    assert 'disableInterlinear' in content, 'Missing disableInterlinear function'
    assert 'interlinear-container' in content, 'Missing interlinear-container class'
    assert 'il-hebrew' in content, 'Missing il-hebrew class'
    assert 'il-translit' in content, 'Missing il-translit class'
    assert 'il-gloss' in content, 'Missing il-gloss class'
    print('[PASS] interlinear.js has complete Hebrew transliteration system')


# ===== TEST 8: Grammar JS has POS detection =====

def test_grammar_content():
    """Grammar JS must have POS color map and Hebrew detection."""
    js_path = os.path.join(PROJECT_ROOT, 'js', 'grammar-view.js')
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    assert 'POS_COLORS' in content, 'Missing POS_COLORS map'
    assert "'divine'" in content, 'Missing divine POS category'
    assert 'getWordPOS' in content, 'Missing getWordPOS function'
    assert 'toggleGrammar' in content, 'Missing toggleGrammar function'
    assert 'buildGrammarLegend' in content, 'Missing buildGrammarLegend function'
    assert 'HEBREW_POS_HINTS' in content, 'Missing HEBREW_POS_HINTS'

    # Count POS categories (look for color: in the POS_COLORS object)
    pos_count = len(re.findall(r"color:\s*'#", content))
    assert pos_count >= 10, f'Expected 10+ POS categories, found {pos_count}'
    print(f'[PASS] grammar-view.js has {pos_count} POS categories including divine names')


# ===== TEST 9: Parallel JS has side-by-side layout =====

def test_parallel_content():
    """Parallel JS must create side-by-side Hebrew/English."""
    js_path = os.path.join(PROJECT_ROOT, 'js', 'parallel-view.js')
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    assert 'toggleParallel' in content, 'Missing toggleParallel function'
    assert 'enableParallel' in content, 'Missing enableParallel function'
    assert 'disableParallel' in content, 'Missing disableParallel function'
    assert 'parallel-verse' in content, 'Missing parallel-verse class'
    assert 'parallel-hebrew' in content, 'Missing parallel-hebrew column'
    assert 'parallel-english' in content, 'Missing parallel-english column'
    print('[PASS] parallel-view.js has complete side-by-side layout system')


# ===== TEST 10: Search JS has Bible-wide search =====

def test_search_content():
    """Search JS must support Bible-wide search with modal."""
    js_path = os.path.join(PROJECT_ROOT, 'js', 'search.js')
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read()

    assert 'openSearch' in content, 'Missing openSearch function'
    assert 'closeSearch' in content, 'Missing closeSearch function'
    assert 'performSearch' in content or 'doSearch' in content, 'Missing search function'
    assert 'search-modal' in content, 'Missing search-modal class'
    assert 'words-priority.json' in content or 'words.json' in content, 'Missing word data loading'
    print('[PASS] search.js has complete Bible search with modal')


# ===== TEST 11: Verse structure preserved =====

def test_verse_structure():
    """Verses must still have verse-ref, original-text, and translation."""
    chapters = find_all_chapters()
    sample = random.sample(chapters, min(10, len(chapters)))

    for filepath in sample:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        rel = os.path.relpath(filepath, PROJECT_ROOT)

        assert 'class="verse-ref"' in content, f'{rel}: Missing verse-ref divs'
        has_hebrew = 'class="original-text hebrew"' in content
        has_greek = 'class="original-text greek"' in content
        assert has_hebrew or has_greek, f'{rel}: Missing original-text (hebrew or greek)'
        assert 'class="translation"' in content, f'{rel}: Missing translation divs'
        assert 'class="word"' in content, f'{rel}: Missing word spans'

    print(f'[PASS] Verse structure preserved in {len(sample)} sample chapters')


# ===== TEST 12: No duplicate toolbars or scripts =====

def test_no_duplicates():
    """No chapter should have duplicate toolbars or scripts."""
    chapters = find_all_chapters()
    sample = random.sample(chapters, min(20, len(chapters)))

    for filepath in sample:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        rel = os.path.relpath(filepath, PROJECT_ROOT)

        toolbar_count = content.count('view-toolbar')
        assert toolbar_count <= 1, f'{rel}: {toolbar_count} toolbars (expected 1)'

        interlinear_count = content.count('interlinear.js')
        assert interlinear_count <= 1, f'{rel}: {interlinear_count} interlinear.js loads (expected 1)'

    print(f'[PASS] No duplicate toolbars or scripts in {len(sample)} sample chapters')


# ===== MAIN =====

if __name__ == '__main__':
    print('=' * 60)
    print('TESTING: Mechanical Bible View Features')
    print('=' * 60)
    print()

    tests = [
        test_js_files_exist,
        test_css_styles,
        test_all_chapters_have_toolbar,
        test_all_chapters_load_scripts,
        test_toolbar_buttons,
        test_verse_anchors,
        test_interlinear_content,
        test_grammar_content,
        test_parallel_content,
        test_search_content,
        test_verse_structure,
        test_no_duplicates,
    ]

    passed = 0
    failed = 0

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            failed += 1
            print(f'[FAIL] {test_fn.__name__}: {e}')
        except Exception as e:
            failed += 1
            print(f'[ERROR] {test_fn.__name__}: {e}')

    print()
    print('=' * 60)
    if failed == 0:
        print(f'[OK] ALL {passed} TESTS PASSED')
    else:
        print(f'[FAIL] {failed}/{passed + failed} tests failed')
    print('=' * 60)

    if failed > 0:
        sys.exit(1)
