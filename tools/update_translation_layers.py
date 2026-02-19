#!/usr/bin/env python3
"""
UPDATE TRANSLATION LAYERS - Mechanical Bible
=============================================
Across all chapter HTML files:
1. Add <script src="../js/translation-toggle.js"></script> before site-footer.js
2. Add empty <span class="oracle"></span> inside each .translation div
   (the JS will populate oracle + convert JPS to toggle at runtime)

MECH and RMT spans stay baked. JPS span stays in HTML but JS converts it
to toggle-translation class at runtime and caches the text.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Skip non-book directories
SKIP_DIRS = {'.git', 'css', 'js', 'data', 'tools', 'images', 'fonts',
             'node_modules', '.claude', 'lexicon'}


def get_book_dirs():
    """Get all book directories (contain numbered HTML files)."""
    dirs = []
    for d in BASE_DIR.iterdir():
        if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith('.'):
            # Check if it has at least one numbered HTML file
            if any(re.match(r'^\d+\.html$', f.name) for f in d.iterdir() if f.is_file()):
                dirs.append(d)
    return sorted(dirs)


def process_file(filepath):
    """Process a single chapter HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Add translation-toggle.js if not present
    if 'translation-toggle.js' not in content:
        if '../js/site-footer.js' in content:
            content = content.replace(
                '<script src="../js/site-footer.js"></script>',
                '<script src="../js/translation-toggle.js"></script>\n<script src="../js/site-footer.js"></script>'
            )
        elif '</body>' in content:
            content = content.replace(
                '</body>',
                '<script src="../js/translation-toggle.js"></script>\n</body>'
            )

    # 2. Add empty oracle span inside each .translation div if not present
    # Insert before the .jps span (so order is: rmt, mechanical, oracle, jps)
    if '<span class="oracle">' not in content:
        content = content.replace(
            '<span class="jps">',
            '<span class="oracle"></span><span class="jps">'
        )

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False


def main():
    total = 0
    modified = 0

    for book_dir in get_book_dirs():
        for filepath in sorted(book_dir.glob('[0-9]*.html')):
            total += 1
            if process_file(filepath):
                modified += 1

    print(f'\n[DONE] Processed {total} chapter files, modified {modified}')


if __name__ == '__main__':
    print('=' * 60)
    print('UPDATE TRANSLATION LAYERS - Mechanical Bible')
    print('=' * 60)
    main()
