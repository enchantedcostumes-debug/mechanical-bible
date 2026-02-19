#!/usr/bin/env python3
"""
Prepare NT HTML for Mechanical Translations - Mechanical Bible
================================================================
Adds <span class="mechanical"> and <span class="oracle"> spans to NT chapter
HTML files so that bake_mechanical.py can fill them in.

Current NT structure:
  <div class="translation">[raw text]</div>

Target structure (matching OT):
  <div class="translation">
    <span class="mechanical"></span>
    <span class="oracle"></span>
  </div>

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# NT book folder names
NT_BOOKS = [
    'matthew', 'mark', 'luke', 'john', 'acts', 'romans',
    '1_corinthians', '2_corinthians', 'galatians', 'ephesians',
    'philippians', 'colossians', '1_thessalonians', '2_thessalonians',
    '1_timothy', '2_timothy', 'titus', 'philemon',
    'hebrews', 'james', '1_peter', '2_peter',
    '1_john', '2_john', '3_john', 'jude', 'revelation',
]


def prepare_chapter(html_path):
    """Add mechanical and oracle spans to a NT chapter HTML file.

    Returns number of verses updated.
    """
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has mechanical spans
    if 'class="mechanical"' in content:
        return 0

    original = content
    updated = 0

    # Find all translation divs and replace their content with layered spans
    # Pattern: <div class="translation">...text...</div>
    def replace_translation(match):
        nonlocal updated
        old_text = match.group(1)
        # Preserve the old translation as the oracle layer
        new_content = f'<span class="mechanical"></span><span class="oracle">{old_text.strip()}</span>'
        updated += 1
        return f'<div class="translation">{new_content}</div>'

    content = re.sub(
        r'<div class="translation">(.*?)</div>',
        replace_translation,
        content,
        flags=re.DOTALL
    )

    if content != original:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)

    return updated


def main():
    print('=' * 60)
    print('PREPARE NT HTML FOR MECHANICAL TRANSLATIONS')
    print('  Adding <span class="mechanical"> to all NT chapter files')
    print('=' * 60)

    total_files = 0
    total_verses = 0

    for book in NT_BOOKS:
        book_dir = BASE_DIR / book
        if not book_dir.exists():
            print(f'  SKIP {book}: folder not found')
            continue

        book_verses = 0
        html_files = sorted(book_dir.glob('[0-9]*.html'))

        for html_path in html_files:
            v = prepare_chapter(html_path)
            book_verses += v
            total_files += 1

        total_verses += book_verses
        print(f'  {book}: {book_verses} verses prepared across {len(html_files)} chapters')

    print(f'\n[DONE] Prepared {total_verses:,} verses across {total_files} HTML files')


if __name__ == '__main__':
    main()
