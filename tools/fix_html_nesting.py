#!/usr/bin/env python3
"""
FIX HTML NESTING - Mechanical Bible
=====================================
Fixes broken div nesting in chapter HTML files.

The problem: after the translation div, there are extra </div> tags
that prematurely close the verse container, breaking page layout.

Copyright (c) 2026 Tammy L Casey. All rights reserved.
"""

import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def fix_file(filepath):
    """Fix div nesting in a single chapter HTML file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    opens_before = content.count('<div')
    closes_before = content.count('</div>')

    if opens_before == closes_before:
        return False

    # Fix pattern 1: Extra </div> between translation and footnotes
    content = re.sub(
        r'(</div>)\s*</div>\s*(<div class="footnotes">)',
        r'\1\2',
        content
    )

    # Fix pattern 2: Extra </div> after footnotes before cross-refs
    content = re.sub(
        r'(</div>)\s*</div>\s*(<div class="cross-refs">)',
        r'\1\2',
        content
    )

    # Fix pattern 3: Extra </div> after cross-refs </ul></div>
    content = re.sub(
        r'(</ul></div>)\s*</div>\s*(<div class="verse"|$)',
        r'\1\2',
        content
    )

    # Fix pattern 4: Extra </div> after footnotes when no cross-refs
    content = re.sub(
        r'(</div>)\s*</div>\s*</div>\s*(<div class="verse">)',
        r'\1</div>\2',
        content
    )

    # Iteratively remove excess </div> before verse divs
    opens = content.count('<div')
    closes = content.count('</div>')
    while closes > opens:
        new_content = re.sub(
            r'</div>\s*</div>(\s*<div class="verse")',
            r'</div>\1',
            content,
            count=1
        )
        if new_content == content:
            break
        content = new_content
        opens = content.count('<div')
        closes = content.count('</div>')

    # Also try removing excess </div> before chapter-nav or end of body
    while closes > opens:
        new_content = re.sub(
            r'</div>\s*</div>(\s*<div class="chapter-nav")',
            r'</div>\1',
            content,
            count=1
        )
        if new_content == content:
            new_content = re.sub(
                r'</div>\s*</div>(\s*</div>\s*</body>)',
                r'</div>\1',
                content,
                count=1
            )
        if new_content == content:
            break
        content = new_content
        opens = content.count('<div')
        closes = content.count('</div>')

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True

    return False


def process_all():
    """Process all chapter HTML files."""
    fixed = 0
    total = 0
    still_broken = []

    for book_dir in sorted(BASE_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        if book_dir.name.startswith('.') or book_dir.name.startswith('_'):
            continue
        if book_dir.name in ('css', 'js', 'data', 'tools', 'fonts', 'api',
                             'static', 'sacred-library', 'topics',
                             'huggingface_dataset'):
            continue

        html_files = sorted(book_dir.glob('*.html'))
        for hf in html_files:
            if hf.name == 'index.html':
                continue
            total += 1
            was_fixed = fix_file(hf)
            if was_fixed:
                fixed += 1

            with open(hf, 'r', encoding='utf-8') as f:
                c = f.read()
            o = c.count('<div')
            cl = c.count('</div>')
            if o != cl:
                still_broken.append((hf, o - cl))

        if html_files:
            count = len([h for h in html_files if h.name != 'index.html'])
            print(f'  {book_dir.name}: {count} chapters')

    print(f'\n[DONE] Fixed {fixed}/{total} files')
    if still_broken:
        print(f'\n[WARN] {len(still_broken)} files still unbalanced:')
        for p, diff in still_broken[:20]:
            print(f'  {p.relative_to(BASE_DIR)}: diff={diff}')
    else:
        print('[OK] All files have balanced div nesting!')


if __name__ == '__main__':
    print('=' * 60)
    print('FIX HTML NESTING - Mechanical Bible')
    print('=' * 60)
    process_all()
