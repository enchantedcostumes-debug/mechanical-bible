#!/usr/bin/env python3
"""
Add view toolbar + interlinear/parallel/grammar/search to ALL Bible chapters.
Inserts:
  1. View toolbar after chapter-nav div
  2. Four script tags before </body>
  3. Verse anchor IDs for deep linking

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import os
import re
import glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')

# View toolbar HTML to insert after chapter-nav
VIEW_TOOLBAR = '''        <div class="view-toolbar">
            <button id="interlinear-toggle" onclick="toggleInterlinear()">Interlinear View</button>
            <button id="parallel-toggle" onclick="toggleParallel()">Parallel View</button>
            <button id="grammar-toggle" onclick="toggleGrammar()">Grammar View</button>
            <button id="search-toggle" onclick="openSearch()">Search</button>
        </div>'''

# Script tags to add before </body>
SCRIPT_TAGS = '''    <script src="/js/interlinear.js"></script>
    <script src="/js/parallel-view.js"></script>
    <script src="/js/grammar-view.js"></script>
    <script src="/js/search.js"></script>'''


def find_all_chapters():
    """Find all chapter HTML files across all 66+ books."""
    chapters = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Skip tools, css, js, data, .git directories
        skip_dirs = {'tools', 'css', 'js', 'data', '.git', 'node_modules', 'img', 'images'}
        rel = os.path.relpath(root, PROJECT_ROOT)
        if any(part in skip_dirs for part in rel.split(os.sep)):
            continue

        for f in files:
            # Match chapter files: digits.html
            if re.match(r'^\d+\.html$', f):
                filepath = os.path.join(root, f)
                chapters.append(filepath)

    return sorted(chapters)


def update_chapter(filepath):
    """Add view toolbar, scripts, and verse anchors to a chapter file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False

    # 1. Add view toolbar after chapter-nav (if not already present)
    if 'view-toolbar' not in content:
        # Find the end of the chapter-nav div
        # Pattern: </div> that closes chapter-nav, followed by verse divs
        chapter_nav_match = re.search(
            r'(<div class="chapter-nav">.*?</div>)\s*\n?\s*(<div class="verse">)',
            content,
            re.DOTALL
        )
        if chapter_nav_match:
            insert_point = chapter_nav_match.end(1)
            content = (
                content[:insert_point] +
                '\n' + VIEW_TOOLBAR + '\n' +
                content[insert_point:]
            )
            modified = True

    # 2. Add script tags before </body> (if not already present)
    if 'interlinear.js' not in content:
        # Find the last </script> or the word-modal.js script tag
        if '<script src="/js/site-footer.js"></script>' in content:
            content = content.replace(
                '<script src="/js/site-footer.js"></script>',
                '<script src="/js/site-footer.js"></script>\n' + SCRIPT_TAGS
            )
            modified = True
        elif '</body>' in content:
            content = content.replace(
                '</body>',
                SCRIPT_TAGS + '\n</body>'
            )
            modified = True

    # 3. Add verse anchor IDs for deep linking (if not already present)
    if 'id="v' not in content:
        def add_verse_id(match):
            verse_ref = match.group(1)
            # Extract book and verse numbers
            # Handle refs like "Genesis 1:1", "1 Samuel 3:4", etc.
            parts = verse_ref.strip().rsplit(' ', 1)
            if len(parts) == 2:
                chapter_verse = parts[1]
                anchor_id = 'v' + chapter_verse.replace(':', '-')
                return '<div class="verse" id="' + anchor_id + '">'
            return match.group(0)

        new_content = re.sub(
            r'<div class="verse">\s*\n?\s*<div class="verse-ref">([^<]+)',
            lambda m: add_verse_id(m),
            content
        )
        if new_content != content:
            content = new_content
            modified = True

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    return modified


def main():
    chapters = find_all_chapters()
    print(f'[OK] Found {len(chapters)} chapter files')

    updated = 0
    failed = 0
    already_done = 0

    for filepath in chapters:
        rel = os.path.relpath(filepath, PROJECT_ROOT)
        try:
            if update_chapter(filepath):
                updated += 1
                if updated <= 5 or updated % 100 == 0:
                    print(f'  [OK] Updated: {rel}')
            else:
                already_done += 1
        except Exception as e:
            failed += 1
            print(f'  [FAIL] {rel}: {e}')

    print()
    print('=' * 60)
    print(f'[OK] Updated: {updated}')
    print(f'[--] Already done: {already_done}')
    if failed:
        print(f'[FAIL] Failed: {failed}')
    print(f'[OK] Total chapters: {len(chapters)}')
    print('=' * 60)


if __name__ == '__main__':
    main()
