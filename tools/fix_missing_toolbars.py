#!/usr/bin/env python3
"""
Fix chapters that are missing the view toolbar.
Handles NT chapters with 'verse red-letter' and Greek text.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import os
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.join(SCRIPT_DIR, '..')

VIEW_TOOLBAR = '''        <div class="view-toolbar">
            <button id="interlinear-toggle" onclick="toggleInterlinear()">Interlinear View</button>
            <button id="parallel-toggle" onclick="toggleParallel()">Parallel View</button>
            <button id="grammar-toggle" onclick="toggleGrammar()">Grammar View</button>
            <button id="search-toggle" onclick="openSearch()">Search</button>
        </div>'''


def find_all_chapters():
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


def fix_toolbar(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'view-toolbar' in content:
        return False

    # Try multiple patterns for chapter-nav followed by verse
    patterns = [
        # Pattern 1: chapter-nav followed by verse (with or without red-letter)
        r'(<div class="chapter-nav">.*?</div>)\s*\n?\s*(<div class="verse)',
        # Pattern 2: chapter-nav on its own line
        r'(</div>\s*\n\s*)(\s*<div class="verse)',
    ]

    for pattern in patterns:
        match = re.search(pattern, content, re.DOTALL)
        if match:
            # Insert toolbar between chapter-nav and first verse
            insert_pos = match.end(1)
            content = (
                content[:insert_pos] +
                '\n' + VIEW_TOOLBAR + '\n' +
                content[insert_pos:]
            )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

    # Fallback: insert after </nav> line
    nav_end = content.find('</nav>')
    if nav_end >= 0:
        # Find the next line after </nav>
        next_newline = content.find('\n', nav_end)
        if next_newline >= 0:
            # Skip past the chapter-nav div if it exists
            chapter_nav_end = content.find('</div>', next_newline)
            if chapter_nav_end >= 0 and chapter_nav_end < next_newline + 2000:
                insert_pos = chapter_nav_end + len('</div>')
                content = (
                    content[:insert_pos] +
                    '\n' + VIEW_TOOLBAR + '\n' +
                    content[insert_pos:]
                )
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True

    return False


def main():
    chapters = find_all_chapters()
    fixed = 0
    already_ok = 0

    for filepath in chapters:
        rel = os.path.relpath(filepath, PROJECT_ROOT)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'view-toolbar' in content:
            already_ok += 1
            continue

        if fix_toolbar(filepath):
            fixed += 1
            print(f'  [FIX] {rel}')
        else:
            print(f'  [WARN] Could not fix: {rel}')

    print()
    print(f'[OK] Fixed: {fixed}')
    print(f'[--] Already OK: {already_ok}')
    print(f'[OK] Total: {len(chapters)}')


if __name__ == '__main__':
    main()
